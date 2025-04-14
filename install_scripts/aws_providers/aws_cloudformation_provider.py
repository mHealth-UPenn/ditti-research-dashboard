import traceback
import sys

from boto3.exceptions import ClientError

from install_scripts.aws_providers.aws_client_provider import AWSClientProvider
from install_scripts.project_config import ProjectConfigProvider
from install_scripts.utils import Logger


class AwsCloudformationProvider:
    # Unit test: self.client is initialized with expected arguments
    def __init__(self, *,
            logger: Logger,
            settings: ProjectConfigProvider,
            aws_client_provider: AWSClientProvider,
        ):
        self.logger = logger
        self.settings = settings
        self.client = aws_client_provider.cloudformation_client

    # Unit test: self.client.describe_stacks is called with expected arguments
    # Unit test: self.client.describe_stacks returns mocked value
    # Unit test: RuntimeError is raised when stack is not found
    # Unit test: self.logger.red is called once on ClientError
    def get_outputs(self) -> dict[str, str]:
        try:
            res = self.client.describe_stacks(StackName=self.settings.stack_name)
            if len(res["Stacks"]) == 0:
                raise RuntimeError(f"Stack {self.settings.stack_name} not found")
            return res["Stacks"][0]["Outputs"]
        except ClientError:
            traceback.print_exc()
            self.logger.red("Error getting outputs for stack")
            sys.exit(1)
