import json
from typing import Optional

from install_scripts.utils import Logger
from install_scripts.project_settings_provider import ProjectSettingsProvider
from install_scripts.aws_providers.aws_client_provider import AWSClientProvider
from install_scripts.aws_providers.aws_cognito_provider import AwsCognitoProvider
from install_scripts.resource_managers.base_resource_manager import BaseResourceManager
from install_scripts.resource_managers.resource_manager_types import DevSecretValue

class AwsSecretsmanagerResourceManager(BaseResourceManager):
    secret_value: Optional[dict[str, str]]

    def __init__(
            self, *,
            logger: Logger,
            settings: ProjectSettingsProvider,
            aws_client_provider: AWSClientProvider,
            aws_cognito_provider: AwsCognitoProvider,
        ):
        self.logger = logger
        self.settings = settings
        self.client = aws_client_provider.secrets_manager_client
        self.cognito_provider = aws_cognito_provider
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
        secret_value: DevSecretValue = {
            "FITBIT_CLIENT_ID": self.settings.fitbit_client_id,
            "FITBIT_CLIENT_SECRET": self.settings.fitbit_client_secret,
            "COGNITO_PARTICIPANT_CLIENT_SECRET": self.cognito_provider \
                .get_participant_client_secret(),
            "COGNITO_RESEARCHER_CLIENT_SECRET": self.cognito_provider \
                .get_researcher_client_secret()
        }
        self.secret_value = secret_value

    def write_secret(self) -> None:
        """Write the secret value to the secret manager."""
        self.client.put_secret_value(
            SecretId=self.settings.secret_name,
            SecretString=json.dumps(self.secret_value)
        )
