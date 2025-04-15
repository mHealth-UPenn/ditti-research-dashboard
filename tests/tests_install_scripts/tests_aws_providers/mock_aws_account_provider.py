from install_scripts.aws_providers import AwsAccountProvider
from tests.tests_install_scripts.tests_utils.mock_logger import logger
from tests.tests_install_scripts.tests_aws_providers.mock_aws_client_provider import aws_client_provider


def aws_account_provider():
    provider = AwsAccountProvider(
        logger=logger(),
        aws_client_provider=aws_client_provider()
    )
    return provider
