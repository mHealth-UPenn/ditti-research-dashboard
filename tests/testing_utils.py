from aws_portal.extensions import db
from aws_portal.rbac.models import (
    AppPermission,
    AppRole,
    JoinAccountAppRole,
    JoinAccountStudy,
    JoinAppRolePermission,
    JoinStudyRolePermission,
    StudyPermission,
    StudyRole,
)


def give_study_permissions(permission_value: str):
    db.session.add(StudyPermission(value=permission_value))
    db.session.add(StudyRole(name="Role 1"))
    db.session.add(JoinStudyRolePermission(study_role_id=1, study_permission_id=1))
    db.session.add(JoinAccountStudy(account_id=1, study_id=1, study_role_id=1))
    db.session.commit()


def give_app_permissions(permission_value: str):
    db.session.add(AppPermission(value=permission_value))
    db.session.add(AppRole(name="Role 1"))
    db.session.add(JoinAppRolePermission(app_role_id=1, app_permission_id=1))
    db.session.add(JoinAccountAppRole(account_id=1, app_role_id=1))
    db.session.commit()
