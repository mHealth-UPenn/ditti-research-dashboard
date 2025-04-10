import pytest
from unittest.mock import MagicMock
from flask import Flask
from backend.auth.utils.auth_helpers import get_token_from_request, check_permissions


@pytest.fixture
def mock_app():
    """Create a minimal Flask app for testing without database dependencies."""
    app = Flask(__name__)
    return app


def test_get_token_from_request_authorization_header(mock_app):
    """Test extracting token from Authorization header."""
    with mock_app.test_request_context(headers={"Authorization": "Bearer test-token"}):
        token = get_token_from_request()
        assert token == "test-token"


def test_get_token_from_request_cookies(mock_app):
    """Test extracting token from cookies when no Authorization header is present."""
    with mock_app.test_request_context():
        # Simulate a request with cookies but no Authorization header
        from flask import request
        request.cookies = {"id_token": "cookie-token"}

        token = get_token_from_request()
        assert token == "cookie-token"


def test_get_token_from_request_none(mock_app):
    """Test handling when no authentication token is present in either headers or cookies."""
    with mock_app.test_request_context():
        token = get_token_from_request()
        assert token is None


def test_check_permissions_allowed(mock_app):
    """Test permission check passes when user has required permissions."""
    with mock_app.test_request_context(json={"resource": "Accounts"}):
        # Mock an account with sufficient permissions
        account = MagicMock()
        account.get_permissions.return_value = ["some_permissions"]
        # No exception means permission granted
        account.validate_ask.return_value = None

        has_permission, response = check_permissions(
            account, "Create", "Accounts")

        # Verify permission was granted
        assert has_permission is True
        assert response is None

        # Verify correct permission checks were performed
        account.get_permissions.assert_called_once()
        account.validate_ask.assert_called_once_with(
            "Create", "Accounts", ["some_permissions"])


def test_check_permissions_denied(mock_app):
    """Test permission check fails when user lacks required permissions."""
    with mock_app.test_request_context(json={"resource": "Accounts"}):
        # Mock an account with insufficient permissions
        account = MagicMock()
        account.get_permissions.return_value = ["some_permissions"]
        account.validate_ask.side_effect = ValueError(
            "Insufficient permissions")
        account.__str__.return_value = "user@example.com"

        has_permission, response = check_permissions(
            account, "Delete", "Accounts")

        # Verify permission was denied
        assert has_permission is False
        assert response is not None
        assert response.status_code == 403

        # Verify correct permission checks were performed
        account.get_permissions.assert_called_once()
        account.validate_ask.assert_called_once_with(
            "Delete", "Accounts", ["some_permissions"])
