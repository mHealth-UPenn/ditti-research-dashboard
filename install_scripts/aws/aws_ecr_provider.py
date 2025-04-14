import traceback
import sys

from install_scripts.utils import Logger
from install_scripts.project_settings_provider import ProjectSettingsProvider
from install_scripts.aws import (
    AWSClientProvider,
    AwsAccountProvider
)

class AwsEcrProvider:
    __repo_fstring: str = "{account_id}.dkr.ecr.{region}.amazonaws.com"

    def __init__(
            self, *,
            logger: Logger,
            settings: ProjectSettingsProvider,
            aws_client_provider: AWSClientProvider,
            aws_account_provider: AwsAccountProvider
        ):
        self.logger = logger
        self.settings = settings
        self.ecr_client = aws_client_provider.ecr_client
        self.aws_account_provider = aws_account_provider

    def get_password(self) -> str:
        """Get the password for the ECR repository."""
        try:
            # NOTE: This is a workaround to login to ECR. See: https://github.com/docker/docker-py/issues/2256
            return self.ecr_client.get_authorization_token() \
                ["authorizationData"][0]["authorizationToken"]
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Error getting password for ECR repository: {e}")
            sys.exit(1)

    def get_repo_uri(self) -> str:
        """Get the URL for the ECR repository."""
        return self.__repo_fstring.format(
            account_id=self.aws_account_provider.aws_account_id,
            region=self.aws_account_provider.aws_region
        )
