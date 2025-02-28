import logging
from aws_portal.utils.cognito.auth.researcher import ResearcherAuth, init_researcher_oauth_client
from aws_portal.utils.cognito.constants import AUTH_ERROR_MESSAGES
from aws_portal.utils.cognito.controllers.base import AuthControllerBase
from aws_portal.utils.cognito.utils.responses import create_error_response, create_success_response

logger = logging.getLogger(__name__)


class ResearcherAuthController(AuthControllerBase):
    """Authentication controller for researchers."""

    def __init__(self):
        """Initialize the researcher auth controller."""
        super().__init__("researcher")
        self.auth_manager = ResearcherAuth()

    def init_oauth_client(self):
        """Initialize the OAuth client."""
        init_researcher_oauth_client()

    def get_scope(self):
        """Get the OAuth scope.

        Returns:
            str: The OAuth scope
        """
        return "openid email profile"

    def get_redirect_url(self):
        """Get the URL to redirect to after login.

        Returns:
            str: The redirect URL
        """
        frontend_url = self.get_frontend_url()
        return f"{frontend_url}/coordinator"

    def get_or_create_user(self, token, userinfo):
        """Get researcher account from token.

        Args:
            token (dict): The token from Cognito
            userinfo (dict): The user info from Cognito

        Returns:
            tuple: (account, error_response)
                account: The Account object if successful, None otherwise
                error_response: Error response if error occurred, None otherwise
        """
        # Extract email from userinfo
        email = userinfo.get("email")
        if not email:
            logger.warning("No email found in userinfo")
            return None, create_error_response(
                AUTH_ERROR_MESSAGES["auth_failed"],
                status_code=401,
                error_code="MISSING_EMAIL"
            )

        # Get account
        account, error_msg = self.auth_manager.get_account_from_token(
            token["id_token"])

        if not account:
            # Create appropriate error response based on error message
            if error_msg == "Account unavailable. Please contact support.":
                return None, create_error_response(
                    AUTH_ERROR_MESSAGES["account_archived"],
                    status_code=403,
                    error_code="ACCOUNT_ARCHIVED"
                )
            elif error_msg == "Invalid credentials":
                return None, create_error_response(
                    AUTH_ERROR_MESSAGES["invalid_credentials"],
                    status_code=401,
                    error_code="ACCOUNT_NOT_FOUND"
                )
            else:
                return None, create_error_response(
                    AUTH_ERROR_MESSAGES["auth_failed"],
                    status_code=401,
                    error_code="AUTH_FAILED"
                )

        return account, None

    def get_user_from_token(self, id_token):
        """Get account from token.

        Args:
            id_token (str): The ID token

        Returns:
            tuple: (account, error_response)
                account: The Account object if successful, None otherwise
                error_response: Error response if error occurred, None otherwise
        """
        account, error_msg = self.auth_manager.get_account_from_token(id_token)

        # Convert string error messages to proper error responses
        if not account and error_msg:
            if error_msg == "Account unavailable. Please contact support.":
                return None, create_error_response(
                    AUTH_ERROR_MESSAGES["account_archived"],
                    status_code=403,
                    error_code="ACCOUNT_ARCHIVED"
                )
            elif error_msg == "Invalid credentials":
                return None, create_error_response(
                    AUTH_ERROR_MESSAGES["invalid_credentials"],
                    status_code=401,
                    error_code="ACCOUNT_NOT_FOUND"
                )
            else:
                return None, create_error_response(
                    AUTH_ERROR_MESSAGES["auth_failed"],
                    status_code=401,
                    error_code="AUTH_FAILED"
                )

        return account, error_msg

    def create_login_success_response(self, account):
        """Create success response for check-login.

        Args:
            account: The Account object

        Returns:
            Response: JSON response with account info
        """
        return create_success_response(
            data={
                "email": account.email,
                "firstName": account.first_name,
                "lastName": account.last_name,
                "accountId": account.id,
                "msg": "Login successful"
            }
        )
