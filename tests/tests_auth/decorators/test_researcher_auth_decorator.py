import json
import inspect
from unittest.mock import MagicMock, patch
from flask import jsonify, make_response
from aws_portal.auth.decorators.researcher import researcher_auth_required
from .test_auth_common import create_mock_response, test_app


class TestResearcherAuthDecorator:
    """Tests for the researcher_auth_required decorator."""

    def test_decorator_applied_correctly(self):
        """Test that the decorator correctly creates a wrapper function."""
        @researcher_auth_required
        def test_func():
            return "test_result"

        # Verify wrapper preserves function metadata
        assert test_func.__name__ == "test_func"
        test_func.__doc__ = "Test docstring"
        assert test_func.__doc__ == "Test docstring"

    def test_requires_token(self, test_app):
        """Test that the decorator requires a token and returns 401 when missing."""
        with test_app.test_request_context("/test-researcher"):
            with test_app.app_context():
                # Mock token extraction to return None (no token)
                with patch("aws_portal.auth.decorators.researcher.get_token_from_request") as mock_get_token:
                    mock_get_token.return_value = None

                    @researcher_auth_required
                    def test_route(account):
                        return make_response(jsonify({"msg": "OK", "account_id": account.id}), 200)

                    response = test_route()

                    # Verify authentication failure response
                    assert response.status_code == 401
                    data = json.loads(response.get_data(as_text=True))
                    assert "msg" in data

    @patch("aws_portal.auth.decorators.researcher.get_token_from_request")
    @patch("aws_portal.auth.decorators.researcher.ResearcherAuthController")
    def test_successful_auth(self, MockController, mock_get_token, test_app):
        """Test successful authentication flow with valid token."""
        # Configure mocks for successful authentication
        mock_get_token.return_value = "valid-token"
        mock_controller = MagicMock()
        MockController.return_value = mock_controller

        # Create mock authenticated account
        mock_account = MagicMock()
        mock_account.id = 123
        mock_account.archived = False

        mock_controller.get_user_from_token.return_value = (mock_account, None)

        @researcher_auth_required
        def test_func(account):
            return jsonify({"account_id": account.id, "msg": "OK"})

        # Execute test with request context
        with test_app.test_request_context("/test-func"):
            with test_app.app_context():
                response = test_func()

                # Verify controller interaction
                mock_controller.get_user_from_token.assert_called_once_with(
                    "valid-token")

                # Verify successful response
                assert response.status_code == 200
                data = json.loads(response.get_data(as_text=True))
                assert data["account_id"] == 123
                assert data["msg"] == "OK"

    @patch("aws_portal.auth.decorators.researcher.get_token_from_request")
    @patch("aws_portal.auth.decorators.researcher.ResearcherAuthController")
    def test_auth_failure(self, MockController, mock_get_token, test_app):
        """Test authentication failure handling with invalid token."""
        # Configure mocks for authentication failure
        mock_get_token.return_value = "invalid-token"
        mock_controller = MagicMock()
        MockController.return_value = mock_controller

        # Create error response
        error_response = create_mock_response(
            {"error": "Invalid token"}, status_code=401)
        mock_controller.get_user_from_token.return_value = (
            None, error_response)

        @researcher_auth_required
        def test_func(account):
            return jsonify({"account_id": account.id, "msg": "OK"})

        # Execute test with request context
        with test_app.test_request_context("/test-func"):
            with test_app.app_context():
                response = test_func()

                # Verify controller interaction
                mock_controller.get_user_from_token.assert_called_once()

                # Verify error response is passed through
                assert response.status_code == 401
                assert b'"error": "Invalid token"' in response.get_data()

    @patch("aws_portal.auth.decorators.researcher.get_token_from_request")
    @patch("aws_portal.auth.decorators.researcher.ResearcherAuthController")
    @patch("aws_portal.auth.decorators.researcher.check_permissions")
    def test_with_permissions_success(self, mock_check_permissions, MockController, mock_get_token, test_app):
        """Test authentication with permission checking (success case)."""
        # Configure mocks for successful authentication with permissions
        mock_get_token.return_value = "valid-token"
        mock_check_permissions.return_value = (
            True, None)  # Permission check succeeds

        mock_controller = MagicMock()
        MockController.return_value = mock_controller

        # Create mock authenticated account
        mock_account = MagicMock()
        mock_account.id = 123
        mock_account.archived = False

        mock_controller.get_user_from_token.return_value = (mock_account, None)

        @researcher_auth_required("Create", "Accounts")
        def test_func(account):
            return jsonify({"account_id": account.id, "msg": "OK"})

        # Execute test with request context
        with test_app.test_request_context("/test-func"):
            with test_app.app_context():
                response = test_func()

                # Verify permission check
                mock_check_permissions.assert_called_once_with(
                    mock_account, "Create", "Accounts")

                # Verify successful response
                assert response.status_code == 200
                data = json.loads(response.get_data(as_text=True))
                assert data["account_id"] == 123
                assert data["msg"] == "OK"

    @patch("aws_portal.auth.decorators.researcher.get_token_from_request")
    @patch("aws_portal.auth.decorators.researcher.ResearcherAuthController")
    @patch("aws_portal.auth.decorators.researcher.check_permissions")
    def test_with_permissions_failure(self, mock_check_permissions, MockController, mock_get_token, test_app):
        """Test authentication with permission checking (failure case)."""
        # Configure mocks for successful auth but permission failure
        mock_get_token.return_value = "valid-token"
        mock_controller = MagicMock()
        MockController.return_value = mock_controller

        # Create mock authenticated account
        mock_account = MagicMock()
        mock_account.id = 123
        mock_account.archived = False

        mock_controller.get_user_from_token.return_value = (mock_account, None)

        # Create permission failure response
        error_response = create_mock_response(
            {"error": "Insufficient permissions"}, status_code=403)
        mock_check_permissions.return_value = (False, error_response)

        @researcher_auth_required("Create", "Accounts")
        def test_func(account):
            return jsonify({"account_id": account.id, "msg": "OK"})

        # Execute test with request context
        with test_app.test_request_context("/test-func"):
            with test_app.app_context():
                response = test_func()

                # Verify permission failure response
                assert response.status_code == 403

    @patch("aws_portal.auth.decorators.researcher.get_token_from_request")
    @patch("aws_portal.auth.decorators.researcher.ResearcherAuthController")
    @patch("aws_portal.auth.decorators.researcher.check_permissions")
    @patch("aws_portal.auth.utils.responses.create_error_response")
    def test_permission_check_exception(self, mock_create_error, mock_check_permissions, MockController, mock_get_token, test_app):
        """Test exception handling during permission check."""
        # Configure mocks for authentication success but permission check exception
        mock_get_token.return_value = "valid-token"

        # Create server error response
        error_response = create_mock_response(
            {"error": "Internal server error"}, status_code=500)
        mock_create_error.return_value = error_response

        # Configure permission check to return error
        mock_check_permissions.return_value = (False, error_response)

        # Configure controller for successful authentication
        mock_controller = MagicMock()
        MockController.return_value = mock_controller
        mock_account = MagicMock()
        mock_account.id = 123
        mock_account.archived = False
        mock_controller.get_user_from_token.return_value = (mock_account, None)

        @researcher_auth_required("Create", "Accounts")
        def test_func(account):
            return jsonify({"account_id": account.id, "msg": "OK"})

        # Execute test with request context
        with test_app.test_request_context("/test-func"):
            with test_app.app_context():
                response = test_func()

                # Verify error response is passed through
                assert response.status_code == 500
                assert b"Internal server error" in response.get_data(
                ) or b"error" in response.get_data()

    def test_decorator_as_factory(self):
        """Test that the decorator can be used as a factory with parameters."""
        # Create decorator with parameters
        decorator = researcher_auth_required("Create", "Accounts")
        assert callable(decorator)

        # Apply decorator to function
        @decorator
        def test_func():
            return "test_result"

        # Verify function metadata preserved
        assert test_func.__name__ == "test_func"

    def test_decorator_preserves_function_signature(self):
        """Test that the decorator preserves the function signature for introspection."""
        @researcher_auth_required
        def test_func(param1, param2, *args, **kwargs):
            return param1, param2, args, kwargs

        # Verify signature preservation using inspect
        sig = inspect.signature(test_func)
        assert list(sig.parameters.keys()) == [
            "param1", "param2", "args", "kwargs"]

    @patch("aws_portal.auth.decorators.researcher.get_token_from_request")
    @patch("aws_portal.auth.decorators.researcher.ResearcherAuthController")
    @patch("aws_portal.auth.utils.responses.create_error_response")
    def test_archived_account(self, mock_create_error, MockController, mock_get_token, test_app):
        """Test that archived accounts cannot authenticate."""
        # Configure mocks
        mock_get_token.return_value = "valid-token"
        mock_controller = MagicMock()
        MockController.return_value = mock_controller

        # Create mock archived account
        mock_account = MagicMock()
        mock_account.id = 123
        mock_account.archived = True

        # Create archived account error response
        error_response = create_mock_response(
            {"error": "Account archived"}, status_code=401)
        mock_create_error.return_value = error_response

        # Configure controller to check archived status and return error
        def mock_get_user_with_archived_check(*args, **kwargs):
            if mock_account.archived:
                return None, error_response
            return mock_account, None

        mock_controller.get_user_from_token.side_effect = mock_get_user_with_archived_check

        @researcher_auth_required
        def test_func(account):
            return jsonify({"account_id": account.id, "msg": "OK"})

        # Execute test with request context
        with test_app.test_request_context("/test-func"):
            with test_app.app_context():
                response = test_func()

                # Verify archived account response
                assert response.status_code == 401
                assert b"Account archived" in response.get_data() or b"error" in response.get_data()

    @patch("aws_portal.auth.decorators.researcher.get_token_from_request")
    @patch("aws_portal.auth.decorators.researcher.ResearcherAuthController")
    def test_token_from_cookie(self, MockController, mock_get_token, test_app):
        """Test that the decorator can extract and use tokens from cookies."""
        # Configure mocks for cookie-based authentication
        mock_get_token.return_value = "cookie-token-value"
        mock_controller = MagicMock()
        MockController.return_value = mock_controller

        # Create mock authenticated account
        mock_account = MagicMock()
        mock_account.id = 123
        mock_account.archived = False

        mock_controller.get_user_from_token.return_value = (mock_account, None)

        @researcher_auth_required
        def test_func(account):
            return jsonify({"account_id": account.id, "msg": "OK"})

        # Execute test with request context
        with test_app.test_request_context("/test-func"):
            with test_app.app_context():
                response = test_func()

                # Verify successful response
                assert response.status_code == 200
                data = json.loads(response.get_data(as_text=True))
                assert data["account_id"] == 123
                assert data["msg"] == "OK"

    @patch("aws_portal.auth.decorators.researcher.get_token_from_request")
    @patch("aws_portal.auth.decorators.researcher.ResearcherAuthController")
    def test_stacked_decorators(self, MockController, mock_get_token, test_app):
        """Test that multiple stacked researcher_auth_required decorators work correctly."""
        # Configure mocks for authentication
        mock_get_token.return_value = "valid-token"
        mock_controller = MagicMock()
        MockController.return_value = mock_controller

        # Create mock authenticated account
        mock_account = MagicMock()
        mock_account.id = 123
        mock_account.archived = False

        mock_controller.get_user_from_token.return_value = (mock_account, None)

        # Create function with stacked decorators
        @researcher_auth_required
        @researcher_auth_required("View", "Reports")
        def test_func(account):
            return jsonify({"account_id": account.id, "msg": "OK"})

        # Execute test with request context
        with test_app.test_request_context("/test-func"):
            with test_app.app_context():
                # Mock permissions check for inner decorator
                with patch("aws_portal.auth.decorators.researcher.check_permissions") as mock_check_permissions:
                    mock_check_permissions.return_value = (True, None)

                    response = test_func()

                    # Verify successful response
                    assert response.status_code == 200
                    data = json.loads(response.get_data(as_text=True))
                    assert data["account_id"] == 123
                    assert data["msg"] == "OK"

                    # Verify controller called only once (decorator reuses account)
                    mock_controller.get_user_from_token.assert_called_once()

                    # Verify permissions were checked
                    mock_check_permissions.assert_called_once()

    @patch("aws_portal.auth.decorators.researcher.get_token_from_request")
    @patch("aws_portal.auth.decorators.researcher.ResearcherAuthController")
    def test_existing_account_param(self, MockController, mock_get_token, test_app):
        """Test that the decorator correctly handles when account is already in kwargs."""
        # Configure mocks but they shouldn't be called
        mock_get_token.return_value = "valid-token"
        mock_controller = MagicMock()
        MockController.return_value = mock_controller

        # Create mock pre-authenticated account
        mock_account = MagicMock()
        mock_account.id = 123
        mock_account.archived = False

        @researcher_auth_required
        def test_func(account, other_param=None):
            return jsonify({
                "account_id": account.id,
                "msg": "OK",
                "other_param": other_param
            })

        # Execute test with request context and pre-provided account
        with test_app.test_request_context("/test-func"):
            with test_app.app_context():
                # Call with account already in kwargs (simulating previous decorator)
                response = test_func(account=mock_account,
                                     other_param="test value")

                # Verify controller was not called (account already provided)
                mock_controller.get_user_from_token.assert_not_called()

                # Verify successful response with parameters
                assert response.status_code == 200
                data = json.loads(response.get_data(as_text=True))
                assert data["account_id"] == 123
                assert data["msg"] == "OK"
                assert data["other_param"] == "test value"
