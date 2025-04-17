from tests.tests_install_scripts.tests_aws_providers.mock_aws_client_provider import aws_client_provider
from tests.tests_install_scripts.tests_aws_providers.mock_aws_account_provider import aws_account_provider
from tests.tests_install_scripts.tests_project_config.mock_project_config_provider import project_config_provider
from tests.tests_install_scripts.tests_utils.mock_logger import logger
from install_scripts.aws_providers.aws_ecr_provider import AwsEcrProvider


def aws_ecr_provider():
    provider = AwsEcrProvider(
        logger=logger(),
        config=project_config_provider(),
        aws_client_provider=aws_client_provider(),
        aws_account_provider=aws_account_provider(),
    )
    return provider
