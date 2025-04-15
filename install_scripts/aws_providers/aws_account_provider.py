import subprocess
import traceback

from botocore.exceptions import ClientError

from install_scripts.aws_providers.aws_client_provider import AwsClientProvider
from install_scripts.utils import Logger
from install_scripts.utils.exceptions import AwsProviderError, SubprocessError


class AwsAccountProvider:
    def __init__(
            self, *,
            logger: Logger,
            aws_client_provider: AwsClientProvider
        ):
        self.logger = logger
        self.client = aws_client_provider.sts_client

    @property
    def aws_region(self) -> str:
        return self.client.meta.region_name


    @property
    def aws_access_key_id(self) -> str:
        try:
            return subprocess.check_output(
                ["aws", "configure", "get", "aws_access_key_id"]
            ).decode("utf-8").strip()
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger.red(f"AWS access key ID retrieval failed due to subprocess error: {e}")
            raise SubprocessError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"AWS access key ID retrieval failed due to unexpected error: {e}")
            raise SubprocessError(e)

    @property
    def aws_secret_access_key(self) -> str:
        try:
            return subprocess.check_output(
                ["aws", "configure", "get", "aws_secret_access_key"]
            ).decode("utf-8").strip()
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger.red(f"AWS secret access key retrieval failed due to subprocess error: {e}")
            raise SubprocessError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"AWS secret access key retrieval failed due to unexpected error: {e}")
            raise SubprocessError(e)

    @property
    def aws_account_id(self) -> str:
        try:
            return self.client.get_caller_identity()["Account"]
        except ClientError as e:
            traceback.print_exc()
            self.logger.red(f"AWS account ID retrieval failed due to ClientError: {e}")
            raise AwsProviderError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"AWS account ID retrieval failed due to unexpected error: {e}")
            raise AwsProviderError(e)

    def configure_aws_cli(self) -> None:
        """Configure the AWS CLI."""
        try:
            subprocess.run(["aws", "configure"])
        except subprocess.CalledProcessError as e:
            traceback.print_exc()
            self.logger.red("AWS CLI configuration failed")
            raise SubprocessError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.red(f"AWS CLI configuration failed due to unexpected error: {e}")
            raise SubprocessError(e)
