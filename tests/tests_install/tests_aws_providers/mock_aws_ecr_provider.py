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

from install.aws_providers.aws_ecr_provider import AwsEcrProvider
from tests.tests_install.tests_aws_providers.mock_aws_account_provider import (
    aws_account_provider,
)
from tests.tests_install.tests_aws_providers.mock_aws_client_provider import (
    aws_client_provider,
)
from tests.tests_install.tests_project_config.mock_project_config_provider import (
    project_config_provider,
)
from tests.tests_install.tests_utils.mock_logger import logger


def aws_ecr_provider():
    provider = AwsEcrProvider(
        logger=logger(),
        config=project_config_provider(),
        aws_client_provider=aws_client_provider(),
        aws_account_provider=aws_account_provider(),
    )
    return provider
