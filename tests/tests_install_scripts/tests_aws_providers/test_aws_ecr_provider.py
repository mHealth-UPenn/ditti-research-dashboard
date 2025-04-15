import pytest

from botocore.exceptions import ClientError

from install_scripts.aws_providers.aws_ecr_provider import AwsEcrProvider
from install_scripts.utils.exceptions import AwsProviderError
from tests.tests_install_scripts.tests_aws_providers.mock_aws_ecr_provider import aws_ecr_provider
from tests.tests_install_scripts.tests_aws_providers.mock_aws_client_provider import get_authorization_token_response


@pytest.fixture
def get_authorization_token_response_mock():
    return get_authorization_token_response()


@pytest.fixture
def aws_ecr_provider_mock():
    provider = aws_ecr_provider()
    return provider


class TestAwsEcrProvider:
    def test_get_password(self, get_authorization_token_response_mock: dict, aws_ecr_provider_mock: AwsEcrProvider):
        assert aws_ecr_provider_mock.get_password() == get_authorization_token_response_mock["authorizationData"][0]["authorizationToken"]

    def test_get_password_no_authorization_data(self, aws_ecr_provider_mock: AwsEcrProvider):
        aws_ecr_provider_mock.ecr_client.get_authorization_token.return_value = {"authorizationData": []}
        with pytest.raises(AwsProviderError, match="No authorization data found"):
            aws_ecr_provider_mock.get_password()

    def test_get_password_client_error(self, aws_ecr_provider_mock: AwsEcrProvider):
        aws_ecr_provider_mock.ecr_client.get_authorization_token.side_effect = ClientError(
            {"Error": {"Code": "ValidationError", "Message": "Stack with id dev-environment does not exist"}},
            "GetAuthorizationToken"
        )
        with pytest.raises(AwsProviderError):
            aws_ecr_provider_mock.get_password()

    def test_get_password_unexpected_error(self, aws_ecr_provider_mock: AwsEcrProvider):
        aws_ecr_provider_mock.ecr_client.get_authorization_token.side_effect = Exception("Unexpected error")
        with pytest.raises(Exception):
            aws_ecr_provider_mock.get_password()

    def test_get_repo_uri(self, aws_ecr_provider_mock: AwsEcrProvider):
        assert aws_ecr_provider_mock.get_repo_uri() == "123456789012.dkr.ecr.us-east-1.amazonaws.com"
