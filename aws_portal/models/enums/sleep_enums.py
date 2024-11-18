import enum


class SleepLevelEnum(enum.Enum):
    wake = "wake"
    light = "light"
    deep = "deep"
    rem = "rem"
    asleep = "asleep"
    awake = "awake"
    restless = "restless"


class SleepLogTypeEnum(enum.Enum):
    auto_detected = "auto_detected"
    manual = "manual"


class SleepCategoryTypeEnum(enum.Enum):
    stages = "stages"
    classic = "classic"
