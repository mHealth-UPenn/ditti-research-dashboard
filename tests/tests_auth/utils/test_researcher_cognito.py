import pytest
from unittest.mock import MagicMock
from flask import Flask
from aws_portal.auth.utils.researcher_cognito import (
    get_researcher_cognito_client,
    create_researcher,
    update_researcher,
    delete_researcher,
    get_researcher
)


@pytest.fixture
def mock_cognito_client(monkeypatch):
    """Create a mock Cognito client for testing."""
    mock_client = MagicMock()

    def mock_boto3_client(*args, **kwargs):
        if args and args[0] == "cognito-idp":
            return mock_client
        return MagicMock()

    monkeypatch.setattr("boto3.client", mock_boto3_client)
    return mock_client


@pytest.fixture
def test_app():
    """Create a test Flask app without database dependencies."""
    app = Flask("test_app")
    app.config["COGNITO_RESEARCHER_REGION"] = "us-west-2"
    app.config["COGNITO_RESEARCHER_USER_POOL_ID"] = "test-pool-id"
    return app


@pytest.fixture
def app_context(test_app):
    """Provide app context for tests."""
    with test_app.app_context():
        yield


def test_get_researcher_cognito_client(mock_cognito_client, app_context):
    """Test getting a Cognito client."""
    # Execute
    client = get_researcher_cognito_client()

    # Verify
    assert client is mock_cognito_client


def test_create_researcher(mock_cognito_client, app_context):
    """Test creating a researcher in Cognito."""
    # Setup
    mock_cognito_client.admin_create_user.return_value = {
        "User": {"Username": "researcher@example.com"}
    }

    # Execute
    success, message = create_researcher(
        email="researcher@example.com",
        temp_password="initial-password",
        attributes={
            "first_name": "Test",
            "last_name": "Researcher"
        }
    )

    # Verify
    assert success is True
    assert message == "User created successfully in Cognito"
    mock_cognito_client.admin_create_user.assert_called_once()

    # Check the arguments
    call_args = mock_cognito_client.admin_create_user.call_args[1]
    assert call_args["UserPoolId"] == "test-pool-id"
    assert call_args["Username"] == "researcher@example.com"
    assert len(call_args["UserAttributes"]) > 0

    # Check attributes
    user_attrs = {attr["Name"]: attr["Value"]
                  for attr in call_args["UserAttributes"]}
    assert user_attrs["email"] == "researcher@example.com"
    assert user_attrs["email_verified"] == "true"


def test_create_researcher_with_error(mock_cognito_client, app_context):
    """Test handling errors when creating researcher."""
    # Setup - simulate error
    mock_cognito_client.admin_create_user.side_effect = Exception(
        "Cognito error")

    # Execute
    success, message = create_researcher(email="researcher@example.com")

    # Verify error message
    assert success is False
    assert "Unexpected error creating user" in message


def test_update_researcher(mock_cognito_client, app_context):
    """Test updating a researcher in Cognito."""
    # Setup
    mock_cognito_client.admin_update_user_attributes.return_value = {}
    mock_cognito_client.admin_delete_user_attributes.return_value = {}

    # Case 1: Normal attribute update
    success, message = update_researcher(
        email="researcher@example.com",
        attributes={
            "first_name": "Updated",
            "last_name": "Name"
        }
    )

    # Verify
    assert success is True
    assert message == "User attributes updated successfully"
    mock_cognito_client.admin_update_user_attributes.assert_called_once()

    # Check the arguments
    call_args = mock_cognito_client.admin_update_user_attributes.call_args[1]
    assert call_args["UserPoolId"] == "test-pool-id"
    assert call_args["Username"] == "researcher@example.com"
    assert len(call_args["UserAttributes"]) > 0

    # Reset mocks
    mock_cognito_client.reset_mock()

    # Case 2: Test attribute deletion
    success, message = update_researcher(
        email="researcher@example.com",
        attributes={"first_name": "Updated"},
        attributes_to_delete=["phone_number"]
    )

    # Verify
    assert success is True
    assert message == "User attributes updated successfully"

    # Verify update was called for regular attributes
    mock_cognito_client.admin_update_user_attributes.assert_called_once()

    # Verify delete was called for attributes to delete
    mock_cognito_client.admin_delete_user_attributes.assert_called_once_with(
        UserPoolId="test-pool-id",
        Username="researcher@example.com",
        UserAttributeNames=["phone_number"]
    )


def test_update_researcher_with_error(mock_cognito_client, app_context):
    """Test handling errors when updating researcher."""
    # Setup - simulate error
    mock_cognito_client.admin_update_user_attributes.side_effect = Exception(
        "Cognito error")

    # Execute
    success, message = update_researcher(
        email="researcher@example.com",
        attributes={"first_name": "Test"}
    )

    # Verify error message
    assert success is False
    assert "Unexpected error updating user" in message


def test_delete_researcher(mock_cognito_client, app_context):
    """Test deleting a researcher in Cognito."""
    # Setup - mock admin_delete_user as used in implementation
    mock_cognito_client.admin_delete_user.return_value = {}

    # Execute
    success, message = delete_researcher(email="researcher@example.com")

    # Verify
    assert success is True
    mock_cognito_client.admin_delete_user.assert_called_once()

    # Check the arguments
    call_args = mock_cognito_client.admin_delete_user.call_args[1]
    assert call_args["UserPoolId"] == "test-pool-id"
    assert call_args["Username"] == "researcher@example.com"


def test_delete_researcher_with_error(mock_cognito_client, app_context):
    """Test handling errors when deleting researcher."""
    # Setup - simulate error
    mock_cognito_client.admin_delete_user.side_effect = Exception(
        "Cognito error")

    # Execute
    success, message = delete_researcher(email="researcher@example.com")

    # Verify error message
    assert success is False
    assert "Unexpected error deleting user" in message


def test_get_researcher(mock_cognito_client, app_context):
    """Test getting a researcher from Cognito."""
    # Setup
    mock_cognito_client.admin_get_user.return_value = {
        "Username": "researcher@example.com",
        "UserAttributes": [
            {"Name": "email", "Value": "researcher@example.com"},
            {"Name": "given_name", "Value": "Test"},
            {"Name": "family_name", "Value": "Researcher"},
            {"Name": "custom:is_confirmed", "Value": "true"}
        ],
        "Enabled": True
    }

    # Execute
    user_info, error = get_researcher(email="researcher@example.com")

    # Verify
    assert error is None
    mock_cognito_client.admin_get_user.assert_called_once()

    # Check the arguments
    call_args = mock_cognito_client.admin_get_user.call_args[1]
    assert call_args["UserPoolId"] == "test-pool-id"
    assert call_args["Username"] == "researcher@example.com"

    # Check result
    assert user_info["username"] == "researcher@example.com"
    assert "attributes" in user_info
    assert user_info["attributes"]["email"] == "researcher@example.com"


def test_get_researcher_with_error(mock_cognito_client, app_context):
    """Test handling errors when getting researcher."""
    # Setup - simulate error
    mock_cognito_client.admin_get_user.side_effect = Exception(
        "Cognito error")

    # Execute
    user_info, error = get_researcher(email="researcher@example.com")

    # Verify
    assert user_info is None
    assert "Unexpected error" in error
