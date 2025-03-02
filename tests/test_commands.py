# import os
# import pytest
# from sqlalchemy import tuple_
# from aws_portal.app import create_app

# from aws_portal.commands import (
#     init_admin_app_click, init_admin_group_click, init_admin_account_click,
#     init_db_click
# )

# from aws_portal.models import (
#     AccessGroup, Account, App, JoinAccessGroupPermission,
#     JoinAccountAccessGroup, Permission, init_db
# )


# @pytest.fixture
# def app():
#     app = create_app(testing=True)
#     with app.app_context():
#         init_db()
#         yield app


# @pytest.fixture
# def runner(app):
#     runner = app.test_cli_runner()
#     return runner


# def test_init_db(runner):
#     res = runner.invoke(init_db_click)
#     assert res.output == "Database successfully initialized.\n"


# def test_init_admin_app(runner):
#     res = runner.invoke(init_admin_app_click)
#     q1 = App.name == "Admin Dashboard"
#     foo = App.query.filter(q1).first()
#     assert foo is not None
#     assert res.output == repr(foo) + "\n"


# def test_init_admin_app_duplicate(runner):
#     runner.invoke(init_admin_app_click)
#     res = runner.invoke(init_admin_app_click)
#     assert isinstance(res.exception, ValueError)


# def test_init_admin_group(runner):
#     runner.invoke(init_admin_app_click)
#     res = runner.invoke(init_admin_group_click)
#     q1 = AccessGroup.name == "Admin"
#     q2 = Permission.definition == tuple_("*", "*")
#     foo = AccessGroup.query.filter(q1).first()
#     bar = Permission.query.filter(q2).first()
#     baz = JoinAccessGroupPermission.query.get((foo.id, bar.id))
#     assert foo is not None
#     assert res.output == repr(foo) + "\n"
#     assert bar is not None
#     assert baz is not None


# def test_init_admin_access_group_app_doesnt_exits(runner):
#     res = runner.invoke(init_admin_group_click)
#     assert isinstance(res.exception, ValueError)


# def test_init_admin_group_duplicate(runner):
#     runner.invoke(init_admin_app_click)
#     runner.invoke(init_admin_group_click)
#     res = runner.invoke(init_admin_group_click)
#     assert isinstance(res.exception, ValueError)


# def test_init_admin_account(runner):
#     runner.invoke(init_admin_app_click)
#     runner.invoke(init_admin_group_click)
#     res = runner.invoke(init_admin_account_click)
#     q1 = Account.email == os.getenv("FLASK_ADMIN_EMAIL")
#     q2 = AccessGroup.name == "Admin"
#     foo = Account.query.filter(q1).first()
#     bar = AccessGroup.query.filter(q2).first()
#     baz = JoinAccountAccessGroup.query.get((foo.id, bar.id))
#     assert foo is not None
#     assert res.output == repr(foo) + "\n"
#     assert bar is not None
#     assert baz is not None


# def test_init_admin_account_access_group_doesnt_exits(runner):
#     res = runner.invoke(init_admin_account_click)
#     assert isinstance(res.exception, ValueError)


# def test_init_admin_account_duplicate(runner):
#     runner.invoke(init_admin_app_click)
#     runner.invoke(init_admin_group_click)
#     runner.invoke(init_admin_account_click)
#     res = runner.invoke(init_admin_account_click)
#     assert isinstance(res.exception, ValueError)
