from install_scripts.utils import Logger, BaseResourceManager
from install_scripts.project_settings_provider import ProjectSettingsProvider
from install_scripts.aws_providers.aws_client_provider import AWSClientProvider


class AwsCognitoResourceManager(BaseResourceManager):
    def __init__(self, *,
            logger: Logger,
            settings: ProjectSettingsProvider,
            aws_client_provider: AWSClientProvider,
        ):
        self.logger = logger
        self.settings = settings
        self.client = aws_client_provider.cognito_client

    def on_start(self) -> None:
        """Run when the script starts."""
        self.logger.cyan("\n[AWS Cognito Setup]")

    def on_end(self) -> None:
        """Run when the script ends."""
        self.create_admin_user()

    def dev(self) -> None:
        """Run the provider in development mode."""
        pass

    def staging(self) -> None:
        """Run the provider in staging mode."""
        pass

    def prod(self) -> None:
        """Run the provider in production mode."""
        pass

    def create_admin_user(self) -> None:
        """Create an admin user in the Cognito user pool."""
        self.client.admin_create_user(
            UserPoolId=self.settings.participant_user_pool_id,
            Username=self.settings.admin_email,
        )
