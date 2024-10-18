from datetime import datetime, timezone
import json
from aws_portal.models import (
    AccessGroup, Account, App, JoinAccessGroupPermission, Role, Study,
    StudySubject
)
from tests.testing_utils import get_auth_headers, login_admin_account


def test_account(client):
    res = login_admin_account(client)
    headers = get_auth_headers(res)
    opts = "?app=1"
    res = client.get("/admin/account" + opts, headers=headers)
    data = json.loads(res.data)
    assert len(data) == 3
    assert data[0]["email"] == "foo@email.com"
    assert data[1]["email"] == "bar@email.com"


def test_account_create(post_admin):
    data = {
        "app": 1,
        "create": {
            "first_name": "foo",
            "last_name": "bar",
            "email": "baz@email.com",
            "password": "foo123456",
            "access_groups": [
                {"id": 1}
            ],
            "studies": [
                {
                    "id": 1,
                    "role": {
                        "id": 1
                    }
                }
            ]
        }
    }

    data = json.dumps(data)
    res = post_admin("/admin/account/create", data=data)
    data = json.loads(res.data)
    assert "msg" in data
    assert data["msg"] == "Account Created Successfully"

    q1 = Account.email == "baz@email.com"
    foo = Account.query.filter(q1).first()
    assert foo is not None
    assert foo.first_name == "foo"
    assert len(foo.access_groups) == 1
    assert foo.access_groups[0].access_group_id == 1
    assert len(foo.studies) == 1
    assert foo.studies[0].study_id == 1
    assert foo.studies[0].role_id == 1


def test_account_edit(post_admin):
    data = {
        "app": 1,
        "id": 1,
        "edit": {
            "first_name": "foo",
            "last_name": "bar",
            "access_groups": [
                {"id": 2}
            ],
            "studies": [
                {
                    "id": 2,
                    "role": {
                        "id": 2
                    }
                }
            ]
        }
    }

    data = json.dumps(data)
    res = post_admin("/admin/account/edit", data=data)
    data = json.loads(res.data)
    assert "msg" in data
    assert data["msg"] == "Account Edited Successfully"

    foo = Account.query.get(1)
    assert foo.first_name == "foo"
    assert len(foo.access_groups) == 1
    assert foo.access_groups[0].access_group_id == 2
    assert len(foo.studies) == 1
    assert foo.studies[0].study_id == 2
    assert foo.studies[0].role_id == 2


def test_account_archive(post_admin):
    data = {
        "app": 1,
        "id": 1
    }

    data = json.dumps(data)
    res = post_admin("/admin/account/archive", data=data)
    data = json.loads(res.data)
    assert "msg" in data
    assert data["msg"] == "Account Archived Successfully"

    foo = Account.query.get(1)
    assert foo.is_archived


def test_study(get_admin):
    opts = "?app=1"
    res = get_admin("/admin/study" + opts)
    data = json.loads(res.data)
    assert len(data) == 2
    assert data[0]["name"] == "foo"
    assert data[1]["name"] == "bar"


def test_study_create(post_admin):
    data = {
        "app": 1,
        "create": {
            "name": "baz",
            "acronym": "BAZ",
            "ditti_id": "BZ",
            "email": "baz@email.com"
        }
    }

    data = json.dumps(data)
    res = post_admin("/admin/study/create", data=data)
    data = json.loads(res.data)
    assert "msg" in data
    assert data["msg"] == "Study Created Successfully"

    q1 = Study.name == "baz"
    foo = Study.query.filter(q1).first()
    assert foo is not None
    assert foo.name == "baz"
    assert foo.acronym == "BAZ"
    assert foo.ditti_id == "BZ"
    assert foo.email == "baz@email.com"


def test_study_edit(post_admin):
    data = {
        "app": 1,
        "id": 1,
        "edit": {
            "name": "qux",
            "acronym": "QUX",
        }
    }

    data = json.dumps(data)
    res = post_admin("/admin/study/edit", data=data)
    data = json.loads(res.data)
    assert "msg" in data
    assert data["msg"] == "Study Edited Successfully"

    foo = Study.query.get(1)
    assert foo.name == "qux"
    assert foo.acronym == "QUX"


def test_study_archive(post_admin):
    data = {
        "app": 1,
        "id": 1
    }

    data = json.dumps(data)
    res = post_admin("/admin/study/archive", data=data)
    data = json.loads(res.data)
    assert "msg" in data
    assert data["msg"] == "Study Archived Successfully"

    foo = Study.query.get(1)
    assert foo.is_archived


def test_access_group(get_admin):
    opts = "?app=1"
    res = get_admin("/admin/access-group" + opts)
    data = json.loads(res.data)
    assert len(data) == 3
    assert data[1]["name"] == "foo"
    assert data[2]["name"] == "bar"


def test_access_group_create(post_admin):
    data = {
        "app": 1,
        "create": {
            "name": "baz",
            "app": 2,
            "permissions": [
                {
                    "action": "foo",
                    "resource": "qux"
                }
            ]
        }
    }

    data = json.dumps(data)
    res = post_admin("/admin/access-group/create", data=data)
    data = json.loads(res.data)
    assert "msg" in data
    assert data["msg"] == "Access Group Created Successfully"

    q1 = AccessGroup.name == "baz"
    foo = AccessGroup.query.filter(q1).first()
    assert foo.name == "baz"
    assert foo.app.name == "foo"
    assert len(foo.permissions) == 1
    assert foo.permissions[0].permission.action == "foo"


def test_access_group_edit(post_admin):
    data = {
        "app": 1,
        "id": 2,
        "edit": {
            "name": "baz",
            "app": 1
        }
    }

    data = json.dumps(data)
    res = post_admin("/admin/access-group/edit", data=data)
    data = json.loads(res.data)
    assert "msg" in data
    assert data["msg"] == "Access Group Edited Successfully"

    foo = AccessGroup.query.get(2)
    assert foo.name == "baz"
    assert len(foo.accounts) == 1
    assert foo.accounts[0].account.email == "foo@email.com"
    assert len(foo.permissions) == 1
    assert foo.permissions[0].permission.action == "foo"


def test_access_group_edit_permissions(post_admin):
    data = {
        "app": 1,
        "id": 2,
        "edit": {
            "permissions": [
                {
                    "action": "foo",
                    "resource": "qux"
                }
            ]
        }
    }

    foo = JoinAccessGroupPermission.query.get((2, 2))
    assert foo is not None

    data = json.dumps(data)
    res = post_admin("/admin/access-group/edit", data=data)
    data = json.loads(res.data)
    assert "msg" in data
    assert data["msg"] == "Access Group Edited Successfully"

    bar = AccessGroup.query.get(2)
    assert len(bar.permissions) == 1
    assert bar.permissions[0].permission.definition == ("foo", "qux")

    foo = JoinAccessGroupPermission.query.get((2, 2))
    assert foo is None


def test_access_group_archive(post_admin):
    data = {
        "app": 1,
        "id": 1
    }

    data = json.dumps(data)
    res = post_admin("/admin/access-group/archive", data=data)
    data = json.loads(res.data)
    assert "msg" in data
    assert data["msg"] == "Access Group Archived Successfully"

    foo = AccessGroup.query.get(1)
    assert foo.is_archived


def test_role(get_admin):
    opts = "?app=1"
    res = get_admin("/admin/role" + opts)
    data = json.loads(res.data)
    assert len(data) == 2
    assert data[0]["name"] == "foo"
    assert data[1]["name"] == "bar"


def test_role_create(post_admin):
    data = {
        "app": 1,
        "create": {
            "name": "baz",
            "permissions": [
                {
                    "action": "foo",
                    "resource": "baz"
                }
            ]
        }
    }

    data = json.dumps(data)
    res = post_admin("/admin/role/create", data=data)
    data = json.loads(res.data)
    assert "msg" in data
    assert data["msg"] == "Role Created Successfully"

    q1 = Role.name == "baz"
    foo = Role.query.filter(q1).first()
    assert foo is not None
    assert foo.name == "baz"
    assert len(foo.permissions) == 1
    assert foo.permissions[0].permission.action == "foo"
    assert foo.permissions[0].permission.resource == "baz"


def test_role_edit(post_admin):
    data = {
        "app": 1,
        "id": 1,
        "edit": {
            "name": "baz",
            "permissions": [
                {
                    "action": "bar",
                    "resource": "qux"
                }
            ]
        }
    }

    data = json.dumps(data)
    res = post_admin("/admin/role/edit", data=data)
    data = json.loads(res.data)
    assert "msg" in data
    assert data["msg"] == "Role Edited Successfully"

    q1 = Role.name == "baz"
    foo = Role.query.filter(q1).first()
    assert foo is not None
    assert foo.name == "baz"
    assert len(foo.permissions) == 1
    assert foo.permissions[0].permission.action == "bar"
    assert foo.permissions[0].permission.resource == "qux"


def test_app(get_admin):
    opts = "?app=1"
    res = get_admin("/admin/app" + opts)
    data = json.loads(res.data)
    assert len(data) == 3
    assert data[1]["name"] == "foo"
    assert data[2]["name"] == "bar"


def test_app_create(post_admin):
    data = {
        "app": 1,
        "create": {
            "name": "baz"
        }
    }

    data = json.dumps(data)
    res = post_admin("/admin/app/create", data=data)
    data = json.loads(res.data)
    assert "msg" in data
    assert data["msg"] == "App Created Successfully"

    q1 = App.name == "baz"
    foo = App.query.filter(q1).first()
    assert foo is not None
    assert foo.name == "baz"


def test_app_edit(post_admin):
    data = {
        "app": 1,
        "id": 1,
        "edit": {
            "name": "baz"
        }
    }

    data = json.dumps(data)
    res = post_admin("/admin/app/edit", data=data)
    data = json.loads(res.data)
    assert "msg" in data
    assert data["msg"] == "App Edited Successfully"

    foo = App.query.get(1)
    assert foo.name == "baz"

def test_study_subject_create(post_admin):
    data = {
        "app": 1,
        "create": {
            "email": "study_subject@email.com",
            "studies": [
                {
                    "id": 1,
                    "expires_on": "2024-12-31T23:59:59Z",
                    "did_consent": True
                }
            ],
            "apis": [
                {
                    "id": 1,
                    "api_user_uuid": "api-user-uuid-1",
                    "scope": ["read", "write"],
                    "access_key_uuid": "access-key-uuid-1",
                    "refresh_key_uuid": "refresh-key-uuid-1"
                }
            ]
        }
    }

    # Send POST request to create StudySubject
    res = post_admin("/admin/study_subject/create", data=json.dumps(data))
    data = json.loads(res.data)
    
    # Assert response
    assert "msg" in data
    assert data["msg"] == "Study Subject Created Successfully"

    # Query the database to verify creation
    subject = StudySubject.query.filter(StudySubject.email == "study_subject@email.com").first()
    assert subject is not None
    assert subject.email == "study_subject@email.com"
    assert not subject.is_confirmed
    assert not subject.is_archived
    assert len(subject.studies) == 1
    join_study = subject.studies[0]
    assert join_study.study_id == 1
    assert join_study.did_consent is True
    assert join_study.expires_on.replace(tzinfo=timezone.utc) == datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    assert len(subject.apis) == 1
    join_api = subject.apis[0]
    assert join_api.api_id == 1
    assert join_api.api_user_uuid == "api-user-uuid-1"
    assert join_api.scope == ["read", "write"]
    assert join_api.access_key_uuid == "access-key-uuid-1"
    assert join_api.refresh_key_uuid == "refresh-key-uuid-1"

def test_study_subject_archive(post_admin):
    create_data = {
        "app": 1,
        "create": {
            "email": "study_subject@email.com",
            "studies": [
                {
                    "id": 2,
                    "expires_on": "2025-06-30T12:00:00Z",
                    "did_consent": False
                }
            ],
            "apis": [
                {
                    "id": 2,
                    "api_user_uuid": "api-user-uuid-2",
                    "scope": ["read"],
                    "access_key_uuid": "access-key-uuid-2",
                    "refresh_key_uuid": "refresh-key-uuid-2"
                }
            ]
        }
    }

    # Create the StudySubject
    res_create = post_admin("/admin/study_subject/create", data=json.dumps(create_data))
    data_create = json.loads(res_create.data)
    assert "msg" in data_create
    assert data_create["msg"] == "Study Subject Created Successfully"

    # Retrieve the created StudySubject's ID
    subject = StudySubject.query.filter(StudySubject.email == "study_subject@email.com").first()
    assert subject is not None
    subject_id = subject.id

    # Define the payload for archiving the StudySubject
    archive_data = {
        "app": 1,
        "id": subject_id
    }

    # Send POST request to archive StudySubject
    res_archive = post_admin("/admin/study_subject/archive", data=json.dumps(archive_data))
    data_archive = json.loads(res_archive.data)
    
    # Assert response
    assert "msg" in data_archive
    assert data_archive["msg"] == "Study Subject Archived Successfully"

    # Query the database to verify archiving
    archived_subject = StudySubject.query.get(subject_id)
    assert archived_subject.is_archived is True

