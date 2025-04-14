import traceback
import sys

from boto3.exceptions import ClientError

from install_scripts.utils import Logger
from install_scripts.project_settings_provider import ProjectSettingsProvider
from install_scripts.aws_providers import AWSClientProvider


class AwsCloudformationProvider:
    def __init__(self, *,
            logger: Logger,
            settings: ProjectSettingsProvider,
            aws_client_provider: AWSClientProvider,
        ):
        self.logger = logger
        self.settings = settings
        self.client = aws_client_provider.cloudformation_client

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
