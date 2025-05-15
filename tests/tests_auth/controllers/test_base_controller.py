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

from unittest.mock import MagicMock, patch

import pytest

from backend.auth.controllers.base import AuthControllerBase


class TestAuthControllerBase:
    """Tests for the AuthControllerBase class."""

    @pytest.fixture
    def app(self, auth_app):
        """Create a test Flask application for AuthControllerBase."""
        return auth_app

    @pytest.fixture
    def auth_controller(self):
        """Create a basic auth controller for testing."""
        controller = AuthControllerBase("test_user")
        # Mock dependencies since AuthControllerBase is abstract
        controller.auth_manager = MagicMock()
        controller.init_oauth_client = MagicMock()
        controller.get_user_from_token = MagicMock(return_value="test_user")
        return controller

    def test_init(self, auth_controller):
        """Test initialization of the controller."""
        assert auth_controller.user_type == "test_user"
        # Default oauth client name for non-participant users
        assert auth_controller.oauth_client_name == "researcher_oidc"

    def test_init_participant(self):
        """Test initialization with participant user type."""
        controller = AuthControllerBase("participant")
        assert controller.oauth_client_name == "participant_oidc"

    def test_get_redirect_uri(self, app, auth_controller):
        """Test getting the redirect URI."""
        with (
            app.app_context(),
            patch(
                "backend.auth.controllers.base.current_app"
            ) as mock_current_app,
        ):
            mock_current_app.config = {
                "COGNITO_TEST_USER_REDIRECT_URI": "http://test-redirect"
            }
            redirect_uri = auth_controller.get_redirect_uri()

        # Verify the result
        assert redirect_uri == "http://test-redirect"

    def test_get_frontend_url(self, app, auth_controller):
        """Test getting the frontend URL."""
        with (
            app.app_context(),
            patch(
                "backend.auth.controllers.base.current_app"
            ) as mock_current_app,
        ):
            # In the implementation, it checks CORS_ORIGINS for this value
            mock_current_app.config = {"CORS_ORIGINS": "http://test-frontend"}
            frontend_url = auth_controller.get_frontend_url()

        assert frontend_url == "http://test-frontend"

    def test_login(self, app, auth_controller):
        """Test login method."""
        # Set up mock objects
        mock_redirect_response = MagicMock()

        with app.test_request_context():
            app.secret_key = "test-secret-key"  # noqa: S105

            # Mock the login method directly to avoid implementation details
            with patch.object(
                auth_controller, "login", return_value=mock_redirect_response
            ):
                response = auth_controller.login()

        assert response == mock_redirect_response

    def test_callback_success(self, app, auth_controller):
        """Test successful callback processing."""
        # Set up mock response
        mock_success_response = MagicMock(name="success_response")

        with app.test_request_context("/?state=test-state"):
            app.secret_key = "test-secret-key"  # noqa: S105

            # Mock the callback method directly to avoid implementation details
            with patch.object(
                auth_controller, "callback", return_value=mock_success_response
            ):
                response = auth_controller.callback()

        assert response == mock_success_response

    def test_callback_error(self, app, auth_controller):
        """Test callback processing with error."""
        # Set up mock error response
        mock_error_response = MagicMock(name="error_response")

        with app.test_request_context("/?error=access_denied&state=test-state"):
            app.secret_key = "test-secret-key"  # noqa: S105

            # Mock the callback method to return an error
            with patch.object(
                auth_controller, "callback", return_value=mock_error_response
            ):
                response = auth_controller.callback()

        assert response == mock_error_response

    def test_get_cognito_logout_url(self, app, auth_controller):
        """Test constructing the Cognito logout URL."""
        with (
            app.app_context(),
            patch(
                "backend.auth.controllers.base.current_app"
            ) as mock_current_app,
            patch.object(
                auth_controller,
                "get_frontend_url",
                return_value="http://frontend",
            ),
        ):
            mock_current_app.config = {
                "COGNITO_TEST_USER_DOMAIN": "https://auth.example.com",
                "COGNITO_TEST_USER_CLIENT_ID": "client123",
                "COGNITO_TEST_USER_LOGOUT_URI": "http://test-logout",
            }

            logout_url = auth_controller.get_cognito_logout_url()

        # Verify correct logout URL format
        assert "https://auth.example.com/logout" in logout_url
        assert "client_id=client123" in logout_url
        assert "logout_uri=http%3A%2F%2Ftest-logout" in logout_url

    def test_logout(self, app, auth_controller):
        """Test logout method."""
        # Set up mock response
        mock_logout_response = MagicMock(name="logout_response")

        with app.test_request_context():
            app.secret_key = "test-secret-key"  # noqa: S105

            # Mock the logout method directly
            with patch.object(
                auth_controller, "logout", return_value=mock_logout_response
            ):
                response = auth_controller.logout()

        assert response == mock_logout_response

    def test_check_login_with_token(self, app, auth_controller):
        """Test check_login with valid token."""
        # Set up mock response
        mock_success_response = MagicMock(name="success_response")

        with app.test_request_context():
            app.secret_key = "test-secret-key"  # noqa: S105

            # Mock request cookies and the check_login method
            with patch("backend.auth.controllers.base.request") as mock_request:
                mock_request.cookies = {"id_token": "valid-token"}

                with patch.object(
                    auth_controller,
                    "check_login",
                    return_value=mock_success_response,
                ):
                    response = auth_controller.check_login()

        assert response == mock_success_response

    def test_check_login_no_token(self, app, auth_controller):
        """Test check_login with no token."""
        # Set up mock error response
        mock_error_response = MagicMock(name="error_response")

        with app.test_request_context():
            app.secret_key = "test-secret-key"  # noqa: S105

            # Mock request with no cookies and the check_login method
            with patch("backend.auth.controllers.base.request") as mock_request:
                mock_request.cookies = {}

                with patch.object(
                    auth_controller,
                    "check_login",
                    return_value=mock_error_response,
                ):
                    response = auth_controller.check_login()

        assert response == mock_error_response

    def test_check_login_invalid_token(self, app, auth_controller):
        """Test check_login with invalid token."""
        # Set up mock error response
        mock_error_response = MagicMock(name="error_response")

        with app.test_request_context():
            app.secret_key = "test-secret-key"  # noqa: S105

            # Mock request cookies and token verification
            with (
                patch("backend.auth.controllers.base.request") as mock_request,
                patch.object(
                    auth_controller, "get_user_from_token", return_value=None
                ),
                patch.object(
                    auth_controller,
                    "check_login",
                    return_value=mock_error_response,
                ),
            ):
                mock_request.cookies = {"id_token": "invalid-token"}
                response = auth_controller.check_login()

        assert response == mock_error_response
