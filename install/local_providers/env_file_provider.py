# Ditti Research Dashboard
# Copyright (C) 2025 the Trustees of the University of Pennsylvania
#
# Ditti Research Dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Ditti Research Dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os

from install.aws_providers import AwsAccountProvider
from install.local_providers.local_provider_types import (
    RootEnv,
    WearableDataRetrievalEnv,
)
from install.project_config import ProjectConfigProvider
from install.utils import Colorizer, Logger
from install.utils.enums import Postgres


class EnvFileProvider:
    wearable_data_retrieval_filename: str = (
        "functions/wearable_data_retrieval/.env"
    )
    root_filename: str = ".env"

    def __init__(
        self,
        *,
        logger: Logger,
        config: ProjectConfigProvider,
        aws_account_provider: AwsAccountProvider,
    ):
        self.logger = logger
        self.config = config
        self.aws_account_provider = aws_account_provider

    def get_wearable_data_retrieval_env(self) -> WearableDataRetrievalEnv:
        """Get wearable_data_retrieval/.env."""
        return {
            "FLASK_DB": (
                f"postgresql://{Postgres.USER.value}:{Postgres.PASSWORD.value}@"
                f"{self.config.project_name}-postgres:{Postgres.PORT.value}/"
                f"{Postgres.DB.value}"
            ),
            "S3_BUCKET": self.config.logs_bucket_name,
            "AWS_CONFIG_SECRET_NAME": self.config.secret_name,
            "AWS_ACCESS_KEY_ID": self.aws_account_provider.aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": self.aws_account_provider.aws_secret_access_key,
            "AWS_DEFAULT_REGION": self.aws_account_provider.aws_region,
            "TESTING": "true",
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
            "COGNITO_PARTICIPANT_CLIENT_ID": self.config.participant_client_id,
            "COGNITO_PARTICIPANT_DOMAIN": (
                f"{self.config.participant_user_pool_domain}.auth."
                f"{self.aws_account_provider.aws_region}.amazoncognito.com"
            ),
            "COGNITO_PARTICIPANT_REGION": self.aws_account_provider.aws_region,
            "COGNITO_PARTICIPANT_USER_POOL_ID": self.config.participant_user_pool_id,
            "COGNITO_RESEARCHER_CLIENT_ID": self.config.researcher_client_id,
            "COGNITO_RESEARCHER_DOMAIN": (
                f"{self.config.researcher_user_pool_domain}.auth."
                f"{self.aws_account_provider.aws_region}.amazoncognito.com"
            ),
            "COGNITO_RESEARCHER_REGION": self.aws_account_provider.aws_region,
            "COGNITO_RESEARCHER_USER_POOL_ID": self.config.researcher_user_pool_id,
            "LOCAL_LAMBDA_ENDPOINT": (
                "http://localhost:9000/2015-03-31/functions/function/"
                "invocations"
            ),
            "TM_FSTRING": f"{self.config.project_name}-tokens",
        }

    def write_root_env(self) -> None:
        """Create .env files."""
        with open(self.root_filename, "w") as f:
            for key, value in self.get_root_env().items():
                f.write(f"{key}={value}\n")

        self.logger(f".env file {Colorizer.blue(self.root_filename)} created")

    def uninstall(self) -> None:
        """Uninstall the .env files."""
        try:
            os.remove(self.root_filename)
            self.logger(
                f".env file {Colorizer.blue(self.root_filename)} removed"
            )
        except FileNotFoundError:
            self.logger.warning(
                f"Env file {Colorizer.blue(self.root_filename)} not found"
            )
