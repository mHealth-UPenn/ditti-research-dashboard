# Ditti Research Dashboard
# Copyright (C) 2025 the Trustees of the University of Pennsylvania
#
# Ditti Research Dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Ditti Research Dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import traceback

from botocore.exceptions import ClientError

from install.aws_providers.aws_client_provider import AwsClientProvider
from install.project_config import ProjectConfigProvider
from install.utils import Colorizer, Logger
from install.utils.exceptions import AwsProviderError


class AwsCloudformationProvider:
    def __init__(self, *,
            logger: Logger,
            config: ProjectConfigProvider,
            aws_client_provider: AwsClientProvider,
        ):
        self.logger = logger
        self.config = config
        self.client = aws_client_provider.cloudformation_client

    def get_outputs(self) -> dict[str, str]:
        try:
            res = self.client.describe_stacks(StackName=self.config.stack_name)
            if len(res["Stacks"]) == 0:
                raise AwsProviderError(f"Stack {self.config.stack_name} not found")
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
        self.config.participant_user_pool_id = outputs["ParticipantUserPoolId"]
        self.config.participant_client_id = outputs["ParticipantClientId"]
        self.config.researcher_user_pool_id = outputs["ResearcherUserPoolId"]
        self.config.researcher_client_id = outputs["ResearcherClientId"]
