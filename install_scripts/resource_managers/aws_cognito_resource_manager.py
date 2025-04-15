import traceback

from botocore.exceptions import ClientError

from install_scripts.aws_providers.aws_client_provider import AwsClientProvider
from install_scripts.project_config import ProjectConfigProvider
from install_scripts.resource_managers.base_resource_manager import BaseResourceManager
from install_scripts.utils import Logger
from install_scripts.utils.exceptions import ResourceManagerError


class AwsCognitoResourceManager(BaseResourceManager):
    def __init__(self, *,
            logger: Logger,
            settings: ProjectConfigProvider,
            aws_client_provider: AwsClientProvider,
        ):
        self.logger = logger
        self.settings = settings
        self.client = aws_client_provider.cognito_client

    def on_end(self) -> None:
        """Run when the script ends."""
        try:
            self.create_admin_user()
        except ResourceManagerError:
            raise
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Admin user creation failed due to unexpected error: {e}")
            raise ResourceManagerError(e)

    def create_admin_user(self) -> dict:
        """Create an admin user in the Cognito user pool."""
        try:
            res = self.client.admin_create_user(
                UserPoolId=self.settings.researcher_user_pool_id,
                Username=self.settings.admin_email,
            )
            self.logger.blue(f"Admin user {self.settings.admin_email} created in Cognito user pool {self.settings.researcher_user_pool_id}")

            return res
        except ClientError as e:
            traceback.print_exc()
            self.logger.red(f"Admin user creation failed due to ClientError: {e}")
            raise ResourceManagerError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Admin user creation failed due to unexpected error: {e}")
            raise ResourceManagerError(e)
