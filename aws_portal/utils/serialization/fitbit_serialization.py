from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field, model_validator
from aws_portal.models import SleepCategoryTypeEnum, SleepLevel, SleepLevelEnum, SleepLog, SleepLogTypeEnum
from .serialization_common import common_config


class SleepLevelModel(BaseModel):
    date_time: datetime
    level: SleepLevelEnum
    seconds: int
    is_short: Optional[bool] = None

    model_config = common_config

    @model_validator(mode="before")
    def extract_sleep_level(cls, obj):
        """
        Transforms a SleepLevel ORM instance into a dict
        with the required fields for SleepLevelModel.
        """
        if isinstance(obj, SleepLevel):
            return {
                "date_time": obj.date_time,
                "level": obj.level,
                "seconds": obj.seconds,
                "is_short": obj.is_short
            }
        return obj


class SleepLogModel(BaseModel):
    id: int
    log_id: int
    date_of_sleep: datetime
    duration: Optional[int] = None
    efficiency: Optional[int] = None
    end_time: Optional[datetime] = None
    info_code: Optional[int] = None
    is_main_sleep: Optional[bool] = None
    minutes_after_wakeup: Optional[int] = None
    minutes_asleep: Optional[int] = None
    minutes_awake: Optional[int] = None
    minutes_to_fall_asleep: Optional[int] = None
    log_type: SleepLogTypeEnum
    start_time: Optional[datetime] = None
    time_in_bed: Optional[int] = None
    type: SleepCategoryTypeEnum
    levels: List[SleepLevelModel] = Field(default_factory=list)

    model_config = common_config

    @model_validator(mode="before")
    def extract_sleep_log(cls, obj):
        """
        Transforms a SleepLog ORM instance into a dict
        with the required fields for SleepLogModel.
        """
        if isinstance(obj, SleepLog):
            return {
                "id": obj.id,
                "log_id": obj.log_id,
                "date_of_sleep": obj.date_of_sleep,
                "duration": obj.duration,
                "efficiency": obj.efficiency,
                "end_time": obj.end_time,
                "info_code": obj.info_code,
                "is_main_sleep": obj.is_main_sleep,
                "minutes_after_wakeup": obj.minutes_after_wakeup,
                "minutes_asleep": obj.minutes_asleep,
                "minutes_awake": obj.minutes_awake,
                "minutes_to_fall_asleep": obj.minutes_to_fall_asleep,
                "log_type": obj.log_type,
                "start_time": obj.start_time,
                "time_in_bed": obj.time_in_bed,
                "type": obj.type,
                "levels": obj.levels
            }
        return obj


def serialize_fitbit_data(sleep_logs: List[Any]) -> List[dict[str, Any]]:
    serialized = []
    for log in sleep_logs:
        log_model = SleepLogModel.model_validate(log)
        serialized.append(
            log_model.model_dump(by_alias=True, exclude_unset=True)
        )
    return serialized
