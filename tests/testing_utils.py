from base64 import b64encode
from datetime import datetime, timedelta, UTC
import os
import uuid
import time
import json
import jwt
import pytest
import boto3
from flask import current_app, jsonify
from flask_jwt_extended.utils import decode_token
from unittest.mock import patch, MagicMock

from aws_portal.extensions import bcrypt, db
from aws_portal.models import (
    AccessGroup, Account, App, BlockedToken, JoinAccessGroupPermission,
    JoinAccountAccessGroup, JoinAccountStudy, JoinRolePermission,
    JoinStudyRole, Permission, Role, Study, StudySubject, JoinStudySubjectApi,
    JoinStudySubjectStudy, Api
)

# Validate the SQLAlchemy URI
uri = os.getenv("FLASK_DB")
if "localhost" not in uri:
    raise Exception(
        "The SQLAlchemy URI does not point to localhost. Run `source deploy-" +
        "dev.sh` before running pytest. Current URI:",
        uri
    )

# Test data for various models
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
        "email": "foo@study.com",
        "is_archived": False,
        "default_expiry_delta": 14,
        "consent_information": "foo",
        "data_summary": None,
        "is_qi": False
    },
    {
        "name": "bar",
        "acronym": "BAR",
        "ditti_id": "BR",
        "email": "bar@study.com",
        "is_archived": False,
        "default_expiry_delta": 14,
        "consent_information": "foo",
        "data_summary": None,
        "is_qi": False
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
        "ditti_id": "ditti_foo_123",
    },
    {
        "created_on": datetime.now(UTC),
        "ditti_id": "ditti_bar_456",
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
    # Add Apps
    for app_data in apps:
        db.session.add(App(**app_data))

    # Add AccessGroups
    for access_group_data in access_groups:
        db.session.add(AccessGroup(**access_group_data))

    # Add Accounts
    for account_data in accounts:
        db.session.add(Account(**account_data))

    # Add Permissions
    for permission_data in permissions:
        p = Permission()
        p.action = permission_data["action"]
        p.resource = permission_data["resource"]
        db.session.add(p)

    # Add Roles
    for role_data in roles:
        db.session.add(Role(**role_data))

    # Add Studies with all required fields
    for study_data in studies:
        db.session.add(Study(**study_data))

    # Add BlockedTokens
    for blocked_token_data in blocked_tokens:
        db.session.add(BlockedToken(**blocked_token_data))

    # Add StudySubjects with ditti_id
    for study_subject_data in study_subjects:
        db.session.add(StudySubject(**study_subject_data))

    # Add APIs
    for api_data in apis:
        db.session.add(Api(**api_data))


def create_joins():
    # Associate AccessGroups with Apps
    foo_access_group = AccessGroup.query.filter(
        AccessGroup.name == "foo").first()
    foo_app = App.query.filter(App.name == "foo").first()
    foo_access_group.app = foo_app

    bar_access_group = AccessGroup.query.filter(
        AccessGroup.name == "bar").first()
    bar_app = App.query.filter(App.name == "bar").first()
    bar_access_group.app = bar_app

    # Associate AccessGroups with Permissions
    foo_permission = Permission.query.filter(
        Permission.action == "foo", Permission.resource == "baz"
    ).first()
    foo_join = JoinAccessGroupPermission(
        access_group=foo_access_group,
        permission=foo_permission
    )
    db.session.add(foo_join)

    bar_permission = Permission.query.filter(
        Permission.action == "bar", Permission.resource == "baz"
    ).first()
    bar_join = JoinAccessGroupPermission(
        access_group=bar_access_group,
        permission=bar_permission
    )
    db.session.add(bar_join)

    # Associate Roles with Permissions
    role_foo = Role.query.filter(Role.name == "foo").first()
    perm_foo_baz = Permission.query.filter(
        Permission.action == "foo", Permission.resource == "baz"
    ).first()
    perm_edit_user = Permission.query.filter(
        Permission.action == "Edit", Permission.resource == "User"
    ).first()
    perm_create_user = Permission.query.filter(
        Permission.action == "Create", Permission.resource == "User"
    ).first()

    join_role_perm_foo_baz = JoinRolePermission(
        role=role_foo,
        permission=perm_foo_baz
    )
    join_role_perm_edit_user = JoinRolePermission(
        role=role_foo,
        permission=perm_edit_user
    )
    join_role_perm_create_user = JoinRolePermission(
        role=role_foo,
        permission=perm_create_user
    )
    db.session.add(join_role_perm_foo_baz)
    db.session.add(join_role_perm_edit_user)
    db.session.add(join_role_perm_create_user)

    perm_bar_qux = Permission.query.filter(
        Permission.action == "bar", Permission.resource == "qux"
    ).first()
    role_bar = Role.query.filter(Role.name == "bar").first()
    join_role_perm_bar_qux = JoinRolePermission(
        role=role_bar,
        permission=perm_bar_qux
    )
    db.session.add(join_role_perm_bar_qux)

    # Associate Roles with Studies
    study_foo = Study.query.filter(Study.name == "foo").first()
    join_study_role_foo = JoinStudyRole(
        role=role_foo,
        study=study_foo
    )
    db.session.add(join_study_role_foo)

    study_bar = Study.query.filter(Study.name == "bar").first()
    join_study_role_bar = JoinStudyRole(
        role=role_bar,
        study=study_bar
    )
    db.session.add(join_study_role_bar)

    # Associate Accounts with AccessGroups
    account_foo = Account.query.filter(
        Account.email == "foo@email.com").first()
    account_bar = Account.query.filter(
        Account.email == "bar@email.com").first()

    join_account_access_group_foo = JoinAccountAccessGroup(
        account=account_foo,
        access_group=foo_access_group
    )
    join_account_access_group_bar = JoinAccountAccessGroup(
        account=account_bar,
        access_group=bar_access_group
    )
    db.session.add(join_account_access_group_foo)
    db.session.add(join_account_access_group_bar)

    # Associate Accounts with Studies and Roles
    join_account_study_foo = JoinAccountStudy(
        account=account_foo,
        study=study_foo,
        role=role_foo
    )
    join_account_study_bar = JoinAccountStudy(
        account=account_bar,
        study=study_bar,
        role=role_bar
    )
    db.session.add(join_account_study_foo)
    db.session.add(join_account_study_bar)

    # Associate StudySubjects with Studies
    study_subject_foo = StudySubject.query.filter(
        StudySubject.ditti_id == "ditti_foo_123"
    ).first()
    study_subject_bar = StudySubject.query.filter(
        StudySubject.ditti_id == "ditti_bar_456"
    ).first()

    join_study_subject_study_foo = JoinStudySubjectStudy(
        study_subject=study_subject_foo,
        study=study_foo,
        expires_on=datetime.now(UTC) + timedelta(days=14),
    )
    join_study_subject_study_bar = JoinStudySubjectStudy(
        study_subject=study_subject_bar,
        study=study_bar,
        expires_on=datetime.now(UTC) + timedelta(days=14),
    )
    db.session.add(join_study_subject_study_foo)
    db.session.add(join_study_subject_study_bar)

    # Associate StudySubjects with APIs
    api_foo = Api.query.filter(Api.name == "foo").first()
    api_bar = Api.query.filter(Api.name == "bar").first()

    join_study_subject_api_foo = JoinStudySubjectApi(
        study_subject=study_subject_foo,
        api=api_foo,
        api_user_uuid="foo",
        scope=["foo", "bar"]
    )
    join_study_subject_api_bar = JoinStudySubjectApi(
        study_subject=study_subject_bar,
        api=api_bar,
        api_user_uuid="bar",
        scope=["foo", "bar"]
    )
    db.session.add(join_study_subject_api_foo)
    db.session.add(join_study_subject_api_bar)


def login_test_account(name, client, password=None):
    # This function interacts with Account.email and remains unchanged
    q1 = Account.email == f"{name}@email.com"
    foo = Account.query.filter(q1).first()
    if not foo:
        raise ValueError(f"No account found with email: {name}@email.com")
    cred = b64encode(f"{foo.email}:{password or name}".encode())
    headers = {"Authorization": f"Basic {cred.decode()}"}
    res = client.post("/iam/login", headers=headers)

    return res


def login_admin_account(client):
    email = os.getenv("FLASK_ADMIN_EMAIL")
    password = os.getenv("FLASK_ADMIN_PASSWORD")
    if not email or not password:
        raise ValueError(
            "FLASK_ADMIN_EMAIL and FLASK_ADMIN_PASSWORD must be set.")
    cred = b64encode(f"{email}:{password}".encode())
    headers = {"Authorization": f"Basic {cred.decode()}"}
    res = client.post("/iam/login", headers=headers)

    return res


def get_auth_headers(res, headers=None):
    csrf_token = res.json.get("csrfAccessToken")
    if not csrf_token:
        raise ValueError("CSRF token not found in response.")
    headers = headers or {}
    csrf_header_name = current_app.config["JWT_ACCESS_CSRF_HEADER_NAME"]
    headers.update({csrf_header_name: csrf_token})

    jwt_token = res.json.get("jwt")
    if jwt_token:
        headers.update({"Authorization": f"Bearer {jwt_token}"})

    return headers


# New helper functions for Cognito authentication

def mock_cognito_tokens():
    """Generate mock Cognito tokens for testing."""
    return {
        "access_token": "mock_access_token",
        "id_token": "mock_id_token",
        "refresh_token": "mock_refresh_token",
        "expires_in": 3600
    }


def setup_auth_flow_session(client, user_type="participant"):
    """Set up a mock authentication flow session."""
    # Use the simpler session approach that was working in the test files
    with client.session_transaction() as flask_session:
        flask_session["cognito_state"] = "mock_state"
        flask_session["cognito_code_verifier"] = "mock_code_verifier"
        flask_session["cognito_nonce"] = "mock_nonce"
        flask_session["cognito_nonce_generated"] = int(
            datetime.now().timestamp())
        flask_session["auth_flow_user_type"] = user_type

    return "mock_state"
