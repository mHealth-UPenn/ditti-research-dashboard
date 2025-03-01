from datetime import datetime, UTC, timedelta
import enum
import logging
import os
import uuid

from flask import current_app
from sqlalchemy import select, func, tuple_, event, Enum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from sqlalchemy.sql.schema import UniqueConstraint

from aws_portal.extensions import bcrypt, db, jwt
from aws_portal.rbac.api import with_rbac, with_rbac_study_permission
from aws_portal.rbac.models import (
    JoinAccountPermission,
    JoinAccountRole,
    JoinAccountStudy,
    JoinRolePermission,
    Permission,
    RBACAccountMixin,
    RBACStudyMixin,
    Role,
)


logger = logging.getLogger(__name__)


def init_db():
    """
    Create all database tables. This can only be run in a testing environment
    or if the database is hosted locally.

    Raises
    ------
    RuntimeError
        If this function is called outside of a testing environment or if the
        database URI does not contain "localhost."
    """
    db_uri = current_app.config["SQLALCHEMY_DATABASE_URI"]

    if "localhost" not in db_uri:
        raise RuntimeError("init_db requires a localhost database URI.")

    if current_app.config["TESTING"]:
        db.drop_all()
        db.create_all()

    else:
        db.create_all()


def init_admin_app():
    """
    Initialize the admin dashboard app database entry.

    Returns
    -------
    App

    Raises
    ------
    ValueError
        If an entry for the admin dashboard app already exists.
    """
    query = App.name == "Admin Dashboard"
    app = App.query.filter(query).first()

    if app is not None:
        raise ValueError("This app already exists: %s" % app)

    app = App(name="Admin Dashboard")
    db.session.add(app)
    db.session.commit()

    return app


def init_admin_account(email=None, password=None):
    """
    Initialize the admin account

    Args
    ----
    email: str (optional)
    password: str (optional)

    Returns
    -------
    Account

    Raises
    ------
    ValueError
        If an entry for the admin account already exists or if an entry for the
        admin access group does not exist.
    """
    email = email or os.getenv("FLASK_ADMIN_EMAIL")
    password = password or os.getenv("FLASK_ADMIN_PASSWORD")
    admin = Account.query.filter(Account.email == email).first()

    if admin is not None:
        raise ValueError("An admin account already exists: %s" % admin)

    admin = Account(
        public_id=str(uuid.uuid4()),
        created_on=datetime.now(UTC),
        first_name="AWS",
        last_name="Admin",
        email=email,
        is_confirmed=True
    )

    db.session.add(admin)
    db.session.commit()
    return admin


def init_api(click=None):
    """
    Insert Fitbit API entry.
    """
    api_name = "Fitbit"
    existing_api = Api.query.filter_by(name=api_name).first()

    if not existing_api:
        new_api = Api(name=api_name, is_archived=False)
        db.session.add(new_api)
        db.session.commit()
        message = f"<API {api_name}>"
    else:
        message = f"<API {api_name}> already exists with ID {existing_api.id}."

    if click:
        click.echo(message)


def init_lambda_task(status: str):
    db.session.add(LambdaTask(status=status))
    db.session.commit()


def delete_lambda_tasks():
    for task in LambdaTask.query.all():
        db.session.delete(task)
    db.session.commit()


def init_study_subject(ditti_id):
    db_uri = current_app.config["SQLALCHEMY_DATABASE_URI"]
    if "localhost" not in db_uri:
        raise RuntimeError(
            "init_study_subject requires a localhost database URI.")

    study_a = Study.query.get(1)
    study_b = Study.query.get(2)
    if study_a is None or study_b is None:
        raise RuntimeError("Could not retrieve studies from the database.")

    existing = StudySubject.query.filter(
        StudySubject.ditti_id == ditti_id).first()
    if existing is not None:
        raise RuntimeError(f"Study subject with ditti_id {
                           ditti_id} already exists.")

    study_subject = StudySubject(ditti_id=ditti_id)

    JoinStudySubjectStudy(
        study_subject=study_subject,
        study=study_b,
        did_consent=True,
        starts_on=datetime.now(UTC) - timedelta(days=7),
    )

    db.session.add(study_subject)
    db.session.commit()


@jwt.user_identity_loader
def user_identity_lookup(account):
    return account.public_id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return Account.query.filter(Account.public_id == identity).first()


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = BlockedToken.query.filter(BlockedToken.jti == jti).first()
    return token is not None


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


@with_rbac("email")
class Account(db.Model, RBACAccountMixin):
    """
    The account table mappeing class.

    Vars
    ----
    id: sqlalchemy.Column
    public_id: sqlalchemy.Column
        A random string to be used for JWT authentication, e.g.,
        `public_id=str(uuid.uuid4())`.
    created_on: sqlalchemy.Column
        The timestamp of the account"s creation, e.g., `datetime.now(UTC)`.
        The created_on value cannot be modified.
    last_login: sqlalchemy.Column
    first_name: sqlalchemy.Column
    last_name: sqlalchemy.Column
    email: sqlalchemy.Column
    phone_number: sqlalchemy.Column
    is_confirmed: sqlalchemy.Column
        Whether the account holder has logged in and set their password.
    is_archived: sqlalchemy.Column
    access_groups: sqlalchemy.orm.relationship
    studies: sqlalchemy.orm.relationship
    """
    __tablename__ = "account"
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String, nullable=False, unique=True)
    created_on = db.Column(db.DateTime, nullable=False)
    last_login = db.Column(db.DateTime)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    phone_number = db.Column(db.String, nullable=True, unique=True)
    is_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    _password = db.Column(db.String, nullable=False)

    @validates("created_on")
    def validate_created_on(self, key, val):
        """
        Make the created_on column read-only.
        """
        if self.created_on:
            raise ValueError("Account.created_on cannot be modified.")

        return val

    @hybrid_property
    def full_name(self):
        """
        str: The full name of the account holder
        """
        return f"{self.first_name} {self.last_name}"

    @full_name.expression
    def full_name(cls):
        return func.concat(cls.first_name, " ", cls.last_name)

    @hybrid_property
    def password(self):
        """
        str: The account holder"s password
        """
        return self._password

    @password.setter
    def password(self, val):
        """
        Hashes the password using bcrypt
        """
        password_hash = bcrypt.generate_password_hash(val).decode("utf-8")
        self._password = password_hash
        return True

    def check_password(self, val):
        """
        Whether a password matches the account holder"s password.

        Args
        ----
        val: str
            The password to check.

        Returns
        -------
        bool
        """
        return bcrypt.check_password_hash(self._password, val)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "createdOn": self.created_on,
            "lastLogin": self.last_login,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "email": self.email,
            "phoneNumber": self.phone_number,
            "isConfirmed": self.is_confirmed,
        }

    def __repr__(self):
        return "<Account %s>" % self.email


class App(db.Model):
    """
    The app table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    name: sqlalchemy.Column
    """
    __tablename__ = "app"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "name": self.name
        }

    def __repr__(self):
        return "<App %s>" % self.name


@with_rbac("acronym")
class Study(db.Model):
    """
    The study table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    name: sqlalchemy.Column
    acronym: sqlalchemy.Column
    ditti_id: sqlalchemy.Column
    email: sqlalchemy.Column
    default_expiry_delta: sqlalchemy.Column
        The default amount of time in number of days that a subject is enrolled
        in the study. A JoinStudySubjectStudy's expires_on column will be automatically set
        according to this value.
    consent_information: sqlalchemy.Column
        The consent text to show to a study subject.
    is_archived: sqlalchemy.Column
    data_summary: sqlalchemy.Column
        Text describing why we are collecting participants data.
    is_qi: sqlalchemy.Column
        Indicates if the study is QI (Quality Improvement), defaults to False.
    roles: sqlalchemy.orm.relationship
    """
    __tablename__ = "study"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    acronym = db.Column(db.String, nullable=False, unique=True)
    ditti_id = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    default_expiry_delta = db.Column(db.Integer, nullable=False)
    consent_information = db.Column(db.String)
    data_summary = db.Column(db.Text)
    is_qi = db.Column(db.Boolean, default=False, nullable=False)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "name": self.name,
            "acronym": self.acronym,
            "dittiId": self.ditti_id,
            "email": self.email,
            "defaultExpiryDelta": self.default_expiry_delta,
            "consentInformation": self.consent_information,
            "dataSummary": self.data_summary,
            "isQi": self.is_qi
        }

    def __repr__(self):
        return "<Study %s>" % self.acronym


class BlockedToken(db.Model):
    """
    The blocked_token table mapping class. This is used to log users out using
    JWT tokens.

    Vars
    ----
    id: sqlalchemy.Column
    jti: sqlalchemy.Column
        The token to block.
    created_on: sqlalchemy.Column
    """
    __tablename__ = "blocked_token"
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return "<BlockedToken %s>" % self.id


class AboutSleepTemplate(db.Model):
    """
    The about_sleep_template table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    name: sqlalchemy.Column
    text: sqlalchemy.Column
    is_archived: sqlalchemy.Column
    """
    __tablename__ = "about_sleep_template"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    text = db.Column(db.String, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "name": self.name,
            "text": self.text
        }

    def __repr__(self):
        return "<AboutSleepTemplate %s>" % self.name


@with_rbac_study_permission("GetParticipants")
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
            # "sleepLogs": [join.meta for join in self.sleep_logs]
        }

    def __repr__(self):
        return f"<StudySubject {self.ditti_id}>"


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
    starts_on: sqlalchemy.Column
        When data collection for a study subject begins. Data from approved APIs
        will be collected starting from no earlier than this date.
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
    starts_on = db.Column(db.DateTime, default=func.now(), nullable=False)
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
            "startsOn": self.starts_on.isoformat(),
            "expiresOn": self.expires_on.isoformat() if self.expires_on else None,
            "dataSummary": self.study.data_summary,
            "study": self.study.meta,
        }

    def __repr__(self):
        return f"<JoinStudySubjectStudy {self.study_subject_id}-{self.study_id}>"


@event.listens_for(JoinStudySubjectStudy, "before_insert")
def set_expires_on(mapper, connection, target):
    """
    Automatically set the expires_on field based on the Study's default_expiry_delta
    if expires_on is not provided.
    """
    if not target.expires_on:
        if target.study_id:
            # Use a raw SQL query to fetch default_expiry_delta
            stmt = select(Study.default_expiry_delta).where(
                Study.id == target.study_id
            )
            result = connection.execute(stmt).scalar_one_or_none()
            if result is not None:
                target.expires_on = datetime.now(UTC) + timedelta(days=result)
            else:
                raise ValueError(
                    f"Cannot set expires_on: Study with id {
                        target.study_id} not found or default_expiry_delta is missing."
                )
        else:
            raise ValueError("Cannot set expires_on: study_id is missing.")


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

    def __repr__(self):
        return "<JoinStudySubjectApi %s-%s>" % self.primary_key


class Api(db.Model):
    """
    The api table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    name: sqlalchemy.Column
    is_archived: sqlalchemy.Column
    """
    __tablename__ = "api"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "name": self.name
        }

    def __repr__(self):
        return "<Api %s>" % self.name


@with_rbac_study_permission("GetSleepLogs")
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
            "totalMinutesAsleep": self.minutes_asleep,
            "sleepEfficiencyPercentage": self.efficiency,
            "levels": [level.meta for level in self.levels],
            "summaries": [summary.meta for summary in self.summaries]
        }

    def __repr__(self):
        return f"<SleepLog {self.log_id} for StudySubject {self.study_subject_id}>"


@with_rbac_study_permission("GetSleepLevels")
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


@with_rbac_study_permission("GetSleepSummaries")
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


class LambdaTask(db.Model):
    """
    The lambda_task table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    status: sqlalchemy.Column
        The status of the task ("Pending", "InProgress", "Success", "Failed", "CompletedWithErrors").
    billed_ms: sqlalchemy.Column
        The billed duration of the Lambda function in milliseconds.
    created_on: sqlalchemy.Column
    updated_on: sqlalchemy.Column
    completed_on: sqlalchemy.Column
        The datetime when the task was completed.
    log_file: sqlalchemy.Column
        S3 URI location of log file.
    error_code: sqlalchemy.Column
        Error code if any.
    """
    __tablename__ = "lambda_task"
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(
        db.Enum(
            "Pending", "InProgress", "Success", "Failed", "CompletedWithErrors",
            name="taskstatustypeenum"
        ), nullable=False
    )
    billed_ms = db.Column(db.Integer, nullable=True)
    created_on = db.Column(
        db.DateTime,
        default=func.now(),
        nullable=False,
        index=True
    )
    updated_on = db.Column(
        db.DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    completed_on = db.Column(db.DateTime, nullable=True)
    log_file = db.Column(db.String, nullable=True)
    error_code = db.Column(db.String, nullable=True)

    @property
    def meta(self):
        return {
            "id": self.id,
            "status": self.status,
            "billedMs": self.billed_ms,
            "createdOn": self.created_on.isoformat(),
            "updatedOn": self.updated_on.isoformat(),
            "completedOn": self.completed_on.isoformat() if self.completed_on else None,
            "logFile": self.log_file,
            "errorCode": self.error_code
        }

    def __repr__(self):
        return f"<LambdaTask {self.id}>"
