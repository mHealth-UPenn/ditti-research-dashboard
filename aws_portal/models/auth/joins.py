from sqlalchemy import tuple_
from sqlalchemy.ext.hybrid import hybrid_property
from aws_portal.extensions import db


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
