import click
from flask.cli import with_appcontext
from aws_portal.models import (
    init_admin_app, init_admin_group, init_admin_account, init_db
)


@click.command('init-admin-app')
@with_appcontext
def init_admin_app_click():
    app = init_admin_app()
    click.echo(repr(app))


@click.command('init-admin-group')
@with_appcontext
def init_admin_group_click():
    access_group = init_admin_group()
    click.echo(repr(access_group))


@click.command('init-admin')
@with_appcontext
def init_admin_account_click():
    admin = init_admin_account()
    click.echo(repr(admin))


@click.command('init-db')
@with_appcontext
def init_db_click():
    init_db()
    click.echo('Database successfully initialized.')
