from sqlalchemy import Enum
from aws_portal.extensions import db

from ..enums.sleep_enums import SleepLevelEnum


class SleepLevel(db.Model):
    """
    The sleep_level table mapping class.

    Represents detailed sleep stage data within a sleep log.

    Vars
    ----
    id: sqlalchemy.Column
    sleep_log_id: sqlalchemy.Column
    date_time: sqlalchemy.Column
    level: sqlalchemy.Column
        The sleep level entered. Valid values include:
        - Stages: "deep", "light", "rem", "wake"
        - Classic: "asleep", "restless", "awake"
    seconds: sqlalchemy.Column
        Duration in seconds for the sleep level.
    is_short: sqlalchemy.Column
        Indicates if the wake period is short (<= 3 minutes).
        Only applicable for stages sleep logs (nullable).
    """
    __tablename__ = "sleep_level"
    __table_args__ = (
        db.Index("idx_sleep_level_sleep_log_id_date_time",
                 "sleep_log_id", "date_time"),
    )

    id = db.Column(db.Integer, primary_key=True)
    sleep_log_id = db.Column(
        db.Integer,
        db.ForeignKey("sleep_log.id"),
        nullable=False
    )
    date_time = db.Column(db.DateTime, nullable=False, index=True)
    level = db.Column(Enum(SleepLevelEnum), nullable=False)
    seconds = db.Column(db.Integer, nullable=False)
    is_short = db.Column(db.Boolean, default=False, nullable=True)

    sleep_log = db.relationship("SleepLog", back_populates="levels")

    @property
    def meta(self):
        """
        dict: An entry's metadata.
        """
        return {
            "dateTime": self.date_time.isoformat(),
            "level": self.level.value,
            "seconds": self.seconds,
            "isShort": self.is_short
        }

    def __repr__(self):
        return f"<SleepLevel {self.level.value} at {self.date_time} for SleepLog {self.sleep_log_id}>"
