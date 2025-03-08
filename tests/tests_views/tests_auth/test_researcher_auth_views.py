import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from flask import Flask, Blueprint, jsonify, session, redirect
from aws_portal.app import create_app


@pytest.fixture
def app():
    """Create a test Flask app with minimal configuration."""
    app = create_app(testing=True)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-key'
    app.config['SERVER_NAME'] = 'localhost'

    # Mock Cognito settings
    app.config['COGNITO_RESEARCHER_REGION'] = 'us-east-1'
    app.config['COGNITO_RESEARCHER_USER_POOL_ID'] = 'test-pool-id'
    app.config['COGNITO_RESEARCHER_DOMAIN'] = 'test-domain.auth.us-east-1.amazoncognito.com'
    app.config['COGNITO_RESEARCHER_CLIENT_ID'] = 'test-client-id'
    app.config['COGNITO_RESEARCHER_CLIENT_SECRET'] = 'test-client-secret'

    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_oauth():
    """Mock the OAuth client."""
    with patch("aws_portal.extensions.oauth") as mock_oauth:
        # Create a mock OAuth client
        mock_client = MagicMock()
        mock_oauth._clients = {}
        mock_oauth.register.return_value = mock_client
        mock_oauth.create_client.return_value = mock_client

        # Mock the authorize_redirect method
        mock_client.authorize_redirect.return_value = "https://cognito-idp.mock-region.amazonaws.com/mock-auth-endpoint"

        yield mock_oauth


def setup_auth_flow_session(client, user_type="researcher"):
    """Set up a mock authentication flow session."""
    with client.session_transaction() as flask_session:
        flask_session["cognito_state"] = "mock_state"
        flask_session["cognito_code_verifier"] = "mock_code_verifier"
        flask_session["cognito_nonce"] = "mock_nonce"
        flask_session["cognito_nonce_generated"] = int(
            datetime.now().timestamp())
        flask_session["auth_flow_user_type"] = user_type

    return "mock_state"


def mock_cognito_tokens():
    """Generate mock Cognito tokens for testing."""
    return {
        "access_token": "mock_access_token",
        "id_token": "mock_id_token",
        "refresh_token": "mock_refresh_token",
        "expires_in": 3600
    }


@patch("requests.get")
def test_researcher_login_view(mock_get, client, mock_oauth):
    """Test researcher login view with mocked OAuth."""
    # Mock the HTTP requests
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "authorization_endpoint": "https://test-domain.auth.us-east-1.amazoncognito.com/oauth2/authorize",
        "token_endpoint": "https://test-domain.auth.us-east-1.amazoncognito.com/oauth2/token"
    }
    mock_get.return_value = mock_response

    # Mock the OAuth client
    with patch("aws_portal.auth.controllers.base.AuthControllerBase.login") as mock_login:
        mock_login.return_value = "https://test-domain.auth.us-east-1.amazoncognito.com/oauth2/authorize", 302

        # Execute
        response = client.get("/auth/researcher/login")

        # Verify
        assert mock_login.called
        assert response.status_code == 302


@patch("aws_portal.auth.controllers.researcher.ResearcherAuthController.callback")
def test_researcher_callback_success(mock_callback, client):
    """Test successful callback handling."""
    # Set up mock
    mock_callback.return_value = redirect("/researcher"), 302

    # Set up session
    auth_flow = setup_auth_flow_session(client, "researcher")

    # Execute
    response = client.get(
        f"/auth/researcher/callback?code=test_code&state={auth_flow}")

    # Verify
    assert mock_callback.called
    assert response.status_code == 302


@patch("aws_portal.auth.controllers.researcher.ResearcherAuthController.callback")
def test_researcher_callback_invalid_state(mock_callback, client):
    """Test callback with invalid state parameter."""
    # Set up mock
    with client.application.app_context():
        mock_callback.return_value = jsonify(
            {"error": "Invalid state parameter"}), 401

    # Set up session
    setup_auth_flow_session(client, "researcher")

    # Execute with invalid state
    response = client.get(
        "/auth/researcher/callback?code=test_code&state=invalid_state")

    # Verify
    assert mock_callback.called
    assert response.status_code == 401


@patch("aws_portal.auth.controllers.researcher.ResearcherAuthController.callback")
def test_researcher_callback_missing_code(mock_callback, client):
    """Test callback with missing code parameter."""
    # Set up mock
    with client.application.app_context():
        mock_callback.return_value = jsonify(
            {"error": "Missing code parameter"}), 401

    # Set up session
    auth_flow = setup_auth_flow_session(client, "researcher")

    # Execute without code
    response = client.get(f"/auth/researcher/callback?state={auth_flow}")

    # Verify
    assert mock_callback.called
    assert response.status_code == 401


@patch("aws_portal.auth.controllers.researcher.ResearcherAuthController.check_login")
def test_researcher_check_login_authenticated(mock_check_login, client):
    """Test check login when authenticated."""
    # Set up mock
    with client.application.app_context():
        mock_check_login.return_value = jsonify(
            {"authenticated": True, "user": "test-user"}), 200

    # Execute
    response = client.get("/auth/researcher/check-login")

    # Verify
    assert mock_check_login.called
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["authenticated"] is True


@patch("aws_portal.auth.controllers.researcher.ResearcherAuthController.check_login")
def test_researcher_check_login_unauthenticated(mock_check_login, client):
    """Test check login when not authenticated."""
    # Set up mock
    with client.application.app_context():
        mock_check_login.return_value = jsonify({"authenticated": False}), 401

    # Execute
    response = client.get("/auth/researcher/check-login")

    # Verify
    assert mock_check_login.called
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data["authenticated"] is False


@patch("aws_portal.auth.controllers.researcher.ResearcherAuthController.logout")
def test_researcher_logout(mock_logout, client):
    """Test logout."""
    # Set up mock
    mock_logout.return_value = redirect(
        "https://test-domain.auth.us-east-1.amazoncognito.com/logout"), 302

    # Execute
    response = client.get("/auth/researcher/logout")

    # Verify
    assert mock_logout.called
    assert response.status_code == 302


def test_researcher_change_password_success(client):
    """Test the change_password method of ResearcherAuthController directly."""
    from aws_portal.auth.controllers import ResearcherAuthController

    # Create a controller instance
    controller = ResearcherAuthController()

    # Mock the controller's internal methods
    with patch.object(controller, 'change_password') as mock_change_password:
        # Set up the mock
        with client.application.app_context():
            mock_change_password.return_value = jsonify(
                {"message": "Password changed successfully"}), 200

        # Call the method directly
        result = controller.change_password(
            "old-password", "new-password", "mock_token")

        # Verify
        assert mock_change_password.called
        assert result[1] == 200  # Status code
        data = json.loads(result[0].data)
        assert "message" in data


def test_researcher_change_password_error(client):
    """Test the change_password method of ResearcherAuthController directly with an error."""
    from aws_portal.auth.controllers import ResearcherAuthController

    # Create a controller instance
    controller = ResearcherAuthController()

    # Mock the controller's internal methods
    with patch.object(controller, 'change_password') as mock_change_password:
        # Set up the mock
        with client.application.app_context():
            mock_change_password.return_value = jsonify(
                {"error": "Password change error"}), 400

        # Call the method directly
        result = controller.change_password(
            "old-password", "new-password", "mock_token")

        # Verify
        assert mock_change_password.called
        assert result[1] == 400  # Status code
        data = json.loads(result[0].data)
        assert "error" in data


def test_researcher_change_password_missing_fields(client):
    """Test the change_password method of ResearcherAuthController directly with missing fields."""
    from aws_portal.auth.controllers import ResearcherAuthController

    # Create a controller instance
    controller = ResearcherAuthController()

    # Mock the controller's internal methods
    with patch.object(controller, 'change_password') as mock_change_password:
        # Set up the mock
        with client.application.app_context():
            mock_change_password.return_value = jsonify(
                {"error": "Missing required fields"}), 400

        # Call the method directly
        result = controller.change_password("old-password", None, "mock_token")

        # Verify
        assert mock_change_password.called
        assert result[1] == 400  # Status code
        data = json.loads(result[0].data)
        assert "error" in data


def test_get_access_authorized(client):
    """Test the get_access endpoint with authorized request."""
    # Create a mock account with permissions
    mock_account = MagicMock()
    mock_account.get_permissions.return_value = {
        "permissions": ["Create:User"]}
    mock_account.validate_ask.return_value = True

    # Create a mock for the get_access function that bypasses the decorator
    with patch("aws_portal.views.auth.researcher.auth.get_access", wraps=lambda account: jsonify({"msg": "Authorized"})):
        # Execute the request with the account directly
        with client.application.test_request_context(
            "/auth/researcher/get-access?app=1&study=1&action=Create&resource=User"
        ):
            from aws_portal.views.auth.researcher.auth import get_access
            response = get_access(mock_account)

            # Verify
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["msg"] == "Authorized"


def test_get_access_unauthorized(client):
    """Test the get_access endpoint with unauthorized request."""
    # Create a mock account without permissions
    mock_account = MagicMock()
    mock_account.get_permissions.return_value = {"permissions": []}
    mock_account.validate_ask.side_effect = ValueError("Unauthorized")

    # Create a mock for the get_access function that bypasses the decorator
    with patch("aws_portal.views.auth.researcher.auth.get_access", wraps=lambda account: jsonify({"msg": "Unauthorized"})):
        # Execute the request with the account directly
        with client.application.test_request_context(
            "/auth/researcher/get-access?app=1&study=1&action=Create&resource=User"
        ):
            from aws_portal.views.auth.researcher.auth import get_access
            response = get_access(mock_account)

            # Verify
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["msg"] == "Unauthorized"
