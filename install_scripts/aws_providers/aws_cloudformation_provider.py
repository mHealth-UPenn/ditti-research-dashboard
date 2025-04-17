import traceback

from botocore.exceptions import ClientError

from install_scripts.aws_providers.aws_client_provider import AwsClientProvider
from install_scripts.project_config import ProjectConfigProvider
from install_scripts.utils import Colorizer, Logger
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
            res = self.client.describe_stacks(StackName=self.settings.stack_name)
            if len(res["Stacks"]) == 0:
                raise AwsProviderError(f"Stack {self.settings.stack_name} not found")
            return {
                output["OutputKey"]: output["OutputValue"]
                for output in res["Stacks"][0]["Outputs"]
            }
        except AwsProviderError:
            raise
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(f"Error getting outputs for stack due to ClientError: {Colorizer.white(e)}")
            raise AwsProviderError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Error getting outputs for stack due to unexpected error: {Colorizer.white(e)}")
            raise AwsProviderError(e)

    def update_dev_project_config(self) -> None:
        outputs = self.get_outputs()
        self.settings.participant_user_pool_id = outputs["ParticipantUserPoolId"]
        self.settings.participant_client_id = outputs["ParticipantClientId"]
        self.settings.researcher_user_pool_id = outputs["ResearcherUserPoolId"]
        self.settings.researcher_client_id = outputs["ResearcherClientId"]
