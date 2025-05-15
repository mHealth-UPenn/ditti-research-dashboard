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

from install.aws_providers.aws_client_provider import AwsClientProvider


def get_authorization_token_response():
    return {"authorizationData": [{"authorizationToken": "test-token"}]}


def aws_client_provider():
    provider = AwsClientProvider()

    # Mock methods that are not mocked by moto
    provider.ecr_client.get_authorization_token = MagicMock(
        return_value=get_authorization_token_response()
    )
    return provider
