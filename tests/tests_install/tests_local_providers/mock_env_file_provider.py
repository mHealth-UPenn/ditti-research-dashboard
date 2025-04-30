from install.local_providers.env_file_provider import EnvFileProvider
from install.local_providers.local_provider_types import (
    RootEnv,
    WearableDataRetrievalEnv,
)
from install.project_config import ProjectConfigProvider
from install.utils.enums import Postgres
from tests.tests_install.tests_aws_providers.mock_aws_account_provider import (
    aws_account_provider,
)
from tests.tests_install.tests_project_config.mock_project_config_provider import (
    project_config_provider,
)
from tests.tests_install.tests_utils.mock_logger import logger


def wearable_data_retrieval_env(
    config: ProjectConfigProvider,
) -> WearableDataRetrievalEnv:
    provider = aws_account_provider()

    return {
        "FLASK_DB": (
            f"postgresql://{Postgres.USER.value}:{Postgres.PASSWORD.value}@"
            f"{config.project_name}-postgres:{Postgres.PORT.value}/"
            f"{Postgres.DB.value}"
        ),
        "S3_BUCKET": config.logs_bucket_name,
        "AWS_CONFIG_SECRET_NAME": config.secret_name,
        "AWS_ACCESS_KEY_ID": provider.aws_access_key_id,
        "AWS_SECRET_ACCESS_KEY": provider.aws_secret_access_key,
        "AWS_DEFAULT_REGION": provider.aws_region,
        "TESTING": "true",
    }


def root_env(config: ProjectConfigProvider) -> RootEnv:
    provider = aws_account_provider()

    """Get .env."""
    return {
        "FLASK_CONFIG": "Default",
        "FLASK_DEBUG": "True",
        "FLASK_DB": (
            f"postgresql://{Postgres.USER.value}:{Postgres.PASSWORD.value}@"
            f"localhost:{Postgres.PORT.value}/{Postgres.DB.value}"
        ),
        "FLASK_APP": "run.py",
        "APP_SYNC_HOST": "",
        "APPSYNC_ACCESS_KEY": "",
        "APPSYNC_SECRET_KEY": "",
        "AWS_AUDIO_FILE_BUCKET": config.audio_bucket_name,
        "AWS_TABLENAME_AUDIO_FILE": "",
        "AWS_TABLENAME_AUDIO_TAP": "",
        "AWS_TABLENAME_TAP": "",
        "AWS_TABLENAME_USER": "",
        "COGNITO_PARTICIPANT_CLIENT_ID": config.participant_client_id,
        "COGNITO_PARTICIPANT_DOMAIN": (
            f"{config.participant_user_pool_domain}.auth."
            f"{provider.aws_region}.amazoncognito.com"
        ),
        "COGNITO_PARTICIPANT_REGION": provider.aws_region,
        "COGNITO_PARTICIPANT_USER_POOL_ID": config.participant_user_pool_id,
        "COGNITO_RESEARCHER_CLIENT_ID": config.researcher_client_id,
        "COGNITO_RESEARCHER_DOMAIN": (
            f"{config.researcher_user_pool_domain}.auth."
            f"{provider.aws_region}.amazoncognito.com"
        ),
        "COGNITO_RESEARCHER_REGION": provider.aws_region,
        "COGNITO_RESEARCHER_USER_POOL_ID": config.researcher_user_pool_id,
        "LOCAL_LAMBDA_ENDPOINT": (
            "http://localhost:9000/2015-03-31/functions/function/invocations"
        ),
        "TM_FSTRING": f"{config.project_name}-tokens",
    }


def env_file_provider() -> EnvFileProvider:
    provider = EnvFileProvider(
        logger=logger(),
        config=project_config_provider(),
        aws_account_provider=aws_account_provider(),
    )
    return provider
