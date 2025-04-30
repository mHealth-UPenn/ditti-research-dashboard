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

import json
import os
import random
import string
from getpass import getpass

from install.project_config.project_config_types import (
    CognitoConfig,
    DockerConfig,
    ProjectConfig,
    S3Config,
    SecretsResourceManagerConfig,
    UserInput,
)
from install.utils import Colorizer, Logger, is_valid_email, is_valid_name
from install.utils.enums import FString
from install.utils.exceptions import CancelInstallation, ProjectConfigError


class ProjectConfigProvider:
    project_config_filename: str = "project-config.json"
    user_input: UserInput | None
    project_config: ProjectConfig | None

    def __init__(
        self,
        *,
        logger: Logger,
    ):
        self.logger = logger
        self.project_config = None
        self.user_input = None
        self.hashstr = "".join(
            random.choices(string.ascii_letters + string.digits, k=8)
        ).lower()

    def load_existing_config(self) -> None:
        """Load project config from a JSON file."""
        if not os.path.exists(self.project_config_filename):
            msg = (
                "Project config file "
                f"{Colorizer.blue(self.project_config_filename)}"
                " not found"
            )
            self.logger.error(msg)
            raise ProjectConfigError(msg)

        with open(self.project_config_filename) as f:
            self.project_config = json.load(f)

    @property
    def admin_email(self) -> str:
        return self.user_input["admin_email"]

    @property
    def fitbit_client_id(self) -> str:
        return self.user_input["fitbit_client_id"]

    @property
    def fitbit_client_secret(self) -> str:
        return self.user_input["fitbit_client_secret"]

    @property
    def project_name(self) -> str:
        if self.user_input is not None:
            return self.user_input["project_name"]
        return self.project_config["project_name"]

    @project_name.setter
    def project_name(self, value: str) -> None:
        self.project_config["project_name"] = value
        self.write_project_config()

    @property
    def participant_user_pool_name(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["cognito"]["participant_user_pool_name"]

    @participant_user_pool_name.setter
    def participant_user_pool_name(self, value: str) -> None:
        self.project_config["aws"]["cognito"]["participant_user_pool_name"] = (
            value
        )
        self.write_project_config()

    @property
    def participant_user_pool_domain(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["cognito"][
            "participant_user_pool_domain"
        ]

    @participant_user_pool_domain.setter
    def participant_user_pool_domain(self, value: str) -> None:
        self.project_config["aws"]["cognito"]["participant_user_pool_domain"] = (
            value
        )
        self.write_project_config()

    @property
    def participant_user_pool_id(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["cognito"]["participant_user_pool_id"]

    @participant_user_pool_id.setter
    def participant_user_pool_id(self, value: str) -> None:
        self.project_config["aws"]["cognito"]["participant_user_pool_id"] = value
        self.write_project_config()

    @property
    def participant_client_id(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["cognito"]["participant_client_id"]

    @participant_client_id.setter
    def participant_client_id(self, value: str) -> None:
        self.project_config["aws"]["cognito"]["participant_client_id"] = value
        self.write_project_config()

    @property
    def researcher_user_pool_name(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["cognito"]["researcher_user_pool_name"]

    @researcher_user_pool_name.setter
    def researcher_user_pool_name(self, value: str) -> None:
        self.project_config["aws"]["cognito"]["researcher_user_pool_name"] = value
        self.write_project_config()

    @property
    def researcher_user_pool_domain(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["cognito"][
            "researcher_user_pool_domain"
        ]

    @researcher_user_pool_domain.setter
    def researcher_user_pool_domain(self, value: str) -> None:
        self.project_config["aws"]["cognito"]["researcher_user_pool_domain"] = (
            value
        )
        self.write_project_config()

    @property
    def researcher_user_pool_id(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["cognito"]["researcher_user_pool_id"]

    @researcher_user_pool_id.setter
    def researcher_user_pool_id(self, value: str) -> None:
        self.project_config["aws"]["cognito"]["researcher_user_pool_id"] = value
        self.write_project_config()

    @property
    def researcher_client_id(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["cognito"]["researcher_client_id"]

    @researcher_client_id.setter
    def researcher_client_id(self, value: str) -> None:
        self.project_config["aws"]["cognito"]["researcher_client_id"] = value
        self.write_project_config()

    @property
    def logs_bucket_name(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["s3"]["logs_bucket_name"]

    @logs_bucket_name.setter
    def logs_bucket_name(self, value: str) -> None:
        self.project_config["aws"]["s3"]["logs_bucket_name"] = value
        self.write_project_config()

    @property
    def audio_bucket_name(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["s3"]["audio_bucket_name"]

    @audio_bucket_name.setter
    def audio_bucket_name(self, value: str) -> None:
        self.project_config["aws"]["s3"]["audio_bucket_name"] = value
        self.write_project_config()

    @property
    def secret_name(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["secrets_manager"]["secret_name"]

    @secret_name.setter
    def secret_name(self, value: str) -> None:
        self.project_config["aws"]["secrets_manager"]["secret_name"] = value
        self.write_project_config()

    @property
    def tokens_secret_name(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["secrets_manager"]["tokens_secret_name"]

    @tokens_secret_name.setter
    def tokens_secret_name(self, value: str) -> None:
        self.project_config["aws"]["secrets_manager"]["tokens_secret_name"] = (
            value
        )
        self.write_project_config()

    @property
    def stack_name(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["stack_name"]

    @stack_name.setter
    def stack_name(self, value: str) -> None:
        self.project_config["aws"]["stack_name"] = value
        self.write_project_config()

    @property
    def network_name(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["docker"]["network_name"]

    @network_name.setter
    def network_name(self, value: str) -> None:
        self.project_config["docker"]["network_name"] = value
        self.write_project_config()

    @property
    def postgres_container_name(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["docker"]["postgres_container_name"]

    @postgres_container_name.setter
    def postgres_container_name(self, value: str) -> None:
        self.project_config["docker"]["postgres_container_name"] = value
        self.write_project_config()

    @property
    def wearable_data_retrieval_container_name(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["docker"][
            "wearable_data_retrieval_container_name"
        ]

    @wearable_data_retrieval_container_name.setter
    def wearable_data_retrieval_container_name(self, value: str) -> None:
        self.project_config["docker"][
            "wearable_data_retrieval_container_name"
        ] = value
        self.write_project_config()

    def project_settings_exists(self) -> bool:
        return os.path.exists(self.project_config_filename)

    def get_user_input(self) -> None:
        if self.project_settings_exists():
            msg = (
                "Project settings already exist. Please uninstall the project "
                "first."
            )
            raise ProjectConfigError(msg)

        self.logger(
            "\nThis script will install the development environment for"
            " the project."
        )
        self.logger(
            Colorizer.magenta("The following will be configured and installed:")
        )
        self.logger("- AWS CLI")
        self.logger("- Amazon Cognito user pools and clients")
        self.logger("- Amazon S3 buckets")
        self.logger("- Development secrets on AWS Secrets ResourceManager")
        self.logger("- Local .env files")
        self.logger("- Docker containers for the project")

        if not self.get_continue_input() == "y":
            self.logger.warning("Installation cancelled")
            raise CancelInstallation()

        # Get project name
        project_name = ""
        while not is_valid_name(project_name):
            project_name = self.get_project_name_input()
            if not is_valid_name(project_name):
                self.logger.warning("Invalid name")

        # Get Fitbit credentials
        fitbit_client_id, fitbit_client_secret = (
            self.get_fitbit_credentials_input()
        )

        # Get admin email
        admin_email = ""
        while not is_valid_email(admin_email):
            admin_email = self.get_admin_email_input()
            if not is_valid_email(admin_email):
                self.logger.warning("Invalid email")

        self.user_input = {
            "project_name": project_name,
            "fitbit_client_id": fitbit_client_id,
            "fitbit_client_secret": fitbit_client_secret,
            "admin_email": admin_email,
        }

    @staticmethod
    def get_continue_input() -> str:
        return input("\nDo you want to continue? (y/n): ").lower()

    @staticmethod
    def get_project_name_input() -> str:
        return input("\nEnter a name for your project: ")

    @staticmethod
    def get_fitbit_credentials_input() -> tuple[str, str]:
        return (
            input("Enter your dev Fitbit OAuth 2.0 Client ID: "),
            getpass("Enter your dev Fitbit Client Secret: "),
        )

    @staticmethod
    def get_admin_email_input() -> str:
        return input("Enter an email to login as admin: ")

    def setup_project_config(self) -> None:
        """Set up project config."""
        cognito_config: CognitoConfig = {
            "participant_user_pool_name": self.format_string(
                FString.participant_user_pool_name.value, add_hashstr=True
            ),
            "participant_user_pool_domain": self.format_string(
                FString.participant_user_pool_domain.value, add_hashstr=True
            ),
            "participant_user_pool_id": "",
            "participant_client_id": "",
            "researcher_user_pool_name": self.format_string(
                FString.researcher_user_pool_name.value, add_hashstr=True
            ),
            "researcher_user_pool_domain": self.format_string(
                FString.researcher_user_pool_domain.value, add_hashstr=True
            ),
            "researcher_user_pool_id": "",
            "researcher_client_id": "",
        }

        s3_config: S3Config = {
            "logs_bucket_name": self.format_string(
                FString.logs_bucket_name.value, add_hashstr=True
            ),
            "audio_bucket_name": self.format_string(
                FString.audio_bucket_name.value, add_hashstr=True
            ),
        }

        secrets_manager_config: SecretsResourceManagerConfig = {
            "secret_name": self.format_string(
                FString.secret_name.value, add_hashstr=True
            ),
            "tokens_secret_name": self.format_string(
                FString.tokens_secret_name.value, add_hashstr=True
            ),
        }

        docker_config: DockerConfig = {
            "network_name": self.format_string(FString.network_name.value),
            "postgres_container_name": self.format_string(
                FString.postgres_container_name.value
            ),
            "wearable_data_retrieval_container_name": self.format_string(
                FString.wearable_data_retrieval_container_name.value
            ),
        }

        self.project_config = {
            "project_name": self.project_name,
            "admin_email": self.admin_email,
            "aws": {
                "cognito": cognito_config,
                "s3": s3_config,
                "secrets_manager": secrets_manager_config,
                "stack_name": self.format_string(
                    FString.stack_name.value, add_hashstr=True
                ),
            },
            "docker": docker_config,
        }

    def format_string(self, fstr: str, add_hashstr: bool = False) -> str:
        project_name = self.project_name
        if add_hashstr:
            project_name += f"-{self.hashstr}"
        return fstr.format(project_name=project_name)

    def write_project_config(self) -> None:
        """Write project config to a JSON file."""
        with open(self.project_config_filename, "w") as f:
            json.dump(self.project_config, f, indent=4)

    def uninstall(self) -> None:
        """Uninstall the project config."""
        try:
            os.remove(self.project_config_filename)
            msg = (
                "Project config file "
                f"{Colorizer.blue(self.project_config_filename)}"
                " removed"
            )
            self.logger(msg)
        except FileNotFoundError:
            msg = (
                "Project config file "
                f"{Colorizer.blue(self.project_config_filename)}"
                " not found"
            )
            self.logger.warning(msg)
