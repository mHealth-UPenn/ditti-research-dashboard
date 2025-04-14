import subprocess

from install_scripts.aws_providers.aws_client_provider import AWSClientProvider
from install_scripts.utils import Logger


class AwsAccountProvider:
    def __init__(
            self, *,
            logger: Logger,
            aws_client_provider: AWSClientProvider
        ):
        self.logger = logger
        self.client = aws_client_provider.sts_client

    @property
    def aws_region(self) -> str:
        return self.client.meta.region_name

    @property
    def aws_access_key_id(self) -> str:
        return subprocess.check_output(
            ["aws", "configure", "get", "aws_access_key_id"]
        ).decode("utf-8").strip()

    @property
    def aws_secret_access_key(self) -> str:
        return subprocess.check_output(
            ["aws", "configure", "get", "aws_secret_access_key"]
        ).decode("utf-8").strip()
    
    @property
    def aws_account_id(self) -> str:
        return self.client.get_caller_identity()["Account"]
    
    def configure_aws_cli(self) -> None:
        """Configure the AWS CLI."""
        subprocess.run(["aws", "configure"])
