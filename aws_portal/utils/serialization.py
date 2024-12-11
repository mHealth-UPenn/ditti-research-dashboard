from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict
import logging

logger = logging.getLogger(__name__)


def to_camel(string: str) -> str:
    """
    Converts a snake_case string to camelCase.

    Args:
        string (str): The snake_case string to convert.

    Returns:
        str: The converted camelCase string.
    """
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class BaseCamelModel(BaseModel):
    """
    Base Pydantic model with camelCase alias generator and enum value usage.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_enum_values=True
    )


class SleepLogTypeEnum(str, Enum):
    AUTO_DETECTED = "auto_detected"
    MANUAL = "manual"


class SleepCategoryTypeEnum(str, Enum):
    STAGES = "stages"
    CLASSIC = "classic"


class SleepLevelEnum(str, Enum):
    DEEP = "deep"
    LIGHT = "light"
    REM = "rem"
    WAKE = "wake"
    ASLEEP = "asleep"
    RESTLESS = "restless"
    AWAKE = "awake"


class SleepLevelModel(BaseCamelModel):
    """
    Pydantic model representing a single sleep level entry within a sleep log.
    """
    dateTime: Optional[datetime] = Field(None)
    level: Optional[SleepLevelEnum] = None
    seconds: Optional[int] = None
    isShort: Optional[bool] = Field(None)


class SleepLogModel(BaseCamelModel):
    """
    Pydantic model representing a single sleep log entry for a study subject.
    """
    id: Optional[int] = None
    logId: Optional[int] = None
    dateOfSleep: Optional[datetime] = None
    duration: Optional[int] = None
    efficiency: Optional[int] = None
    endTime: Optional[datetime] = None
    infoCode: Optional[int] = None
    isMainSleep: Optional[bool] = None
    minutesAfterWakeup: Optional[int] = None
    minutesAsleep: Optional[int] = None
    minutesAwake: Optional[int] = None
    minutesToFallAsleep: Optional[int] = None
    logType: Optional[SleepLogTypeEnum] = None
    startTime: Optional[datetime] = None
    timeInBed: Optional[int] = None
    type: Optional[SleepCategoryTypeEnum] = None
    levels: List[SleepLevelModel] = Field(default_factory=list)


def serialize_participant(study_subject) -> dict[str, Any]:
    """
    Transforms a StudySubject object into a JSON-serializable dictionary containing only the required fields.

    Args:
        study_subject (StudySubject): The StudySubject instance to serialize.

    Returns:
        dict: A dictionary containing the serialized participant data.
    """
    participant_data = {
        "dittiId": study_subject.meta.dittiId,
        "userId": study_subject.meta.id,
        "apis": [],
        "studies": []
    }

    # Serialize APIs
    for api_entry in study_subject.meta.apis:
        api_data = {
            "apiName": api_entry.meta.api.meta.name,
            "scope": api_entry.meta.scope
        }
        participant_data["apis"].append(api_data)

    # Serialize Studies
    for study_entry in study_subject.studies:
        study_data = {
            "studyName": study_entry.meta.study.meta.name,
            "studyId": study_entry.meta.study.meta.id,
            "createdOn": study_entry.meta.createdOn,
            "expiresOn": study_entry.meta.expiresOn,
            "dataSummary": study_entry.meta.study.meta.dataSummary
        }
        participant_data["studies"].append(study_data)

    return participant_data


def serialize_fitbit_data(results: List[Any]) -> List[Dict[str, Any]]:
    """
    Serializes Fitbit data from query results into a structured format using Pydantic models.

    This function processes a list of SQLAlchemy row objects resulting from a joined query
    between SleepLog and SleepLevel tables. It groups sleep logs by their unique ID,
    serializes each log and its associated levels, and handles missing or incomplete data gracefully.

    Args:
        results (List[Any]): List of SQLAlchemy row objects from the SleepLog and SleepLevel join query.

    Returns:
        List[Dict[str, Any]]: A list of serialized sleep log dictionaries ready for JSON response.
    """
    # Initialize defaultdict with a lambda to create SleepLogModel instances
    sleep_logs_dict = defaultdict(lambda: SleepLogModel())

    for row in results:
        log_id = getattr(row, "sleep_log_id", None)
        if log_id is None:
            logger.warning(f"Row missing 'sleep_log_id': {row}")
            continue

        # Retrieve or create the SleepLogModel instance
        sleep_log = sleep_logs_dict[log_id]

        # Populate SleepLogModel fields if not already set
        if sleep_log.id is None:
            sleep_log_data = {
                "id": row.sleep_log_id,
                "logId": row.log_id,
                "dateOfSleep": row.date_of_sleep,
                "duration": row.duration,
                "efficiency": row.efficiency,
                "endTime": row.end_time,
                "infoCode": row.info_code,
                "isMainSleep": row.is_main_sleep,
                "minutesAfterWakeup": row.minutes_after_wakeup,
                "minutesAsleep": row.minutes_asleep,
                "minutesAwake": row.minutes_awake,
                "minutesToFallAsleep": row.minutes_to_fall_asleep,
                "logType": row.log_type,
                "startTime": row.start_time,
                "timeInBed": row.time_in_bed,
                "type": row.type
            }

            try:
                # Initialize SleepLogModel with the extracted data
                sleep_log = SleepLogModel(**sleep_log_data)
                sleep_logs_dict[log_id] = sleep_log
            except Exception as e:
                logger.error(
                    f"Error creating SleepLogModel for log_id {log_id}: {e}"
                )
                continue

        # Extract SleepLevel data
        level_date_time = getattr(row, "level_date_time", None)
        level_level = getattr(row, "level_level", None)
        level_seconds = getattr(row, "level_seconds", None)
        is_short = getattr(row, "is_short", None)

        if any([level_date_time, level_level, level_seconds, is_short]):
            try:
                sleep_level = SleepLevelModel(
                    dateTime=level_date_time,  # Pydantic handles datetime serialization
                    level=level_level,         # Enum handled by Pydantic's use_enum_values
                    seconds=level_seconds,
                    isShort=is_short,
                )
                sleep_log.levels.append(sleep_level)
            except Exception as e:
                logger.error(
                    f"Error processing SleepLevel for log_id {log_id}: {e}"
                )

    # Serialize all SleepLogModel instances to dictionaries
    serialized_data = [
        sleep_log.model_dump(by_alias=True, exclude_unset=True)
        for sleep_log in sleep_logs_dict.values()
    ]

    return serialized_data
