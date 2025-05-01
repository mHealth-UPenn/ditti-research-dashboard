from install.resource_managers.aws_cognito_resource_manager import (
    AwsCognitoResourceManager,
)
from tests.tests_install.tests_aws_providers.mock_aws_client_provider import (
    aws_client_provider,
)
from tests.tests_install.tests_project_config.mock_project_config_provider import (
    project_config_provider,
)
from tests.tests_install.tests_utils.mock_logger import logger


def participant_user_pool():
    return aws_client_provider().cognito_client.create_user_pool(
        PoolName="participant-user-pool"
    )


def researcher_user_pool():
    return aws_client_provider().cognito_client.create_user_pool(
        PoolName="researcher-user-pool"
    )


def participant_user_pool_client(participant_user_pool: dict):
    return aws_client_provider().cognito_client.create_user_pool_client(
        UserPoolId=participant_user_pool["UserPool"]["Id"],
        ClientName="participant-user-pool-client",
        GenerateSecret=True,
    )


def researcher_user_pool_client(researcher_user_pool: dict):
    return aws_client_provider().cognito_client.create_user_pool_client(
        UserPoolId=researcher_user_pool["UserPool"]["Id"],
        ClientName="researcher-user-pool-client",
        GenerateSecret=True,
    )


def aws_cognito_resource_manager():
    provider = AwsCognitoResourceManager(
        logger=logger(),
        config=project_config_provider(),
        aws_client_provider=aws_client_provider(),
    )
    participant = participant_user_pool()
    researcher = researcher_user_pool()
    participant_client = participant_user_pool_client(participant)
    researcher_client = researcher_user_pool_client(researcher)
    provider.config.participant_user_pool_id = participant["UserPool"]["Id"]
    provider.config.participant_client_id = participant_client["UserPoolClient"][
        "ClientId"
    ]
    provider.config.researcher_user_pool_id = researcher["UserPool"]["Id"]
    provider.config.researcher_client_id = researcher_client["UserPoolClient"][
        "ClientId"
    ]
    return provider
