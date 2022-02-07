from base64 import b64encode
import json
import pytest
from flask_jwt_extended import decode_token
from aws_portal.app import create_app
from aws_portal.extensions import db
from aws_portal.models import Account, BlockedToken, init_db
from tests.testing_utils import (
    get_cookie_from_response, get_csrf_headers, login_test_account
)
from tests.test_models import create_joins, create_tables


@pytest.fixture
def app():
    app = create_app(testing=True)
    with app.app_context():
        init_db()
        create_tables()
        create_joins()
        db.session.commit()

        yield app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


def test_login_no_credentials(client):
    res = client.post('/iam/login')
    assert res.status_code == 401


def test_login_invalid_credentials(client):
    res = login_test_account('foo', client, 'bar')
    assert res.status_code == 403


def test_login_archived_account(client):
    q1 = Account.email == 'foo@email.com'
    foo = Account.query.filter(q1).first()
    assert foo is not None

    foo.is_archived = True
    db.session.commit()
    foo = Account.query.filter(q1).first()
    assert foo.is_archived

    cred = b64encode('foo@email.com:foo'.encode())
    headers = {'Authorization': 'Basic %s' % cred.decode()}
    res = client.post('/iam/login', headers=headers)
    assert res.status_code == 403


def test_login(client):
    res = login_test_account('foo', client)
    data = json.loads(res.data)
    assert res.status_code == 200
    assert 'msg' in data
    assert data['msg'] == 'Login Successful'

    access_cookie = get_cookie_from_response(res, 'access_token_cookie')
    assert access_cookie is not None
    assert access_cookie['path'] == '/'
    assert access_cookie['httponly'] is True
    assert 'samesite' not in access_cookie

    csrf_cookie = get_cookie_from_response(res, 'csrf_access_token')
    assert csrf_cookie is not None
    assert csrf_cookie['path'] == '/'
    assert 'httponly' not in csrf_cookie
    assert 'samesite' not in csrf_cookie


def test_logout(client):
    res = login_test_account('foo', client)
    data = json.loads(res.data)
    assert res.status_code == 200
    assert 'msg' in data
    assert data['msg'] == 'Login Successful'

    access_cookie = get_cookie_from_response(res, 'access_token_cookie')
    assert access_cookie is not None
    assert access_cookie['path'] == '/'
    assert access_cookie['httponly'] is True
    assert 'samesite' not in access_cookie

    csrf_cookie = get_cookie_from_response(res, 'csrf_access_token')
    assert csrf_cookie is not None
    assert csrf_cookie['path'] == '/'
    assert 'httponly' not in csrf_cookie
    assert 'samesite' not in csrf_cookie

    headers = get_csrf_headers(res)
    res = client.post('/iam/logout', headers=headers)
    data = json.loads(res.data)
    assert res.status_code == 200
    assert 'msg' in data
    assert data['msg'] == 'Logout Successful'

    blocked_token = BlockedToken.query.all()[-1]
    old_token = decode_token(access_cookie['access_token_cookie'])['jti']
    assert old_token == blocked_token.jti

    access_cookie = get_cookie_from_response(res, 'access_token_cookie')
    assert access_cookie['access_token_cookie'] == ''
