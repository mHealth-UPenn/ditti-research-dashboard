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

from enum import Enum


class Postgres(Enum):
    USER = "username"
    PASSWORD = "password"
    PORT = 5432
    DB = "postgres"


class FString(Enum):
    participant_user_pool_name = "{project_name}-participant-pool"
    participant_user_pool_domain = "{project_name}-participant"
    researcher_user_pool_name = "{project_name}-researcher-pool"
    researcher_user_pool_domain = "{project_name}-researcher"
    logs_bucket_name = "{project_name}-wearable-data-retrieval-logs"
    audio_bucket_name = "{project_name}-audio-files"
    secret_name = "{project_name}-secret"
    tokens_secret_name = "{project_name}-Fitbit-tokens"
    stack_name = "{project_name}-stack"
    network_name = "{project_name}-network"
    postgres_container_name = "{project_name}-postgres"
    wearable_data_retrieval_container_name = \
        "{project_name}-wearable-data-retrieval"
