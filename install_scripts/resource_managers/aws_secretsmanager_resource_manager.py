import json
from typing import Optional

from install_scripts.aws_providers import AWSClientProvider, AwsCognitoProvider
from install_scripts.project_config import ProjectConfigProvider
from install_scripts.resource_managers.base_resource_manager import BaseResourceManager
from install_scripts.resource_managers.resource_manager_types import DevSecretValue
from install_scripts.utils import Logger

class AwsSecretsmanagerResourceManager(BaseResourceManager):
    secret_value: Optional[dict[str, str]]

    def __init__(
            self, *,
            logger: Logger,
            settings: ProjectConfigProvider,
            aws_client_provider: AWSClientProvider,
            aws_cognito_provider: AwsCognitoProvider,
        ):
        self.logger = logger
        self.settings = settings
        self.client = aws_client_provider.secrets_manager_client
        self.cognito_provider = aws_cognito_provider
        self.secret_value = None

    def on_end(self) -> None:
        """Run when the script ends."""
        self.__write_secret()

    def dev(self) -> None:
        """Run the provider in development mode."""
        self.__set_dev_secret_value()

    def __set_dev_secret_value(self) -> None:
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

    def __write_secret(self) -> None:
        """Write the secret value to the secret manager."""
        self.client.put_secret_value(
            SecretId=self.settings.secret_name,
            SecretString=json.dumps(self.secret_value)
        )
