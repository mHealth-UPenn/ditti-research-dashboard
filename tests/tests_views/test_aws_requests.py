from flask import json
from moto import mock_aws
import pytest
from aws_portal.utils.aws import Connection, Loader, Query
from tests.testing_utils import login_admin_account


@mock_aws
def test_scan_invalid(get_admin):
    opts = "?app=1"
    opts = opts + "&group=1"
    opts = opts + "&key=User"
    opts = opts + "&query=user_permission_id==\"^abc123\""
    res = get_admin("/aws/scan" + opts)
    data = json.loads(res.data)
    assert "msg" in data
    assert data["msg"] == "Invalid Query"


@mock_aws
def test_scan(get_admin):
    opts = "?app=1"
    opts = opts + "&group=1"
    opts = opts + "&key=User"
    opts = opts + "&query=user_permission_id==\"abc123\""
    res = get_admin("/aws/scan" + opts)
    data = json.loads(res.data)
    assert len(data) == 1


@mock_aws
@pytest.mark.skip(reason="Must create mock for requests")
def test_user_create(post_admin):
    data = {
        "group": 2,
        "study": 1,
        "app": 1,
        "create": {
            "exp_time": "1900-01-01T09:00:00.000Z",
            "tap_permission": True,
            "team_email": "foo@email.com",
            "user_permission_id": "foo",
            "information": "foo"
        }
    }

    data = json.dumps(data)
    res = post_admin("/aws/user/create", data=data)
    res = json.loads(res.data)
    assert "msg" in res
    assert res["msg"] == "User Created Successfully"

    query = "user_permission_id==\"foo\""
    bar = Query("User", query)
    res = bar.scan()
    assert len(res["Items"]) == 1
    assert "exp_time" in res["Items"][0]
    assert res["Items"][0]["exp_time"] == "1900-01-01T09:00:00.000Z"
    assert "tap_permission" in res["Items"][0]
    assert res["Items"][0]["tap_permission"]
    assert "team_email" in res["Items"][0]
    assert res["Items"][0]["team_email"] == "foo@email.com"
    assert "user_permission_id" in res["Items"][0]
    assert res["Items"][0]["user_permission_id"] == "foo"
    assert "information" in res["Items"][0]
    assert res["Items"][0]["information"] == "foo"

    connection = Connection()
    connection.open_connection("dynamodb")
    loader = Loader("DittiApp", "User")
    loader.connect(connection)
    loader.load_table()
    res = loader.table.delete_item(Key={"id": res["Items"][0]["id"]})

    res = bar.scan()
    assert len(res["Items"]) == 0


@mock_aws
def test_user_edit_invalid_acronym(post_admin):
    data = {
        "group": 2,
        "study": 1,
        "app": 1,
        "user_permission_id": "QU000",
        "edit": {
            "information": "foo"
        }
    }

    data = json.dumps(data)
    res = post_admin("/aws/user/edit", data=data)
    res = json.loads(res.data)
    assert "msg" in res
    assert res["msg"] == "Invalid study acronym: QU"


@mock_aws
def test_user_edit_invalid_id(post_admin):
    data = {
        "group": 2,
        "study": 1,
        "app": 1,
        "user_permission_id": "FO000#",
        "edit": {
            "information": "foo"
        }
    }

    data = json.dumps(data)
    res = post_admin("/aws/user/edit", data=data)
    res = json.loads(res.data)
    assert "msg" in res
    assert res["msg"] == "Invalid Ditti ID: FO000#"


@mock_aws
def test_user_edit_id_not_found(post_admin):
    data = {
        "group": 2,
        "study": 1,
        "app": 1,
        "user_permission_id": "FO001",
        "edit": {
            "information": "foo"
        }
    }

    data = json.dumps(data)
    res = post_admin("/aws/user/edit", data=data)
    res = json.loads(res.data)
    assert "msg" in res
    assert res["msg"] == "Ditti ID not found: FO001"


@mock_aws
@pytest.mark.skip(reason="Must create mock for requests")
def test_user_edit(post):
    query = "user_permission_id==\"FO000\""
    data = {
        "group": 2,
        "study": 1,
        "app": 1,
        "user_permission_id": "FO000",
        "edit": {
            "information": "foo"
        }
    }

    res = Query("User", query).scan()
    assert len(res["Items"]) == 1
    assert "information" in res["Items"][0]
    assert res["Items"][0]["information"] == ""

    data = json.dumps(data)
    res = post("/aws/user/edit", data=data)
    res = json.loads(res.data)
    assert "msg" in res
    assert res["msg"] == "User Successfully Edited"

    res = Query("User", query).scan()
    assert len(res["Items"]) == 1
    assert "information" in res["Items"][0]
    assert res["Items"][0]["information"] == "foo"

    data = json.loads(data)
    data["edit"]["information"] = ""
    data = json.dumps(data)
    res = post("/aws/user/edit", data=data)
    res = json.loads(res.data)
    assert "msg" in res
    assert res["msg"] == "User Successfully Edited"

    res = Query("User", query).scan()
    assert len(res["Items"]) == 1
    assert "information" in res["Items"][0]
    assert res["Items"][0]["information"] == ""
