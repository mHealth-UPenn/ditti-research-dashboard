# Ditti Research Dashboard
# Copyright (C) 2025 the Trustees of the University of Pennsylvania
#
# Ditti Research Dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Ditti Research Dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import enum
import logging
import os
import re
from datetime import UTC, datetime, timedelta

from flask import current_app
from sqlalchemy import Enum, event, func, select, tuple_
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from sqlalchemy.sql.schema import UniqueConstraint

from backend.extensions import db

logger = logging.getLogger(__name__)


def init_db():
    """
    Create all database tables.

    This can only be run in a testing environment or
    if the database is hosted locally.

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
        raise ValueError(f"This app already exists: {app}")

    app = App(name="Admin Dashboard")
    db.session.add(app)
    db.session.commit()

    return app


def init_admin_group():
    """
    Initialize the admin access group.

    Returns
    -------
    AccessGroup

    Raises
    ------
    ValueError
        If an entry for the admin access group already exists or if an entry
        for the admin dashboard app does not exist.
    """
    query = AccessGroup.name == "Admin"
    access_group = AccessGroup.query.filter(query).first()

    if access_group is not None:
        raise ValueError(f"This access group already exists: {access_group}")

    query = App.name == "Admin Dashboard"
    app = App.query.filter(query).first()

    if app is None:
        raise ValueError(
            "The admin dashboard app has not been created. It can be created u"
            + "sing `flask init-admin-app`"
        )

    access_group = AccessGroup(name="Admin", app=app)
    permission = Permission()
    permission.action = "*"
    permission.resource = "*"
    join = JoinAccessGroupPermission(
        access_group=access_group, permission=permission
    )

    db.session.add(permission)
    db.session.add(access_group)
    db.session.add(join)
    db.session.commit()

    return access_group


def init_admin_account(email=None):
    """
    Initialize the admin account.

    Args
    ----
    email: str (optional)

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
    admin = Account.query.filter(Account.email == email).first()

    if admin is not None:
        raise ValueError(f"An admin account already exists: {admin}")

    query = AccessGroup.name == "Admin"
    admin_group = AccessGroup.query.filter(query).first()

    if admin_group is None:
        raise ValueError(
            "The admin access group has not been created. It can be created us"
            + "ing `flask init-access-group`"
        )

    query = AccessGroup.name == "Ditti Admin"
    ditti_group = AccessGroup.query.filter(query).first()

    admin = Account(
        created_on=datetime.now(UTC),
        first_name="AWS",
        last_name="Admin",
        email=email,
        is_confirmed=True,
    )

    db.session.commit()
    admin_join = JoinAccountAccessGroup(account=admin, access_group=admin_group)
    db.session.add(admin_join)

    # if an entry for the Ditti Admin group exists
    if ditti_group is not None:
        # add the admin account to it
        ditti_join = JoinAccountAccessGroup(
            account=admin, access_group=ditti_group
        )
        db.session.add(ditti_join)

    db.session.add(admin)
    db.session.commit()

    return admin


def init_api(click=None):
    """Insert Fitbit API entry."""
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


def init_integration_testing_db():
    """
    Initialize the database for integration testing.

    Creates necessary tables and populates the database with test data.
    Enforces that the environment must be pointing at a local database.
    """
    # Enforce that the environment must be pointing at a local database
    db_uri = current_app.config["SQLALCHEMY_DATABASE_URI"]
    if "localhost" not in db_uri:
        raise RuntimeError(
            "Dev data initialization attempted on non-localhost database"
        )

    # Create all possible `(action, resource)` permission combinations
    actions = ["*", "Create", "View", "Edit", "Archive", "Delete", "Invoke"]
    resources = [
        "*",
        "Admin Dashboard",
        "Ditti App Dashboard",
        "Wearable Dashboard",
        "Accounts",
        "Access Groups",
        "Roles",
        "Studies",
        "All Studies",
        "About Sleep Templates",
        "Audio Files",
        "Participants",
        "Taps",
        "Wearable Data",
        "Data Retrieval Task",
    ]

    for action in actions:
        for resource in resources:
            permission = Permission()
            permission.action = action
            permission.resource = resource
            db.session.add(permission)

    roles = {
        "Admin": [
            ("*", "*"),
        ],
        "Coordinator": [
            ("View", "*"),
            ("Create", "Participants"),
            ("Edit", "Participants"),
        ],
        "Analyst": [
            ("View", "*"),
        ],
        "Can View Participants": [("View", "Participants")],
        "Can Create Participants": [("Create", "Participants")],
        "Can Edit Participants": [("Edit", "Participants")],
        "Can View Taps": [("View", "Taps")],
        "Can View Wearable Data": [("View", "Wearable Data")],
        "Can View Taps & Wearable Data": [
            ("View", "Taps"),
            ("View", "Wearable Data"),
        ],
        "Can Invoke Data Retrieval Task": [
            ("View", "Wearable Data"),
            ("View", "Data Retrieval Task"),
            ("Invoke", "Data Retrieval Task"),
        ],
    }

    # Create all study-level roles
    for role_name, permissions in roles.items():
        role = Role(name=role_name)
        for action, resource in permissions:
            query = Permission.definition == tuple_(action, resource)
            permission = Permission.query.filter(query).first()
            JoinRolePermission(role=role, permission=permission)
        db.session.add(role)

    # Create the Admin access group
    admin_app = App(name="Admin Dashboard")
    admin_group = AccessGroup(name="Admin", app=admin_app)
    query = Permission.definition == tuple_("*", "*")
    wildcard = Permission.query.filter(query).first()
    JoinAccessGroupPermission(access_group=admin_group, permission=wildcard)
    db.session.add(admin_app)
    db.session.add(admin_group)

    # Create the Ditti Admin access group
    ditti_app = App(name="Ditti App Dashboard")
    ditti_admin_group = AccessGroup(name="Ditti App Admin", app=ditti_app)
    JoinAccessGroupPermission(access_group=ditti_admin_group, permission=wildcard)
    query = Permission.definition == tuple_("View", "Ditti App Dashboard")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(
        access_group=ditti_admin_group, permission=permission
    )
    db.session.add(ditti_app)
    db.session.add(ditti_admin_group)

    # Create the Ditti Coordinator access group
    ditti_coordinator_group = AccessGroup(
        name="Ditti App Coordinator", app=ditti_app
    )
    query = Permission.definition == tuple_("View", "Ditti App Dashboard")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(
        access_group=ditti_coordinator_group, permission=permission
    )
    query = Permission.definition == tuple_("View", "Audio Files")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(
        access_group=ditti_coordinator_group, permission=permission
    )
    query = Permission.definition == tuple_("Create", "Audio Files")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(
        access_group=ditti_coordinator_group, permission=permission
    )
    query = Permission.definition == tuple_("Delete", "Audio Files")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(
        access_group=ditti_coordinator_group, permission=permission
    )
    query = Permission.definition == tuple_("View", "Participants")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(
        access_group=ditti_coordinator_group, permission=permission
    )
    db.session.add(ditti_app)
    db.session.add(ditti_coordinator_group)

    # Create the Wearable Admin access group
    wear_app = App(name="Wearable Dashboard")
    wear_admin_group = AccessGroup(name="Wearable Dashboard Admin", app=wear_app)
    JoinAccessGroupPermission(access_group=wear_admin_group, permission=wildcard)
    query = Permission.definition == tuple_("View", "Wearable Dashboard")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(
        access_group=wear_admin_group, permission=permission
    )
    db.session.add(wear_app)
    db.session.add(wear_admin_group)

    # Create the Wearable Dashboard Coordinator access group
    wear_coordinator_group = AccessGroup(
        name="Wearable Dashboard Coordinator", app=wear_app
    )
    query = Permission.definition == tuple_("View", "Wearable Dashboard")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(
        access_group=wear_coordinator_group, permission=permission
    )
    query = Permission.definition == tuple_("View", "Participants")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(
        access_group=wear_coordinator_group, permission=permission
    )
    db.session.add(wear_coordinator_group)

    admin_access_groups = {
        "Can Create Accounts": [
            ("View", "Admin Dashboard"),
            ("Create", "Accounts"),
        ],
        "Can Edit Accounts": [
            ("View", "Admin Dashboard"),
            ("Edit", "Accounts"),
        ],
        "Can Archive Accounts": [
            ("View", "Admin Dashboard"),
            ("Archive", "Accounts"),
        ],
        "Can Create Access Groups": [
            ("View", "Admin Dashboard"),
            ("Create", "Access Groups"),
        ],
        "Can Edit Access Groups": [
            ("View", "Admin Dashboard"),
            ("Edit", "Access Groups"),
        ],
        "Can Archive Access Groups": [
            ("View", "Admin Dashboard"),
            ("Archive", "Access Groups"),
        ],
        "Can Create Roles": [("View", "Admin Dashboard"), ("Create", "Roles")],
        "Can Edit Roles": [("View", "Admin Dashboard"), ("Edit", "Roles")],
        "Can Archive Roles": [
            ("View", "Admin Dashboard"),
            ("Archive", "Roles"),
        ],
        "Can Create Studies": [
            ("View", "Admin Dashboard"),
            ("Create", "Studies"),
        ],
        "Can Edit Studies": [("View", "Admin Dashboard"), ("Edit", "Studies")],
        "Can Archive Studies": [
            ("View", "Admin Dashboard"),
            ("Archive", "Studies"),
        ],
        "Can Create About Sleep Templates": [
            ("View", "Admin Dashboard"),
            ("Create", "About Sleep Templates"),
        ],
        "Can Edit About Sleep Templates": [
            ("View", "Admin Dashboard"),
            ("Edit", "About Sleep Templates"),
        ],
        "Can Archive About Sleep Templates": [
            ("View", "Admin Dashboard"),
            ("Archive", "About Sleep Templates"),
        ],
    }

    # Create access groups for testing admin dashboard permissions
    for access_group_name, permissions in admin_access_groups.items():
        access_group = AccessGroup(name=access_group_name, app=admin_app)
        for action, resource in permissions:
            query = Permission.definition == tuple_(action, resource)
            permission = Permission.query.filter(query).first()
            JoinAccessGroupPermission(
                access_group=access_group, permission=permission
            )
        db.session.add(access_group)

    ditti_access_groups = {
        "Can View Audio Files": [
            ("View", "Participants"),
            ("View", "Ditti App Dashboard"),
            ("View", "Audio Files"),
        ],
        "Can Create Audio Files": [
            ("View", "Participants"),
            ("View", "Ditti App Dashboard"),
            ("View", "Audio Files"),
            ("Create", "Audio Files"),
        ],
        "Can Delete Audio Files": [
            ("View", "Participants"),
            ("View", "Ditti App Dashboard"),
            ("View", "Audio Files"),
            ("Delete", "Audio Files"),
        ],
    }

    # Create access groups for testing Ditti dashboard permissions
    for access_group_name, permissions in ditti_access_groups.items():
        access_group = AccessGroup(name=access_group_name, app=ditti_app)
        for action, resource in permissions:
            query = Permission.definition == tuple_(action, resource)
            permission = Permission.query.filter(query).first()
            JoinAccessGroupPermission(
                access_group=access_group, permission=permission
            )
        db.session.add(access_group)

    data_summary = """The clinical trial collects sleep data from participants' \
wearable devices over four weeks to evaluate the
impact of mindfulness exercises on treating insomnia. By monitoring sleep \
patterns, duration, and quality,
researchers can gain objective insights into participants' sleep behavior \
before, during, and after engaging in
mindfulness interventions. This data enables the study to measure the \
effectiveness of these exercises in
improving sleep outcomes. Wearable devices provide a convenient, non-invasive \
method for gathering accurate,
real-time data essential for understanding the physiological effects of \
mindfulness on sleep."""

    studies = [
        {
            "name": "Test Study A",
            "acronym": "TESTA",
            "ditti_id": "TA",
            "email": "test.study.A@studyAemail.com",
            "default_expiry_delta": 14,
            "consent_information": "By accepting, you agree that your data "
            "will be used. You can withdraw consent "
            "at any time.",
            "data_summary": data_summary,
        },
        {
            "name": "Test Study B",
            "acronym": "TESTB",
            "ditti_id": "TB",
            "email": "test.study.B@studyBemail.com",
            "default_expiry_delta": 14,
            "consent_information": "By accepting, you agree that your data "
            "will be used. You cannot withdraw consent.",
            "data_summary": data_summary,
        },
    ]

    # Create two test studies
    study_a = Study(**studies[0])
    study_b = Study(**studies[1])
    db.session.add(study_a)
    db.session.add(study_b)

    # Create a Ditti admin account to test whether permissions are scoped to the
    # Ditti Dashboard only
    account = Account(
        created_on=datetime.now(UTC),
        first_name="Jane",
        last_name="Doe",
        email="Ditti Admin",
        is_confirmed=True,
    )
    JoinAccountAccessGroup(account=account, access_group=ditti_admin_group)
    db.session.add(account)

    # Create a Wearable admin account to test whether permissions are scoped
    # to the Wearable Dashboard only
    account = Account(
        created_on=datetime.now(UTC),
        first_name="Jane",
        last_name="Doe",
        email="Wearable Admin",
        is_confirmed=True,
    )
    JoinAccountAccessGroup(account=account, access_group=wear_admin_group)
    db.session.add(account)

    # Create a Study A Admin account to test whether permissions are scoped to the
    # Study A only
    account = Account(
        created_on=datetime.now(UTC),
        first_name="Jane",
        last_name="Doe",
        email="Study A Admin",
        is_confirmed=True,
    )
    role = Role.query.filter(Role.name == "Admin").first()
    JoinAccountStudy(account=account, study=study_a, role=role)
    JoinAccountAccessGroup(account=account, access_group=ditti_coordinator_group)
    JoinAccountAccessGroup(account=account, access_group=wear_coordinator_group)
    JoinAccountAccessGroup(account=account, access_group=admin_group)
    db.session.add(account)

    # Create an account for each role
    # Assign each role to Study A to test whether permissions are scoped
    # to Study A only
    other_role = Role.query.filter(Role.name == "Can View Participants").first()
    for role_name in roles:
        account = Account(
            created_on=datetime.now(UTC),
            first_name="Jane",
            last_name="Doe",
            email=role_name,
            is_confirmed=True,
        )
        role = Role.query.filter(Role.name == role_name).first()
        JoinAccountStudy(account=account, study=study_a, role=role)
        JoinAccountStudy(account=account, study=study_b, role=other_role)
        JoinAccountAccessGroup(
            account=account, access_group=ditti_coordinator_group
        )
        JoinAccountAccessGroup(
            account=account, access_group=wear_coordinator_group
        )
        JoinAccountAccessGroup(account=account, access_group=admin_group)
        db.session.add(account)

    # Create an account for each access group to test whether permissions are
    # scoped properly on the Admin Dashboard
    access_group_names = list(admin_access_groups.keys()) + list(
        ditti_access_groups.keys()
    )
    for access_group_name in access_group_names:
        account = Account(
            created_on=datetime.now(UTC),
            first_name="Jane",
            last_name="Doe",
            email=access_group_name,
            is_confirmed=True,
        )
        access_group = AccessGroup.query.filter(
            AccessGroup.name == access_group_name
        ).first()
        JoinAccountAccessGroup(account=account, access_group=access_group)
        db.session.add(account)

    template_html = """<div>
    <h1>Heading 1</h1>
    <h2>Heading 2</h2>
    <h3>Heading 3</h3>
    <h4>Heading 4</h4>
    <h5>Heading 5</h5>
    <h6>Heading 6</h6>
    <p>Paragraph. <i>Italics.</i> <b>Bold</b></p>
    <unallowed>Unallowed tag.</unallowed>
    <p unallowed>Unallowed attribute.</p>
</div>"""

    db.session.add(
        AboutSleepTemplate(name="About Sleep Template", text=template_html)
    )

    # Add Fitbit API
    api = Api(name="Fitbit")
    db.session.add(api)

    test001 = StudySubject(ditti_id="test001")
    test002 = StudySubject(ditti_id="test002")
    test003 = StudySubject(ditti_id="test003")
    db.session.add(test001)
    db.session.add(test002)
    db.session.add(test003)

    # Add study subjects for testing filtering sleep logs by study ditti prefix
    ta001 = StudySubject(ditti_id="TA001")
    tb001 = StudySubject(ditti_id="TB001")
    db.session.add(ta001)
    db.session.add(tb001)

    study_subject_studies = [
        {
            "study_subject": test001,
            "study": study_a,
            "did_consent": True,
        },
        {
            "study_subject": test002,
            "study": study_a,
            "did_consent": False,
            # Consenting should retroactively pull from this date
            "starts_on": datetime.now(UTC) - timedelta(days=7),
        },
        {
            "study_subject": test002,
            "study": study_b,
            "did_consent": True,
            # Data should be pulled from this date
            "starts_on": datetime.now(UTC) - timedelta(days=1),
        },
        {
            "study_subject": test003,  # No data should be pulled for this subject
            "study": study_a,
            "did_consent": False,
        },
        {
            "study_subject": test003,
            "study": study_b,
            "did_consent": False,
        },
        {
            "study_subject": ta001,
            "study": study_a,
            "did_consent": True,
            "starts_on": datetime.now(UTC),
        },
        {
            "study_subject": tb001,
            "study": study_b,
            "did_consent": True,
            "starts_on": datetime.now(UTC),
        },
    ]

    for join in study_subject_studies:
        JoinStudySubjectStudy(**join)

    study_subject_apis = [
        {
            "study_subject": test001,
            "api": api,
            "api_user_uuid": "test",
            "scope": ["sleep"],
            "last_sync_date": datetime.now(),
        },
        {
            "study_subject": test002,
            "api": api,
            "api_user_uuid": "test",
            "scope": ["sleep"],
        },
        {
            "study_subject": test003,
            "api": api,
            "api_user_uuid": "test",
            "scope": ["sleep"],
        },
        {
            "study_subject": ta001,
            "api": api,
            "api_user_uuid": "test",
            "scope": ["sleep"],
        },
        {
            "study_subject": tb001,
            "api": api,
            "api_user_uuid": "test",
            "scope": ["sleep"],
        },
    ]

    for join in study_subject_apis:
        JoinStudySubjectApi(**join)

    db.session.commit()


def init_lambda_task(status: str):
    """
    Initialize a lambda task with the specified status.

    Args:
        status: The status of the lambda task to create.
    """
    db.session.add(LambdaTask(status=status))
    db.session.commit()


def delete_lambda_tasks():
    """
    Delete all lambda tasks from the database.

    Used primarily for testing and cleanup operations.
    """
    for task in LambdaTask.query.all():
        db.session.delete(task)
    db.session.commit()


def init_study_subject(ditti_id):
    """
    Initialize a study subject with the specified Ditti ID.

    Creates a new StudySubject record with the given Ditti ID.

    Args:
        ditti_id: The Ditti ID for the study subject.
    """
    db_uri = current_app.config["SQLALCHEMY_DATABASE_URI"]
    if "localhost" not in db_uri:
        raise RuntimeError(
            "init_study_subject requires a localhost database URI."
        )

    study_a = Study.query.get(1)
    study_b = Study.query.get(2)
    if study_a is None or study_b is None:
        raise RuntimeError("Could not retrieve studies from the database.")

    existing = StudySubject.query.filter(
        StudySubject.ditti_id == ditti_id
    ).first()
    if existing is not None:
        raise RuntimeError(
            f"Study subject with ditti_id {ditti_id} already exists."
        )

    study_subject = StudySubject(ditti_id=ditti_id)

    JoinStudySubjectStudy(
        study_subject=study_subject,
        study=study_b,
        did_consent=True,
        starts_on=datetime.now(UTC) - timedelta(days=7),
    )

    db.session.add(study_subject)
    db.session.commit()


class SleepLevelEnum(enum.Enum):
    """Enumeration of sleep levels tracked in the system."""

    wake = "wake"
    light = "light"
    deep = "deep"
    rem = "rem"
    asleep = "asleep"
    awake = "awake"
    restless = "restless"


class SleepLogTypeEnum(enum.Enum):
    """Enumeration of sleep log types in the system."""

    auto_detected = "auto_detected"
    manual = "manual"


class SleepCategoryTypeEnum(enum.Enum):
    """Enumeration of sleep category types in the system."""

    stages = "stages"
    classic = "classic"


class Account(db.Model):
    """
    The account table mappeing class.

    Vars
    ----
    id: sqlalchemy.Column
    created_on: sqlalchemy.Column
        The timestamp of the account"s creation, e.g., `datetime.now(UTC)`.
        The created_on value cannot be modified.
    last_login: sqlalchemy.Column
    first_name: sqlalchemy.Column
    last_name: sqlalchemy.Column
    email: sqlalchemy.Column
    phone_number: sqlalchemy.Column
        Phone number in E.164 format (+1XXXXXXXXXX)
    is_confirmed: sqlalchemy.Column
        Whether the account holder has logged in and set their password.
    is_archived: sqlalchemy.Column
    access_groups: sqlalchemy.orm.relationship
    studies: sqlalchemy.orm.relationship
    """

    __tablename__ = "account"
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, nullable=False)
    last_login = db.Column(db.DateTime)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    phone_number = db.Column(db.String, nullable=True, unique=True)
    is_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    # ignore archived access groups
    access_groups = db.relationship(
        "JoinAccountAccessGroup",
        back_populates="account",
        cascade="all, delete-orphan",
        primaryjoin=(
            "and_("
            + "   Account.id == JoinAccountAccessGroup.account_id,"
            + "   JoinAccountAccessGroup.access_group_id == AccessGroup.id,"
            + "   AccessGroup.is_archived == False"
            + ")"
        ),
    )

    # ignore archived studies
    studies = db.relationship(
        "JoinAccountStudy",
        back_populates="account",
        cascade="all, delete-orphan",
        primaryjoin=(
            "and_("
            + "   Account.id == JoinAccountStudy.account_id,"
            + "   JoinAccountStudy.study_id == Study.id,"
            + "   Study.is_archived == False"
            + ")"
        ),
    )

    @validates("created_on")
    def validate_created_on(self, _key, val):
        """Make the created_on column read-only."""
        if self.created_on:
            raise ValueError("Account.created_on cannot be modified.")

        return val

    @validates("phone_number")
    def validate_phone_number(self, _key, value):
        """
        Validate phone number format.

        Must be in E.164 format.
        For US numbers: +1 followed by 10 digits.

        Parameters
        ----------
        _key : str
            The attribute name (not used).
        value : str or None
            The phone number to validate.

        Returns
        -------
        str or None
            The validated phone number or None.
        """
        if value is None:
            return None

        # If it's already in valid E.164 format, return as is
        if value and re.match(r"^\+[1-9]\d{1,14}$", value):
            return value

        # Invalid format
        raise ValueError(
            "Phone number must be in E.164 format (e.g., +12345678901)"
        )

    @hybrid_property
    def full_name(self):
        """str: The full name of the account holder."""
        return f"{self.first_name} {self.last_name}"

    @full_name.expression
    def full_name(cls):
        """
        Generate SQL expression for concatenating first and last name.

        Returns
        -------
        SQLAlchemy expression
            SQL expression for the full name.
        """
        return func.concat(cls.first_name, " ", cls.last_name)

    def get_permissions(self, app_id, study_id=None):
        """
        Get all of an account's permissions for an app and study.

        Retrieves all permissions that are granted to the account by access
        groups for the specified app and optionally for a specific study.

        Parameters
        ----------
        app_id : int
            The app's primary key.
        study_id : int, optional
            The study's primary key.

        Returns
        -------
        dict
            A dictionary of permission objects.
        """
        # query all permissions that are granted to the account by access
        # groups that grant access to the app
        q1 = (
            Permission.query.join(JoinAccessGroupPermission)
            .join(AccessGroup)
            .filter(AccessGroup.app_id == app_id)
            .join(JoinAccountAccessGroup)
            .filter(
                (~AccessGroup.is_archived)
                & (JoinAccountAccessGroup.account_id == self.id)
            )
        )

        # if a study id was passed and the study is not archived
        if study_id and not Study.query.get(study_id).is_archived:
            # query all permissions that are granted to the account by the
            # study
            q2 = (
                Permission.query.join(JoinRolePermission)
                .join(Role)
                .join(JoinAccountStudy, Role.id == JoinAccountStudy.role_id)
                .filter(JoinAccountStudy.primary_key == tuple_(self.id, study_id))
            )

            # return the union of all permission for the app and study
            permissions = q1.union(q2)

        else:
            # return all permissions for the app
            permissions = q1

        return permissions

    def validate_ask(self, action, resource, permissions):
        """
        Validate a request using a set of permissions.

        Args
        ----
        action: str
        resource: str
        permissions:

        Raises
        ------
        ValueError
            If the account has no permissions that satisfy the request.
        """
        # build a query using the requested action and resource
        query = Permission.definition == tuple_(action, resource)

        # also check if the account has wildcard permissions
        query = query | (Permission.definition == tuple_(action, "*"))
        query = query | (Permission.definition == tuple_("*", resource))
        query = query | (Permission.definition == tuple_("*", "*"))

        # filter the account's permissions
        valid = permissions.filter(query).first()

        # if no permissions were found
        if valid is None:
            raise ValueError("Unauthorized Ask")

    @property
    def meta(self):
        """dict: an entry's metadata."""
        return {
            "id": self.id,
            "createdOn": self.created_on,
            "lastLogin": self.last_login,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "email": self.email,
            "phoneNumber": self.phone_number,
            "isConfirmed": self.is_confirmed,
            "accessGroups": [j.access_group.meta for j in self.access_groups],
            "studies": [s.meta for s in self.studies],
        }

    def __repr__(self):
        return f"<Account {self.email}>"


class JoinAccountAccessGroup(db.Model):
    """
    The join_account_access_group table mapping class.

    Vars
    ----
    account_id: sqlalchemy.Column
    access_group_id: sqlalchemy.Column
    account: sqlalchemy.orm.relationship
    access_group: sqlalchemy.orm.relationship
    """

    __tablename__ = "join_account_access_group"

    account_id = db.Column(
        db.Integer, db.ForeignKey("account.id"), primary_key=True
    )

    access_group_id = db.Column(
        db.Integer,
        db.ForeignKey("access_group.id", ondelete="CASCADE"),
        primary_key=True,
    )

    account = db.relationship("Account", back_populates="access_groups")
    access_group = db.relationship("AccessGroup", back_populates="accounts")

    @hybrid_property
    def primary_key(self):
        """Tuple of int: an entry's primary key."""
        return self.account_id, self.access_group_id

    @primary_key.expression
    def primary_key(cls):
        """
        Generate SQL expression for the primary key.

        Returns
        -------
        SQLAlchemy tuple expression
            The composite primary key expression.
        """
        return tuple_(cls.account_id, cls.access_group_id)

    def __repr__(self):
        return "<JoinAccountAccessGroup {}-{}>".format(*self.primary_key)


class JoinAccountStudy(db.Model):
    """
    The join_account_study table mapping class.

    Vars
    ----
    account_id: sqlalchemy.Column
    study_id: sqlalchemy.Column
    account: sqlalchemy.orm.relationship
    study: sqlalchemy.orm.relationship
    role_id: sqlalchemy.Column
        The primary key of the role that an account is assigned for a study.
    role: sqlalchemy.orm.relationship
    """

    __tablename__ = "join_account_study"

    account_id = db.Column(
        db.Integer, db.ForeignKey("account.id"), primary_key=True
    )

    study_id = db.Column(
        db.Integer,
        db.ForeignKey("study.id", ondelete="CASCADE"),
        primary_key=True,
    )

    account = db.relationship("Account", back_populates="studies")
    study = db.relationship("Study")

    role_id = db.Column(
        db.Integer, db.ForeignKey("role.id", ondelete="CASCADE"), nullable=False
    )

    role = db.relationship("Role")

    @hybrid_property
    def primary_key(self):
        """Tuple of int: an entry's primary key."""
        return self.account_id, self.study_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.account_id, cls.study_id)

    @property
    def meta(self):
        """dict: an entry's metadata."""
        return {**self.study.meta, "role": self.role.meta}

    def __repr__(self):
        return "<JoinAccountStudy {}-{}>".format(*self.primary_key)


class AccessGroup(db.Model):
    """
    The access_group table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    name: sqlalchemy.Column
    is_archived: sqlalchemy.Column
    app_id: sqlalchemy.Column
        The primary key of the app that an access group grants permissions for.
    app: sqlalchemy.orm.relationship
    accounts: sqlalchemy.orm.relationship
    permissions: sqlalchemy.orm.relationship
        The permissions that an access group grants for an app.
    """

    __tablename__ = "access_group"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    app_id = db.Column(db.Integer, db.ForeignKey("app.id", ondelete="CASCADE"))
    app = db.relationship("App")

    # ignore archived accounts
    accounts = db.relationship(
        "JoinAccountAccessGroup",
        back_populates="access_group",
        cascade="all, delete-orphan",
        primaryjoin=(
            "and_("
            + "   AccessGroup.id == JoinAccountAccessGroup.access_group_id,"
            + "   JoinAccountAccessGroup.account_id == Account.id,"
            + "   Account.is_archived == False"
            + ")"
        ),
    )

    permissions = db.relationship(
        "JoinAccessGroupPermission",
        back_populates="access_group",
        cascade="all, delete-orphan",
    )

    @property
    def meta(self):
        """dict: an entry's metadata."""
        return {
            "id": self.id,
            "name": self.name,
            "app": self.app.meta,
            "permissions": [p.meta for p in self.permissions],
        }

    def __repr__(self):
        return f"<AccessGroup {self.name}>"


class JoinAccessGroupPermission(db.Model):
    """
    The join_access_group_permission table mapping class.

    Vars
    ----
    access_group_id: sqlalchemy.Column
    permission_id: sqlalchemy.Column
    access_group: sqlalchemy.orm.relationship
    permission: sqlalchemy.orm.relationship
    """

    __tablename__ = "join_access_group_permission"

    access_group_id = db.Column(
        db.Integer,
        db.ForeignKey("access_group.id", ondelete="CASCADE"),
        primary_key=True,
    )

    permission_id = db.Column(
        db.Integer,
        db.ForeignKey("permission.id", ondelete="CASCADE"),
        primary_key=True,
    )

    access_group = db.relationship("AccessGroup", back_populates="permissions")
    permission = db.relationship("Permission")

    @hybrid_property
    def primary_key(self):
        """Tuple of int: an entry's primary key."""
        return self.access_group_id, self.permission_id

    @primary_key.expression
    def primary_key(cls):
        """
        Generate SQL expression for the primary key.

        Returns
        -------
        SQLAlchemy tuple expression
            The composite primary key expression.
        """
        return tuple_(cls.access_group_id, cls.permission_id)

    @property
    def meta(self):
        """dict: an entry's metadata."""
        return self.permission.meta

    def __repr__(self):
        return "<JoinAccessGroupPermission {}-{}>".format(*self.primary_key)


class Role(db.Model):
    """
    The role table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    name: sqlalchemy.Column
    is_archived: sqlalchemy.Column
    permissions: sqlalchemy.orm.relationship
    """

    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    permissions = db.relationship(
        "JoinRolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
    )

    @property
    def meta(self):
        """dict: an entry's metadata."""
        return {
            "id": self.id,
            "name": self.name,
            "permissions": [p.meta for p in self.permissions],
        }

    def __repr__(self):
        return f"<Role {self.name}>"


class JoinRolePermission(db.Model):
    """
    The join_role_permission table mapping class.

    Vars
    ----
    role_id: sqlalchemy.Column
    permission_id: sqlalchemy.Column
    role: sqlalchemy.orm.relationship
    permission: sqlalchemy.orm.relationship
    """

    __tablename__ = "join_role_permission"

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("role.id", ondelete="CASCADE"),
        primary_key=True,
    )

    permission_id = db.Column(
        db.Integer,
        db.ForeignKey("permission.id", ondelete="CASCADE"),
        primary_key=True,
    )

    role = db.relationship("Role", back_populates="permissions")
    permission = db.relationship("Permission")

    @hybrid_property
    def primary_key(self):
        """Tuple of int: an entry's primary key."""
        return self.role_id, self.permission_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.role_id, cls.permission_id)

    @property
    def meta(self):
        """dict: an entry's metadata."""
        return self.permission.meta

    def __repr__(self):
        return "<JoinRolePermission {}-{}>".format(*self.primary_key)


class Action(db.Model):
    """
    The action table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    value: sqlalchemy.Column
    """

    __tablename__ = "action"
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String, nullable=False, unique=True)

    @property
    def meta(self):
        """dict: an entry's metadata."""
        return {"id": self.id, "value": self.value}

    def __repr__(self):
        return f"<Action {self.value}>"


class Resource(db.Model):
    """
    The resource table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    value: sqlalchemy.Column
    """

    __tablename__ = "resource"
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String, nullable=False, unique=True)

    @property
    def meta(self):
        """dict: an entry's metadata."""
        return {"id": self.id, "value": self.value}

    def __repr__(self):
        return f"<Resource {self.value}>"


class Permission(db.Model):
    """
    The permission table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    """

    __tablename__ = "permission"

    # ensure the action-resource combination is unique.
    __table_args__ = (UniqueConstraint("_action_id", "_resource_id"),)
    id = db.Column(db.Integer, primary_key=True)

    _action_id = db.Column(
        db.Integer, db.ForeignKey("action.id", ondelete="CASCADE")
    )

    _resource_id = db.Column(
        db.Integer, db.ForeignKey("resource.id", ondelete="CASCADE")
    )

    _action = db.relationship("Action")
    _resource = db.relationship("Resource")

    @hybrid_property
    def action(self):
        """str: an entry's action."""
        return self._action.value

    @action.setter
    def action(self, value):
        q = Action.query.filter(Action.value == value)

        # if the action does not exist, create a new action
        action = q.first() or Action(value=value)
        db.session.add(action)
        self._action = action

    @action.expression
    def action(cls):
        """
        Generate SQL expression for the action attribute.

        Returns
        -------
        SQLAlchemy subquery
            The subquery for the action value.
        """
        return (
            select(Action.value)
            .where(Action.id == cls._action_id)
            .scalar_subquery()
        )

    @hybrid_property
    def resource(self):
        """str: an entry's resource."""
        return self._resource.value

    @resource.setter
    def resource(self, value):
        q = Resource.query.filter(Resource.value == value)

        # if the resource does not exist, create a new resource
        resource = q.first() or Resource(value=value)
        db.session.add(resource)
        self._resource = resource

    @resource.expression
    def resource(cls):
        """
        Generate SQL expression for the resource attribute.

        Returns
        -------
        SQLAlchemy subquery
            The subquery for the resource value.
        """
        return (
            select(Resource.value)
            .where(Resource.id == cls._resource_id)
            .scalar_subquery()
        )

    @validates("_action_id")
    def validate_action(self, _key, val):
        """Ensure an entry's action cannot be modified."""
        if self._action_id is not None:
            raise ValueError("permission.action cannot be modified.")

        return val

    @validates("_resource_id")
    def validate_resource(self, _key, val):
        """Ensure an entry's resource cannot be modified."""
        if self._resource_id is not None:
            raise ValueError("permission.resource cannot be modified.")

        return val

    @hybrid_property
    def definition(self):
        """Tuple of str: an entry's (action, resource) definition."""
        return self.action, self.resource

    @definition.expression
    def definition(cls):
        """
        Generate SQL expression for the definition attribute.

        Returns
        -------
        SQLAlchemy tuple expression
            The tuple expression combining action and resource.
        """
        return tuple_(
            select(Action.value)
            .where(Action.id == cls._action_id)
            .scalar_subquery(),
            select(Resource.value)
            .where(Resource.id == cls._resource_id)
            .scalar_subquery(),
        )

    @property
    def meta(self):
        """dict: an entry's metadata."""
        return {"id": self.id, "action": self.action, "resource": self.resource}

    def __repr__(self):
        return "<Permission {} {}>".format(*self.definition)


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
        """dict: an entry's metadata."""
        return {"id": self.id, "name": self.name}

    def __repr__(self):
        return f"<App {self.name}>"


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
        in the study. A JoinStudySubjectStudy's expires_on column will be
        automatically set according to this value.
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

    roles = db.relationship("JoinStudyRole", cascade="all, delete-orphan")

    @property
    def meta(self):
        """dict: an entry's metadata."""
        return {
            "id": self.id,
            "name": self.name,
            "acronym": self.acronym,
            "dittiId": self.ditti_id,
            "email": self.email,
            "roles": [r.meta for r in self.roles],
            "defaultExpiryDelta": self.default_expiry_delta,
            "consentInformation": self.consent_information,
            "dataSummary": self.data_summary,
            "isQi": self.is_qi,
        }

    def __repr__(self):
        return f"<Study {self.acronym}>"


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

    study_id = db.Column(db.Integer, db.ForeignKey("study.id"), primary_key=True)

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("role.id", ondelete="CASCADE"),
        primary_key=True,
    )

    study = db.relationship("Study", back_populates="roles")
    role = db.relationship("Role")

    @hybrid_property
    def primary_key(self):
        """Tuple of int: an entry's primary key."""
        return self.study_id, self.role_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.study_id, cls.role_id)

    @property
    def meta(self):
        """dict: an entry's metadata."""
        return self.role.meta

    def __repr__(self):
        return f"<JoinStudyRole {self.study_id}-{self.role_id}>"


class BlockedToken(db.Model):
    """
    Log users out using JWT tokens.

    The blocked_token table mapping class.

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
        return f"<BlockedToken {self.id}>"


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
        """dict: an entry's metadata."""
        return {"id": self.id, "name": self.name, "text": self.text}

    def __repr__(self):
        return f"<AboutSleepTemplate {self.name}>"


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
        ),
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
        ),
    )

    sleep_logs = db.relationship(
        "SleepLog",
        back_populates="study_subject",
        cascade="all, delete-orphan",
        lazy="dynamic",  # Use dynamic loading for large datasets
    )

    @property
    def meta(self):
        return {
            "id": self.id,
            "createdOn": self.created_on.isoformat(),
            "dittiId": self.ditti_id,
            "studies": [join.meta for join in self.studies],
            "apis": [join.meta for join in self.apis],
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
        primary_key=True,
    )
    study_id = db.Column(
        db.Integer,
        db.ForeignKey("study.id"),  # Do not allow deletions on study table
        primary_key=True,
    )
    did_consent = db.Column(db.Boolean, default=False, nullable=False)
    created_on = db.Column(db.DateTime, default=func.now(), nullable=False)
    starts_on = db.Column(db.DateTime, default=func.now(), nullable=False)
    expires_on = db.Column(db.DateTime, nullable=True)

    study_subject = db.relationship("StudySubject", back_populates="studies")
    study = db.relationship("Study")

    @validates("created_on")
    def validate_created_on(self, _key, val):
        """Make the created_on column read-only."""
        if self.created_on:
            raise ValueError(
                "JoinStudySubjectStudy.created_on cannot be modified."
            )
        return val

    @validates("expires_on")
    def validate_expires_on(self, _key, value):
        """
        Validate that expires_on is a future date.

        Parameters
        ----------
        _key : str
            The attribute name (not used).
        value : datetime or None
            The date value to validate.

        Returns
        -------
        datetime or None
            The validated value if it passes validation.

        Raises
        ------
        ValueError
            If the value is not a future date.
        """
        if value and value <= datetime.now(UTC):
            raise ValueError("expires_on must be a future date.")
        return value

    @hybrid_property
    def primary_key(self):
        """Tuple of int: an entry's primary key."""
        return self.study_subject_id, self.study_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.study_subject_id, cls.study_id)

    @property
    def meta(self):
        """dict: an entry's metadata."""
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
def set_expires_on(_mapper, connection, target):
    """
    Set the expires_on field.

    Automatically set based on the Study's default_expiry_delta
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
                        target.study_id
                    } not found or default_expiry_delta is missing."
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
        primary_key=True,
    )

    api_id = db.Column(db.Integer, db.ForeignKey("api.id"), primary_key=True)

    api_user_uuid = db.Column(db.String, nullable=False)
    scope = db.Column(db.ARRAY(db.String))
    last_sync_date = db.Column(db.Date, nullable=True)
    created_on = db.Column(db.DateTime, default=func.now(), nullable=False)

    study_subject = db.relationship("StudySubject", back_populates="apis")
    api = db.relationship("Api")

    @validates("created_on")
    def validate_created_on(self, _key, val):
        """Make the created_on column read-only."""
        if self.created_on:
            raise ValueError("JoinStudySubjectApi.created_on cannot be modified.")
        return val

    @hybrid_property
    def primary_key(self):
        """Tuple of int: an entry's primary key."""
        return self.study_subject_id, self.api_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.study_subject_id, cls.api_id)

    @property
    def meta(self):
        """dict: An entry's metadata."""
        return {
            "apiUserUuid": self.api_user_uuid,
            "scope": self.scope,
            "api": self.api.meta,
            "lastSyncDate": self.last_sync_date.isoformat()
            if self.last_sync_date
            else None,
            "createdOn": self.created_on.isoformat(),
        }

    def __repr__(self):
        return (
            f"<JoinStudySubjectApi StudySubject {self.study_subject_id} - "
            f"Api {self.api_id}>"
        )


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
        """dict: an entry's metadata."""
        return {"id": self.id, "name": self.name}

    def __repr__(self):
        return f"<Api {self.name}>"


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
        index=True,
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

    study_subject = db.relationship("StudySubject", back_populates="sleep_logs")
    levels = db.relationship(
        "SleepLevel",
        back_populates="sleep_log",
        cascade="all, delete-orphan",
        lazy="selectin",  # Efficient loading of related objects
    )
    summaries = db.relationship(
        "SleepSummary",
        back_populates="sleep_log",
        cascade="all, delete-orphan",
        lazy="joined",  # Eagerly load summaries
    )

    @validates("efficiency")
    def validate_efficiency(self, _key, value):
        """
        Validate that efficiency value is within acceptable range.

        Parameters
        ----------
        _key : str
            The attribute name (not used).
        value : int or None
            The value to validate.

        Returns
        -------
        int or None
            The validated value if it passes validation.

        Raises
        ------
        ValueError
            If the value is not between 0 and 100.
        """
        if value is not None and not (0 <= value <= 100):
            raise ValueError("Efficiency must be between 0 and 100.")
        return value

    @property
    def meta(self):
        """dict: An entry's metadata."""
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
            "summaries": [summary.meta for summary in self.summaries],
        }

    def __repr__(self):
        return (
            f"<SleepLog {self.log_id} for StudySubject {self.study_subject_id}>"
        )


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
        db.Index(
            "idx_sleep_level_sleep_log_id_date_time",
            "sleep_log_id",
            "date_time",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    sleep_log_id = db.Column(
        db.Integer, db.ForeignKey("sleep_log.id"), nullable=False
    )
    date_time = db.Column(db.DateTime, nullable=False, index=True)
    level = db.Column(Enum(SleepLevelEnum), nullable=False)
    seconds = db.Column(db.Integer, nullable=False)
    is_short = db.Column(db.Boolean, default=False, nullable=True)

    sleep_log = db.relationship("SleepLog", back_populates="levels")

    @property
    def meta(self):
        """dict: An entry's metadata."""
        return {
            "dateTime": self.date_time.isoformat(),
            "level": self.level.value,
            "seconds": self.seconds,
            "isShort": self.is_short,
        }

    def __repr__(self):
        return (
            f"<SleepLevel {self.level.value} at {self.date_time} for "
            f"SleepLog {self.sleep_log_id}>"
        )


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
        db.Integer, db.ForeignKey("sleep_log.id"), nullable=False
    )
    level = db.Column(Enum(SleepLevelEnum), nullable=False)
    count = db.Column(db.Integer)
    minutes = db.Column(db.Integer)
    thirty_day_avg_minutes = db.Column(db.Integer, nullable=True)

    sleep_log = db.relationship("SleepLog", back_populates="summaries")

    @property
    def meta(self):
        """dict: An entry's metadata."""
        return {
            "level": self.level.value,
            "count": self.count,
            "minutes": self.minutes,
            "thirtyDayAvgMinutes": self.thirty_day_avg_minutes,
        }

    def __repr__(self):
        return (
            f"<SleepSummary {self.level.value} for SleepLog {self.sleep_log_id}>"
        )


class LambdaTask(db.Model):
    """
    The lambda_task table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    status: sqlalchemy.Column
        The status of the task ("Pending", "InProgress", "Success", "Failed",
        "CompletedWithErrors").
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
            "Pending",
            "InProgress",
            "Success",
            "Failed",
            "CompletedWithErrors",
            name="taskstatustypeenum",
        ),
        nullable=False,
    )
    billed_ms = db.Column(db.Integer, nullable=True)
    created_on = db.Column(
        db.DateTime, default=func.now(), nullable=False, index=True
    )
    updated_on = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now(), nullable=False
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
            "completedOn": self.completed_on.isoformat()
            if self.completed_on
            else None,
            "logFile": self.log_file,
            "errorCode": self.error_code,
        }

    def __repr__(self):
        return f"<LambdaTask {self.id}>"
