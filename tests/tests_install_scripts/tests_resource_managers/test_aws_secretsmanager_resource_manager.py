from botocore.exceptions import ClientError
from moto import mock_aws
import pytest
from unittest.mock import MagicMock

from install_scripts.resource_managers.aws_secretsmanager_resource_manager import AwsSecretsmanagerResourceManager
from install_scripts.utils.exceptions import ResourceManagerError
from install_scripts.resource_managers.aws_secretsmanager_resource_manager import DevSecretValue
from tests.tests_install_scripts.tests_resource_managers.mock_aws_secretsmanager_resource_manager import aws_secretsmanager_resource_manager, dev_secret_value


@pytest.fixture
def dev_secret_value_mock():
    with mock_aws():
        yield dev_secret_value()


@pytest.fixture
def aws_secretsmanager_resource_manager_mock():
    with mock_aws():
        yield aws_secretsmanager_resource_manager()


class TestAwsSecretsmanagerResourceManager:
    def test_dev(self, aws_secretsmanager_resource_manager_mock: AwsSecretsmanagerResourceManager):
        aws_secretsmanager_resource_manager_mock.set_dev_secret_value = MagicMock()
        aws_secretsmanager_resource_manager_mock.dev()
        aws_secretsmanager_resource_manager_mock.set_dev_secret_value.assert_called_once_with()

    def test_dev_unexpected_error(self, aws_secretsmanager_resource_manager_mock: AwsSecretsmanagerResourceManager):
        aws_secretsmanager_resource_manager_mock.set_dev_secret_value = MagicMock(side_effect=Exception("Unexpected error"))
        with pytest.raises(ResourceManagerError):
            aws_secretsmanager_resource_manager_mock.dev()

    def test_on_end(self, aws_secretsmanager_resource_manager_mock: AwsSecretsmanagerResourceManager):
        aws_secretsmanager_resource_manager_mock.write_secret = MagicMock()
        aws_secretsmanager_resource_manager_mock.on_end()
        aws_secretsmanager_resource_manager_mock.write_secret.assert_called_once_with()

    def test_on_end_unexpected_error(self, aws_secretsmanager_resource_manager_mock: AwsSecretsmanagerResourceManager):
        aws_secretsmanager_resource_manager_mock.write_secret = MagicMock(side_effect=Exception("Unexpected error"))
        with pytest.raises(ResourceManagerError, match="Unexpected error"):
            aws_secretsmanager_resource_manager_mock.on_end()

    def test_on_end_resource_manager_error(self, aws_secretsmanager_resource_manager_mock: AwsSecretsmanagerResourceManager):
        aws_secretsmanager_resource_manager_mock.write_secret = MagicMock(side_effect=ResourceManagerError("Resource manager error"))
        with pytest.raises(ResourceManagerError, match="Resource manager error"):
            aws_secretsmanager_resource_manager_mock.on_end()

    def test_write_secret(self, aws_secretsmanager_resource_manager_mock: AwsSecretsmanagerResourceManager, dev_secret_value_mock: DevSecretValue):
        aws_secretsmanager_resource_manager_mock.secret_value = dev_secret_value_mock
        res = aws_secretsmanager_resource_manager_mock.write_secret()
        assert res is not None

    def test_write_secret_unexpected_error(self, aws_secretsmanager_resource_manager_mock: AwsSecretsmanagerResourceManager):
        aws_secretsmanager_resource_manager_mock.client.put_secret_value = MagicMock(side_effect=Exception("Unexpected error"))
        with pytest.raises(ResourceManagerError, match="Unexpected error"):
            aws_secretsmanager_resource_manager_mock.write_secret()

    def test_write_secret_client_error(self, aws_secretsmanager_resource_manager_mock: AwsSecretsmanagerResourceManager):
        aws_secretsmanager_resource_manager_mock.client.put_secret_value = MagicMock(side_effect=ClientError(
            error_response={"Error": {"Code": "ClientError"}},
            operation_name="PutSecretValue"
        ))
        with pytest.raises(ResourceManagerError, match="ClientError"):
            aws_secretsmanager_resource_manager_mock.write_secret()
