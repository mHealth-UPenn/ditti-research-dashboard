import pytest

from flask.testing import FlaskClient
from sqlalchemy import Column, String, Integer, select

from aws_portal.extensions import db
from aws_portal.models import SleepLog, Study
from aws_portal.rbac.api import (
    RBACManager,
    rbac_required,
    with_rbac,
)
from aws_portal.rbac.mixins import RBACAccountMixin
from tests.testing_utils import MockAccounts, MockSleepLogs, patch_account


#################################
# Tests for with_rbac decorator #
#################################
# def test_with_rbac_no_rbac_type():
#     class Invalid(db.Model):
#         __tablename__ = "invalid"
#         id = Column(Integer, primary_key=True)
#         name = Column(String)

#     with pytest.raises(ValueError, match="Invalid must inherit from an RBAC mixin"):
#         with_rbac("name")(Invalid)


# def test_with_rbac_no_column():
#     class NoColumn(db.Model, RBACAccountMixin):
#         __tablename__ = "no_column"
#         id = Column(Integer, primary_key=True)
#         rbac_type = "account"

#     with pytest.raises(ValueError, match="NoColumn must have a email column"):
#         with_rbac("email")(NoColumn)


# def test_with_rbac_no_unique_constraint():
#     class NoUnique(db.Model, RBACAccountMixin):
#         __tablename__ = "no_unique"
#         id = Column(Integer, primary_key=True)
#         email = Column(String)
#         rbac_type = "account"

#     with pytest.raises(ValueError, match="NoUnique must have a unique constraint on email"):
#         with_rbac("email")(NoUnique)


def test_with_rbac():
    assert hasattr(Study, "rbac_name")
    assert Study.rbac_name == Study.acronym
    assert RBACManager.StudyTable == Study


########################################
# Tests for with_rbac_study_permission #
########################################
def test_with_rbac_study_permission_no_user(client: FlaskClient):
    query = SleepLog.select()
    assert db.session.execute(query).scalars().all() == []


@patch_account(MockAccounts.has_app_role)
def test_with_rbac_study_permission_no_study_access(client: FlaskClient):
    query = SleepLog.select(SleepLog.id)
    assert db.session.execute(query).scalars().all() == []


@patch_account(MockAccounts.has_study_role)
def test_with_rbac_study_permission_with_access(client: FlaskClient):
    query = SleepLog.select(SleepLog.id)
    assert str(db.session.execute(query).scalars().all()) == str(db.session.execute(select(SleepLog.id)).scalars().all())


###########################
# Tests for rbac_required #
###########################
@rbac_required("AppGetData")
def get_data():
    return "Success", 200


def test_rbac_required_no_user(client: FlaskClient):
    response = get_data()
    assert response == ("Forbidden", 403)


@patch_account(MockAccounts.has_no_role)
def test_rbac_required_no_access(client: FlaskClient):
    response = get_data()
    assert response == ("Forbidden", 403)


@patch_account(MockAccounts.has_app_role)
def test_rbac_required_with_access(client: FlaskClient):
    response = get_data()
    assert response == ("Success", 200)
