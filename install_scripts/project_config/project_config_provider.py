from getpass import getpass
import json
import sys
from typing import Optional

from install_scripts.utils import (
    Logger,
    is_valid_name,
    is_valid_email,
)
from install_scripts.utils.enums import FString
from install_scripts.project_config.project_config_types import (
    ProjectConfig,
    CognitoConfig,
    S3Config,
    SecretsResourceManagerConfig,
    DockerConfig,
    UserInput,
)


class ProjectConfigProvider:
    project_config_filename: str = "project-config-{project_name}.json"
    user_input: Optional[UserInput]
    project_config: Optional[ProjectConfig]

    def __init__(
            self, *,
            logger: Logger,
            project_suffix: Optional[str] = None
        ):
        self.logger = logger
        self.project_config = None
        self.user_input = None
        self.project_suffix = project_suffix

    @property
    def project_name(self) -> str:
        return self.user_input["project_name"]

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
    def participant_user_pool_name(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["cognito"] \
            ["participant_user_pool_name"]

    @participant_user_pool_name.setter
    def participant_user_pool_name(self, value: str) -> None:
        self.project_config["aws"]["cognito"] \
            ["participant_user_pool_name"] = value
        self.write_project_config()

    @property
    def participant_user_pool_domain(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["cognito"] \
            ["participant_user_pool_domain"]

    @participant_user_pool_domain.setter
    def participant_user_pool_domain(self, value: str) -> None:
        self.project_config["aws"]["cognito"] \
            ["participant_user_pool_domain"] = value
        self.write_project_config()

    @property
    def participant_user_pool_id(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["cognito"] \
            ["participant_user_pool_id"]

    @participant_user_pool_id.setter
    def participant_user_pool_id(self, value: str) -> None:
        self.project_config["aws"]["cognito"] \
            ["participant_user_pool_id"] = value
        self.write_project_config()

    @property
    def participant_client_id(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["cognito"] \
            ["participant_client_id"]

    @participant_client_id.setter
    def participant_client_id(self, value: str) -> None:
        self.project_config["aws"]["cognito"] \
            ["participant_client_id"] = value
        self.write_project_config()

    @property
    def researcher_user_pool_name(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["cognito"] \
            ["researcher_user_pool_name"]

    @researcher_user_pool_name.setter
    def researcher_user_pool_name(self, value: str) -> None:
        self.project_config["aws"]["cognito"] \
            ["researcher_user_pool_name"] = value
        self.write_project_config()

    @property
    def researcher_user_pool_domain(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["cognito"] \
            ["researcher_user_pool_domain"]

    @researcher_user_pool_domain.setter
    def researcher_user_pool_domain(self, value: str) -> None:
        self.project_config["aws"]["cognito"] \
            ["researcher_user_pool_domain"] = value
        self.write_project_config()

    @property
    def researcher_user_pool_id(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["cognito"] \
            ["researcher_user_pool_id"]

    @researcher_user_pool_id.setter
    def researcher_user_pool_id(self, value: str) -> None:
        self.project_config["aws"]["cognito"] \
            ["researcher_user_pool_id"] = value
        self.write_project_config()

    @property
    def researcher_client_id(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["cognito"] \
            ["researcher_client_id"]

    @researcher_client_id.setter
    def researcher_client_id(self, value: str) -> None:
        self.project_config["aws"]["cognito"] \
            ["researcher_client_id"] = value
        self.write_project_config()

    @property
    def logs_bucket_name(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["s3"] \
            ["logs_bucket_name"]

    @logs_bucket_name.setter
    def logs_bucket_name(self, value: str) -> None:
        self.project_config["aws"]["s3"]["logs_bucket_name"] = value
        self.write_project_config()

    @property
    def audio_bucket_name(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["s3"] \
            ["audio_bucket_name"]

    @audio_bucket_name.setter
    def audio_bucket_name(self, value: str) -> None:
        self.project_config["aws"]["s3"]["audio_bucket_name"] = value
        self.write_project_config()

    @property
    def secret_name(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["secrets_manager"] \
            ["secret_name"]

    @secret_name.setter
    def secret_name(self, value: str) -> None:
        self.project_config["aws"]["secrets_manager"]["secret_name"] = value
        self.write_project_config()

    @property
    def tokens_secret_name(self) -> str:
        if self.project_config is None:
            return ""
        return self.project_config["aws"]["secrets_manager"] \
            ["tokens_secret_name"]

    @tokens_secret_name.setter
    def tokens_secret_name(self, value: str) -> None:
        self.project_config["aws"]["secrets_manager"] \
            ["tokens_secret_name"] = value
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
        return self.project_config["docker"] \
            ["wearable_data_retrieval_container_name"]

    @wearable_data_retrieval_container_name.setter
    def wearable_data_retrieval_container_name(self, value: str) -> None:
        self.project_config["docker"] \
            ["wearable_data_retrieval_container_name"] = value
        self.write_project_config()

    def initialize_project_config(self) -> None:
        self.get_user_input()
        self.setup_project_config()
        self.write_project_config()

    def get_user_input(self) -> None:
        print("\nThis script will install the development environment for the "
              "project.")
        self.logger.magenta("The following will be configured and installed:")
        self.logger("- AWS CLI")
        self.logger("- Python 3.13")
        self.logger("- Python packages")
        self.logger("- Amazon Cognito user pools and clients")
        self.logger("- Amazon S3 buckets")
        self.logger("- Development secrets on AWS Secrets ResourceManager")
        self.logger("- Local .env files")
        self.logger("- Docker containers for the project")

        if input("\nDo you want to continue? (y/n): ").lower() != "y":
            self.logger.red("Installation cancelled")
            sys.exit(1)

        """Get user input for project setup."""
        # Get project name
        project_name = ""
        while not is_valid_name(project_name):
            project_name = input("\nEnter a name for your project: ")
            if not is_valid_name(project_name):
                self.logger.red("Invalid name")
            elif self.project_suffix:
                project_name = f"{project_name}-{self.project_suffix}"

        # Get Fitbit credentials
        fitbit_client_id = getpass("Enter your dev Fitbit client ID: ")
        fitbit_client_secret = getpass("Enter your dev Fitbit client secret: ")

        # Get admin email
        admin_email = ""
        while not is_valid_email(admin_email):
            admin_email = input("Enter an email to login as admin: ")
            if not is_valid_email(admin_email):
                self.logger.red("Invalid email")

        self.user_input = {
            "project_name": project_name,
            "fitbit_client_id": fitbit_client_id,
            "fitbit_client_secret": fitbit_client_secret,
            "admin_email": admin_email
        }

    def setup_project_config(self) -> None:
        """Set up project config."""
        cognito_config: CognitoConfig = {
            "participant_user_pool_name": \
                self.format_string(FString.participant_user_pool_name),
            "participant_user_pool_domain": \
                self.format_string(FString.participant_user_pool_domain),
            "participant_user_pool_id": "",
            "participant_client_id": "",
            "researcher_user_pool_name": \
                self.format_string(FString.researcher_user_pool_name),
            "researcher_user_pool_domain": \
                self.format_string(FString.researcher_user_pool_domain),
            "researcher_user_pool_id": "",
            "researcher_client_id": ""
        }

        s3_config: S3Config = {
            "logs_bucket_name": self.format_string(FString.logs_bucket_name),
            "audio_bucket_name": self.format_string(FString.audio_bucket_name)
        }

        secrets_manager_config: SecretsResourceManagerConfig = {
            "secret_name": self.format_string(FString.secret_name),
            "tokens_secret_name": self.format_string(FString.tokens_secret_name)
        }

        docker_config: DockerConfig = {
            "network_name": self.format_string(FString.network_name),
            "postgres_container_name": \
                self.format_string(FString.postgres_container_name),
            "wearable_data_retrieval_container_name": \
                self.format_string(
                    FString.wearable_data_retrieval_container_name
                )
        }

        self.project_config = {
            "project_name": self.project_name,
            "admin_email": self.admin_email,
            "aws": {
                "cognito": cognito_config,
                "s3": s3_config,
                "secrets_manager": secrets_manager_config,
                "stack_name": self.format_string(FString.stack_name)
            },
            "docker": docker_config
        }

    def format_string(self, fstr: str) -> str:
        return fstr.format(project_name=self.project_name)

    def write_project_config(self) -> None:
        """Write project config to a JSON file."""
        filename = self.format_string(self.project_config_filename)
        with open(filename, "w") as f:
            json.dump(self.project_config, f, indent=4)
