import os
import pytest
from sqlalchemy import tuple_
from backend.app import create_app

from backend.commands import (
    init_admin_app_click, init_admin_group_click, init_admin_account_click,
    init_db_click, create_researcher_account_click, init_integration_testing_db_click
)

from backend.models import (
    AccessGroup, Account, App, JoinAccessGroupPermission,
    JoinAccountAccessGroup, Permission, init_db
)


@pytest.fixture
def app():
    app = create_app(testing=True)
    with app.app_context():
        init_db()
        yield app


@pytest.fixture
def runner(app):
    runner = app.test_cli_runner()
    return runner


def test_init_db(runner):
    res = runner.invoke(init_db_click)
    assert res.output == "Database successfully initialized.\n"


def test_init_admin_app(runner):
    res = runner.invoke(init_admin_app_click)
    q1 = App.name == "Admin Dashboard"
    foo = App.query.filter(q1).first()
    assert foo is not None
    assert res.output == repr(foo) + "\n"


def test_init_admin_app_duplicate(runner):
    runner.invoke(init_admin_app_click)
    res = runner.invoke(init_admin_app_click)
    assert isinstance(res.exception, ValueError)


def test_init_admin_group(runner):
    runner.invoke(init_admin_app_click)
    res = runner.invoke(init_admin_group_click)
    q1 = AccessGroup.name == "Admin"
    q2 = Permission.definition == tuple_("*", "*")
    foo = AccessGroup.query.filter(q1).first()
    bar = Permission.query.filter(q2).first()
    baz = JoinAccessGroupPermission.query.get((foo.id, bar.id))
    assert foo is not None
    assert res.output == repr(foo) + "\n"
    assert bar is not None
    assert baz is not None


def test_init_admin_access_group_app_doesnt_exits(runner):
    res = runner.invoke(init_admin_group_click)
    assert isinstance(res.exception, ValueError)


def test_init_admin_group_duplicate(runner):
    runner.invoke(init_admin_app_click)
    runner.invoke(init_admin_group_click)
    res = runner.invoke(init_admin_group_click)
    assert isinstance(res.exception, ValueError)


def test_init_admin_account(runner):
    runner.invoke(init_admin_app_click)
    runner.invoke(init_admin_group_click)
    res = runner.invoke(init_admin_account_click)
    q1 = Account.email == "testing"
    q2 = AccessGroup.name == "Admin"
    foo = Account.query.filter(q1).first()
    bar = AccessGroup.query.filter(q2).first()
    baz = JoinAccountAccessGroup.query.get((foo.id, bar.id))
    assert foo is not None
    assert res.output == repr(foo) + "\n"
    assert bar is not None
    assert baz is not None


def test_init_admin_account_access_group_doesnt_exits(runner):
    res = runner.invoke(init_admin_account_click)
    assert isinstance(res.exception, ValueError)


def test_init_admin_account_duplicate(runner):
    runner.invoke(init_admin_app_click)
    runner.invoke(init_admin_group_click)
    runner.invoke(init_admin_account_click)
    res = runner.invoke(init_admin_account_click)
    assert isinstance(res.exception, ValueError)


def test_create_researcher_account(runner):
    runner.invoke(init_integration_testing_db_click)
    res = runner.invoke(create_researcher_account_click, args=["--email", "test@test.com"])
    assert res.output == "Researcher account successfully created.\n"

    # Check that the account was created
    q1 = Account.email == "test@test.com"
    foo = Account.query.filter(q1).first()
    assert foo is not None
    assert foo.email == "test@test.com"
    assert foo.first_name == "Jane"
    assert foo.last_name == "Doe"
    assert foo.phone_number == "+12345678901"
    assert foo.is_confirmed == True

    # Check that the account has access to all groups
    q2 = AccessGroup.name == "Admin"
    bar = AccessGroup.query.filter(q2).first()
    baz = JoinAccountAccessGroup.query.get((foo.id, bar.id))
    assert bar is not None
    assert baz is not None

    q3 = AccessGroup.name == "Ditti App Admin"
    bar = AccessGroup.query.filter(q3).first()
    baz = JoinAccountAccessGroup.query.get((foo.id, bar.id))
    assert bar is not None
    assert baz is not None

    q4 = AccessGroup.name == "Wearable Dashboard Admin"
    bar = AccessGroup.query.filter(q4).first()
    baz = JoinAccountAccessGroup.query.get((foo.id, bar.id))
    assert bar is not None
    assert baz is not None
