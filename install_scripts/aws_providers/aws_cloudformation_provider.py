import traceback

from botocore.exceptions import ClientError

from install_scripts.aws_providers.aws_client_provider import AwsClientProvider
from install_scripts.project_config import ProjectConfigProvider
from install_scripts.utils import Logger
from install_scripts.utils.exceptions import AwsProviderError

class AwsCloudformationProvider:
    def __init__(self, *,
            logger: Logger,
            settings: ProjectConfigProvider,
            aws_client_provider: AwsClientProvider,
        ):
        self.logger = logger
        self.settings = settings
        self.client = aws_client_provider.cloudformation_client

    def get_outputs(self) -> dict[str, str]:
        try:
            res = self.client.describe_stacks(StackName=self.settings.stack_name)  # Mocked by moto
            if len(res["Stacks"]) == 0:
                raise AwsProviderError(f"Stack {self.settings.stack_name} not found")
            return res["Stacks"][0]["Outputs"]
        except AwsProviderError:
            raise
        except ClientError as e:
            traceback.print_exc()
            self.logger.red(f"Error getting outputs for stack due to ClientError: {e}")
            raise AwsProviderError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"Error getting outputs for stack due to unexpected error: {e}")
            raise AwsProviderError(e)
