import subprocess
from unittest.mock import MagicMock, patch

from install.aws_providers import AwsAccountProvider
from tests.tests_install.tests_aws_providers.mock_aws_client_provider import (
    aws_client_provider,
)
from tests.tests_install.tests_utils.mock_logger import logger

mock_account_id = "test-account-id"
mock_aws_region = "test-region"
mock_aws_access_key_id = "test-access-key-id"
mock_aws_secret_access_key = "test-secret-access-key"


def aws_account_provider():
    provider = AwsAccountProvider(
        logger=logger(), aws_client_provider=aws_client_provider()
    )

    provider.get_aws_access_key_id = MagicMock(
        return_value=mock_aws_access_key_id
    )
    provider.get_aws_secret_access_key = MagicMock(
        return_value=mock_aws_secret_access_key
    )
    provider.client = MagicMock()
    provider.client.meta.region_name = mock_aws_region
    provider.client.get_caller_identity = MagicMock(
        return_value={"Account": mock_account_id}
    )

    return provider
