import json
import pytest
from aws_portal.app import create_app
from aws_portal.models import (
    init_admin_account, init_admin_app, init_admin_group, init_db
)
from tests.testing_utils import (
    create_joins, create_tables, create_test_access_group,
    login_admin_account, login_test_account
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
    assert res[0]['Name'] == 'foo'


def test_apps_admin(client):
    login_admin_account(client)
    res = client.get('/db/get-apps')
    res = json.loads(res.data)
    assert len(res) == 1
    assert res[0]['Name'] == 'Admin Dashboard'


def test_studies(client):
    login_test_account('foo', client)
    opts = '?group=2'
    res = client.get('/db/get-studies' + opts)
    res = json.loads(res.data)
    assert len(res) == 1
    assert res[0]['Name'] == 'foo'


def test_study_details():
    raise NotImplementedError


def test_study_contacts():
    raise NotImplementedError


def test_account_details():
    raise NotImplementedError
