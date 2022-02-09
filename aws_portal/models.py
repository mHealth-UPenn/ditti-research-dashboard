from datetime import datetime
import logging
import os
import uuid
from flask import current_app
from sqlalchemy import func, tuple_
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from sqlalchemy.sql.schema import UniqueConstraint
from aws_portal.extensions import bcrypt, db, jwt

logger = logging.getLogger(__name__)


def init_db():
    db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']

    if current_app.config['TESTING']:
        db.drop_all()
        db.create_all()

    elif 'localhost' in db_uri:
        db.create_all()

    else:
        raise RuntimeError(
            'init_db requires either a testing evironment or a localhost datab'
            + 'ase URI.'
        )


def init_admin_app():
    query = App.name == 'Admin Dashboard'
    app = App.query.filter(query).first()

    if app is not None:
        raise ValueError('This app already exists: %s' % app)

    app = App(name='Admin Dashboard')
    db.session.add(app)
    db.session.commit()

    return app


def init_admin_group():
    query = AccessGroup.name == 'Admin'
    access_group = AccessGroup.query.filter(query).first()

    if access_group is not None:
        raise ValueError('This access group already exists: %s' % access_group)

    query = App.name == 'Admin Dashboard'
    app = App.query.filter(query).first()

    if app is None:
        raise ValueError(
            'The admin dashboard app has not been created. It can be created u'
            + 'sing `flask init-admin-app`'
        )

    access_group = AccessGroup(name='Admin', app=app)
    permission = Permission(action='*', resource='*')
    join = JoinAccessGroupPermission(
        access_group=access_group,
        permission=permission
    )

    db.session.add(permission)
    db.session.add(access_group)
    db.session.add(join)
    db.session.commit()

    return access_group


def init_admin_account():
    email = os.getenv('FLASK_ADMIN_EMAIL')
    password = os.getenv('FLASK_ADMIN_PASSWORD')
    admin = Account.query.filter(Account.email == email).first()

    if admin is not None:
        raise ValueError('An admin account already exists: %s' % admin)

    query = AccessGroup.name == 'Admin'
    access_group = AccessGroup.query.filter(query).first()

    if access_group is None:
        raise ValueError(
            'The admin access group has not been created. It can be created us'
            + 'ing `flask init-access-group`'
        )

    admin = Account(
        public_id=str(uuid.uuid4()),
        created_on=datetime.utcnow(),
        first_name='AWS',
        last_name='Admin',
        email=email,
        is_confirmed=True
    )

    db.session.flush()
    admin.password = password
    join = JoinAccountAccessGroup(account=admin, access_group=access_group)
    db.session.add(join)
    db.session.add(admin)
    db.session.commit()

    return admin


@jwt.user_identity_loader
def user_identity_lookup(account):
    return account.public_id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return Account.query.filter(Account.public_id == identity).first()


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    print('checking %s' % jti)
    token = BlockedToken.query.filter(BlockedToken.jti == jti).first()
    return token is not None


class Account(db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String, nullable=False, unique=True)
    created_on = db.Column(db.DateTime, nullable=False)
    last_login = db.Column(db.DateTime)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    is_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    _password = db.Column(db.String, nullable=False)

    access_groups = db.relationship(
        'JoinAccountAccessGroup',
        back_populates='account',
        cascade='all, delete-orphan',
        primaryjoin=(
            'and_(' +
            '   Account.id == JoinAccountAccessGroup.account_id,' +
            '   JoinAccountAccessGroup.access_group_id == AccessGroup.id,' +
            '   AccessGroup.is_archived == False' +
            ')'
        )
    )

    studies = db.relationship(
        'JoinAccountStudy',
        back_populates='account',
        cascade='all, delete-orphan',
        primaryjoin=(
            'and_(' +
            '   Account.id == JoinAccountStudy.account_id,' +
            '   JoinAccountStudy.study_id == Study.id,' +
            '   Study.is_archived == False' +
            ')'
        )
    )

    @validates('created_on')
    def validate_created_on(self, key, val):
        if self.created_on:
            raise ValueError('Account.created_on cannot be modified.')

        return val

    @hybrid_property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @full_name.expression
    def full_name(cls):
        return func.concat(cls.first_name, ' ', cls.last_name)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, val):
        password_hash = bcrypt.generate_password_hash(val).decode('utf-8')
        self._password = password_hash
        return True

    def check_password(self, val):
        return bcrypt.check_password_hash(self._password, val)

    def get_permissions(self, group_id, study_id=None):
        q1 = Permission.query.join(JoinAccessGroupPermission)\
            .join(AccessGroup)\
            .join(JoinAccountAccessGroup)\
            .filter(
                (~AccessGroup.is_archived) &
                (
                    JoinAccountAccessGroup.primary_key ==
                    tuple_(self.id, group_id)
                )
            )

        if study_id and not Study.query.get(study_id).is_archived:
            q2 = Permission.query.join(JoinRolePermission)\
                .join(Role)\
                .join(JoinAccountStudy, Role.id == JoinAccountStudy.role_id)\
                .filter(
                    JoinAccountStudy.primary_key == tuple_(self.id, study_id)
                )

            permissions = q1.union(q2)

        else:
            permissions = q1

        return permissions

    def validate_ask(self, action, resource, permissions):
        query = Permission.definition == tuple_(action, resource)
        query = query | (Permission.definition == tuple_('*', resource))
        query = query | (Permission.definition == tuple_('*', '*'))
        valid = permissions.filter(query).first()

        if valid is None:
            raise ValueError('Unauthorized Ask')

    @property
    def meta(self):
        return {
            'ID': self.id,
            'CreatedOn': self.created_on,
            'LastLogin': self.last_login,
            'FirstName': self.first_name,
            'LastName': self.last_name,
            'Email': self.email,
            'IsConfirmed': self.is_confirmed,
            'AccessGroups': [j.access_group.meta for j in self.access_groups],
            'Studies': [s.meta for s in self.studies]
        }

    def __repr__(self):
        return '<Account %s>' % self.email


class JoinAccountAccessGroup(db.Model):
    __tablename__ = 'join_account_access_group'

    account_id = db.Column(
        db.Integer,
        db.ForeignKey('account.id'),
        primary_key=True
    )

    access_group_id = db.Column(
        db.Integer,
        db.ForeignKey('access_group.id', ondelete='CASCADE'),
        primary_key=True
    )

    account = db.relationship('Account', back_populates='access_groups')
    access_group = db.relationship('AccessGroup', back_populates='accounts')

    @hybrid_property
    def primary_key(self):
        return self.account_id, self.access_group_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.account_id, cls.access_group_id)

    def __repr__(self):
        return '<JoinAccountAccessGroup %s-%s>' % self.primary_key


class JoinAccountStudy(db.Model):
    __tablename__ = 'join_account_study'

    account_id = db.Column(
        db.Integer,
        db.ForeignKey('account.id'),
        primary_key=True
    )

    study_id = db.Column(
        db.Integer,
        db.ForeignKey('study.id', ondelete='CASCADE'),
        primary_key=True
    )

    account = db.relationship('Account', back_populates='studies')
    study = db.relationship('Study')

    role_id = db.Column(
        db.Integer,
        db.ForeignKey('role.id', ondelete='CASCADE'),
        nullable=False
    )

    role = db.relationship('Role')

    @hybrid_property
    def primary_key(self):
        return self.account_id, self.study_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.account_id, cls.study_id)

    @property
    def meta(self):
        return {
            **self.study.meta,
            'Role': self.role.meta
        }

    def __repr__(self):
        return '<JoinAccountStudy %s-%s>' % self.primary_key


class AccessGroup(db.Model):
    __tablename__ = 'access_group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    app_id = db.Column(db.Integer, db.ForeignKey('app.id', ondelete='CASCADE'))
    app = db.relationship('App')

    accounts = db.relationship(
        'JoinAccountAccessGroup',
        back_populates='access_group',
        cascade='all, delete-orphan',
        primaryjoin=(
            'and_(' +
            '   AccessGroup.id == JoinAccountAccessGroup.access_group_id,' +
            '   JoinAccountAccessGroup.account_id == Account.id,' +
            '   Account.is_archived == False' +
            ')'
        )
    )

    roles = db.relationship(
        'Role',
        back_populates='access_group',
        cascade='all, delete-orphan'
    )

    permissions = db.relationship(
        'JoinAccessGroupPermission',
        back_populates='access_group',
        cascade='all, delete-orphan'
    )

    studies = db.relationship(
        'JoinAccessGroupStudy',
        back_populates='access_group',
        cascade='all, delete-orphan',
        primaryjoin=(
            'and_(' +
            '   AccessGroup.id == JoinAccessGroupStudy.access_group_id,' +
            '   JoinAccessGroupStudy.study_id == Study.id,' +
            '   Study.is_archived == False' +
            ')'
        )
    )

    @property
    def meta(self):
        return {
            'Name': self.name,
            'Roles': [r.meta for r in self.roles],
            'Studies': [j.study.meta for j in self.studies]
        }

    def __repr__(self):
        return '<AccessGroup %s>' % self.name


class JoinAccessGroupPermission(db.Model):
    __tablename__ = 'join_access_group_permission'

    access_group_id = db.Column(
        db.Integer,
        db.ForeignKey('access_group.id', ondelete='CASCADE'),
        primary_key=True
    )

    permission_id = db.Column(
        db.Integer,
        db.ForeignKey('permission.id', ondelete='CASCADE'),
        primary_key=True
    )

    access_group = db.relationship('AccessGroup', back_populates='permissions')
    permission = db.relationship('Permission')

    @hybrid_property
    def primary_key(self):
        return self.access_group_id, self.permission_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.access_group_id, cls.permission_id)

    def __repr__(self):
        return '<JoinAccessGroupPermission %s-%s>' % self.primary_key


class JoinAccessGroupStudy(db.Model):
    __tablename__ = 'join_access_group_study'

    access_group_id = db.Column(
        db.Integer,
        db.ForeignKey('access_group.id', ondelete='CASCADE'),
        primary_key=True
    )

    study_id = db.Column(
        db.Integer,
        db.ForeignKey('study.id', ondelete='CASCADE'),
        primary_key=True
    )

    access_group = db.relationship('AccessGroup', back_populates='studies')
    study = db.relationship('Study')

    @hybrid_property
    def primary_key(self):
        return self.access_group_id, self.study_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.access_group_id, cls.study_id)

    def __repr__(self):
        return '<JoinAccessGroupStudy %s-%s>' % self.primary_key


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    access_group_id = db.Column(
        db.Integer,
        db.ForeignKey('access_group.id', ondelete='CASCADE')
    )

    access_group = db.relationship('AccessGroup', back_populates='roles')

    permissions = db.relationship(
        'JoinRolePermission',
        back_populates='role',
        cascade='all, delete-orphan'
    )

    @property
    def meta(self):
        return {
            'Name': self.name,
            'Permissions': [p.permission.meta for p in self.permissions]
        }

    def __repr__(self):
        return '<Role %s %s>' % (self.access_group.name, self.name)


class JoinRolePermission(db.Model):
    __tablename__ = 'join_role_permission'

    role_id = db.Column(
        db.Integer,
        db.ForeignKey('role.id', ondelete='CASCADE'),
        primary_key=True
    )

    permission_id = db.Column(
        db.Integer,
        db.ForeignKey('permission.id', ondelete='CASCADE'),
        primary_key=True
    )

    role = db.relationship('Role', back_populates='permissions')
    permission = db.relationship('Permission')

    @hybrid_property
    def primary_key(self):
        return self.role_id, self.permission_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.role_id, cls.permission_id)

    def __repr__(self):
        return '<JoinRolePermission %s-%s>' % self.primary_key


class Permission(db.Model):
    __tablename__ = 'permission'
    __table_args__ = (UniqueConstraint('action', 'resource'),)
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String, nullable=False)
    resource = db.Column(db.String, nullable=False)

    @validates('action')
    def validate_action(self, key, val):
        if self.action is not None:
            raise ValueError('permission.action cannot be modified.')

        return val

    @validates('resource')
    def validate_resource(self, key, val):
        if self.resource:
            raise ValueError('permission.resource cannot be modified.')

        return val

    @hybrid_property
    def definition(self):
        return self.action, self.resource

    @definition.expression
    def definition(cls):
        return tuple_(cls.action, cls.resource)

    @property
    def meta(self):
        return {
            'Action': self.action,
            'Resource': self.resource
        }

    def __repr__(self):
        return '<Permission %s %s>' % self.definition


class App(db.Model):
    __tablename__ = 'app'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    @property
    def meta(self):
        return {
            'Name': self.name
        }

    def __repr__(self):
        return '<App %s>' % self.name


class Study(db.Model):
    __tablename__ = 'study'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    acronym = db.Column(db.String, nullable=False, unique=True)
    ditti_id = db.Column(db.String, nullable=False, unique=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    @property
    def meta(self):
        return {
            'Name': self.name,
            'Acronym': self.acronym,
            'DittiID': self.ditti_id,
        }

    def __repr__(self):
        return '<Study %s>' % self.acronym


class BlockedToken(db.Model):
    __tablename__ = 'blocked_token'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<BlockedToken %s>' % self.id
