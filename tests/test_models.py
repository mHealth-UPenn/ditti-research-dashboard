from datetime import datetime
import os
import pytest
from sqlalchemy.exc import IntegrityError
from aws_portal.app import create_app
from aws_portal.extensions import db
from aws_portal.models import (
    AccessGroup, Account, App, JoinAccessGroupPermission,
    JoinAccountAccessGroup, JoinAccountStudy, JoinRolePermission,
    JoinStudyRole, Permission, Role, Study, init_admin_account,
    init_admin_app, init_admin_group, init_db
)
from tests.testing_utils import create_joins, create_tables


@pytest.fixture
def app():
    app = create_app(testing=True)
    with app.app_context():
        init_db()
        create_tables()
        create_joins()
        db.session.commit()

        yield app


class TestPermission:
    def test_duplicate(self, app):
        with pytest.raises(IntegrityError):
            foo = Permission()
            foo.action = 'foo'
            foo.resource = 'baz'
            db.session.add(foo)
            db.session.commit()

    def test_validate_action(self, app):
        with pytest.raises(ValueError):
            q1 = Permission.definition == ('foo', 'baz')
            foo = Permission.query.filter(q1).first()
            foo.action = 'bar'
            db.session.commit()

    def test_validate_resource(self, app):
        with pytest.raises(ValueError):
            q1 = Permission.definition == ('bar', 'qux')
            foo = Permission.query.filter(q1).first()
            foo.resource = 'baz'
            db.session.commit()

    def test_definition(self, app):
        q1 = Permission.definition == ('foo', 'baz')
        foo = Permission.query.filter(q1).first()
        assert 'foo: %s' % foo != 'foo: %s' % None
        assert foo.action == 'foo'
        assert foo.resource == 'baz'


class TestAccount:
    def test_validate_created_on(self, app):
        with pytest.raises(ValueError):
            q1 = Account.email == 'foo@email.com'
            foo = Account.query.filter(q1).first()
            foo.created_on = datetime.utcnow()
            db.session.commit()

    def test_full_name(self, app):
        q1 = Account.full_name == 'John Smith'
        foo = Account.query.filter(q1).first()
        assert 'foo: %s' % foo != 'foo: %s' % None
        assert foo.first_name == 'John'
        assert foo.last_name == 'Smith'

    def test_check_password(self, app):
        q1 = Account.email == 'foo@email.com'
        foo = Account.query.filter(q1).first()
        assert foo.check_password('foo')

    def test_get_permissions_access_group(self, app):
        q1 = Account.email == 'foo@email.com'
        q2 = AccessGroup.name == 'foo'
        foo = Account.query.filter(q1).first()
        bar = AccessGroup.query.filter(q2).first()
        qux = foo.get_permissions(bar.id).all()
        assert 'qux: %s' % qux != 'qux: %s' % None

        qux = [x.definition for x in qux]
        assert qux == [('foo', 'baz')]

    def test_get_permissions_study(self, app):
        q1 = Account.email == 'bar@email.com'
        q2 = AccessGroup.name == 'bar'
        q3 = Study.name == 'bar'
        foo = Account.query.filter(q1).first()
        bar = AccessGroup.query.filter(q2).first()
        baz = Study.query.filter(q3).first()
        qux = foo.get_permissions(bar.id, baz.id).all()
        assert 'qux: %s' % qux != 'qux: %s' % None

        qux = [x.definition for x in qux]
        assert qux == [('bar', 'baz'), ('bar', 'qux')]

    def test_validate_ask_invalid(self, app):
        with pytest.raises(ValueError):
            q1 = Account.email == 'foo@email.com'
            q2 = AccessGroup.name == 'bar'
            q3 = Study.name == 'bar'
            foo = Account.query.filter(q1).first()
            bar = AccessGroup.query.filter(q2).first()
            baz = Study.query.filter(q3).first()
            qux = foo.get_permissions(bar.id, baz.id)
            foo.validate_ask('bar', 'baz', qux)

    def test_validate_ask(self, app):
        q1 = Account.email == 'foo@email.com'
        q2 = AccessGroup.name == 'foo'
        q3 = Study.name == 'foo'
        foo = Account.query.filter(q1).first()
        bar = AccessGroup.query.filter(q2).first()
        baz = Study.query.filter(q3).first()
        qux = foo.get_permissions(bar.id, baz.id)
        foo.validate_ask('foo', 'baz', qux)

    def test_validate_ask_wildcard(self, app):
        init_admin_app()
        init_admin_group()
        init_admin_account()
        q1 = Account.email == os.getenv('FLASK_ADMIN_EMAIL')
        q2 = AccessGroup.name == 'Admin'
        foo = Account.query.filter(q1).first()
        bar = AccessGroup.query.filter(q2).first()
        baz = foo.get_permissions(bar.id)
        foo.validate_ask('qux', 'qaz', baz)


class TestDeletions:
    def test_delete_access_group(self, app):
        q1 = AccessGroup.name == 'foo'
        foo = AccessGroup.query.filter(q1).first()
        assert 'foo: %s' % foo != 'foo: %s' % None

        foo_id = foo.id
        q2 = JoinAccessGroupPermission.access_group_id == foo_id
        q3 = JoinAccountAccessGroup.access_group_id == foo_id
        bar = JoinAccessGroupPermission.query.filter(q2).first()
        baz = JoinAccountAccessGroup.query.filter(q3).first()
        assert 'bar: %s' % bar != 'bar: %s' % None
        assert 'baz: %s' % baz != 'baz: %s' % None

        db.session.delete(foo)
        db.session.commit()
        foo = AccessGroup.query.filter(q1).first()
        bar = JoinAccessGroupPermission.query.filter(q2).first()
        baz = JoinAccountAccessGroup.query.filter(q3).first()
        assert 'foo: %s' % foo == 'foo: %s' % None
        assert 'bar: %s' % bar == 'bar: %s' % None
        assert 'baz: %s' % baz == 'baz: %s' % None

    def test_delete_account(self, app):
        q1 = Account.email == 'foo@email.com'
        foo = Account.query.filter(q1).first()
        assert 'foo: %s' % foo != 'foo: %s' % None

        foo_id = foo.id
        q2 = JoinAccountAccessGroup.account_id == foo_id
        q3 = JoinAccountStudy.account_id == foo_id
        bar = JoinAccountAccessGroup.query.filter(q2).first()
        baz = JoinAccountStudy.query.filter(q3).first()
        assert 'bar: %s' % bar != 'bar: %s' % None
        assert 'baz: %s' % baz != 'baz: %s' % None

        db.session.delete(foo)
        db.session.commit()
        foo = Account.query.filter(q1).first()
        bar = JoinAccountAccessGroup.query.filter(q2).first()
        baz = JoinAccountStudy.query.filter(q3).first()
        assert 'foo: %s' % foo == 'foo: %s' % None
        assert 'bar: %s' % bar == 'bar: %s' % None
        assert 'baz: %s' % baz == 'baz: %s' % None

    def test_delete_app(self, app):
        q1 = App.name == 'foo'
        foo = App.query.filter(q1).first()
        assert 'foo: %s' % foo != 'foo: %s' % None

        db.session.delete(foo)
        db.session.commit()
        foo = App.query.filter(q1).first()
        assert 'foo: %s' % foo == 'foo: %s' % None

    def test_delete_permission(self, app):
        q1 = Permission.definition == ('foo', 'baz')
        foo = Permission.query.filter(q1).first()
        assert 'foo: %s' % foo != 'foo: %s' % None

        foo_id = foo.id
        q2 = JoinAccessGroupPermission.permission_id == foo_id
        q3 = JoinRolePermission.permission_id == foo_id
        bar = JoinAccessGroupPermission.query.filter(q2).first()
        baz = JoinRolePermission.query.filter(q3).first()
        assert 'bar: %s' % bar != 'bar: %s' % None
        assert 'baz: %s' % baz != 'baz: %s' % None

        db.session.delete(foo)
        db.session.commit()
        foo = Permission.query.filter(q1).first()
        bar = JoinAccessGroupPermission.query.filter(q2).first()
        baz = JoinRolePermission.query.filter(q3).first()
        assert 'foo: %s' % foo == 'foo: %s' % None
        assert 'bar: %s' % bar == 'bar: %s' % None
        assert 'baz: %s' % baz == 'baz: %s' % None

    def test_delete_role(self, app):
        q1 = Role.name == 'foo'
        foo = Role.query.filter(q1).first()
        assert 'foo: %s' % foo != 'foo: %s' % None

        foo_id = foo.id
        q2 = JoinRolePermission.role_id == foo_id
        q3 = JoinAccountStudy.role_id == foo_id
        bar = JoinRolePermission.query.filter(q2).first()
        baz = JoinAccountStudy.query.filter(q3).first()
        assert 'bar: %s' % bar != 'bar: %s' % None
        assert 'baz: %s' % baz != 'baz: %s' % None

        db.session.delete(foo)
        db.session.commit()
        foo = Role.query.filter(q1).first()
        bar = JoinRolePermission.query.filter(q2).first()
        baz = JoinAccountStudy.query.filter(q3).first()
        assert 'foo: %s' % foo == 'foo: %s' % None
        assert 'bar: %s' % bar == 'bar: %s' % None
        assert 'baz: %s' % baz == 'baz: %s' % None

    def test_delete_study(self, app):
        q1 = Study.name == 'foo'
        foo = Study.query.filter(q1).first()
        assert 'foo: %s' % foo != 'foo: %s' % None

        foo_id = foo.id
        q2 = JoinAccountStudy.study_id == foo_id
        q3 = JoinStudyRole.study_id == foo_id
        bar = JoinAccountStudy.query.filter(q2).first()
        baz = JoinStudyRole.query.filter(q3).first()
        assert 'bar: %s' % bar != 'bar: %s' % None
        assert 'baz: %s' % baz != 'baz: %s' % None

        db.session.delete(foo)
        db.session.commit()
        foo = Study.query.filter(q1).filter().first()
        bar = JoinAccountStudy.query.filter(q2).first()
        baz = JoinStudyRole.query.filter(q3).first()
        assert 'foo: %s' % foo == 'foo: %s' % None
        assert 'bar: %s' % bar == 'bar: %s' % None
        assert 'baz: %s' % baz == 'baz: %s' % None


class TestArchives:
    def test_archive_account(self, app):
        q1 = Account.email == 'foo@email.com'
        foo = Account.query.filter(q1).first()
        assert 'foo: %s' % foo != 'foo: %s' % None

        q2 = AccessGroup.name == 'foo'
        bar = AccessGroup.query.filter(q2).first()
        assert 'bar: %s' % bar != 'bar: %s' % None
        assert len(bar.accounts) == 1
        assert bar.accounts[0].account is foo

        foo.is_archived = True
        db.session.commit()
        assert foo.is_archived
        assert len(bar.accounts) == 0

    def test_archive_access_group(self, app):
        q1 = AccessGroup.name == 'foo'
        foo = AccessGroup.query.filter(q1).first()
        assert 'foo: %s' % foo != 'foo: %s' % None

        q2 = Account.email == 'foo@email.com'
        bar = Account.query.filter(q2).first()
        assert 'bar: %s' % bar != 'bar: %s' % None
        assert len(bar.access_groups) == 1
        assert bar.access_groups[0].access_group is foo

        baz = bar.get_permissions(foo.id).all()
        assert 'baz: %s' % baz != 'baz: %s' % None

        qux = [x.definition for x in baz]
        assert qux == [('foo', 'baz')]

        foo.is_archived = True
        db.session.commit()
        assert foo.is_archived
        assert len(bar.access_groups) == 0

        baz = bar.get_permissions(foo.id).all()
        assert 'baz: %s' % baz != 'baz: %s' % None

        qux = [x.definition for x in baz]
        assert qux == []

    def test_archive_study(self, app):
        q1 = Study.name == 'bar'
        foo = Study.query.filter(q1).first()
        assert 'foo: %s' % foo != 'foo: %s' % None

        q2 = Account.email == 'bar@email.com'
        bar = Account.query.filter(q2).first()
        assert 'bar: %s' % bar != 'bar: %s' % None
        assert len(bar.studies) == 1
        assert bar.studies[0].study is foo

        foo.is_archived = True
        db.session.commit()
        assert foo.is_archived
        assert len(bar.studies) == 0
        assert len(bar.studies) == 0
