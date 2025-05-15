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

from install.resource_managers.aws_cognito_resource_manager import (
    AwsCognitoResourceManager,
)
from tests.tests_install.tests_aws_providers.mock_aws_client_provider import (
    aws_client_provider,
)
from tests.tests_install.tests_project_config.mock_project_config_provider import (
    project_config_provider,
)
from tests.tests_install.tests_utils.mock_logger import logger


def participant_user_pool():
    return aws_client_provider().cognito_client.create_user_pool(
        PoolName="participant-user-pool"
    )


def researcher_user_pool():
    return aws_client_provider().cognito_client.create_user_pool(
        PoolName="researcher-user-pool"
    )


def participant_user_pool_client(participant_user_pool: dict):
    return aws_client_provider().cognito_client.create_user_pool_client(
        UserPoolId=participant_user_pool["UserPool"]["Id"],
        ClientName="participant-user-pool-client",
        GenerateSecret=True,
    )


def researcher_user_pool_client(researcher_user_pool: dict):
    return aws_client_provider().cognito_client.create_user_pool_client(
        UserPoolId=researcher_user_pool["UserPool"]["Id"],
        ClientName="researcher-user-pool-client",
        GenerateSecret=True,
    )


def aws_cognito_resource_manager():
    provider = AwsCognitoResourceManager(
        logger=logger(),
        config=project_config_provider(),
        aws_client_provider=aws_client_provider(),
    )
    participant = participant_user_pool()
    researcher = researcher_user_pool()
    participant_client = participant_user_pool_client(participant)
    researcher_client = researcher_user_pool_client(researcher)
    provider.config.participant_user_pool_id = participant["UserPool"]["Id"]
    provider.config.participant_client_id = participant_client["UserPoolClient"][
        "ClientId"
    ]
    provider.config.researcher_user_pool_id = researcher["UserPool"]["Id"]
    provider.config.researcher_client_id = researcher_client["UserPoolClient"][
        "ClientId"
    ]
    return provider
