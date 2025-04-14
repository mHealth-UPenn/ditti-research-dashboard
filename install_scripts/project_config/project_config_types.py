from typing import Optional, TypedDict


class CognitoConfig(TypedDict):
    participant_user_pool_name: str
    participant_user_pool_domain: str
    participant_user_pool_id: str
    participant_client_id: str
    researcher_user_pool_name: str
    researcher_user_pool_domain: str
    researcher_user_pool_id: str
    researcher_client_id: str


class S3Config(TypedDict):
    logs_bucket_name: str
    audio_bucket_name: str


class SecretsResourceManagerConfig(TypedDict):
    secret_name: str
    tokens_secret_name: str


class DockerConfig(TypedDict):
    network_name: str
    postgres_container_name: str
    wearable_data_retrieval_container_name: str


class AwsConfig(TypedDict):
    cognito: CognitoConfig
    s3: S3Config
    secrets_manager: SecretsResourceManagerConfig
    stack_name: str


class ProjectConfig(TypedDict):
    project_name: str
    admin_email: str
    aws: AwsConfig
    docker: DockerConfig


class UserInput(TypedDict):
    project_name: Optional[str]
    fitbit_client_id: Optional[str]
    fitbit_client_secret: Optional[str]
    admin_email: Optional[str]
