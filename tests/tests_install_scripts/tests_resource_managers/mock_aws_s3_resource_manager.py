from install_scripts.resource_managers.aws_s3_resource_manager import AwsS3ResourceManager
from tests.tests_install_scripts.tests_aws_providers.mock_aws_client_provider import aws_client_provider
from tests.tests_install_scripts.tests_project_config.mock_project_config_provider import project_config_provider
from tests.tests_install_scripts.tests_utils.mock_logger import logger


def aws_s3_resource_manager():
    return AwsS3ResourceManager(
        logger=logger(),
        config=project_config_provider(),
        aws_client_provider=aws_client_provider(),
    )
