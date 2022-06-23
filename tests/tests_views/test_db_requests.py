import json
import pytest
from aws_portal.app import create_app
from aws_portal.models import (
    init_admin_account, init_admin_app, init_admin_group, init_db
)
from tests.testing_utils import (
    create_joins, create_tables, login_admin_account, login_test_account
)


@pytest.fixture
def app():
    app = create_app(testing=True)
    with app.app_context():
        init_db()
        init_admin_app()
        init_admin_group()
        init_admin_account()
        create_tables()
        create_joins()
        yield app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


def test_apps(client):
    login_test_account('foo', client)
    res = client.get('/db/get-apps')
    res = json.loads(res.data)
    assert len(res) == 1
    assert res[0]['name'] == 'foo'


def test_apps_admin(client):
    login_admin_account(client)
    res = client.get('/db/get-apps')
    res = json.loads(res.data)
    assert len(res) == 1
    assert res[0]['name'] == 'Admin Dashboard'


def test_studies(client):
    login_test_account('foo', client)
    opts = '?app=2'
    res = client.get('/db/get-studies' + opts)
    res = json.loads(res.data)
    assert len(res) == 1
    assert res[0]['name'] == 'foo'


def test_studies_invalid_app(client):
    login_test_account('foo', client)
    opts = '?app=3'
    res = client.get('/db/get-studies' + opts)
    res = json.loads(res.data)
    assert len(res) == 0


def test_study_details(client):
    login_test_account('foo', client)
    opts = '?study=1'
    res = client.get('/db/get-study-details' + opts)
    res = json.loads(res.data)
    assert 'name' in res
    assert res['name'] == 'foo'
    assert 'acronym' in res
    assert 'dittiId' in res


def test_study_details_invalid_study(client):
    login_test_account('foo', client)
    opts = '?study=2'
    res = client.get('/db/get-study-details' + opts)
    res = json.loads(res.data)
    assert res == {}


def test_study_contacts(client):
    login_test_account('foo', client)
    opts = '?study=1'
    res = client.get('/db/get-study-contacts' + opts)
    res = json.loads(res.data)
    assert len(res) == 1
    assert 'FullName' in res[0]
    assert res[0]['FullName'] == 'John Smith'
    assert 'Role' in res[0]
    assert res[0]['Role'] == 'foo'


def test_study_contacts_invalid_study(client):
    login_test_account('foo', client)
    opts = '?study=2'
    res = client.get('/db/get-study-contacts' + opts)
    res = json.loads(res.data)
    assert len(res) == 0


def test_account_details(client):
    login_test_account('foo', client)
    res = client.get('/db/get-account-details')
    res = json.loads(res.data)
    assert 'FirstName' in res
    assert res['FirstName'] == 'John'
