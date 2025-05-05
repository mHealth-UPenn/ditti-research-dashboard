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

from install.aws_providers import AwsAccountProvider
from tests.tests_install.tests_aws_providers.mock_aws_client_provider import (
    aws_client_provider,
)
from tests.tests_install.tests_utils.mock_logger import logger

mock_account_id = "test-account-id"
mock_aws_region = "test-region"
mock_aws_access_key_id = "test-access-key-id"
mock_aws_secret_access_key = "test-secret-access-key"  # noqa: S105


def aws_account_provider():
    provider = AwsAccountProvider(
        logger=logger(), aws_client_provider=aws_client_provider()
    )

    provider.get_aws_access_key_id = MagicMock(
        return_value=mock_aws_access_key_id
    )
    provider.get_aws_secret_access_key = MagicMock(
        return_value=mock_aws_secret_access_key
    )
    provider.client = MagicMock()
    provider.client.meta.region_name = mock_aws_region
    provider.client.get_caller_identity = MagicMock(
        return_value={"Account": mock_account_id}
    )

    return provider
