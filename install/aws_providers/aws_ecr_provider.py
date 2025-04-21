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
from install.aws_providers.aws_account_provider import AwsAccountProvider
from install.project_config import ProjectConfigProvider
from install.utils import Colorizer, Logger
from install.utils.exceptions import AwsProviderError

class AwsEcrProvider:
    __repo_fstring: str = "{account_id}.dkr.ecr.{region}.amazonaws.com"

    def __init__(
            self, *,
            logger: Logger,
            config: ProjectConfigProvider,
            aws_client_provider: AwsClientProvider,
            aws_account_provider: AwsAccountProvider
        ):
        self.logger = logger
        self.config = config
        self.ecr_client = aws_client_provider.ecr_client
        self.aws_account_provider = aws_account_provider

    def get_password(self) -> str:
        """Get the password for the ECR repository."""
        try:
            # NOTE: This is a workaround to login to ECR. See: https://github.com/docker/docker-py/issues/2256
            res = self.ecr_client.get_authorization_token()
            if len(res["authorizationData"]) == 0:
                raise AwsProviderError("No authorization data found")
            return res["authorizationData"][0]["authorizationToken"]
        except AwsProviderError:
            raise
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(f"Error getting password for ECR repository due to ClientError: {Colorizer.white(e)}")
            raise AwsProviderError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Error getting password for ECR repository due to unexpected error: {Colorizer.white(e)}")
            raise AwsProviderError(e)

    def get_repo_uri(self) -> str:
        """Get the URL for the ECR repository."""
        return self.__repo_fstring.format(
            account_id=self.aws_account_provider.aws_account_id,
            region=self.aws_account_provider.aws_region
        )
