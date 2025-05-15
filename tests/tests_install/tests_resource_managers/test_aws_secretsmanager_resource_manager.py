# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may]
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

from install.resource_managers.aws_secretsmanager_resource_manager import (
    AwsSecretsManagerResourceManager,
    DevSecretValue,
)
from install.utils.exceptions import ResourceManagerError
from tests.tests_install.tests_resource_managers.mock_aws_secretsmanager_resource_manager import (
    aws_secretsmanager_resource_manager,
    dev_secret_value,
)


@pytest.fixture
def dev_secret_value_mock():
    with mock_aws():
        yield dev_secret_value()


@pytest.fixture
def aws_secretsmanager_resource_manager_mock():
    with mock_aws():
        yield aws_secretsmanager_resource_manager()


def test_dev(
    aws_secretsmanager_resource_manager_mock: AwsSecretsManagerResourceManager,
):
    aws_secretsmanager_resource_manager_mock.set_dev_secret_value = MagicMock()
    aws_secretsmanager_resource_manager_mock.dev()
    aws_secretsmanager_resource_manager_mock.set_dev_secret_value.assert_called_once_with()


def test_dev_unexpected_error(
    aws_secretsmanager_resource_manager_mock: AwsSecretsManagerResourceManager,
):
    aws_secretsmanager_resource_manager_mock.set_dev_secret_value = MagicMock(
        side_effect=Exception("Unexpected error")
    )
    with pytest.raises(ResourceManagerError):
        aws_secretsmanager_resource_manager_mock.dev()


def test_on_end(
    aws_secretsmanager_resource_manager_mock: AwsSecretsManagerResourceManager,
):
    aws_secretsmanager_resource_manager_mock.write_secret = MagicMock()
    aws_secretsmanager_resource_manager_mock.on_end()
    aws_secretsmanager_resource_manager_mock.write_secret.assert_called_once_with()


def test_on_end_unexpected_error(
    aws_secretsmanager_resource_manager_mock: AwsSecretsManagerResourceManager,
):
    aws_secretsmanager_resource_manager_mock.write_secret = MagicMock(
        side_effect=Exception("Unexpected error")
    )
    with pytest.raises(ResourceManagerError, match="Unexpected error"):
        aws_secretsmanager_resource_manager_mock.on_end()


def test_on_end_resource_manager_error(
    aws_secretsmanager_resource_manager_mock: AwsSecretsManagerResourceManager,
):
    aws_secretsmanager_resource_manager_mock.write_secret = MagicMock(
        side_effect=ResourceManagerError("Resource manager error")
    )
    with pytest.raises(ResourceManagerError, match="Resource manager error"):
        aws_secretsmanager_resource_manager_mock.on_end()


def test_write_secret(
    aws_secretsmanager_resource_manager_mock: AwsSecretsManagerResourceManager,
    dev_secret_value_mock: DevSecretValue,
):
    aws_secretsmanager_resource_manager_mock.secret_value = dev_secret_value_mock
    res = aws_secretsmanager_resource_manager_mock.write_secret()
    assert res is not None


def test_write_secret_unexpected_error(
    aws_secretsmanager_resource_manager_mock: AwsSecretsManagerResourceManager,
):
    aws_secretsmanager_resource_manager_mock.client.put_secret_value = MagicMock(
        side_effect=Exception("Unexpected error")
    )
    with pytest.raises(ResourceManagerError, match="Unexpected error"):
        aws_secretsmanager_resource_manager_mock.write_secret()


def test_write_secret_client_error(
    aws_secretsmanager_resource_manager_mock: AwsSecretsManagerResourceManager,
):
    aws_secretsmanager_resource_manager_mock.client.put_secret_value = MagicMock(
        side_effect=ClientError(
            error_response={"Error": {"Code": "ClientError"}},
            operation_name="PutSecretValue",
        )
    )
    with pytest.raises(ResourceManagerError, match="ClientError"):
        aws_secretsmanager_resource_manager_mock.write_secret()
