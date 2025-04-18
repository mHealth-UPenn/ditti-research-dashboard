import traceback

from botocore.exceptions import ClientError

from install.aws_providers.aws_client_provider import AwsClientProvider
from install.project_config import ProjectConfigProvider
from install.resource_managers.base_resource_manager import BaseResourceManager
from install.utils import Logger, Colorizer
from install.utils.exceptions import ResourceManagerError


class AwsCognitoResourceManager(BaseResourceManager):
    def __init__(self, *,
            logger: Logger,
            config: ProjectConfigProvider,
            aws_client_provider: AwsClientProvider,
        ):
        self.logger = logger
        self.config = config
        self.client = aws_client_provider.cognito_client

    def on_end(self) -> None:
        """Run when the script ends."""
        try:
            self.create_admin_user()
        except ResourceManagerError:
            raise
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Admin user creation failed due to unexpected error: {Colorizer.white(e)}")
            raise ResourceManagerError(e)

    def create_admin_user(self) -> dict:
        """Create an admin user in the Cognito user pool."""
        try:
            res = self.client.admin_create_user(
                UserPoolId=self.config.researcher_user_pool_id,
                Username=self.config.admin_email,
            )
            self.logger(f"Admin user {Colorizer.blue(self.config.admin_email)} created in Cognito user pool {Colorizer.blue(self.config.researcher_user_pool_id)}")

            return res
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(f"Admin user creation failed due to ClientError: {Colorizer.white(e)}")
            raise ResourceManagerError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Admin user creation failed due to unexpected error: {Colorizer.white(e)}")
            raise ResourceManagerError(e)
