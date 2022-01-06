from flask import json
import pytest
from aws_portal.app import create_app
from aws_portal.models import (
    init_admin_account, init_admin_app, init_admin_group, init_db
)
from tests.testing_utils import login_admin_account


@pytest.fixture
def app():
    app = create_app(testing=True)
    with app.app_context():
        init_db()
        init_admin_app()
        init_admin_group()
        init_admin_account()
        yield app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


def test_scan_invalid(client):
    res = login_admin_account(client)
    opts = '?app=DittiApp'
    opts = opts + '&group=1'
    opts = opts + '&key=User'
    opts = opts + '&query=user_permission_id=="^abc123"'
    res = client.get('/aws/scan' + opts)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Invalid Query'


def test_scan(client):
    res = login_admin_account(client)
    opts = '?app=DittiApp'
    opts = opts + '&group=1'
    opts = opts + '&key=User'
    opts = opts + '&query=user_permission_id=="abc123"'
    res = client.get('/aws/scan' + opts)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Scan Successful'
    assert 'res' in data
    assert len(data['res']) == 1
