import json
from tests.testing_utils import get_auth_headers, login_admin_account, login_test_account


def test_apps(get):
    res = get("/db/get-apps")
    res = json.loads(res.data)
    assert len(res) == 1
    assert res[0]["name"] == "foo"


def test_apps_admin(get_admin):
    res = get_admin("/db/get-apps")
    res = json.loads(res.data)
    assert len(res) == 1
    assert res[0]["name"] == "Admin Dashboard"


def test_studies(get):
    opts = "?app=2"
    res = get("/db/get-studies" + opts)
    res = json.loads(res.data)
    assert len(res) == 1
    assert res[0]["name"] == "foo"


def test_study_details(get):
    opts = "?app=2&study=1"
    res = get("/db/get-study-details" + opts)
    res = json.loads(res.data)
    assert "name" in res
    assert res["name"] == "foo"
    assert "acronym" in res
    assert "dittiId" in res


def test_study_details_invalid_study(get):
    opts = "?app=2&study=2"
    res = get("/db/get-study-details" + opts)
    res = json.loads(res.data)
    assert res == {}


def test_study_contacts(get):
    opts = "?app=2&study=1"
    res = get("/db/get-study-contacts" + opts)
    res = json.loads(res.data)
    assert len(res) == 1
    assert "fullName" in res[0]
    assert res[0]["fullName"] == "John Smith"
    assert "role" in res[0]
    assert res[0]["role"] == "foo"


def test_study_contacts_invalid_study(get):
    opts = "?app=2&study=2"
    res = get("/db/get-study-contacts" + opts)
    res = json.loads(res.data)
    assert len(res) == 0


def test_account_details(get):
    res = get("/db/get-account-details")
    res = json.loads(res.data)
    assert "firstName" in res
    assert res["firstName"] == "John"
