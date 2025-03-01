from typing import Any, Literal

from sqlalchemy import and_, or_, select
from sqlalchemy.sql import Select
from sqlalchemy.orm import InstrumentedAttribute

from aws_portal.rbac.models import JoinRolePermission, JoinAccountApp, JoinAccountStudy, Permission
from aws_portal.rbac.query_class import _QueryClass

type RBACType = Literal["account", "app", "study"]


class RBACManager:
    AccountTable = None
    AppTable = None
    StudyTable = None


def with_rbac(attr: str):
    def decorator(cls):
        if not hasattr(cls, "rbac_type"):
            raise ValueError(f"{cls.__name__} must inherit from an RBAC mixin")
        if not (hasattr(cls, attr) and isinstance(getattr(cls, attr), InstrumentedAttribute)):
            raise ValueError(f"{cls.__name__} must have a {attr} column")
        if not getattr(cls, attr).unique:
            raise ValueError(f"{cls.__name__} must have a unique constraint on {attr}")
        match cls.rbac_type:
            case "account":
                RBACManager.AccountTable = cls
            case "app":
                RBACManager.AppTable = cls
            case "study":
                RBACManager.StudyTable = cls
            case _:
                raise ValueError(f"Invalid rbac_type: {cls.rbac_type}")
        setattr(cls, "rbac_name", getattr(cls, attr))
        return cls
    return decorator


def with_rbac_study_permission(permission_value: str):
    """Decorator to enforce study-level permissions on SQLAlchemy queries."""
    def decorator(cls):
        @classmethod
        def _select(cls, *entities: list[Any], **__kw: Any) -> Select[Any]:
            account_id = 1

            # If no user, return empty query
            if not account_id:
                return select(cls).where(False)

            study_ids = select(RBACManager.StudyTable.id) \
                .join(JoinAccountStudy, RBACManager.StudyTable.id == JoinAccountStudy.study_id) \
                .join(JoinRolePermission, JoinAccountStudy.role_id == JoinRolePermission.role_id) \
                .join(Permission, JoinRolePermission.permission_id == Permission.id) \
                .where(and_(
                    JoinAccountStudy.account_id == account_id,
                    or_(
                        Permission.value == permission_value,
                        Permission.value == "*",
                    )
                ))

            return select(*entities, **__kw) \
                .join(RBACManager.StudyTable, cls.study_id == RBACManager.StudyTable.id) \
                .filter(RBACManager.StudyTable.id.in_(study_ids))

        cls.select = _select
        cls.query_class = _QueryClass()
        return cls

    return decorator


def with_rbac_app_permission(permission_value: str):
    """Decorator to enforce app-level permissions on SQLAlchemy queries."""
    def decorator(cls):
        @classmethod
        def _select(cls, *entities: list[Any], **__kw: Any) -> Select[Any]:
            account_id = 1

            # If no user, return empty query
            if not account_id:
                return select(cls).where(False)

            app_ids = select(RBACManager.AppTable.id) \
                .join(JoinAccountApp, RBACManager.AppTable.id == JoinAccountApp.app_id) \
                .join(JoinRolePermission, JoinAccountApp.role_id == JoinRolePermission.role_id) \
                .join(Permission, JoinRolePermission.permission_id == Permission.id) \
                .where(and_(
                    JoinAccountApp.account_id == account_id,
                    or_(
                        Permission.value == permission_value,
                        Permission.value == "*",
                    )
                ))

            return select(*entities, **__kw) \
                .join(RBACManager.AppTable, cls.app_id == RBACManager.AppTable.id) \
                .filter(RBACManager.AppTable.id.in_(app_ids))

        cls.select = _select
        cls.query_class = _QueryClass()
        return cls

    return decorator


def with_rbac_permission(permission_value: str, rbac_type: RBACType):
    def decorator(func):
        def wrapper(*args, **kwargs):
            account_id = 1

            # If no user, return 403
            if not account_id:
                return "Forbidden", 403

            if rbac_type == "account":
                table = RBACManager.AccountTable
                join_table = JoinAccountApp
                join_column = "account_id"
            elif rbac_type == "app":
                table = RBACManager.AppTable
                join_table = JoinAccountApp
                join_column = "app_id"
            elif rbac_type == "study":
                table = RBACManager.StudyTable
                join_table = JoinAccountStudy
                join_column = "study_id"
            else:
                raise ValueError(f"Invalid rbac_type: {rbac_type}")

            query = select(table.id) \
                .join(join_table, table.id == getattr(join_table, join_column)) \
                .join(JoinRolePermission, getattr(join_table, "role_id") == JoinRolePermission.role_id) \
                .join(Permission, JoinRolePermission.permission_id == Permission.id) \
                .where(and_(
                    getattr(join_table, "account_id") == account_id,
                    or_(
                        Permission.value == permission_value,
                        Permission.value == "*",
                    )
                ))

            if not query.scalar():
                return "Forbidden", 403

            return func(*args, **kwargs)

        return wrapper

    return decorator
