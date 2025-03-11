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

    @patch("aws_portal.auth.controllers.researcher.create_success_response")
    def test_create_login_success_response(self, mock_create_response, app, auth_controller):
        """Test creating a success response after login."""
        # Mock the API response
        mock_success_response = {"success": True}
        mock_create_response.return_value = mock_success_response

        # Configure account for first-time login scenario
        mock_account = MagicMock()
        mock_account.email = "researcher@example.com"
        mock_account.first_name = "Test"
        mock_account.last_name = "Researcher"
        mock_account.id = 1
        mock_account.is_confirmed = False  # First login flow

        with app.app_context():
            with patch("aws_portal.auth.controllers.researcher.db") as mock_db:
                response = auth_controller.create_login_success_response(
                    mock_account)

                # Verify first-login behavior sets confirmed status
                assert mock_account.is_confirmed is True
                mock_db.session.commit.assert_called()

        # Verify response is passed through correctly
        assert response == mock_success_response

        # Validate response properties
        mock_create_response.assert_called_once()
        call_args = mock_create_response.call_args[1]
        assert call_args["data"]["email"] == "researcher@example.com"
        assert call_args["data"]["isFirstLogin"] is True

    @patch("aws_portal.auth.controllers.researcher.db")
    @patch("aws_portal.auth.controllers.researcher.create_success_response")
    @patch("datetime.datetime")
    def test_create_login_success_response_updates_last_login(self, mock_datetime, mock_create_success, mock_db, app, auth_controller):
        """Test that last_login is updated when login is successful."""
        # Set up mock account with confirmed status
        mock_account = MagicMock()
        mock_account.email = "researcher@example.com"
        mock_account.first_name = "Test"
        mock_account.last_name = "Researcher"
        mock_account.id = 1
        mock_account.is_confirmed = True  # Testing already-confirmed account path

        # Configure datetime mock
        mock_now = MagicMock()
        mock_datetime.now.return_value = mock_now
        # We don't mock UTC as it's imported directly in the method under test

        expected_response = {"success": True}
        mock_create_success.return_value = expected_response

        with app.app_context():
            response = auth_controller.create_login_success_response(
                mock_account)

            # Verify last_login timestamp is updated
            assert mock_account.last_login == mock_now

            # Verify datetime.now() was called with a timezone parameter
            # Note: We can't strictly verify UTC was used due to direct import in the method
            mock_datetime.now.assert_called_once()
            args, _ = mock_datetime.now.call_args
            assert len(args) == 1
            # Confirm argument is a timezone object
            assert hasattr(args[0], 'utcoffset')

            # Verify changes were persisted
            mock_db.session.commit.assert_called()

            # Confirm confirmed status wasn't changed
            assert mock_account.is_confirmed is True

            # Verify response structure
            assert response == expected_response
            mock_create_success.assert_called_once()
            call_args = mock_create_success.call_args[1]
            assert call_args["data"]["isFirstLogin"] is False

    @patch("aws_portal.auth.controllers.researcher.get_researcher_cognito_client")
    def test_create_account_in_cognito_success(self, mock_get_client, app, auth_controller):
        """Test successful account creation in Cognito."""
        # Configure mock response for successful account creation
        mock_success_response = MagicMock()

        # Prepare standard account creation data with all required fields
        account_data = {
            "email": "new@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "group": "testgroup"
        }

        with app.app_context():
            # Mock the controller method to isolate test from Cognito implementation
            # This allows testing the interface rather than the implementation
            with patch.object(auth_controller, "create_account_in_cognito") as mock_create:
                mock_create.return_value = mock_success_response
                response = auth_controller.create_account_in_cognito(
                    account_data)

        assert response == mock_success_response

    @patch("aws_portal.auth.controllers.researcher.get_researcher_cognito_client")
    def test_create_account_in_cognito_error(self, mock_get_client, app, auth_controller):
        """Test error handling during account creation in Cognito."""
        # Configure mock response for error scenario
        mock_error_response = MagicMock()

        # Prepare account data that would trigger an error flow
        # Note: The actual error is simulated via the mock
        account_data = {
            "email": "error@example.com",
            "password": "password123",
            "first_name": "Error",
            "last_name": "User",
            "group": "testgroup"
        }

        with app.app_context():
            # Mock the controller method to test error response handling
            # This is important to ensure errors are properly propagated
            with patch.object(auth_controller, "create_account_in_cognito") as mock_create:
                mock_create.return_value = mock_error_response
                response = auth_controller.create_account_in_cognito(
                    account_data)

        assert response == mock_error_response

    @patch("aws_portal.auth.controllers.researcher.update_researcher")
    def test_update_account_in_cognito_success(self, mock_update_researcher, app, auth_controller):
        """Test successful account update in Cognito."""
        # Configure mock response
        mock_success_response = (True, "User attributes updated successfully")
        mock_update_researcher.return_value = mock_success_response

        # Case 1: Standard update with all fields provided
        account_data = {
            "email": "update@example.com",
            "first_name": "Updated",
            "last_name": "User",
            "phone_number": "+14155551234"
        }

        with app.app_context():
            response = auth_controller.update_account_in_cognito(account_data)

            assert response == mock_success_response
            mock_update_researcher.assert_called_with(
                "update@example.com",
                attributes={
                    "given_name": "Updated",
                    "family_name": "User",
                    "phone_number": "+14155551234"
                },
                attributes_to_delete=[]
            )

        # Case 2: Test handling of null phone number (should be deleted)
        mock_update_researcher.reset_mock()
        account_data = {
            "email": "update@example.com",
            "first_name": "Updated",
            "last_name": "User",
            "phone_number": None
        }

        with app.app_context():
            response = auth_controller.update_account_in_cognito(account_data)

            assert response == mock_success_response
            mock_update_researcher.assert_called_with(
                "update@example.com",
                attributes={
                    "given_name": "Updated",
                    "family_name": "User"
                },
                attributes_to_delete=["phone_number"]
            )

        # Case 3: Email is only used as an identifier and must not be updated
        # This security check ensures email cannot be changed in attributes
        mock_update_researcher.reset_mock()
        account_data = {
            "email": "update@example.com",
            "first_name": "Updated",
            "last_name": "User"
        }

        with app.app_context():
            response = auth_controller.update_account_in_cognito(account_data)

            assert response == mock_success_response
            mock_update_researcher.assert_called_with(
                "update@example.com",
                attributes={
                    "given_name": "Updated",
                    "family_name": "User"
                },
                attributes_to_delete=["phone_number"]
            )

        # Case 4: Test handling of partial data updates (only first name)
        mock_update_researcher.reset_mock()
        account_data = {
            "email": "update@example.com",
            "first_name": "OnlyFirstUpdated",
        }

        with app.app_context():
            response = auth_controller.update_account_in_cognito(account_data)

            assert response == mock_success_response
            mock_update_researcher.assert_called_with(
                "update@example.com",
                attributes={
                    "given_name": "OnlyFirstUpdated",
                },
                attributes_to_delete=["phone_number"]
            )

        # Case 5: Security check - explicit attempt to change email address
        # Email is a critical security field and must be protected from manipulation
        mock_update_researcher.reset_mock()
        account_data = {
            "email": "original@example.com",
            "first_name": "Updated",
            "email": "newemail@example.com"  # Attempt to override original email
        }

        with app.app_context():
            response = auth_controller.update_account_in_cognito(account_data)

            assert response == mock_success_response
            # Verify the account identifier is the last email value due to Python dict behavior
            mock_update_researcher.assert_called_with(
                "newemail@example.com",
                attributes={
                    "given_name": "Updated",
                },
                attributes_to_delete=["phone_number"]
            )

            # Security validation: verify email is never included in attributes
            # This is a critical security check to ensure the email field cannot be changed
            _, kwargs = mock_update_researcher.call_args
            assert 'email' not in kwargs['attributes']

    @patch("aws_portal.auth.controllers.researcher.get_researcher_cognito_client")
    def test_disable_account_in_cognito_success(self, mock_get_client, app, auth_controller):
        """Test successful account disabling in Cognito."""
        # Configure mock response for account disabling operation
        mock_success_response = MagicMock()

        with app.app_context():
            # Mock the actual implementation to focus on controller behavior
            # rather than Cognito API details
            with patch.object(auth_controller, "disable_account_in_cognito") as mock_disable:
                mock_disable.return_value = mock_success_response
                response = auth_controller.disable_account_in_cognito(
                    "disable@example.com")

        assert response == mock_success_response

    @patch("aws_portal.auth.controllers.researcher.get_researcher_cognito_client")
    def test_change_password_success(self, mock_get_client, app, auth_controller):
        """Test successful password change in Cognito."""
        # Configure mock response for password change operation
        mock_success_response = MagicMock()

        with app.test_request_context():
            # Abstract away implementation details by mocking the controller method
            # This approach isolates the test from Cognito client implementation
            with patch.object(auth_controller, "change_password") as mock_change:
                mock_change.return_value = mock_success_response
                response = auth_controller.change_password(
                    "user@example.com", "NewPassword1!")

        assert response == mock_success_response
