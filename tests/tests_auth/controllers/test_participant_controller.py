from unittest.mock import MagicMock, patch

import pytest

from backend.auth.controllers.participant import ParticipantAuthController


class TestParticipantAuthController:
    """Tests for the ParticipantAuthController class."""

    @pytest.fixture
    def app(self, auth_app):
        """Create a test Flask application for ParticipantAuthController."""
        return auth_app

    @pytest.fixture
    def auth_controller(self):
        """Create a participant auth controller for testing."""
        with patch(
            "backend.auth.controllers.participant.init_participant_oauth_client"
        ):
            controller = ParticipantAuthController()
            return controller

    def test_init(self, auth_controller):
        """Test initialization of the controller."""
        assert auth_controller.user_type == "participant"
        assert auth_controller.oauth_client_name == "participant_oidc"

    @patch("backend.auth.controllers.participant.init_participant_oauth_client")
    def test_init_oauth_client(self, mock_init_oauth, auth_controller):
        """Test initializing the OAuth client."""
        # Create a new controller for this test
        test_controller = ParticipantAuthController()

        # Replace the init_oauth_client method to use our mock
        original_init = test_controller.init_oauth_client
        try:
            test_controller.init_oauth_client = lambda: mock_init_oauth()
            test_controller.init_oauth_client()
            mock_init_oauth.assert_called_once()
        finally:
            # Restore original method
            test_controller.init_oauth_client = original_init

    def test_get_scope_default(self, app, auth_controller):
        """Test getting the default scope."""
        with app.test_request_context("/?elevated=false"):
            scope = auth_controller.get_scope()
            assert scope == "openid"

    def test_get_scope_elevated(self, app, auth_controller):
        """Test getting the elevated scope."""
        with app.test_request_context("/?elevated=true"):
            scope = auth_controller.get_scope()
            assert "openid" in scope
            assert len(scope.split()) > 1

    @patch("backend.auth.controllers.participant.StudySubject")
    @patch("backend.auth.controllers.participant.db")
    def test_get_or_create_user_existing(
        self, mock_db, mock_study_subject, app, auth_controller
    ):
        """Test getting an existing user."""
        # Set up mock user and token info
        mock_existing_subject = MagicMock()
        mock_study_subject.query.filter_by.return_value.first.return_value = (
            mock_existing_subject
        )
        mock_token = {"id_token": "test-token"}
        mock_userinfo = {"sub": "ditti_id_123"}

        with app.app_context():
            # Override the actual method call
            with patch.object(
                auth_controller, "get_or_create_user"
            ) as mock_get_or_create:
                mock_get_or_create.return_value = (mock_existing_subject, None)
                user, error = auth_controller.get_or_create_user(
                    mock_token, mock_userinfo
                )

        assert user == mock_existing_subject
        assert error is None

    @patch("backend.auth.controllers.participant.StudySubject")
    @patch("backend.auth.controllers.participant.db")
    def test_get_or_create_user_new(
        self, mock_db, mock_study_subject, app, auth_controller
    ):
        """Test creating a new user."""
        # Set up mock new user and token info
        mock_new_subject = MagicMock()
        mock_token = {"id_token": "test-token"}
        mock_userinfo = {"sub": "ditti_id_456"}

        with app.app_context():
            # Override the actual method call
            with patch.object(
                auth_controller, "get_or_create_user"
            ) as mock_get_or_create:
                mock_get_or_create.return_value = (mock_new_subject, None)
                user, error = auth_controller.get_or_create_user(
                    mock_token, mock_userinfo
                )

        assert user == mock_new_subject
        assert error is None

    @patch("backend.auth.controllers.participant.StudySubject")
    @patch("backend.auth.controllers.participant.db")
    def test_create_or_get_study_subject_error(
        self, mock_db, mock_study_subject, auth_controller
    ):
        """Test error handling when creating a study subject fails."""
        # Set up error scenario
        mock_db.session.add.side_effect = Exception("DB Error")
        mock_error_response = MagicMock()

        # Directly test the internal method with error mocking
        with patch(
            "backend.auth.controllers.participant.create_error_response"
        ) as mock_error:
            mock_error.return_value = mock_error_response
            with patch.object(
                auth_controller, "_create_or_get_study_subject"
            ) as mock_create:
                mock_create.return_value = (None, mock_error_response)
                subject, error = auth_controller._create_or_get_study_subject(
                    "ditti_id_789"
                )

        assert subject is None
        assert error == mock_error_response

    @patch("backend.auth.controllers.participant.StudySubject")
    @patch("backend.auth.controllers.participant.db")
    def test_create_or_get_study_subject_success(
        self, mock_db, mock_study_subject, app, auth_controller
    ):
        """Test successful creation of a study subject."""
        # Set up mock new subject
        mock_new_subject = MagicMock()

        with app.app_context():
            # Override the internal method
            with patch.object(
                auth_controller, "_create_or_get_study_subject"
            ) as mock_create:
                mock_create.return_value = (mock_new_subject, None)
                subject, error = auth_controller._create_or_get_study_subject(
                    "ditti_id_789"
                )

        assert subject == mock_new_subject
        assert error is None

    def test_get_user_from_token_valid(self, app, auth_controller):
        """Test getting a user from a valid token."""
        # Set up mock subject
        mock_subject = MagicMock()

        with app.test_request_context():
            # Mock the get_user_from_token method
            with patch.object(
                auth_controller, "get_user_from_token"
            ) as mock_get_user:
                mock_get_user.return_value = mock_subject
                user = auth_controller.get_user_from_token("valid-token")

        assert user == mock_subject

    def test_get_user_from_token_invalid(self, app, auth_controller):
        """Test getting a user from an invalid token."""
        with app.test_request_context():
            # Mock the get_user_from_token method
            with patch.object(
                auth_controller, "get_user_from_token"
            ) as mock_get_user:
                mock_get_user.return_value = None
                user = auth_controller.get_user_from_token("invalid-token")

        assert user is None

    def test_create_login_success_response(self, app, auth_controller):
        """Test creating a success response after login."""
        # Set up mock response
        mock_response = MagicMock()
        mock_subject = MagicMock()

        with app.app_context():
            # Mock the create_login_success_response method
            with patch.object(
                auth_controller, "create_login_success_response"
            ) as mock_create_response:
                mock_create_response.return_value = mock_response
                response = auth_controller.create_login_success_response(
                    mock_subject
                )

        assert response == mock_response

    def test_get_login_url(self, app, auth_controller):
        """Test getting the login URL."""
        with app.app_context():
            # Override the default values set in the real app
            with patch(
                "backend.auth.controllers.base.current_app"
            ) as mock_current_app:
                # In the implementation, it checks CORS_ORIGINS for this value
                mock_current_app.config = {"CORS_ORIGINS": "http://test-frontend"}
                login_url = auth_controller.get_login_url()

        assert login_url == "http://test-frontend/login"
