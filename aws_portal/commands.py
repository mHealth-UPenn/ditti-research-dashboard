import click
from flask import current_app
from flask.cli import with_appcontext
from flask_migrate import upgrade

from aws_portal.extensions import db, cache
from aws_portal.models import (
    init_admin_app, init_admin_group, init_admin_account, init_db, init_api,
    init_integration_testing_db, init_study_subject, init_lambda_task,
    delete_lambda_tasks
)


@click.command("init-admin-app")
@click.option("--uri", default=None, help="Overrides the SQLAlchemy URI.")
@with_appcontext
def init_admin_app_click(uri):
    if uri is not None:
        current_app.config["SQLALCHEMY_DATABASE_URI"] = uri

    app = init_admin_app()
    click.echo(repr(app))


@click.command("init-admin-group")
@click.option("--uri", default=None, help="Overrides the SQLAlchemy URI.")
@with_appcontext
def init_admin_group_click(uri):
    if uri is not None:
        current_app.config["SQLALCHEMY_DATABASE_URI"] = uri

    access_group = init_admin_group()
    click.echo(repr(access_group))


@click.command("init-admin")
@click.option("--uri", default=None, help="Overrides the SQLAlchemy URI.")
@click.option("--email", default=None)
@click.option("--password", default=None)
@with_appcontext
def init_admin_account_click(uri, email, password):
    if uri is not None:
        current_app.config["SQLALCHEMY_DATABASE_URI"] = uri

    admin = init_admin_account(email, password)
    click.echo(repr(admin))


@click.command("init-db")
@with_appcontext
def init_db_click():
    init_db()
    click.echo("Database successfully initialized.")


@click.command("init-api")
@with_appcontext
def init_api_click():
    init_api(click)


@click.command("reset-db", help="Reset the database.")
@with_appcontext
def reset_db_click():
    db_uri = current_app.config["SQLALCHEMY_DATABASE_URI"]

    if "localhost" in db_uri:
        db.drop_all()
        db.create_all()
        upgrade()
    else:
        raise RuntimeError("reset-db requires a localhost database URI.")

    click.echo("Database successfully reset.")


@click.command("init-integration-testing-db", help="Initialize the integration testing database.")
@with_appcontext
def init_integration_testing_db_click():
    init_integration_testing_db()
    click.echo("Database successfully initialized.")


@click.command("init-study-subject", help="Create a new StudySubject database entry.")
@click.option("--ditti_id", default=None, help="The ditti_id of the StudySubject.")
@with_appcontext
def init_study_subject_click(ditti_id):
    if ditti_id is None:
        raise RuntimeError("Option `ditti_id` is required.")
    init_study_subject(ditti_id)
    click.echo("Study subject successfully initialized.")


@click.command("clear-cache", help="Clear the Flask cache.")
@with_appcontext
def clear_cache_click():
    cache.clear()


@click.command("init-lambda-task", help="Create a new LambdaTask database entry.")
@click.option("--status", default="InProgress", help="The status of the LambdaTask.")
@with_appcontext
def init_lambda_task_click(status):
    init_lambda_task(status)


@click.command("delete-lambda-tasks", help="Delete all LambdaTask database entries.")
@with_appcontext
def delete_lambda_tasks_click():
    delete_lambda_tasks()
