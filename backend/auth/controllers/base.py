# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may]
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
from urllib.parse import urlencode

from flask import current_app, make_response, redirect, request, session

from backend.auth.providers.cognito import AUTH_ERROR_MESSAGES
from backend.auth.utils import (
    AuthFlowSession,
    clear_auth_cookies,
    create_error_response,
    set_auth_cookies,
)
from backend.extensions import db, oauth

logger = logging.getLogger(__name__)


class AuthControllerBase:
    """Base class for authentication controllers."""

    def __init__(self, user_type):
        """Initialize the auth controller.

        Parameters
        ----------
            user_type (str): Either "participant" or "researcher"
        """
        self.user_type = user_type
        self.oauth_client_name = (
            "participant_oidc"
            if user_type == "participant"
            else "researcher_oidc"
        )
        self.auth_manager = None  # To be set by subclasses
        logger.debug(
            f"Initialized {user_type} auth controller with OAuth client: {self.oauth_client_name}"
        )

    def init_oauth_client(self):
        """Initialize the OAuth client."""
        logger.debug(f"Initializing OAuth client for {self.user_type}")
        raise NotImplementedError("Subclasses must implement init_oauth_client")

    def get_redirect_uri(self):
        """Get the redirect URI from config.

        Returns
        -------
            str: The redirect URI
        """
        key = f"COGNITO_{self.user_type.upper()}_REDIRECT_URI"
        redirect_uri = current_app.config[key]
        logger.debug(
            f"Retrieved redirect URI for {self.user_type}: {redirect_uri}"
        )
        return redirect_uri

    def get_frontend_url(self):
        """Get the frontend URL to redirect to after login.

        Returns
        -------
            str: The frontend URL
        """
        frontend_url = current_app.config.get(
            "CORS_ORIGINS", "http://localhost:3000"
        )
        logger.debug(f"Retrieved frontend URL: {frontend_url}")
        return frontend_url

    def get_login_url(self):
        """Get the login URL.

        Returns
        -------
            str: The login URL
        """
        raise NotImplementedError("Subclasses must implement get_login_url")

    def login(self):
        """Handle login request.

        Returns
        -------
            Response: Redirect to Cognito login page
        """
        logger.debug(f"Starting login flow for {self.user_type}")

        # Initialize OAuth client
        self.init_oauth_client()

        # Generate and store security parameters
        security_params = AuthFlowSession.generate_and_store_security_params()
        logger.debug(f"Generated security parameters for {self.user_type} login")

        # Get scope (to be overridden by subclasses)
        scope = self.get_scope()
        logger.debug(f"Using OAuth scope for {self.user_type}: {scope}")

        # Get redirect URI
        redirect_uri = self.get_redirect_uri()

        # Get OAuth client
        oauth_client = getattr(oauth, self.oauth_client_name)
        logger.debug(f"Retrieved OAuth client: {self.oauth_client_name}")

        # Redirect to Cognito authorization endpoint
        logger.debug(
            f"Redirecting {self.user_type} to Cognito authorization endpoint"
        )
        return oauth_client.authorize_redirect(
            redirect_uri,
            scope=scope,
            nonce=security_params["nonce"],
            state=security_params["state"],
            code_challenge=security_params["code_challenge"],
            code_challenge_method="S256",
        )

    def get_scope(self):
        """Get the OAuth scope.

        Returns
        -------
            str: The OAuth scope
        """
        raise NotImplementedError("Subclasses must implement get_scope")

    def callback(self):
        """Handle callback request.

        Returns
        -------
            Response: Redirect to frontend with cookies set
        """
        logger.debug(f"Handling callback for {self.user_type}")
        self.init_oauth_client()

        try:
            # Validate state parameter
            request_state = request.args.get("state")
            logger.debug(f"Validating state parameter: {request_state}")
            if not AuthFlowSession.validate_state(request_state):
                logger.warning(
                    f"Invalid state parameter in callback for {self.user_type}"
                )
                redirect_url = self.get_login_url()
                return make_response(redirect(redirect_url))

            # Get code verifier
            code_verifier = AuthFlowSession.get_code_verifier()
            if not code_verifier:
                logger.warning(
                    f"Missing code_verifier in session for {self.user_type}"
                )
                return create_error_response(
                    AUTH_ERROR_MESSAGES["invalid_request"],
                    status_code=401,
                    error_code="MISSING_CODE_VERIFIER",
                )
            logger.debug("Retrieved code verifier from session")

            # Validate nonce
            nonce_valid, nonce = AuthFlowSession.validate_nonce()
            logger.debug(f"Nonce validation result: {nonce_valid}")
            if not nonce_valid:
                return create_error_response(
                    AUTH_ERROR_MESSAGES["session_expired"],
                    status_code=401,
                    error_code="EXPIRED_NONCE",
                )

            # Exchange code for tokens
            oauth_client = getattr(oauth, self.oauth_client_name)
            logger.debug("Exchanging authorization code for tokens")
            token = oauth_client.authorize_access_token(
                code_verifier=code_verifier
            )
            logger.debug("Successfully exchanged code for tokens")

            # Parse ID token with nonce validation
            try:
                logger.debug("Parsing ID token with nonce validation")
                userinfo = oauth_client.parse_id_token(token, nonce=nonce)
                logger.debug(
                    f"Successfully parsed ID token for user: {userinfo.get('email', 'unknown')}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to validate ID token for {self.user_type}: {e!s}"
                )
                return create_error_response(
                    AUTH_ERROR_MESSAGES["auth_failed"],
                    status_code=401,
                    error_code="TOKEN_VALIDATION_FAILED",
                )

            # Get or create user (to be implemented by subclasses)
            logger.debug("Getting or creating user from token")
            user, error = self.get_or_create_user(token, userinfo)
            if error:
                logger.warning(
                    f"Failed to get/create user for {self.user_type}: {error}"
                )
                return error
            logger.debug(
                f"Successfully retrieved/created user: {user.id if hasattr(user, 'id') else 'unknown'}"
            )

            # Update session with authenticated user info
            AuthFlowSession.set_user_data(
                self.user_type,
                user.id if hasattr(user, "id") else None,
                userinfo,
            )
            logger.debug(f"Updated session with user data for {self.user_type}")

            # Set cookies
            redirect_url = self.get_redirect_url()
            logger.debug(
                f"Setting auth cookies and redirecting to: {redirect_url}"
            )
            response = make_response(redirect(redirect_url))
            return set_auth_cookies(response, token)

        except Exception as e:
            logger.error(f"Authentication error for {self.user_type}: {e!s}")
            db.session.rollback()
            return create_error_response(
                AUTH_ERROR_MESSAGES["auth_failed"],
                status_code=400,
                error_code="AUTHENTICATION_ERROR",
            )

    def get_or_create_user(self, token, userinfo):
        """Get or create user from token.

        Parameters
        ----------
            token (dict): The token from Cognito
            userinfo (dict): The user info from Cognito

        Returns
        -------
            tuple: (user, error_response)
                user: The user object if successful, None otherwise
                error_response: Error response if error occurred, None otherwise
        """
        raise NotImplementedError("Subclasses must implement get_or_create_user")

    def get_redirect_url(self):
        """Get the URL to redirect to after login.

        Returns
        -------
            str: The redirect URL
        """
        redirect_url = self.get_frontend_url()
        logger.debug(f"Redirect URL for {self.user_type}: {redirect_url}")
        return redirect_url

    def get_cognito_logout_url(self):
        """Build the Cognito logout URL with appropriate parameters.

        Returns
        -------
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
            "response_type": "code",
        }

        # Return the full logout URL
        logout_url = f"https://{domain}/logout?{urlencode(params)}"
        logger.debug(
            f"Generated Cognito logout URL for {self.user_type}: {logout_url}"
        )
        return logout_url

    def logout(self):
        """Handle logout request.

        Returns
        -------
            Response: Redirect to Cognito logout URL
        """
        logger.debug(f"Handling logout for {self.user_type}")
        self.init_oauth_client()

        # Clear session
        session.clear()
        logger.debug("Cleared session data")

        # Create response with redirect to Cognito logout
        logout_url = self.get_cognito_logout_url()
        logger.debug(f"Redirecting to Cognito logout URL: {logout_url}")
        response = make_response(redirect(logout_url))

        # Clear cookies
        logger.debug("Clearing auth cookies")
        return clear_auth_cookies(response)

    def check_login(self):
        """Handle check-login request.

        Returns
        -------
            Response: JSON response with user info or error
        """
        logger.debug(f"Checking login status for {self.user_type}")
        self.init_oauth_client()

        # Check for ID token
        id_token = request.cookies.get("id_token")
        if not id_token:
            logger.debug(f"No ID token found in cookies for {self.user_type}")
            return create_error_response(
                AUTH_ERROR_MESSAGES["auth_required"],
                status_code=401,
                error_code="NO_TOKEN",
            )
        logger.debug("Found ID token in cookies")

        # Get user from token
        logger.debug("Getting user from token")
        user, error = self.get_user_from_token(id_token)
        if error:
            logger.warning(
                f"Failed to get user from token for {self.user_type}: {error}"
            )
            return error
        logger.debug(
            f"Successfully retrieved user from token: {user.id if hasattr(user, 'id') else 'unknown'}"
        )

        # Return success with user info
        logger.debug("Creating login success response")
        return self.create_login_success_response(user)

    def get_user_from_token(self, id_token):
        """Get user from token.

        Parameters
        ----------
            id_token (str): The ID token

        Returns
        -------
            tuple: (user, error_response)
                user: The user object if successful, None otherwise
                error_response: Error response if error occurred, None otherwise
        """
        raise NotImplementedError("Subclasses must implement get_user_from_token")

    def create_login_success_response(self, user):
        """Create success response for check-login.

        Parameters
        ----------
            user: The user object

        Returns
        -------
            Response: JSON response with user info
        """
        raise NotImplementedError(
            "Subclasses must implement create_login_success_response"
        )
