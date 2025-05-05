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

from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

from install.aws_providers.aws_cognito_provider import AwsCognitoProvider
from install.utils.exceptions import AwsProviderError
from tests.tests_install.tests_aws_providers.mock_aws_cognito_provider import (
    aws_cognito_provider,
)
from tests.tests_install.tests_resource_managers.mock_aws_cognito_resource_manager import (
    participant_user_pool,
    participant_user_pool_client,
    researcher_user_pool,
    researcher_user_pool_client,
)


@pytest.fixture
def participant_user_pool_mock():
    with mock_aws():
        yield participant_user_pool()


@pytest.fixture
def researcher_user_pool_mock():
    with mock_aws():
        yield researcher_user_pool()


@pytest.fixture
def participant_user_pool_client_mock(participant_user_pool_mock: dict):
    return participant_user_pool_client(participant_user_pool_mock)


@pytest.fixture
def researcher_user_pool_client_mock(researcher_user_pool_mock: dict):
    return researcher_user_pool_client(researcher_user_pool_mock)


@pytest.fixture
def aws_cognito_provider_mock(
    participant_user_pool_mock: dict,
    researcher_user_pool_mock: dict,
    participant_user_pool_client_mock: dict,
    researcher_user_pool_client_mock: dict,
):
    provider = aws_cognito_provider()
    provider.config.participant_user_pool_id = participant_user_pool_mock[
        "UserPool"
    ]["Id"]
    provider.config.participant_client_id = participant_user_pool_client_mock[
        "UserPoolClient"
    ]["ClientId"]
    provider.config.researcher_user_pool_id = researcher_user_pool_mock[
        "UserPool"
    ]["Id"]
    provider.config.researcher_client_id = researcher_user_pool_client_mock[
        "UserPoolClient"
    ]["ClientId"]
    return provider


@pytest.fixture
def describe_user_pool_client_mock(
    aws_cognito_provider_mock: AwsCognitoProvider,
):
    aws_cognito_provider_mock.cognito_client.describe_user_pool_client = (
        MagicMock()
    )
    return aws_cognito_provider_mock.cognito_client.describe_user_pool_client


def test_get_participant_client_secret(
    participant_user_pool_client_mock: dict,
    aws_cognito_provider_mock: AwsCognitoProvider,
):
    assert (
        aws_cognito_provider_mock.get_participant_client_secret()
        == participant_user_pool_client_mock["UserPoolClient"]["ClientSecret"]
    )


def test_get_participant_client_secret_client_error(
    describe_user_pool_client_mock: MagicMock,
    aws_cognito_provider_mock: AwsCognitoProvider,
):
    describe_user_pool_client_mock.side_effect = ClientError(
        {
            "Error": {
                "Code": "ValidationError",
                "Message": "Stack with id dev-environment does not exist",
            }
        },
        "DescribeUserPoolClient",
    )
    with pytest.raises(AwsProviderError, match="ValidationError"):
        aws_cognito_provider_mock.get_participant_client_secret()


def test_get_participant_client_secret_unexpected_error(
    describe_user_pool_client_mock: MagicMock,
    aws_cognito_provider_mock: AwsCognitoProvider,
):
    describe_user_pool_client_mock.side_effect = Exception("Unexpected error")
    with pytest.raises(AwsProviderError, match="Unexpected error"):
        aws_cognito_provider_mock.get_participant_client_secret()


def test_get_researcher_client_secret(
    researcher_user_pool_client_mock: dict,
    aws_cognito_provider_mock: AwsCognitoProvider,
):
    assert (
        aws_cognito_provider_mock.get_researcher_client_secret()
        == researcher_user_pool_client_mock["UserPoolClient"]["ClientSecret"]
    )


def test_get_researcher_client_secret_client_error(
    describe_user_pool_client_mock: MagicMock,
    aws_cognito_provider_mock: AwsCognitoProvider,
):
    describe_user_pool_client_mock.side_effect = ClientError(
        {
            "Error": {
                "Code": "ValidationError",
                "Message": "Stack with id dev-environment does not exist",
            }
        },
        "DescribeUserPoolClient",
    )
    with pytest.raises(AwsProviderError, match="ValidationError"):
        aws_cognito_provider_mock.get_researcher_client_secret()


def test_get_researcher_client_secret_unexpected_error(
    describe_user_pool_client_mock: MagicMock,
    aws_cognito_provider_mock: AwsCognitoProvider,
):
    describe_user_pool_client_mock.side_effect = Exception("Unexpected error")
    with pytest.raises(AwsProviderError, match="Unexpected error"):
        aws_cognito_provider_mock.get_researcher_client_secret()
