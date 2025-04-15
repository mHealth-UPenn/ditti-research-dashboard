from install_scripts.aws_providers.aws_cloudformation_provider import AwsCloudformationProvider
from tests.tests_install_scripts.tests_utils.mock_logger import logger
from tests.tests_install_scripts.tests_project_config.mock_project_config_provider import project_config_provider
from tests.tests_install_scripts.tests_aws_providers.mock_aws_client_provider import aws_client_provider


def outputs():
    return [
        {
            "Description": "ID of the test resource 1",
            "OutputKey": "TestResource1Id",
            "OutputValue": "test-parameter-1-value",
        },
        {
            "Description": "ID of the test resource 2",
            "OutputKey": "TestResource2Id",
            "OutputValue": "test-parameter-2-value",
        },
    ]


def aws_cloudformation_provider():
    return AwsCloudformationProvider(
        logger=logger(),
        settings=project_config_provider(),
        aws_client_provider=aws_client_provider()
    )
