from base64 import b64encode
from datetime import datetime, timedelta, UTC
import os
import uuid

from flask import current_app
from flask_jwt_extended.utils import decode_token

from aws_portal.extensions import bcrypt, db
from aws_portal.models import (
    AccessGroup, Account, App, BlockedToken, JoinAccessGroupPermission,
    JoinAccountAccessGroup, JoinAccountStudy, JoinRolePermission,
    JoinStudyRole, Permission, Role, Study, StudySubject, JoinStudySubjectApi,
    JoinStudySubjectStudy, Api
)

uri = os.getenv("FLASK_DB")
if "localhost" not in uri:
    raise Exception(
        "The SQLAlchemy URI does not point to localhost. Run `source deploy-" +
        "dev.sh` before running pytest. Current URI:",
        uri
    )

apps = [
    {
        "name": "foo"
    },
    {
        "name": "bar"
    }
]

access_groups = [
    {
        "name": "foo"
    },
    {
        "name": "bar"
    }
]

accounts = [
    {
        "public_id": str(uuid.uuid4()),
        "created_on": datetime.now(UTC),
        "first_name": "John",
        "last_name": "Smith",
        "email": "foo@email.com",
        "is_confirmed": True,
        "_password": bcrypt.generate_password_hash("foo").decode("utf-8")
    },
    {
        "public_id": str(uuid.uuid4()),
        "created_on": datetime.now(UTC),
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "bar@email.com",
        "_password": bcrypt.generate_password_hash("bar").decode("utf-8")
    }
]

permissions = [
    {
        "action": "foo",
        "resource": "baz"
    },
    {
        "action": "bar",
        "resource": "baz"
    },
    {
        "action": "bar",
        "resource": "qux"
    },
    {
        "action": "Edit",
        "resource": "User"
    },
    {
        "action": "Create",
        "resource": "User"
    }
]

roles = [
    {
        "name": "foo"
    },
    {
        "name": "bar"
    }
]

studies = [
    {
        "name": "foo",
        "acronym": "FOO",
        "ditti_id": "FO",
        "email": "foo@email.com"
    },
    {
        "name": "bar",
        "acronym": "BAR",
        "ditti_id": "BR",
        "email": "bar@email.com"
    }
]

blocked_tokens = [
    {
        "jti": "foo",
        "created_on": datetime.now(UTC)
    },
    {
        "jti": "bar",
        "created_on": datetime.now(UTC)
    }
]

study_subjects = [
    {
        "created_on": datetime.now(UTC),
        "email": "foo@email.com",
        "is_confirmed": True,
    },
    {
        "created_on": datetime.now(UTC),
        "email": "bar@email.com",
        "is_confirmed": True,
    }
]

apis = [
    {
        "name": "foo",
    },
    {
        "name": "bar",
    }
]


def create_tables():
    for app in apps:
        db.session.add(App(**app))

    for access_group in access_groups:
        db.session.add(AccessGroup(**access_group))

    for account in accounts:
        db.session.add(Account(**account))

    for permission in permissions:
        p = Permission()
        p.action = permission["action"]
        p.resource = permission["resource"]
        db.session.add(p)

    for role in roles:
        db.session.add(Role(**role))

    for study in studies:
        db.session.add(Study(**study))

    for blocked_token in blocked_tokens:
        db.session.add(BlockedToken(**blocked_token))

    for study_subject in study_subjects:
        db.session.add(StudySubject(**study_subject))

    for api in apis:
        db.session.add(Api(**api))


def create_joins():
    q1 = AccessGroup.name == "foo"
    q2 = App.name == "foo"
    access_group = AccessGroup.query.filter(q1).first()
    access_group.app = App.query.filter(q2).first()

    q1 = AccessGroup.name == "bar"
    q2 = App.name == "bar"
    access_group = AccessGroup.query.filter(q1).first()
    access_group.app = App.query.filter(q2).first()

    q1 = AccessGroup.name == "foo"
    q2 = Permission.definition == ("foo", "baz")
    foo = JoinAccessGroupPermission(
        access_group=AccessGroup.query.filter(q1).first(),
        permission=Permission.query.filter(q2).first()
    )

    db.session.add(foo)

    q1 = AccessGroup.name == "bar"
    q2 = Permission.definition == ("bar", "baz")
    foo = JoinAccessGroupPermission(
        access_group=AccessGroup.query.filter(q1).first(),
        permission=Permission.query.filter(q2).first()
    )

    db.session.add(foo)

    q1 = Role.name == "foo"
    q2 = Permission.definition == ("foo", "baz")
    q3 = Permission.definition == ("Edit", "User")
    q4 = Permission.definition == ("Create", "User")
    foo = JoinRolePermission(
        role=Role.query.filter(q1).first(),
        permission=Permission.query.filter(q2).first()
    )

    bar = JoinRolePermission(
        role=Role.query.filter(q1).first(),
        permission=Permission.query.filter(q3).first()
    )

    baz = JoinRolePermission(
        role=Role.query.filter(q1).first(),
        permission=Permission.query.filter(q4).first()
    )

    db.session.add(foo)
    db.session.add(bar)
    db.session.add(baz)

    q1 = Role.name == "bar"
    q2 = Permission.definition == ("bar", "qux")
    foo = JoinRolePermission(
        role=Role.query.filter(q1).first(),
        permission=Permission.query.filter(q2).first()
    )

    db.session.add(foo)

    foo = Role.query.filter(Role.name == "foo").first()
    bar = Study.query.filter(Study.name == "foo").first()
    baz = JoinStudyRole(role=foo, study=bar)
    db.session.add(baz)

    foo = Role.query.filter(Role.name == "bar").first()
    bar = Study.query.filter(Study.name == "bar").first()
    baz = JoinStudyRole(role=foo, study=bar)
    db.session.add(baz)

    q1 = Account.email == "foo@email.com"
    q2 = AccessGroup.name == "foo"
    foo = JoinAccountAccessGroup(
        account=Account.query.filter(q1).first(),
        access_group=AccessGroup.query.filter(q2).first()
    )

    db.session.add(foo)

    q1 = Account.email == "bar@email.com"
    q2 = AccessGroup.name == "bar"
    foo = JoinAccountAccessGroup(
        account=Account.query.filter(q1).first(),
        access_group=AccessGroup.query.filter(q2).first()
    )

    db.session.add(foo)

    q1 = Account.email == "foo@email.com"
    q2 = Study.name == "foo"
    q3 = Role.name == "foo"
    foo = JoinAccountStudy(
        account=Account.query.filter(q1).first(),
        study=Study.query.filter(q2).first(),
        role=Role.query.filter(q3).first()
    )

    db.session.add(foo)

    q1 = Account.email == "bar@email.com"
    q2 = Study.name == "bar"
    q3 = Role.name == "bar"
    foo = JoinAccountStudy(
        account=Account.query.filter(q1).first(),
        study=Study.query.filter(q2).first(),
        role=Role.query.filter(q3).first()
    )

    db.session.add(foo)

    q1 = StudySubject.email == "foo@email.com"
    q2 = Study.name == "foo"
    foo = JoinStudySubjectStudy(
        study_subject=StudySubject.query.filter(q1).first(),
        study=Study.query.filter(q2).first(),
        expires_on=datetime.now(UTC) + timedelta(days=14),
    )

    db.session.add(foo)

    q1 = StudySubject.email == "bar@email.com"
    q2 = Study.name == "bar"
    foo = JoinStudySubjectStudy(
        study_subject=StudySubject.query.filter(q1).first(),
        study=Study.query.filter(q2).first(),
        expires_on=datetime.now(UTC) + timedelta(days=14),
    )


    q1 = StudySubject.email == "foo@email.com"
    q2 = Api.name == "foo"
    foo = JoinStudySubjectApi(
        study_subject=StudySubject.query.filter(q1).first(),
        api=Api.query.filter(q2).first(),
        api_user_uuid="foo",
        scope=["foo", "bar"],
        access_key_uuid=str(uuid.uuid4()),
        refresh_key_uuid=str(uuid.uuid4()),
    )

    db.session.add(foo)

    q1 = StudySubject.email == "bar@email.com"
    q2 = Api.name == "bar"
    foo = JoinStudySubjectApi(
        study_subject=StudySubject.query.filter(q1).first(),
        api=Api.query.filter(q2).first(),
        api_user_uuid="foo",
        scope=["foo", "bar"],
        access_key_uuid=str(uuid.uuid4()),
        refresh_key_uuid=str(uuid.uuid4()),
    )

    db.session.add(foo)


def login_test_account(name, client, password=None):
    q1 = Account.email == "%s@email.com" % name
    foo = Account.query.filter(q1).first()
    cred = b64encode(f"{foo.email}:{password or name}".encode())
    headers = {"Authorization": "Basic %s" % cred.decode()}
    res = client.post("/iam/login", headers=headers)

    return res


def login_admin_account(client):
    email = os.getenv("FLASK_ADMIN_EMAIL")
    password = os.getenv("FLASK_ADMIN_PASSWORD")
    cred = b64encode(f"{email}:{password}".encode())
    headers = {"Authorization": "Basic %s" % cred.decode()}
    res = client.post("/iam/login", headers=headers)

    return res


def get_auth_headers(res, headers=None):
    csrf_token = res.json["csrfAccessToken"]
    headers = headers or {}
    csrf_header_name = current_app.config["JWT_ACCESS_CSRF_HEADER_NAME"]
    headers.update({csrf_header_name: csrf_token})

    if "jwt" in res.json:
        headers.update({"Authorization": "Bearer " + res.json["jwt"]})

    return headers


def get_account_from_response(res):
    access_token = res.json["jwt"]
    public_id = decode_token(access_token)["sub"]
    account = Account.query.filter(Account.public_id == public_id).first()

    return account
