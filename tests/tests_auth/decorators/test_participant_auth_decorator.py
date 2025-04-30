import json
from unittest.mock import MagicMock, patch

from flask import jsonify

from backend.auth.decorators.participant import participant_auth_required

from .test_auth_common import create_mock_response, test_app


class TestParticipantAuthDecorator:
    """Tests for the participant_auth_required decorator."""

    def test_decorator_applied_correctly(self):
        """Test that the decorator correctly creates a wrapper function."""

        @participant_auth_required
        def test_func():
            return "test_result"

        # Verify the wrapper function maintains the same metadata
        assert test_func.__name__ == "test_func"
        test_func.__doc__ = "Test docstring"
        assert test_func.__doc__ == "Test docstring"

    def test_requires_token(self, test_app):
        """Test that the decorator requires a token and returns 401 when missing."""
        with test_app.test_request_context("/test-participant"):
            # Mock empty request (no token in headers or cookies)
            with patch(
                "backend.auth.decorators.participant.request"
            ) as mock_request:
                mock_request.headers = {}
                mock_request.cookies = {}

                @participant_auth_required
                def test_route():
                    return "OK"

                response = test_route()

                # Verify authentication failure response
                assert response.status_code == 401
                data = json.loads(response.get_data(as_text=True))
                assert "msg" in data
                assert data["msg"] == "Authentication required"

    def test_invalid_token_format(self, test_app):
        """Test that the decorator rejects invalid token formats."""
        with test_app.test_request_context("/test-participant"):
            # Mock request with malformed Authorization header
            with patch(
                "backend.auth.decorators.participant.request"
            ) as mock_request:
                mock_request.headers = {"Authorization": "InvalidFormat"}
                mock_request.cookies = {}

                @participant_auth_required
                def test_route():
                    return "OK"

                response = test_route()

                # Verify authentication failure response
                assert response.status_code == 401
                data = json.loads(response.get_data(as_text=True))
                assert "msg" in data
                assert data["msg"] == "Authentication required"

    @patch("backend.auth.decorators.participant.ParticipantAuthController")
    def test_successful_auth(self, MockController, test_app):
        """Test successful authentication flow with valid token."""
        # Configure mock auth controller to return successful authentication
        mock_controller = MagicMock()
        MockController.return_value = mock_controller
        mock_controller.get_user_from_token.return_value = (
            "test_ditti_id",
            None,
        )

        @participant_auth_required
        def test_func(ditti_id):
            return jsonify({"ditti_id": ditti_id, "msg": "OK"})

        # Set up request with valid bearer token
        with test_app.test_request_context(
            "/test-func", headers={"Authorization": "Bearer valid-token"}
        ):
            with test_app.app_context():
                response = test_func()

                # Verify controller interaction
                mock_controller.get_user_from_token.assert_called_once()
                args, kwargs = mock_controller.get_user_from_token.call_args
                assert args[0] == "valid-token"

                # Verify successful response
                assert response.status_code == 200
                data = json.loads(response.get_data(as_text=True))
                assert data["ditti_id"] == "test_ditti_id"
                assert data["msg"] == "OK"

    @patch("backend.auth.decorators.participant.ParticipantAuthController")
    @patch("backend.auth.utils.responses.create_error_response")
    def test_auth_with_exception(
        self, mock_create_error, MockController, test_app
    ):
        """Test exception handling during authentication process."""
        # Configure mocks for error scenario
        mock_controller = MagicMock()
        MockController.return_value = mock_controller

        error_response = create_mock_response(
            {"error": "Internal server error"}, status_code=500
        )
        mock_create_error.return_value = error_response

        # Simulate error response from authentication controller
        mock_controller.get_user_from_token.return_value = (
            None,
            error_response,
        )

        @participant_auth_required
        def test_func(ditti_id):
            return jsonify({"ditti_id": ditti_id, "msg": "OK"})

        # Test with valid-looking but problematic token
        with test_app.test_request_context(
            "/test-func", headers={"Authorization": "Bearer valid-token"}
        ):
            with test_app.app_context():
                response = test_func()

                # Verify error response is passed through
                assert response.status_code == 500
                assert (
                    b"Internal server error" in response.get_data()
                    or b"error" in response.get_data()
                )

    @patch("backend.auth.decorators.participant.ParticipantAuthController")
    def test_auth_failure(self, MockController, test_app):
        """Test authentication failure handling with invalid token."""
        # Configure mock controller to return authentication failure
        mock_controller = MagicMock()
        MockController.return_value = mock_controller

        error_response = create_mock_response(
            {"error": "Invalid token"}, status_code=401
        )
        mock_controller.get_user_from_token.return_value = (
            None,
            error_response,
        )

        @participant_auth_required
        def test_func(ditti_id):
            return jsonify({"ditti_id": ditti_id, "msg": "OK"})

        # Test with explicitly invalid token
        with test_app.test_request_context(
            "/test-func", headers={"Authorization": "Bearer invalid-token"}
        ):
            with test_app.app_context():
                response = test_func()

                # Verify controller interaction
                mock_controller.get_user_from_token.assert_called_once()
                args, kwargs = mock_controller.get_user_from_token.call_args
                assert args[0] == "invalid-token"

                # Verify error response is passed through
                assert response.status_code == 401
                assert b'"error": "Invalid token"' in response.get_data()

    @patch("backend.auth.decorators.participant.ParticipantAuthController")
    def test_token_from_cookie(self, MockController, test_app):
        """Test that the decorator can extract and use tokens from cookies."""
        # Configure mock controller for successful authentication
        mock_controller = MagicMock()
        MockController.return_value = mock_controller
        mock_controller.get_user_from_token.return_value = (
            "test_ditti_id",
            None,
        )

        @participant_auth_required
        def test_func(ditti_id):
            return jsonify({"ditti_id": ditti_id, "msg": "OK"})

        # Test with token in cookie instead of header
        with test_app.test_request_context("/test-func"):
            with test_app.app_context():
                with patch(
                    "backend.auth.decorators.participant.request"
                ) as mock_request:
                    # Set cookie with token but no Authorization header
                    mock_request.headers = {}
                    mock_request.cookies = {"id_token": "cookie-token-value"}

                    response = test_func()

                    # Verify cookie token was used
                    mock_controller.get_user_from_token.assert_called_once()
                    args, kwargs = mock_controller.get_user_from_token.call_args
                    assert args[0] == "cookie-token-value"

                    # Verify successful response
                    assert response.status_code == 200
                    data = json.loads(response.get_data(as_text=True))
                    assert data["ditti_id"] == "test_ditti_id"
                    assert data["msg"] == "OK"
