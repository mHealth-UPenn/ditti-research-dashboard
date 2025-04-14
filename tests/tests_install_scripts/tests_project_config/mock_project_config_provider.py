import pytest

from install_scripts.project_config.project_config_types import (
    AwsConfig,
    UserInput,
    ProjectConfig,
    CognitoConfig,
    S3Config,
    SecretsResourceManagerConfig,
    DockerConfig,
)
from install_scripts.project_config.project_config_provider import ProjectConfigProvider


@pytest.fixture(scope="session")
def user_input_mock() -> UserInput:
    return {
        "admin_email": "test-admin-email",
        "project_name": "test-project-name",
        "fitbit_client_id": "test-fitbit-client-id",
        "fitbit_client_secret": "test-fitbit-client-secret",
    }


@pytest.fixture(scope="session")
def cognito_config_mock() -> CognitoConfig:
    return {
        "participant_user_pool_name": "test-participant-user-pool-name",
        "participant_user_pool_domain": "test-participant-user-pool-domain",
        "participant_user_pool_id": "test-participant-user-pool-id",
        "participant_client_id": "test-participant-client-id",
        "researcher_user_pool_name": "test-researcher-user-pool-name",
        "researcher_user_pool_domain": "test-researcher-user-pool-domain",
        "researcher_user_pool_id": "test-researcher-user-pool-id",
        "researcher_client_id": "test-researcher-client-id",
    }


@pytest.fixture(scope="session")
def s3_config_mock() -> S3Config:
    return {
        "logs_bucket_name": "test-logs-bucket-name",
        "audio_bucket_name": "test-audio-bucket-name",
    }


@pytest.fixture(scope="session")
def secrets_resource_manager_config_mock() -> SecretsResourceManagerConfig:
    return {
        "secret_name": "test-secret-name",
        "tokens_secret_name": "test-tokens-secret-name",
    }


@pytest.fixture(scope="session")
def aws_config_mock(cognito_config_mock, s3_config_mock, secrets_resource_manager_config_mock) -> AwsConfig:
    return {
        "cognito": cognito_config_mock,
        "s3": s3_config_mock,
        "secrets_manager": secrets_resource_manager_config_mock,
        "stack_name": "test-stack-name",
    }


@pytest.fixture(scope="session")
def docker_config_mock() -> DockerConfig:
    return {
        "network_name": "test-network-name",
        "postgres_container_name": "test-postgres-container-name",
        "wearable_data_retrieval_container_name": "test-wearable-data-retrieval-container-name",
    }


@pytest.fixture(scope="session")
def project_config_mock(aws_config_mock, docker_config_mock) -> ProjectConfig:
    return {
        "admin_email": "test-admin-email",
        "project_name": "test-project-name",
        "aws": aws_config_mock,
        "docker": docker_config_mock,
    }


@pytest.fixture(scope="session")
def project_config_provider_mock(user_input_mock, project_config_mock, logger_mock) -> ProjectConfigProvider:
    provider = ProjectConfigProvider(
        logger=logger_mock,
        project_suffix="test-project-suffix",
    )
    provider.user_input = user_input_mock
    provider.project_config = project_config_mock
    return provider
