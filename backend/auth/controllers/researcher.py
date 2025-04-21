# Ditti Research Dashboard
# Copyright (C) 2025 the Trustees of the University of Pennsylvania
#
# Ditti Research Dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Ditti Research Dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging

from flask import current_app, request

from backend.auth.controllers.base import AuthControllerBase
from backend.auth.providers.cognito import (
    AUTH_ERROR_MESSAGES,
    ResearcherAuth,
    init_researcher_oauth_client,
)
from backend.auth.utils import (
    create_error_response,
    create_researcher,
    create_success_response,
    get_researcher_cognito_client,
    update_researcher,
)
from backend.extensions import db

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

    def get_login_url(self):
        """Get the login URL.

        Returns:
            str: The login URL
        """
        return f"{self.get_frontend_url()}/coordinator/login"

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
                error_code="MISSING_EMAIL",
            )

        # Get account
        account, error_msg = self.auth_manager.get_account_from_token(
            token["id_token"]
        )

        if not account:
            # Create appropriate error response based on error message
            if error_msg == "Account unavailable. Please contact support.":
                return None, create_error_response(
                    AUTH_ERROR_MESSAGES["account_archived"],
                    status_code=403,
                    error_code="ACCOUNT_ARCHIVED",
                )
            elif error_msg == "Invalid credentials":
                return None, create_error_response(
                    AUTH_ERROR_MESSAGES["invalid_credentials"],
                    status_code=401,
                    error_code="ACCOUNT_NOT_FOUND",
                )
            else:
                return None, create_error_response(
                    AUTH_ERROR_MESSAGES["auth_failed"],
                    status_code=401,
                    error_code="AUTH_FAILED",
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
                    error_code="ACCOUNT_ARCHIVED",
                )
            elif error_msg == "Invalid credentials":
                return None, create_error_response(
                    AUTH_ERROR_MESSAGES["invalid_credentials"],
                    status_code=401,
                    error_code="ACCOUNT_NOT_FOUND",
                )
            else:
                return None, create_error_response(
                    AUTH_ERROR_MESSAGES["auth_failed"],
                    status_code=401,
                    error_code="AUTH_FAILED",
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
                    f"Failed to update account confirmation status: {str(e)}"
                )
                db.session.rollback()

        # Update the last_login timestamp
        try:
            from datetime import UTC, datetime

            account.last_login = datetime.now(UTC)
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to update last_login timestamp: {str(e)}")
            db.session.rollback()

        return create_success_response(
            data={
                "email": account.email,
                "firstName": account.first_name,
                "lastName": account.last_name,
                "accountId": account.id,
                "phoneNumber": account.phone_number,
                "isFirstLogin": is_first_login,
            },
            message=AUTH_ERROR_MESSAGES["login_successful"],
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
            return False, AUTH_ERROR_MESSAGES["missing_required_fields"]

        # Phone number is optional - only include if non-empty
        phone_number = account_data.get("phone_number")
        phone_number = phone_number if phone_number else None

        # Prepare user attributes
        attributes = {"given_name": first_name, "family_name": last_name}

        # Only include phone number if it has a value
        if phone_number:
            attributes["phone_number"] = phone_number

        # Create user in Cognito - let Cognito generate and send temp password
        return create_researcher(email, attributes=attributes)

    def update_account_in_cognito(self, account_data):
        """
        Update an existing account in Cognito.

        Handles both updating standard attributes and deletion of optional attributes.
        For attributes that should be removed (like phone_number), include them in the
        account_data with a None or empty value, and they'll be added to attributes_to_delete.

        Args:
            account_data (dict): Account information with keys:
                email (required): User's email address (used as identifier)
                first_name (optional): User's first name
                last_name (optional): User's last name
                phone_number (optional): User's phone number in E.164 format (+[country code][number])
                                        If explicitly set to None or empty string, the attribute will be deleted

        Returns:
            tuple: (success, message)
                success: True if account was updated successfully, False otherwise
                message: Success/error message
        """
        # Validate required fields
        email = account_data.get("email")
        if not email:
            logger.error("Missing email for account update")
            return False, AUTH_ERROR_MESSAGES["missing_email"]

        first_name = account_data.get("first_name")
        last_name = account_data.get("last_name")
        phone_number = account_data.get("phone_number")

        # Prepare user attributes to update
        attributes = {}
        attributes_to_delete = []

        # Only include non-empty required fields
        if first_name is not None:
            attributes["given_name"] = first_name
        if last_name is not None:
            attributes["family_name"] = last_name

        # Handle phone number - include if non-empty, or mark for deletion if null/empty
        if phone_number:
            attributes["phone_number"] = phone_number
        else:
            # If phone_number is explicitly None or empty string, mark it for deletion
            attributes_to_delete.append("phone_number")

        # Update user in Cognito
        return update_researcher(
            email,
            attributes=attributes,
            attributes_to_delete=attributes_to_delete,
        )

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
            client.admin_disable_user(UserPoolId=user_pool_id, Username=email)

            logger.info(f"Disabled Cognito user: {email}")
            return True, AUTH_ERROR_MESSAGES["account_disabled"]

        except Exception as e:
            logger.error(f"Failed to disable account in Cognito: {str(e)}")
            return False, AUTH_ERROR_MESSAGES["account_disable_error"]

    def sync_account_with_cognito(self, account):
        """
        Synchronize account data with Cognito.

        Args:
            account: The Account object to synchronize

        Returns:
            tuple: (success, message)
                success: True if account was synchronized successfully, False otherwise
                message: Success/error message
        """
        account_data = {
            "email": account.email,
            "first_name": account.first_name,
            "last_name": account.last_name,
            "phone_number": account.phone_number
            if hasattr(account, "phone_number")
            else None,
        }

        return self.update_account_in_cognito(account_data)

    def change_password(self, previous_password, new_password, access_token=None):
        """
        Change a researcher's password in Cognito.

        Args:
            previous_password (str): The user's current password
            new_password (str): The new password to set
            access_token (str, optional): The access token for the user. If not provided,
                                          it will try to get it from the request.

        Returns:
            tuple: (success, message_or_response)
                success: True if password was changed successfully, False otherwise
                message_or_response: Success message or error response object
        """
        try:
            # Validate input parameters
            if not new_password:
                return False, create_error_response(
                    AUTH_ERROR_MESSAGES["missing_password"],
                    status_code=400,
                    error_code="MISSING_PASSWORD",
                )

            if not previous_password:
                return False, create_error_response(
                    AUTH_ERROR_MESSAGES["missing_previous_password"],
                    status_code=400,
                    error_code="MISSING_PREVIOUS_PASSWORD",
                )

            # If no access token was provided, try to get it from the request
            if not access_token and request:
                access_token = request.cookies.get("access_token")

            if not access_token:
                return False, create_error_response(
                    AUTH_ERROR_MESSAGES["auth_required"],
                    status_code=401,
                    error_code="AUTH_REQUIRED",
                )

            # Initialize Cognito client
            client = get_researcher_cognito_client()

            # Change password using the access token
            client.change_password(
                PreviousPassword=previous_password,
                ProposedPassword=new_password,
                AccessToken=access_token,
            )

            return True, create_success_response(
                message=AUTH_ERROR_MESSAGES["password_change_success"]
            )

        except client.exceptions.NotAuthorizedException:
            logger.warning("Incorrect password provided during password change")
            return False, create_error_response(
                AUTH_ERROR_MESSAGES["incorrect_password"],
                status_code=400,
                error_code="INCORRECT_PASSWORD",
            )

        except client.exceptions.InvalidPasswordException:
            logger.warning("Invalid password format during password change")
            return False, create_error_response(
                AUTH_ERROR_MESSAGES["invalid_password"],
                status_code=400,
                error_code="INVALID_PASSWORD",
            )

        except client.exceptions.UserNotFoundException:
            logger.error("User not found during password change")
            return False, create_error_response(
                AUTH_ERROR_MESSAGES["user_not_found"],
                status_code=404,
                error_code="USER_NOT_FOUND",
            )

        except client.exceptions.UserNotConfirmedException:
            logger.error("User not confirmed during password change")
            return False, create_error_response(
                AUTH_ERROR_MESSAGES["user_not_confirmed"],
                status_code=400,
                error_code="USER_NOT_CONFIRMED",
            )

        except client.exceptions.PasswordResetRequiredException:
            logger.warning("Password reset required")
            return False, create_error_response(
                AUTH_ERROR_MESSAGES["password_reset_required"],
                status_code=400,
                error_code="PASSWORD_RESET_REQUIRED",
            )

        except client.exceptions.TooManyRequestsException:
            logger.warning("Rate limit exceeded during password change")
            return False, create_error_response(
                AUTH_ERROR_MESSAGES["too_many_requests"],
                status_code=429,
                error_code="TOO_MANY_REQUESTS",
            )

        except client.exceptions.LimitExceededException:
            logger.warning("Limit exceeded during password change")
            return False, create_error_response(
                AUTH_ERROR_MESSAGES["limit_exceeded"],
                status_code=400,
                error_code="LIMIT_EXCEEDED",
            )

        except client.exceptions.ForbiddenException:
            logger.error("Forbidden request during password change")
            return False, create_error_response(
                AUTH_ERROR_MESSAGES["forbidden"],
                status_code=403,
                error_code="FORBIDDEN",
            )

        except client.exceptions.InvalidParameterException as e:
            logger.error(f"Invalid parameter during password change: {str(e)}")

            # Check the error message to see if it's a password format issue
            error_message = str(e)
            if "proposedPassword" in error_message:
                return False, create_error_response(
                    AUTH_ERROR_MESSAGES["invalid_password"],
                    status_code=400,
                    error_code="INVALID_PASSWORD",
                )
            else:
                return False, create_error_response(
                    AUTH_ERROR_MESSAGES["invalid_parameters"],
                    status_code=400,
                    error_code="INVALID_PARAMETERS",
                )

        except client.exceptions.ResourceNotFoundException:
            logger.error("Resource not found during password change")
            return False, create_error_response(
                AUTH_ERROR_MESSAGES["resource_not_found"],
                status_code=404,
                error_code="RESOURCE_NOT_FOUND",
            )

        except client.exceptions.InternalErrorException:
            logger.error("Cognito internal error during password change")
            return False, create_error_response(
                AUTH_ERROR_MESSAGES["internal_service_error"],
                status_code=500,
                error_code="INTERNAL_SERVICE_ERROR",
            )

        except Exception as e:
            logger.error(f"Unexpected error during password change: {str(e)}")
            return False, create_error_response(
                AUTH_ERROR_MESSAGES["password_change_error"],
                status_code=500,
                error_code="PASSWORD_CHANGE_ERROR",
            )
