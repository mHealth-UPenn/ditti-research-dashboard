from datetime import datetime
from unittest.mock import patch
import uuid

from aws_portal.extensions import db
from aws_portal.models import (
    AboutSleepTemplate,
    Account,
    Api,
    App,
    BlockedToken,
    JoinAccountApp,
    JoinStudySubjectApi,
    LambdaTask,
    SleepLevel,
    SleepLevelEnum,
    SleepLog,
    SleepLogTypeEnum,
    SleepCategoryTypeEnum,
    SleepSummary,
    Study,
    StudySubject,
)
from aws_portal.rbac.api import with_rbac_study_permission
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


class MockApps:
    app = App(name="App")


class MockAccounts:
    not_confirmed = Account(email="NotConfirmed", is_confirmed=False)
    has_no_role = Account(email="HasNoRole", is_confirmed=True)
    has_app_role = Account(email="HasAppRole", is_confirmed=True)
    has_study_role = Account(email="HasStudyRole", is_confirmed=True)
    has_both_roles = Account(email="HasBothRoles", is_confirmed=True)


class MockPermissions:
    app_get_data = AppPermission(value="AppGetData", display_label="App Get Data")
    study_get_data = StudyPermission(value="StudyGetData", display_label="Study Get Data")


class MockRoles:
    app_role = AppRole(name="AppRole")
    study_role = StudyRole(name="StudyRole")


class MockSleepLogs:
    study_1_subject_1_sleep_log_1: SleepLog
    study_1_subject_1_sleep_log_2: SleepLog
    study_1_subject_2_sleep_log_1: SleepLog
    study_1_subject_2_sleep_log_2: SleepLog
    study_2_subject_1_sleep_log_1: SleepLog
    study_2_subject_1_sleep_log_2: SleepLog
    study_2_subject_2_sleep_log_1: SleepLog
    study_2_subject_2_sleep_log_2: SleepLog


class MockStudies:
    study_1 = Study(
        name="Study1",
        acronym="S1",
        ditti_id="S1",
        email="S1",
        default_expiry_delta=30,
    )
    study_2 = Study(
        name="Study2",
        acronym="S2",
        ditti_id="S2",
        email="S2",
        default_expiry_delta=7,
    )


class MockStudySubjects:
    study_1_subject_1: StudySubject
    study_1_subject_2: StudySubject
    study_2_subject_1: StudySubject
    study_2_subject_2: StudySubject


MockAccounts.not_confirmed.password = "password"
MockAccounts.has_no_role.password = "password"
MockAccounts.has_app_role.password = "password"
MockAccounts.has_study_role.password = "password"
MockAccounts.has_both_roles.password = "password"
MockAccounts.not_confirmed.public_id = str(uuid.uuid4())
MockAccounts.has_no_role.public_id = str(uuid.uuid4())
MockAccounts.has_app_role.public_id = str(uuid.uuid4())
MockAccounts.has_study_role.public_id = str(uuid.uuid4())
MockAccounts.has_both_roles.public_id = str(uuid.uuid4())
MockAccounts.not_confirmed.created_on = datetime.now()
MockAccounts.has_no_role.created_on = datetime.now()
MockAccounts.has_app_role.created_on = datetime.now()
MockAccounts.has_study_role.created_on = datetime.now()
MockAccounts.has_both_roles.created_on = datetime.now()
MockAccounts.not_confirmed.first_name = "Not"
MockAccounts.has_no_role.first_name = "Has"
MockAccounts.has_app_role.first_name = "Has"
MockAccounts.has_study_role.first_name = "Has"
MockAccounts.has_both_roles.first_name = "Has"
MockAccounts.not_confirmed.last_name = "Confirmed"
MockAccounts.has_no_role.last_name = "NoRole"
MockAccounts.has_app_role.last_name = "AppRole"
MockAccounts.has_study_role.last_name = "StudyRole"
MockAccounts.has_both_roles.last_name = "BothRoles"


def create_unit_testing_db():
    db.create_all()

    # Create apps
    db.session.add(MockApps.app)

    # Create studies
    db.session.add(MockStudies.study_1)
    db.session.add(MockStudies.study_2)
    db.session.flush()

    # Create study subjects
    MockStudySubjects.study_1_subject_1 = StudySubject(ditti_id="S1S1", study_id=MockStudies.study_1.id)
    MockStudySubjects.study_1_subject_2 = StudySubject(ditti_id="S1S2", study_id=MockStudies.study_1.id)
    MockStudySubjects.study_2_subject_1 = StudySubject(ditti_id="S2S1", study_id=MockStudies.study_2.id)
    MockStudySubjects.study_2_subject_2 = StudySubject(ditti_id="S2S2", study_id=MockStudies.study_2.id)
    db.session.add(MockStudySubjects.study_1_subject_1)
    db.session.add(MockStudySubjects.study_1_subject_2)
    db.session.add(MockStudySubjects.study_2_subject_1)
    db.session.add(MockStudySubjects.study_2_subject_2)
    db.session.flush()

    # Create sleep logs
    MockSleepLogs.study_1_subject_1_sleep_log_1 = SleepLog(
        study_subject_id=MockStudySubjects.study_1_subject_1.id,
        log_id=1,
        date_of_sleep=datetime.now().date(),
        log_type=SleepLogTypeEnum.auto_detected,
        type=SleepCategoryTypeEnum.stages
    )
    MockSleepLogs.study_1_subject_1_sleep_log_2 = SleepLog(
        study_subject_id=MockStudySubjects.study_1_subject_1.id,
        log_id=2,
        date_of_sleep=datetime.now().date(),
        log_type=SleepLogTypeEnum.auto_detected,
        type=SleepCategoryTypeEnum.stages
    )
    MockSleepLogs.study_1_subject_2_sleep_log_1 = SleepLog(
        study_subject_id=MockStudySubjects.study_1_subject_2.id,
        log_id=3,
        date_of_sleep=datetime.now().date(),
        log_type=SleepLogTypeEnum.auto_detected,
        type=SleepCategoryTypeEnum.stages
    )
    MockSleepLogs.study_1_subject_2_sleep_log_2 = SleepLog(
        study_subject_id=MockStudySubjects.study_1_subject_2.id,
        log_id=4,
        date_of_sleep=datetime.now().date(),
        log_type=SleepLogTypeEnum.auto_detected,
        type=SleepCategoryTypeEnum.stages
    )
    MockSleepLogs.study_2_subject_1_sleep_log_1 = SleepLog(
        study_subject_id=MockStudySubjects.study_2_subject_1.id,
        log_id=5,
        date_of_sleep=datetime.now().date(),
        log_type=SleepLogTypeEnum.auto_detected,
        type=SleepCategoryTypeEnum.stages
    )
    MockSleepLogs.study_2_subject_1_sleep_log_2 = SleepLog(
        study_subject_id=MockStudySubjects.study_2_subject_1.id,
        log_id=6,
        date_of_sleep=datetime.now().date(),
        log_type=SleepLogTypeEnum.auto_detected,
        type=SleepCategoryTypeEnum.stages
    )
    MockSleepLogs.study_2_subject_2_sleep_log_1 = SleepLog(
        study_subject_id=MockStudySubjects.study_2_subject_2.id,
        log_id=7,
        date_of_sleep=datetime.now().date(),
        log_type=SleepLogTypeEnum.auto_detected,
        type=SleepCategoryTypeEnum.stages
    )
    MockSleepLogs.study_2_subject_2_sleep_log_2 = SleepLog(
        study_subject_id=MockStudySubjects.study_2_subject_2.id,
        log_id=8,
        date_of_sleep=datetime.now().date(),
        log_type=SleepLogTypeEnum.auto_detected,
        type=SleepCategoryTypeEnum.stages
    )
    db.session.add(MockSleepLogs.study_1_subject_1_sleep_log_1)
    db.session.add(MockSleepLogs.study_1_subject_1_sleep_log_2)
    db.session.add(MockSleepLogs.study_1_subject_2_sleep_log_1)
    db.session.add(MockSleepLogs.study_1_subject_2_sleep_log_2)
    db.session.add(MockSleepLogs.study_2_subject_1_sleep_log_1)
    db.session.add(MockSleepLogs.study_2_subject_1_sleep_log_2)
    db.session.add(MockSleepLogs.study_2_subject_2_sleep_log_1)
    db.session.add(MockSleepLogs.study_2_subject_2_sleep_log_2)
    db.session.flush()

    # Create permissions
    db.session.add(MockPermissions.app_get_data)
    db.session.add(MockPermissions.study_get_data)

    # Create roles
    db.session.add(MockRoles.app_role)
    db.session.add(MockRoles.study_role)
    db.session.flush()

    db.session.add(JoinAppRolePermission(app_role_id=MockRoles.app_role.id, app_permission_id=MockPermissions.app_get_data.id))
    db.session.add(JoinStudyRolePermission(study_role_id=MockRoles.study_role.id, study_permission_id=MockPermissions.study_get_data.id))

    # Create accounts
    db.session.add(MockAccounts.not_confirmed)
    db.session.add(MockAccounts.has_no_role)
    db.session.add(MockAccounts.has_app_role)
    db.session.add(MockAccounts.has_study_role)
    db.session.add(MockAccounts.has_both_roles)
    db.session.flush()

    db.session.add(JoinAccountAppRole(account_id=MockAccounts.has_app_role.id, app_role_id=MockRoles.app_role.id))
    db.session.add(JoinAccountStudy(account_id=MockAccounts.has_study_role.id, study_id=MockStudies.study_1.id, study_role_id=MockRoles.study_role.id))
    db.session.add(JoinAccountAppRole(account_id=MockAccounts.has_both_roles.id, app_role_id=MockRoles.app_role.id))
    db.session.add(JoinAccountStudy(account_id=MockAccounts.has_both_roles.id, study_id=MockStudies.study_1.id, study_role_id=MockRoles.study_role.id))
    db.session.commit()


def patch_account(account: Account):
    return patch("aws_portal.rbac.api.current_user", account)
