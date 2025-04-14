import subprocess
import sys
import traceback
from typing import Optional

from botocore.exceptions import ClientError

from install_scripts.utils import Logger, BaseProvider
from install_scripts.aws.aws_client_provider import AWSClientProvider


class AwsAccountProvider(BaseProvider):
    __aws_account_id: Optional[str]
    __aws_region: Optional[str]
    __aws_access_key_id: Optional[str]

    def __init__(
            self, *,
            logger: Logger,
            aws_client_provider: AWSClientProvider
        ):
        self.logger = logger
        self.sts_client = aws_client_provider.sts_client
        self.__aws_account_id = None
        self.__aws_region = None
        self.__aws_access_key_id = None
        self.__aws_secret_access_key = None

    def on_start(self) -> None:
        """Run when the script starts."""
        self.logger.cyan("\n[AWS CLI Setup]")
        self.configure_aws_cli()
        self.get_aws_account()

    def on_end(self) -> None:
        """Run when the script ends."""
        pass

    def dev(self) -> None:
        """Run the provider in development mode."""
        pass

    def staging(self) -> None:
        """Run the provider in staging mode."""
        pass

    def prod(self) -> None:
        """Run the provider in production mode."""
        pass

    @property
    def aws_region(self) -> str:
        if self.__aws_region is None:
            self.run()
        return self.__aws_region

    @property
    def aws_access_key_id(self) -> str:
        if self.__aws_access_key_id is None:
            self.run()
        return self.__aws_access_key_id

    @property
    def aws_secret_access_key(self) -> str:
        if self.__aws_secret_access_key is None:
            self.run()
        return self.__aws_secret_access_key
    
    @property
    def aws_account_id(self) -> str:
        if self.__aws_account_id is None:
            self.run()
        return self.__aws_account_id
    
    def configure_aws_cli(self) -> None:
        """Configure the AWS CLI."""
        subprocess.run(["aws", "configure"])

    def get_aws_account(self) -> None:
        try:
            self.__aws_access_key_id = subprocess.check_output(
                ["aws", "configure", "get", "aws_access_key_id"]
            ).decode("utf-8").strip()
            self.__aws_secret_access_key = subprocess.check_output(
                ["aws", "configure", "get", "aws_secret_access_key"]
            ).decode("utf-8").strip()
            self.__aws_region = subprocess.check_output(
                ["aws", "configure", "get", "region"]
            ).decode("utf-8").strip()
            self.__aws_account_id = self.sts_client \
                .get_caller_identity()["Account"]
        except (subprocess.CalledProcessError, ClientError):
            traceback.print_exc()
            self.logger.red("AWS configuration failed")
            sys.exit(1)
