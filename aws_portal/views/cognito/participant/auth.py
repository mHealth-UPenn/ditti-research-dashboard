from datetime import datetime, timezone
import logging
import boto3
from botocore.exceptions import ClientError
from flask import Blueprint, current_app, make_response, redirect, request, session
from sqlalchemy import select, func
from aws_portal.extensions import db, oauth
from aws_portal.models import StudySubject
from aws_portal.utils.cognito.participant.auth_utils import (
    init_oauth_client, validate_token_for_authenticated_route, ParticipantAuth
)
from aws_portal.utils.cognito.common import (
    initialize_oauth_and_security_params,
    clear_auth_cookies, set_auth_cookies, validate_security_params, get_cognito_logout_url,
    create_error_response, create_success_response, AUTH_ERROR_MESSAGES
)
from aws_portal.utils.cognito.researcher.decorators import researcher_auth_required

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
                return None, create_error_response(
                    AUTH_ERROR_MESSAGES["account_archived"],
                    status_code=403,
                    error_code="ACCOUNT_ARCHIVED"
                )
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
        return None, create_error_response(
            AUTH_ERROR_MESSAGES["system_error"],
            status_code=500,
            error_code="DATABASE_ERROR"
        )


def _get_ditti_id_from_token(id_token):
    """
    Extract ditti_id from a validated ID token.

    Validates the token and ensures the study subject exists and is not archived.

    Args:
        id_token (str): The ID token to validate

    Returns:
        tuple: (ditti_id, error_response)
            ditti_id: The study subject's ditti_id if valid, None otherwise
            error_response: Error response object if error occurred, None otherwise
    """
    try:
        # Validate token
        success, userinfo = validate_token_for_authenticated_route(id_token)

        if not success:
            return None, create_error_response(
                AUTH_ERROR_MESSAGES["auth_failed"],
                status_code=401,
                error_code="INVALID_TOKEN"
            )

        # Extract cognito username
        cognito_username = userinfo.get("cognito:username")
        if not cognito_username:
            logger.warning("No cognito:username found in token claims")
            return None, create_error_response(
                AUTH_ERROR_MESSAGES["auth_failed"],
                status_code=401,
                error_code="MISSING_USERNAME"
            )

        # Check if a study subject with this ID exists, regardless of archived status
        any_subject = StudySubject.query.filter_by(
            ditti_id=cognito_username).first()

        # If study subject exists but is archived
        if any_subject and any_subject.is_archived:
            logger.warning(
                f"Attempt to access with archived study subject: {cognito_username}")
            return None, create_error_response(
                AUTH_ERROR_MESSAGES["account_archived"],
                status_code=403,
                error_code="ACCOUNT_ARCHIVED"
            )

        # Get active study subject from database (not archived)
        stmt = select(StudySubject.ditti_id).where(
            func.lower(StudySubject.ditti_id) == cognito_username.lower(),
            StudySubject.is_archived == False
        )
        ditti_id = db.session.execute(stmt).scalar()

        if not ditti_id:
            if any_subject:  # This shouldn't happen given the check above, but just for defensive coding
                logger.warning(
                    f"Attempt to access with archived study subject: {cognito_username}")
                return None, create_error_response(
                    AUTH_ERROR_MESSAGES["account_archived"],
                    status_code=403,
                    error_code="ACCOUNT_ARCHIVED"
                )
            else:
                logger.warning(
                    f"No study subject found for ID: {cognito_username}")
                return None, create_error_response(
                    AUTH_ERROR_MESSAGES["not_found"],
                    status_code=404,
                    error_code="USER_NOT_FOUND"
                )

        return ditti_id, None

    except Exception as e:
        logger.error(f"Error extracting ditti_id from token: {str(e)}")
        return None, create_error_response(
            AUTH_ERROR_MESSAGES["system_error"],
            status_code=500,
            error_code="TOKEN_PROCESSING_ERROR"
        )


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
    # Initialize OAuth client and generate security parameters
    security_params = initialize_oauth_and_security_params("participant")

    # Determine scope based on elevated parameter
    elevated = request.args.get("elevated") == "true"
    scope = "openid" + (" aws.cognito.signin.user.admin" if elevated else "")

    # Redirect to Cognito authorization endpoint with all security parameters
    return oauth.oidc.authorize_redirect(
        current_app.config["COGNITO_PARTICIPANT_REDIRECT_URI"],
        scope=scope,
        nonce=security_params["nonce"],
        state=security_params["state"],
        code_challenge=security_params["code_challenge"],
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
        403 Forbidden if study subject is archived
    """
    init_oauth_client()

    try:
        # Validate security parameters
        success, result = validate_security_params(request.args.get("state"))
        if not success:
            return result

        code_verifier = result["code_verifier"]
        nonce = result["nonce"]

        # Exchange code for tokens with PKCE code_verifier
        token = oauth.oidc.authorize_access_token(code_verifier=code_verifier)

        # Parse ID token with nonce validation
        try:
            userinfo = oauth.oidc.parse_id_token(token, nonce=nonce)
        except Exception as e:
            logger.error(f"Failed to validate ID token: {str(e)}")
            return create_error_response(
                AUTH_ERROR_MESSAGES["auth_failed"],
                status_code=401,
                error_code="TOKEN_VALIDATION_FAILED"
            )

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

        # Set auth cookies
        return set_auth_cookies(response, token)

    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        db.session.rollback()
        return create_error_response(
            AUTH_ERROR_MESSAGES["auth_failed"],
            status_code=400,
            error_code="AUTHENTICATION_ERROR"
        )


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
    response = make_response(redirect(get_cognito_logout_url("participant")))

    # Clear all auth cookies
    return clear_auth_cookies(response)


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
        403 Forbidden if study subject is archived
        404 Not Found if study subject not found
    """
    init_oauth_client()

    # Check for ID token
    id_token = request.cookies.get("id_token")
    if not id_token:
        return create_error_response(
            AUTH_ERROR_MESSAGES["auth_required"],
            status_code=401,
            error_code="NO_TOKEN"
        )

    # Get ditti ID from token
    ditti_id, error = _get_ditti_id_from_token(id_token)
    if error:
        return error

    # Return success with ditti ID
    return create_success_response(
        data={
            "dittiId": ditti_id,
            "msg": "Login successful"
        }
    )


@blueprint.route("/register/participant", methods=["POST"])
@researcher_auth_required("Create", "Participants")
def register_participant(account):
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
            - 200 OK: Participant registered successfully.
            - 400 Bad Request: Missing required fields.
            - 500 Internal Server Error: AWS Cognito or other server-side errors.
    """
    client = boto3.client("cognito-idp")
    data = request.json.get("data", {})

    try:
        # Extract required fields
        cognito_username = data.get("cognitoUsername")
        temporary_password = data.get("temporaryPassword")

        # Validate required fields
        if not cognito_username or not temporary_password:
            return create_error_response(
                "Missing required information",
                status_code=400,
                error_code="MISSING_FIELDS"
            )

        # Create user in Cognito
        user_pool_id = current_app.config["COGNITO_PARTICIPANT_USER_POOL_ID"]
        client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=cognito_username,
            TemporaryPassword=temporary_password,
            MessageAction="SUPPRESS"
        )

        return create_success_response(
            data={
                "username": cognito_username,
                "msg": "Registration successful"
            }
        )

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        logger.error(f"Cognito registration error: {error_code}")
        return create_error_response(
            "Registration failed. Please try again.",
            status_code=500,
            error_code=f"COGNITO_ERROR_{error_code}"
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return create_error_response(
            "Registration failed. Please try again.",
            status_code=500,
            error_code="REGISTRATION_ERROR"
        )
