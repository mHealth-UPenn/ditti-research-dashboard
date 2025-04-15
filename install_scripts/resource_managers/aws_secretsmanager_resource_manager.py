import json
import traceback
from typing import Optional

from botocore.exceptions import ClientError

from install_scripts.aws_providers import AwsClientProvider, AwsCognitoProvider
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
            aws_client_provider: AwsClientProvider,
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
            self.write_secret()
        except ResourceManagerError:
            raise
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Secret write failed due to unexpected error: {e}")
            raise ResourceManagerError(e)

    def dev(self) -> None:
        """Run the provider in development mode."""
        try:
            self.set_dev_secret_value()
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Secret value setting failed due to unexpected error: {e}")
            raise ResourceManagerError(e)

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
        try:
            res = self.client.put_secret_value(
                SecretId=self.settings.secret_name,
                SecretString=json.dumps(self.secret_value)
            )
            self.logger.blue(f"Secret {self.settings.secret_name} written")

            return res
        except ClientError as e:
            traceback.print_exc()
            self.logger.red(f"Secret write failed due to ClientError: {e}")
            raise ResourceManagerError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Secret write failed due to unexpected error: {e}")
            raise ResourceManagerError(e)
