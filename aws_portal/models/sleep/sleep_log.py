from sqlalchemy import Enum
from sqlalchemy.orm import validates
from aws_portal.extensions import db

from ..enums.sleep_enums import SleepLogTypeEnum, SleepCategoryTypeEnum


class SleepLog(db.Model):
    """
    The sleep_log table mapping class.

    Represents an individual sleep log entry for a study subject.
    Supports both 'stages' and 'classic' sleep logs.

    Vars
    ----
    id: sqlalchemy.Column
    study_subject_id: sqlalchemy.Column
    log_id: sqlalchemy.Column
        Fitbit's unique log ID.
    date_of_sleep: sqlalchemy.Column
        The date the sleep log ended.
    duration: sqlalchemy.Column
        Length of sleep in milliseconds.
    efficiency: sqlalchemy.Column
        Calculated sleep efficiency score provided by the API.
    end_time: sqlalchemy.Column
        Timestamp when sleep ended.
    info_code: sqlalchemy.Column
        Quality of data collected within the sleep log.
    is_main_sleep: sqlalchemy.Column
        Indicates if this is the main sleep log.
    minutes_after_wakeup: sqlalchemy.Column
    minutes_asleep: sqlalchemy.Column
    minutes_awake: sqlalchemy.Column
    minutes_to_fall_asleep: sqlalchemy.Column
    log_type: sqlalchemy.Column
        Type of sleep log (e.g., "auto_detected", "manual").
    start_time: sqlalchemy.Column
        Timestamp when sleep began.
    time_in_bed: sqlalchemy.Column
        Total number of minutes in bed.
    type: sqlalchemy.Column
        Type of sleep log ("stages" or "classic").
    """
    __tablename__ = "sleep_log"

    id = db.Column(db.Integer, primary_key=True)
    study_subject_id = db.Column(
        db.Integer,
        db.ForeignKey("study_subject.id"),
        nullable=False,
        index=True
    )

    log_id = db.Column(db.BigInteger, nullable=False, unique=True, index=True)
    date_of_sleep = db.Column(db.Date, nullable=False, index=True)
    duration = db.Column(db.Integer)
    efficiency = db.Column(db.Integer)
    end_time = db.Column(db.DateTime)
    info_code = db.Column(db.Integer)
    is_main_sleep = db.Column(db.Boolean)
    minutes_after_wakeup = db.Column(db.Integer)
    minutes_asleep = db.Column(db.Integer)
    minutes_awake = db.Column(db.Integer)
    minutes_to_fall_asleep = db.Column(db.Integer)
    log_type = db.Column(Enum(SleepLogTypeEnum), nullable=False)
    start_time = db.Column(db.DateTime)
    time_in_bed = db.Column(db.Integer)
    type = db.Column(Enum(SleepCategoryTypeEnum), nullable=False)

    study_subject = db.relationship(
        "StudySubject",
        back_populates="sleep_logs"
    )
    levels = db.relationship(
        "SleepLevel",
        back_populates="sleep_log",
        cascade="all, delete-orphan",
        lazy="selectin"  # Efficient loading of related objects
    )
    summaries = db.relationship(
        "SleepSummary",
        back_populates="sleep_log",
        cascade="all, delete-orphan",
        lazy="joined"  # Eagerly load summaries
    )

    @validates("efficiency")
    def validate_efficiency(self, key, value):
        if value is not None and not (0 <= value <= 100):
            raise ValueError("Efficiency must be between 0 and 100.")
        return value

    @property
    def meta(self):
        """
        dict: An entry's metadata.
        """
        return {
            "id": self.id,
            "studySubjectId": self.study_subject_id,
            "logId": self.log_id,
            "dateOfSleep": self.date_of_sleep.isoformat(),
            "duration": self.duration,
            "efficiency": self.efficiency,
            "endTime": self.end_time.isoformat() if self.end_time else None,
            "infoCode": self.info_code,
            "isMainSleep": self.is_main_sleep,
            "minutesAfterWakeup": self.minutes_after_wakeup,
            "minutesAsleep": self.minutes_asleep,
            "minutesAwake": self.minutes_awake,
            "minutesToFallAsleep": self.minutes_to_fall_asleep,
            "logType": self.log_type.value,
            "startTime": self.start_time.isoformat() if self.start_time else None,
            "timeInBed": self.time_in_bed,
            "type": self.type.value,
            "totalMinutesAsleep": self.total_minutes_asleep,
            "sleepEfficiencyPercentage": self.sleep_efficiency_percentage,
            "levels": [level.meta for level in self.levels],
            "summaries": [summary.meta for summary in self.summaries]
        }

    def __repr__(self):
        return f"<SleepLog {self.log_id} for StudySubject {self.study_subject_id}>"
