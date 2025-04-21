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

import subprocess
import traceback

from botocore.exceptions import ClientError

from install.aws_providers.aws_client_provider import AwsClientProvider
from install.utils import Colorizer, Logger
from install.utils.exceptions import AwsProviderError, SubprocessError


class AwsAccountProvider:
    def __init__(self, *, logger: Logger, aws_client_provider: AwsClientProvider):
        self.logger = logger
        self.client = aws_client_provider.sts_client

    @property
    def aws_region(self) -> str:
        return self.client.meta.region_name

    @property
    def aws_access_key_id(self) -> str:
        try:
            return self.get_aws_access_key_id()
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger.error(
                f"AWS access key ID retrieval failed due to subprocess error: {Colorizer.white(e)}"
            )
            raise SubprocessError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"AWS access key ID retrieval failed due to unexpected error: {Colorizer.white(e)}"
            )
            raise SubprocessError(e)

    @property
    def aws_secret_access_key(self) -> str:
        try:
            return self.get_aws_secret_access_key()
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger.error(
                f"AWS secret access key retrieval failed due to subprocess error: {Colorizer.white(e)}"
            )
            raise SubprocessError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"AWS secret access key retrieval failed due to unexpected error: {Colorizer.white(e)}"
            )
            raise SubprocessError(e)

    @property
    def aws_account_id(self) -> str:
        try:
            return self.client.get_caller_identity()["Account"]
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(
                f"AWS account ID retrieval failed due to ClientError: {Colorizer.white(e)}"
            )
            raise AwsProviderError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"AWS account ID retrieval failed due to unexpected error: {Colorizer.white(e)}"
            )
            raise AwsProviderError(e)

    @staticmethod
    def get_aws_access_key_id() -> str:
        return (
            subprocess.check_output(
                ["aws", "configure", "get", "aws_access_key_id"]
            )
            .decode("utf-8")
            .strip()
        )

    @staticmethod
    def get_aws_secret_access_key() -> str:
        return (
            subprocess.check_output(
                ["aws", "configure", "get", "aws_secret_access_key"]
            )
            .decode("utf-8")
            .strip()
        )

    def configure_aws_cli(self) -> None:
        """Configure the AWS CLI."""
        try:
            subprocess.run(["aws", "configure"])
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger.error("AWS CLI configuration failed")
            raise SubprocessError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"AWS CLI configuration failed due to unexpected error: {Colorizer.white(e)}"
            )
            raise SubprocessError(e)
