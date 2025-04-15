import pytest
from unittest.mock import MagicMock

from botocore.exceptions import ClientError
from moto import mock_aws

from install_scripts.aws_providers.aws_cognito_provider import AwsCognitoProvider
from install_scripts.utils.exceptions import AwsProviderError
from tests.tests_install_scripts.tests_resource_managers.mock_aws_cognito_resource_manager import participant_user_pool, researcher_user_pool, participant_user_pool_client, researcher_user_pool_client
from tests.tests_install_scripts.tests_aws_providers.mock_aws_cognito_provider import aws_cognito_provider


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
def aws_cognito_provider_mock(participant_user_pool_mock: dict, researcher_user_pool_mock: dict, participant_user_pool_client_mock: dict, researcher_user_pool_client_mock: dict):
    provider = aws_cognito_provider()
    provider.settings.participant_user_pool_id = participant_user_pool_mock["UserPool"]["Id"]
    provider.settings.participant_client_id = participant_user_pool_client_mock["UserPoolClient"]["ClientId"]
    provider.settings.researcher_user_pool_id = researcher_user_pool_mock["UserPool"]["Id"]
    provider.settings.researcher_client_id = researcher_user_pool_client_mock["UserPoolClient"]["ClientId"]
    return provider


@pytest.fixture
def describe_user_pool_client_mock(aws_cognito_provider_mock: AwsCognitoProvider):
    aws_cognito_provider_mock.cognito_client.describe_user_pool_client = MagicMock()
    return aws_cognito_provider_mock.cognito_client.describe_user_pool_client


class TestAwsCognitoProvider:
    def test_get_participant_client_secret(self, participant_user_pool_client_mock: dict, aws_cognito_provider_mock: AwsCognitoProvider):
        assert aws_cognito_provider_mock.get_participant_client_secret() == participant_user_pool_client_mock["UserPoolClient"]["ClientSecret"]

    def test_get_participant_client_secret_client_error(self, describe_user_pool_client_mock: MagicMock, aws_cognito_provider_mock: AwsCognitoProvider):
        describe_user_pool_client_mock.side_effect = ClientError(
            {"Error": {"Code": "ValidationError", "Message": "Stack with id dev-environment does not exist"}},
            "DescribeUserPoolClient"
        )
        with pytest.raises(AwsProviderError):
            aws_cognito_provider_mock.get_participant_client_secret()

    def test_get_participant_client_secret_unexpected_error(self, describe_user_pool_client_mock: MagicMock, aws_cognito_provider_mock: AwsCognitoProvider):
        describe_user_pool_client_mock.side_effect = Exception("Unexpected error")
        with pytest.raises(Exception):
            aws_cognito_provider_mock.get_participant_client_secret()

    def test_get_researcher_client_secret(self, researcher_user_pool_client_mock: dict, aws_cognito_provider_mock: AwsCognitoProvider):
        assert aws_cognito_provider_mock.get_researcher_client_secret() == researcher_user_pool_client_mock["UserPoolClient"]["ClientSecret"]

    def test_get_researcher_client_secret_client_error(self, describe_user_pool_client_mock: MagicMock, aws_cognito_provider_mock: AwsCognitoProvider):
        describe_user_pool_client_mock.side_effect = ClientError(
            {"Error": {"Code": "ValidationError", "Message": "Stack with id dev-environment does not exist"}},
            "DescribeUserPoolClient"
        )
        with pytest.raises(AwsProviderError):
            aws_cognito_provider_mock.get_researcher_client_secret()

    def test_get_researcher_client_secret_unexpected_error(self, describe_user_pool_client_mock: MagicMock, aws_cognito_provider_mock: AwsCognitoProvider):
        describe_user_pool_client_mock.side_effect = Exception("Unexpected error")
        with pytest.raises(Exception):
            aws_cognito_provider_mock.get_researcher_client_secret()
