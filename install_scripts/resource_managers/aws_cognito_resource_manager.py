from install_scripts.aws_providers.aws_client_provider import AWSClientProvider
from install_scripts.project_config import ProjectConfigProvider
from install_scripts.resource_managers.base_resource_manager import BaseResourceManager
from install_scripts.utils import Logger


class AwsCognitoResourceManager(BaseResourceManager):
    def __init__(self, *,
            logger: Logger,
            settings: ProjectConfigProvider,
            aws_client_provider: AWSClientProvider,
        ):
        self.logger = logger
        self.settings = settings
        self.client = aws_client_provider.cognito_client

    def on_end(self) -> None:
        """Run when the script ends."""
        self.__create_admin_user()

    def __create_admin_user(self) -> None:
        """Create an admin user in the Cognito user pool."""
        self.client.admin_create_user(
            UserPoolId=self.settings.researcher_user_pool_id,
            Username=self.settings.admin_email,
        )
