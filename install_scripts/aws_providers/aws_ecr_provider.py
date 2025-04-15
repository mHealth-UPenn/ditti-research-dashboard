import traceback

from botocore.exceptions import ClientError

from install_scripts.aws_providers.aws_client_provider import AwsClientProvider
from install_scripts.aws_providers.aws_account_provider import AwsAccountProvider
from install_scripts.project_config import ProjectConfigProvider
from install_scripts.utils import Logger
from install_scripts.utils.exceptions import AwsProviderError

class AwsEcrProvider:
    __repo_fstring: str = "{account_id}.dkr.ecr.{region}.amazonaws.com"

    def __init__(
            self, *,
            logger: Logger,
            settings: ProjectConfigProvider,
            aws_client_provider: AwsClientProvider,
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
            res = self.ecr_client.get_authorization_token()
            if len(res["authorizationData"]) == 0:
                raise AwsProviderError("No authorization data found")
            return res["authorizationData"][0]["authorizationToken"]
        except AwsProviderError:
            raise
        except ClientError as e:
            traceback.print_exc()
            self.logger.red(f"Error getting password for ECR repository due to ClientError: {e}")
            raise AwsProviderError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Error getting password for ECR repository due to unexpected error: {e}")
            raise

    def get_repo_uri(self) -> str:
        """Get the URL for the ECR repository."""
        return self.__repo_fstring.format(
            account_id=self.aws_account_provider.aws_account_id,
            region=self.aws_account_provider.aws_region
        )
