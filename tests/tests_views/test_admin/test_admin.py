import json
from backend.models import AccessGroup, Account, App, JoinAccessGroupPermission, Role, Study


def test_account_create(post_admin):
    data = {
        "app": 1,
        "create": {
            "first_name": "foo",
            "last_name": "bar",
            "email": "baz@email.com",
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

    res = post_admin("/admin/account/create", data=data)
    data = json.loads(res.data)
    assert "msg" in data
    assert "Account Created Successfully" in data["msg"]

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
    # Case 1: Basic account edit
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

    # Case 2: Adding a valid phone number
    data = {
        "app": 1,
        "id": 1,
        "edit": {
            "phone_number": "+14155551234"
        }
    }

    res = post_admin("/admin/account/edit", data=data)
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["msg"] == "Account Edited Successfully"

    # Verify phone number was saved
    foo = Account.query.get(1)
    assert foo.phone_number == "+14155551234"

    # Case 3: Invalid phone number format
    data = {
        "app": 1,
        "id": 1,
        "edit": {
            "phone_number": "+0123456789"  # Invalid: starts with +0
        }
    }

    res = post_admin("/admin/account/edit", data=data)
    assert res.status_code == 400
    data = json.loads(res.data)
    assert "phone number" in data["msg"].lower()

    # Case 4: Removing phone number
    data = {
        "app": 1,
        "id": 1,
        "edit": {
            "phone_number": ""  # Empty string to remove phone number
        }
    }

    res = post_admin("/admin/account/edit", data=data)
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["msg"] == "Account Edited Successfully"

    # Verify phone number was removed
    foo = Account.query.get(1)
    assert foo.phone_number is None

    # Case 5: Verify email changes are blocked
    data = {
        "app": 1,
        "id": 1,
        "edit": {
            "email": "newemail@example.com",
            "first_name": "UpdatedName"
        }
    }

    res = post_admin("/admin/account/edit", data=data)
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["msg"] == "Account Edited Successfully"

    # Verify first name was updated but email was not
    foo = Account.query.get(1)
    assert foo.first_name == "UpdatedName"
    assert foo.email != "newemail@example.com"  # Email should not change


def test_account_archive(post_admin):
    data = {
        "app": 1,
        "id": 1
    }

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
            "dittiId": "BZ",
            "email": "baz@email.com",
            "defaultExpiryDelta": 30,
            "consentInformation": "Consent text...",
            "dataSummary": "Data summary..."
        }
    }

    res = post_admin("/admin/study/create", data=data)
    response_data = json.loads(res.data)

    assert "msg" in response_data
    assert response_data["msg"] == "Study Created Successfully"

    created_study = Study.query.filter_by(name="baz").first()

    # Assert that the study exists in the database
    assert created_study is not None

    # Validate the study's attributes
    assert created_study.name == "baz"
    assert created_study.acronym == "BAZ"
    assert created_study.ditti_id == "BZ"
    assert created_study.email == "baz@email.com"
    assert created_study.default_expiry_delta == 30

    # Assert default values for optional fields
    assert created_study.is_archived == False
    assert created_study.is_qi == False

    # Other optional fields
    assert created_study.consent_information == "Consent text..."
    assert created_study.data_summary == "Data summary..."


def test_study_edit(post_admin):
    data = {
        "app": 1,
        "id": 1,
        "edit": {
            "name": "qux",
            "acronym": "QUX",
        }
    }

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

    res = post_admin("/admin/app/edit", data=data)
    data = json.loads(res.data)
    assert "msg" in data
    assert data["msg"] == "App Edited Successfully"

    foo = App.query.get(1)
    assert foo.name == "baz"
