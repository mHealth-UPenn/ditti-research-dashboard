from unittest.mock import MagicMock

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
        "admin_email": "test@example.com",
        "project_name": "test-project",
        "fitbit_client_id": "test-fitbit-client-id",
        "fitbit_client_secret": "test-fitbit-client-secret",
    }


def cognito_config(hashstr: str) -> CognitoConfig:
    return {
        "participant_user_pool_name": f"test-project-suffix-{hashstr}-participant-pool",
        "participant_user_pool_domain": f"test-project-suffix-{hashstr}-participant",
        "participant_user_pool_id": "",
        "participant_client_id": "",
        "researcher_user_pool_name": f"test-project-suffix-{hashstr}-researcher-pool",
        "researcher_user_pool_domain": f"test-project-suffix-{hashstr}-researcher",
        "researcher_user_pool_id": "",
        "researcher_client_id": "",
    }


def s3_config(hashstr: str) -> S3Config:
    return {
        "logs_bucket_name": f"test-project-suffix-{hashstr}-wearable-data-retrieval-logs",
        "audio_bucket_name": f"test-project-suffix-{hashstr}-audio-files",
    }


def secrets_resource_manager_config(hashstr: str) -> SecretsResourceManagerConfig:
    return {
        "secret_name": f"test-project-suffix-{hashstr}-secret",
        "tokens_secret_name": f"test-project-suffix-{hashstr}-Fitbit-tokens",
    }


def aws_config(hashstr: str) -> AwsConfig:
    return {
        "cognito": cognito_config(hashstr),
        "s3": s3_config(hashstr),
        "secrets_manager": secrets_resource_manager_config(hashstr),
        "stack_name": f"test-project-suffix-{hashstr}-stack",
    }


def docker_config(hashstr: str) -> DockerConfig:
    return {
        "network_name": f"test-project-suffix-network",
        "postgres_container_name": f"test-project-suffix-postgres",
        "wearable_data_retrieval_container_name": f"test-project-suffix-wearable-data-retrieval",
    }


def project_config(hashstr: str) -> ProjectConfig:
    return {
        "admin_email": "test@example.com",
        "project_name": "test-project-suffix",
        "aws": aws_config(hashstr),
        "docker": docker_config(hashstr),
    }


def project_config_provider() -> ProjectConfigProvider:
    provider = ProjectConfigProvider(
        logger=logger(),
        project_suffix="suffix",
    )
    provider.user_input = user_input()
    provider.project_config = project_config(provider.hashstr)
    provider.get_continue_input = MagicMock(return_value="y")
    provider.get_project_name_input = MagicMock(return_value=provider.user_input["project_name"])
    provider.get_fitbit_credentials_input = MagicMock(return_value=(provider.user_input["fitbit_client_id"], provider.user_input["fitbit_client_secret"]))
    provider.get_admin_email_input = MagicMock(return_value=provider.user_input["admin_email"])
    provider.write_project_config = MagicMock()  # Suppresses writing to file
    return provider
