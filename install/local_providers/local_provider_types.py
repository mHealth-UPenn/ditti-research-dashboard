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


class RootEnv(TypedDict):
    """
    Type definition for root environment variables.

    Contains environment variables required for the main application.
    """

    FLASK_CONFIG: str
    FLASK_DEBUG: str
    FLASK_DB: str
    FLASK_APP: str
    APP_SYNC_HOST: str
    APPSYNC_ACCESS_KEY: str
    APPSYNC_SECRET_KEY: str
    AWS_AUDIO_FILE_BUCKET: str
    AWS_TABLENAME_AUDIO_FILE: str
    AWS_TABLENAME_AUDIO_TAP: str
    AWS_TABLENAME_TAP: str
    AWS_TABLENAME_USER: str
    COGNITO_PARTICIPANT_CLIENT_ID: str
    COGNITO_PARTICIPANT_DOMAIN: str
    COGNITO_PARTICIPANT_REGION: str
    COGNITO_PARTICIPANT_USER_POOL_ID: str
    COGNITO_RESEARCHER_CLIENT_ID: str
    COGNITO_RESEARCHER_DOMAIN: str
    COGNITO_RESEARCHER_REGION: str
    COGNITO_RESEARCHER_USER_POOL_ID: str
    LOCAL_LAMBDA_ENDPOINT: str
    TM_FSTRING: str


class WearableDataRetrievalEnv(TypedDict):
    """
    Type definition for wearable data retrieval environment variables.

    Contains environment variables required for the wearable data
    retrieval Lambda function.
    """

    DB_URI: str
    S3_BUCKET: str
    AWS_CONFIG_SECRET_NAME: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str
