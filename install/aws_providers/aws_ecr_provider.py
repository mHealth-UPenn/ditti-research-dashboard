import traceback

from botocore.exceptions import ClientError

from install.aws_providers.aws_account_provider import AwsAccountProvider
from install.aws_providers.aws_client_provider import AwsClientProvider
from install.project_config import ProjectConfigProvider
from install.utils import Colorizer, Logger
from install.utils.exceptions import AwsProviderError


class AwsEcrProvider:
    """
    Provider for AWS Elastic Container Registry operations.

    Manages ECR repository interactions for Docker images used
    in the application.
    """

    __repo_fstring: str = "{account_id}.dkr.ecr.{region}.amazonaws.com"

    def __init__(
        self,
        *,
        logger: Logger,
        config: ProjectConfigProvider,
        aws_client_provider: AwsClientProvider,
        aws_account_provider: AwsAccountProvider,
    ):
        self.logger = logger
        self.config = config
        self.ecr_client = aws_client_provider.ecr_client
        self.aws_account_provider = aws_account_provider

    def get_password(self) -> str:
        """Get the password for the ECR repository."""
        try:
            # NOTE: This is a workaround to login to ECR.
            # See: https://github.com/docker/docker-py/issues/2256
            res = self.ecr_client.get_authorization_token()
            if len(res["authorizationData"]) == 0:
                raise AwsProviderError("No authorization data found")
            return res["authorizationData"][0]["authorizationToken"]
        except AwsProviderError:
            raise
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(
                "Error getting password for ECR repository due to ClientError: "
                f"{Colorizer.white(e)}"
            )
            raise AwsProviderError(e) from e
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                "Error getting password for ECR repository due to unexpected "
                f"error: {Colorizer.white(e)}"
            )
            raise AwsProviderError(e) from e

    def get_repo_uri(self) -> str:
        """Get the URL for the ECR repository."""
        return self.__repo_fstring.format(
            account_id=self.aws_account_provider.aws_account_id,
            region=self.aws_account_provider.aws_region,
        )
