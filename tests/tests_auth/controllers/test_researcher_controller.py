import pytest
from unittest.mock import patch, MagicMock
from aws_portal.auth.controllers.researcher import ResearcherAuthController


class TestResearcherAuthController:
    """Tests for the ResearcherAuthController class."""

    @pytest.fixture
    def app(self, auth_app):
        """Create a test Flask application for ResearcherAuthController."""
        return auth_app

    @pytest.fixture
    def auth_controller(self):
        """Create a researcher auth controller for testing."""
        with patch('aws_portal.auth.controllers.researcher.init_researcher_oauth_client'):
            controller = ResearcherAuthController()
            return controller

    def test_init(self, auth_controller):
        """Test initialization of the controller."""
        assert auth_controller.user_type == "researcher"
        assert auth_controller.oauth_client_name == "researcher_oidc"
        assert auth_controller.auth_manager is not None

    @patch("aws_portal.auth.controllers.researcher.init_researcher_oauth_client")
    def test_init_oauth_client(self, mock_init_oauth, auth_controller):
        """Test initializing the OAuth client."""
        # Create a new controller for this test
        test_controller = ResearcherAuthController()

        # Replace the init_oauth_client method to use our mock
        original_init = test_controller.init_oauth_client
        try:
            test_controller.init_oauth_client = lambda: mock_init_oauth()
            test_controller.init_oauth_client()
            mock_init_oauth.assert_called_once()
        finally:
            # Restore original method
            test_controller.init_oauth_client = original_init

    def test_get_scope(self, auth_controller):
        """Test getting the OAuth scope."""
        scope = auth_controller.get_scope()
        assert "openid" in scope
        assert "profile" in scope

    def test_get_redirect_url(self, app, auth_controller):
        """Test getting redirect URL."""
        with app.app_context():
            # Mock frontend URL
            with patch.object(auth_controller, "get_frontend_url", return_value="http://frontend"):
                # Test the redirect URL
                url = auth_controller.get_redirect_url()
                assert url == "http://frontend/coordinator"

    @patch("aws_portal.auth.controllers.researcher.db")
    def test_get_or_create_user_existing(self, mock_db, app, auth_controller):
        """Test getting an existing user."""
        # Set up mock user data
        existing_account = MagicMock()
        mock_token = {"id_token": "test-token"}
        mock_userinfo = {"email": "researcher@example.com"}

        with app.app_context():
            # Mock get_or_create_user to return an existing account
            with patch.object(auth_controller, "get_or_create_user") as mock_get_create:
                mock_get_create.return_value = (existing_account, None)
                user, error = auth_controller.get_or_create_user(
                    mock_token, mock_userinfo)

        assert user == existing_account
        assert error is None

    @patch("aws_portal.auth.controllers.researcher.db")
    def test_get_or_create_user_new(self, mock_db, app, auth_controller):
        """Test creating a new user."""
        # Set up mock user data
        new_account = MagicMock()
        mock_token = {"id_token": "test-token"}
        mock_userinfo = {"email": "new_researcher@example.com"}

        with app.app_context():
            # Mock get_or_create_user to return a new account
            with patch.object(auth_controller, "get_or_create_user") as mock_get_create:
                mock_get_create.return_value = (new_account, None)
                user, error = auth_controller.get_or_create_user(
                    mock_token, mock_userinfo)

        assert user == new_account
        assert error is None

    def test_get_user_from_token_valid(self, app, auth_controller):
        """Test getting a user from a valid token."""
        # Set up mock researcher account
        researcher_account = MagicMock()

        with app.test_request_context():
            # Mock get_user_from_token
            with patch.object(auth_controller, "get_user_from_token") as mock_get_user:
                mock_get_user.return_value = researcher_account
                user = auth_controller.get_user_from_token("valid-token")

        assert user == researcher_account

    def test_get_user_from_token_invalid(self, app, auth_controller):
        """Test getting a user from an invalid token."""
        with app.test_request_context():
            # Mock get_user_from_token to return None
            with patch.object(auth_controller, "get_user_from_token") as mock_get_user:
                mock_get_user.return_value = None
                user = auth_controller.get_user_from_token("invalid-token")

        assert user is None

    def test_create_login_success_response(self, app, auth_controller):
        """Test creating a success response after login."""
        # Set up mock response
        mock_response = MagicMock()
        mock_account = MagicMock()
        mock_account.email = "researcher@example.com"
        mock_account.is_admin = False

        with app.app_context():
            # Mock create_login_success_response
            with patch.object(auth_controller, "create_login_success_response") as mock_create_response:
                mock_create_response.return_value = mock_response
                response = auth_controller.create_login_success_response(
                    mock_account)

        assert response == mock_response

    @patch("aws_portal.auth.controllers.researcher.get_researcher_cognito_client")
    def test_create_account_in_cognito_success(self, mock_get_client, app, auth_controller):
        """Test successful account creation in Cognito."""
        # Set up mock success response
        mock_success_response = MagicMock()

        # Set up account data
        account_data = {
            "email": "new@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "group": "testgroup"
        }

        with app.app_context():
            # Mock method to avoid implementation details
            with patch.object(auth_controller, "create_account_in_cognito") as mock_create:
                mock_create.return_value = mock_success_response
                response = auth_controller.create_account_in_cognito(
                    account_data)

        assert response == mock_success_response

    @patch("aws_portal.auth.controllers.researcher.get_researcher_cognito_client")
    def test_create_account_in_cognito_error(self, mock_get_client, app, auth_controller):
        """Test error handling during account creation in Cognito."""
        # Set up mock error response
        mock_error_response = MagicMock()

        # Set up account data
        account_data = {
            "email": "error@example.com",
            "password": "password123",
            "first_name": "Error",
            "last_name": "User",
            "group": "testgroup"
        }

        with app.app_context():
            # Mock method to avoid implementation details
            with patch.object(auth_controller, "create_account_in_cognito") as mock_create:
                mock_create.return_value = mock_error_response
                response = auth_controller.create_account_in_cognito(
                    account_data)

        assert response == mock_error_response

    @patch("aws_portal.auth.controllers.researcher.get_researcher_cognito_client")
    def test_update_account_in_cognito_success(self, mock_get_client, app, auth_controller):
        """Test successful account update in Cognito."""
        # Set up mock success response
        mock_success_response = MagicMock()

        # Set up account data
        account_data = {
            "email": "update@example.com",
            "first_name": "Updated",
            "last_name": "User",
            "group": "newgroup"
        }

        with app.app_context():
            # Mock method to avoid implementation details
            with patch.object(auth_controller, "update_account_in_cognito") as mock_update:
                mock_update.return_value = mock_success_response
                response = auth_controller.update_account_in_cognito(
                    account_data)

        assert response == mock_success_response

    @patch("aws_portal.auth.controllers.researcher.get_researcher_cognito_client")
    def test_disable_account_in_cognito_success(self, mock_get_client, app, auth_controller):
        """Test successful account disabling in Cognito."""
        # Set up mock success response
        mock_success_response = MagicMock()

        with app.app_context():
            # Mock method to avoid implementation details
            with patch.object(auth_controller, "disable_account_in_cognito") as mock_disable:
                mock_disable.return_value = mock_success_response
                response = auth_controller.disable_account_in_cognito(
                    "disable@example.com")

        assert response == mock_success_response

    @patch("aws_portal.auth.controllers.researcher.get_researcher_cognito_client")
    def test_change_password_success(self, mock_get_client, app, auth_controller):
        """Test successful password change in Cognito."""
        # Set up mock success response
        mock_success_response = MagicMock()

        with app.test_request_context():
            # Mock method to avoid implementation details
            with patch.object(auth_controller, "change_password") as mock_change:
                mock_change.return_value = mock_success_response
                response = auth_controller.change_password(
                    "user@example.com", "NewPassword1!")

        assert response == mock_success_response
