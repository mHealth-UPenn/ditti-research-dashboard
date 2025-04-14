import traceback
import sys

from boto3.exceptions import ClientError

from install_scripts.aws_providers.aws_client_provider import AWSClientProvider
from install_scripts.aws_providers.aws_account_provider import AwsAccountProvider
from install_scripts.project_config import ProjectConfigProvider
from install_scripts.utils import Logger

class AwsEcrProvider:
    __repo_fstring: str = "{account_id}.dkr.ecr.{region}.amazonaws.com"

    # Unit test: self.ecr_client is initialized with expected arguments
    def __init__(
            self, *,
            logger: Logger,
            settings: ProjectConfigProvider,
            aws_client_provider: AWSClientProvider,
            aws_account_provider: AwsAccountProvider
        ):
        self.logger = logger
        self.settings = settings
        self.ecr_client = aws_client_provider.ecr_client
        self.aws_account_provider = aws_account_provider

    # Unit test: self.ecr_client.get_authorization_token is called with expected arguments
    # Unit test: self.ecr_client.get_authorization_token returns mocked value
    # Unit test: RuntimeError is raised when no authorization data is found
    # Unit test: self.logger.red is called once on ClientError
    def get_password(self) -> str:
        """Get the password for the ECR repository."""
        try:
            # NOTE: This is a workaround to login to ECR. See: https://github.com/docker/docker-py/issues/2256
            res = self.ecr_client.get_authorization_token()
            if len(res["authorizationData"]) == 0:
                raise RuntimeError("No authorization data found")
            return res["authorizationData"][0]["authorizationToken"]
        except ClientError:
            traceback.print_exc()
            self.logger.red("Error getting password for ECR repository")
            sys.exit(1)

    # Unit test: self.__repo_fstring.format is called with expected arguments
    # Unit test: self.__repo_fstring.format returns mocked value
    def get_repo_uri(self) -> str:
        """Get the URL for the ECR repository."""
        return self.__repo_fstring.format(
            account_id=self.aws_account_provider.aws_account_id,
            region=self.aws_account_provider.aws_region
        )
