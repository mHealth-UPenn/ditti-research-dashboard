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

from install.aws_providers.aws_cloudformation_provider import (
    AwsClientProvider,
    AwsCloudformationProvider,
)
from install.utils.exceptions import AwsProviderError
from tests.tests_install.tests_aws_providers.mock_aws_cloudformation_provider import (
    aws_cloudformation_provider,
    outputs,
)
from tests.tests_install.tests_resource_managers.mock_aws_cloudformation_resource_manager import (
    parameters,
    template,
)


@pytest.fixture
def aws_cloudformation_provider_mock():
    with mock_aws():
        yield aws_cloudformation_provider()


@pytest.fixture
def template_mock():
    return template()


@pytest.fixture
def parameters_mock():
    return parameters()


@pytest.fixture
def outputs_mock():
    return outputs()


@pytest.fixture
def describe_stacks_mock(
    aws_cloudformation_provider_mock: AwsCloudformationProvider,
):
    aws_cloudformation_provider_mock.client.describe_stacks = MagicMock()
    return aws_cloudformation_provider_mock.client.describe_stacks


def test_get_outputs_success(
    template_mock: str,
    parameters_mock: list[dict[str, str]],
    outputs_mock: list[dict[str, str]],
    aws_cloudformation_provider_mock: AwsCloudformationProvider,
):
    AwsClientProvider().cloudformation_client.create_stack(
        StackName=aws_cloudformation_provider_mock.config.stack_name,
        TemplateBody=template_mock,
        Parameters=parameters_mock,
        Capabilities=["CAPABILITY_IAM"],
    )
    outputs = aws_cloudformation_provider_mock.get_outputs()
    assert outputs == outputs_mock


def test_get_outputs_stack_not_found(
    describe_stacks_mock: MagicMock,
    aws_cloudformation_provider_mock: AwsCloudformationProvider,
):
    describe_stacks_mock.return_value = {"Stacks": []}
    with pytest.raises(
        AwsProviderError,
        match=f"Stack {aws_cloudformation_provider_mock.config.stack_name} not found",
    ):
        aws_cloudformation_provider_mock.get_outputs()


def test_get_outputs_client_error(
    describe_stacks_mock: MagicMock,
    aws_cloudformation_provider_mock: AwsCloudformationProvider,
):
    describe_stacks_mock.side_effect = ClientError(
        {
            "Error": {
                "Code": "ValidationError",
                "Message": "Stack with id dev-environment does not exist",
            }
        },
        "DescribeStacks",
    )
    with pytest.raises(AwsProviderError, match="ValidationError"):
        aws_cloudformation_provider_mock.get_outputs()


def test_get_outputs_unexpected_error(
    describe_stacks_mock: MagicMock,
    aws_cloudformation_provider_mock: AwsCloudformationProvider,
):
    describe_stacks_mock.side_effect = Exception("Unexpected error")
    with pytest.raises(AwsProviderError, match="Unexpected error"):
        aws_cloudformation_provider_mock.get_outputs()
