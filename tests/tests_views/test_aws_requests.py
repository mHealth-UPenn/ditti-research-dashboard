from functools import partial
from flask import json
import pytest
from aws_portal.app import create_app
from aws_portal.extensions import db
from aws_portal.models import (
    init_admin_account, init_admin_app, init_admin_group, init_db
)
from aws_portal.utils.aws import Connection, Loader, Query
from tests.testing_utils import (
    create_joins, create_tables, get_csrf_headers, login_admin_account,
    login_test_account
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
        db.session.commit()
        yield app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def post(client):
    res = login_test_account('foo', client)
    headers = get_csrf_headers(res)
    post = partial(
        client.post,
        content_type='application/json',
        headers=headers
    )

    yield post


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


def test_user_create(post):
    data = {
        'group': 2,
        'study': 1,
        'app': 'DittiApp',
        'create': {
            'exp_time': '1900-01-01T09:00:00.000Z',
            'tap_permission': True,
            'team_email': 'foo@email.com',
            'user_permission_id': 'foo',
            'information': 'foo'
        }
    }

    data = json.dumps(data)
    res = post('/aws/user/create', data=data)
    res = json.loads(res.data)
    assert 'msg' in res
    assert res['msg'] == 'User Created Successfully'

    query = 'user_permission_id=="foo"'
    bar = Query('DittiApp', 'User', query)
    res = bar.scan()
    assert len(res['Items']) == 1
    assert 'exp_time' in res['Items'][0]
    assert res['Items'][0]['exp_time'] == '1900-01-01T09:00:00.000Z'
    assert 'tap_permission' in res['Items'][0]
    assert res['Items'][0]['tap_permission']
    assert 'team_email' in res['Items'][0]
    assert res['Items'][0]['team_email'] == 'foo@email.com'
    assert 'user_permission_id' in res['Items'][0]
    assert res['Items'][0]['user_permission_id'] == 'foo'
    assert 'information' in res['Items'][0]
    assert res['Items'][0]['information'] == 'foo'

    connection = Connection()
    connection.open_connection('dynamodb')
    loader = Loader('DittiApp', 'User')
    loader.connect(connection)
    loader.load_table()
    res = loader.table.delete_item(Key={'id': res['Items'][0]['id']})

    res = bar.scan()
    assert len(res['Items']) == 0


def test_user_edit_invalid_acronym(post):
    data = {
        'group': 2,
        'study': 1,
        'app': 'DittiApp',
        'user_permission_id': 'QU000',
        'edit': {
            'information': 'foo'
        }
    }

    data = json.dumps(data)
    res = post('/aws/user/edit', data=data)
    res = json.loads(res.data)
    assert 'msg' in res
    assert res['msg'] == 'Invalid study acronym: QU'


def test_user_edit_invalid_id(post):
    data = {
        'group': 2,
        'study': 1,
        'app': 'DittiApp',
        'user_permission_id': 'FO000#',
        'edit': {
            'information': 'foo'
        }
    }

    data = json.dumps(data)
    res = post('/aws/user/edit', data=data)
    res = json.loads(res.data)
    assert 'msg' in res
    assert res['msg'] == 'Invalid Ditti ID: FO000#'


def test_user_edit_id_not_found(post):
    data = {
        'group': 2,
        'study': 1,
        'app': 'DittiApp',
        'user_permission_id': 'FO001',
        'edit': {
            'information': 'foo'
        }
    }

    data = json.dumps(data)
    res = post('/aws/user/edit', data=data)
    res = json.loads(res.data)
    assert 'msg' in res
    assert res['msg'] == 'Ditti ID not found: FO001'


def test_user_edit(post):
    query = 'user_permission_id=="FO000"'
    data = {
        'group': 2,
        'study': 1,
        'app': 'DittiApp',
        'user_permission_id': 'FO000',
        'edit': {
            'information': 'foo'
        }
    }

    res = Query('DittiApp', 'User', query).scan()
    assert len(res['Items']) == 1
    assert 'information' in res['Items'][0]
    assert res['Items'][0]['information'] == ''

    data = json.dumps(data)
    res = post('/aws/user/edit', data=data)
    res = json.loads(res.data)
    assert 'msg' in res
    assert res['msg'] == 'User Successfully Edited'

    res = Query('DittiApp', 'User', query).scan()
    assert len(res['Items']) == 1
    assert 'information' in res['Items'][0]
    assert res['Items'][0]['information'] == 'foo'

    data = json.loads(data)
    data['edit']['information'] = ''
    data = json.dumps(data)
    res = post('/aws/user/edit', data=data)
    res = json.loads(res.data)
    assert 'msg' in res
    assert res['msg'] == 'User Successfully Edited'

    res = Query('DittiApp', 'User', query).scan()
    assert len(res['Items']) == 1
    assert 'information' in res['Items'][0]
    assert res['Items'][0]['information'] == ''


def test_user_archive(client):
    raise NotImplementedError
