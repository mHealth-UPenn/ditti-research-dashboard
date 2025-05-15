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

import os
from unittest.mock import MagicMock

from install.resource_managers.aws_cloudformation_resource_manager import (
    AwsCloudformationResourceManager,
)
from tests.tests_install.tests_aws_providers.mock_aws_client_provider import (
    aws_client_provider,
)
from tests.tests_install.tests_project_config.mock_project_config_provider import (
    project_config_provider,
)
from tests.tests_install.tests_utils.mock_logger import logger


def template():
    # Get the absolute path to the project root directory
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../..")
    )
    template_path = os.path.join(
        project_root, "tests/data/cloudformation/template.yml"
    )

    with open(template_path) as f:
        return f.read()


def parameters():
    return [
        {
            "ParameterKey": "TestParameter1",
            "ParameterValue": "test-parameter-1-value",
        },
        {
            "ParameterKey": "TestParameter2",
            "ParameterValue": "test-parameter-2-value",
        },
    ]


def aws_cloudformation_resource_manager():
    provider = AwsCloudformationResourceManager(
        logger=logger(),
        config=project_config_provider(),
        aws_client_provider=aws_client_provider(),
    )
    provider.get_dev_parameters = MagicMock(return_value=parameters())
    provider.get_dev_template_body = MagicMock(return_value=template())
    return provider
