from typing import Literal, Optional, TypedDict

Env = Literal["dev", "staging", "prod"]


class CognitoSettings(TypedDict):
    participant_user_pool_name: str
    participant_user_pool_domain: str
    participant_user_pool_id: str
    participant_client_id: str
    researcher_user_pool_name: str
    researcher_user_pool_domain: str
    researcher_user_pool_id: str
    researcher_client_id: str


class S3Settings(TypedDict):
    logs_bucket_name: str
    audio_bucket_name: str


class SecretsResourceManagerSettings(TypedDict):
    secret_name: str
    tokens_secret_name: str


class DockerSettings(TypedDict):
    network_name: str
    postgres_container_name: str
    wearable_data_retrieval_container_name: str


class AwsSettings(TypedDict):
    cognito: CognitoSettings
    s3: S3Settings
    secrets_manager: SecretsResourceManagerSettings
    stack_name: str


class ProjectSettings(TypedDict):
    project_name: str
    admin_email: str
    aws: AwsSettings
    docker: DockerSettings


class UserInput(TypedDict):
    project_name: Optional[str]
    fitbit_client_id: Optional[str]
    fitbit_client_secret: Optional[str]
    admin_email: Optional[str]
