from sqlalchemy import tuple_
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped

from aws_portal.extensions import db


class BasePermission:
    @declared_attr
    def id(cls) -> Mapped[int]:
        return db.Column(db.Integer, primary_key=True)

    @declared_attr
    def value(cls) -> Mapped[str]:
        return db.Column(db.String, nullable=False, unique=True)

    @declared_attr
    def display_label(cls) -> Mapped[str]:
        return db.Column(db.String, unique=True)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return {
            "id": self.id,
            "value": self.value,
            "displayLabel": self.display_label,
        }


class AppPermission(BasePermission, db.Model):
    __tablename__ = "app_permission"

    def __repr__(self):
        return "<Permission %s>" % self.value


class StudyPermission(BasePermission, db.Model):
    __tablename__ = "study_permission"

    def __repr__(self):
        return "<Permission %s>" % self.value


class BaseRole:
    @declared_attr
    def id(cls) -> Mapped[int]:
        return db.Column(db.Integer, primary_key=True)

    @declared_attr
    def name(cls) -> Mapped[str]:
        return db.Column(db.String, nullable=False)

    @declared_attr
    def is_archived(cls) -> Mapped[bool]:
        return db.Column(db.Boolean, default=False, nullable=False)

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


class AppRole(BaseRole, db.Model):
    __tablename__ = "app_role"

    permissions = db.relationship(
        "JoinAppRolePermission",
        back_populates="app_role",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return "<AppRole %s>" % self.name


class StudyRole(BaseRole, db.Model):
    __tablename__ = "study_role"

    permissions = db.relationship(
        "JoinStudyRolePermission",
        back_populates="study_role",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return "<StudyRole %s>" % self.name


class JoinAppRolePermission(db.Model):
    __tablename__ = "join_app_role_permission"

    app_role_id = db.Column(
        db.Integer,
        db.ForeignKey("app_role.id", ondelete="CASCADE"),
        primary_key=True
    )

    app_permission_id = db.Column(
        db.Integer,
        db.ForeignKey("app_permission.id", ondelete="CASCADE"),
        primary_key=True
    )

    app_role = db.relationship("AppRole", back_populates="permissions")
    app_permission = db.relationship("AppPermission")

    @hybrid_property
    def primary_key(self):
        """
        tuple of int: an entry's primary key.
        """
        return self.app_role_id, self.app_permission_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.app_role_id, cls.app_permission_id)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return self.app_permission.meta

    def __repr__(self):
        return "<JoinAppRolePermission %s-%s>" % self.primary_key


class JoinStudyRolePermission(db.Model):
    __tablename__ = "join_study_role_permission"

    study_role_id = db.Column(
        db.Integer,
        db.ForeignKey("study_role.id", ondelete="CASCADE"),
        primary_key=True
    )

    study_permission_id = db.Column(
        db.Integer,
        db.ForeignKey("study_permission.id", ondelete="CASCADE"),
        primary_key=True
    )

    study_role = db.relationship("StudyRole", back_populates="permissions")
    study_permission = db.relationship("StudyPermission")

    @hybrid_property
    def primary_key(self):
        """
        tuple of int: an entry's primary key.
        """
        return self.study_role_id, self.study_permission_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.study_role_id, cls.study_permission_id)

    @property
    def meta(self):
        """
        dict: an entry's metadata.
        """
        return self.study_permission.meta

    def __repr__(self):
        return "<JoinStudyRolePermission %s-%s>" % self.primary_key


class JoinAccountStudy(db.Model):
    __tablename__ = "join_account_study"

    account_id = db.Column(db.
        Integer,
        db.ForeignKey("account.id"),
        primary_key=True
    )

    study_id = db.Column(db.
        Integer,
        db.ForeignKey("study.id", ondelete="CASCADE"),
        primary_key=True
    )

    account = db.relationship("Account", back_populates="studies")
    study = db.relationship("Study")

    study_role_id = db.Column(db.
        Integer,
        db.ForeignKey("study_role.id", ondelete="CASCADE"),
        nullable=False
    )

    study_role = db.relationship("StudyRole")

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
            "role": self.study_role.meta
        }

    def __repr__(self):
        return "<JoinAccountStudy %s-%s>" % self.primary_key


class JoinAccountAppRole(db.Model):
    __tablename__ = "join_account_app_role"

    account_id = db.Column(db.
        Integer,
        db.ForeignKey("account.id"),
        primary_key=True
    )

    app_role_id = db.Column(db.
        Integer,
        db.ForeignKey("app_role.id", ondelete="CASCADE"),
        primary_key=True
    )

    account = db.relationship("Account", back_populates="app_roles")
    app_role = db.relationship("AppRole")

    @hybrid_property
    def primary_key(self):
        return self.account_id, self.app_role_id

    @primary_key.expression
    def primary_key(cls):
        return tuple_(cls.account_id, cls.app_role_id)

    @property
    def meta(self):
        return self.app_role.meta

    def __repr__(self):
        return "<JoinAccountAppRole %s-%s>" % self.primary_key
