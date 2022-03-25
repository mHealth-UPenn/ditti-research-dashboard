from functools import partial
import json
import pytest
from aws_portal.app import create_app
from aws_portal.extensions import db
from aws_portal.models import (
    AccessGroup, Account, App, JoinAccessGroupPermission, JoinAccessGroupStudy,
    JoinAccountAccessGroup, Role, Study, init_admin_account, init_admin_app,
    init_admin_group, init_db
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
        'create': {
            'first_name': 'foo',
            'last_name': 'bar',
            'email': 'baz@email.com',
            'password': 'foo'
        }
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


def test_account_archive(post):
    data = {
        'group': 1,
        'id': 1
    }

    data = json.dumps(data)
    res = post('/admin/account/archive', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Account Archived Successfully'

    foo = Account.query.get(1)
    assert foo.is_archived


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
        'create': {
            'name': 'baz',
            'acronym': 'BAZ',
            'ditti_id': 'BZ'
        }
    }

    data = json.dumps(data)
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

    data = json.dumps(data)
    res = post('/admin/study/edit', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Study Edited Successfully'

    foo = Study.query.get(1)
    assert foo.name == 'qux'
    assert foo.acronym == 'QUX'


def test_study_archive(post):
    data = {
        'group': 1,
        'id': 1
    }

    data = json.dumps(data)
    res = post('/admin/study/archive', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Study Archived Successfully'

    foo = Study.query.get(1)
    assert foo.is_archived


def test_access_group(client):
    res = login_admin_account(client)
    opts = '?group=1'
    res = client.get('/admin/access-group' + opts)
    data = json.loads(res.data)
    assert len(data) == 3
    assert data[1]['Name'] == 'foo'
    assert data[2]['Name'] == 'bar'


def test_access_group_create(post):
    data = {
        'group': 1,
        'create': {
            'name': 'baz',
            'app': 2,
            'accounts': [
                2
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
    }

    data = json.dumps(data)
    res = post('/admin/access-group/create', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Access Group Created Successfully'

    q1 = AccessGroup.name == 'baz'
    foo = AccessGroup.query.filter(q1).first()
    assert foo.name == 'baz'
    assert foo.app.name == 'foo'
    assert len(foo.accounts) == 1
    assert foo.accounts[0].account.email == 'foo@email.com'
    assert len(foo.roles) == 1
    assert foo.roles[0].name == 'baz'
    assert len(foo.roles[0].permissions) == 1
    assert foo.roles[0].permissions[0].permission.id == 2
    assert len(foo.permissions) == 1
    assert foo.permissions[0].permission.action == 'foo'
    assert len(foo.studies) == 1
    assert foo.studies[0].study.name == 'foo'


def test_access_group_edit(post):
    data = {
        'group': 1,
        'id': 2,
        'edit': {
            'name': 'baz',
            'app': 1
        }
    }

    data = json.dumps(data)
    res = post('/admin/access-group/edit', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Access Group Edited Successfully'

    foo = AccessGroup.query.get(2)
    assert foo.name == 'baz'
    assert len(foo.accounts) == 1
    assert foo.accounts[0].account.email == 'foo@email.com'
    assert len(foo.roles) == 1
    assert foo.roles[0].name == 'foo'
    assert len(foo.roles[0].permissions) == 2
    assert foo.roles[0].permissions[0].permission.action == 'foo'
    assert len(foo.permissions) == 1
    assert len(foo.studies) == 1
    assert foo.studies[0].study.name == 'foo'


def test_access_group_edit_accounts(post):
    data = {
        'group': 1,
        'id': 2,
        'edit': {
            'accounts': [
                1, 3
            ]
        }
    }

    foo = JoinAccountAccessGroup.query.get((2, 2))
    assert foo is not None

    data = json.dumps(data)
    res = post('/admin/access-group/edit', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Access Group Edited Successfully'

    bar = AccessGroup.query.get(2)
    assert len(bar.accounts) == 2
    assert bar.accounts[0].account.email == 'admin@email.com'
    assert bar.accounts[1].account.email == 'bar@email.com'

    foo = JoinAccountAccessGroup.query.get((2, 2))
    assert foo is None


def test_access_group_edit_roles(post):
    data = {
        'group': 1,
        'id': 2,
        'edit': {
            'roles': [
                {
                    'name': 'bar',
                    'permissions': [
                        {
                            'action': '*',
                            'resource': '*'
                        }
                    ]
                }
            ]
        }
    }

    q = (Role.access_group_id == 2) & (Role.name == 'foo')
    foo = Role.query.filter(q).first()
    assert foo is not None

    data = json.dumps(data)
    res = post('/admin/access-group/edit', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Access Group Edited Successfully'

    bar = AccessGroup.query.get(2)
    assert len(bar.roles) == 1
    assert bar.roles[0].name == 'bar'
    assert len(bar.roles[0].permissions) == 1
    assert bar.roles[0].permissions[0].permission.definition == ('*', '*')

    q = (Role.access_group_id == 2) & (Role.name == 'foo')
    foo = Role.query.filter(q).first()
    assert foo is None


def test_access_group_edit_permissions(post):
    data = {
        'group': 1,
        'id': 2,
        'edit': {
            'permissions': [
                {
                    'action': 'foo',
                    'resource': 'qux'
                }
            ]
        }
    }

    foo = JoinAccessGroupPermission.query.get((2, 2))
    assert foo is not None

    data = json.dumps(data)
    res = post('/admin/access-group/edit', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Access Group Edited Successfully'

    bar = AccessGroup.query.get(2)
    assert len(bar.permissions) == 1
    assert bar.permissions[0].permission.definition == ('foo', 'qux')

    foo = JoinAccessGroupPermission.query.get((2, 2))
    assert foo is None


def test_access_group_edit_studies(post):
    data = {
        'group': 1,
        'id': 2,
        'edit': {
            'studies': [
                2
            ]
        }
    }

    foo = JoinAccessGroupStudy.query.get((2, 1))
    assert foo is not None

    data = json.dumps(data)
    res = post('/admin/access-group/edit', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Access Group Edited Successfully'

    bar = AccessGroup.query.get(2)
    assert len(bar.studies) == 1
    assert bar.studies[0].study.name == 'bar'

    foo = JoinAccessGroupStudy.query.get((2, 1))
    assert foo is None


def test_access_group_archive(post):
    data = {
        'group': 1,
        'id': 1
    }

    data = json.dumps(data)
    res = post('/admin/access-group/archive', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'Access Group Archived Successfully'

    foo = AccessGroup.query.get(1)
    assert foo.is_archived


def test_app(client):
    res = login_admin_account(client)
    opts = '?group=1'
    res = client.get('/admin/app' + opts)
    data = json.loads(res.data)
    assert len(data) == 3
    assert data[1]['Name'] == 'foo'
    assert data[2]['Name'] == 'bar'


def test_app_create(post):
    data = {
        'group': 1,
        'create': {
            'name': 'baz'
        }
    }

    data = json.dumps(data)
    res = post('/admin/app/create', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'App Created Successfully'

    q1 = App.name == 'baz'
    foo = App.query.filter(q1).first()
    assert foo is not None
    assert foo.name == 'baz'


def test_app_edit(post):
    data = {
        'group': 1,
        'id': 1,
        'edit': {
            'name': 'baz'
        }
    }

    data = json.dumps(data)
    res = post('/admin/app/edit', data=data)
    data = json.loads(res.data)
    assert 'msg' in data
    assert data['msg'] == 'App Edited Successfully'

    foo = App.query.get(1)
    assert foo.name == 'baz'
