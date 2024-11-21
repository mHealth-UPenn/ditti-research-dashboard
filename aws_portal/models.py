from datetime import datetime, UTC
import logging
import os
import uuid
from flask import current_app
from sqlalchemy import func, select, tuple_
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from sqlalchemy.sql.schema import UniqueConstraint
from aws_portal.extensions import bcrypt, db, jwt, tm

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


class Account(db.Model):
    """
    The account table mappeing class.

    Vars
    ----
    id: sqlalchemy.Column
    public_id: sqlalchemy.Column
        A random string to be used for JWT authentication, e.g.,
        `public_id=str(uuid.uuid4())`.
    created_on: sqlalchemy.Column
        The timestamp of the account"s creation, e.g., `datetime.now(UTC)`.
        The created_on value cannot be modified.
    last_login: sqlalchemy.Column
    first_name: sqlalchemy.Column
    last_name: sqlalchemy.Column
    email: sqlalchemy.Column
    phone_number: sqlalchemy.Column
    is_confirmed: sqlalchemy.Column
        Whether the account holder has logged in and set their password.
    is_archived: sqlalchemy.Column
    access_groups: sqlalchemy.orm.relationship
    studies: sqlalchemy.orm.relationship
    """
    __tablename__ = "account"
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String, nullable=False, unique=True)
    created_on = db.Column(db.DateTime, nullable=False)
    last_login = db.Column(db.DateTime)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    phone_number = db.Column(db.String, nullable=True, unique=True)
    is_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    _password = db.Column(db.String, nullable=False)

    # ignore archived access groups
    access_groups = db.relationship(
        "JoinAccountAccessGroup",
        back_populates="account",
        cascade="all, delete-orphan",
        primaryjoin=(
            "and_(" +
            "   Account.id == JoinAccountAccessGroup.account_id," +
            "   JoinAccountAccessGroup.access_group_id == AccessGroup.id," +
            "   AccessGroup.is_archived == False" +
            ")"
        )
    )

    # ignore archived studies
    studies = db.relationship(
        "JoinAccountStudy",
        back_populates="account",
        cascade="all, delete-orphan",
        primaryjoin=(
            "and_(" +
            "   Account.id == JoinAccountStudy.account_id," +
            "   JoinAccountStudy.study_id == Study.id," +
            "   Study.is_archived == False" +
            ")"
        )
    )

    @validates("created_on")
    def validate_created_on(self, key, val):
        """
        Make the created_on column read-only.
        """
        if self.created_on:
            raise ValueError("Account.created_on cannot be modified.")

        return val

    @hybrid_property
    def full_name(self):
        """
        str: The full name of the account holder
        """
        return f"{self.first_name} {self.last_name}"

    @full_name.expression
    def full_name(cls):
        return func.concat(cls.first_name, " ", cls.last_name)

    @hybrid_property
    def password(self):
        """
        str: The account holder"s password
        """
        return self._password

    @password.setter
    def password(self, val):
        """
        Hashes the password using bcrypt
        """
        password_hash = bcrypt.generate_password_hash(val).decode("utf-8")
        self._password = password_hash
        return True

    def check_password(self, val):
        """
        Whether a password matches the account holder"s password.

        Args
        ----
        val: str
            The password to check.

        Returns
        -------
        bool
        """
        return bcrypt.check_password_hash(self._password, val)

    def get_permissions(self, app_id, study_id=None):
        """
        Get all of an account"s permissions for an app and optionally for a
        study.

        Args
        ----
        app_id: int
            The app"s primary key.
        study_id: int (optional)
            The study"s primary key.

        Returns
        -------
        """

        # query all permissions that are granted to the account by access
        # groups that grant access to the app
        q1 = Permission.query.join(JoinAccessGroupPermission)\
            .join(AccessGroup)\
            .filter(AccessGroup.app_id == app_id)\
            .join(JoinAccountAccessGroup)\
            .filter(
                (~AccessGroup.is_archived) &
                (JoinAccountAccessGroup.account_id == self.id)
        )

        # if a study id was passed and the study is not archived
        if study_id and not Study.query.get(study_id).is_archived:

            # query all permissions that are granted to the account by the
            # study
            q2 = Permission.query.join(JoinRolePermission)\
                .join(Role)\
                .join(JoinAccountStudy, Role.id == JoinAccountStudy.role_id)\
                .filter(
                    JoinAccountStudy.primary_key == tuple_(self.id, study_id)
            )

            # return the union of all permission for the app and study
            permissions = q1.union(q2)

        else:

            # return all permissions for the app
            permissions = q1

        return permissions

    def validate_ask(self, action, resource, permissions):
        """
        Validate a request using a set of permissions

        Args
        ----
        action: str
        resource: str
        permissions:

        Raises
        ------
        ValueError
            If the account has no permissions that satisfy the request.
        """

        # build a query using the requested action and resource
        query = Permission.definition == tuple_(action, resource)

        # also check if the account has wildcard permissions
        query = query | (Permission.definition == tuple_(action, "*"))
        query = query | (Permission.definition == tuple_("*", resource))
        query = query | (Permission.definition == tuple_("*", "*"))

        # filter the account"s permissions
        valid = permissions.filter(query).first()

        # if no permissions were found
        if valid is None:
            raise ValueError("Unauthorized Ask")

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "createdOn": self.created_on,
            "lastLogin": self.last_login,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "email": self.email,
            "phoneNumber": self.phone_number,
            "isConfirmed": self.is_confirmed,
            "accessGroups": [j.access_group.meta for j in self.access_groups],
            "studies": [s.meta for s in self.studies]
        }

    def __repr__(self):
        return "<Account %s>" % self.email


class JoinAccountAccessGroup(db.Model):
    """
    The join_account_access_group table mapping class.

    Vars
    ----
    account_id: sqlalchemy.Column
    access_group_id: sqlalchemy.Column
    account: sqlalchemy.orm.relationship
    access_group: sqlalchemy.orm.relationship
    """
    __tablename__ = "join_account_access_group"

    account_id = db.Column(
        db.Integer,
        db.ForeignKey("account.id"),
        primary_key=True
    )

    access_group_id = db.Column(
        db.Integer,
        db.ForeignKey("access_group.id", ondelete="CASCADE"),
        primary_key=True
    )

    account = db.relationship("Account", back_populates="access_groups")
    access_group = db.relationship("AccessGroup", back_populates="accounts")

    @hybrid_property
    def primary_key(self):
        """
        tuple of int: an entry's primary key.
        """
        return self.account_id, self.access_group_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.account_id, cls.access_group_id)

    def __repr__(self):
        return "<JoinAccountAccessGroup %s-%s>" % self.primary_key


class JoinAccountStudy(db.Model):
    """
    The join_account_study table mapping class.

    Vars
    ----
    account_id: sqlalchemy.Column
    study_id: sqlalchemy.Column
    account: sqlalchemy.orm.relationship
    study: sqlalchemy.orm.relationship
    role_id: sqlalchemy.Column
        The primary key of the role that an account is assigned for a study.
    role: sqlalchemy.orm.relationship
    """
    __tablename__ = "join_account_study"

    account_id = db.Column(
        db.Integer,
        db.ForeignKey("account.id"),
        primary_key=True
    )

    study_id = db.Column(
        db.Integer,
        db.ForeignKey("study.id", ondelete="CASCADE"),
        primary_key=True
    )

    account = db.relationship("Account", back_populates="studies")
    study = db.relationship("Study")

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("role.id", ondelete="CASCADE"),
        nullable=False
    )

    role = db.relationship("Role")

    @hybrid_property
    def primary_key(self):
        """
        tuple of int: an entry's primary key.
        """
        return self.account_id, self.study_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.account_id, cls.study_id)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            **self.study.meta,
            "role": self.role.meta
        }

    def __repr__(self):
        return "<JoinAccountStudy %s-%s>" % self.primary_key


class AccessGroup(db.Model):
    """
    The access_group table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    name: sqlalchemy.Column
    is_archived: sqlalchemy.Column
    app_id: sqlalchemy.Column
        The primary key of the app that an access group grants permissions for.
    app: sqlalchemy.orm.relationship
    accounts: sqlalchemy.orm.relationship
    permissions: sqlalchemy.orm.relationship
        The permissions that an access group grants for an app.
    """
    __tablename__ = "access_group"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    app_id = db.Column(db.Integer, db.ForeignKey("app.id", ondelete="CASCADE"))
    app = db.relationship("App")

    # ignore archived accounts
    accounts = db.relationship(
        "JoinAccountAccessGroup",
        back_populates="access_group",
        cascade="all, delete-orphan",
        primaryjoin=(
            "and_(" +
            "   AccessGroup.id == JoinAccountAccessGroup.access_group_id," +
            "   JoinAccountAccessGroup.account_id == Account.id," +
            "   Account.is_archived == False" +
            ")"
        )
    )

    permissions = db.relationship(
        "JoinAccessGroupPermission",
        back_populates="access_group",
        cascade="all, delete-orphan"
    )

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "name": self.name,
            "app": self.app.meta,
            "permissions": [p.meta for p in self.permissions]
        }

    def __repr__(self):
        return "<AccessGroup %s>" % self.name


class JoinAccessGroupPermission(db.Model):
    """
    The join_access_group_permission table mapping class.

    Vars
    ----
    access_group_id: sqlalchemy.Column
    permission_id: sqlalchemy.Column
    access_group: sqlalchemy.orm.relationship
    permission: sqlalchemy.orm.relationship
    """
    __tablename__ = "join_access_group_permission"

    access_group_id = db.Column(
        db.Integer,
        db.ForeignKey("access_group.id", ondelete="CASCADE"),
        primary_key=True
    )

    permission_id = db.Column(
        db.Integer,
        db.ForeignKey("permission.id", ondelete="CASCADE"),
        primary_key=True
    )

    access_group = db.relationship("AccessGroup", back_populates="permissions")
    permission = db.relationship("Permission")

    @hybrid_property
    def primary_key(self):
        """
        tuple of int: an entry's primary key
        """
        return self.access_group_id, self.permission_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.access_group_id, cls.permission_id)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return self.permission.meta

    def __repr__(self):
        return "<JoinAccessGroupPermission %s-%s>" % self.primary_key


class Role(db.Model):
    """
    The role table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    name: sqlalchemy.Column
    is_archived: sqlalchemy.Column
    permissions: sqlalchemy.orm.relationship
    """
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    permissions = db.relationship(
        "JoinRolePermission",
        back_populates="role",
        cascade="all, delete-orphan"
    )

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "name": self.name,
            "permissions": [p.meta for p in self.permissions]
        }

    def __repr__(self):
        return "<Role %s>" % self.name


class JoinRolePermission(db.Model):
    """
    The join_role_permission table mapping class.

    Vars
    ----
    role_id: sqlalchemy.Column
    permission_id: sqlalchemy.Column
    role: sqlalchemy.orm.relationship
    permission: sqlalchemy.orm.relationship
    """
    __tablename__ = "join_role_permission"

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("role.id", ondelete="CASCADE"),
        primary_key=True
    )

    permission_id = db.Column(
        db.Integer,
        db.ForeignKey("permission.id", ondelete="CASCADE"),
        primary_key=True
    )

    role = db.relationship("Role", back_populates="permissions")
    permission = db.relationship("Permission")

    @hybrid_property
    def primary_key(self):
        """
        tuple of int: an entry's primary key.
        """
        return self.role_id, self.permission_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.role_id, cls.permission_id)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return self.permission.meta

    def __repr__(self):
        return "<JoinRolePermission %s-%s>" % self.primary_key


class Action(db.Model):
    """
    The action table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    value: sqlalchemy.Column
    """
    __tablename__ = "action"
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String, nullable=False, unique=True)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "value": self.value
        }

    def __repr__(self):
        return "<Action %s>" % self.value


class Resource(db.Model):
    """
    The resource table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    value: sqlalchemy.Column
    """
    __tablename__ = "resource"
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String, nullable=False, unique=True)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "value": self.value
        }

    def __repr__(self):
        return "<Resource %s>" % self.value


class Permission(db.Model):
    """
    The permission table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    """
    __tablename__ = "permission"

    # ensure the action-resource combination is unique.
    __table_args__ = (UniqueConstraint("_action_id", "_resource_id"),)
    id = db.Column(db.Integer, primary_key=True)

    _action_id = db.Column(
        db.Integer,
        db.ForeignKey("action.id", ondelete="CASCADE")
    )

    _resource_id = db.Column(
        db.Integer,
        db.ForeignKey("resource.id", ondelete="CASCADE")
    )

    _action = db.relationship("Action")
    _resource = db.relationship("Resource")

    @hybrid_property
    def action(self):
        """
        str: an entry's action
        """
        return self._action.value

    @action.setter
    def action(self, value):
        q = Action.query.filter(Action.value == value)

        # if the action does not exist, create a new action
        action = q.first() or Action(value=value)
        db.session.add(action)
        self._action = action

    @action.expression
    def action(cls):
        return select(Action.value)\
            .where(Action.id == cls._action_id)\
            .scalar_subquery()

    @hybrid_property
    def resource(self):
        """
        str: an entry's resource
        """
        return self._resource.value

    @resource.setter
    def resource(self, value):
        q = Resource.query.filter(Resource.value == value)

        # if the resource does not exist, create a new resource
        resource = q.first() or Resource(value=value)
        db.session.add(resource)
        self._resource = resource

    @resource.expression
    def resource(cls):
        return select(Resource.value)\
            .where(Resource.id == cls._resource_id)\
            .scalar_subquery()

    @validates("_action_id")
    def validate_action(self, key, val):
        """
        Ensure an entry's action cannot be modified.
        """
        if self._action_id is not None:
            raise ValueError("permission.action cannot be modified.")

        return val

    @validates("_resource_id")
    def validate_resource(self, key, val):
        """
        Ensure an entry's resource cannot be modified.
        """
        if self._resource_id is not None:
            raise ValueError("permission.resource cannot be modified.")

        return val

    @hybrid_property
    def definition(self):
        """
        tuple of str: an entry's (action, resource) definition
        """
        return self.action, self.resource

    @definition.expression
    def definition(cls):
        return tuple_(
            select(Action.value)
            .where(Action.id == cls._action_id)
            .scalar_subquery(),
            select(Resource.value)
            .where(Resource.id == cls._resource_id)
            .scalar_subquery()
        )

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "action": self.action,
            "resource": self.resource
        }

    def __repr__(self):
        return "<Permission %s %s>" % self.definition


class App(db.Model):
    """
    The app table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    name: sqlalchemy.Column
    """
    __tablename__ = "app"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "name": self.name
        }

    def __repr__(self):
        return "<App %s>" % self.name


# TODO: Add Why We Are Collecting Your Data
class Study(db.Model):
    """
    The study table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    name: sqlalchemy.Column
    acronym: sqlalchemy.Column
    ditti_id: sqlalchemy.Column
    email: sqlalchemy.Column
    default_expiry_delta: sqlalchemy.Column
        The default amount of time in number of days that a subject is enrolled
        in the study. A subject's expires_on column will be automatically set
        according to this value.
    consent_information: sqlalchemt.Column
        The consent text to show to a study subject.
    is_archived: sqlalchemy.Column
    roles: sqlalchemy.orm.relationship
    """
    __tablename__ = "study"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    acronym = db.Column(db.String, nullable=False, unique=True)
    ditti_id = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    default_expiry_delta = db.Column(db.Integer)
    consent_information = db.Column(db.String)

    roles = db.relationship("JoinStudyRole", cascade="all, delete-orphan")

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "name": self.name,
            "acronym": self.acronym,
            "dittiId": self.ditti_id,
            "email": self.email,
            "roles": [r.meta for r in self.roles]
        }

    def __repr__(self):
        return "<Study %s>" % self.acronym


class JoinStudyRole(db.Model):
    """
    The join_study_role table mapping class.

    Vars
    ----
    study_id: sqlalchemy.Column
    role_id: sqlalchemy.Column
    study: sqlalchemy.orm.relationship
    role: sqlalchemy.orm.relationship
    """
    __tablename__ = "join_study_role"

    study_id = db.Column(
        db.Integer,
        db.ForeignKey("study.id"),
        primary_key=True
    )

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("role.id", ondelete="CASCADE"),
        primary_key=True
    )

    study = db.relationship("Study", back_populates="roles")
    role = db.relationship("Role")

    @hybrid_property
    def primary_key(self):
        """
        tuple of int: an entry's primary key.
        """
        return self.study_id, self.role_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.study_id, cls.role_id)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return self.role.meta

    def __repr__(self):
        return "<JoinStudyRole %s-%s>" % self.primary_key


class BlockedToken(db.Model):
    """
    The blocked_token table mapping class. This is used to log users out using
    JWT tokens.

    Vars
    ----
    id: sqlalchemy.Column
    jti: sqlalchemy.Column
        The token to block.
    created_on: sqlalchemy.Column
    """
    __tablename__ = "blocked_token"
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return "<BlockedToken %s>" % self.id


class AboutSleepTemplate(db.Model):
    """
    The about_sleep_template table mapping class.

    Vars
    ----
    id: sqlalchemy.Column
    name: sqlalchemy.Column
    text: sqlalchemy.Column
    is_archived: sqlalchemy.Column
    """
    __tablename__ = "about_sleep_template"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    text = db.Column(db.String, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "name": self.name,
            "text": self.text
        }

    def __repr__(self):
        return "<AboutSleepTemplate %s>" % self.name


class StudySubject(db.Model):
    """
    The study_subject table mapping calss

    Vars
    ----
    id: sqlalchemy.Column
    created_on: sqlalchemy.Column
    email: sqlalchemy.Column
        The study subject's email as it is stored in AWS Cognito
    is_confirmed: sqlalchemy.Column
        Whether the user verified their email with AWS Cognito
    is_archived: sqlalchemy.Column
    studies: sqlalchemy.Column
        Any studies the subject is enrolled in
    apis: sqlalchemy.Column
        Any APIs that the subject has granted access to
    """
    __tablename__ = "study_subject"
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    is_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    # ignore archived studies
    studies = db.relationship(
        "JoinStudySubjectStudy",
        back_populates="study_subject",
        cascade="all, delete-orphan",
        primaryjoin=(
            "and_(" +
            "   StudySubject.id == JoinStudySubjectStudy.study_subject_id," +
            "   JoinStudySubjectStudy.study_id == Study.id," +
            "   Study.is_archived == False" +
            ")"
        )
    )

    # ignore archived apis
    apis = db.relationship(
        "JoinStudySubjectApi",
        back_populates="study_subject",
        cascade="all, delete-orphan",
        primaryjoin=(
            "and_(" +
            "   StudySubject.id == JoinStudySubjectApi.study_subject_id," +
            "   JoinStudySubjectApi.api_id == Api.id," +
            "   Api.is_archived == False" +
            ")"
        )
    )

    @property
    def meta(self):
        return {
            "id": self.id,
            "createdOn": self.created_on,
            "email": self.email,
            "isConfirmed": self.is_confirmed,
            "studies": [join.meta for join in self.studies],
            "apis": [join.meta for join in self.apis],
        }

    def __repr__(self):
        return f"<StudySubject {self.email}>"


class JoinStudySubjectStudy(db.Model):
    """
    The join_study_subject_study table mapping class.

    Vars
    ----
    study_subject_id: sqlalchemy.Column
    study_id: sqlalchemy.Column
    did_consent: sqlalchemy.Column
        Whether the study subject consented to the collection of their data
    expires_on: sqlalchemy.Column
        When the study is no longer a part of the study and data should no
        longer be collected from any of the subject's approved APIs
    study_subject: sqlalchemy.orm.relationship
    study: sqlalchemy.orm.relationship
    """
    __tablename__ = "join_study_subject_study"

    study_subject_id = db.Column(
        db.Integer,
        db.ForeignKey("study_subject.id", ondelete="CASCADE"),
        primary_key=True
    )

    study_id = db.Column(
        db.Integer,
        db.ForeignKey("study.id"),  # do not allow deletions on study table
        primary_key=True
    )

    did_consent = db.Column(db.Boolean, default=False, nullable=False)
    expires_on = db.Column(db.DateTime, nullable=False)

    study_subject = db.relationship("StudySubject", back_populates="studies")
    study = db.relationship("Study")

    @hybrid_property
    def primary_key(self):
        """
        tuple of int: an entry's primary key.
        """
        return self.study_subject_id, self.study_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.study_subject_id, cls.study_id)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "did_consent": self.did_consent,
            "expires_on": self.expires_on,
            "study": self.study.meta,
        }

    def __repr__(self):
        return "<JoinStudySubjectStudy %s-%s>" % self.primary_key


class JoinStudySubjectApi(db.Model):
    """
    The join_study_subject_api table mapping class.

    Vars
    ----
    study_subject_id: sqlalchemy.Column
    api_id: sqlalchemy.Column
    api_user_uuid: sqlalchemy.Column
        The study subject's user ID associated with the API
    scope: sqlalchemy.Column
        The scope of data that the study subject approved access for
    access_key_uuid: sqlalchemy.Column
        DEPRECATED
    refresh_key_uuid: sqlalchemy.Column
        DEPRECATED
    study_subject: sqlalchemy.orm.relationship
    api: sqlalchemy.orm.relationship
    """
    __tablename__ = "join_study_subject_api"

    study_subject_id = db.Column(
        db.Integer,
        db.ForeignKey("study_subject.id", ondelete="CASCADE"),
        primary_key=True
    )

    api_id = db.Column(
        db.Integer,
        db.ForeignKey("api.id"),  # Do not allow deletion on api table
        primary_key=True
    )

    api_user_uuid = db.Column(db.String, nullable=False)
    scope = db.Column(db.ARRAY(db.String))
    access_key_uuid = db.Column(db.String, unique=True)
    refresh_key_uuid = db.Column(db.String, unique=True)

    study_subject = db.relationship("StudySubject", back_populates="apis")
    api = db.relationship("Api")

    @hybrid_property
    def primary_key(self):
        """
        tuple of int: an entry's primary key.
        """
        return self.study_subject_id, self.api_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.study_subject_id, cls.api_id)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        metadata = {
            "api_user_uuid": self.api_user_uuid,
            "scope": self.scope,
            "access_key_uuid": self.access_key_uuid,
            "refresh_key_uuid": self.refresh_key_uuid,
            "api": self.api.meta,
        }

        try:
            tokens = tm.get_api_tokens(self.api.name, self.study_subject_id)
            expires_at_unix = tokens.get('expires_at')
            metadata['expires_at'] = (
                datetime.fromtimestamp(expires_at_unix).isoformat()
                if expires_at_unix is not None
                else None
            )
        except Exception:
            metadata['expires_at'] = None

        return metadata

    def __repr__(self):
        return "<JoinStudySubjectApi %s-%s>" % self.primary_key


class Api(db.Model):
    """
    The api table mapping class

    Vars
    ----
    id: sqlalchemy.Column
    name: sqlalchemy.Column
    is_archived: sqlalchemy.Column
    """
    __tablename__ = "api"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "name": self.name
        }

    def __repr__(self):
        return "<Api %s>" % self.name
