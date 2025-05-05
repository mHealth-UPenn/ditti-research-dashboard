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
from install.resource_managers.base_resource_manager import BaseResourceManager
from install.utils import Colorizer, Logger
from install.utils.exceptions import ResourceManagerError


class AwsCognitoResourceManager(BaseResourceManager):
    """
    Resource manager for AWS Cognito operations.

    Manages user pools, clients, and other Cognito resources
    for user authentication.
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
        self.client = aws_client_provider.cognito_client

    def on_end(self) -> None:
        """Run when the script ends."""
        try:
            self.create_admin_user()
        except ResourceManagerError:
            raise
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"Admin user creation failed due to unexpected error: "
                f"{Colorizer.white(e)}"
            )
            raise ResourceManagerError(e) from e

    def create_admin_user(self) -> dict:
        """Create an admin user in the Cognito user pool."""
        try:
            res = self.client.admin_create_user(
                UserPoolId=self.config.researcher_user_pool_id,
                Username=self.config.admin_email,
            )
            self.logger(
                f"Admin user {Colorizer.blue(self.config.admin_email)} "
                "created in Cognito user pool "
                f"{Colorizer.blue(self.config.researcher_user_pool_id)}"
            )

            return res
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(
                f"Admin user creation failed due to ClientError: "
                f"{Colorizer.white(e)}"
            )
            raise ResourceManagerError(e) from e
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"Admin user creation failed due to unexpected error: "
                f"{Colorizer.white(e)}"
            )
            raise ResourceManagerError(e) from e
