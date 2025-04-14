import subprocess

from install_scripts.aws_providers.aws_client_provider import AWSClientProvider
from install_scripts.utils import Logger


class AwsAccountProvider:
    # Unit test: self.client is initialized with expected arguments
    def __init__(
            self, *,
            logger: Logger,
            aws_client_provider: AWSClientProvider
        ):
        self.logger = logger
        self.client = aws_client_provider.sts_client

    # Unit test: self.client.meta.region_name returns mocked value
    @property
    def aws_region(self) -> str:
        return self.client.meta.region_name

    # Unit test: subprocess.check_output is called with expected arguments
    # Unit test: subprocess.check_output returns mocked value
    @property
    def aws_access_key_id(self) -> str:
        return subprocess.check_output(
            ["aws", "configure", "get", "aws_access_key_id"]
        ).decode("utf-8").strip()

    # Unit test: subprocess.check_output is called with expected arguments
    # Unit test: subprocess.check_output returns mocked value
    @property
    def aws_secret_access_key(self) -> str:
        return subprocess.check_output(
            ["aws", "configure", "get", "aws_secret_access_key"]
        ).decode("utf-8").strip()

    # Unit test: self.client.get_caller_identity() returns mocked value
    @property
    def aws_account_id(self) -> str:
        return self.client.get_caller_identity()["Account"]

    # Unit test: subprocess.run is called with expected arguments
    def configure_aws_cli(self) -> None:
        """Configure the AWS CLI."""
        subprocess.run(["aws", "configure"])
