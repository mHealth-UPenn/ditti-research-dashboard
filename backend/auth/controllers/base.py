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
from urllib.parse import urlencode
from flask import current_app, make_response, redirect, request, session
from backend.extensions import db, oauth
from backend.auth.providers.cognito import AUTH_ERROR_MESSAGES
from backend.auth.utils import (
    clear_auth_cookies, set_auth_cookies, create_error_response, AuthFlowSession
)

logger = logging.getLogger(__name__)


class AuthControllerBase:
    """Base class for authentication controllers."""

    def __init__(self, user_type):
        """Initialize the auth controller.

        Args:
            user_type (str): Either "participant" or "researcher"
        """
        self.user_type = user_type
        self.oauth_client_name = "participant_oidc" if user_type == "participant" else "researcher_oidc"
        self.auth_manager = None  # To be set by subclasses

    def init_oauth_client(self):
        """Initialize the OAuth client."""
        raise NotImplementedError(
            "Subclasses must implement init_oauth_client")

    def get_redirect_uri(self):
        """Get the redirect URI from config.

        Returns:
            str: The redirect URI
        """
        key = f"COGNITO_{self.user_type.upper()}_REDIRECT_URI"
        return current_app.config[key]

    def get_frontend_url(self):
        """Get the frontend URL to redirect to after login.

        Returns:
            str: The frontend URL
        """
        return current_app.config.get("CORS_ORIGINS", "http://localhost:3000")

    def get_login_url(self):
        """Get the login URL.

        Returns:
            str: The login URL
        """
        raise NotImplementedError("Subclasses must implement get_login_url")

    def login(self):
        """Handle login request.

        Returns:
            Response: Redirect to Cognito login page
        """
        # Initialize OAuth client
        self.init_oauth_client()

        # Generate and store security parameters
        security_params = AuthFlowSession.generate_and_store_security_params()

        # Get scope (to be overridden by subclasses)
        scope = self.get_scope()

        # Get redirect URI
        redirect_uri = self.get_redirect_uri()

        # Get OAuth client
        oauth_client = getattr(oauth, self.oauth_client_name)

        # Redirect to Cognito authorization endpoint
        return oauth_client.authorize_redirect(
            redirect_uri,
            scope=scope,
            nonce=security_params["nonce"],
            state=security_params["state"],
            code_challenge=security_params["code_challenge"],
            code_challenge_method="S256"
        )

    def get_scope(self):
        """Get the OAuth scope.

        Returns:
            str: The OAuth scope
        """
        raise NotImplementedError("Subclasses must implement get_scope")

    def callback(self):
        """Handle callback request.

        Returns:
            Response: Redirect to frontend with cookies set
        """
        self.init_oauth_client()

        try:
            # Validate state parameter
            request_state = request.args.get("state")
            if not AuthFlowSession.validate_state(request_state):
                logger.warning("Invalid state parameter in callback")
                redirect_url = self.get_login_url()
                return make_response(redirect(redirect_url))

            # Get code verifier
            code_verifier = AuthFlowSession.get_code_verifier()
            if not code_verifier:
                logger.warning("Missing code_verifier in session")
                return create_error_response(
                    AUTH_ERROR_MESSAGES["invalid_request"],
                    status_code=401,
                    error_code="MISSING_CODE_VERIFIER"
                )

            # Validate nonce
            nonce_valid, nonce = AuthFlowSession.validate_nonce()
            if not nonce_valid:
                return create_error_response(
                    AUTH_ERROR_MESSAGES["session_expired"],
                    status_code=401,
                    error_code="EXPIRED_NONCE"
                )

            # Exchange code for tokens
            oauth_client = getattr(oauth, self.oauth_client_name)
            token = oauth_client.authorize_access_token(
                code_verifier=code_verifier)

            # Parse ID token with nonce validation
            try:
                userinfo = oauth_client.parse_id_token(token, nonce=nonce)
            except Exception as e:
                logger.error(f"Failed to validate ID token: {str(e)}")
                return create_error_response(
                    AUTH_ERROR_MESSAGES["auth_failed"],
                    status_code=401,
                    error_code="TOKEN_VALIDATION_FAILED"
                )

            # Get or create user (to be implemented by subclasses)
            user, error = self.get_or_create_user(token, userinfo)
            if error:
                return error

            # Set session data
            AuthFlowSession.set_user_data(
                self.user_type,
                user.id if hasattr(user, "id") else None,
                userinfo
            )

            # Create redirect response
            redirect_url = self.get_redirect_url()
            response = make_response(redirect(redirect_url))

            # Set cookies
            return set_auth_cookies(response, token)

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            db.session.rollback()
            return create_error_response(
                AUTH_ERROR_MESSAGES["auth_failed"],
                status_code=400,
                error_code="AUTHENTICATION_ERROR"
            )

    def get_or_create_user(self, token, userinfo):
        """Get or create user from token.

        Args:
            token (dict): The token from Cognito
            userinfo (dict): The user info from Cognito

        Returns:
            tuple: (user, error_response)
                user: The user object if successful, None otherwise
                error_response: Error response if error occurred, None otherwise
        """
        raise NotImplementedError(
            "Subclasses must implement get_or_create_user")

    def get_redirect_url(self):
        """Get the URL to redirect to after login.

        Returns:
            str: The redirect URL
        """
        return self.get_frontend_url()

    def get_cognito_logout_url(self):
        """Build the Cognito logout URL with appropriate parameters.

        Returns:
            str: The Cognito logout URL
        """
        # Get the appropriate configuration based on user type
        prefix = f"COGNITO_{self.user_type.upper()}"
        domain = current_app.config[f"{prefix}_DOMAIN"]
        client_id = current_app.config[f"{prefix}_CLIENT_ID"]
        logout_uri = current_app.config[f"{prefix}_LOGOUT_URI"]

        # Build the query parameters
        params = {
            "client_id": client_id,
            "logout_uri": logout_uri,
            "response_type": "code"
        }

        # Return the full logout URL
        return f"https://{domain}/logout?{urlencode(params)}"

    def logout(self):
        """Handle logout request.

        Returns:
            Response: Redirect to Cognito logout URL
        """
        self.init_oauth_client()

        # Clear session
        session.clear()

        # Create response with redirect to Cognito logout
        response = make_response(redirect(self.get_cognito_logout_url()))

        # Clear cookies
        return clear_auth_cookies(response)

    def check_login(self):
        """Handle check-login request.

        Returns:
            Response: JSON response with user info or error
        """
        self.init_oauth_client()

        # Check for ID token
        id_token = request.cookies.get("id_token")
        if not id_token:
            return create_error_response(
                AUTH_ERROR_MESSAGES["auth_required"],
                status_code=401,
                error_code="NO_TOKEN"
            )

        # Get user from token
        user, error = self.get_user_from_token(id_token)
        if error:
            return error

        # Return success with user info
        return self.create_login_success_response(user)

    def get_user_from_token(self, id_token):
        """Get user from token.

        Args:
            id_token (str): The ID token

        Returns:
            tuple: (user, error_response)
                user: The user object if successful, None otherwise
                error_response: Error response if error occurred, None otherwise
        """
        raise NotImplementedError(
            "Subclasses must implement get_user_from_token")

    def create_login_success_response(self, user):
        """Create success response for check-login.

        Args:
            user: The user object

        Returns:
            Response: JSON response with user info
        """
        raise NotImplementedError(
            "Subclasses must implement create_login_success_response")
