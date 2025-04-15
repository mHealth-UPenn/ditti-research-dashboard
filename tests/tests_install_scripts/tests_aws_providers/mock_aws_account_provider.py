from unittest.mock import MagicMock

from install_scripts.aws_providers import AwsAccountProvider, AwsClientProvider
from tests.tests_install_scripts.tests_utils.mock_logger import logger

def aws_account_provider():
    provider = AwsAccountProvider(
        logger=logger(),
        aws_client_provider=AwsClientProvider()
    )
    return provider
