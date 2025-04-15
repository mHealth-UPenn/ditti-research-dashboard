from unittest.mock import MagicMock

from install_scripts.aws_providers.aws_client_provider import AwsClientProvider


def get_authorization_token_response():
    return {"authorizationData": [{"authorizationToken": "test-token"}]}


def aws_client_provider():
    provider = AwsClientProvider()

    # Mock methods that are not mocked by moto
    provider.ecr_client.get_authorization_token = MagicMock(return_value=get_authorization_token_response())
    return provider
