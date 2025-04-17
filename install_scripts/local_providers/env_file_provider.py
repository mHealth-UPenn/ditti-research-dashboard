import os

from install_scripts.aws_providers import AwsAccountProvider
from install_scripts.local_providers.local_provider_types import (
    WearableDataRetrievalEnv,
    RootEnv,
)
from install_scripts.project_config import ProjectConfigProvider
from install_scripts.utils import Logger, Colorizer
from install_scripts.utils.enums import Postgres


class EnvFileProvider:
    wearable_data_retrieval_filename: str = "functions/wearable_data_retrieval/.env"
    root_filename: str = ".env"

    def __init__(
            self, *,
            logger: Logger,
            config: ProjectConfigProvider,
            aws_account_provider: AwsAccountProvider
        ):
        self.logger = logger
        self.config = config
        self.aws_account_provider = aws_account_provider

    def get_wearable_data_retrieval_env(self) -> WearableDataRetrievalEnv:
        """Get wearable_data_retrieval/.env."""
        return {
            "DB_URI": (
                f"postgresql://{Postgres.USER.value}:{Postgres.PASSWORD.value}@"
                f"{self.config.project_name}-postgres:{Postgres.PORT.value}/"
                f"{Postgres.DB.value}"
            ),
            "S3_BUCKET": self.config.logs_bucket_name,
            "AWS_CONFIG_SECRET_NAME": self.config.secret_name,
            "AWS_ACCESS_KEY_ID": self.aws_account_provider.aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": \
                self.aws_account_provider.aws_secret_access_key,
            "AWS_DEFAULT_REGION": self.aws_account_provider.aws_region,
        }

    def get_root_env(self) -> RootEnv:
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
            "AWS_AUDIO_FILE_BUCKET": self.config.audio_bucket_name,
            "AWS_TABLENAME_AUDIO_FILE": "",
            "AWS_TABLENAME_AUDIO_TAP": "",
            "AWS_TABLENAME_TAP": "",
            "AWS_TABLENAME_USER": "",
            "COGNITO_PARTICIPANT_CLIENT_ID": \
                self.config.participant_client_id,
            "COGNITO_PARTICIPANT_DOMAIN": (
                f"{self.config.participant_user_pool_domain}.auth."
                f"{self.aws_account_provider.aws_region}.amazoncognito.com"
            ),
            "COGNITO_PARTICIPANT_REGION": self.aws_account_provider.aws_region,
            "COGNITO_PARTICIPANT_USER_POOL_ID": \
                self.config.participant_user_pool_id,
            "COGNITO_RESEARCHER_CLIENT_ID": self.config.researcher_client_id,
            "COGNITO_RESEARCHER_DOMAIN": (
                f"{self.config.researcher_user_pool_domain}.auth."
                f"{self.aws_account_provider.aws_region}.amazoncognito.com"
            ),
            "COGNITO_RESEARCHER_REGION": self.aws_account_provider.aws_region,
            "COGNITO_RESEARCHER_USER_POOL_ID": \
                self.config.researcher_user_pool_id,
            "LOCAL_LAMBDA_ENDPOINT": (
                "http://localhost:9000/2015-03-31/functions/function/"
                "invocations"
            ),
            "TM_FSTRING": f"{self.config.project_name}-tokens",
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

        self.logger(f".env file {Colorizer.blue(self.wearable_data_retrieval_filename)} created")

        with open(self.root_filename, "w") as f:
            for key, value in root_env.items():
                f.write(f"{key}={value}\n")

        self.logger(f".env file {Colorizer.blue(self.root_filename)} created")

    def uninstall(self) -> None:
        """Uninstall the .env files."""
        try:
            os.remove(self.wearable_data_retrieval_filename)
            self.logger(f".env file {Colorizer.blue(self.wearable_data_retrieval_filename)} removed")
        except FileNotFoundError:
            self.logger.warning(f"Env file {Colorizer.blue(self.wearable_data_retrieval_filename)} not found")

        try:
            os.remove(self.root_filename)
            self.logger(f".env file {Colorizer.blue(self.root_filename)} removed")
        except FileNotFoundError:
            self.logger.warning(f"Env file {Colorizer.blue(self.root_filename)} not found")
