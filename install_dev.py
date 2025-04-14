#!/usr/bin/env python3

from enum import Enum
from getpass import getpass
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
from typing import TypedDict, Optional, Literal, Any

import boto3
from botocore.exceptions import ClientError
import docker

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
    return bool(
        re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)
    )


class AWSClientProvider:
    sts_client: Any
    cognito_client: Any
    s3_client: Any
    secrets_manager_client: Any
    cloudformation_client: Any
    ecr_client: Any

    def __init__(self):
        self.sts_client = boto3.client("sts")
        self.cognito_client = boto3.client("cognito-idp")
        self.s3_client = boto3.client("s3")
        self.secrets_manager_client = boto3.client("secretsmanager")
        self.cloudformation_client = boto3.client("cloudformation")
        self.ecr_client = boto3.client("ecr")

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
    __aws_account_id: Optional[str]
    __aws_region: Optional[str]
    __aws_access_key_id: Optional[str]
    __aws_secret_access_key: Optional[str]

    def __init__(
            self, *,
            logger: Logger,
            aws_client_provider: AWSClientProvider
        ):
        self.logger = logger
        self.sts_client = aws_client_provider.sts_client
        self.__aws_account_id = None
        self.__aws_region = None
        self.__aws_access_key_id = None
        self.__aws_secret_access_key = None

    def run(self) -> None:
        """Run the AWS account handler."""
        self.logger.cyan("\n[AWS CLI Setup]")

        try:
            subprocess.run(["aws", "configure"])
            self.__aws_access_key_id = subprocess.check_output(
                ["aws", "configure", "get", "aws_access_key_id"]
            ).decode("utf-8").strip()
            self.__aws_secret_access_key = subprocess.check_output(
                ["aws", "configure", "get", "aws_secret_access_key"]
            ).decode("utf-8").strip()
            self.__aws_region = subprocess.check_output(
                ["aws", "configure", "get", "region"]
            ).decode("utf-8").strip()
            self.__aws_account_id = self.sts_client \
                .get_caller_identity()["Account"]
        except (subprocess.CalledProcessError, ClientError):
            traceback.print_exc()
            self.logger.red("AWS configuration failed")
            sys.exit(1)

    @property
    def aws_region(self) -> str:
        if self.__aws_region is None:
            self.run()
        return self.__aws_region

    @property
    def aws_access_key_id(self) -> str:
        if self.__aws_access_key_id is None:
            self.run()
        return self.__aws_access_key_id

    @property
    def aws_secret_access_key(self) -> str:
        if self.__aws_secret_access_key is None:
            self.run()
        return self.__aws_secret_access_key
    
    @property
    def aws_account_id(self) -> str:
        if self.__aws_account_id is None:
            self.run()
        return self.__aws_account_id


class ProjectSettingsHandler:
    project_settings_filename: str = "project-settings-{project_name}.json"
    user_input: Optional[UserInput]
    project_settings: Optional[ProjectSettings]

    def __init__(
            self, *,
            logger: Logger,
            project_suffix: Optional[str] = None
        ):
        self.logger = logger
        self.project_settings = None
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
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["cognito"] \
            ["participant_user_pool_name"]

    @participant_user_pool_name.setter
    def participant_user_pool_name(self, value: str) -> None:
        self.project_settings["aws"]["cognito"] \
            ["participant_user_pool_name"] = value
        self.write_project_settings()

    @property
    def participant_user_pool_domain(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["cognito"] \
            ["participant_user_pool_domain"]

    @participant_user_pool_domain.setter
    def participant_user_pool_domain(self, value: str) -> None:
        self.project_settings["aws"]["cognito"] \
            ["participant_user_pool_domain"] = value
        self.write_project_settings()

    @property
    def participant_user_pool_id(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["cognito"] \
            ["participant_user_pool_id"]

    @participant_user_pool_id.setter
    def participant_user_pool_id(self, value: str) -> None:
        self.project_settings["aws"]["cognito"] \
            ["participant_user_pool_id"] = value
        self.write_project_settings()

    @property
    def participant_client_id(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["cognito"] \
            ["participant_client_id"]

    @participant_client_id.setter
    def participant_client_id(self, value: str) -> None:
        self.project_settings["aws"]["cognito"] \
            ["participant_client_id"] = value
        self.write_project_settings()

    @property
    def researcher_user_pool_name(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["cognito"] \
            ["researcher_user_pool_name"]

    @researcher_user_pool_name.setter
    def researcher_user_pool_name(self, value: str) -> None:
        self.project_settings["aws"]["cognito"] \
            ["researcher_user_pool_name"] = value
        self.write_project_settings()

    @property
    def researcher_user_pool_domain(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["cognito"] \
            ["researcher_user_pool_domain"]

    @researcher_user_pool_domain.setter
    def researcher_user_pool_domain(self, value: str) -> None:
        self.project_settings["aws"]["cognito"] \
            ["researcher_user_pool_domain"] = value
        self.write_project_settings()

    @property
    def researcher_user_pool_id(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["cognito"] \
            ["researcher_user_pool_id"]

    @researcher_user_pool_id.setter
    def researcher_user_pool_id(self, value: str) -> None:
        self.project_settings["aws"]["cognito"] \
            ["researcher_user_pool_id"] = value
        self.write_project_settings()

    @property
    def researcher_client_id(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["cognito"] \
            ["researcher_client_id"]

    @researcher_client_id.setter
    def researcher_client_id(self, value: str) -> None:
        self.project_settings["aws"]["cognito"] \
            ["researcher_client_id"] = value
        self.write_project_settings()

    @property
    def logs_bucket_name(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["s3"] \
            ["logs_bucket_name"]

    @logs_bucket_name.setter
    def logs_bucket_name(self, value: str) -> None:
        self.project_settings["aws"]["s3"]["logs_bucket_name"] = value
        self.write_project_settings()

    @property
    def audio_bucket_name(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["s3"] \
            ["audio_bucket_name"]

    @audio_bucket_name.setter
    def audio_bucket_name(self, value: str) -> None:
        self.project_settings["aws"]["s3"]["audio_bucket_name"] = value
        self.write_project_settings()

    @property
    def secret_name(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["secrets_manager"] \
            ["secret_name"]

    @secret_name.setter
    def secret_name(self, value: str) -> None:
        self.project_settings["aws"]["secrets_manager"]["secret_name"] = value
        self.write_project_settings()

    @property
    def tokens_secret_name(self) -> str:
        if self.project_settings is None:
            return ""
        return self.project_settings["aws"]["secrets_manager"] \
            ["tokens_secret_name"]

    @tokens_secret_name.setter
    def tokens_secret_name(self, value: str) -> None:
        self.project_settings["aws"]["secrets_manager"] \
            ["tokens_secret_name"] = value
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
        return self.project_settings["docker"] \
            ["wearable_data_retrieval_container_name"]

    @wearable_data_retrieval_container_name.setter
    def wearable_data_retrieval_container_name(self, value: str) -> None:
        self.project_settings["docker"] \
            ["wearable_data_retrieval_container_name"] = value
        self.write_project_settings()

    def run(self) -> None:
        """Initialize the project settings handler."""
        self.get_user_input()
        self.setup_project_settings()
        self.write_project_settings()

    def get_user_input(self) -> None:
        """Get user input for project setup."""
        print("\nThis script will install the development environment for the "
              "project.")
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

    def setup_project_settings(self) -> None:
        """Set up project settings."""
        cognito_settings: CognitoSettings = {
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

        s3_settings: S3Settings = {
            "logs_bucket_name": self.format_string(FString.logs_bucket_name),
            "audio_bucket_name": self.format_string(FString.audio_bucket_name)
        }

        secrets_manager_settings: SecretsManagerSettings = {
            "secret_name": self.format_string(FString.secret_name),
            "tokens_secret_name": self.format_string(FString.tokens_secret_name)
        }

        docker_settings: DockerSettings = {
            "network_name": self.format_string(FString.network_name),
            "postgres_container_name": \
                self.format_string(FString.postgres_container_name),
            "wearable_data_retrieval_container_name": \
                self.format_string(
                    FString.wearable_data_retrieval_container_name
                )
        }

        self.project_settings = {
            "project_name": self.project_name,
            "admin_email": self.admin_email,
            "aws": {
                "cognito": cognito_settings,
                "s3": s3_settings,
                "secrets_manager": secrets_manager_settings,
                "stack_name": self.format_string(FString.stack_name)
            },
            "docker": docker_settings
        }

    def format_string(self, fstr: str) -> str:
        return fstr.format(project_name=self.project_name)

    def write_project_settings(self) -> None:
        """Write project settings to a JSON file."""
        filename = self.format_string(self.project_settings_filename)
        with open(filename, "w") as f:
            json.dump(self.project_settings, f, indent=4)


class AwsResourcesHandler:
    cloudformation_template_filename: str = "cloudformation/dev-environment.yml"

    def __init__(
            self, *,
            logger: Logger,
            settings: ProjectSettingsHandler,
            aws_client_provider: AWSClientProvider
        ):
        self.logger = logger
        self.settings = settings
        self.client = aws_client_provider.cloudformation_client
        self.cognito_client = aws_client_provider.cognito_client
        self.secrets_client = aws_client_provider.secrets_manager_client

    def run(self) -> None:
        """Run the AWS resources handler."""
        self.logger.cyan("\n[AWS Resource Setup]")
        self.setup_aws_resources()
        self.create_admin_user()

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
                    {
                        "ParameterKey": "ParticipantUserPoolName",
                        "ParameterValue": \
                            self.settings.participant_user_pool_name
                    },
                    {
                        "ParameterKey": "ParticipantUserPoolDomainName",
                        "ParameterValue": \
                            self.settings.participant_user_pool_domain
                    },
                    {
                        "ParameterKey": "ResearcherUserPoolName",
                        "ParameterValue": \
                            self.settings.researcher_user_pool_name
                    },
                    {
                        "ParameterKey": "ResearcherUserPoolDomainName",
                        "ParameterValue": \
                            self.settings.researcher_user_pool_domain
                    },
                    {
                        "ParameterKey": "LogsBucketName",
                        "ParameterValue": self.settings.logs_bucket_name
                    },
                    {
                        "ParameterKey": "AudioBucketName",
                        "ParameterValue": self.settings.audio_bucket_name
                    },
                    {
                        "ParameterKey": "SecretName",
                        "ParameterValue": self.settings.secret_name
                    },
                    {
                        "ParameterKey": "TokensSecretName",
                        "ParameterValue": self.settings.tokens_secret_name
                    },
                ],
                Capabilities=["CAPABILITY_IAM"]
            )

            # Wait for stack creation to complete
            print("Waiting for AWS resources to be created...")
            waiter = self.client.get_waiter("stack_create_complete")
            waiter.wait(StackName=self.settings.stack_name)

            # Get stack outputs
            response = self.client \
                .describe_stacks(StackName=self.settings.stack_name)
            outputs = {
                output["OutputKey"]: output["OutputValue"]
                for output in response["Stacks"][0]["Outputs"]
            }

            self.settings.participant_user_pool_id = \
                outputs["ParticipantUserPoolId"]
            self.settings.participant_client_id = outputs["ParticipantClientId"]
            self.settings.researcher_user_pool_id = \
                outputs["ResearcherUserPoolId"]
            self.settings.researcher_client_id = outputs["ResearcherClientId"]

            self.logger.green("AWS resources created successfully")

        except ClientError as e:
            traceback.print_exc()
            self.logger.red("AWS resource creation failed")
            sys.exit(1)

    def create_admin_user(self) -> None:
        """Create an admin user in the Cognito user pool."""
        self.cognito_client.admin_create_user(
            UserPoolId=self.settings.participant_user_pool_id,
            Username=self.settings.admin_email,
        )

    def get_participant_client_secret(self) -> str:
        return self.cognito_client.describe_user_pool_client(
            UserPoolId=self.settings.participant_user_pool_id,
            ClientId=self.settings.participant_client_id
        )["UserPoolClient"]["ClientSecret"]

    def get_researcher_client_secret(self) -> str:
        return self.cognito_client.describe_user_pool_client(
            UserPoolId=self.settings.researcher_user_pool_id,
            ClientId=self.settings.researcher_client_id
        )["UserPoolClient"]["ClientSecret"]

    # def wait_for_stack_creation(self) -> None:
    #     """Wait for the stack creation to complete."""
    #     waiter = self.client.get_waiter("stack_create_complete")
    #     waiter.wait(StackName=self.settings.stack_name)

    #     while True:
    #         try:
    #             response = self.client.describe_stacks(StackName=self.settings.stack_name)
    #             if response["Stacks"][0]["StackStatus"] == "CREATE_COMPLETE":
    #                 break
    #             time.sleep(1)

class SecretValue(TypedDict):
    FITBIT_CLIENT_ID: str
    FITBIT_CLIENT_SECRET: str
    COGNITO_PARTICIPANT_CLIENT_SECRET: str
    COGNITO_RESEARCHER_CLIENT_SECRET: str


class SecretValueHandler:
    secret_value: Optional[SecretValue]

    def __init__(
            self, *,
            logger: Logger,
            settings: ProjectSettingsHandler,
            aws_resources_handler: AwsResourcesHandler,
            aws_client_provider: AWSClientProvider
        ):
        self.logger = logger
        self.settings = settings
        self.aws_resources_handler = aws_resources_handler
        self.secrets_client = aws_client_provider.secrets_manager_client
        self.secret_value = None

    def run(self) -> None:
        """Run the secret value handler."""
        self.logger.cyan("\n[Secret Value Setup]")
        self.set_secret_value()
        self.write_secret()

    def set_secret_value(self) -> None:
        """Set the secret value."""
        self.secret_value = {
            "FITBIT_CLIENT_ID": self.settings.fitbit_client_id,
            "FITBIT_CLIENT_SECRET": self.settings.fitbit_client_secret,
            "COGNITO_PARTICIPANT_CLIENT_SECRET": self.aws_resources_handler \
                .get_participant_client_secret(),
            "COGNITO_RESEARCHER_CLIENT_SECRET": self.aws_resources_handler \
                .get_researcher_client_secret()
        }

    def write_secret(self) -> None:
        """Write the secret value to the secret manager."""
        self.secrets_client.put_secret_value(
            SecretId=self.settings.secret_name,
            SecretString=json.dumps(self.secret_value)
        )

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
            subprocess.run(
                [self.python_version, "-m", "venv", self.env_name],
                check=True
            )

        # Activate virtual environment and install packages
        if sys.platform == "win32":
            activate_script = f"{self.env_name}\\Scripts\\activate"
        else:
            activate_script = f"source {self.env_name}/bin/activate"

        subprocess.run(
            f"{activate_script} && pip install -qr "
            f"{self.requirements_filename}",
            shell=True,
            check=True
        )

        self.logger.green("Python environment setup successfully")


class DockerHandler:
    def __init__(
            self, *,
            logger: Logger,
            settings: ProjectSettingsHandler,
            aws_account_handler: AwsAccountHandler,
            aws_client_provider: AWSClientProvider
        ):
        self.logger = logger
        self.settings = settings
        self.aws_account_handler = aws_account_handler
        self.docker_client = docker.from_env()
        self.ecr_client = aws_client_provider.ecr_client

    def run(self) -> None:
        """Run the Docker handler."""
        try:
            # NOTE: This is a workaround to login to ECR. See: https://github.com/docker/docker-py/issues/2256
            password = self.ecr_client.get_authorization_token() \
                ["authorizationData"][0]["authorizationToken"]
            subprocess.run([
                "docker", "login",
                "--username", "AWS",
                "--password-stdin",
                f"{self.aws_account_handler.aws_account_id}.dkr.ecr."
                f"{self.aws_account_handler.aws_region}.amazonaws.com"
            ], input=password.encode("utf-8"), check=True)
        except subprocess.CalledProcessError:
            traceback.print_exc()
            self.logger.red("ECR login failed")
            sys.exit(1)

        self.setup_postgres_container()
        self.setup_wearable_data_retrieval_container()

    def setup_postgres_container(self) -> None:
        """Set up Postgres container."""
        self.logger.cyan("\n[Docker Setup]")

        # Create Docker network
        self.docker_client.networks.create(self.settings.network_name)
        self.logger.blue(f"Created docker network {self.settings.network_name}")

        # Create Postgres container
        self.docker_client.containers.run(
            image="postgres",
            name=self.settings.postgres_container_name,
            environment={
                "POSTGRES_USER": Postgres.USER,
                "POSTGRES_PASSWORD": Postgres.PASSWORD,
                "POSTGRES_DB": Postgres.DB,
            },
            ports={Postgres.PORT: Postgres.PORT},
            network=self.settings.network_name,
        )

        # Wait for Postgres to be ready
        while True:
            try:
                response = self.docker_client.containers \
                    .get(self.settings.postgres_container_name) \
                    .exec_run([
                        "pg_isready",
                        "-U", Postgres.USER,
                        "-d", Postgres.DB
                    ])
                if (
                    response.exit_code == 0
                    and "accepting connections"
                    in response.output.decode("utf-8").strip()
                ):
                    break
                else:
                    time.sleep(1)
            except docker.errors.NotFoundError:
                time.sleep(1)

        self.logger.blue(
            f"Created postgres container "
            f"{self.settings.postgres_container_name}"
        )

        try:
            subprocess.run(
                ["flask", "--app", "run.py", "db", "upgrade"],
                check=True
            )
        except subprocess.CalledProcessError:
            traceback.print_exc()
            self.logger.red("Database upgrade failed")
            sys.exit(1)

        try:
            subprocess.run(
                ["flask", "--app", "run.py", "init-integration-testing-db"],
                check=True
            )
        except subprocess.CalledProcessError:
            traceback.print_exc()
            self.logger \
                .red("Integration testing database initialization failed")
            sys.exit(1)

        try:
            subprocess.run([
                "flask",
                "--app", "run.py",
                "create-researcher-account",
                "--email", self.settings.admin_email
            ], check=True)
        except subprocess.CalledProcessError:
            traceback.print_exc()
            self.logger.red("Researcher account creation failed")
            sys.exit(1)

        self.logger.blue(
            f"Created researcher account "
            f"{self.settings.admin_email}"
        )

    def setup_wearable_data_retrieval_container(self) -> None:
        """Set up wearable data retrieval container."""
        self.logger.cyan("\n[Wearable Data Retrieval Container Setup]")

        self.logger.blue("Logged in to ECR")

        shutil.copytree("shared", "functions/wearable_data_retrieval/shared")

        try:
            self.docker_client.images.build(
                path="functions/wearable_data_retrieval",
                tag=self.settings.wearable_data_retrieval_container_name,
                platform="linux/amd64"
            )
        except docker.errors.BuildError:
            traceback.print_exc()
            self.logger.red("Wearable data retrieval container creation failed")
            sys.exit(1)

        shutil.rmtree("functions/wearable_data_retrieval/shared")

        try:
            self.docker_client.containers.run(
                image=self.settings.wearable_data_retrieval_container_name,
                name=self.settings.wearable_data_retrieval_container_name,
                platform="linux/amd64",
                network=self.settings.network_name,
                ports={"9000": 8080},
                environment={"TESTING": "true"},
                detach=True
            )
        except docker.errors.ContainerError:
            traceback.print_exc()
            self.logger.red("Wearable data retrieval container creation failed")
            sys.exit(1)

        self.logger.blue(
            f"Created wearable data retrieval container "
            f"{self.settings.wearable_data_retrieval_container_name}"
        )


class EnvHandler:
    wearable_data_retrieval_env: WearableDataRetrievalEnv
    root_env: RootEnv

    def __init__(
            self, *,
            logger: Logger,
            settings: ProjectSettingsHandler,
            aws_account_handler: AwsAccountHandler
        ):
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
    project_settings_handler = ProjectSettingsHandler(
        logger=logger,
        project_suffix=suffix,
    )
    aws_resources_handler = AwsResourcesHandler(
        logger=logger,
        settings=project_settings_handler,
    )
    python_env_handler = PythonEnvHandler(
        logger=logger,
        settings=project_settings_handler,
    )
    docker_handler = DockerHandler(
        logger=logger,
        settings=project_settings_handler,
        aws_account_handler=aws_account_handler,
    )
    env_handler = EnvHandler(
        logger=logger,
        settings=project_settings_handler,
        aws_account_handler=aws_account_handler,
    )
    frontend_handler = FrontendHandler(
        logger=logger,
        settings=project_settings_handler,
    )

    try:
        aws_account_handler.run()
        project_settings_handler.run()
        # aws_resources_handler.run()
        python_env_handler.run()
        docker_handler.run()
        env_handler.run()
        frontend_handler.run()

        logger.green("\n[Installation complete]")
        logger.cyan(
            "Check your email for a temporary password for the researcher "
            "admin user"
        )
        logger.blue(
            "You can now start the development server with npm run start and "
            "flask run"
        )

    except Exception:
        traceback.print_exc()
        logger.red("Installation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
