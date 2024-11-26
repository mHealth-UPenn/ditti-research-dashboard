import enum
import logging
import os
import random
import uuid
from datetime import datetime, UTC, timedelta
from flask import current_app
from sqlalchemy import select, func, tuple_, event, Enum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from sqlalchemy.sql.schema import UniqueConstraint

from aws_portal.extensions import bcrypt, db, jwt
from shared.utils.sleep_logs import generate_sleep_logs


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
        raise ValueError("This access group already exists: %s" % access_group)

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
        access_group=access_group,
        permission=permission
    )

    db.session.add(permission)
    db.session.add(access_group)
    db.session.add(join)
    db.session.commit()

    return access_group


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
        public_id=str(uuid.uuid4()),
        created_on=datetime.now(UTC),
        first_name="AWS",
        last_name="Admin",
        email=email,
        is_confirmed=True
    )

    db.session.commit()
    admin.password = password
    admin_join = JoinAccountAccessGroup(
        account=admin, access_group=admin_group
    )
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


def init_demo_db():
    demo_admin_email = os.getenv("DEMO_ADMIN_EMAIL")
    demo_admin_password = os.getenv("DEMO_ADMIN_PASSWORD")
    demo_email = os.getenv("DEMO_EMAIL")
    demo_password = os.getenv("DEMO_PASSWORD")

    if (
        demo_admin_email is None or
        demo_admin_password is None or
        demo_email is None or
        demo_password is None
    ):
        raise RuntimeError("One or more of the following environment variables are missing: DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD, DEMO_EMAIL, DEMO_PASSWORD")

    # Request user confirmation when pointing to non-localhost database
    db_uri = current_app.config["SQLALCHEMY_DATABASE_URI"]
    if input(f"(y/n) Confirm creating demo data on following database: {db_uri}\n") not in {"y", "yes"}:
        print("Creation of demo data cancelled")
        return False

    # Create all possible `(action, resource)` permission combinations
    actions = ["*", "Create", "View", "Edit", "Archive", "Delete"]
    resources = ["*", "Admin Dashboard", "Ditti App Dashboard", "Accounts", "Access Groups", "Roles", "Studies", "All Studies", "About Sleep Templates", "Audio Files", "Users", "Taps"]
    for action in actions:
        for resource in resources:
            permission = Permission()
            permission.action = action
            permission.resource = resource
            db.session.add(permission)

    # Create the Admin access group
    admin_app = App(name="Admin Dashboard")
    admin_group = AccessGroup(name="Admin", app=admin_app)
    query = Permission.definition == tuple_("*", "*")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(access_group=admin_group, permission=permission)
    db.session.add(admin_app)
    db.session.add(admin_group)

    # Create the Ditti Admin access group
    ditti_app = App(name="Ditti App Dashboard")
    ditti_admin_group = AccessGroup(name="Ditti App Admin", app=ditti_app)
    query = Permission.definition == tuple_("*", "*")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(access_group=ditti_admin_group, permission=permission)
    query = Permission.definition == tuple_("View", "Ditti App Dashboard")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(access_group=ditti_admin_group, permission=permission)
    db.session.add(ditti_app)
    db.session.add(ditti_admin_group)

    # Create the demo access group
    demo_group = AccessGroup(name="Demo Group", app=ditti_app)
    query = Permission.definition == tuple_("View", "Ditti App Dashboard")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(access_group=demo_group, permission=permission)
    query = Permission.definition == tuple_("View", "Audio Files")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(access_group=demo_group, permission=permission)
    query = Permission.definition == tuple_("View", "All Studies")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(access_group=demo_group, permission=permission)
    db.session.add(demo_group)

    # Create the demo role
    demo_role = Role(name="Demo Role")
    query = Permission.definition == tuple_("View", "Taps")
    permission = Permission.query.filter(query).first()
    JoinRolePermission(role=demo_role, permission=permission)
    query = Permission.definition == tuple_("View", "Users")
    permission = Permission.query.filter(query).first()
    JoinRolePermission(role=demo_role, permission=permission)
    db.session.add(demo_role)

    studies = [
        {
            "name": "Sleep and Lifestyle Enhancement through Evidence-based Practices for Insomnia Treatment",
            "acronym": "SLEEP-IT",
            "ditti_id": "sit",
            "email": "sleep.it@research.edu",
            "default_expiry_delta": 14,
            "consent_information": "",
        },
        {
            "name": "Cognitive and Affective Lifestyle Modifications for Sleep Enhancement through Mindfulness Practices",
            "acronym": "CALM-SLEEP",
            "ditti_id": "cs",
            "email": "calm.sleep@research.edu",
            "default_expiry_delta": 14,
            "consent_information": "",
        }
    ]

    # Create two test studies
    study_a = Study(**studies[0])
    study_b = Study(**studies[1])
    db.session.add(study_a)
    db.session.add(study_b)

    # Create an admin account
    account = Account(
        public_id=str(uuid.uuid4()),
        created_on=datetime.now(UTC),
        first_name="Admin",
        last_name="Admin",
        email=os.getenv("DEMO_ADMIN_EMAIL"),
        is_confirmed=True,
    )
    account.password = os.getenv("DEMO_ADMIN_PASSWORD")
    JoinAccountAccessGroup(account=account, access_group=ditti_admin_group)
    JoinAccountAccessGroup(account=account, access_group=admin_group)
    db.session.add(account)

    # Create a demo account
    account = Account(
        public_id=str(uuid.uuid4()),
        created_on=datetime.now(UTC),
        first_name="Demo",
        last_name="Demo",
        email=os.getenv("DEMO_EMAIL"),
        is_confirmed=True,
    )
    account.password = os.getenv("DEMO_PASSWORD")
    JoinAccountAccessGroup(account=account, access_group=demo_group)
    JoinAccountStudy(account=account, study=study_a, role=demo_role)
    JoinAccountStudy(account=account, study=study_b, role=demo_role)
    db.session.add(account)

    template_html = """<div>
    <h1>Sleep Hygiene Instructions: General</h1>
    <p>Maintain a regular sleep/wake schedule. Try to keep the same rise time and bedtime every day.</p>
    <p>Set your alarm to get up at the same time each morning, regardless of how much sleep you got during the night, in
        order to maintain a consistent sleep/wake schedule.</p>
    <p>Do not attempt to “make up for lost sleep” on weekends or hopdays. It may not work and it means you are not up to
        par for the second half of the week.</p>
    <p>Do not watch the alarm clock and worry about the time or lost sleep. </p>
    <p>Do not spend too much time in bed “chasing sleep”</p>
    <p>Do not nap during the day. Not napping will allow you to sleep much better at night. Exercise instead of napping.
        Stay active during the day when you feel sleepy.</p>
    <p>Eat meals at the same time each day, every day. Three or four small meals per day are better than one to two
        large meals.</p>
    <p>Avoid or minimize the use of caffeine. It is a stimulant that interferes with sleep. The effects can last as long
        as 8-14 hours. One cup of coffee contains 100 mg of caffeine and takes three hours to leave the body. Most sodas
        and teas, some headache and cold medicines, and most diet pills will worsen sleep. It is recommended not to
        drink coffee, tea or soda after lunch. If you continue to have difficulty falling asleep, avoid drinking
        caffeinated beverages after breakfast.</p>
    <p>Avoid alcohol. You may feel it helps you get to sleep, but for most people it causes awakenings as well as poor
        sleep later in the night. Alcohol can make snoring and sleep apnea worse.</p>
    <p>Maintain a regular exercise schedule. Walking is an excellent form of exercise. The best time is early in the
        morning (7 AM – 9 AM). Stretching can be done on rainy days. Guard against “strenuous exercise” before</p>
</div>"""

    db.session.add(AboutSleepTemplate(name="Default Template", text=template_html))
    db.session.commit()

    return True


def init_integration_testing_db():
    # Enforce that the environment must be pointing at a local database
    db_uri = current_app.config["SQLALCHEMY_DATABASE_URI"]
    if "localhost" not in db_uri:
        raise RuntimeError("Dev data initialization attempted on non-localhost database")

    # Create all possible `(action, resource)` permission combinations
    actions = ["*", "Create", "View", "Edit", "Archive", "Delete"]
    resources = ["*", "Admin Dashboard", "Ditti App Dashboard", "Accounts", "Access Groups", "Roles", "Studies", "All Studies", "About Sleep Templates", "Audio Files", "Users", "Taps"]
    for action in actions:
        for resource in resources:
            permission = Permission()
            permission.action = action
            permission.resource = resource
            db.session.add(permission)

    roles = {
        "Admin": [
            ("*", "*"),
            ("View", "All Studies")
        ],
        "Coordinator": [
            ("View", "*"),
            ("Create", "Users"),
            ("Edit", "Users"),
            ("Create", "Audio Files"),
            ("Edit", "Audio Files"),
        ],
        "Analyst": [
            ("View", "*"),
        ],
        "Can View Users": [
            ("View", "Users")
        ],
        "Can Create Users": [
            ("View", "Users"),
            ("Create", "Users")
        ],
        "Can Edit Users": [
            ("View", "Users"),
            ("Edit", "Users")
        ],
        "Can View Taps": [
            ("View", "Taps")
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
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(access_group=admin_group, permission=permission)
    db.session.add(admin_app)
    db.session.add(admin_group)

    # Create the Ditti Admin access group
    ditti_app = App(name="Ditti App Dashboard")
    ditti_admin_group = AccessGroup(name="Ditti App Admin", app=ditti_app)
    query = Permission.definition == tuple_("*", "*")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(access_group=ditti_admin_group, permission=permission)
    query = Permission.definition == tuple_("View", "Ditti App Dashboard")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(access_group=ditti_admin_group, permission=permission)
    db.session.add(ditti_app)
    db.session.add(ditti_admin_group)

    # Create the Ditti Coordinator access group
    ditti_coordinator_group = AccessGroup(name="Ditti App Coordinator", app=ditti_app)
    query = Permission.definition == tuple_("View", "Ditti App Dashboard")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(access_group=ditti_coordinator_group, permission=permission)
    query = Permission.definition == tuple_("View", "Audio Files")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(access_group=ditti_coordinator_group, permission=permission)
    query = Permission.definition == tuple_("Create", "Audio Files")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(access_group=ditti_coordinator_group, permission=permission)
    query = Permission.definition == tuple_("Delete", "Audio Files")
    permission = Permission.query.filter(query).first()
    JoinAccessGroupPermission(access_group=ditti_coordinator_group, permission=permission)
    db.session.add(ditti_app)
    db.session.add(ditti_coordinator_group)

    admin_access_groups = {
        "Can Create Accounts": [
            ("View", "Admin Dashboard"),
            ("Create", "Accounts")
        ],
        "Can Edit Accounts": [
            ("View", "Admin Dashboard"),
            ("Edit", "Accounts")
        ],
        "Can Archive Accounts": [
            ("View", "Admin Dashboard"),
            ("Archive", "Accounts")
        ],
        "Can Create Access Groups": [
            ("View", "Admin Dashboard"),
            ("Create", "Access Groups")
        ],
        "Can Edit Access Groups": [
            ("View", "Admin Dashboard"),
            ("Edit", "Access Groups")
        ],
        "Can Archive Access Groups": [
            ("View", "Admin Dashboard"),
            ("Archive", "Access Groups")
        ],
        "Can Create Roles": [
            ("View", "Admin Dashboard"),
            ("Create", "Roles")
        ],
        "Can Edit Roles": [
            ("View", "Admin Dashboard"),
            ("Edit", "Roles")
        ],
        "Can Archive Roles": [
            ("View", "Admin Dashboard"),
            ("Archive", "Roles")
        ],
        "Can Create Studies": [
            ("View", "Admin Dashboard"),
            ("Create", "Studies")
        ],
        "Can Edit Studies": [
            ("View", "Admin Dashboard"),
            ("Edit", "Studies")
        ],
        "Can Archive Studies": [
            ("View", "Admin Dashboard"),
            ("Archive", "Studies")
        ],
        "Can Create About Sleep Templates": [
            ("View", "Admin Dashboard"),
            ("Create", "About Sleep Templates")
        ],
        "Can Edit About Sleep Templates": [
            ("View", "Admin Dashboard"),
            ("Edit", "About Sleep Templates")
        ],
        "Can Archive About Sleep Templates": [
            ("View", "Admin Dashboard"),
            ("Archive", "About Sleep Templates")
        ],
    }

    # Create access groups for testing admin dashboard permissions
    for access_group_name, permissions in admin_access_groups.items():
        access_group = AccessGroup(name=access_group_name, app=admin_app)
        for action, resource in permissions:
            query = Permission.definition == tuple_(action, resource)
            permission = Permission.query.filter(query).first()
            JoinAccessGroupPermission(access_group=access_group, permission=permission)
        db.session.add(access_group)

    ditti_access_groups = {
        "Can View Audio Files": [
            ("View", "Ditti App Dashboard"),
            ("View", "Audio Files")
        ],
        "Can Create Audio Files": [
            ("View", "Ditti App Dashboard"),
            ("View", "Audio Files"),
            ("Create", "Audio Files")
        ],
        "Can Delete Audio Files": [
            ("View", "Ditti App Dashboard"),
            ("View", "Audio Files"),
            ("Delete", "Audio Files")
        ],
    }

    # Create access groups for testing Ditti dashboard permissions
    for access_group_name, permissions in ditti_access_groups.items():
        access_group = AccessGroup(name=access_group_name, app=ditti_app)
        for action, resource in permissions:
            query = Permission.definition == tuple_(action, resource)
            permission = Permission.query.filter(query).first()
            JoinAccessGroupPermission(access_group=access_group, permission=permission)
        db.session.add(access_group)

    studies = [
        {
            "name": "Test Study A",
            "acronym": "TESTA",
            "ditti_id": "TA",
            "email": "test.study.A@studyAemail.com",
            "default_expiry_delta": 14,
            "consent_information": "",
        },
        {
            "name": "Test Study B",
            "acronym": "TESTB",
            "ditti_id": "TB",
            "email": "test.study.B@studyBemail.com",
            "default_expiry_delta": 14,
            "consent_information": "",
        }
    ]

    # Create two test studies
    study_a = Study(**studies[0])
    study_b = Study(**studies[1])
    db.session.add(study_a)
    db.session.add(study_b)

    # Create an admin account
    account = Account(
        public_id=str(uuid.uuid4()),
        created_on=datetime.now(UTC),
        first_name="Jane",
        last_name="Doe",
        email=os.getenv("FLASK_ADMIN_EMAIL"),
        is_confirmed=True,
    )
    account.password = os.getenv("FLASK_ADMIN_PASSWORD")
    JoinAccountAccessGroup(account=account, access_group=ditti_admin_group)
    JoinAccountAccessGroup(account=account, access_group=admin_group)
    db.session.add(account)

    # Create a Ditti admin account to test whether pemissions are scoped to the Ditti Dashboard only
    account = Account(
        public_id=str(uuid.uuid4()),
        created_on=datetime.now(UTC),
        first_name="Jane",
        last_name="Doe",
        email="Ditti Admin",
        is_confirmed=True,
    )
    account.password = os.getenv("FLASK_ADMIN_PASSWORD")
    JoinAccountAccessGroup(account=account, access_group=ditti_admin_group)
    db.session.add(account)

    # Create a Study A Admin account to test whether permissions are scopeed to Study A only
    account = Account(
        public_id=str(uuid.uuid4()),
        created_on=datetime.now(UTC),
        first_name="Jane",
        last_name="Doe",
        email="Study A Admin",
        is_confirmed=True,
    )
    account.password = os.getenv("FLASK_ADMIN_PASSWORD")
    role = Role.query.filter(Role.name == "Admin").first()
    JoinAccountStudy(account=account, study=study_a, role=role)
    JoinAccountAccessGroup(account=account, access_group=ditti_coordinator_group)
    JoinAccountAccessGroup(account=account, access_group=admin_group)
    db.session.add(account)

    # Create an account for each role
    # Assign each role to Study A to test whether permissions are scoped to Study A only
    other_role = Role.query.filter(Role.name == "Can View Users").first()
    for role_name in roles.keys():
        account = Account(
            public_id=str(uuid.uuid4()),
            created_on=datetime.now(UTC),
            first_name="Jane",
            last_name="Doe",
            email=role_name,
            is_confirmed=True,
        )
        account.password = os.getenv("FLASK_ADMIN_PASSWORD")
        role = Role.query.filter(Role.name == role_name).first()
        JoinAccountStudy(account=account, study=study_a, role=role)
        JoinAccountStudy(account=account, study=study_b, role=other_role)
        JoinAccountAccessGroup(account=account, access_group=ditti_coordinator_group)
        JoinAccountAccessGroup(account=account, access_group=admin_group)
        db.session.add(account)

    # Create an account for each access group to test whether permissions are scoped properly on the Admin Dashboard
    access_group_names = (
        list(admin_access_groups.keys()) + list(ditti_access_groups.keys())
    )
    for access_group_name in access_group_names:
        account = Account(
            public_id=str(uuid.uuid4()),
            created_on=datetime.now(UTC),
            first_name="Jane",
            last_name="Doe",
            email=access_group_name,
            is_confirmed=True,
        )
        account.password = os.getenv("FLASK_ADMIN_PASSWORD")
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

    db.session.add(AboutSleepTemplate(name="About Sleep Template", text=template_html))

    api = Api(name="Fitbit")
    db.session.add(api)

    test001 = StudySubject(ditti_id="test001")
    test002 = StudySubject(ditti_id="test002")
    test003 = StudySubject(ditti_id="test003")
    db.session.add(test001)
    db.session.add(test002)
    db.session.add(test003)

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
        },
        {
            "study_subject": test002,
            "study": study_b,
            "did_consent": True,
        },
        {
            "study_subject": test003,
            "study": study_a,
            "did_consent": True,
        }
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
            "study_subject": test003,
            "api": api,
            "api_user_uuid": "test",
            "scope": ["sleep"],
        }
    ]

    for join in study_subject_apis:
        JoinStudySubjectApi(**join)

    for i, study_subject in enumerate([test001, test002, test003]):
        sleep_logs = generate_sleep_logs()
        for j, entry in enumerate(sleep_logs["sleep"]):
            sleep_log = SleepLog(
                study_subject=study_subject,
                log_id=i * 10 + j,
                date_of_sleep=datetime.strptime(entry["dateOfSleep"], "%Y-%m-%d").date(),
                duration=entry["duration"],
                efficiency=entry["efficiency"],
                end_time=datetime.strptime(entry["endTime"], "%Y-%m-%dT%H:%M:%S.%f"),
                info_code=entry.get("infoCode"),
                is_main_sleep=entry["isMainSleep"],
                minutes_after_wakeup=entry["minutesAfterWakeup"],
                minutes_asleep=entry["minutesAsleep"],
                minutes_awake=entry["minutesAwake"],
                minutes_to_fall_asleep=entry["minutesToFallAsleep"],
                log_type=entry["logType"],
                start_time=datetime.strptime(entry["startTime"], "%Y-%m-%dT%H:%M:%S.%f"),
                time_in_bed=entry["timeInBed"],
                type=entry["type"],
            )
            for level in entry["levels"]["data"]:
                SleepLevel(
                    sleep_log=sleep_log,
                    date_time=datetime.strptime(level["dateTime"], "%Y-%m-%dT%H:%M:%S.%f"),
                    level=level["level"],
                    seconds=level["seconds"],
                    is_short=level.get("isShort", False)
                )
            db.session.add(sleep_log)

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


class Account(db.Model):
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

    # ignore archived access groups
    access_groups = db.relationship(
        "JoinAccountAccessGroup",
        back_populates="account",
        cascade="all, delete-orphan",
        primaryjoin=(
            "and_(" +
            "   Account.id == JoinAccountAccessGroup.account_id," +
            "   JoinAccountAccessGroup.access_group_id == AccessGroup.id," +
            "   AccessGroup.is_archived == False" +
            ")"
        )
    )

    # ignore archived studies
    studies = db.relationship(
        "JoinAccountStudy",
        back_populates="account",
        cascade="all, delete-orphan",
        primaryjoin=(
            "and_(" +
            "   Account.id == JoinAccountStudy.account_id," +
            "   JoinAccountStudy.study_id == Study.id," +
            "   Study.is_archived == False" +
            ")"
        )
    )

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

    def get_permissions(self, app_id, study_id=None):
        """
        Get all of an account"s permissions for an app and optionally for a
        study.

        Args
        ----
        app_id: int
            The app"s primary key.
        study_id: int (optional)
            The study"s primary key.

        Returns
        -------
        """

        # query all permissions that are granted to the account by access
        # groups that grant access to the app
        q1 = Permission.query.join(JoinAccessGroupPermission)\
            .join(AccessGroup)\
            .filter(AccessGroup.app_id == app_id)\
            .join(JoinAccountAccessGroup)\
            .filter(
                (~AccessGroup.is_archived) &
                (JoinAccountAccessGroup.account_id == self.id)
            )

        # if a study id was passed and the study is not archived
        if study_id and not Study.query.get(study_id).is_archived:

            # query all permissions that are granted to the account by the
            # study
            q2 = Permission.query.join(JoinRolePermission)\
                .join(Role)\
                .join(JoinAccountStudy, Role.id == JoinAccountStudy.role_id)\
                .filter(
                    JoinAccountStudy.primary_key == tuple_(self.id, study_id)
                )

            # return the union of all permission for the app and study
            permissions = q1.union(q2)

        else:

            # return all permissions for the app
            permissions = q1

        return permissions

    def validate_ask(self, action, resource, permissions):
        """
        Validate a request using a set of permissions

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

        # filter the account"s permissions
        valid = permissions.filter(query).first()

        # if no permissions were found
        if valid is None:
            raise ValueError("Unauthorized Ask")

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
            "accessGroups": [j.access_group.meta for j in self.access_groups],
            "studies": [s.meta for s in self.studies]
        }

    def __repr__(self):
        return "<Account %s>" % self.email


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
        db.Integer,
        db.ForeignKey("account.id"),
        primary_key=True
    )

    access_group_id = db.Column(
        db.Integer,
        db.ForeignKey("access_group.id", ondelete="CASCADE"),
        primary_key=True
    )

    account = db.relationship("Account", back_populates="access_groups")
    access_group = db.relationship("AccessGroup", back_populates="accounts")

    @hybrid_property
    def primary_key(self):
        """
        tuple of int: an entry's primary key.
        """
        return self.account_id, self.access_group_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.account_id, cls.access_group_id)

    def __repr__(self):
        return "<JoinAccountAccessGroup %s-%s>" % self.primary_key


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
        db.Integer,
        db.ForeignKey("account.id"),
        primary_key=True
    )

    study_id = db.Column(
        db.Integer,
        db.ForeignKey("study.id", ondelete="CASCADE"),
        primary_key=True
    )

    account = db.relationship("Account", back_populates="studies")
    study = db.relationship("Study")

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("role.id", ondelete="CASCADE"),
        nullable=False
    )

    role = db.relationship("Role")

    @hybrid_property
    def primary_key(self):
        """
        tuple of int: an entry's primary key.
        """
        return self.account_id, self.study_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.account_id, cls.study_id)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            **self.study.meta,
            "role": self.role.meta
        }

    def __repr__(self):
        return "<JoinAccountStudy %s-%s>" % self.primary_key


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
            "and_(" +
            "   AccessGroup.id == JoinAccountAccessGroup.access_group_id," +
            "   JoinAccountAccessGroup.account_id == Account.id," +
            "   Account.is_archived == False" +
            ")"
        )
    )

    permissions = db.relationship(
        "JoinAccessGroupPermission",
        back_populates="access_group",
        cascade="all, delete-orphan"
    )

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "name": self.name,
            "app": self.app.meta,
            "permissions": [p.meta for p in self.permissions]
        }

    def __repr__(self):
        return "<AccessGroup %s>" % self.name


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
        primary_key=True
    )

    permission_id = db.Column(
        db.Integer,
        db.ForeignKey("permission.id", ondelete="CASCADE"),
        primary_key=True
    )

    access_group = db.relationship("AccessGroup", back_populates="permissions")
    permission = db.relationship("Permission")

    @hybrid_property
    def primary_key(self):
        """
        tuple of int: an entry's primary key
        """
        return self.access_group_id, self.permission_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.access_group_id, cls.permission_id)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return self.permission.meta

    def __repr__(self):
        return "<JoinAccessGroupPermission %s-%s>" % self.primary_key


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
        cascade="all, delete-orphan"
    )

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "name": self.name,
            "permissions": [p.meta for p in self.permissions]
        }

    def __repr__(self):
        return "<Role %s>" % self.name


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
        primary_key=True
    )

    permission_id = db.Column(
        db.Integer,
        db.ForeignKey("permission.id", ondelete="CASCADE"),
        primary_key=True
    )

    role = db.relationship("Role", back_populates="permissions")
    permission = db.relationship("Permission")

    @hybrid_property
    def primary_key(self):
        """
        tuple of int: an entry's primary key.
        """
        return self.role_id, self.permission_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.role_id, cls.permission_id)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return self.permission.meta

    def __repr__(self):
        return "<JoinRolePermission %s-%s>" % self.primary_key


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
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "value": self.value
        }

    def __repr__(self):
        return "<Action %s>" % self.value


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
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "value": self.value
        }

    def __repr__(self):
        return "<Resource %s>" % self.value


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
        db.Integer,
        db.ForeignKey("action.id", ondelete="CASCADE")
    )

    _resource_id = db.Column(
        db.Integer,
        db.ForeignKey("resource.id", ondelete="CASCADE")
    )

    _action = db.relationship("Action")
    _resource = db.relationship("Resource")

    @hybrid_property
    def action(self):
        """
        str: an entry's action
        """
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
        return select(Action.value)\
            .where(Action.id == cls._action_id)\
            .scalar_subquery()

    @hybrid_property
    def resource(self):
        """
        str: an entry's resource
        """
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
        return select(Resource.value)\
            .where(Resource.id == cls._resource_id)\
            .scalar_subquery()

    @validates("_action_id")
    def validate_action(self, key, val):
        """
        Ensure an entry's action cannot be modified.
        """
        if self._action_id is not None:
            raise ValueError("permission.action cannot be modified.")

        return val

    @validates("_resource_id")
    def validate_resource(self, key, val):
        """
        Ensure an entry's resource cannot be modified.
        """
        if self._resource_id is not None:
            raise ValueError("permission.resource cannot be modified.")

        return val

    @hybrid_property
    def definition(self):
        """
        tuple of str: an entry's (action, resource) definition
        """
        return self.action, self.resource

    @definition.expression
    def definition(cls):
        return tuple_(
            select(Action.value)
            .where(Action.id == cls._action_id)
            .scalar_subquery(),
            select(Resource.value)
            .where(Resource.id == cls._resource_id)
            .scalar_subquery()
        )

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "action": self.action,
            "resource": self.resource
        }

    def __repr__(self):
        return "<Permission %s %s>" % self.definition


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

    roles = db.relationship("JoinStudyRole", cascade="all, delete-orphan")

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
            "roles": [r.meta for r in self.roles],
            "dataSummary": self.data_summary,
            "isQi": self.is_qi
        }

    def __repr__(self):
        return "<Study %s>" % self.acronym


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
