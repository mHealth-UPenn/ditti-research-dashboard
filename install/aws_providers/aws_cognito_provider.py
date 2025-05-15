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


class AwsCognitoProvider:
    """
    Provider for AWS Cognito operations.

    Manages Cognito user pools and app clients for authentication
    in the application.
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
        self.cognito_client = aws_client_provider.cognito_client

    def get_participant_client_secret(self) -> str:
        """
        Get the client secret for the participant app client.

        Retrieves the client secret for the Cognito participant user pool
        app client.

        Returns
        -------
        str
            The participant client secret.

        Raises
        ------
        AwsProviderError
            If there is an error retrieving the client secret.
        """
        try:
            return self.cognito_client.describe_user_pool_client(
                UserPoolId=self.config.participant_user_pool_id,
                ClientId=self.config.participant_client_id,
            )["UserPoolClient"]["ClientSecret"]
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(
                "Error getting participant client secret due to ClientError: "
                f"{Colorizer.white(e)}"
            )
            raise AwsProviderError(e) from e
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                "Error getting participant client secret due to unexpected "
                f"error: {Colorizer.white(e)}"
            )
            raise AwsProviderError(e) from e

    def get_researcher_client_secret(self) -> str:
        """
        Get the client secret for the researcher app client.

        Retrieves the client secret for the Cognito researcher user pool
        app client.

        Returns
        -------
        str
            The researcher client secret.

        Raises
        ------
        AwsProviderError
            If there is an error retrieving the client secret.
        """
        try:
            return self.cognito_client.describe_user_pool_client(
                UserPoolId=self.config.researcher_user_pool_id,
                ClientId=self.config.researcher_client_id,
            )["UserPoolClient"]["ClientSecret"]
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(
                "Error getting researcher client secret due to ClientError: "
                f"{Colorizer.white(e)}"
            )
            raise AwsProviderError(e) from e
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                "Error getting researcher client secret due to unexpected "
                f"error: {Colorizer.white(e)}"
            )
            raise AwsProviderError(e) from e
