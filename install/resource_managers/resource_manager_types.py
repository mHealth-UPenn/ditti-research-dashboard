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

from typing import TypedDict


class CloudFormationParameter(TypedDict):
    """
    Type definition for CloudFormation parameters.

    Represents key-value pairs used as parameters when creating
    or updating CloudFormation stacks.
    """

    ParameterKey: str
    ParameterValue: str


class DevSecretValue(TypedDict):
    """
    Type definition for development environment secrets.

    Contains credential values required for third-party integrations
    and authentication in the development environment.
    """

    FITBIT_CLIENT_ID: str
    FITBIT_CLIENT_SECRET: str
    COGNITO_PARTICIPANT_CLIENT_SECRET: str
    COGNITO_RESEARCHER_CLIENT_SECRET: str


class S3Object(TypedDict):
    """
    Type definition for S3 object identifiers.

    Contains the key and version ID needed to uniquely identify
    objects in versioned S3 buckets.
    """

    Key: str
    VersionId: str
