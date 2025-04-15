import sys
import traceback

from install_scripts.project_config import ProjectConfigProvider
from install_scripts.aws_providers import (
    AwsAccountProvider,
    AwsClientProvider,
    AwsCloudformationProvider,
    AwsCognitoProvider,
    AwsEcrProvider,
)
from install_scripts.local_providers import (
    DockerProvider,
    EnvFileProvider,
    PythonEnvProvider,
    FrontendProvider,
)
from install_scripts.resource_managers import (
    AwsCloudformationResourceManager,
    AwsCognitoResourceManager,
    AwsSecretsmanagerResourceManager,
)
from install_scripts.utils import Logger
from install_scripts.utils.types import Env
from install_scripts.utils.exceptions import CancelInstallation

class Installer:
    def __init__(self, env: Env) -> None:
        self.logger = Logger()

        project_suffix = ""
        match env:
            case "dev":
                project_suffix = "dev"
            case "staging":
                project_suffix = "staging"
            case _:
                pass

        # Initialize project config provider
        self.project_config_provider = ProjectConfigProvider(
            logger=self.logger,
            project_suffix=project_suffix,
        )

        # Initialize AWS providers
        self.aws_client_provider = AwsClientProvider()
        self.aws_account_provider = AwsAccountProvider(
            logger=self.logger,
            aws_client_provider=self.aws_client_provider,
        )
        self.aws_cloudformation_provider = AwsCloudformationProvider(
            logger=self.logger,
            settings=self.project_config_provider,
            aws_client_provider=self.aws_client_provider,
        )
        self.aws_cognito_provider = AwsCognitoProvider(
            logger=self.logger,
            settings=self.project_config_provider,
            aws_client_provider=self.aws_client_provider,
        )
        self.aws_ecr_provider = AwsEcrProvider(
            logger=self.logger,
            settings=self.project_config_provider,
            aws_client_provider=self.aws_client_provider,
            aws_account_provider=self.aws_account_provider,
        )

        # Initialize local providers
        self.docker_provider = DockerProvider(
            logger=self.logger,
            settings=self.project_config_provider,
        )
        self.env_file_provider = EnvFileProvider(
            logger=self.logger,
            settings=self.project_config_provider,
            aws_account_provider=self.aws_account_provider,
        )
        self.python_env_provider = PythonEnvProvider(
            logger=self.logger,
            settings=self.project_config_provider,
        )
        self.frontend_provider = FrontendProvider(
            logger=self.logger,
            settings=self.project_config_provider,
        )

        # Initialize resource managers
        self.aws_cloudformation_resource_manager = AwsCloudformationResourceManager(
            logger=self.logger,
            settings=self.project_config_provider,
            aws_client_provider=self.aws_client_provider,
        )
        self.aws_cognito_resource_manager = AwsCognitoResourceManager(
            logger=self.logger,
            settings=self.project_config_provider,
            aws_client_provider=self.aws_client_provider,
        )
        self.aws_secretsmanager_resource_manager = AwsSecretsmanagerResourceManager(
            logger=self.logger,
            settings=self.project_config_provider,
            aws_client_provider=self.aws_client_provider,
            aws_cognito_provider=self.aws_cognito_provider,
        )

    def run(self) -> None:
        try:
            # Configure AWS CLI
            self.logger.cyan("\n[AWS CLI Configuration]")
            self.aws_account_provider.configure_aws_cli()

            # Get project settings
            self.logger.cyan("\n[Project Settings]")
            self.project_config_provider.get_user_input()
            self.project_config_provider.setup_project_config()
            self.project_config_provider.write_project_config()

            # Setup Python environment
            # self.logger.cyan("\n[Python Environment Setup]")
            # self.python_env_provider.initialize_python_env()
            # self.python_env_provider.install_requirements()

            # Setup Docker containers
            self.logger.cyan("\n[Docker Setup]")
            self.docker_provider.setup()

            # Setup CloudFormation stack
            self.logger.cyan("\n[CloudFormation Stack Setup]")
            self.aws_cloudformation_resource_manager.run(env="dev")

            outputs = self.aws_cloudformation_provider.get_outputs()
            self.project_config_provider.participant_user_pool_id = outputs["ParticipantUserPoolId"]
            self.project_config_provider.participant_client_id = outputs["ParticipantClientId"]
            self.project_config_provider.researcher_user_pool_id = outputs["ResearcherUserPoolId"]
            self.project_config_provider.researcher_client_id = outputs["ResearcherClientId"]

            # Setup Secrets Manager
            self.logger.cyan("\n[Secrets Manager Setup]")
            self.aws_secretsmanager_resource_manager.run(env="dev")

            # Setup Cognito
            self.logger.cyan("\n[Cognito Setup]")
            self.aws_cognito_resource_manager.run(env="dev")

            # Setup .env files
            self.logger.cyan("\n[Environment Files Setup]")
            wearable_data_retrieval_env = self.env_file_provider.get_wearable_data_retrieval_env()
            root_env = self.env_file_provider.get_root_env()
            self.env_file_provider.write_env_files(wearable_data_retrieval_env, root_env)

            # Setup frontend
            self.logger.cyan("\n[Frontend Setup]")
            self.frontend_provider.initialize_frontend()
            self.frontend_provider.build_frontend()

        except CancelInstallation:
            sys.exit(0)
        except Exception:
            traceback.print_exc()
            self.logger.red(f"Installation failed.")
            sys.exit(1)

    def uninstall(self, project_name: str, env: Env = "dev") -> None:
        """Uninstall the resources."""
        try:
            self.logger.red("This will delete all resources created by the installer.")
            self.logger.red("ANY LOST DATA WILL BE PERMANENTLY DELETED.")
            self.logger.red(f"Please confirm by typing \"{project_name}\".")
            confirm = input("> ")

            if confirm != project_name:
                self.logger.red("Uninstall cancelled.")
                sys.exit(0)

            # Configure AWS CLI
            self.logger.cyan("\n[AWS CLI Configuration]")
            self.aws_account_provider.configure_aws_cli()

            # Load project config
            self.project_config_provider.load_existing_config(project_name)

            if env == "dev":
                self.logger.cyan("\n[Docker Cleanup]")
                self.docker_provider.uninstall()

                self.logger.cyan("\n[.env Files Cleanup]")
                self.env_file_provider.uninstall()

                self.logger.cyan("\n[Frontend Cleanup]")
                self.frontend_provider.uninstall()

            self.logger.cyan("\n[CloudFormation Stack Cleanup]")
            self.aws_cloudformation_resource_manager.uninstall(env=env)

            self.logger.cyan("\n[Project Config Cleanup]")
            self.project_config_provider.uninstall()

        except Exception:
            traceback.print_exc()
            self.logger.red(f"Uninstall failed.")
            sys.exit(1)
