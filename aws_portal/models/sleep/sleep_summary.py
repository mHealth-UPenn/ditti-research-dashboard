from sqlalchemy import Enum
from aws_portal.extensions import db

from .sleep_log import SleepLog
from ..enums.sleep_enums import SleepLevelEnum


class SleepSummary(db.Model):
    """
    The sleep_summary table mapping class.

    Represents summary data of sleep levels within a sleep log.

    Vars
    ----
    id: sqlalchemy.Column
    sleep_log_id: sqlalchemy.Column
    level: sqlalchemy.Column
        The sleep level. Valid values include:
        - Stages: "deep", "light", "rem", "wake"
        - Classic: "asleep", "restless", "awake"
    count: sqlalchemy.Column
        Total number of times the user entered the sleep level.
    minutes: sqlalchemy.Column
        Total number of minutes the user appeared in the sleep level.
    thirty_day_avg_minutes: sqlalchemy.Column
        Average sleep stage time over the past 30 days.
        Only applicable for stages sleep logs (nullable).
    """
    __tablename__ = "sleep_summary"

    id = db.Column(db.Integer, primary_key=True)
    sleep_log_id = db.Column(
        db.Integer,
        db.ForeignKey("sleep_log.id"),
        nullable=False
    )
    level = db.Column(Enum(SleepLevelEnum), nullable=False)
    count = db.Column(db.Integer)
    minutes = db.Column(db.Integer)
    thirty_day_avg_minutes = db.Column(db.Integer, nullable=True)

    sleep_log = db.relationship("SleepLog", back_populates="summaries")

    @property
    def meta(self):
        """
        dict: An entry's metadata.
        """
        return {
            "level": self.level.value,
            "count": self.count,
            "minutes": self.minutes,
            "thirtyDayAvgMinutes": self.thirty_day_avg_minutes,
        }

    def __repr__(self):
        return f"<SleepSummary {self.level.value} for SleepLog {self.sleep_log_id}>"
