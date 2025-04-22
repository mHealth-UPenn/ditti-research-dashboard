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
from install.resource_managers.base_resource_manager import BaseResourceManager
from install.utils import Colorizer, Logger
from install.utils.exceptions import ResourceManagerError


class AwsCognitoResourceManager(BaseResourceManager):
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
