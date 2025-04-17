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
    DatabaseProvider,
    DockerProvider,
    EnvFileProvider,
    FrontendProvider,
)
from install_scripts.resource_managers import (
    AwsCloudformationResourceManager,
    AwsCognitoResourceManager,
    AwsS3ResourceManager,
    AwsSecretsmanagerResourceManager,
)
from install_scripts.utils import Colorizer, Logger, get_project_suffix
from install_scripts.utils.types import Env
from install_scripts.utils.exceptions import (
    CancelInstallation,
    ProjectConfigError,
)


class Installer:
    def __init__(self, env: Env) -> None:
        self.logger = Logger()
        self.env = env

        # Initialize project config provider
        self.project_config_provider = ProjectConfigProvider(
            logger=self.logger,
            project_suffix=get_project_suffix(env),
        )

        # Initialize AWS providers
        self.aws_client_provider = AwsClientProvider()
        self.aws_account_provider = AwsAccountProvider(
            logger=self.logger,
            aws_client_provider=self.aws_client_provider,
        )
        self.aws_s3_resource_manager = AwsS3ResourceManager(
            logger=self.logger,
            settings=self.project_config_provider,
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
        self.database_provider = DatabaseProvider(
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
            # Get project settings
            self.logger(Colorizer.cyan("\n[Project Setup]"))
            self.project_config_provider.get_user_input()
            self.project_config_provider.setup_project_config()
            self.project_config_provider.write_project_config()

            # Configure AWS CLI
            self.logger(Colorizer.cyan("\n[AWS CLI Configuration]"))
            self.aws_account_provider.configure_aws_cli()

            # Setup Docker containers
            self.logger(Colorizer.cyan("\n[Docker Setup]"))
            self.docker_provider.create_network()
            self.docker_provider.run_postgres_container()
            self.docker_provider.build_wearable_data_retrieval_container()
            self.docker_provider.run_wearable_data_retrieval_container()

            # Setup CloudFormation stack
            self.logger(Colorizer.cyan("\n[CloudFormation Stack Setup]"))
            self.aws_cloudformation_resource_manager.run(env="dev")
            self.aws_cloudformation_provider.update_dev_project_config()

            # Setup Secrets Manager
            self.logger(Colorizer.cyan("\n[Secrets Manager Setup]"))
            self.aws_secretsmanager_resource_manager.run(env="dev")

            # Setup Cognito
            self.logger(Colorizer.cyan("\n[Cognito Setup]"))
            self.aws_cognito_resource_manager.run(env="dev")

            # Setup .env files
            self.logger(Colorizer.cyan("\n[Environment Files Setup]"))
            wearable_data_retrieval_env = self.env_file_provider.get_wearable_data_retrieval_env()
            root_env = self.env_file_provider.get_root_env()
            self.env_file_provider.write_env_files(wearable_data_retrieval_env, root_env)

            # Setup database
            self.logger(Colorizer.cyan("\n[Database Setup]"))
            self.database_provider.upgrade_database()
            self.database_provider.initialize_database()
            self.database_provider.create_researcher_account()

            # Setup frontend
            self.logger(Colorizer.cyan("\n[Frontend Setup]"))
            self.frontend_provider.initialize_frontend()

        except CancelInstallation:
            sys.exit(0)
        except Exception:
            traceback.print_exc()
            self.logger(Colorizer.red("Installation failed."))
            sys.exit(1)

    def uninstall(self) -> None:
        """Uninstall the resources."""
        try:
            self.logger("This will delete all resources created by the installer.")
            self.logger(Colorizer.red("ANY LOST DATA WILL BE PERMANENTLY DELETED."))
            self.logger("Please confirm by typing \"uninstall\".")
            confirm = input("> ")

            if confirm != "uninstall":
                self.logger(Colorizer.cyan("Uninstall cancelled."))
                sys.exit(0)

            # Load project config
            try:
                self.project_config_provider.load_existing_config()
            except ProjectConfigError:
                self.logger(Colorizer.red("Uninstall failed."))
                sys.exit(1)

            # Configure AWS CLI
            self.logger(Colorizer.cyan("\n[AWS CLI Configuration]"))
            self.aws_account_provider.configure_aws_cli()

            self.logger(Colorizer.cyan("\n[S3 Buckets Cleanup]"))
            self.aws_s3_resource_manager.uninstall(env=self.env)

            self.logger(Colorizer.cyan("\n[CloudFormation Stack Cleanup]"))
            self.aws_cloudformation_resource_manager.uninstall(env=self.env)

            self.logger(Colorizer.cyan("\n[Project Config Cleanup]"))
            self.project_config_provider.uninstall()

            if self.env == "dev":
                self.logger(Colorizer.cyan("\n[Docker Cleanup]"))
                self.docker_provider.uninstall()

                self.logger(Colorizer.cyan("\n[.env Files Cleanup]"))
                self.env_file_provider.uninstall()

                self.logger(Colorizer.cyan("\n[Frontend Cleanup]"))
                self.frontend_provider.uninstall()

        except Exception:
            traceback.print_exc()
            self.logger.error(f"Uninstall failed.")
            sys.exit(1)
