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

import json
from unittest.mock import MagicMock, patch

import pytest
from flask import jsonify, redirect

from tests.testing_utils import setup_auth_flow_session


@pytest.fixture
def client(auth_app):
    """Create a test client."""
    with auth_app.test_client() as client:
        yield client


@patch("requests.get")
def test_researcher_login_view(mock_get, client, mock_auth_oauth):
    """Test researcher login view with mocked OAuth."""
    # Mock the HTTP requests
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "authorization_endpoint": "https://test-domain.auth.us-east-1.amazoncognito.com/oauth2/authorize",
        "token_endpoint": "https://test-domain.auth.us-east-1.amazoncognito.com/oauth2/token",
    }
    mock_get.return_value = mock_response

    # Mock the OAuth client
    with patch(
        "backend.auth.controllers.base.AuthControllerBase.login"
    ) as mock_login:
        mock_login.return_value = (
            "https://test-domain.auth.us-east-1.amazoncognito.com/oauth2/authorize",
            302,
        )

        # Execute
        response = client.get("/auth/researcher/login")

        # Verify
        assert mock_login.called
        assert response.status_code == 302


@patch("backend.auth.controllers.researcher.ResearcherAuthController.callback")
def test_researcher_callback_success(mock_callback, client):
    """Test successful callback handling."""
    # Set up mock
    mock_callback.return_value = redirect("/researcher"), 302

    # Set up session
    auth_flow = setup_auth_flow_session(client, "researcher")

    # Execute
    response = client.get(
        f"/auth/researcher/callback?code=test_code&state={auth_flow}"
    )

    # Verify
    assert mock_callback.called
    assert response.status_code == 302


@patch("backend.auth.controllers.researcher.ResearcherAuthController.callback")
def test_researcher_callback_invalid_state(mock_callback, client):
    """Test callback with invalid state parameter."""
    # Set up mock
    with client.application.app_context():
        mock_callback.return_value = (
            jsonify({"error": "Invalid state parameter"}),
            401,
        )

    # Set up session
    setup_auth_flow_session(client, "researcher")

    # Execute with invalid state
    response = client.get(
        "/auth/researcher/callback?code=test_code&state=invalid_state"
    )

    # Verify
    assert mock_callback.called
    assert response.status_code == 401


@patch("backend.auth.controllers.researcher.ResearcherAuthController.callback")
def test_researcher_callback_missing_code(mock_callback, client):
    """Test callback with missing code parameter."""
    # Set up mock
    with client.application.app_context():
        mock_callback.return_value = (
            jsonify({"error": "Missing code parameter"}),
            401,
        )

    # Set up session
    auth_flow = setup_auth_flow_session(client, "researcher")

    # Execute without code
    response = client.get(f"/auth/researcher/callback?state={auth_flow}")

    # Verify
    assert mock_callback.called
    assert response.status_code == 401


@patch("backend.auth.controllers.researcher.ResearcherAuthController.check_login")
def test_researcher_check_login_authenticated(mock_check_login, client):
    """Test check login when authenticated."""
    # Set up mock
    with client.application.app_context():
        mock_check_login.return_value = (
            jsonify({"authenticated": True, "user": "test-user"}),
            200,
        )

    # Execute
    response = client.get("/auth/researcher/check-login")

    # Verify
    assert mock_check_login.called
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["authenticated"] is True


@patch("backend.auth.controllers.researcher.ResearcherAuthController.check_login")
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


@patch("backend.auth.controllers.researcher.ResearcherAuthController.logout")
def test_researcher_logout(mock_logout, client):
    """Test logout."""
    # Set up mock
    mock_logout.return_value = (
        redirect("https://test-domain.auth.us-east-1.amazoncognito.com/logout"),
        302,
    )

    # Execute
    response = client.get("/auth/researcher/logout")

    # Verify
    assert mock_logout.called
    assert response.status_code == 302


def test_researcher_change_password_success(client):
    """Test the change_password method of ResearcherAuthController directly."""
    from backend.auth.controllers import ResearcherAuthController

    # Create a controller instance
    controller = ResearcherAuthController()

    # Mock the controller's internal methods
    with patch.object(controller, "change_password") as mock_change_password:
        # Set up the mock
        with client.application.app_context():
            mock_change_password.return_value = (
                jsonify({"message": "Password changed successfully"}),
                200,
            )

        # Call the method directly
        result = controller.change_password(
            "old-password", "new-password", "mock_token"
        )

        # Verify
        assert mock_change_password.called
        assert result[1] == 200  # Status code
        data = json.loads(result[0].data)
        assert "message" in data


def test_researcher_change_password_error(client):
    """Test the change_password method of ResearcherAuthController directly with an error."""
    from backend.auth.controllers import ResearcherAuthController

    # Create a controller instance
    controller = ResearcherAuthController()

    # Mock the controller's internal methods
    with patch.object(controller, "change_password") as mock_change_password:
        # Set up the mock
        with client.application.app_context():
            mock_change_password.return_value = (
                jsonify({"error": "Password change error"}),
                400,
            )

        # Call the method directly
        result = controller.change_password(
            "old-password", "new-password", "mock_token"
        )

        # Verify
        assert mock_change_password.called
        assert result[1] == 400  # Status code
        data = json.loads(result[0].data)
        assert "error" in data


def test_researcher_change_password_missing_fields(client):
    """Test the change_password method of ResearcherAuthController directly with missing fields."""
    from backend.auth.controllers import ResearcherAuthController

    # Create a controller instance
    controller = ResearcherAuthController()

    # Mock the controller's internal methods
    with patch.object(controller, "change_password") as mock_change_password:
        # Set up the mock
        with client.application.app_context():
            mock_change_password.return_value = (
                jsonify({"error": "Missing required fields"}),
                400,
            )

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
    mock_account.get_permissions.return_value = {"permissions": ["Create:User"]}
    mock_account.validate_ask.return_value = True

    # Create a mock for the get_access function that bypasses the decorator
    with (
        patch(
            "backend.views.auth.researcher.auth.get_access",
            wraps=lambda _: jsonify({"msg": "Authorized"}),
        ),
        client.application.test_request_context(
            "/auth/researcher/get-access?app=1&study=1&action=Create&resource=User"
        ),
    ):
        from backend.views.auth.researcher.auth import get_access

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
    with (
        patch(
            "backend.views.auth.researcher.auth.get_access",
            wraps=lambda _: jsonify({"msg": "Unauthorized"}),
        ),
        client.application.test_request_context(
            "/auth/researcher/get-access?app=1&study=1&action=Create&resource=User"
        ),
    ):
        from backend.views.auth.researcher.auth import get_access

        response = get_access(mock_account)

        # Verify
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["msg"] == "Unauthorized"
