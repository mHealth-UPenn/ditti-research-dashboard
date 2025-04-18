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


class RootEnv(TypedDict):
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
    DB_URI: str
    S3_BUCKET: str
    AWS_CONFIG_SECRET_NAME: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str
