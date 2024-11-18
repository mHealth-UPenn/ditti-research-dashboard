from datetime import datetime, UTC
from sqlalchemy import func, tuple_
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from aws_portal.extensions import db


class JoinStudyRole(db.Model):
    """
    The join_study_role table mapping class.

    Vars
    ----
    study_id: sqlalchemy.Column
    role_id: sqlalchemy.Column
    study: sqlalchemy.orm.relationship
    role: sqlalchemy.orm.relationship
    """
    __tablename__ = "join_study_role"

    study_id = db.Column(
        db.Integer,
        db.ForeignKey("study.id"),
        primary_key=True
    )

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("role.id", ondelete="CASCADE"),
        primary_key=True
    )

    study = db.relationship("Study", back_populates="roles")
    role = db.relationship("Role")

    @hybrid_property
    def primary_key(self):
        """
        tuple of int: an entry's primary key.
        """
        return self.study_id, self.role_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.study_id, cls.role_id)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return self.role.meta

    def __repr__(self):
        return f"<JoinStudyRole {self.study_id}-{self.role_id}>"


class JoinStudySubjectStudy(db.Model):
    """
    The join_study_subject_study table mapping class.

    Vars
    ----
    study_subject_id: sqlalchemy.Column
    study_id: sqlalchemy.Column
    did_consent: sqlalchemy.Column
        Whether the study subject consented to the collection of their data
    created_on: sqlalchemy.Column
        The timestamp of the account's creation, e.g., `datetime.now(UTC)`.
        The created_on value cannot be modified.
    expires_on: sqlalchemy.Column
        When the study subject is no longer a part of the study and data should no
        longer be collected from any of the subject's approved APIs
    study_subject: sqlalchemy.orm.relationship
    study: sqlalchemy.orm.relationship
    """
    __tablename__ = "join_study_subject_study"

    study_subject_id = db.Column(
        db.Integer,
        db.ForeignKey("study_subject.id", ondelete="CASCADE"),
        primary_key=True
    )
    study_id = db.Column(
        db.Integer,
        db.ForeignKey("study.id"),  # Do not allow deletions on study table
        primary_key=True
    )
    did_consent = db.Column(db.Boolean, default=False, nullable=False)
    created_on = db.Column(db.DateTime, default=func.now(), nullable=False)
    expires_on = db.Column(db.DateTime, nullable=True)

    study_subject = db.relationship("StudySubject", back_populates="studies")
    study = db.relationship("Study")

    @validates("created_on")
    def validate_created_on(self, key, val):
        """
        Make the created_on column read-only.
        """
        if self.created_on:
            raise ValueError(
                "JoinStudySubjectApi.created_on cannot be modified.")
        return val

    @validates("expires_on")
    def validate_expires_on(self, key, value):
        if value and value <= datetime.now(UTC):
            raise ValueError("expires_on must be a future date.")
        return value

    @hybrid_property
    def primary_key(self):
        """
        tuple of int: an entry's primary key.
        """
        return self.study_subject_id, self.study_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.study_subject_id, cls.study_id)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "didConsent": self.did_consent,
            "createdOn": self.created_on.isoformat(),
            "expiresOn": self.expires_on.isoformat() if self.expires_on else None,
            "study": self.study.meta,
        }

    def __repr__(self):
        return f"<JoinStudySubjectStudy {self.study_subject_id}-{self.study_id}>"


class JoinStudySubjectApi(db.Model):
    """
    The join_study_subject_api table mapping class.

    Vars
    ----
    study_subject_id: sqlalchemy.Column
    api_id: sqlalchemy.Column
    api_user_uuid: sqlalchemy.Column
        The study subject's user ID associated with the API.
    scope: sqlalchemy.Column
        The scope of data that the study subject approved access for.
    last_sync_date: sqlalchemy.Column
        The last date sleep data was synchronized.
    created_on: sqlalchemy.Column
        The timestamp of the account's creation, e.g., `datetime.now(UTC)`.
        The created_on value cannot be modified.
    study_subject: sqlalchemy.orm.relationship
    api: sqlalchemy.orm.relationship
    """
    __tablename__ = "join_study_subject_api"

    study_subject_id = db.Column(
        db.Integer,
        db.ForeignKey("study_subject.id", ondelete="CASCADE"),
        primary_key=True
    )

    api_id = db.Column(
        db.Integer,
        db.ForeignKey("api.id"),
        primary_key=True
    )

    api_user_uuid = db.Column(db.String, nullable=False)
    scope = db.Column(db.ARRAY(db.String))
    last_sync_date = db.Column(db.Date, nullable=True)
    created_on = db.Column(db.DateTime, default=func.now(), nullable=False)

    study_subject = db.relationship("StudySubject", back_populates="apis")
    api = db.relationship("Api")

    @validates("created_on")
    def validate_created_on(self, key, val):
        """
        Make the created_on column read-only.
        """
        if self.created_on:
            raise ValueError(
                "JoinStudySubjectApi.created_on cannot be modified.")
        return val

    @hybrid_property
    def primary_key(self):
        """
        tuple of int: an entry's primary key.
        """
        return self.study_subject_id, self.api_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.study_subject_id, cls.api_id)

    @property
    def meta(self):
        """
        dict: An entry's metadata.
        """
        return {
            "apiUserUuid": self.api_user_uuid,
            "scope": self.scope,
            "api": self.api.meta,
            "lastSyncDate": self.last_sync_date.isoformat() if self.last_sync_date else None,
            "createdOn": self.created_on.isoformat()
        }

    def __repr__(self):
        return f"<JoinStudySubjectApi StudySubject {self.study_subject_id} - Api {self.api_id}>"
