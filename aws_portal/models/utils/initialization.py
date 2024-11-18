import logging
import os
import uuid
from datetime import datetime, UTC
from flask import current_app
from aws_portal.extensions import db, jwt

from ..auth.account import Account
from ..auth.access_group import AccessGroup
from ..auth.permission import Permission
from ..auth.joins import JoinAccessGroupPermission
from ..app.app_model import App
from ..auth.api import Api
from ..auth.joins import JoinAccountAccessGroup
from ..auth.joins import JoinAccessGroupPermission
from ..auth.blocked_token import BlockedToken

logger = logging.getLogger(__name__)


def init_db():
    """
    Create all database tables. This can only be run in a testing environment
    or if the database is hosted locally.

    Raises
    ------
    RuntimeError
        If this function is called outside of a testing environment or if the
        database URI does not contain "localhost."
    """
    db_uri = current_app.config["SQLALCHEMY_DATABASE_URI"]

    if current_app.config["TESTING"]:
        db.drop_all()
        db.create_all()

    elif "localhost" in db_uri:
        db.create_all()

    else:
        raise RuntimeError(
            "init_db requires either a testing evironment or a localhost datab"
            + "ase URI."
        )


def init_admin_app():
    """
    Initialize the admin dashboard app database entry.

    Returns
    -------
    App

    Raises
    ------
    ValueError
        If an entry for the admin dashboard app already exists.
    """
    query = App.name == "Admin Dashboard"
    app = App.query.filter(query).first()

    if app is not None:
        raise ValueError("This app already exists: %s" % app)

    app = App(name="Admin Dashboard")
    db.session.add(app)
    db.session.commit()

    return app


def init_admin_group():
    """
    Initialize the admin access group.

    Returns
    -------
    AccessGroup

    Raises
    ------
    ValueError
        If an entry for the admin access group already exists or if an entry
        for the admin dashboard app does not exist.
    """
    query = AccessGroup.name == "Admin"
    access_group = AccessGroup.query.filter(query).first()

    if access_group is not None:
        raise ValueError("This access group already exists: %s" % access_group)

    query = App.name == "Admin Dashboard"
    app = App.query.filter(query).first()

    if app is None:
        raise ValueError(
            "The admin dashboard app has not been created. It can be created u"
            + "sing `flask init-admin-app`"
        )

    access_group = AccessGroup(name="Admin", app=app)
    permission = Permission()
    permission.action = "*"
    permission.resource = "*"
    join = JoinAccessGroupPermission(
        access_group=access_group,
        permission=permission
    )

    db.session.add(permission)
    db.session.add(access_group)
    db.session.add(join)
    db.session.commit()

    return access_group


def init_admin_account(email=None, password=None):
    """
    Initialize the admin account

    Args
    ----
    email: str (optional)
    password: str (optional)

    Returns
    -------
    Account

    Raises
    ------
    ValueError
        If an entry for the admin account already exists or if an entry for the
        admin access group does not exist.
    """
    email = email or os.getenv("FLASK_ADMIN_EMAIL")
    password = password or os.getenv("FLASK_ADMIN_PASSWORD")
    admin = Account.query.filter(Account.email == email).first()

    if admin is not None:
        raise ValueError("An admin account already exists: %s" % admin)

    query = AccessGroup.name == "Admin"
    admin_group = AccessGroup.query.filter(query).first()

    if admin_group is None:
        raise ValueError(
            "The admin access group has not been created. It can be created us"
            + "ing `flask init-access-group`"
        )

    query = AccessGroup.name == "Ditti Admin"
    ditti_group = AccessGroup.query.filter(query).first()

    admin = Account(
        public_id=str(uuid.uuid4()),
        created_on=datetime.now(UTC),
        first_name="AWS",
        last_name="Admin",
        email=email,
        is_confirmed=True
    )

    db.session.flush()
    admin.password = password
    admin_join = JoinAccountAccessGroup(
        account=admin, access_group=admin_group
    )
    db.session.add(admin_join)

    # if an entry for the Ditti Admin group exists
    if ditti_group is not None:

        # add the admin account to it
        ditti_join = JoinAccountAccessGroup(
            account=admin, access_group=ditti_group
        )
        db.session.add(ditti_join)

    db.session.add(admin)
    db.session.commit()

    return admin


def init_api(click=None):
    """
    Insert Fitbit API entry.
    """
    api_name = "Fitbit"
    existing_api = Api.query.filter_by(name=api_name).first()

    if not existing_api:
        new_api = Api(name=api_name, is_archived=False)
        db.session.add(new_api)
        db.session.commit()
        message = f"<API {api_name}>"
    else:
        message = f"<API {api_name}> already exists with ID {existing_api.id}."

    if click:
        click.echo(message)


@jwt.user_identity_loader
def user_identity_lookup(account):
    return account.public_id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return Account.query.filter(Account.public_id == identity).first()


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    print("checking %s" % jti)
    token = BlockedToken.query.filter(BlockedToken.jti == jti).first()
    return token is not None
