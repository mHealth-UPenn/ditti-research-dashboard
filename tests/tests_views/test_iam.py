from base64 import b64encode
import json
from time import sleep
from flask_jwt_extended import decode_token
from aws_portal.extensions import db
from aws_portal.models import Account, BlockedToken
from tests.testing_utils import get_csrf_headers, login_test_account


def test_check_login_no_token(client):
    res = client.get('/iam/check-login')
    assert res.status_code == 401


def test_check_login_expired_token(timeout_client):
    login_test_account('foo', timeout_client)
    sleep(2)
    res = timeout_client.get('/iam/check-login')
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Token has expired'


def test_check_login(client):
    login_test_account('foo', client)
    res = client.get('/iam/check-login')
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'User is logged in'


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
    assert data['msg'] == 'Login successful'

    access_cookie = res.json["jwt"]
    assert access_cookie is not None

    csrf_cookie = res.json["csrfAccessToken"]
    assert csrf_cookie is not None


def test_logout(client):
    res = login_test_account('foo', client)
    data = json.loads(res.data)
    assert res.status_code == 200
    assert 'msg' in data
    assert data['msg'] == 'Login successful'

    access_cookie = res.json["jwt"]
    assert access_cookie is not None

    csrf_cookie = res.json["csrfAccessToken"]
    assert csrf_cookie is not None

    headers = get_csrf_headers(res)
    res = client.post('/iam/logout', headers=headers)
    data = json.loads(res.data)
    assert res.status_code == 200
    assert 'msg' in data
    assert data['msg'] == 'Logout Successful'

    blocked_token = BlockedToken.query.all()[-1]
    old_token = decode_token(access_cookie['access_token_cookie'])['jti']
    assert old_token == blocked_token.jti

    access_cookie = res.json["jwt"]
    assert access_cookie['access_token_cookie'] == ''
