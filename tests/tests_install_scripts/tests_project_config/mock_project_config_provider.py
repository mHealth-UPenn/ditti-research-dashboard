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
from tests.tests_install_scripts.tests_utils.mock_logger import logger


def user_input() -> UserInput:
    return {
        "admin_email": "test-admin-email",
        "project_name": "test-project",
        "fitbit_client_id": "test-fitbit-client-id",
        "fitbit_client_secret": "test-fitbit-client-secret",
    }


def cognito_config() -> CognitoConfig:
    return {
        "participant_user_pool_name": "test-project-participant-pool",
        "participant_user_pool_domain": "test-project-participant",
        "participant_user_pool_id": "",
        "participant_client_id": "",
        "researcher_user_pool_name": "test-project-researcher-pool",
        "researcher_user_pool_domain": "test-project-researcher",
        "researcher_user_pool_id": "",
        "researcher_client_id": "",
    }


def s3_config() -> S3Config:
    return {
        "logs_bucket_name": "test-project-wearable-data-retrieval-logs",
        "audio_bucket_name": "test-project-audio-files",
    }


def secrets_resource_manager_config() -> SecretsResourceManagerConfig:
    return {
        "secret_name": "test-project-secret",
        "tokens_secret_name": "test-project-Fitbit-tokens",
    }


def aws_config() -> AwsConfig:
    return {
        "cognito": cognito_config(),
        "s3": s3_config(),
        "secrets_manager": secrets_resource_manager_config(),
        "stack_name": "test-project-stack",
    }


def docker_config() -> DockerConfig:
    return {
        "network_name": "test-project-network",
        "postgres_container_name": "test-project-postgres",
        "wearable_data_retrieval_container_name": "test-project-wearable-data-retrieval",
    }


def project_config() -> ProjectConfig:
    return {
        "admin_email": "test-admin-email",
        "project_name": "test-project",
        "aws": aws_config(),
        "docker": docker_config(),
    }


def project_config_provider() -> ProjectConfigProvider:
    provider = ProjectConfigProvider(
        logger=logger(),
        project_suffix="test-project-suffix",
    )
    provider.user_input = user_input()
    provider.project_config = project_config()
    return provider
