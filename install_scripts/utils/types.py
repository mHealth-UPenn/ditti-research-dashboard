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


class SecretsCreatorSettings(TypedDict):
    secret_name: str
    tokens_secret_name: str


class DockerSettings(TypedDict):
    network_name: str
    postgres_container_name: str
    wearable_data_retrieval_container_name: str


class AwsSettings(TypedDict):
    cognito: CognitoSettings
    s3: S3Settings
    secrets_manager: SecretsCreatorSettings
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


class RootEnv(TypedDict):
    FLASK_CONFIG: str
    FLASK_DEBUG: str
    FLASK_DB: str
    FLASK_APP: str
    APP_SYNC_HOST: str
    APPSYNC_ACCESS_KEY: str
    APPSYNC_SECRET_KEY: str
    AWS_AUDIO_FILE_BUCKET: str
    AWS_TABLENAME_AUDIO_FILE: str
    AWS_TABLENAME_AUDIO_TAP: str
    AWS_TABLENAME_TAP: str
    AWS_TABLENAME_USER: str
    COGNITO_PARTICIPANT_CLIENT_ID: str
    COGNITO_PARTICIPANT_DOMAIN: str
    COGNITO_PARTICIPANT_REGION: str
    COGNITO_PARTICIPANT_USER_POOL_ID: str
    COGNITO_RESEARCHER_CLIENT_ID: str
    COGNITO_RESEARCHER_DOMAIN: str
    COGNITO_RESEARCHER_REGION: str
    COGNITO_RESEARCHER_USER_POOL_ID: str
    LOCAL_LAMBDA_ENDPOINT: str
    TM_FSTRING: str


class WearableDataRetrievalEnv(TypedDict):
    DB_URI: str
    S3_BUCKET: str
    AWS_CONFIG_SECRET_NAME: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str


class SecretValue(TypedDict):
    FITBIT_CLIENT_ID: str
    FITBIT_CLIENT_SECRET: str
    COGNITO_PARTICIPANT_CLIENT_SECRET: str
    COGNITO_RESEARCHER_CLIENT_SECRET: str
