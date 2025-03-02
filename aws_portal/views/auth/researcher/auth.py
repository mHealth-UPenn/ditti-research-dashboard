import logging
from flask import Blueprint, request, current_app, jsonify
from aws_portal.auth.controllers import ResearcherAuthController
from aws_portal.auth.decorators import researcher_auth_required

blueprint = Blueprint("researcher_auth", __name__,
                      url_prefix="/auth/researcher")
logger = logging.getLogger(__name__)

# Create auth controller instance
auth_controller = ResearcherAuthController()


@blueprint.route("/login")
def login():
    """
    Redirect researchers to the Cognito login page.

    This endpoint:
    1. Generates a secure nonce for ID token validation
    2. Generates a secure state parameter for CSRF protection
    3. Generates PKCE code_verifier and code_challenge for authorization code security
    4. Redirects to the Cognito authorization endpoint with all security parameters

    Returns:
        Redirect to Cognito login page
    """
    return auth_controller.login()


@blueprint.route("/callback")
def cognito_callback():
    """
    Handle Cognito's authorization callback for researchers.

    This endpoint:
    1. Validates the state parameter to prevent CSRF attacks
    2. Provides the code_verifier for PKCE validation
    3. Exchanges the authorization code for tokens
    4. Validates the ID token with the stored nonce
    5. Retrieves the researcher in the database
    6. Sets secure cookies with the tokens
    7. Redirects to the frontend application

    Returns:
        Redirect to frontend with tokens set in cookies, or
        400 Bad Request on authentication errors
        403 Forbidden if account is archived
    """
    return auth_controller.callback()


@blueprint.route("/logout")
def logout():
    """
    Log out the researcher from the application and Cognito.

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
    Verify active login status and return the researcher's info.

    This endpoint:
    1. Checks if the ID token exists in cookies
    2. Validates the token and extracts the account
    3. Returns the account info on success

    Returns:
        200 OK with account info on success
        401 Unauthorized if not authenticated or token invalid or account not found
        403 Forbidden if account is archived
    """
    return auth_controller.check_login()


@blueprint.route("/change-password", methods=["POST"])
@researcher_auth_required
def change_password(account):
    """
    Change a researcher's password using boto3.

    This endpoint replaces the deprecated set_password functionality in iam.py.
    It handles both initial password setting and password changes.

    The endpoint uses the researcher_auth_required decorator which ensures
    proper authentication before the function is called.

    Request Body:
        {
            "previousPassword": str,  # Required when changing an existing password
            "newPassword": str        # Required in all cases
        }

    Returns:
        Response: JSON response indicating success or error
    """
    try:
        import boto3
        from botocore.exceptions import ClientError
        from aws_portal.auth.utils.responses import create_error_response, create_success_response

        # Get request data
        data = request.json
        previous_password = data.get("previousPassword")
        new_password = data.get("newPassword")

        # Validate new password is provided
        if not new_password:
            return create_error_response(
                "New password is required",
                status_code=400,
                error_code="MISSING_PASSWORD"
            )

        # Initialize a boto3 client for Cognito
        client = boto3.client('cognito-idp',
                              region_name=current_app.config["COGNITO_RESEARCHER_REGION"])

        # Check if this is a password change or initial password setup
        if previous_password:
            # Scenario 1: Change password for existing user
            # Try to get access token from Authorization header or cookies
            access_token = None

            # Check Authorization header first
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                access_token = auth_header[7:]  # Remove "Bearer " prefix
            else:
                # If not in header, try to get from cookies
                access_token = request.cookies.get("access_token")

            if not access_token:
                return create_error_response(
                    "Valid access token is required. Please make sure you're authenticated.",
                    status_code=401,
                    error_code="MISSING_AUTH"
                )

            # Change password using the access token
            client.change_password(
                PreviousPassword=previous_password,
                ProposedPassword=new_password,
                AccessToken=access_token
            )

            return create_success_response(
                message="Password changed successfully"
            )
        else:
            # Scenario 2: Password setup without previous password
            # We already have the account object from the decorator
            if not account:
                return create_error_response(
                    "Authentication required",
                    status_code=401,
                    error_code="AUTH_REQUIRED"
                )

            # Get username (email) from account
            email = account.email

            # Create a new, random temporary password
            import secrets
            import string
            temp_password = ''.join(secrets.choice(
                string.ascii_letters + string.digits + string.punctuation) for _ in range(20))

            # Get user pool ID from config
            user_pool_id = current_app.config["COGNITO_RESEARCHER_USER_POOL_ID"]

            # Set temporary password for user
            client.admin_set_user_password(
                UserPoolId=user_pool_id,
                Username=email,
                Password=temp_password,
                Permanent=False
            )

            # Authenticate with temporary password to get an access token
            try:
                auth_response = client.admin_initiate_auth(
                    UserPoolId=user_pool_id,
                    ClientId=current_app.config["COGNITO_RESEARCHER_CLIENT_ID"],
                    AuthFlow="ADMIN_USER_PASSWORD_AUTH",
                    AuthParameters={
                        "USERNAME": email,
                        "PASSWORD": temp_password
                    }
                )

                # This should return a challenge to set a new password
                if auth_response.get("ChallengeName") == "NEW_PASSWORD_REQUIRED":
                    # Respond to challenge with new password
                    challenge_response = client.admin_respond_to_auth_challenge(
                        UserPoolId=user_pool_id,
                        ClientId=current_app.config["COGNITO_RESEARCHER_CLIENT_ID"],
                        ChallengeName="NEW_PASSWORD_REQUIRED",
                        ChallengeResponses={
                            "USERNAME": email,
                            "NEW_PASSWORD": new_password
                        },
                        Session=auth_response.get("Session")
                    )

                    # Mark user as confirmed in our database if needed
                    if not account.is_confirmed:
                        account.is_confirmed = True
                        from aws_portal.extensions import db
                        db.session.commit()

                    return create_success_response(
                        message="Password set successfully"
                    )
                else:
                    return create_error_response(
                        "Unexpected authentication response",
                        status_code=500,
                        error_code="AUTH_ERROR"
                    )
            except Exception as e:
                logger.error(f"Error during password setup: {str(e)}")
                return create_error_response(
                    "Password setup failed",
                    status_code=500,
                    error_code="PASSWORD_SETUP_ERROR"
                )

    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.warning(f"Cognito error during password change: {error_code}")

        if error_code == 'NotAuthorizedException':
            return create_error_response(
                "Authorization failed. This could be due to invalid credentials, expired token, or insufficient permissions. Make sure you have the required scopes (aws.cognito.signin.user.admin).",
                status_code=401,
                error_code="AUTHORIZATION_FAILED"
            )
        elif error_code == 'InvalidPasswordException':
            return create_error_response(
                "Password does not meet Cognito requirements. Password must be at least 8 characters, include uppercase and lowercase letters, numbers, and special characters.",
                status_code=400,
                error_code="INVALID_PASSWORD"
            )
        elif error_code == 'LimitExceededException':
            return create_error_response(
                "Too many attempts. Please try again later.",
                status_code=429,
                error_code="TOO_MANY_ATTEMPTS"
            )
        else:
            logger.error(f"Unhandled Cognito error: {error_code}")
            return create_error_response(
                "Failed to change password",
                status_code=500,
                error_code="PASSWORD_CHANGE_ERROR"
            )
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        return create_error_response(
            "Failed to change password",
            status_code=500,
            error_code="PASSWORD_CHANGE_ERROR"
        )


@blueprint.route("/get-access")
@researcher_auth_required
def get_access(account):
    """
    Check whether the user has permissions for an action and resource for a
    given app and study.

    Query Parameters:
        app (str): The app ID (1, 2, or 3)
        study (str): The study ID
        action (str): The action to check permissions for
        resource (str): The resource to check permissions for

    Returns:
        Response: JSON response indicating whether the request is authorized
            200 OK with message "Authorized" if permitted
            200 OK with message "Unauthorized" if not permitted
    """
    msg = "Authorized"
    app_id = request.args.get("app")
    study_id = request.args.get("study")
    action = request.args.get("action")
    resource = request.args.get("resource")
    permissions = account.get_permissions(app_id, study_id)

    try:
        account.validate_ask(action, resource, permissions)
    except ValueError:
        msg = "Unauthorized"

    return jsonify({"msg": msg})
