from unittest.mock import MagicMock

from botocore.exceptions import ClientError
import pytest
from moto import mock_aws

from install.resource_managers.aws_cognito_resource_manager import AwsCognitoResourceManager
from tests.tests_install.tests_resource_managers.mock_aws_cognito_resource_manager import aws_cognito_resource_manager
from install.utils.exceptions import ResourceManagerError


@pytest.fixture
def aws_cognito_resource_manager_mock():
    with mock_aws():
        yield aws_cognito_resource_manager()


def test_create_admin_user(aws_cognito_resource_manager_mock: AwsCognitoResourceManager):
    res = aws_cognito_resource_manager_mock.create_admin_user()
    assert res is not None


def test_create_admin_user_client_error(aws_cognito_resource_manager_mock: AwsCognitoResourceManager):
    aws_cognito_resource_manager_mock.client.admin_create_user = MagicMock(side_effect=ClientError(
        error_response={"Error": {"Code": "ClientError"}},
        operation_name="AdminCreateUser"
    ))
    with pytest.raises(ResourceManagerError, match="ClientError"):
        aws_cognito_resource_manager_mock.create_admin_user()


def test_create_admin_user_unexpected_error(aws_cognito_resource_manager_mock: AwsCognitoResourceManager):
    aws_cognito_resource_manager_mock.client.admin_create_user = MagicMock(side_effect=Exception("Unexpected error"))
    with pytest.raises(ResourceManagerError, match="Unexpected error"):
        aws_cognito_resource_manager_mock.create_admin_user()


def test_on_end(aws_cognito_resource_manager_mock: AwsCognitoResourceManager):
    aws_cognito_resource_manager_mock.create_admin_user = MagicMock(return_value={"User": {"Username": "test-user"}})
    aws_cognito_resource_manager_mock.on_end()
    aws_cognito_resource_manager_mock.create_admin_user.assert_called_once()


def test_on_end_unexpected_error(aws_cognito_resource_manager_mock: AwsCognitoResourceManager):
    aws_cognito_resource_manager_mock.create_admin_user = MagicMock(side_effect=Exception("Unexpected error"))
    with pytest.raises(ResourceManagerError, match="Unexpected error"):
        aws_cognito_resource_manager_mock.on_end()


def test_on_end_resource_manager_error(aws_cognito_resource_manager_mock: AwsCognitoResourceManager):
    aws_cognito_resource_manager_mock.create_admin_user = MagicMock(side_effect=ResourceManagerError("Resource manager error"))
    with pytest.raises(ResourceManagerError, match="Resource manager error"):
        aws_cognito_resource_manager_mock.on_end()
