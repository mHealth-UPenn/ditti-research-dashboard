from functools import partial
import json
import pytest
from aws_portal.app import create_app
from aws_portal.extensions import db
from aws_portal.models import (
    AccessGroup, Account, App, Permission, Role, Study, init_admin_account,
    init_admin_app, init_admin_group, init_db
)
from tests.testing_utils import (
    create_joins, create_tables, get_csrf_headers, login_admin_account
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
    res = login_admin_account(client)
    headers = get_csrf_headers(res)
    post = partial(
        client.post,
        content_type='application/json',
        headers=headers
    )

    yield post


def test_account(client):
    res = login_admin_account(client)
    opts = '?group=1'
    res = client.get('/admin/account' + opts)
    data = json.loads(res.data)
    assert len(data) == 3
    assert data[1]['Email'] == 'foo@email.com'
    assert data[2]['Email'] == 'bar@email.com'


def test_account_create(post):
    data = {
        'group': 1,
        'first_name': 'foo',
        'last_name': 'bar',
        'email': 'baz@email.com',
        'password': 'foo'
    }

    data = json.dumps(data)
    res = post('/admin/account/create', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Account Created Successfully'

    q1 = Account.email == 'baz@email.com'
    foo = Account.query.filter(q1).first()
    assert foo is not None
    assert foo.first_name == 'foo'
    assert foo.last_name == 'bar'
    assert foo.check_password('foo')


def test_account_edit(post):
    data = {
        'group': 1,
        'id': 1,
        'edit': {
            'first_name': 'foo',
            'last_name': 'bar',
        }
    }

    data = json.dumps(data)
    res = post('/admin/account/edit', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Account Edited Successfully'

    foo = Account.query.get(1)
    assert foo.first_name == 'foo'
    assert foo.last_name == 'bar'


def test_account_edit_invalid(post):
    data = {
        'group': 1,
        'id': 1,
        'edit': {
            'foo': 'bar'
        }
    }

    data = json.dumps(data)
    res = post('/admin/account/edit', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Invalid attribute: foo'


def test_account_archive():
    raise Exception


def test_study(client):
    res = login_admin_account(client)
    opts = '?group=1'
    res = client.get('/admin/study' + opts)
    data = json.loads(res.data)
    assert len(data) == 2
    assert data[0]['Name'] == 'foo'
    assert data[1]['Name'] == 'bar'


def test_study_create(post):
    data = {
        'group': 1,
        'name': 'baz',
        'acronym': 'BAZ',
        'ditti_id': 'BZ'
    }

    res = post('/admin/study/create', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Study Created Successfully'

    q1 = Study.name == 'baz'
    foo = Study.query.filter(q1).first()
    assert foo is not None
    assert foo.name == 'baz'
    assert foo.acronym == 'BAZ'
    assert foo.ditti_id == 'BZ'


def test_study_edit(post):
    data = {
        'group': 1,
        'id': 1,
        'edit': {
            'name': 'qux',
            'acronym': 'QUX',
        }
    }

    res = post('/admin/account/edit', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Account Edited Successfully'

    foo = Study.query.get(1)
    assert foo.name == 'qux'
    assert foo.acronym == 'QUX'


def test_study_archive():
    raise Exception


def test_access_group(client):
    res = login_admin_account(client)
    opts = '?group=1'
    res = client.get('/admin/access-group' + opts)
    data = json.loads(res.data)
    assert len(data) == 2
    assert data[0]['Name'] == 'foo'
    assert data[1]['Name'] == 'bar'


def test_access_group_create(post):
    data = {
        'group': 1,
        'name': 'baz',
        'app': 1,
        'accounts': [
            1
        ],
        'roles': [
            {
                'name': 'baz',
                'permissions': [
                    {
                        'action': 'foo',
                        'resource': 'baz'
                    }
                ]
            }
        ],
        'permissions': [
            {
                'action': 'foo',
                'resource': 'qux'
            }
        ],
        'studies': [
            1
        ]
    }

    res = post('/admin/access-group/create', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Access Group Created Successfully'

    q1 = AccessGroup.name == 'baz'
    foo = AccessGroup.query.filter(q1).first()
    assert foo.name == 'baz'
    assert foo.app.name == 'foo'
    assert len(foo.accounts) == 1
    assert foo.accounts[0].email == 'foo@email.com'
    assert len(foo.roles) == 1
    assert foo.roles[0].name == 'baz'
    assert len(foo.roles[0].permissions) == 1
    assert foo.roles[0].permissions[0].id == 1
    assert len(foo.permissions) == 0
    assert foo.permissions[0].action == 'foo'
    assert len(foo.studies) == 1
    assert foo.studies[0].name == 'foo'


def test_access_group_edit(post):
    data = {
        'group': 1,
        'id': 1,
        'edit': {
            'name': 'baz',
            'roles': [
                {
                    'name': 'baz',
                    'permissions': [
                        {
                            'action': 'foo',
                            'resource': 'baz'
                        }
                    ]
                }
            ],
            'permissions': []
        }
    }

    res = post('/admin/access-group/edit', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Access Group Edited Successfully'

    q1 = Role.name == 'foo'
    q2 = Permission.definition == ('foo', 'baz')
    foo = AccessGroup.query.get(1)
    bar = Role.query.filter(q1).first()
    baz = Permission.query.filter(q2).first()
    assert foo.name == 'baz'
    assert len(foo.roles) == 1
    assert foo.roles[0].name == 'baz'
    assert len(foo.roles[0].permissions) == 1
    assert foo.roles[0].permissions[0].action == 'foo'
    assert len(foo.permissions) == 0
    assert bar is None
    assert baz is None


def test_access_group_archive():
    raise Exception


def test_role(client):
    res = login_admin_account(client)
    opts = '?group=1&access-group=1'
    res = client.get('/admin/role' + opts)
    data = json.loads(res.data)
    assert len(data) == 1
    assert data[0]['Name'] == 'foo'


def test_permission_from_access_group(client):
    res = login_admin_account(client)
    opts = '?group=1&access-group=1'
    res = client.get('/admin/permission' + opts)
    data = json.loads(res.data)
    assert len(data) == 1
    assert data[0]['Action'] == 'foo'


def test_permission_from_role(client):
    res = login_admin_account(client)
    opts = '?group=1&role=1'
    res = client.get('/admin/permission' + opts)
    data = json.loads(res.data)
    assert len(data) == 1
    assert data[0]['Action'] == 'foo'


def test_app():
    res = login_admin_account(client)
    opts = '?group=1'
    res = client.get('/admin/app' + opts)
    data = json.loads(res.data)
    assert len(data) == 2
    assert data[0]['Name'] == 'foo'
    assert data[0]['Name'] == 'bar'


def test_app_create(post):
    data = {
        'group': 1,
        'name': 'baz'
    }

    res = post('/admin/app/create', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'App Created Successfully'

    q1 = App.name == 'baz'
    foo = App.query.filter(q1).first()
    assert foo is not None
    assert foo.name == 'baz'


def test_app_edit():
    data = {
        'group': 1,
        'id': 1,
        'edit': {
            'name': 'baz'
        }
    }

    res = post('/admin/app/edit', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'App Edited Successfully'

    foo = App.query.get(1)
    assert foo.name == 'baz'


def test_app_archive():
    raise Exception
