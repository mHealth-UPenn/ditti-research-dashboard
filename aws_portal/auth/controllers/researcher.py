import logging
from flask import current_app
from aws_portal.auth.providers.cognito import ResearcherAuth, init_researcher_oauth_client, AUTH_ERROR_MESSAGES
from aws_portal.auth.controllers.base import AuthControllerBase
from aws_portal.auth.utils import (
    create_error_response, create_success_response, get_researcher_cognito_client,
    get_researcher, create_researcher, update_researcher
)
from aws_portal.extensions import db

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
        return "openid email profile aws.cognito.signin.user.admin"

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
        # Check if this is the first login
        is_first_login = not account.is_confirmed

        # If this is a successful login and the account wasn't previously confirmed,
        # mark it as confirmed now
        if not account.is_confirmed:
            try:
                account.is_confirmed = True
                db.session.commit()
                logger.info(f"Account confirmed for {account.email}")
            except Exception as e:
                logger.error(
                    f"Failed to update account confirmation status: {str(e)}")
                db.session.rollback()

        return create_success_response(
            data={
                "email": account.email,
                "firstName": account.first_name,
                "lastName": account.last_name,
                "accountId": account.id,
                "isFirstLogin": is_first_login,
                "msg": "Login successful"
            }
        )

    def create_account_in_cognito(self, account_data):
        """
        Create a new account in Cognito.

        Args:
            account_data (dict): Account information with keys:
                email, first_name, last_name, phone_number

        Returns:
            tuple: (success, message)
                success: True if account was created successfully, False otherwise
                message: Success/error message
        """
        # Validate required fields
        email = account_data.get("email")
        first_name = account_data.get("first_name")
        last_name = account_data.get("last_name")

        if not email or not first_name or not last_name:
            logger.error("Missing required fields for account creation")
            return False, "Email, first name, and last name are required"

        # Phone number is optional - only include if non-empty
        phone_number = account_data.get("phone_number")
        phone_number = phone_number if phone_number else None

        # Prepare user attributes
        attributes = {
            "given_name": first_name,
            "family_name": last_name
        }

        # Only include phone number if it has a value
        if phone_number:
            attributes["phone_number"] = phone_number

        # Create user in Cognito - let Cognito generate and send temp password
        return create_researcher(email, attributes=attributes)

    def update_account_in_cognito(self, account_data):
        """
        Update an existing account in Cognito.

        Args:
            account_data (dict): Account information with keys:
                email, first_name, last_name, phone_number

        Returns:
            tuple: (success, message)
                success: True if account was updated successfully, False otherwise
                message: Success/error message
        """
        # Validate required fields
        email = account_data.get("email")
        if not email:
            logger.error("Missing email for account update")
            return False, "Email is required for updating an account"

        first_name = account_data.get("first_name")
        last_name = account_data.get("last_name")
        phone_number = account_data.get("phone_number")

        # Prepare user attributes to update
        attributes = {}

        # Only include non-empty required fields
        if first_name is not None:
            attributes["given_name"] = first_name
        if last_name is not None:
            attributes["family_name"] = last_name

        # Phone number is optional - only include if non-empty
        if phone_number:
            attributes["phone_number"] = phone_number

        # Update user in Cognito
        return update_researcher(email, attributes=attributes)

    def disable_account_in_cognito(self, email):
        """
        Disable an account in Cognito.

        Args:
            email (str): The account's email address

        Returns:
            tuple: (success, message)
                success: True if account was disabled successfully, False otherwise
                message: Success/error message
        """
        try:
            client = get_researcher_cognito_client()
            user_pool_id = current_app.config["COGNITO_RESEARCHER_USER_POOL_ID"]

            # Disable user
            client.admin_disable_user(
                UserPoolId=user_pool_id,
                Username=email
            )

            logger.info(f"Disabled Cognito user: {email}")
            return True, "Account disabled successfully"

        except Exception as e:
            logger.error(f"Failed to disable account in Cognito: {str(e)}")
            return False, f"Failed to disable account: {str(e)}"

    def sync_account_with_cognito(self, account):
        """
        Sync an existing database account with Cognito.
        If the account doesn't exist in Cognito, create it.
        If it exists, update its attributes.

        Args:
            account (Account): The account to sync

        Returns:
            tuple: (success, message)
                success: True if account was synced successfully, False otherwise
                message: Success/error message
        """
        # Check if user exists in Cognito
        user_info, _ = get_researcher(account.email)

        account_data = {
            "email": account.email,
            "first_name": account.first_name,
            "last_name": account.last_name,
            "phone_number": account.phone_number
        }

        if user_info:
            # User exists, update attributes
            return self.update_account_in_cognito(account_data)
        else:
            # User doesn't exist, create it
            return self.create_account_in_cognito(account_data)
