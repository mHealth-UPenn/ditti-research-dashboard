import pytest
from datetime import datetime, date
from typing import List
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
    def __init__(self, date_time: datetime, level: SleepLevelEnum, seconds: int, is_short: bool = False):
        self.date_time = date_time
        self.level = level
        self.seconds = seconds
        self.is_short = is_short


class MockSleepLog:
    def __init__(
        self,
        log_id: int,
        date_of_sleep: date,
        start_time: datetime,
        end_time: datetime,
        log_type: SleepLogTypeEnum,
        sleep_type: SleepCategoryTypeEnum,
        levels: List[MockSleepLevel],
        duration: int = 28800000,  # 8 hours in milliseconds
        efficiency: int = 85,
        info_code: int = 0,
        is_main_sleep: bool = True,
        minutes_after_wakeup: int = 30,
        minutes_asleep: int = 450,
        minutes_awake: int = 30,
        minutes_to_fall_asleep: int = 15,
        time_in_bed: int = 480
    ):
        self.id = log_id
        self.log_id = log_id
        self.date_of_sleep = date_of_sleep
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.efficiency = efficiency
        self.info_code = info_code
        self.is_main_sleep = is_main_sleep
        self.minutes_after_wakeup = minutes_after_wakeup
        self.minutes_asleep = minutes_asleep
        self.minutes_awake = minutes_awake
        self.minutes_to_fall_asleep = minutes_to_fall_asleep
        self.log_type = log_type
        self.time_in_bed = time_in_bed
        self.type = sleep_type
        self.levels = levels
        self.summaries = []  # Empty for simplicity

# ----------------------------
# Fixtures for Sample Data
# ----------------------------


@pytest.fixture
def sample_sleep_logs(app):
    # SleepLog 1: Stages type
    levels_stages = [
        MockSleepLevel(datetime(2024, 4, 20, 23, 0, 0),
                       SleepLevelEnum.deep, 1800),
        MockSleepLevel(datetime(2024, 4, 20, 23, 30, 0),
                       SleepLevelEnum.light, 2700),
        MockSleepLevel(datetime(2024, 4, 21, 0, 15, 0),
                       SleepLevelEnum.rem, 1800),
        MockSleepLevel(datetime(2024, 4, 21, 0, 45, 0),
                       SleepLevelEnum.wake, 600),
    ]
    sleep_log1 = MockSleepLog(
        log_id=123456789,
        date_of_sleep=date(2024, 4, 21),
        start_time=datetime(2024, 4, 20, 23, 0, 0),
        end_time=datetime(2024, 4, 21, 7, 0, 0),
        log_type=SleepLogTypeEnum.auto_detected,
        sleep_type=SleepCategoryTypeEnum.stages,
        levels=levels_stages
    )

    # SleepLog 2: Classic type with some None fields
    levels_classic = [
        MockSleepLevel(datetime(2024, 4, 19, 22, 30, 0),
                       SleepLevelEnum.asleep, 3600),
        MockSleepLevel(datetime(2024, 4, 19, 23, 30, 0),
                       SleepLevelEnum.awake, 900),
        MockSleepLevel(datetime(2024, 4, 19, 23, 45, 0),
                       SleepLevelEnum.asleep, 1800),
    ]
    sleep_log2 = MockSleepLog(
        log_id=987654321,
        date_of_sleep=date(2024, 4, 20),
        start_time=datetime(2024, 4, 19, 22, 30, 0),
        end_time=None,  # end_time is None
        log_type=SleepLogTypeEnum.manual,
        sleep_type=SleepCategoryTypeEnum.classic,
        levels=levels_classic
    )

    return [sleep_log1, sleep_log2]

# ----------------------------
# Unit Tests
# ----------------------------


def test_serialize_fitbit_data(app, sample_sleep_logs):
    serialized = serialize_fitbit_data(sample_sleep_logs)

    assert isinstance(serialized, list)
    assert len(serialized) == 2

    # Test first SleepLog (Stages)
    log1_serialized = serialized[0]
    assert log1_serialized["id"] == 123456789
    assert log1_serialized["logId"] == 123456789
    assert log1_serialized["dateOfSleep"] == "2024-04-21"
    assert log1_serialized["startTime"] == "2024-04-20T23:00:00"
    assert log1_serialized["endTime"] == "2024-04-21T07:00:00"
    assert log1_serialized["duration"] == 28800000
    assert log1_serialized["efficiency"] == 85
    assert log1_serialized["infoCode"] == 0
    assert log1_serialized["isMainSleep"] is True
    assert log1_serialized["minutesAfterWakeup"] == 30
    assert log1_serialized["minutesAsleep"] == 450
    assert log1_serialized["minutesAwake"] == 30
    assert log1_serialized["minutesToFallAsleep"] == 15
    assert log1_serialized["logType"] == "auto_detected"
    assert log1_serialized["timeInBed"] == 480
    assert log1_serialized["type"] == "stages"

    # Check levels
    assert len(log1_serialized["levels"]) == 4
    assert log1_serialized["levels"][0]["dateTime"] == "2024-04-20T23:00:00"
    assert log1_serialized["levels"][0]["level"] == "deep"
    assert log1_serialized["levels"][0]["seconds"] == 1800
    assert log1_serialized["levels"][0].get("isShort") is False

    assert log1_serialized["levels"][3]["level"] == "wake"
    assert log1_serialized["levels"][3]["seconds"] == 600
    assert log1_serialized["levels"][3]["isShort"] is False

    # Test second SleepLog (Classic)
    log2_serialized = serialized[1]
    assert log2_serialized["id"] == 987654321
    assert log2_serialized["logId"] == 987654321
    assert log2_serialized["dateOfSleep"] == "2024-04-20"
    assert log2_serialized["startTime"] == "2024-04-19T22:30:00"
    assert log2_serialized["endTime"] is None
    assert log2_serialized["duration"] == 28800000
    assert log2_serialized["efficiency"] == 85
    assert log2_serialized["infoCode"] == 0
    assert log2_serialized["isMainSleep"] is True
    assert log2_serialized["minutesAfterWakeup"] == 30
    assert log2_serialized["minutesAsleep"] == 450
    assert log2_serialized["minutesAwake"] == 30
    assert log2_serialized["minutesToFallAsleep"] == 15
    assert log2_serialized["logType"] == "manual"
    assert log2_serialized["timeInBed"] == 480
    assert log2_serialized["type"] == "classic"

    # Check levels
    assert len(log2_serialized["levels"]) == 3
    assert log2_serialized["levels"][0]["dateTime"] == "2024-04-19T22:30:00"
    assert log2_serialized["levels"][0]["level"] == "asleep"
    assert log2_serialized["levels"][0]["seconds"] == 3600
    assert log2_serialized["levels"][0].get("isShort") is False

    assert log2_serialized["levels"][1]["level"] == "awake"
    assert log2_serialized["levels"][1]["seconds"] == 900
    assert log2_serialized["levels"][1].get("isShort") is False


def test_serialize_fitbit_data_empty(app):
    # Test serialization with empty input
    serialized = serialize_fitbit_data([])
    assert serialized == []


def test_serialize_fitbit_data_missing_fields(app):
    # Create a SleepLog with some fields set to None
    sleep_log = MockSleepLog(
        log_id=111222333,
        date_of_sleep=date(2024, 5, 1),
        start_time=datetime(2024, 4, 30, 23, 0, 0),
        end_time=None,
        log_type=SleepLogTypeEnum.auto_detected,
        sleep_type=SleepCategoryTypeEnum.stages,
        levels=[]
    )
    # Override some fields to None
    sleep_log.duration = None
    sleep_log.efficiency = None
    sleep_log.info_code = None
    sleep_log.is_main_sleep = None
    sleep_log.minutes_after_wakeup = None
    sleep_log.minutes_asleep = None
    sleep_log.minutes_awake = None
    sleep_log.minutes_to_fall_asleep = None
    sleep_log.time_in_bed = None

    serialized = serialize_fitbit_data([sleep_log])

    assert len(serialized) == 1
    log_serialized = serialized[0]
    assert log_serialized["id"] == 111222333
    assert log_serialized["logId"] == 111222333
    assert log_serialized["dateOfSleep"] == "2024-05-01"
    assert log_serialized["startTime"] == "2024-04-30T23:00:00"
    assert log_serialized["endTime"] is None
    assert log_serialized.get("duration") is None
    assert log_serialized.get("efficiency") is None
    assert log_serialized.get("infoCode") is None
    assert log_serialized.get("isMainSleep") is None
    assert log_serialized.get("minutesAfterWakeup") is None
    assert log_serialized.get("minutesAsleep") is None
    assert log_serialized.get("minutesAwake") is None
    assert log_serialized.get("minutesToFallAsleep") is None
    assert log_serialized["logType"] == "auto_detected"
    assert log_serialized.get("timeInBed") is None
    assert log_serialized["type"] == "stages"
    assert log_serialized["levels"] == []


def test_serialize_fitbit_data_invalid_enum(app):
    # Create a SleepLog with invalid enum values
    sleep_log = MockSleepLog(
        log_id=444555666,
        date_of_sleep=date(2024, 6, 1),
        start_time=datetime(2024, 5, 31, 22, 0, 0),
        end_time=datetime(2024, 6, 1, 6, 0, 0),
        log_type="invalid_type",  # Invalid enum
        sleep_type="invalid_category",  # Invalid enum
        levels=[]
    )

    with pytest.raises(ValueError):
        serialize_fitbit_data([sleep_log])


def test_serialize_fitbit_data_partial_levels(app):
    # Create a SleepLog with some levels missing optional fields
    levels_partial = [
        MockSleepLevel(datetime(2024, 7, 1, 23, 0, 0),
                       SleepLevelEnum.rem, 1200),
        MockSleepLevel(datetime(2024, 7, 1, 23, 20, 0),
                       SleepLevelEnum.deep, 1800, is_short=True),
    ]
    sleep_log = MockSleepLog(
        log_id=555666777,
        date_of_sleep=date(2024, 7, 2),
        start_time=datetime(2024, 7, 1, 23, 0, 0),
        end_time=datetime(2024, 7, 2, 7, 0, 0),
        log_type=SleepLogTypeEnum.auto_detected,
        sleep_type=SleepCategoryTypeEnum.stages,
        levels=levels_partial
    )

    serialized = serialize_fitbit_data([sleep_log])

    assert len(serialized) == 1
    log_serialized = serialized[0]
    assert log_serialized["id"] == 555666777
    assert log_serialized["logId"] == 555666777
    assert log_serialized["dateOfSleep"] == "2024-07-02"
    assert log_serialized["startTime"] == "2024-07-01T23:00:00"
    assert log_serialized["endTime"] == "2024-07-02T07:00:00"
    assert log_serialized["logType"] == "auto_detected"
    assert log_serialized["type"] == "stages"

    # Check levels
    assert len(log_serialized["levels"]) == 2

    level1 = log_serialized["levels"][0]
    assert level1["dateTime"] == "2024-07-01T23:00:00"
    assert level1["level"] == "rem"
    assert level1["seconds"] == 1200
    assert level1.get("isShort") is False  # Default value

    level2 = log_serialized["levels"][1]
    assert level2["dateTime"] == "2024-07-01T23:20:00"
    assert level2["level"] == "deep"
    assert level2["seconds"] == 1800
    assert level2["isShort"] is True
