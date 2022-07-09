import click
from flask import current_app
from flask.cli import with_appcontext
from aws_portal.models import (
    init_admin_app, init_admin_group, init_admin_account, init_db
)


@click.command('init-admin-app')
@click.option('--uri', default=None, help='Overrides the SQLAlchemy URI.')
@with_appcontext
def init_admin_app_click(uri):
    if uri is not None:
        current_app.config['SQLALCHEMY_DATABASE_URI'] = uri

    app = init_admin_app()
    click.echo(repr(app))


@click.command('init-admin-group')
@click.option('--uri', default=None, help='Overrides the SQLAlchemy URI.')
@with_appcontext
def init_admin_group_click(uri):
    if uri is not None:
        current_app.config['SQLALCHEMY_DATABASE_URI'] = uri

    access_group = init_admin_group()
    click.echo(repr(access_group))


@click.command('init-admin')
@click.option('--uri', default=None, help='Overrides the SQLAlchemy URI.')
@with_appcontext
def init_admin_account_click(uri):
    if uri is not None:
        current_app.config['SQLALCHEMY_DATABASE_URI'] = uri

    admin = init_admin_account()
    click.echo(repr(admin))


@click.command('init-db')
@with_appcontext
def init_db_click():
    init_db()
    click.echo('Database successfully initialized.')
