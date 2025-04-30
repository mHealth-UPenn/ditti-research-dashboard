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

        Retrieves the client secret for the Cognito participant user pool app client.

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

        Retrieves the client secret for the Cognito researcher user pool app client.

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
