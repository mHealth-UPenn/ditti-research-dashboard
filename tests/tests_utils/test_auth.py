from datetime import timedelta
import json
from time import sleep
from flask import Blueprint, jsonify
import pytest
from aws_portal.app import create_app
from aws_portal.extensions import db
from aws_portal.models import (
    AccessGroup, App, JoinAccountAccessGroup, JoinAccountStudy, Study, init_db
)
from aws_portal.utils.auth import auth_required
from tests.testing_utils import (
    create_joins, create_tables, get_account_from_response,
    get_cookie_from_response, get_csrf_headers, login_test_account
)

blueprint = Blueprint('test', __name__, url_prefix='/test')


def get_user_app_id(account):
    foo = App.query.join(AccessGroup)\
        .join(JoinAccountAccessGroup)\
        .filter(JoinAccountAccessGroup.account_id == account.id)\
        .first()

    return foo.id


def get_user_study_id(account):
    foo = Study.query.join(JoinAccountStudy)\
        .filter(JoinAccountStudy.account_id == account.id)\
        .first()

    return foo.id


@blueprint.route('/get-auth-required-action')
@auth_required('foo')
def get_auth_required_action():
    return jsonify({'msg': 'OK'})


@blueprint.route('/get-auth-required-resource')
@auth_required('bar', 'baz')
def get_auth_required_resource():
    return jsonify({'msg': 'OK'})


@blueprint.route('/post-auth-required-action', methods=['POST'])
@auth_required('foo')
def post_auth_required_action():
    return jsonify({'msg': 'OK'})


@blueprint.route('/post-auth-required-resource', methods=['POST'])
@auth_required('bar', 'baz')
def post_auth_required_resource():
    return jsonify({'msg': 'OK'})


@pytest.fixture
def app():
    app = create_app(testing=True)
    app.register_blueprint(blueprint)

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


@pytest.fixture
def timeout_client(app):
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=1)
    with app.test_client() as client:
        yield client


def test_get_auth_required_no_token(client):
    res = login_test_account('foo', client)
    account = get_account_from_response(res)
    # client.delete_cookie('localhost', 'access_token_cookie')
    app = get_user_app_id(account)
    study = get_user_study_id(account)
    resource = 'baz'
    opts = '?app=%s&study=%s&resource=%s' % (app, study, resource)
    res = client.get('/test/get-auth-required-action%s' % opts)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Missing Authorization Header'


def test_get_auth_required_timeout(timeout_client):
    res = login_test_account('foo', timeout_client)
    headers = {"Authorization": "Bearer " + res.json["jwt"]}
    account = get_account_from_response(res)
    app = get_user_app_id(account)
    study = get_user_study_id(account)
    resource = 'baz'
    opts = '?app=%s&study=%s&resource=%s' % (app, study, resource)
    sleep(2)

    res = timeout_client.get('/test/get-auth-required-action%s' % opts, headers=headers)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Token has expired'


def test_get_auth_required_after_logout(client):
    res = login_test_account('foo', client)
    headers = get_csrf_headers(res)
    client.post('/iam/logout', headers=headers)
    account = get_account_from_response(res)
    app = get_user_app_id(account)
    study = get_user_study_id(account)
    resource = 'baz'
    opts = '?app=%s&study=%s&resource=%s' % (app, study, resource)
    res = client.get('/test/get-auth-required-action%s' % opts)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Missing Authorization Header'


def test_get_auth_required_after_logout_with_fake(client):
    res = login_test_account('foo', client)
    headers = get_csrf_headers(res)
    # headers = get_csrf_headers(res)
    client.post('/iam/logout', headers=headers)
    # access_token = res.json["jwt"]

    account = get_account_from_response(res)
    app = get_user_app_id(account)
    study = get_user_study_id(account)
    resource = 'baz'
    opts = '?app=%s&study=%s&resource=%s' % (app, study, resource)
    res = client.get('/test/get-auth-required-action%s' % opts, headers=headers)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Token has been revoked'


def test_post_auth_required_no_csrf(client):
    res = login_test_account('foo', client)
    headers = {"Authorization": "Bearer " + res.json["jwt"]}
    account = get_account_from_response(res)
    app = get_user_app_id(account)
    study = get_user_study_id(account)
    data = {'app': app, 'study': study, 'resource': 'baz'}
    res = client.post('/test/post-auth-required-action', json=data, headers=headers)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Missing CSRF token'


def test_get_auth_required_action(client):
    res = login_test_account('foo', client)
    headers = {"Authorization": "Bearer " + res.json["jwt"]}
    account = get_account_from_response(res)
    app = get_user_app_id(account)
    study = get_user_study_id(account)
    resource = 'baz'
    opts = '?app=%s&study=%s&resource=%s' % (app, study, resource)
    res = client.get('/test/get-auth-required-action%s' % opts, headers=headers)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'OK'


def test_get_auth_required_resource_unauthorized(client):
    res = login_test_account('foo', client)
    headers = {"Authorization": "Bearer " + res.json["jwt"]}
    account = get_account_from_response(res)
    app = get_user_app_id(account)
    study = get_user_study_id(account)
    opts = '?app=%s&study=%s' % (app, study)
    res = client.get('/test/get-auth-required-resource%s' % opts, headers=headers)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Unauthorized Request'


def test_get_auth_required_resource(client):
    res = login_test_account('bar', client)
    headers = {"Authorization": "Bearer " + res.json["jwt"]}
    account = get_account_from_response(res)
    app = get_user_app_id(account)
    study = get_user_study_id(account)
    opts = '?app=%s&study=%s' % (app, study)
    res = client.get('/test/get-auth-required-resource%s' % opts, headers=headers)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'OK'


def test_post_auth_required_action_unauthorized(client):
    res = login_test_account('bar', client)
    headers = get_csrf_headers(res)
    account = get_account_from_response(res)
    app = get_user_app_id(account)
    study = get_user_study_id(account)
    data = {'app': app, 'study': study, 'resource': 'baz'}
    data = json.dumps(data)
    res = client.post(
        '/test/post-auth-required-action',
        content_type='application/json',
        data=data,
        headers=headers
    )

    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Unauthorized Request'


def test_post_auth_required_action(client):
    res = login_test_account('foo', client)
    account = get_account_from_response(res)
    app = get_user_app_id(account)
    study = get_user_study_id(account)
    data = {'app': app, 'study': study, 'resource': 'baz'}
    data = json.dumps(data)
    headers = get_csrf_headers(res)
    res = client.post(
        '/test/post-auth-required-action',
        content_type='application/json',
        data=data,
        headers=headers
    )

    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'OK'


def test_post_auth_required_resource_unauthorized(client):
    res = login_test_account('foo', client)
    account = get_account_from_response(res)
    app = get_user_app_id(account)
    study = get_user_study_id(account)
    data = {'app': app, 'study': study}
    data = json.dumps(data)
    headers = get_csrf_headers(res)
    res = client.post(
        '/test/post-auth-required-resource',
        content_type='application/json',
        data=data,
        headers=headers
    )

    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Unauthorized Request'


def post_auth_required_resource(client):
    res = login_test_account('bar', client)
    account = get_account_from_response(res)
    app = get_user_app_id(account)
    study = get_user_study_id(account)
    data = {'app': app, 'study': study}
    data = json.dumps(data)
    headers = get_csrf_headers(res)
    res = client.post(
        '/test/post-auth-required-resource',
        content_type='application/json',
        data=data,
        headers=headers
    )

    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'OK'
