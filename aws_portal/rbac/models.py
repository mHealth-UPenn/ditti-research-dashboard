from typing import Literal

from sqlalchemy import select, tuple_
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, validates
from sqlalchemy.sql.schema import UniqueConstraint

from aws_portal.extensions import db
from aws_portal.rbac.query_class import _QueryClass

type RBACType = Literal["study", "account"]


class Role(db.Model):
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
    __tablename__ = "join_role_permission"

    role_id = db.Column(db.
        Integer,
        db.ForeignKey("role.id", ondelete="CASCADE"),
        primary_key=True
    )

    permission_id = db.Column(db.
        Integer,
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


# class Action(db.Model):
#     __tablename__ = "action"
#     id = db.Column(db.Integer, primary_key=True)
#     value = db.Column(db.String, nullable=False, unique=True)
#     display_label = db.Column(db.String, unique=True)

#     @property
#     def meta(self):
#         """
#         dict: an entry's metadata.
#         """
#         return {
#             "id": self.id,
#             "value": self.value,
#             "displayLabel": self.display_label,
#         }

#     def __repr__(self):
#         return "<Action %s>" % self.value


# class Resource(db.Model):
#     __tablename__ = "resource"
#     id = db.Column(db.Integer, primary_key=True)
#     value = db.Column(db.String, nullable=False, unique=True)
#     display_label = db.Column(db.String, unique=True)

#     @property
#     def meta(self):
#         """
#         dict: an entry's metadata.
#         """
#         return {
#             "id": self.id,
#             "value": self.value,
#             "displayLabel": self.display_label,
#         }

#     def __repr__(self):
#         return "<Resource %s>" % self.value


# class Permission(db.Model):
#     __tablename__ = "permission"
#     __table_args__ = (UniqueConstraint("_action_id", "_resource_id"),)
#     id = db.Column(db.Integer, primary_key=True)

#     _action_id = db.Column(db.
#         Integer,
#         db.ForeignKey("action.id", ondelete="CASCADE")
#     )

#     _resource_id = db.Column(db.
#         Integer,
#         db.ForeignKey("resource.id", ondelete="CASCADE")
#     )

#     _action = db.relationship("Action")
#     _resource = db.relationship("Resource")

#     @hybrid_property
#     def action(self):
#         """
#         str: an entry's action
#         """
#         return self._action.value

#     @action.setter
#     def action(self, value: str):
#         q = select(Action.id).where(Action.value == value)
#         action_id = db.session.execute(q).scalar()
#         if not action_id:
#             action = Action(value=value)
#             db.session.add(action)
#             db.session.flush()
#         self._action_id = action_id
#         db.session.commit()

#     @action.expression
#     def action(cls):
#         return select(Action.value)\
#             .where(Action.id == cls._action_id)\
#             .scalar_subquery()

#     @hybrid_property
#     def resource(self):
#         return self._resource.value

#     @resource.setter
#     def resource(self, value: str):
#         q = select(Resource.id).where(Resource.value == value)
#         resource_id = db.session.execute(q).scalar()
#         if not resource_id:
#             resource = Resource(value=value)
#             db.session.add(resource)
#             db.session.flush()
#         self._resource_id = resource_id
#         db.session.commit()

#     @resource.expression
#     def resource(cls):
#         return select(Resource.value)\
#             .where(Resource.id == cls._resource_id)\
#             .scalar_subquery()

#     @validates("_action_id")
#     def validate_action(self, key, val):
#         if self._action_id is not None:
#             raise ValueError("permission.action cannot be modified.")
#         return val

#     @validates("_resource_id")
#     def validate_resource(self, key, val):
#         if self._resource_id is not None:
#             raise ValueError("permission.resource cannot be modified.")
#         return val

#     @hybrid_property
#     def definition(self):
#         return self.action, self.resource

#     @definition.expression
#     def definition(cls):
#         return tuple_(
#             select(Action.value)
#                 .where(Action.id == cls._action_id)
#                 .scalar_subquery(),
#             select(Resource.value)
#                 .where(Resource.id == cls._resource_id)
#                 .scalar_subquery()
#         )

#     @property
#     def meta(self):
#         """
#         dict: an entry's metadata.
#         """
#         return {
#             "id": self.id,
#             "action": self.action,
#             "resource": self.resource
#         }

#     def __repr__(self):
#         return "<Permission %s-%s>" % self.definition


class Permission(db.Model):
    __tablename__ = "permission"
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String, nullable=False, unique=True)
    display_label = db.Column(db.String, unique=True)

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

    def __repr__(self):
        return "<Permission %s>" % self.value


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

    role_id = db.Column(db.
        Integer,
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


class JoinAccountRole(db.Model):
    __tablename__ = "join_account_role"
    account_id = db.Column(db.
        Integer,
        db.ForeignKey("account.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id = db.Column(db.
        Integer,
        db.ForeignKey("role.id", ondelete="CASCADE"),
        primary_key=True,
    )
    study_id = db.Column(db.
        Integer,
        db.ForeignKey("study.id", ondelete="CASCADE"),
        primary_key=True,
    )
    account = db.relationship("Account", back_populates="roles")
    role = db.relationship("Role")
    study = db.relationship("Study")


class JoinAccountPermission(db.Model):
    __tablename__ = "join_account_permission"
    account_id = db.Column(db.
        Integer,
        db.ForeignKey("account.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id = db.Column(db.
        Integer,
        db.ForeignKey("permission.id", ondelete="CASCADE"),
        primary_key=True,
    )
    account = db.relationship("Account", back_populates="permissions")
    permission = db.relationship("Permission")


class RBACBase:
    query_class = _QueryClass()
    rbac_name: Mapped[str]


class RBACAccountMixin(RBACBase):
    rbac_type: RBACType = "account"

    @declared_attr
    def studies(cls) -> Mapped[JoinAccountStudy]:
        return db.relationship(
            "JoinAccountStudy",
            back_populates="account",
            cascade="all, delete-orphan",
        )

    @declared_attr
    def roles(cls) -> Mapped[JoinAccountRole]:
        return db.relationship(
            "JoinAccountRole",
            back_populates="account",
            cascade="all, delete-orphan",
        )

    @declared_attr
    def permissions(cls) -> Mapped[JoinAccountPermission]:
        return db.relationship(
            "JoinAccountPermission",
            back_populates="account",
            cascade="all, delete-orphan",
        )


class RBACStudyMixin(RBACBase):
    rbac_type: RBACType = "study"
