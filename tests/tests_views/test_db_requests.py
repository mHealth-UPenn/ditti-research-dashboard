import json
from tests.testing_utils import get_csrf_headers, login_admin_account, login_test_account


def test_apps(client):
    res = login_test_account('foo', client)
    headers = get_csrf_headers(res)
    res = client.get('/db/get-apps', headers=headers)
    res = json.loads(res.data)
    assert len(res) == 1
    assert res[0]['name'] == 'foo'


def test_apps_admin(client):
    res = login_admin_account(client)
    headers = get_csrf_headers(res)
    res = client.get('/db/get-apps', headers=headers)
    res = json.loads(res.data)
    assert len(res) == 1
    assert res[0]['name'] == 'Admin Dashboard'


def test_studies(client):
    res = login_test_account('foo', client)
    headers = get_csrf_headers(res)
    opts = '?app=2'
    res = client.get('/db/get-studies' + opts, headers=headers)
    res = json.loads(res.data)
    assert len(res) == 1
    assert res[0]['name'] == 'foo'


def test_study_details(client):
    res = login_test_account('foo', client)
    headers = get_csrf_headers(res)
    opts = '?app=2&study=1'
    res = client.get('/db/get-study-details' + opts, headers=headers)
    res = json.loads(res.data)
    assert 'name' in res
    assert res['name'] == 'foo'
    assert 'acronym' in res
    assert 'dittiId' in res


def test_study_details_invalid_study(client):
    res = login_test_account('foo', client)
    headers = get_csrf_headers(res)
    opts = '?app=2&study=2'
    res = client.get('/db/get-study-details' + opts, headers=headers)
    res = json.loads(res.data)
    assert res == {}


def test_study_contacts(client):
    res = login_test_account('foo', client)
    headers = get_csrf_headers(res)
    opts = '?app=2&study=1'
    res = client.get('/db/get-study-contacts' + opts, headers=headers)
    res = json.loads(res.data)
    assert len(res) == 1
    assert 'fullName' in res[0]
    assert res[0]['fullName'] == 'John Smith'
    assert 'role' in res[0]
    assert res[0]['role'] == 'foo'


def test_study_contacts_invalid_study(client):
    res = login_test_account('foo', client)
    headers = get_csrf_headers(res)
    opts = '?app=2&study=2'
    res = client.get('/db/get-study-contacts' + opts, headers=headers)
    res = json.loads(res.data)
    assert len(res) == 0


def test_account_details(client):
    res = login_test_account('foo', client)
    headers = get_csrf_headers(res)
    res = client.get('/db/get-account-details', headers=headers)
    res = json.loads(res.data)
    assert 'firstName' in res
    assert res['firstName'] == 'John'
