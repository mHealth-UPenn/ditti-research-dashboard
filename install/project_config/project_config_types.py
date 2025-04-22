# Ditti Research Dashboard
# Copyright (C) 2025 the Trustees of the University of Pennsylvania
#
# Ditti Research Dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Ditti Research Dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import TypedDict


class CognitoConfig(TypedDict):
    """
    Type definition for AWS Cognito configuration.

    Contains configuration settings for participant and researcher
    user pools in AWS Cognito.
    """

    participant_user_pool_name: str
    participant_user_pool_domain: str
    participant_user_pool_id: str
    participant_client_id: str
    researcher_user_pool_name: str
    researcher_user_pool_domain: str
    researcher_user_pool_id: str
    researcher_client_id: str


class S3Config(TypedDict):
    """
    Type definition for AWS S3 bucket configuration.

    Contains configuration settings for logs and audio storage buckets.
    """

    logs_bucket_name: str
    audio_bucket_name: str


class SecretsResourceManagerConfig(TypedDict):
    """
    Type definition for AWS Secrets Manager configuration.

    Contains configuration settings for secrets storage.
    """

    secret_name: str
    tokens_secret_name: str


class DockerConfig(TypedDict):
    """
    Type definition for Docker configuration.

    Contains configuration settings for Docker networks and containers.
    """

    network_name: str
    postgres_container_name: str
    wearable_data_retrieval_container_name: str


class AwsConfig(TypedDict):
    """
    Type definition for AWS service configuration.

    Contains configuration settings for various AWS services.
    """

    cognito: CognitoConfig
    s3: S3Config
    secrets_manager: SecretsResourceManagerConfig
    stack_name: str


class ProjectConfig(TypedDict):
    """
    Type definition for overall project configuration.

    Contains all configuration settings for the project.
    """

    project_name: str
    admin_email: str
    aws: AwsConfig
    docker: DockerConfig


class UserInput(TypedDict):
    """
    Type definition for user input during configuration.

    Contains user-provided configuration values.
    """

    project_name: str | None
    fitbit_client_id: str | None
    fitbit_client_secret: str | None
    admin_email: str | None
