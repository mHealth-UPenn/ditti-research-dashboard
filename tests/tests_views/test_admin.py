from flask import json
import pytest
from aws_portal.app import create_app
from aws_portal.models import (
    Account, init_admin_account, init_admin_app, init_admin_group, init_db
)
from tests.testing_utils import get_csrf_headers, login_admin_account


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


def test_user_create(client):
    res = login_admin_account(client)
    headers = get_csrf_headers(res)
    data = {
        'group': 1,
        'first-name': 'foo',
        'last-name': 'bar',
        'email': 'foo@email.com',
        'password': 'foo'
    }

    res = client.post(
        '/admin/account/create',
        content_type='multipart/form-data',
        data=data,
        headers=headers
    )

    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Account Created Successfully'

    q1 = Account.email == 'foo@email.com'
    foo = Account.query.filter(q1).first()
    assert foo is not None
    assert foo.first_name == 'foo'
    assert foo.last_name == 'bar'
    assert foo.check_password('foo')
