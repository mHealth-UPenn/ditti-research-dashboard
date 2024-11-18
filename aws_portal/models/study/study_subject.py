from sqlalchemy import func
from aws_portal.extensions import db


class StudySubject(db.Model):
    """
    The study_subject table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    created_on: sqlalchemy.Column
    ditti_id: sqlalchemy.Column
        The study subject's Cognito username (unique identifier).
    is_archived: sqlalchemy.Column
    studies: sqlalchemy.orm.relationship
        Studies the subject is enrolled in.
    apis: sqlalchemy.orm.relationship
        APIs that the subject has granted access to.
    sleep_logs: sqlalchemy.orm.relationship
        Sleep logs associated with the study subject.
    """
    __tablename__ = "study_subject"
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, default=func.now(), nullable=False)
    ditti_id = db.Column(db.String, nullable=False, unique=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    # Ignore archived studies
    studies = db.relationship(
        "JoinStudySubjectStudy",
        back_populates="study_subject",
        cascade="all, delete-orphan",
        primaryjoin=(
            "and_("
            "   StudySubject.id == JoinStudySubjectStudy.study_subject_id,"
            "   JoinStudySubjectStudy.study_id == Study.id,"
            "   Study.is_archived == False"
            ")"
        )
    )

    # Ignore archived apis
    apis = db.relationship(
        "JoinStudySubjectApi",
        back_populates="study_subject",
        cascade="all, delete-orphan",
        primaryjoin=(
            "and_("
            "   StudySubject.id == JoinStudySubjectApi.study_subject_id,"
            "   JoinStudySubjectApi.api_id == Api.id,"
            "   Api.is_archived == False"
            ")"
        )
    )

    sleep_logs = db.relationship(
        "SleepLog",
        back_populates="study_subject",
        cascade="all, delete-orphan",
        lazy="dynamic"  # Use dynamic loading for large datasets
    )

    @property
    def meta(self):
        return {
            "id": self.id,
            "createdOn": self.created_on.isoformat(),
            "dittiId": self.ditti_id,
            "studies": [join.meta for join in self.studies],
            "apis": [join.meta for join in self.apis],
            "sleepLogs": [join.meta for join in self.sleep_logs]
        }

    def __repr__(self):
        return f"<StudySubject {self.ditti_id}>"
