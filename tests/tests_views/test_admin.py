import json
from aws_portal.models import (
    AccessGroup, Account, App, JoinAccessGroupPermission, Role, Study
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
