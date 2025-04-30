from flask import json
from moto import mock_aws
import pytest
from unittest.mock import patch, MagicMock
from backend.utils.aws import Connection, Loader, Query
from tests.testing_utils import mock_researcher_auth_for_testing


@pytest.fixture
def researcher_headers(client):
    """Fixture providing researcher authentication headers"""
    return mock_researcher_auth_for_testing(client, is_admin=False)


@pytest.fixture
def researcher_post(client, researcher_headers):
    """Create a test POST request function with researcher authentication"""
    def _post(url, data=None, **kwargs):
        return client.post(url, data=data, content_type="application/json", headers=researcher_headers, **kwargs)
    return _post


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

    res = post_admin("/aws/user/create", data=json.dumps(data))
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
def test_user_edit_invalid_study_ditti_id(post_admin):
    data = {
        "group": 2,
        "study": 1,
        "app": 1,
        "user_permission_id": "QU000",
        "edit": {
            "information": "foo"
        }
    }

    res = post_admin("/aws/user/edit", data=json.dumps(data))
    res = json.loads(res.data)
    assert "msg" in res
    assert res["msg"] == "Invalid study Ditti ID: QU"


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

    res = post_admin("/aws/user/edit", data=json.dumps(data))
    res = json.loads(res.data)
    assert "msg" in res
    assert res["msg"] == "Invalid study or study subject Ditti ID: FO000#"


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

    res = post_admin("/aws/user/edit", data=json.dumps(data))
    res = json.loads(res.data)
    assert "msg" in res
    assert res["msg"] == "Ditti ID not found: FO001"


@mock_aws
@pytest.mark.skip(reason="Must create mock for requests")
def test_user_edit(researcher_post):
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

    res = researcher_post("/aws/user/edit", data=json.dumps(data))
    res = json.loads(res.data)
    assert "msg" in res
    assert res["msg"] == "User Successfully Edited"

    res = Query("User", query).scan()
    assert len(res["Items"]) == 1
    assert "information" in res["Items"][0]
    assert res["Items"][0]["information"] == "foo"

    data["edit"]["information"] = ""
    res = researcher_post("/aws/user/edit", data=json.dumps(data))
    res = json.loads(res.data)
    assert "msg" in res
    assert res["msg"] == "User Successfully Edited"

    res = Query("User", query).scan()
    assert len(res["Items"]) == 1
    assert "information" in res["Items"][0]
    assert res["Items"][0]["information"] == ""
