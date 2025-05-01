from install.resource_managers.aws_secretsmanager_resource_manager import (
    AwsSecretsManagerResourceManager,
)
from install.resource_managers.resource_manager_types import DevSecretValue
from tests.tests_install.tests_aws_providers.mock_aws_client_provider import (
    aws_client_provider,
)
from tests.tests_install.tests_aws_providers.mock_aws_cognito_provider import (
    aws_cognito_provider,
)
from tests.tests_install.tests_project_config.mock_project_config_provider import (
    project_config_provider,
)
from tests.tests_install.tests_resource_managers.mock_aws_cognito_resource_manager import (
    participant_user_pool,
    participant_user_pool_client,
    researcher_user_pool,
    researcher_user_pool_client,
)
from tests.tests_install.tests_utils.mock_logger import logger


def dev_secret_value() -> DevSecretValue:
    participant = participant_user_pool()
    researcher = researcher_user_pool()
    return {
        "FITBIT_CLIENT_ID": "test-fitbit-client-id",
        "FITBIT_CLIENT_SECRET": "test-fitbit-client-secret",
        "COGNITO_PARTICIPANT_CLIENT_SECRET": participant_user_pool_client(
            participant
        )["UserPoolClient"]["ClientSecret"],
        "COGNITO_RESEARCHER_CLIENT_SECRET": researcher_user_pool_client(
            researcher
        )["UserPoolClient"]["ClientSecret"],
    }


def aws_secretsmanager_resource_manager():
    client_provider = aws_client_provider()
    config = project_config_provider()

    # The resource manager expects the secret to be created by cloudformation
    client_provider.secrets_manager_client.create_secret(Name=config.secret_name)

    return AwsSecretsManagerResourceManager(
        logger=logger(),
        config=config,
        aws_client_provider=client_provider,
        aws_cognito_provider=aws_cognito_provider(),
    )
