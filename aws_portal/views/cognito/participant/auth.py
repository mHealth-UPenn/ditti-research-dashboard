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
from aws_portal.utils.cognito.participant.auth_utils import (
    init_oauth_client, validate_token_for_authenticated_route, ParticipantAuth
)
from aws_portal.utils.cognito.common import generate_code_verifier, create_code_challenge

blueprint = Blueprint("participant_cognito", __name__, url_prefix="/cognito")
logger = logging.getLogger(__name__)
auth = ParticipantAuth()


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
        # Check for existing study subject
        study_subject = StudySubject.query.filter_by(ditti_id=ditti_id).first()

        if study_subject:
            if study_subject.is_archived:
                logger.warning(
                    f"Attempt to login with archived account: {ditti_id}")
                return None, make_response({"msg": "Account is archived."}, 400)
            return study_subject, None

        # Create new study subject
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
    """Build the Cognito logout URL with appropriate parameters."""
    domain = current_app.config["COGNITO_PARTICIPANT_DOMAIN"]
    client_id = current_app.config["COGNITO_PARTICIPANT_CLIENT_ID"]
    logout_uri = current_app.config["COGNITO_PARTICIPANT_LOGOUT_URI"]

    params = {
        "client_id": client_id,
        "logout_uri": logout_uri,
        "response_type": "code"
    }
    return f"https://{domain}/logout?{urlencode(params)}"


def _get_ditti_id_from_token(id_token):
    """Extract ditti_id from a validated ID token."""
    try:
        # Validate token
        success, userinfo = validate_token_for_authenticated_route(id_token)

        if not success:
            return None, make_response({"msg": userinfo}, 401)

        # Extract cognito username
        cognito_username = userinfo.get("cognito:username")

        # Get ditti_id from database
        stmt = select(StudySubject.ditti_id).where(
            func.lower(StudySubject.ditti_id) == cognito_username.lower()
        )
        ditti_id = db.session.execute(stmt).scalar()

        if not ditti_id:
            logger.warning(f"Participant {cognito_username} not found.")
            return None, make_response({"msg": f"Participant {cognito_username} not found."}, 400)

        return ditti_id, None

    except Exception as e:
        logger.error(f"Error extracting ditti_id from token: {str(e)}")
        return None, make_response({"msg": "Database error."}, 500)


@blueprint.route("/login")
def login():
    """
    Redirect users to the Cognito login page.

    This endpoint:
    1. Generates a secure nonce for ID token validation
    2. Generates a secure state parameter for CSRF protection
    3. Generates PKCE code_verifier and code_challenge for authorization code security
    4. Redirects to the Cognito authorization endpoint with all security parameters

    Query Parameters:
        elevated (bool): If "true", requests additional admin scopes

    Returns:
        Redirect to Cognito login page
    """
    init_oauth_client()

    # Determine scope based on elevated parameter
    elevated = request.args.get("elevated") == "true"
    scope = "openid" + (" aws.cognito.signin.user.admin" if elevated else "")

    # Generate and store nonce for ID token validation
    nonce = secrets.token_urlsafe(32)
    session["cognito_nonce"] = nonce
    session["cognito_nonce_generated"] = int(
        datetime.now(timezone.utc).timestamp())

    # Generate and store state for CSRF protection
    state = secrets.token_urlsafe(32)
    session["cognito_state"] = state

    # Generate and store PKCE code_verifier and code_challenge
    code_verifier = generate_code_verifier()
    code_challenge = create_code_challenge(code_verifier)
    session["cognito_code_verifier"] = code_verifier

    # Redirect to Cognito authorization endpoint with all security parameters
    return oauth.oidc.authorize_redirect(
        current_app.config["COGNITO_PARTICIPANT_REDIRECT_URI"],
        scope=scope,
        nonce=nonce,
        state=state,
        code_challenge=code_challenge,
        code_challenge_method="S256"
    )


@blueprint.route("/callback")
def cognito_callback():
    """
    Handle Cognito's authorization callback.

    This endpoint:
    1. Validates the state parameter to prevent CSRF attacks
    2. Provides the code_verifier for PKCE validation
    3. Exchanges the authorization code for tokens
    4. Validates the ID token with the stored nonce
    5. Creates or retrieves the user in the database
    6. Sets secure cookies with the tokens
    7. Redirects to the frontend application

    Returns:
        Redirect to frontend with tokens set in cookies, or
        400 Bad Request on authentication errors
    """
    init_oauth_client()

    try:
        # Validate state parameter to prevent CSRF attacks
        state = session.pop("cognito_state", None)
        state_in_request = request.args.get("state")
        if not state or state != state_in_request:
            logger.warning("Invalid state parameter in callback")
            return make_response({"msg": "Invalid authorization state"}, 401)

        # Get code_verifier for PKCE
        code_verifier = session.pop("cognito_code_verifier", None)
        if not code_verifier:
            logger.warning("Missing code_verifier in session")
            return make_response({"msg": "Authorization security error"}, 401)

        # Validate nonce
        nonce = session.pop("cognito_nonce", None)
        nonce_generated = session.pop("cognito_nonce_generated", 0)

        # Check if nonce is valid
        nonce_age = int(datetime.now(
            timezone.utc).timestamp()) - nonce_generated
        if not nonce or nonce_age > 300:  # 5 minutes expiration
            logger.warning(f"Invalid or expired nonce. Age: {nonce_age}s")
            return make_response({"msg": "Authentication session expired"}, 401)

        # Exchange code for tokens with PKCE code_verifier
        token = oauth.oidc.authorize_access_token(code_verifier=code_verifier)

        # Parse ID token with nonce validation
        try:
            userinfo = oauth.oidc.parse_id_token(token, nonce=nonce)
        except Exception as e:
            logger.error(f"Failed to validate ID token: {str(e)}")
            return make_response({"msg": f"Authentication failed: {str(e)}"}, 401)

        # Get or create study subject
        ditti_id = userinfo.get("cognito:username")
        study_subject, error = _create_or_get_study_subject(ditti_id)
        if error:
            return error

        # Set session data
        session["study_subject_id"] = study_subject.id
        session["user"] = userinfo

        # Create response with redirect to frontend
        frontend_url = current_app.config.get(
            "CORS_ORIGINS", "http://localhost:3000")
        response = make_response(redirect(frontend_url))

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
        return make_response({"msg": f"Authentication error: {str(e)}"}, 400)


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

    # Create response with redirect to Cognito logout
    response = make_response(redirect(_get_cognito_logout_url()))

    # Clear all auth cookies
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

    # Check for ID token
    id_token = request.cookies.get("id_token")
    if not id_token:
        return make_response({"msg": "Not authenticated"}, 401)

    # Get ditti ID from token
    ditti_id, error = _get_ditti_id_from_token(id_token)
    if error:
        return error

    # Return success with ditti ID
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
        # Extract required fields
        cognito_username = data.get("cognitoUsername")
        temporary_password = data.get("temporaryPassword")

        # Validate required fields
        if not cognito_username or not temporary_password:
            return jsonify({"error": "Missing required field."}), 400

        # Create user in Cognito
        user_pool_id = current_app.config["COGNITO_PARTICIPANT_USER_POOL_ID"]
        client.admin_create_user(
            UserPoolId=user_pool_id,
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
