from datetime import datetime, timezone
import logging
from urllib.parse import urlencode
import boto3
from botocore.exceptions import ClientError
from flask import Blueprint, current_app, make_response, redirect, request, session, jsonify
import secrets
from sqlalchemy import select, func
from aws_portal.extensions import db, oauth
from aws_portal.models import StudySubject
from aws_portal.utils.auth import auth_required
from aws_portal.utils.cognito.participant.auth_utils import init_oauth_client, parse_and_validate_id_token

blueprint = Blueprint("participant_cognito", __name__, url_prefix="/cognito")
logger = logging.getLogger(__name__)


def _create_or_get_study_subject(ditti_id):
    """
    Find an existing study subject or create a new one.

    Args:
        ditti_id (str): The participant's ditti ID

    Returns:
        tuple: (study_subject, error_response)
            study_subject: The StudySubject object if found/created successfully, None otherwise
            error_response: Error response object if error occurred, None otherwise
    """
    try:
        # Check for study subject in database
        study_subject = StudySubject.query.filter_by(ditti_id=ditti_id).first()

        if study_subject:
            if study_subject.is_archived:
                logger.warning(
                    f"Attempt to login with archived account: {ditti_id}")
                return None, make_response({"msg": "Account is archived."}, 400)
            return study_subject, None

        # If not found, create a new study subject
        study_subject = StudySubject(
            created_on=datetime.now(timezone.utc),
            ditti_id=ditti_id,
            is_archived=False
        )
        db.session.add(study_subject)
        db.session.commit()

        return study_subject, None

    except Exception as e:
        logger.error(f"Database error with study subject: {str(e)}")
        db.session.rollback()
        return None, make_response({"msg": "Database error."}, 500)


def _get_cognito_logout_url():
    """
    Build the Cognito logout URL with appropriate parameters.

    Returns:
        str: Complete Cognito logout URL
    """
    base_url = f"https://{current_app.config['COGNITO_PARTICIPANT_DOMAIN']}/logout"
    params = {
        "client_id": current_app.config["COGNITO_PARTICIPANT_CLIENT_ID"],
        "logout_uri": current_app.config["COGNITO_PARTICIPANT_LOGOUT_URI"],
        "response_type": "code"
    }
    return f"{base_url}?{urlencode(params)}"


def _get_ditti_id_from_token(id_token, nonce=None):
    """
    Extract and validate ditti_id from an ID token.

    Args:
        id_token (str): The ID token to parse
        nonce (str): Optional nonce for token validation

    Returns:
        tuple: (ditti_id, error_response)
            ditti_id: The extracted ditti_id if successful, None otherwise
            error_response: Error response object if error occurred, None otherwise
    """
    # Use the shared function to parse and validate the token
    success, result = parse_and_validate_id_token(id_token, nonce)

    if not success:
        # Handle the error case
        return None, make_response({"msg": result}, 401)

    # Success case - extract the cognito username
    userinfo = result
    cognito_username = userinfo.get("cognito:username")

    # Get actual ditti_id from database (Cognito stores ditti IDs lowercase)
    try:
        stmt = select(StudySubject.ditti_id).where(
            func.lower(StudySubject.ditti_id) == cognito_username
        )
        ditti_id = db.session.execute(stmt).scalar()

        if not ditti_id:
            logger.warning(
                f"Participant with cognito:username {cognito_username} not found.")
            return None, make_response({"msg": f"Participant {cognito_username} not found."}, 400)

        return ditti_id, None
    except Exception as e:
        logger.error(f"Database error retrieving ditti_id: {str(e)}")
        return None, make_response({"msg": "Database error."}, 500)


@blueprint.route("/login")
def login():
    """
    Redirect users to the Cognito login page.

    This endpoint generates a secure nonce, stores it in the session,
    and redirects to the Cognito authorization endpoint with appropriate parameters.

    Query Parameters:
        elevated (bool): If "true", requests additional admin scopes

    Returns:
        Redirect to Cognito login page
    """
    init_oauth_client()

    # Determine scope based on elevated parameter
    elevated = request.args.get("elevated") == "true"
    scope = "openid" + (" aws.cognito.signin.user.admin" if elevated else "")

    # Generate and store a nonce for OIDC security
    nonce = secrets.token_urlsafe(32)
    session["cognito_nonce"] = nonce

    # Store nonce generation time to enforce expiration
    session["cognito_nonce_generated"] = int(
        datetime.now(timezone.utc).timestamp())

    # Redirect to Cognito login
    return oauth.oidc.authorize_redirect(
        current_app.config["COGNITO_PARTICIPANT_REDIRECT_URI"],
        scope=scope,
        nonce=nonce
    )


@blueprint.route("/callback")
def cognito_callback():
    """
    Handle Cognito's authorization callback.

    This endpoint:
    1. Exchanges the authorization code for tokens
    2. Validates the ID token with the stored nonce
    3. Creates or retrieves the user in the database
    4. Sets secure cookies with the tokens
    5. Redirects to the frontend application

    Returns:
        Redirect to frontend with tokens set in cookies, or
        400 Bad Request on authentication errors
    """
    init_oauth_client()

    try:
        # Retrieve and use nonce from session with validation
        nonce = session.pop("cognito_nonce", None)
        nonce_generated = session.pop("cognito_nonce_generated", 0)

        # Check if nonce is missing or expired (nonces valid for max 5 minutes)
        nonce_age = int(datetime.now(
            timezone.utc).timestamp()) - nonce_generated
        if not nonce or nonce_age > 300:  # 5 minutes in seconds
            logger.warning(
                f"Invalid or expired nonce for OIDC callback. Age: {nonce_age}s")
            return make_response({"msg": "Authentication session expired."}, 401)

        # Exchange authorization code for tokens
        token = oauth.oidc.authorize_access_token()

        # Extract and validate user information with required nonce
        success, result = parse_and_validate_id_token(token["id_token"], nonce)
        if not success:
            logger.error(f"Failed to validate ID token: {result}")
            return make_response({"msg": f"Authentication failed: {result}"}, 401)

        userinfo = result
        ditti_id = userinfo.get("cognito:username")

        # Create or get study subject
        study_subject, error = _create_or_get_study_subject(ditti_id)
        if error:
            return error

        # Set session values
        session["study_subject_id"] = study_subject.id
        session["user"] = userinfo

        # Create response with redirect to frontend
        response = make_response(redirect(
            current_app.config.get("CORS_ORIGINS", "http://localhost:3000")
        ))

        # Set tokens in secure cookies
        response.set_cookie(
            "id_token", token["id_token"],
            httponly=True, secure=True, samesite="None"
        )
        response.set_cookie(
            "access_token", token["access_token"],
            httponly=True, secure=True, samesite="None"
        )
        if "refresh_token" in token:
            response.set_cookie(
                "refresh_token", token["refresh_token"],
                httponly=True, secure=True, samesite="None"
            )

        return response

    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        db.session.rollback()
        return make_response({"msg": "Authentication error."}, 400)


@blueprint.route("/logout")
def logout():
    """
    Log out the user from the application and Cognito.

    This endpoint:
    1. Clears the session data
    2. Builds a logout URL for Cognito
    3. Clears authentication cookies
    4. Redirects to Cognito logout

    Returns:
        Redirect to Cognito logout URL with cookies cleared
    """
    init_oauth_client()

    # Clear session
    session.clear()

    # Build logout URL and create response
    logout_url = _get_cognito_logout_url()
    response = make_response(redirect(logout_url))

    # Clear cookies
    for cookie_name in ["id_token", "access_token", "refresh_token"]:
        response.set_cookie(
            cookie_name, "", expires=0,
            httponly=True, secure=True, samesite="None"
        )

    return response


@blueprint.route("/check-login", methods=["GET"])
def check_login():
    """
    Verify active login status and return the user's ditti ID.

    This endpoint:
    1. Checks if the ID token exists in cookies
    2. Validates the token and extracts the ditti_id
    3. Returns the ditti_id on success

    Returns:
        200 OK with ditti_id on success
        401 Unauthorized if not authenticated or token invalid
        400 Bad Request if user not found
    """
    init_oauth_client()

    # Check if token exists
    id_token = request.cookies.get("id_token")
    if not id_token:
        return make_response({"msg": "Not authenticated"}, 401)

    # Get ditti_id from token - in check-login we can't use a nonce
    # but we'll enforce stricter validation in production environments
    ditti_id, error = _get_ditti_id_from_token(id_token)
    if error:
        return error

    # Return success response with ditti_id
    return jsonify({
        "msg": "Login successful",
        "dittiId": ditti_id
    }), 200


@blueprint.route("/register/participant", methods=["POST"])
@auth_required("Create", "Participants")
def register_participant():
    """
    Registers a study participant in AWS Cognito with a temporary password.

    This endpoint allows a research coordinator to create a new participant account
    in the AWS Cognito user pool. The research coordinator provides a Cognito username
    and a temporary password that the participant will use to log in initially.

    The temporary password will require the participant to reset their password
    upon first login.

    Request Body:
        app (int): The app where the request is being made from.
        study (int): The ID of the study the participant is being enrolled for.
        data (dict): A JSON object containing the following fields:
            - cognitoUsername (str): The unique username for the participant.
            - temporaryPassword (str): A temporary password for the participant.

    Returns:
        Response: A JSON response with one of the following:
            - 201 Created: Participant registered successfully.
            - 400 Bad Request: Missing required fields.
            - 500 Internal Server Error: AWS Cognito or other server-side errors.

    Example:
        POST /cognito/register/participant
        {
            "app": 2,
            "study": 1,
            "data": {
                "cognitoUsername": "testuser",
                "temporaryPassword": "TempPass123!"
            }
        }

    Response (201):
        {
            "msg": "Participant registered with AWS Cognito successfully."
        }
    """
    client = boto3.client("cognito-idp")
    data = request.json.get("data", {})

    try:
        cognito_username = data.get("cognitoUsername")
        temporary_password = data.get("temporaryPassword")

        if not cognito_username or not temporary_password:
            return jsonify({"error": "Missing required field."}), 400

        # Create user in Cognito
        client.admin_create_user(
            UserPoolId=current_app.config["COGNITO_PARTICIPANT_USER_POOL_ID"],
            Username=cognito_username,
            TemporaryPassword=temporary_password,
            MessageAction="SUPPRESS"
        )

        return jsonify({"msg": "Participant registered successfully."}), 200

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        logger.error(f"Cognito registration error: {error_code}")
        return jsonify({"msg": f"Cognito registration error."}), 500
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({"msg": "Registration error."}), 500
