from tests.tests_install_scripts.tests_aws_providers.mock_aws_client_provider import aws_client_provider


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
