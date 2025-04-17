from enum import Enum


class Postgres(Enum):
    USER = "username"
    PASSWORD = "password"
    PORT = 5432
    DB = "database_name"


class FString(Enum):
    participant_user_pool_name = "{project_name}-participant-pool"
    participant_user_pool_domain = "{project_name}-participant"
    researcher_user_pool_name = "{project_name}-researcher-pool"
    researcher_user_pool_domain = "{project_name}-researcher"
    logs_bucket_name = "{project_name}-wearable-data-retrieval-logs"
    audio_bucket_name = "{project_name}-audio-files"
    secret_name = "{project_name}-secret"
    tokens_secret_name = "{project_name}-Fitbit-tokens"
    stack_name = "{project_name}-stack"
    network_name = "{project_name}-network"
    postgres_container_name = "{project_name}-postgres"
    wearable_data_retrieval_container_name = \
        "{project_name}-wearable-data-retrieval"
