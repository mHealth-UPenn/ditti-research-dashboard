import json
import traceback

from botocore.exceptions import ClientError

from install.aws_providers import AwsClientProvider, AwsCognitoProvider
from install.project_config import ProjectConfigProvider
from install.resource_managers.base_resource_manager import BaseResourceManager
from install.resource_managers.resource_manager_types import DevSecretValue
from install.utils import Colorizer, Logger
from install.utils.exceptions import ResourceManagerError


class AwsSecretsManagerResourceManager(BaseResourceManager):
    """
    Resource manager for AWS Secrets Manager operations.

    Manages creation, updating, and deletion of secrets used by the application.
    """

    secret_value: dict[str, str] | None

    def __init__(
        self,
        *,
        logger: Logger,
        config: ProjectConfigProvider,
        aws_client_provider: AwsClientProvider,
        aws_cognito_provider: AwsCognitoProvider,
    ):
        self.logger = logger
        self.config = config
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
            self.logger.error(
                f"Secret write failed due to unexpected error: "
                f"{Colorizer.white(e)}"
            )
            raise ResourceManagerError(e) from e

    def dev(self) -> None:
        """Run the provider in development mode."""
        try:
            self.set_dev_secret_value()
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"Secret value setting failed due to unexpected error: "
                f"{Colorizer.white(e)}"
            )
            raise ResourceManagerError(e) from e

    def set_dev_secret_value(self) -> None:
        """Set the secret value."""
        secret_value: DevSecretValue = {
            "FITBIT_CLIENT_ID": self.config.fitbit_client_id,
            "FITBIT_CLIENT_SECRET": self.config.fitbit_client_secret,
            "COGNITO_PARTICIPANT_CLIENT_SECRET": (
                self.cognito_provider.get_participant_client_secret()
            ),
            "COGNITO_RESEARCHER_CLIENT_SECRET": (
                self.cognito_provider.get_researcher_client_secret()
            ),
        }
        self.secret_value = secret_value

    def write_secret(self) -> None:
        """Write the secret value to the secret manager."""
        try:
            res = self.client.put_secret_value(
                SecretId=self.config.secret_name,
                SecretString=json.dumps(self.secret_value),
            )
            self.logger(
                f"Secret {Colorizer.blue(self.config.secret_name)} written"
            )

            return res
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(
                f"Secret write failed due to ClientError: {Colorizer.white(e)}"
            )
            raise ResourceManagerError(e) from e
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"Secret write failed due to unexpected error: "
                f"{Colorizer.white(e)}"
            )
            raise ResourceManagerError(e) from e
