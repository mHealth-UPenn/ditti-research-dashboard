import os

from install_scripts.utils import (
    Logger,
    Postgres,
    WearableDataRetrievalEnv,
    RootEnv,
    BaseProvider
)
from install_scripts.project_settings_provider import ProjectSettingsProvider
from install_scripts.aws import AwsAccountProvider


class EnvProvider(BaseProvider):
    wearable_data_retrieval_env: WearableDataRetrievalEnv
    root_env: RootEnv

    def __init__(
            self, *,
            logger: Logger,
            settings: ProjectSettingsProvider,
            aws_account_handler: AwsAccountProvider
        ):
        self.logger = logger
        self.settings = settings
        self.aws_account_handler = aws_account_handler

    def on_start(self) -> None:
        """Run when the script starts."""
        self.logger.cyan("\n[Environment Setup]")

    def on_end(self) -> None:
        """Run when the script ends."""
        pass

    def dev(self) -> None:
        """Run the environment handler in development mode."""
        self.create_wearable_data_retrieval_env()
        self.create_root_env()
        self.write_env_files()

    def prod(self) -> None:
        """Run the environment handler in production mode."""
        pass

    def staging(self) -> None:
        """Run the environment handler in staging mode."""
        pass

    def create_wearable_data_retrieval_env(self) -> None:
        """Create wearable_data_retrieval/.env."""
        self.wearable_data_retrieval_env = {
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

    def create_root_env(self) -> None:
        """Create .env."""
        self.root_env = {
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

    def write_env_files(self) -> None:
        """Create .env files."""
        self.logger.cyan("\n[Local .env Files Setup]")

        os.makedirs("functions/wearable_data_retrieval", exist_ok=True)
        with open("functions/wearable_data_retrieval/.env", "w") as f:
            for key, value in self.wearable_data_retrieval_env.items():
                f.write(f"{key}={value}\n")

        with open(".env", "w") as f:
            for key, value in self.root_env.items():
                f.write(f"{key}={value}\n")

        self.logger.green(".env files created successfully")
