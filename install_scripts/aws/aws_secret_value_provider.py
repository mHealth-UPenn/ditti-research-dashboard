import json
from typing import Optional

from install_scripts.utils import Logger, SecretValue, BaseProvider
from install_scripts.project_settings_provider import ProjectSettingsProvider
from install_scripts.aws.aws_resources_provider import AwsResourcesProvider
from install_scripts.aws.aws_client_provider import AWSClientProvider


class AwsSecretValueProvider(BaseProvider):
    secret_value: Optional[SecretValue]

    def __init__(
            self, *,
            logger: Logger,
            settings: ProjectSettingsProvider,
            aws_resources_handler: AwsResourcesProvider,
            aws_client_provider: AWSClientProvider,
        ):
        self.logger = logger
        self.settings = settings
        self.aws_resources_handler = aws_resources_handler
        self.secrets_client = aws_client_provider.secrets_manager_client
        self.secret_value = None

    def on_start(self) -> None:
        """Run when the script starts."""
        self.logger.cyan("\n[AWS Secret Value Setup]")

    def on_end(self) -> None:
        """Run when the script ends."""
        self.write_secret()

    def dev(self) -> None:
        """Run the provider in development mode."""
        self.set_dev_secret_value()

    def staging(self) -> None:
        """Run the provider in staging mode."""
        pass

    def prod(self) -> None:
        """Run the provider in production mode."""
        pass

    def set_dev_secret_value(self) -> None:
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
