from typing import Literal

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped

from aws_portal.extensions import db
from aws_portal.rbac.models import JoinAccountAppRole, JoinAccountStudy

type RBACType = Literal["study", "account"]


class _QueryClass:
    def __get__(self, instance, owner):
        raise RuntimeError("`query` cannot be used on RBAC-enabled tables. Use `cls.select` instead.")


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
    def app_roles(cls) -> Mapped[JoinAccountAppRole]:
        return db.relationship(
            "JoinAccountAppRole",
            back_populates="account",
            cascade="all, delete-orphan",
        )


class RBACStudyMixin(RBACBase):
    rbac_type: RBACType = "study"
