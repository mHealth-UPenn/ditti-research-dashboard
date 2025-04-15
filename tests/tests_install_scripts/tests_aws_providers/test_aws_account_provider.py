import pytest
from unittest.mock import patch, MagicMock

from botocore.exceptions import ClientError
from moto import mock_aws
import subprocess

from install_scripts.aws_providers import AwsAccountProvider, AwsClientProvider
from install_scripts.utils.exceptions import AwsProviderError, SubprocessError
from tests.tests_install_scripts.tests_utils.mock_logger import logger
from tests.tests_install_scripts.tests_aws_providers.mock_aws_account_provider import aws_account_provider


@pytest.fixture
def logger_mock():
    return logger()


@pytest.fixture
def aws_account_provider_mock():
    with mock_aws():
        yield aws_account_provider()


@pytest.fixture
def mock_check_output():
    with patch("subprocess.check_output") as mock_check_output:
        yield mock_check_output


@pytest.fixture
def mock_run():
    with patch("subprocess.run") as mock_run:
        yield mock_run


class TestAwsAccountProvider:
    def test_aws_region_success(self, aws_account_provider_mock: AwsAccountProvider):
        expected_region = AwsClientProvider().sts_client.meta.region_name

        result = aws_account_provider_mock.aws_region

        assert result == expected_region

    def test_aws_access_key_id_success(self, mock_check_output: MagicMock, aws_account_provider_mock: AwsAccountProvider):
        expected_key = AwsClientProvider().sts_client.get_caller_identity()["Account"]  # Value mocked by moto
        mock_check_output.return_value = expected_key.encode("utf-8")

        result = aws_account_provider_mock.aws_access_key_id

        assert result == expected_key
        mock_check_output.assert_called_once_with(["aws", "configure", "get", "aws_access_key_id"])

    def test_aws_access_key_id_subprocess_error(self, mock_check_output: MagicMock, aws_account_provider_mock: AwsAccountProvider):
        mock_check_output.side_effect = subprocess.CalledProcessError(1, "aws configure get")

        with pytest.raises(SubprocessError):
            _ = aws_account_provider_mock.aws_access_key_id

    def test_aws_access_key_id_unexpected_error(self, mock_check_output: MagicMock, aws_account_provider_mock: AwsAccountProvider):
        mock_check_output.side_effect = Exception("Unexpected error")

        with pytest.raises(SubprocessError):
            _ = aws_account_provider_mock.aws_access_key_id

    def test_aws_secret_access_key_success(self, mock_check_output: MagicMock, aws_account_provider_mock: AwsAccountProvider):
        expected_key = "secretkey1234567890example"
        mock_check_output.return_value = expected_key.encode("utf-8")

        result = aws_account_provider_mock.aws_secret_access_key

        assert result == expected_key
        mock_check_output.assert_called_once_with(["aws", "configure", "get", "aws_secret_access_key"])

    def test_aws_secret_access_key_subprocess_error(self, mock_check_output: MagicMock, aws_account_provider_mock: AwsAccountProvider):
        mock_check_output.side_effect = subprocess.CalledProcessError(1, "aws configure get")

        with pytest.raises(SubprocessError):
            _ = aws_account_provider_mock.aws_secret_access_key

    def test_aws_secret_access_key_unexpected_error(self, mock_check_output: MagicMock, aws_account_provider_mock: AwsAccountProvider):
        mock_check_output.side_effect = Exception("Unexpected error")

        with pytest.raises(SubprocessError):
            _ = aws_account_provider_mock.aws_secret_access_key

    def test_aws_account_id_success(self, aws_account_provider_mock: AwsAccountProvider):
        expected_account_id = "123456789012"

        result = aws_account_provider_mock.aws_account_id

        assert result == expected_account_id

    def test_aws_account_id_client_error(self, aws_account_provider_mock: AwsAccountProvider):
        aws_account_provider_mock.client.get_caller_identity = MagicMock()
        aws_account_provider_mock.client.get_caller_identity.side_effect = ClientError(
            error_response={"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            operation_name="GetCallerIdentity"
        )

        with pytest.raises(AwsProviderError):
            _ = aws_account_provider_mock.aws_account_id

    def test_aws_account_id_unexpected_error(self, aws_account_provider_mock: AwsAccountProvider):
        aws_account_provider_mock.client.get_caller_identity = MagicMock()
        aws_account_provider_mock.client.get_caller_identity.side_effect = Exception("Unexpected error")

        with pytest.raises(AwsProviderError):
            _ = aws_account_provider_mock.aws_account_id

    def test_configure_aws_cli_success(self, mock_run: MagicMock, aws_account_provider_mock: AwsAccountProvider):
        aws_account_provider_mock.configure_aws_cli()

        mock_run.assert_called_once_with(["aws", "configure"])

    def test_configure_aws_cli_subprocess_error(self, mock_run: MagicMock, aws_account_provider_mock: AwsAccountProvider):
        mock_run.side_effect = subprocess.CalledProcessError(1, "aws configure")

        with pytest.raises(SubprocessError):
            aws_account_provider_mock.configure_aws_cli()

    def test_configure_aws_cli_unexpected_error(self, mock_run: MagicMock, aws_account_provider_mock: AwsAccountProvider):
        mock_run.side_effect = Exception("Unexpected error")

        with pytest.raises(SubprocessError):
            aws_account_provider_mock.configure_aws_cli()
