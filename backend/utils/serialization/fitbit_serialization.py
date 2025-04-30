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

import logging
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ValidationError, field_serializer

from backend.models import (
    SleepCategoryTypeEnum,
    SleepLevelEnum,
    SleepLog,
    SleepLogTypeEnum,
)

from .serialization_common import common_config

logger = logging.getLogger(__name__)


class SleepLevelModel(BaseModel):
    date_time: datetime
    level: SleepLevelEnum
    seconds: int
    is_short: Optional[bool] = None

    model_config = common_config

    @field_serializer("date_time", mode="plain")
    def serialize_date_time(value: datetime) -> str:
        return value.isoformat()


class SleepLogModel(BaseModel):
    date_of_sleep: date
    log_type: SleepLogTypeEnum
    type: SleepCategoryTypeEnum
    levels: List[SleepLevelModel] = Field(default_factory=list)

    model_config = common_config

    @field_serializer("date_of_sleep", mode="plain")
    def serialize_date_of_sleep(value: date) -> str:
        return value.isoformat()


def serialize_fitbit_data(sleep_logs: List[SleepLog]) -> List[Dict[str, Any]]:
    serialized = []
    for log in sleep_logs:
        try:
            log_model = SleepLogModel.model_validate(log)
            serialized_dump = log_model.model_dump(
                by_alias=True, exclude_unset=True, exclude_none=True
            )

            serialized.append(serialized_dump)
        except ValidationError as ve:
            logger.error(f"Validation error in SleepLogModel: {ve}")
        except Exception as e:
            logger.error(f"Error validating SleepLogModel: {e}")
    return serialized
