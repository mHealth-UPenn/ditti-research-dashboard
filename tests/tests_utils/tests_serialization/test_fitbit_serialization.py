import logging
from datetime import datetime, date
from typing import List, Optional

import pytest

from aws_portal.utils.serialization.fitbit_serialization import serialize_fitbit_data
from aws_portal.models import (
    SleepLevelEnum,
    SleepLogTypeEnum,
    SleepCategoryTypeEnum
)

# ----------------------------
# Mock Classes
# ----------------------------


class MockSleepLevel:
    def __init__(
        self,
        date_time: datetime,
        level: SleepLevelEnum,
        seconds: int,
        is_short: Optional[bool] = None
    ):
        self.date_time = date_time
        self.level = level
        self.seconds = seconds
        self.is_short = is_short


class MockSleepLog:
    def __init__(
        self,
        date_of_sleep: date,
        log_type: SleepLogTypeEnum,
        sleep_type: SleepCategoryTypeEnum,
        levels: List[MockSleepLevel],
    ):
        self.date_of_sleep = date_of_sleep
        self.log_type = log_type
        self.type = sleep_type
        self.levels = levels

# ----------------------------
# Fixtures for Sample Data
# ----------------------------


@pytest.fixture
def sample_sleep_logs():
    # SleepLog 1: Stages type
    levels_stages = [
        MockSleepLevel(
            date_time=datetime(2024, 4, 20, 23, 0, 0),
            level=SleepLevelEnum.deep,
            seconds=1800
        ),
        MockSleepLevel(
            date_time=datetime(2024, 4, 20, 23, 30, 0),
            level=SleepLevelEnum.light,
            seconds=2700
        ),
        MockSleepLevel(
            date_time=datetime(2024, 4, 21, 0, 15, 0),
            level=SleepLevelEnum.rem,
            seconds=1800
        ),
        MockSleepLevel(
            date_time=datetime(2024, 4, 21, 0, 45, 0),
            level=SleepLevelEnum.wake,
            seconds=600
        ),
    ]
    sleep_log1 = MockSleepLog(
        date_of_sleep=date(2024, 4, 21),
        log_type=SleepLogTypeEnum.auto_detected,
        sleep_type=SleepCategoryTypeEnum.stages,
        levels=levels_stages
    )

    # SleepLog 2: Classic type
    levels_classic = [
        MockSleepLevel(
            date_time=datetime(2024, 4, 19, 22, 30, 0),
            level=SleepLevelEnum.asleep,
            seconds=3600
        ),
        MockSleepLevel(
            date_time=datetime(2024, 4, 19, 23, 30, 0),
            level=SleepLevelEnum.awake,
            seconds=900
        ),
        MockSleepLevel(
            date_time=datetime(2024, 4, 19, 23, 45, 0),
            level=SleepLevelEnum.asleep,
            seconds=1800
        ),
    ]
    sleep_log2 = MockSleepLog(
        date_of_sleep=date(2024, 4, 20),
        log_type=SleepLogTypeEnum.manual,
        sleep_type=SleepCategoryTypeEnum.classic,
        levels=levels_classic
    )

    return [sleep_log1, sleep_log2]

# ----------------------------
# Unit Tests
# ----------------------------


def test_serialize_fitbit_data(sample_sleep_logs):
    serialized = serialize_fitbit_data(sample_sleep_logs)

    assert isinstance(serialized, list)
    assert len(serialized) == 2

    # Test first SleepLog (Stages)
    log1_serialized = serialized[0]
    assert log1_serialized["dateOfSleep"] == "2024-04-21"
    assert log1_serialized["logType"] == "auto_detected"
    assert log1_serialized["type"] == "stages"

    # Check levels
    assert len(log1_serialized["levels"]) == 4
    assert log1_serialized["levels"][0]["dateTime"] == "2024-04-20T23:00:00"
    assert log1_serialized["levels"][0]["level"] == "deep"
    assert log1_serialized["levels"][0]["seconds"] == 1800
    assert log1_serialized["levels"][0].get(
        "isShort") is None  # Optional field

    assert log1_serialized["levels"][1]["dateTime"] == "2024-04-20T23:30:00"
    assert log1_serialized["levels"][1]["level"] == "light"
    assert log1_serialized["levels"][1]["seconds"] == 2700
    assert log1_serialized["levels"][1].get(
        "isShort") is None  # Optional field

    assert log1_serialized["levels"][2]["dateTime"] == "2024-04-21T00:15:00"
    assert log1_serialized["levels"][2]["level"] == "rem"
    assert log1_serialized["levels"][2]["seconds"] == 1800
    assert log1_serialized["levels"][2].get(
        "isShort") is None  # Optional field

    assert log1_serialized["levels"][3]["dateTime"] == "2024-04-21T00:45:00"
    assert log1_serialized["levels"][3]["level"] == "wake"
    assert log1_serialized["levels"][3]["seconds"] == 600
    assert log1_serialized["levels"][3].get(
        "isShort") is None  # Optional field

    # Test second SleepLog (Classic)
    log2_serialized = serialized[1]
    assert log2_serialized["dateOfSleep"] == "2024-04-20"
    assert log2_serialized["logType"] == "manual"
    assert log2_serialized["type"] == "classic"

    # Check levels
    assert len(log2_serialized["levels"]) == 3
    assert log2_serialized["levels"][0]["dateTime"] == "2024-04-19T22:30:00"
    assert log2_serialized["levels"][0]["level"] == "asleep"
    assert log2_serialized["levels"][0]["seconds"] == 3600
    assert log2_serialized["levels"][0].get(
        "isShort") is None  # Optional field

    assert log2_serialized["levels"][1]["dateTime"] == "2024-04-19T23:30:00"
    assert log2_serialized["levels"][1]["level"] == "awake"
    assert log2_serialized["levels"][1]["seconds"] == 900
    assert log2_serialized["levels"][1].get(
        "isShort") is None  # Optional field

    assert log2_serialized["levels"][2]["dateTime"] == "2024-04-19T23:45:00"
    assert log2_serialized["levels"][2]["level"] == "asleep"
    assert log2_serialized["levels"][2]["seconds"] == 1800
    assert log2_serialized["levels"][2].get(
        "isShort") is None  # Optional field


def test_serialize_fitbit_data_empty():
    # Test serialization with empty input
    serialized = serialize_fitbit_data([])
    assert serialized == []


def test_serialize_fitbit_data_missing_fields():
    # Create a SleepLog with empty levels
    sleep_log = MockSleepLog(
        date_of_sleep=date(2024, 5, 1),
        log_type=SleepLogTypeEnum.auto_detected,
        sleep_type=SleepCategoryTypeEnum.stages,
        levels=[]
    )

    serialized = serialize_fitbit_data([sleep_log])

    assert len(serialized) == 1
    log_serialized = serialized[0]
    assert log_serialized["dateOfSleep"] == "2024-05-01"
    assert log_serialized["logType"] == "auto_detected"
    assert log_serialized["type"] == "stages"
    assert log_serialized["levels"] == []


def test_serialize_fitbit_data_invalid_enum(caplog):
    # Create a SleepLog with invalid enum values
    sleep_log = MockSleepLog(
        date_of_sleep=date(2024, 6, 1),
        log_type="invalid_type",  # Invalid enum
        sleep_type="invalid_category",  # Invalid enum
        levels=[]
    )

    with caplog.at_level(logging.ERROR):
        serialized = serialize_fitbit_data([sleep_log])

    # Since the SleepLog is invalid, it should not be in the serialized output
    assert len(serialized) == 0

    # Check that an error was logged
    error_message_start = "Validation error in SleepLogModel:"
    assert any(error_message_start in record.message for record in caplog.records)


def test_serialize_fitbit_data_partial_levels():
    # Create a SleepLog with some levels missing optional fields
    levels_partial = [
        MockSleepLevel(
            date_time=datetime(2024, 7, 1, 23, 0, 0),
            level=SleepLevelEnum.rem,
            seconds=1200
        ),
        MockSleepLevel(
            date_time=datetime(2024, 7, 1, 23, 20, 0),
            level=SleepLevelEnum.deep,
            seconds=1800,
            is_short=True
        ),
    ]
    sleep_log = MockSleepLog(
        date_of_sleep=date(2024, 7, 2),
        log_type=SleepLogTypeEnum.auto_detected,
        sleep_type=SleepCategoryTypeEnum.stages,
        levels=levels_partial
    )

    serialized = serialize_fitbit_data([sleep_log])

    assert len(serialized) == 1
    log_serialized = serialized[0]
    assert log_serialized["dateOfSleep"] == "2024-07-02"
    assert log_serialized["logType"] == "auto_detected"
    assert log_serialized["type"] == "stages"

    # Check levels
    assert len(log_serialized["levels"]) == 2

    level1 = log_serialized["levels"][0]
    assert level1["dateTime"] == "2024-07-01T23:00:00"
    assert level1["level"] == "rem"
    assert level1["seconds"] == 1200
    assert level1.get("isShort") is None  # Optional field not provided

    level2 = log_serialized["levels"][1]
    assert level2["dateTime"] == "2024-07-01T23:20:00"
    assert level2["level"] == "deep"
    assert level2["seconds"] == 1800
    assert level2["isShort"] is True  # Optional field provided
