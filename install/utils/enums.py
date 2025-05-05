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

from enum import Enum


class Postgres(Enum):
    """
    Enumeration of PostgreSQL configuration values.

    Contains standard configuration values for PostgreSQL database
    connection and authentication.
    """

    USER = "username"
    PASSWORD = "password"  # noqa: S105
    PORT = 5432
    DB = "postgres"


class FString(Enum):
    """
    Enumeration of format strings for resource naming.

    Contains format string templates for naming various resources
    in the installation process.
    """

    participant_user_pool_name = "{project_name}-participant-pool"
    participant_user_pool_domain = "{project_name}-participant"
    researcher_user_pool_name = "{project_name}-researcher-pool"
    researcher_user_pool_domain = "{project_name}-researcher"
    logs_bucket_name = "{project_name}-wearable-data-retrieval-logs"
    audio_bucket_name = "{project_name}-audio-files"
    secret_name = "{project_name}-secret"  # noqa: S105
    tokens_secret_name = "{project_name}-Fitbit-tokens"  # noqa: S105
    stack_name = "{project_name}-stack"
    network_name = "{project_name}-network"
    postgres_container_name = "{project_name}-postgres"
    wearable_data_retrieval_container_name = (
        "{project_name}-wearable-data-retrieval"
    )
