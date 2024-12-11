from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field
from aws_portal.models import SleepCategoryTypeEnum, SleepLevelEnum, SleepLogTypeEnum
from .serialization_common import common_config


class SleepLevelModel(BaseModel):
    date_time: datetime
    level: SleepLevelEnum
    seconds: int
    is_short: Optional[bool] = None

    model_config = common_config


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

    @classmethod
    def model_validate(cls, obj):
        # Validate the base model
        model = super().model_validate(obj)

        # Parse levels from the ORM object
        levels_models = [SleepLevelModel.model_validate(lvl)
                         for lvl in obj.levels]

        # Construct the model with parsed levels
        return cls.model_construct(
            **model.__dict__,
            levels=levels_models
        )


def serialize_fitbit_data(sleep_logs: List[Any]) -> List[dict[str, Any]]:
    serialized = []
    for log in sleep_logs:
        log_model = SleepLogModel.model_validate(log)
        serialized.append(
            log_model.model_dump(by_alias=True, exclude_unset=True)
        )
    return serialized
