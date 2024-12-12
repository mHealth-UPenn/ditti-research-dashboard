from datetime import datetime, date
from typing import Any, List, Optional, Dict
from pydantic import BaseModel, Field, ValidationError, field_serializer
from aws_portal.models import (
    SleepCategoryTypeEnum, SleepLevelEnum, SleepLog, SleepLogTypeEnum
)
from .serialization_common import common_config
import logging

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
                by_alias=True,
                exclude_unset=True,
                exclude_none=True
            )

            serialized.append(serialized_dump)
        except ValidationError as ve:
            logger.error(
                f"Validation error in SleepLogModel for log {log.id}: {ve}"
            )
        except Exception as e:
            logger.error(f"Error validating SleepLogModel: {e}")
    return serialized
