from install.aws_providers.aws_cognito_provider import AwsCognitoProvider
from tests.tests_install.tests_aws_providers.mock_aws_client_provider import (
    aws_client_provider,
)
from tests.tests_install.tests_project_config.mock_project_config_provider import (
    project_config_provider,
)
from tests.tests_install.tests_utils.mock_logger import logger


def aws_cognito_provider():
    return AwsCognitoProvider(
        config=project_config_provider(),
        logger=logger(),
        aws_client_provider=aws_client_provider(),
    )
