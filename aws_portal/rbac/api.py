from typing import Any, Literal

from flask_jwt_extended.utils import current_user
from sqlalchemy import and_, or_, select
from sqlalchemy.sql import Select
from sqlalchemy.orm import InstrumentedAttribute

from aws_portal.extensions import db
from aws_portal.rbac.models import (
    AppPermission,
    AppRole,
    JoinAccountAppRole,
    JoinAccountStudy,
    JoinAppRolePermission,
    JoinStudyRolePermission,
    StudyPermission,
)
from aws_portal.rbac.mixins import _QueryClass

type RBACType = Literal["account", "study"]


class RBACManager:
    AccountTable = None
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
            if not current_user:
                return select(cls).where(False)

            study_ids = select(RBACManager.StudyTable.id) \
                .join(JoinAccountStudy, RBACManager.StudyTable.id == JoinAccountStudy.study_id) \
                .join(JoinStudyRolePermission, JoinAccountStudy.study_role_id == JoinStudyRolePermission.study_role_id) \
                .join(StudyPermission, JoinStudyRolePermission.study_permission_id == StudyPermission.id) \
                .where(and_(
                    JoinAccountStudy.account_id == current_user.id,
                    or_(
                        StudyPermission.value == permission_value,
                        StudyPermission.value == "*",
                    )
                ))

            return select(*entities, **__kw) \
                .join(RBACManager.StudyTable, cls.study_id == RBACManager.StudyTable.id) \
                .filter(RBACManager.StudyTable.id.in_(study_ids))

        cls.select = _select
        cls.query_class = _QueryClass()
        return cls

    return decorator


def rbac_required(permission_value: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not current_user:
                return "Forbidden", 403

            query = select(AppPermission.id) \
                .join(JoinAppRolePermission, AppPermission.id == JoinAppRolePermission.app_permission_id) \
                .join(AppRole, JoinAppRolePermission.app_role_id == AppRole.id) \
                .join(JoinAccountAppRole, AppRole.id == JoinAccountAppRole.app_role_id) \
                .where(and_(
                    JoinAccountAppRole.account_id == current_user.id,
                    or_(
                        AppPermission.value == permission_value,
                        AppPermission.value == "*",
                    )
                ))
            
            # Debug queries
            # print("================================")
            # query = select(AppPermission.id)
            # print(db.session.execute(query).scalars().all())
            # print("================================")
            # query = select(AppPermission.id) \
            #     .join(JoinAppRolePermission, AppPermission.id == JoinAppRolePermission.app_permission_id)
            # print(db.session.execute(query).scalars().all())
            # print("================================")
            # query = select(AppPermission.id) \
            #     .join(JoinAppRolePermission, AppPermission.id == JoinAppRolePermission.app_permission_id) \
            #     .join(AppRole, JoinAppRolePermission.app_role == AppRole.id)
            # print(db.session.execute(query).scalars().all())
            # print("================================")
            # query = select(AppPermission.id) \
            #     .join(JoinAppRolePermission, AppPermission.id == JoinAppRolePermission.app_permission_id) \
            #     .join(AppRole, JoinAppRolePermission.app_role == AppRole.id) \
            #     .join(JoinAccountAppRole, AppRole.id == JoinAccountAppRole.app_role_id)
            # print(db.session.execute(query).scalars().all())
            # print("================================")
            # query = select(AppPermission.id) \
            #     .join(JoinAppRolePermission, AppPermission.id == JoinAppRolePermission.app_permission_id) \
            #     .join(AppRole, JoinAppRolePermission.app_role == AppRole.id) \
            #     .join(JoinAccountAppRole, AppRole.id == JoinAccountAppRole.app_role_id) \
            #     .where(JoinAccountAppRole.account_id == current_user.id)
            # print(db.session.execute(query).scalars().all())
            # print("================================")
            # query = select(AppPermission.id) \
            #     .join(JoinAppRolePermission, AppPermission.id == JoinAppRolePermission.app_permission_id) \
            #     .join(AppRole, JoinAppRolePermission.app_role == AppRole.id) \
            #     .join(JoinAccountAppRole, AppRole.id == JoinAccountAppRole.app_role_id) \
            #     .where(and_(
            #         JoinAccountAppRole.account_id == current_user.id,
            #         or_(
            #             AppPermission.value == permission_value,
            #             AppPermission.value == "*",
            #         )
            #     ))
            # print(db.session.execute(query).scalars().all())

            if not db.session.execute(query).scalars().all():
                return "Forbidden", 403

            return func(*args, **kwargs)

        return wrapper

    return decorator
