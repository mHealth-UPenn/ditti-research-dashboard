#!/usr/bin/env python3

from enum import Enum
import json
import os
import re
import shutil
import subprocess
import sys
import time
from typing import TypedDict, Optional, Literal

import boto3
from botocore.exceptions import ClientError

type Env = Literal["dev", "staging","prod"]


def is_valid_name(name: str) -> bool:
    """Validate project name."""
    if not name:
        return False
    return bool(re.match(r"^[a-zA-Z0-9_-]+$", name)) and len(name) <= 64


def is_valid_email(email: str) -> bool:
    """Validate email address."""
    if not email:
        return False
    return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email))


class Logger:
    def __init__(self):
        self.color_codes = {
            "red": "\033[0;31m",
            "green": "\033[0;32m",
            "yellow": "\033[0;33m",
            "blue": "\033[0;34m",
            "magenta": "\033[0;35m",
            "cyan": "\033[0;36m",
            "reset": "\033[0m"
        }

    def __call__(self, text: str) -> None:
        print(text)

    def print_colored(self, text: str, color: str) -> None:
        print(f"{self.color_codes[color]}{text}{self.color_codes['reset']}")

    def red(self, text: str) -> None:
        self.print_colored(text, "red")

    def green(self, text: str) -> None:
        self.print_colored(text, "green")

    def yellow(self, text: str) -> None:
        self.print_colored(text, "yellow")

    def blue(self, text: str) -> None:
        self.print_colored(text, "blue")

    def magenta(self, text: str) -> None:
        self.print_colored(text, "magenta")

    def cyan(self, text: str) -> None:
        self.print_colored(text, "cyan")


class Postgres(Enum):
    USER = "username"
    PASSWORD = "password"
    PORT = 5432
    DB = "database_name"


class FString(Enum):
    participant_user_pool_name="{project_name}-participant-pool"
    participant_user_pool_domain="{project_name}-participant"
    researcher_user_pool_name="{project_name}-researcher-pool"
    researcher_user_pool_domain="{project_name}-researcher"
    logs_bucket_name="{project_name}-wearable-data-retrieval-logs"
    audio_bucket_name="{project_name}-audio-files"
    secret_name="{project_name}-secret"
    tokens_secret_name="{project_name}-Fitbit-tokens"
    stack_name="{project_name}-stack"
    network_name="{project_name}-network"
    postgres_container_name="{project_name}-postgres"
    wearable_data_retrieval_container_name="{project_name}-wearable-data-retrieval"


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


class SecretsManagerSettings(TypedDict):
    secret_name: str
    tokens_secret_name: str


class DockerSettings(TypedDict):
    network_name: str
    postgres_container_name: str
    wearable_data_retrieval_container_name: str


class AwsSettings(TypedDict):
    cognito: CognitoSettings
    s3: S3Settings
    secrets_manager: SecretsManagerSettings
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


class AwsAccountHandler:
    aws_account_id: str

    def __init__(self, *, logger: Logger):
        self.logger = logger
        self.aws_account_id = boto3.client("sts").get_caller_identity()["Account"]

    @property
    def aws_region(self) -> str:
        return os.environ.get("AWS_DEFAULT_REGION", "")

    @property
    def aws_access_key_id(self) -> str:
        return os.environ.get("AWS_ACCESS_KEY_ID", "")

    @property
    def aws_secret_access_key(self) -> str:
        return os.environ.get("AWS_SECRET_ACCESS_KEY", "")


class ProjectSettingsHandler:
    project_settings_filename: str = "project-settings-{project_name}.json"
    user_input: UserInput
    project_settings: Optional[ProjectSettings]

    def __init__(
            self, *,
            logger: Logger,
            project_suffix: Optional[str] = None
        ):
        self.logger = logger
        self.project_settings = None
        self.user_input = {}
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
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["cognito"]["participant_user_pool_name"]

    @participant_user_pool_name.setter
    def participant_user_pool_name(self, value: str) -> None:
        self.project_settings["aws"]["cognito"]["participant_user_pool_name"] = value
        self.write_project_settings()

    @property
    def participant_user_pool_domain(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["cognito"]["participant_user_pool_domain"]

    @participant_user_pool_domain.setter
    def participant_user_pool_domain(self, value: str) -> None:
        self.project_settings["aws"]["cognito"]["participant_user_pool_domain"] = value
        self.write_project_settings()

    @property
    def participant_user_pool_id(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["cognito"]["participant_user_pool_id"]

    @participant_user_pool_id.setter
    def participant_user_pool_id(self, value: str) -> None:
        self.project_settings["aws"]["cognito"]["participant_user_pool_id"] = value
        self.write_project_settings()

    @property
    def participant_client_id(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["cognito"]["participant_client_id"]

    @participant_client_id.setter
    def participant_client_id(self, value: str) -> None:
        self.project_settings["aws"]["cognito"]["participant_client_id"] = value
        self.write_project_settings()

    @property
    def researcher_user_pool_name(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["cognito"]["researcher_user_pool_name"]

    @researcher_user_pool_name.setter
    def researcher_user_pool_name(self, value: str) -> None:
        self.project_settings["aws"]["cognito"]["researcher_user_pool_name"] = value
        self.write_project_settings()

    @property
    def researcher_user_pool_domain(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["cognito"]["researcher_user_pool_domain"]

    @researcher_user_pool_domain.setter
    def researcher_user_pool_domain(self, value: str) -> None:
        self.project_settings["aws"]["cognito"]["researcher_user_pool_domain"] = value
        self.write_project_settings()

    @property
    def researcher_user_pool_id(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["cognito"]["researcher_user_pool_id"]

    @researcher_user_pool_id.setter
    def researcher_user_pool_id(self, value: str) -> None:
        self.project_settings["aws"]["cognito"]["researcher_user_pool_id"] = value
        self.write_project_settings()

    @property
    def researcher_client_id(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["cognito"]["researcher_client_id"]

    @researcher_client_id.setter
    def researcher_client_id(self, value: str) -> None:
        self.project_settings["aws"]["cognito"]["researcher_client_id"] = value
        self.write_project_settings()

    @property
    def logs_bucket_name(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["s3"]["logs_bucket_name"]

    @logs_bucket_name.setter
    def logs_bucket_name(self, value: str) -> None:
        self.project_settings["aws"]["s3"]["logs_bucket_name"] = value
        self.write_project_settings()

    @property
    def audio_bucket_name(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["s3"]["audio_bucket_name"]

    @audio_bucket_name.setter
    def audio_bucket_name(self, value: str) -> None:
        self.project_settings["aws"]["s3"]["audio_bucket_name"] = value
        self.write_project_settings()

    @property
    def secret_name(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["secrets_manager"]["secret_name"]

    @secret_name.setter
    def secret_name(self, value: str) -> None:
        self.project_settings["aws"]["secrets_manager"]["secret_name"] = value
        self.write_project_settings()

    @property
    def tokens_secret_name(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["secrets_manager"]["tokens_secret_name"]

    @tokens_secret_name.setter
    def tokens_secret_name(self, value: str) -> None:
        self.project_settings["aws"]["secrets_manager"]["tokens_secret_name"] = value
        self.write_project_settings()

    @property
    def stack_name(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["stack_name"]

    @stack_name.setter
    def stack_name(self, value: str) -> None:
        self.project_settings["aws"]["stack_name"] = value
        self.write_project_settings()

    @property
    def network_name(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["docker"]["network_name"]

    @network_name.setter
    def network_name(self, value: str) -> None:
        self.project_settings["docker"]["network_name"] = value
        self.write_project_settings()

    @property
    def postgres_container_name(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["docker"]["postgres_container_name"]

    @postgres_container_name.setter
    def postgres_container_name(self, value: str) -> None:
        self.project_settings["docker"]["postgres_container_name"] = value
        self.write_project_settings()

    @property
    def wearable_data_retrieval_container_name(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["docker"]["wearable_data_retrieval_container_name"]

    @wearable_data_retrieval_container_name.setter
    def wearable_data_retrieval_container_name(self, value: str) -> None:
        self.project_settings["docker"]["wearable_data_retrieval_container_name"] = value
        self.write_project_settings()

    def run(self) -> None:
        """Initialize the project settings handler."""
        self.get_user_input()
        self.setup_project_settings()
        self.write_project_settings()

    def get_user_input(self) -> None:
        """Get user input for project setup."""
        print("\nThis script will install the development environment for the project.")
        self.logger.magenta("The following will be configured and installed:")
        self.logger("- AWS CLI")
        self.logger("- Python 3.13")
        self.logger("- Python packages")
        self.logger("- Amazon Cognito user pools and clients")
        self.logger("- Amazon S3 buckets")
        self.logger("- Development secrets on AWS Secrets Manager")
        self.logger("- Local .env files")
        self.logger("- Docker containers for the project")

        if input("\nDo you want to continue? (y/n): ").lower() != "y":
            self.logger.red("Installation cancelled")
            sys.exit(1)

        # Get project name
        project_name = ""
        while not is_valid_name(project_name):
            project_name = input("\nEnter a name for your project: ")
            if not is_valid_name(project_name):
                self.logger.red("Invalid name")
            elif self.project_suffix:
                project_name = f"{project_name}-{self.project_suffix}"

        # Get Fitbit credentials
        fitbit_client_id = input("Enter your dev Fitbit client ID: ")
        fitbit_client_secret = input("Enter your dev Fitbit client secret: ")

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

    def setup_project_settings(self) -> None:
        """Set up project settings."""
        cognito_settings: CognitoSettings = {
            "participant_user_pool_name": FString.participant_user_pool_name.value.format(project_name=self.user_input["project_name"]),
            "participant_user_pool_domain": FString.participant_user_pool_domain.value.format(project_name=self.user_input["project_name"]),
            "participant_user_pool_id": "",
            "participant_client_id": "",
            "researcher_user_pool_name": FString.researcher_user_pool_name.value.format(project_name=self.user_input["project_name"]),
            "researcher_user_pool_domain": FString.researcher_user_pool_domain.value.format(project_name=self.user_input["project_name"]),
            "researcher_user_pool_id": "",
            "researcher_client_id": ""
        }

        s3_settings: S3Settings = {
            "logs_bucket_name": FString.logs_bucket_name.value.format(project_name=self.user_input["project_name"]),
            "audio_bucket_name": FString.audio_bucket_name.value.format(project_name=self.user_input["project_name"])
        }

        secrets_manager_settings: SecretsManagerSettings = {
            "secret_name": FString.secret_name.value.format(project_name=self.user_input["project_name"]),
            "tokens_secret_name": FString.tokens_secret_name.value.format(project_name=self.user_input["project_name"])
        }

        docker_settings: DockerSettings = {
            "network_name": FString.network_name.value.format(project_name=self.user_input["project_name"]),
            "postgres_container_name": FString.postgres_container_name.value.format(project_name=self.user_input["project_name"]),
            "wearable_data_retrieval_container_name": FString.wearable_data_retrieval_container_name.value.format(project_name=self.user_input["project_name"])
        }

        self.project_settings = {
            "project_name": self.user_input["project_name"],
            "admin_email": self.user_input["admin_email"],
            "aws": {
                "cognito": cognito_settings,
                "s3": s3_settings,
                "secrets_manager": secrets_manager_settings,
                "stack_name": FString.stack_name.value.format(project_name=self.user_input["project_name"])
            },
            "docker": docker_settings
        }

    def write_project_settings(self) -> None:
        """Write project settings to a JSON file."""
        with open(self.project_settings_filename.format(project_name=self.user_input["project_name"]), "w") as f:
            json.dump(self.project_settings, f, indent=4)


class AwsResourcesHandler:
    outputs_filename: str = "{project_name}-outputs.json"
    cloudformation_template_filename: str = "cloudformation/dev-environment.yml"

    def __init__(self, *, logger: Logger, settings: ProjectSettingsHandler):
        self.logger = logger
        self.settings = settings
        self.client = boto3.client("cloudformation")
        self.outputs = {}

    def run(self) -> None:
        """Run the AWS resources handler."""
        self.setup_aws_resources()

    def setup_aws_resources(self):
        """Set up AWS resources using CloudFormation."""
        self.logger.cyan("\n[AWS Resource Setup]")

        # Read CloudFormation template
        with open(self.cloudformation_template_filename, "r") as f:
            template_body = f.read()

        # Create CloudFormation stack
        try:
            response = self.client.create_stack(
                StackName=self.settings.stack_name,
                TemplateBody=template_body,
                Parameters=[
                    {"ParameterKey": "ProjectName", "ParameterValue": self.settings.project_name},
                    {"ParameterKey": "AdminEmail", "ParameterValue": self.settings.admin_email},
                    {"ParameterKey": "FitbitClientId", "ParameterValue": self.settings.fitbit_client_id},
                    {"ParameterKey": "FitbitClientSecret", "ParameterValue": self.settings.fitbit_client_secret}
                ],
                Capabilities=["CAPABILITY_IAM"]
            )

            # Wait for stack creation to complete
            print("Waiting for AWS resources to be created...")
            waiter = self.client.get_waiter("stack_create_complete")
            waiter.wait(StackName=self.settings.stack_name)

            # Get stack outputs
            response = self.client.describe_stacks(StackName=self.settings.stack_name)
            self.outputs = {
                output["OutputKey"]: output["OutputValue"]
                for output in response["Stacks"][0]["Outputs"]
            }

            self.logger.green("AWS resources created successfully")

        except ClientError as e:
            self.logger.red(f"AWS resource creation failed: {str(e)}")
            sys.exit(1)

    def write_outputs(self) -> None:
        """Write outputs to a JSON file."""
        with open(self.outputs_filename.format(project_name=self.settings.project_name), "w") as f:
            json.dump(self.outputs, f, indent=4)


class PythonEnvHandler:
    python_version: str = "python3.13"
    env_name: str = "env"
    requirements_filename: str = "requirements.txt"

    def __init__(self, *, logger: Logger, settings: ProjectSettingsHandler):
        self.logger = logger
        self.settings = settings

    def run(self) -> None:
        """Run the Python environment handler."""
        self.setup_python_env()

    def setup_python_env(self) -> None:
        """Set up Python virtual environment and install packages."""
        self.logger.cyan("\n[Python Setup]")

        if not os.path.exists("env/bin/activate"):
            self.logger.cyan("Initializing Python virtual environment...")
            subprocess.run([self.python_version, "-m", "venv", self.env_name], check=True)

        # Activate virtual environment and install packages
        if sys.platform == "win32":
            activate_script = f"{self.env_name}\\Scripts\\activate"
        else:
            activate_script = f"source {self.env_name}/bin/activate"

        subprocess.run(
            f"{activate_script} && pip install -qr {self.requirements_filename}",
            shell=True,
            check=True
        )

        self.logger.green("Python environment setup successfully")


class DockerHandler:
    def __init__(self, *, logger: Logger, settings: ProjectSettingsHandler):
        self.logger = logger
        self.settings = settings

    def run(self) -> None:
        """Run the Docker handler."""
        self.setup_postgres_container()
        self.setup_wearable_data_retrieval_container()

    def setup_postgres_container(self) -> None:
        """Set up Postgres container."""
        self.logger.cyan("\n[Docker Setup]")

        # Create Docker network
        subprocess.run(["docker", "network", "create", self.settings.network_name], check=True)
        self.logger.blue(f"Created docker network {self.settings.network_name}")

        # Create Postgres container
        subprocess.run([
            "docker", "run",
            "-ditp", f"{Postgres.PORT}:{Postgres.PORT}",
            "--name", self.settings.postgres_container_name,
            "-e", f"POSTGRES_USER={Postgres.USER}",
            "-e", f"POSTGRES_PASSWORD={Postgres.PASSWORD}",
            "-e", f"POSTGRES_DB={Postgres.DB}",
            "-e", f"POSTGRES_PORT={Postgres.PORT}",
            "--network", self.settings.network_name,
            "postgres",
        ], check=True)

        # Wait for Postgres to be ready
        while True:
            try:
                subprocess.run([
                    "docker", "exec",
                    "-t", self.settings.postgres_container_name,
                    "pg_isready",
                    "-U", Postgres.USER,
                    "-d", Postgres.DB,
                ], check=True)
                break
            except subprocess.CalledProcessError:
                time.sleep(1)

        self.logger.blue(f"Created postgres container {self.settings.postgres_container_name}")

        try:
            subprocess.run(["flask", "--app", "run.py", "db", "upgrade"], check=True)
        except subprocess.CalledProcessError:
            self.logger.red("Database upgrade failed")
            sys.exit(1)

        try:
            subprocess.run(["flask", "--app", "run.py", "init-integration-testing-db"], check=True)
        except subprocess.CalledProcessError:
            self.logger.red("Integration testing database initialization failed")
            sys.exit(1)

        try:
            subprocess.run(["flask", "--app", "run.py", "create-researcher-account", "--email", self.settings.admin_email], check=True)
        except subprocess.CalledProcessError:
            self.logger.red("Researcher account creation failed")
            sys.exit(1)

        self.logger.blue(f"Created researcher account {self.settings.admin_email}")

    def setup_wearable_data_retrieval_container(self) -> None:
        """Set up wearable data retrieval container."""
        self.logger.cyan("\n[Wearable Data Retrieval Container Setup]")

        try:
            subprocess.run([
                "aws", "ecr", "get-login-password",
                "|", "docker", "login",
                "--username", "AWS",
                "--password-stdin", self.settings.aws_account_id
            ], check=True)
        except subprocess.CalledProcessError:
            self.logger.red("ECR login failed")
            sys.exit(1)

        self.logger.blue("Logged in to ECR")

        shutil.copytree("shared", "functions/wearable_data_retrieval/shared")

        try:
            subprocess.run([
                "docker", "build",
                "--platform", "linux/amd64",
                "-t", self.settings.wearable_data_retrieval_container_name,
                "functions/wearable_data_retrieval"
            ], check=True)
        except subprocess.CalledProcessError:
            self.logger.red("Wearable data retrieval container creation failed")
            sys.exit(1)

        shutil.rmtree("functions/wearable_data_retrieval/shared")

        subprocess.run([
            "docker", "run",
            "--platform", "linux/amd64",
            "--name", self.settings.wearable_data_retrieval_container_name,
            "--network", self.settings.network_name,
            "-ditp", "9000:8080",
            "--env-file", "functions/wearable_data_retrieval/.env",
            "-e", "TESTING=true",
            self.settings.wearable_data_retrieval_container_name
        ], check=True)

        self.logger.blue(f"Created wearable data retrieval container {self.settings.wearable_data_retrieval_container_name}")


class EnvHandler:
    wearable_data_retrieval_env: WearableDataRetrievalEnv
    root_env: RootEnv

    def __init__(self, *, logger: Logger, settings: ProjectSettingsHandler, aws_account_handler: AwsAccountHandler):
        self.logger = logger
        self.settings = settings
        self.aws_account_handler = aws_account_handler

    def run(self) -> None:
        """Run the environment handler."""
        self.create_wearable_data_retrieval_env()
        self.create_root_env()
        self.write_env_files()

    def create_wearable_data_retrieval_env(self) -> None:
        """Create wearable_data_retrieval/.env."""
        self.wearable_data_retrieval_env = {
            "DB_URI": f"postgresql://{Postgres.USER}:{Postgres.PASSWORD}@{self.settings.project_name}-postgres:{Postgres.PORT}/{Postgres.DB}",
            "S3_BUCKET": self.settings.logs_bucket_name,
            "AWS_CONFIG_SECRET_NAME": self.settings.secret_name,
            "AWS_ACCESS_KEY_ID": self.aws_account_handler.aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": self.aws_account_handler.aws_secret_access_key,
            "AWS_DEFAULT_REGION": self.aws_account_handler.aws_region,
        }

    def create_root_env(self) -> None:
        """Create .env."""
        self.root_env = {
            "FLASK_CONFIG": "Default",
            "FLASK_DEBUG": "True",
            "FLASK_DB": f"postgresql://{Postgres.USER}:{Postgres.PASSWORD}@localhost:{Postgres.PORT}/{Postgres.DB}",
            "FLASK_APP": "run.py",
            "APP_SYNC_HOST": "",
            "APPSYNC_ACCESS_KEY": "",
            "APPSYNC_SECRET_KEY": "",
            "AWS_AUDIO_FILE_BUCKET": self.settings.audio_bucket_name,
            "AWS_TABLENAME_AUDIO_FILE": "",
            "AWS_TABLENAME_AUDIO_TAP": "",
            "AWS_TABLENAME_TAP": "",
            "AWS_TABLENAME_USER": "",
            "COGNITO_PARTICIPANT_CLIENT_ID": self.settings.participant_client_id,
            "COGNITO_PARTICIPANT_DOMAIN": f"{self.settings.participant_user_pool_domain}.auth.{self.aws_account_handler.aws_region}.amazoncognito.com",
            "COGNITO_PARTICIPANT_REGION": self.aws_account_handler.aws_region,
            "COGNITO_PARTICIPANT_USER_POOL_ID": self.settings.participant_user_pool_id,
            "COGNITO_RESEARCHER_CLIENT_ID": self.settings.researcher_client_id,
            "COGNITO_RESEARCHER_DOMAIN": f"{self.settings.researcher_user_pool_domain}.auth.{self.aws_account_handler.aws_region}.amazoncognito.com",
            "COGNITO_RESEARCHER_REGION": self.aws_account_handler.aws_region,
            "COGNITO_RESEARCHER_USER_POOL_ID": self.settings.researcher_user_pool_id,
            "LOCAL_LAMBDA_ENDPOINT": "http://localhost:9000/2015-03-31/functions/function/invocations",
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


class FrontendHandler:
    def __init__(self, *, logger: Logger, settings: ProjectSettingsHandler):
        self.logger = logger
        self.settings = settings

    def run(self) -> None:
        """Run the frontend handler."""
        self.setup_frontend()

    def setup_frontend(self) -> None:
        """Set up frontend dependencies."""
        self.logger.cyan("\n[Frontend Setup]")

        os.chdir("frontend")
        subprocess.run(["npm", "install"], check=True)
        subprocess.run([
            "npx", "tailwindcss",
            "-i", "./src/index.css",
            "-o", "./src/output.css"
        ], check=True)
        os.chdir("..")

        self.logger.green("Frontend setup completed")


def main(env: Env = "dev"):
    """Main installation function."""
    suffix = ""
    match env:
        case "dev":
            suffix = "dev"
        case "staging":
            suffix = "staging"
        case _:
            pass

    logger = Logger()
    aws_account_handler = AwsAccountHandler(logger=logger)
    project_settings_handler = ProjectSettingsHandler(logger=logger, project_suffix=suffix)
    aws_resources_handler = AwsResourcesHandler(logger=logger, settings=project_settings_handler)
    python_env_handler = PythonEnvHandler(logger=logger, settings=project_settings_handler)
    docker_handler = DockerHandler(logger=logger, settings=project_settings_handler)
    env_handler = EnvHandler(logger=logger, settings=project_settings_handler, aws_account_handler=aws_account_handler)
    frontend_handler = FrontendHandler(logger=logger, settings=project_settings_handler)

    try:
        project_settings_handler.run()
        aws_resources_handler.run()
        python_env_handler.run()
        docker_handler.run()
        env_handler.run()
        frontend_handler.run()

        logger.green("\n[Installation complete]")
        logger.cyan("Check your email for a temporary password for the researcher admin user")
        logger.blue("You can now start the development server with npm run start and flask run")

    except Exception as e:
        logger.red(f"Installation failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
