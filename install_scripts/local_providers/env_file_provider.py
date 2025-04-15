import os

from install_scripts.aws_providers import AwsAccountProvider
from install_scripts.local_providers.local_provider_types import (
    WearableDataRetrievalEnv,
    RootEnv,
)
from install_scripts.project_config import ProjectConfigProvider
from install_scripts.utils import Logger
from install_scripts.utils.enums import Postgres


class EnvFileProvider:
    wearable_data_retrieval_filename: str = "functions/wearable_data_retrieval/.env"
    root_filename: str = ".env"

    def __init__(
            self, *,
            logger: Logger,
            settings: ProjectConfigProvider,
            aws_account_provider: AwsAccountProvider
        ):
        self.logger = logger
        self.settings = settings
        self.aws_account_provider = aws_account_provider

    def get_wearable_data_retrieval_env(self) -> WearableDataRetrievalEnv:
        """Get wearable_data_retrieval/.env."""
        return {
            "DB_URI": (
                f"postgresql://{Postgres.USER}:{Postgres.PASSWORD}@"
                f"{self.settings.project_name}-postgres:{Postgres.PORT}/"
                f"{Postgres.DB}"
            ),
            "S3_BUCKET": self.settings.logs_bucket_name,
            "AWS_CONFIG_SECRET_NAME": self.settings.secret_name,
            "AWS_ACCESS_KEY_ID": self.aws_account_handler.aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": \
                self.aws_account_handler.aws_secret_access_key,
            "AWS_DEFAULT_REGION": self.aws_account_handler.aws_region,
        }

    def get_root_env(self) -> RootEnv:
        """Get .env."""
        return {
            "FLASK_CONFIG": "Default",
            "FLASK_DEBUG": "True",
            "FLASK_DB": (
                f"postgresql://{Postgres.USER}:{Postgres.PASSWORD}@"
                f"localhost:{Postgres.PORT}/{Postgres.DB}"
            ),
            "FLASK_APP": "run.py",
            "APP_SYNC_HOST": "",
            "APPSYNC_ACCESS_KEY": "",
            "APPSYNC_SECRET_KEY": "",
            "AWS_AUDIO_FILE_BUCKET": self.settings.audio_bucket_name,
            "AWS_TABLENAME_AUDIO_FILE": "",
            "AWS_TABLENAME_AUDIO_TAP": "",
            "AWS_TABLENAME_TAP": "",
            "AWS_TABLENAME_USER": "",
            "COGNITO_PARTICIPANT_CLIENT_ID": \
                self.settings.participant_client_id,
            "COGNITO_PARTICIPANT_DOMAIN": (
                f"{self.settings.participant_user_pool_domain}.auth."
                f"{self.aws_account_handler.aws_region}.amazoncognito.com"
            ),
            "COGNITO_PARTICIPANT_REGION": self.aws_account_handler.aws_region,
            "COGNITO_PARTICIPANT_USER_POOL_ID": \
                self.settings.participant_user_pool_id,
            "COGNITO_RESEARCHER_CLIENT_ID": self.settings.researcher_client_id,
            "COGNITO_RESEARCHER_DOMAIN": (
                f"{self.settings.researcher_user_pool_domain}.auth."
                f"{self.aws_account_handler.aws_region}.amazoncognito.com"
            ),
            "COGNITO_RESEARCHER_REGION": self.aws_account_handler.aws_region,
            "COGNITO_RESEARCHER_USER_POOL_ID": \
                self.settings.researcher_user_pool_id,
            "LOCAL_LAMBDA_ENDPOINT": (
                "http://localhost:9000/2015-03-31/functions/function/"
                "invocations"
            ),
            "TM_FSTRING": f"{self.settings.project_name}-tokens",
        }

    def write_env_files(
            self,
            wearable_data_retrieval_env: WearableDataRetrievalEnv,
            root_env: RootEnv
        ) -> None:
        """Create .env files."""
        with open(self.wearable_data_retrieval_filename, "w") as f:
            for key, value in wearable_data_retrieval_env.items():
                f.write(f"{key}={value}\n")

        with open(self.root_filename, "w") as f:
            for key, value in root_env.items():
                f.write(f"{key}={value}\n")

    def uninstall(self) -> None:
        """Uninstall the .env files."""
        try:
            os.remove(self.wearable_data_retrieval_filename)
        except FileNotFoundError:
            self.logger.yellow(f"Env file {self.wearable_data_retrieval_filename} not found")

        try:
            os.remove(self.root_filename)
        except FileNotFoundError:
            self.logger.yellow(f"Env file {self.root_filename} not found")
