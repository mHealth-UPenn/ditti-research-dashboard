import logging
import boto3
from botocore.exceptions import ClientError
from flask import Blueprint, current_app, request
from aws_portal.auth.decorators import researcher_auth_required
from aws_portal.auth.controllers import ParticipantAuthController
from aws_portal.auth.providers.cognito import AUTH_ERROR_MESSAGES
from aws_portal.auth.utils.responses import create_error_response, create_success_response

blueprint = Blueprint("participant_auth", __name__,
                      url_prefix="/auth/participant")
logger = logging.getLogger(__name__)

# Create auth controller instance
auth_controller = ParticipantAuthController()


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
    return auth_controller.login()


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
    return auth_controller.callback()


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
    return auth_controller.logout()


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
    return auth_controller.check_login()


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
            data={"username": cognito_username},
            message=AUTH_ERROR_MESSAGES["registration_successful"]
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
