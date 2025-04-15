from unittest.mock import MagicMock

from install_scripts.resource_managers.aws_cloudformation_resource_manager import AwsCloudformationResourceManager
from tests.tests_install_scripts.tests_utils.mock_logger import logger
from tests.tests_install_scripts.tests_project_config.mock_project_config_provider import project_config_provider
from tests.tests_install_scripts.tests_aws_providers.mock_aws_client_provider import aws_client_provider


def template():
    with open("tests/data/cloudformation/template.yml", "r") as f:
        return f.read()


def parameters():
    return [
        {
            "ParameterKey": "TestParameter1",
            "ParameterValue": "test-parameter-1-value",
        },
        {
            "ParameterKey": "TestParameter2",
            "ParameterValue": "test-parameter-2-value",
        },
    ]


def aws_cloudformation_resource_manager():
    provider = AwsCloudformationResourceManager(
        logger=logger(),
        settings=project_config_provider(),
        aws_client_provider=aws_client_provider()
    )
    provider.get_dev_parameters = MagicMock(return_value=parameters())
    provider.get_dev_template_body = MagicMock(return_value=template())
    return provider
