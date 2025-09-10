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
import requests
from botocore.exceptions import ClientError

# This is a bit of a hack to allow the test to import the handler module
# from the `functions` directory. A better solution would be to make
# `functions` a proper python package.
from functions.secret_rotator import handler as rotator_handler

# Constants for testing
SECRET_ARN = (
    "arn:aws:secretsmanager:us-east-1:123456789012:secret:my-secret-123456"
)
CLIENT_REQUEST_TOKEN = "a-very-long-and-unique-guid"
APP_LAMBDA_NAME = "my-test-app-lambda"
APP_URL = "http://fake-app.example.com"


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for the rotator function."""
    monkeypatch.setenv("APP_LAMBDA_FUNCTION_NAME", APP_LAMBDA_NAME)
    monkeypatch.setenv("APP_URL", APP_URL)


@pytest.fixture
def mock_sm_client():
    """Provide a mocked Secrets Manager client."""
    client = MagicMock()
    # Default metadata for a secret enabled for rotation
    client.describe_secret.return_value = {
        "RotationEnabled": True,
        "VersionIdsToStages": {
            CLIENT_REQUEST_TOKEN: ["AWSPENDING"],
            "another-version-id": ["AWSCURRENT"],
        },
    }
    # Default secret value
    client.get_secret_value.return_value = {
        "SecretString": "current-secret-value",
        "VersionId": "another-version-id",
    }
    return client


@pytest.fixture
def mock_lambda_client():
    """Provide a mocked Lambda client."""
    client = MagicMock()
    # Default lambda configuration
    client.get_function_configuration.return_value = {
        "Environment": {"Variables": {"EXISTING_VAR": "value"}}
    }
    return client


def test_handler_exits_if_no_secret_id():
    """Verify the handler exits gracefully if the event is not from Secrets Manager."""
    event = {"Step": "createSecret", "ClientRequestToken": CLIENT_REQUEST_TOKEN}
    # No "SecretId" in event
    assert rotator_handler.lambda_handler(event, None) is None


def test_handler_raises_if_rotation_not_enabled(mock_sm_client):
    """Verify the handler fails if rotation is not enabled on the secret."""
    mock_sm_client.describe_secret.return_value = {"RotationEnabled": False}
    event = {
        "SecretId": SECRET_ARN,
        "Step": "createSecret",
        "ClientRequestToken": CLIENT_REQUEST_TOKEN,
    }
    with (
        patch("boto3.client", return_value=mock_sm_client),
        pytest.raises(ValueError, match="not enabled for rotation"),
    ):
        rotator_handler.lambda_handler(event, None)


@patch("functions.secret_rotator.handler.create_secret")
def test_handler_calls_create_secret(mock_create_secret, mock_sm_client):
    """Test that the handler correctly dispatches to the create_secret function."""
    event = {
        "SecretId": SECRET_ARN,
        "Step": "createSecret",
        "ClientRequestToken": CLIENT_REQUEST_TOKEN,
    }
    with patch("boto3.client", return_value=mock_sm_client):
        rotator_handler.lambda_handler(event, None)
        mock_create_secret.assert_called_once_with(
            mock_sm_client, SECRET_ARN, CLIENT_REQUEST_TOKEN
        )


@patch("functions.secret_rotator.handler.set_secret")
def test_handler_calls_set_secret(mock_set_secret, mock_sm_client):
    """Test that the handler correctly dispatches to the set_secret function."""
    event = {
        "SecretId": SECRET_ARN,
        "Step": "setSecret",
        "ClientRequestToken": CLIENT_REQUEST_TOKEN,
    }
    with patch("boto3.client", return_value=mock_sm_client):
        rotator_handler.lambda_handler(event, None)
        mock_set_secret.assert_called_once()


@patch("functions.secret_rotator.handler.test_secret")
def test_handler_calls_test_secret(mock_test_secret, mock_sm_client):
    """Test that the handler correctly dispatches to the test_secret function."""
    event = {
        "SecretId": SECRET_ARN,
        "Step": "testSecret",
        "ClientRequestToken": CLIENT_REQUEST_TOKEN,
    }
    with patch("boto3.client", return_value=mock_sm_client):
        rotator_handler.lambda_handler(event, None)
        mock_test_secret.assert_called_once_with(CLIENT_REQUEST_TOKEN)


@patch("functions.secret_rotator.handler.finish_secret")
def test_handler_calls_finish_secret(mock_finish_secret, mock_sm_client):
    """Test that the handler correctly dispatches to the finish_secret function."""
    event = {
        "SecretId": SECRET_ARN,
        "Step": "finishSecret",
        "ClientRequestToken": CLIENT_REQUEST_TOKEN,
    }
    with patch("boto3.client", return_value=mock_sm_client):
        rotator_handler.lambda_handler(event, None)
        mock_finish_secret.assert_called_once_with(
            mock_sm_client, SECRET_ARN, CLIENT_REQUEST_TOKEN
        )


def test_create_secret_puts_new_password(mock_sm_client):
    """Test the create_secret function when a new password needs to be generated."""
    # Simulate the AWSPENDING secret not being found
    mock_sm_client.get_secret_value.side_effect = [
        {"SecretString": "current-secret"},  # First call for AWSCURRENT
        ClientError(
            {"Error": {"Code": "ResourceNotFoundException"}}, "GetSecretValue"
        ),  # Second for AWSPENDING
    ]
    # Mock the response for get_random_password
    mock_sm_client.get_random_password.return_value = {
        "RandomPassword": "new-password"
    }

    rotator_handler.create_secret(
        mock_sm_client, SECRET_ARN, CLIENT_REQUEST_TOKEN
    )

    # Verify that we tried to get AWSCURRENT and AWSPENDING
    assert mock_sm_client.get_secret_value.call_count == 2
    # Verify a new password was generated
    mock_sm_client.get_random_password.assert_called_once()
    # Verify the new secret was put with the correct parameters
    mock_sm_client.put_secret_value.assert_called_once_with(
        SecretId=SECRET_ARN,
        ClientRequestToken=CLIENT_REQUEST_TOKEN,
        SecretString="new-password",
        VersionStages=["AWSPENDING"],
    )


def test_set_secret_updates_lambda_env(mock_env, mock_lambda_client):
    """Verify that set_secret correctly updates the app lambda's environment."""
    with patch("boto3.client", return_value=mock_lambda_client):
        rotator_handler.set_secret()

        mock_lambda_client.update_function_configuration.assert_called_once()
        # Check that the environment variables passed to the update call are correct
        update_kwargs = (
            mock_lambda_client.update_function_configuration.call_args.kwargs
        )
        assert update_kwargs["FunctionName"] == APP_LAMBDA_NAME
        env_vars = update_kwargs["Environment"]["Variables"]
        assert env_vars["SECRET_VERSION_STAGE"] == "AWSPENDING"
        assert "LAST_SECRET_ROTATION_TIMESTAMP" in env_vars


@patch("functions.secret_rotator.handler.requests.get")
def test_test_secret_success(mock_requests_get, mock_env):
    """Verify test_secret succeeds when the app's health check returns the correct version."""
    # Skip the wait helper to speed up tests
    with patch(
        "functions.secret_rotator.handler._wait_for_lambda_ready",
        return_value=None,
    ):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "flask_secret_key_version_id": CLIENT_REQUEST_TOKEN,
        }
        mock_requests_get.return_value = mock_response

        # The function should run without raising an exception
        rotator_handler.test_secret(CLIENT_REQUEST_TOKEN)

        mock_requests_get.assert_called_once_with(f"{APP_URL}/health", timeout=60)


@patch("functions.secret_rotator.handler.requests.get")
def test_test_secret_fails_on_wrong_version(mock_requests_get, mock_env):
    """Verify test_secret fails if the app returns the wrong secret version ID."""
    # Skip the wait helper to speed up tests
    with patch(
        "functions.secret_rotator.handler._wait_for_lambda_ready",
        return_value=None,
    ):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "flask_secret_key_version_id": "some-other-version-id",
        }
        mock_requests_get.return_value = mock_response

        with pytest.raises(
            ValueError, match="Application is using the wrong secret version"
        ):
            rotator_handler.test_secret(CLIENT_REQUEST_TOKEN)


@patch("functions.secret_rotator.handler.requests.get")
def test_test_secret_fails_on_http_error(mock_requests_get, mock_env):
    """Verify test_secret fails if the health check request fails."""
    # Skip the wait helper to speed up tests
    with patch(
        "functions.secret_rotator.handler._wait_for_lambda_ready",
        return_value=None,
    ):
        mock_requests_get.side_effect = requests.exceptions.RequestException(
            "Connection Error"
        )

        with pytest.raises(requests.exceptions.RequestException):
            rotator_handler.test_secret(CLIENT_REQUEST_TOKEN)


def test_finish_secret_updates_version_stage(
    mock_sm_client, mock_lambda_client, mock_env
):
    """Verify finish_secret promotes AWSPENDING to AWSCURRENT and cleans up the env var."""
    # The current version is 'another-version-id'
    current_version_id = "another-version-id"
    # The version to promote is the CLIENT_REQUEST_TOKEN

    # Configure the mock to return an environment with the temp variable
    mock_lambda_client.get_function_configuration.return_value = {
        "Environment": {
            "Variables": {
                "EXISTING_VAR": "value",
                "SECRET_VERSION_STAGE": "AWSPENDING",
            }
        }
    }

    with patch("boto3.client", return_value=mock_lambda_client):
        rotator_handler.finish_secret(
            mock_sm_client, SECRET_ARN, CLIENT_REQUEST_TOKEN
        )

        # Verify that the secret stage was updated correctly
        mock_sm_client.update_secret_version_stage.assert_called_once_with(
            SecretId=SECRET_ARN,
            VersionStage="AWSCURRENT",
            MoveToVersionId=CLIENT_REQUEST_TOKEN,
            RemoveFromVersionId=current_version_id,
        )

        # Verify the lambda env var was cleaned up
        mock_lambda_client.update_function_configuration.assert_called_once()
        update_kwargs = (
            mock_lambda_client.update_function_configuration.call_args.kwargs
        )
        env_vars = update_kwargs["Environment"]["Variables"]
        assert "SECRET_VERSION_STAGE" not in env_vars
