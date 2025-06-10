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
import requests
from botocore.exceptions import ClientError
from moto import mock_aws

from shared.secrets import get_secret


@pytest.fixture
def mock_lambda_env(monkeypatch):
    """Mock environment variables to simulate a Lambda execution environment."""
    monkeypatch.setenv("AWS_SESSION_TOKEN", "fake-token")
    monkeypatch.setenv("AWS_LAMBDA_RUNTIME_API", "foo.bar")


@pytest.fixture
def mock_aws_credentials(monkeypatch):
    """Mock AWS credentials to prevent boto3 from complaining."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")


def create_secret(
    secret_name,
    secret_data,
    version_id="1",
    version_stages=None,
    previous_version_data=None,
):
    """Helper function to create a secret in the mocked AWS Secrets Manager."""
    from boto3 import client

    if version_stages is None:
        version_stages = ["AWSCURRENT"]

    sm_client = client("secretsmanager")
    sm_client.create_secret(
        Name=secret_name,
        SecretString=json.dumps(secret_data),
    )
    if previous_version_data:
        sm_client.put_secret_value(
            SecretId=secret_name,
            SecretString=json.dumps(previous_version_data),
            VersionStages=["AWSPREVIOUS"],
        )


@mock_aws
def test_get_secret_from_extension_success(mock_lambda_env, mock_aws_credentials):
    """Verify that `get_secret` successfully retrieves a secret via the Lambda extension."""
    secret_name = "my-secret"
    secret_data = {"key": "value"}
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "SecretString": json.dumps(secret_data),
        "VersionId": "1",
        "VersionStages": ["AWSCURRENT"],
        "Name": secret_name,
    }

    with patch("requests.get", return_value=mock_response) as mock_get:
        payload = get_secret(secret_name)
        assert payload.secret_dict == secret_data
        assert payload.version_id == "1"
        assert payload.name == secret_name
        mock_get.assert_called_once()
        request_kwargs = mock_get.call_args.kwargs
        assert "params" in request_kwargs
        assert request_kwargs["params"].get("secretId") == secret_name


@mock_aws
def test_get_secret_boto3_fallback_success(mock_aws_credentials):
    """Verify that `get_secret` successfully falls back to boto3 when the extension is not available."""
    secret_name = "my-secret"
    secret_data = {"key": "value"}
    create_secret(secret_name, secret_data)

    payload = get_secret(secret_name)
    assert payload.secret_dict == secret_data
    assert payload.version_id is not None
    assert "AWSCURRENT" in payload.version_stages


@mock_aws
def test_get_secret_extension_fails_boto3_fallback(
    mock_lambda_env, mock_aws_credentials
):
    """Verify that `get_secret` falls back to boto3 when the extension request fails."""
    secret_name = "my-secret"
    secret_data = {"key": "value"}
    create_secret(secret_name, secret_data)

    with patch(
        "requests.get",
        side_effect=requests.exceptions.RequestException("conn error"),
    ):
        payload = get_secret(secret_name)
        assert payload.secret_dict == secret_data


@mock_aws
def test_get_secret_with_version_stage(mock_aws_credentials):
    """Verify `get_secret` can retrieve a specific version using a stage."""
    secret_name = "my-versioned-secret"
    current_data = {"key": "current_value"}
    previous_data = {"key": "previous_value"}
    create_secret(
        secret_name,
        current_data,
        version_id="2",
        previous_version_data=previous_data,
    )

    # Get the AWSPREVIOUS version
    payload = get_secret(secret_name, version_stage="AWSPREVIOUS")
    assert payload.secret_dict == previous_data
    assert "AWSPREVIOUS" in payload.version_stages


@mock_aws
def test_get_secret_boto3_client_error(mock_aws_credentials):
    """Verify that a ClientError from boto3 is propagated correctly."""
    secret_name = "non-existent-secret"
    with pytest.raises(ClientError) as exc_info:
        get_secret(secret_name)
    assert exc_info.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_get_secret_from_extension_malformed_json(
    mock_lambda_env, mock_aws_credentials
):
    """Verify `get_secret` handles malformed JSON from the extension gracefully."""
    secret_name = "my-secret"
    # This string is intentionally malformed (uses single quotes)
    malformed_string = "{'key': 'value'}"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "SecretString": malformed_string,
        "VersionId": "1",
    }

    # The extension call should succeed, and _parse_response_to_payload should
    # handle the malformed JSON gracefully by returning it as a raw string.
    with patch("requests.get", return_value=mock_response):
        payload = get_secret(secret_name)
        assert payload.secret_dict is None
        assert payload.secret_string == malformed_string
        assert payload.version_id == "1"


@mock_aws
def test_get_secret_boto3_malformed_json(mock_aws_credentials):
    """Verify that `get_secret` handles malformed JSON from boto3."""
    secret_name = "my-secret"
    from boto3 import client

    sm_client = client("secretsmanager")
    # Store a non-JSON string in the secret
    sm_client.create_secret(Name=secret_name, SecretString="not-json")

    payload = get_secret(secret_name)
    assert payload.secret_dict is None
    assert payload.secret_string == "not-json"
