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

import sys
import traceback

from install.aws_providers import (
    AwsAccountProvider,
    AwsClientProvider,
    AwsCloudformationProvider,
    AwsCognitoProvider,
    AwsEcrProvider,
)
from install.local_providers import (
    DatabaseProvider,
    DockerProvider,
    EnvFileProvider,
    FrontendProvider,
)
from install.project_config import ProjectConfigProvider
from install.resource_managers import (
    AwsCloudformationResourceManager,
    AwsCognitoResourceManager,
    AwsS3ResourceManager,
    AwsSecretsmanagerResourceManager,
)
from install.utils import Colorizer, Logger
from install.utils.exceptions import (
    CancelInstallation,
    ProjectConfigError,
)
from install.utils.types import Env


class Installer:
    def __init__(self, env: Env) -> None:
        self.logger = Logger()
        self.env = env

        # Initialize project config provider
        self.project_config_provider = ProjectConfigProvider(logger=self.logger)

        # Initialize AWS providers
        self.aws_client_provider = AwsClientProvider()
        self.aws_account_provider = AwsAccountProvider(
            logger=self.logger,
            aws_client_provider=self.aws_client_provider,
        )
        self.aws_s3_resource_manager = AwsS3ResourceManager(
            logger=self.logger,
            config=self.project_config_provider,
            aws_client_provider=self.aws_client_provider,
        )
        self.aws_cloudformation_provider = AwsCloudformationProvider(
            logger=self.logger,
            config=self.project_config_provider,
            aws_client_provider=self.aws_client_provider,
        )
        self.aws_cognito_provider = AwsCognitoProvider(
            logger=self.logger,
            config=self.project_config_provider,
            aws_client_provider=self.aws_client_provider,
        )
        self.aws_ecr_provider = AwsEcrProvider(
            logger=self.logger,
            config=self.project_config_provider,
            aws_client_provider=self.aws_client_provider,
            aws_account_provider=self.aws_account_provider,
        )

        # Initialize local providers
        self.env_file_provider = EnvFileProvider(
            logger=self.logger,
            config=self.project_config_provider,
            aws_account_provider=self.aws_account_provider,
        )
        self.docker_provider = DockerProvider(
            logger=self.logger,
            config=self.project_config_provider,
            env_file_provider=self.env_file_provider,
        )
        self.database_provider = DatabaseProvider(
            logger=self.logger,
            config=self.project_config_provider,
        )
        self.frontend_provider = FrontendProvider(
            logger=self.logger,
            config=self.project_config_provider,
        )

        # Initialize resource managers
        self.aws_cloudformation_resource_manager = (
            AwsCloudformationResourceManager(
                logger=self.logger,
                config=self.project_config_provider,
                aws_client_provider=self.aws_client_provider,
            )
        )
        self.aws_cognito_resource_manager = AwsCognitoResourceManager(
            logger=self.logger,
            config=self.project_config_provider,
            aws_client_provider=self.aws_client_provider,
        )
        self.aws_secretsmanager_resource_manager = (
            AwsSecretsmanagerResourceManager(
                logger=self.logger,
                config=self.project_config_provider,
                aws_client_provider=self.aws_client_provider,
                aws_cognito_provider=self.aws_cognito_provider,
            )
        )

    def run(self) -> None:
        try:
            # Get project config
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
            self.env_file_provider.write_root_env()

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
            self.logger(
                "This will delete all resources created by the installer."
            )
            self.logger(
                Colorizer.red("ANY LOST DATA WILL BE PERMANENTLY DELETED.")
            )
            self.logger('Please confirm by typing "uninstall".')
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
            self.logger.error("Uninstall failed.")
            sys.exit(1)
