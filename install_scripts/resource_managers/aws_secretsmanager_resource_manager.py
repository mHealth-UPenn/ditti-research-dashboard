import json
import traceback
from typing import Optional

from boto3.exceptions import ClientError

from install_scripts.aws_providers import AWSClientProvider, AwsCognitoProvider
from install_scripts.project_config import ProjectConfigProvider
from install_scripts.resource_managers.base_resource_manager import BaseResourceManager
from install_scripts.resource_managers.resource_manager_types import DevSecretValue
from install_scripts.utils import Logger
from install_scripts.utils.exceptions import ResourceManagerError


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
        try:
            self.__write_secret()
        except ResourceManagerError:
            raise
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Secret write failed due to unexpected error: {e}")
            raise ResourceManagerError(e)

    def dev(self) -> None:
        """Run the provider in development mode."""
        try:
            self.__set_dev_secret_value()
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Secret value setting failed due to unexpected error: {e}")
            raise ResourceManagerError(e)

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
        try:
            self.client.put_secret_value(
                SecretId=self.settings.secret_name,
                SecretString=json.dumps(self.secret_value)
            )
        except ClientError as e:
            traceback.print_exc()
            self.logger.red(f"Secret write failed due to ClientError: {e}")
            raise ResourceManagerError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Secret write failed due to unexpected error: {e}")
            raise ResourceManagerError(e)
