from unittest.mock import MagicMock
import pytest

from botocore.exceptions import ClientError
from moto import mock_aws

from install_scripts.resource_managers.aws_cloudformation_resource_manager import AwsCloudformationResourceManager
from install_scripts.utils.exceptions import ResourceManagerError, UninstallError
from tests.tests_install_scripts.tests_resource_managers.mock_aws_cloudformation_resource_manager import aws_cloudformation_resource_manager, parameters, template

@pytest.fixture
def parameters_mock():
    return parameters()


@pytest.fixture
def template_mock():
    return template()


@pytest.fixture
def aws_cloudformation_resource_manager_mock():
    with mock_aws():
        yield aws_cloudformation_resource_manager()


class TestAwsCloudformationResourceManager:
    def test_dev_success(self, aws_cloudformation_resource_manager_mock: AwsCloudformationResourceManager, template_mock: str, parameters_mock: list[dict[str, str]]):
        aws_cloudformation_resource_manager_mock.create_cloudformation_stack = MagicMock(return_value=None)

        aws_cloudformation_resource_manager_mock.dev()

        aws_cloudformation_resource_manager_mock.create_cloudformation_stack.assert_called_once_with(
            template_body=template_mock,
            parameters=parameters_mock,
        )

    def test_dev_client_error(self, aws_cloudformation_resource_manager_mock: AwsCloudformationResourceManager):
        aws_cloudformation_resource_manager_mock.create_cloudformation_stack = MagicMock(
            side_effect=ClientError(
                error_response={"Error": {"Code": "ClientError"}},
                operation_name="CreateCloudFormationStack"
            )
        )

        with pytest.raises(ResourceManagerError, match="ClientError"):
            aws_cloudformation_resource_manager_mock.dev()

    def test_dev_unexpected_error(self, aws_cloudformation_resource_manager_mock: AwsCloudformationResourceManager):
        aws_cloudformation_resource_manager_mock.create_cloudformation_stack = MagicMock(side_effect=Exception("Unexpected error"))

        with pytest.raises(ResourceManagerError, match="Unexpected error"):
            aws_cloudformation_resource_manager_mock.dev()


    def test_create_cloudformation_stack_success(self, aws_cloudformation_resource_manager_mock: AwsCloudformationResourceManager, template_mock: str, parameters_mock: list[dict[str, str]]):
        res = aws_cloudformation_resource_manager_mock.create_cloudformation_stack(
            template_body=template_mock,
            parameters=parameters_mock,
        )

        assert res is not None

    def test_create_cloudformation_stack_client_error(self, aws_cloudformation_resource_manager_mock: AwsCloudformationResourceManager, template_mock: str, parameters_mock: list[dict[str, str]]):
        aws_cloudformation_resource_manager_mock.client.create_stack = MagicMock(side_effect=ClientError(
            error_response={"Error": {"Code": "ClientError"}},
            operation_name="CreateCloudFormationStack"
        ))

        with pytest.raises(ResourceManagerError):
            aws_cloudformation_resource_manager_mock.create_cloudformation_stack(
                template_body=template_mock,
                parameters=parameters_mock,
            )

    def test_create_cloudformation_stack_unexpected_error(self, aws_cloudformation_resource_manager_mock: AwsCloudformationResourceManager, template_mock: str, parameters_mock: list[dict[str, str]]):
        aws_cloudformation_resource_manager_mock.client.create_stack = MagicMock(side_effect=Exception("Unexpected error"))

        with pytest.raises(ResourceManagerError):
            aws_cloudformation_resource_manager_mock.create_cloudformation_stack(
                template_body=template_mock,
                parameters=parameters_mock,
            )

    def test_dev_uninstall_success(self, aws_cloudformation_resource_manager_mock: AwsCloudformationResourceManager):
        aws_cloudformation_resource_manager_mock.client.delete_stack = MagicMock(return_value=None)

        aws_cloudformation_resource_manager_mock.dev_uninstall()

        aws_cloudformation_resource_manager_mock.client.delete_stack.assert_called_once_with(StackName=aws_cloudformation_resource_manager_mock.settings.stack_name)

    def test_dev_uninstall_client_error(self, aws_cloudformation_resource_manager_mock: AwsCloudformationResourceManager):
        aws_cloudformation_resource_manager_mock.client.delete_stack = MagicMock(side_effect=ClientError(
            error_response={"Error": {"Code": "ClientError"}},
            operation_name="DeleteCloudFormationStack"
        ))

        with pytest.raises(UninstallError, match="ClientError"):
            aws_cloudformation_resource_manager_mock.dev_uninstall()

    def test_dev_uninstall_unexpected_error(self, aws_cloudformation_resource_manager_mock: AwsCloudformationResourceManager):
        aws_cloudformation_resource_manager_mock.client.delete_stack = MagicMock(side_effect=Exception("Unexpected error"))

        with pytest.raises(UninstallError, match="Unexpected error"):
            aws_cloudformation_resource_manager_mock.dev_uninstall()

