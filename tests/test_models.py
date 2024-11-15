from datetime import datetime, UTC
import os

import pytest
from sqlalchemy.exc import IntegrityError

from aws_portal.app import create_app
from aws_portal.extensions import db
from aws_portal.models import (
    AccessGroup, Account, App, JoinAccessGroupPermission,
    JoinAccountAccessGroup, JoinAccountStudy, JoinRolePermission,
    JoinStudyRole, Permission, Role, Study, StudySubject, JoinStudySubjectApi,
    JoinStudySubjectStudy, Api, init_admin_account, init_admin_app,
    init_admin_group, init_db
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
            foo.action = "foo"
            foo.resource = "baz"
            db.session.add(foo)
            db.session.commit()

    def test_validate_action(self, app):
        with pytest.raises(ValueError):
            q1 = Permission.definition == ("foo", "baz")
            foo = Permission.query.filter(q1).first()
            foo.action = "bar"
            db.session.commit()

    def test_validate_resource(self, app):
        with pytest.raises(ValueError):
            q1 = Permission.definition == ("bar", "qux")
            foo = Permission.query.filter(q1).first()
            foo.resource = "baz"
            db.session.commit()

    def test_definition(self, app):
        q1 = Permission.definition == ("foo", "baz")
        foo = Permission.query.filter(q1).first()
        assert "foo: %s" % foo != "foo: %s" % None
        assert foo.action == "foo"
        assert foo.resource == "baz"


class TestAccount:
    def test_validate_created_on(self, app):
        with pytest.raises(ValueError):
            q1 = Account.email == "foo@email.com"
            foo = Account.query.filter(q1).first()
            foo.created_on = datetime.now(UTC)
            db.session.commit()

    def test_full_name(self, app):
        q1 = Account.full_name == "John Smith"
        foo = Account.query.filter(q1).first()
        assert "foo: %s" % foo != "foo: %s" % None
        assert foo.first_name == "John"
        assert foo.last_name == "Smith"

    def test_check_password(self, app):
        q1 = Account.email == "foo@email.com"
        foo = Account.query.filter(q1).first()
        assert foo.check_password("foo")

    def test_get_permissions_access_group(self, app):
        q1 = Account.email == "foo@email.com"
        q2 = AccessGroup.name == "foo"
        foo = Account.query.filter(q1).first()
        bar = AccessGroup.query.filter(q2).first()
        qux = foo.get_permissions(bar.id).all()
        assert "qux: %s" % qux != "qux: %s" % None

        qux = [x.definition for x in qux]
        assert qux == [("foo", "baz")]

    def test_get_permissions_study(self, app):
        q1 = Account.email == "bar@email.com"
        q2 = AccessGroup.name == "bar"
        q3 = Study.name == "bar"
        foo = Account.query.filter(q1).first()
        bar = AccessGroup.query.filter(q2).first()
        baz = Study.query.filter(q3).first()
        qux = foo.get_permissions(bar.id, baz.id).all()
        assert "qux: %s" % qux != "qux: %s" % None

        qux = [x.definition for x in qux]
        assert qux == [("bar", "baz"), ("bar", "qux")]

    def test_validate_ask_invalid(self, app):
        with pytest.raises(ValueError):
            q1 = Account.email == "foo@email.com"
            q2 = AccessGroup.name == "bar"
            q3 = Study.name == "bar"
            foo = Account.query.filter(q1).first()
            bar = AccessGroup.query.filter(q2).first()
            baz = Study.query.filter(q3).first()
            qux = foo.get_permissions(bar.id, baz.id)
            foo.validate_ask("bar", "baz", qux)

    def test_validate_ask(self, app):
        q1 = Account.email == "foo@email.com"
        q2 = AccessGroup.name == "foo"
        q3 = Study.name == "foo"
        foo = Account.query.filter(q1).first()
        bar = AccessGroup.query.filter(q2).first()
        baz = Study.query.filter(q3).first()
        qux = foo.get_permissions(bar.id, baz.id)
        foo.validate_ask("foo", "baz", qux)

    def test_validate_ask_wildcard(self, app):
        init_admin_app()
        init_admin_group()
        init_admin_account()
        q1 = Account.email == os.getenv("FLASK_ADMIN_EMAIL")
        q2 = AccessGroup.name == "Admin"
        foo = Account.query.filter(q1).first()
        bar = AccessGroup.query.filter(q2).first()
        baz = foo.get_permissions(bar.id)
        foo.validate_ask("qux", "qaz", baz)


class TestDeletions:
    def test_delete_access_group(self, app):
        q1 = AccessGroup.name == "foo"
        foo = AccessGroup.query.filter(q1).first()
        assert "foo: %s" % foo != "foo: %s" % None

        foo_id = foo.id
        q2 = JoinAccessGroupPermission.access_group_id == foo_id
        q3 = JoinAccountAccessGroup.access_group_id == foo_id
        bar = JoinAccessGroupPermission.query.filter(q2).first()
        baz = JoinAccountAccessGroup.query.filter(q3).first()
        assert "bar: %s" % bar != "bar: %s" % None
        assert "baz: %s" % baz != "baz: %s" % None

        db.session.delete(foo)
        db.session.commit()
        foo = AccessGroup.query.filter(q1).first()
        bar = JoinAccessGroupPermission.query.filter(q2).first()
        baz = JoinAccountAccessGroup.query.filter(q3).first()
        assert "foo: %s" % foo == "foo: %s" % None
        assert "bar: %s" % bar == "bar: %s" % None
        assert "baz: %s" % baz == "baz: %s" % None

    def test_delete_account(self, app):
        q1 = Account.email == "foo@email.com"
        foo = Account.query.filter(q1).first()
        assert "foo: %s" % foo != "foo: %s" % None

        foo_id = foo.id
        q2 = JoinAccountAccessGroup.account_id == foo_id
        q3 = JoinAccountStudy.account_id == foo_id
        bar = JoinAccountAccessGroup.query.filter(q2).first()
        baz = JoinAccountStudy.query.filter(q3).first()
        assert "bar: %s" % bar != "bar: %s" % None
        assert "baz: %s" % baz != "baz: %s" % None

        db.session.delete(foo)
        db.session.commit()
        foo = Account.query.filter(q1).first()
        bar = JoinAccountAccessGroup.query.filter(q2).first()
        baz = JoinAccountStudy.query.filter(q3).first()
        assert "foo: %s" % foo == "foo: %s" % None
        assert "bar: %s" % bar == "bar: %s" % None
        assert "baz: %s" % baz == "baz: %s" % None

    def test_delete_app(self, app):
        q1 = App.name == "foo"
        foo = App.query.filter(q1).first()
        assert "foo: %s" % foo != "foo: %s" % None

        db.session.delete(foo)
        db.session.commit()
        foo = App.query.filter(q1).first()
        assert "foo: %s" % foo == "foo: %s" % None

    def test_delete_permission(self, app):
        q1 = Permission.definition == ("foo", "baz")
        foo = Permission.query.filter(q1).first()
        assert "foo: %s" % foo != "foo: %s" % None

        foo_id = foo.id
        q2 = JoinAccessGroupPermission.permission_id == foo_id
        q3 = JoinRolePermission.permission_id == foo_id
        bar = JoinAccessGroupPermission.query.filter(q2).first()
        baz = JoinRolePermission.query.filter(q3).first()
        assert "bar: %s" % bar != "bar: %s" % None
        assert "baz: %s" % baz != "baz: %s" % None

        db.session.delete(foo)
        db.session.commit()
        foo = Permission.query.filter(q1).first()
        bar = JoinAccessGroupPermission.query.filter(q2).first()
        baz = JoinRolePermission.query.filter(q3).first()
        assert "foo: %s" % foo == "foo: %s" % None
        assert "bar: %s" % bar == "bar: %s" % None
        assert "baz: %s" % baz == "baz: %s" % None

    def test_delete_role(self, app):
        q1 = Role.name == "foo"
        foo = Role.query.filter(q1).first()
        assert "foo: %s" % foo != "foo: %s" % None

        foo_id = foo.id
        q2 = JoinRolePermission.role_id == foo_id
        q3 = JoinAccountStudy.role_id == foo_id
        bar = JoinRolePermission.query.filter(q2).first()
        baz = JoinAccountStudy.query.filter(q3).first()
        assert "bar: %s" % bar != "bar: %s" % None
        assert "baz: %s" % baz != "baz: %s" % None

        db.session.delete(foo)
        db.session.commit()
        foo = Role.query.filter(q1).first()
        bar = JoinRolePermission.query.filter(q2).first()
        baz = JoinAccountStudy.query.filter(q3).first()
        assert "foo: %s" % foo == "foo: %s" % None
        assert "bar: %s" % bar == "bar: %s" % None
        assert "baz: %s" % baz == "baz: %s" % None

    def test_delete_study_with_enrolled_subject(self, app):
        with pytest.raises(IntegrityError):
            q1 = Study.name == "foo"
            foo = Study.query.filter(q1).first()
            assert "foo: %s" % foo != "foo: %s" % None

            foo_id = foo.id
            q2 = JoinStudySubjectStudy.study_id == foo_id
            bar = JoinStudySubjectStudy.query.filter(q2).first()
            assert "bar: %s" % bar != "bar: %s" % None

            db.session.delete(foo)
            db.session.commit()

    def test_delete_study(self, app):
        q1 = Study.name == "foo"
        foo = Study.query.filter(q1).first()
        assert "foo: %s" % foo != "foo: %s" % None

        # First delete all enrolled subjects
        foo_id = foo.id
        q2 = JoinStudySubjectStudy.study_id == foo_id
        bar = JoinStudySubjectStudy.query.filter(q2).all()
        assert len(bar) == 1

        for join in bar:
            db.session.delete(join)
        db.session.commit()
        bar = JoinStudySubjectStudy.query.filter(q2).all()
        assert len(bar) == 0

        foo_id = foo.id
        q2 = JoinAccountStudy.study_id == foo_id
        q3 = JoinStudyRole.study_id == foo_id
        bar = JoinAccountStudy.query.filter(q2).first()
        baz = JoinStudyRole.query.filter(q3).first()
        assert "bar: %s" % bar != "bar: %s" % None
        assert "baz: %s" % baz != "baz: %s" % None

        db.session.delete(foo)
        db.session.commit()
        foo = Study.query.filter(q1).filter().first()
        bar = JoinAccountStudy.query.filter(q2).first()
        baz = JoinStudyRole.query.filter(q3).first()
        assert "foo: %s" % foo == "foo: %s" % None
        assert "bar: %s" % bar == "bar: %s" % None
        assert "baz: %s" % baz == "baz: %s" % None

    def test_delete_study_subject(self, app):
        q1 = StudySubject.email == "foo@email.com"
        foo = StudySubject.query.filter(q1).first()
        assert "foo: %s" % foo != "foo: %s" % None

        foo_id = foo.id
        q3 = JoinStudySubjectStudy.study_subject_id == foo_id
        q2 = JoinStudySubjectApi.study_subject_id == foo_id
        baz = JoinStudySubjectStudy.query.filter(q3).first()
        bar = JoinStudySubjectApi.query.filter(q2).first()
        assert "bar: %s" % bar != "bar: %s" % None
        assert "baz: %s" % baz != "baz: %s" % None

        db.session.delete(foo)
        db.session.commit()
        foo = StudySubject.query.filter(q1).first()
        baz = JoinStudySubjectStudy.query.filter(q3).first()
        bar = JoinStudySubjectApi.query.filter(q2).first()
        assert "foo: %s" % foo == "foo: %s" % None
        assert "bar: %s" % bar == "bar: %s" % None
        assert "baz: %s" % baz == "baz: %s" % None

    def test_delete_api_with_enrolled_subject(self, app):
        with pytest.raises(IntegrityError):
            q1 = Api.name == "foo"
            foo = Api.query.filter(q1).first()
            assert "foo: %s" % foo != "foo: %s" % None

            foo_id = foo.id
            q2 = JoinStudySubjectApi.api_id == foo_id
            bar = JoinStudySubjectApi.query.filter(q2).first()
            assert "bar: %s" % bar != "bar: %s" % None

            db.session.delete(foo)
            db.session.commit()

    def test_delete_api(self, app):
        q1 = Api.name == "foo"
        foo = Api.query.filter(q1).first()
        assert "foo: %s" % foo != "foo: %s" % None

        # First delete all enrolled subjects
        foo_id = foo.id
        q2 = JoinStudySubjectApi.api_id == foo_id
        bar = JoinStudySubjectApi.query.filter(q2).all()
        assert len(bar) == 1

        for join in bar:
            db.session.delete(join)
        db.session.commit()
        bar = JoinStudySubjectApi.query.filter(q2).all()
        assert len(bar) == 0

        db.session.delete(foo)
        db.session.commit()
        foo = Api.query.filter(q1).filter().first()
        bar = JoinStudySubjectApi.query.filter(q2).first()
        assert "foo: %s" % foo == "foo: %s" % None
        assert "bar: %s" % bar == "bar: %s" % None


class TestArchives:
    def test_archive_account(self, app):
        q1 = Account.email == "foo@email.com"
        foo = Account.query.filter(q1).first()
        assert "foo: %s" % foo != "foo: %s" % None

        q2 = AccessGroup.name == "foo"
        bar = AccessGroup.query.filter(q2).first()
        assert "bar: %s" % bar != "bar: %s" % None
        assert len(bar.accounts) == 1
        assert bar.accounts[0].account is foo

        foo.is_archived = True
        db.session.commit()
        assert foo.is_archived
        assert len(bar.accounts) == 0

    def test_archive_access_group(self, app):
        q1 = AccessGroup.name == "foo"
        foo = AccessGroup.query.filter(q1).first()
        assert "foo: %s" % foo != "foo: %s" % None

        q2 = Account.email == "foo@email.com"
        bar = Account.query.filter(q2).first()
        assert "bar: %s" % bar != "bar: %s" % None
        assert len(bar.access_groups) == 1
        assert bar.access_groups[0].access_group is foo

        baz = bar.get_permissions(foo.id).all()
        assert "baz: %s" % baz != "baz: %s" % None

        qux = [x.definition for x in baz]
        assert qux == [("foo", "baz")]

        foo.is_archived = True
        db.session.commit()
        assert foo.is_archived
        assert len(bar.access_groups) == 0

        baz = bar.get_permissions(foo.id).all()
        assert "baz: %s" % baz != "baz: %s" % None

        qux = [x.definition for x in baz]
        assert qux == []

    def test_archive_study(self, app):
        # Retrieve the Study instance
        q1 = Study.name == "bar"
        foo = Study.query.filter(q1).first()
        assert foo is not None, "Study 'bar' should exist."

        # Retrieve the Account associated with the Study
        q2 = Account.email == "bar@email.com"
        bar = Account.query.filter(q2).first()
        assert bar is not None, "Account 'bar@email.com' should exist."
        assert len(
            bar.studies) == 1, "Account should be associated with one study."
        assert bar.studies[0].study is foo, "Associated study should be 'bar'."

        # Retrieve the StudySubject using ditti_id
        q2 = StudySubject.ditti_id == "ditti_bar_456"
        baz = StudySubject.query.filter(q2).first()
        assert baz is not None, "StudySubject with ditti_id 'ditti_bar_456' should exist."
        assert len(
            baz.studies) == 1, "StudySubject should be associated with one study."
        assert baz.studies[0].study is foo, "Associated study should be 'bar'."

        # Archive the Study
        foo.is_archived = True
        db.session.commit()

        # Validate archiving
        assert foo.is_archived, "Study should be marked as archived."
        assert len(
            bar.studies) == 0, "Account should no longer be associated with the archived study."
        assert len(
            baz.studies) == 0, "StudySubject should no longer be associated with the archived study."

    def test_archive_api(self, app):
        q1 = Api.name == "bar"
        foo = Api.query.filter(q1).first()
        assert foo is not None, "API 'bar' should exist."

        # Updated to use ditti_id instead of email
        q2 = StudySubject.ditti_id == "ditti_bar_456"
        baz = StudySubject.query.filter(q2).first()
        assert baz is not None, "StudySubject with ditti_id 'ditti_bar_456' should exist."
        assert len(
            baz.apis) == 1, "StudySubject should be associated with one API."
        assert baz.apis[0].api is foo, "Associated API should be 'bar'."
