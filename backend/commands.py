# Ditti Research Dashboard
# Copyright (C) 2025 the Trustees of the University of Pennsylvania
#
# Ditti Research Dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Ditti Research Dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from datetime import datetime

import click
from flask import current_app
from flask.cli import with_appcontext
from flask_migrate import upgrade

from backend.extensions import cache, db
from backend.models import (
    AccessGroup,
    Account,
    JoinAccountAccessGroup,
    delete_lambda_tasks,
    init_admin_account,
    init_admin_app,
    init_admin_group,
    init_api,
    init_db,
    init_integration_testing_db,
    init_lambda_task,
    init_study_subject,
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
@with_appcontext
def init_admin_account_click(uri, email):
    if uri is not None:
        current_app.config["SQLALCHEMY_DATABASE_URI"] = uri

    admin = init_admin_account(email)
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


@click.command(
    "init-integration-testing-db",
    help="Initialize the integration testing database.",
)
@with_appcontext
def init_integration_testing_db_click():
    init_integration_testing_db()
    click.echo("Database successfully initialized.")


@click.command(
    "init-study-subject", help="Create a new StudySubject database entry."
)
@click.option(
    "--ditti_id", default=None, help="The ditti_id of the StudySubject."
)
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


@click.command(
    "init-lambda-task", help="Create a new LambdaTask database entry."
)
@click.option(
    "--status", default="InProgress", help="The status of the LambdaTask."
)
@with_appcontext
def init_lambda_task_click(status):
    init_lambda_task(status)


@click.command(
    "delete-lambda-tasks", help="Delete all LambdaTask database entries."
)
@with_appcontext
def delete_lambda_tasks_click():
    delete_lambda_tasks()


@click.command(
    "export-accounts-to-cognito", help="Export accounts to AWS Cognito."
)
@with_appcontext
def export_accounts_to_cognito_click():
    """Export accounts to AWS Cognito for researcher authentication."""
    # This is a stub function to fix the import error
    # The actual implementation would interact with AWS Cognito
    click.echo("Export accounts to AWS Cognito functionality would go here.")


@click.command(
    "create-researcher-account", help="Create a new researcher account."
)
@click.option("--email", default=None, help="The email of the researcher.")
@with_appcontext
def create_researcher_account_click(email):
    if email is None:
        raise RuntimeError("Option `email` is required.")

    account = Account(
        created_on=datetime.now(),
        last_login=datetime.now(),
        first_name="Jane",
        last_name="Doe",
        email=email,
        phone_number="+12345678901",
        is_confirmed=True,
    )

    db.session.add(account)
    db.session.flush()

    # Give the account access to all groups
    admin_group = AccessGroup.query.filter_by(name="Admin").first()
    ditti_group = AccessGroup.query.filter_by(name="Ditti App Admin").first()
    wearable_group = AccessGroup.query.filter_by(
        name="Wearable Dashboard Admin"
    ).first()

    if not (admin_group and ditti_group and wearable_group):
        raise RuntimeError("One or more access groups were not found.")

    db.session.add(
        JoinAccountAccessGroup(
            account_id=account.id, access_group_id=admin_group.id
        )
    )
    db.session.add(
        JoinAccountAccessGroup(
            account_id=account.id, access_group_id=ditti_group.id
        )
    )
    db.session.add(
        JoinAccountAccessGroup(
            account_id=account.id, access_group_id=wearable_group.id
        )
    )

    db.session.commit()

    click.echo("Researcher account successfully created.")
