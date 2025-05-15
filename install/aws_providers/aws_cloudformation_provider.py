# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may]
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import traceback

from botocore.exceptions import ClientError

from install.aws_providers.aws_client_provider import AwsClientProvider
from install.project_config import ProjectConfigProvider
from install.utils import Colorizer, Logger
from install.utils.exceptions import AwsProviderError


class AwsCloudformationProvider:
    """
    Provider for AWS CloudFormation operations.

    Manages CloudFormation stack interactions and retrieval of stack outputs
    for configuration.
    """

    def __init__(
        self,
        *,
        logger: Logger,
        config: ProjectConfigProvider,
        aws_client_provider: AwsClientProvider,
    ):
        self.logger = logger
        self.config = config
        self.client = aws_client_provider.cloudformation_client

    def get_outputs(self) -> dict[str, str]:
        """
        Get outputs from the CloudFormation stack.

        Retrieves all output values from the deployed CloudFormation stack.

        Returns
        -------
        dict[str, str]
            Dictionary of stack output key-value pairs.

        Raises
        ------
        AwsProviderError
            If there is an error retrieving the stack outputs.
        """
        try:
            res = self.client.describe_stacks(StackName=self.config.stack_name)
            if len(res["Stacks"]) == 0:
                raise AwsProviderError(
                    f"Stack {self.config.stack_name} not found"
                )
            return {
                output["OutputKey"]: output["OutputValue"]
                for output in res["Stacks"][0]["Outputs"]
            }
        except AwsProviderError:
            raise
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(
                "Error getting outputs for stack due to ClientError: "
                f"{Colorizer.white(e)}"
            )
            raise AwsProviderError(e) from e
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                "Error getting outputs for stack due to unexpected error: "
                f"{Colorizer.white(e)}"
            )
            raise AwsProviderError(e) from e

    def update_dev_project_config(self) -> None:
        """
        Update the development project configuration with CloudFormation outputs.

        Retrieves outputs from the CloudFormation stack and updates the
        project configuration values accordingly.

        Returns
        -------
        None
        """
        outputs = self.get_outputs()
        self.config.participant_user_pool_id = outputs["ParticipantUserPoolId"]
        self.config.participant_client_id = outputs["ParticipantClientId"]
        self.config.researcher_user_pool_id = outputs["ResearcherUserPoolId"]
        self.config.researcher_client_id = outputs["ResearcherClientId"]
