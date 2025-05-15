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

import subprocess
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

from install.aws_providers import AwsAccountProvider
from install.utils.exceptions import AwsProviderError, SubprocessError
from tests.tests_install.tests_aws_providers.mock_aws_account_provider import (
    aws_account_provider,
    mock_account_id,
    mock_aws_access_key_id,
    mock_aws_region,
    mock_aws_secret_access_key,
)
from tests.tests_install.tests_utils.mock_logger import logger


@pytest.fixture
def logger_mock():
    return logger()


@pytest.fixture
def aws_account_provider_mock():
    with mock_aws():
        yield aws_account_provider()


@pytest.fixture
def mock_check_output():
    with patch("subprocess.check_output") as mock_check_output:
        yield mock_check_output


@pytest.fixture
def mock_run():
    with patch("subprocess.run") as mock_run:
        yield mock_run


@pytest.fixture
def mock_which():
    with patch("shutil.which") as mock_which:
        # Return the input command name to simulate simple path
        mock_which.side_effect = lambda x: x
        yield mock_which


def test_aws_region_success(aws_account_provider_mock: AwsAccountProvider):
    assert aws_account_provider_mock.aws_region == mock_aws_region


def test_aws_access_key_id_success(
    aws_account_provider_mock: AwsAccountProvider,
):
    assert aws_account_provider_mock.aws_access_key_id == mock_aws_access_key_id


def test_aws_access_key_id_subprocess_error(
    aws_account_provider_mock: AwsAccountProvider,
):
    aws_account_provider_mock.get_aws_access_key_id = MagicMock(
        side_effect=subprocess.CalledProcessError(1, "aws configure get")
    )

    with pytest.raises(SubprocessError):
        _ = aws_account_provider_mock.aws_access_key_id


def test_aws_access_key_id_unexpected_error(
    aws_account_provider_mock: AwsAccountProvider,
):
    aws_account_provider_mock.get_aws_access_key_id = MagicMock(
        side_effect=Exception("Unexpected error")
    )

    with pytest.raises(SubprocessError):
        _ = aws_account_provider_mock.aws_access_key_id


def test_aws_secret_access_key_success(
    aws_account_provider_mock: AwsAccountProvider,
):
    result = aws_account_provider_mock.aws_secret_access_key

    assert result == mock_aws_secret_access_key


def test_aws_secret_access_key_subprocess_error(
    aws_account_provider_mock: AwsAccountProvider,
):
    aws_account_provider_mock.get_aws_secret_access_key = MagicMock(
        side_effect=subprocess.CalledProcessError(1, "aws configure get")
    )

    with pytest.raises(SubprocessError, match="aws configure get"):
        _ = aws_account_provider_mock.aws_secret_access_key


def test_aws_secret_access_key_unexpected_error(
    aws_account_provider_mock: AwsAccountProvider,
):
    aws_account_provider_mock.get_aws_secret_access_key = MagicMock(
        side_effect=Exception("Unexpected error")
    )

    with pytest.raises(SubprocessError, match="Unexpected error"):
        _ = aws_account_provider_mock.aws_secret_access_key


def test_aws_account_id_success(aws_account_provider_mock: AwsAccountProvider):
    result = aws_account_provider_mock.aws_account_id

    assert result == mock_account_id


def test_aws_account_id_client_error(
    aws_account_provider_mock: AwsAccountProvider,
):
    aws_account_provider_mock.client.get_caller_identity = MagicMock()
    aws_account_provider_mock.client.get_caller_identity.side_effect = (
        ClientError(
            error_response={
                "Error": {"Code": "AccessDenied", "Message": "Access Denied"}
            },
            operation_name="GetCallerIdentity",
        )
    )

    with pytest.raises(AwsProviderError, match="AccessDenied"):
        _ = aws_account_provider_mock.aws_account_id


def test_aws_account_id_unexpected_error(
    aws_account_provider_mock: AwsAccountProvider,
):
    aws_account_provider_mock.client.get_caller_identity = MagicMock()
    aws_account_provider_mock.client.get_caller_identity.side_effect = Exception(
        "Unexpected error"
    )

    with pytest.raises(AwsProviderError, match="Unexpected error"):
        _ = aws_account_provider_mock.aws_account_id


def test_configure_aws_cli_success(
    mock_run: MagicMock,
    aws_account_provider_mock: AwsAccountProvider,
    mock_which: MagicMock,
):
    aws_account_provider_mock.configure_aws_cli()

    mock_run.assert_called_once_with(["aws", "configure"])


def test_configure_aws_cli_subprocess_error(
    mock_run: MagicMock, aws_account_provider_mock: AwsAccountProvider
):
    mock_run.side_effect = subprocess.CalledProcessError(1, "aws configure")

    with pytest.raises(SubprocessError, match="aws configure"):
        aws_account_provider_mock.configure_aws_cli()


def test_configure_aws_cli_unexpected_error(
    mock_run: MagicMock, aws_account_provider_mock: AwsAccountProvider
):
    mock_run.side_effect = Exception("Unexpected error")

    with pytest.raises(SubprocessError, match="Unexpected error"):
        aws_account_provider_mock.configure_aws_cli()
