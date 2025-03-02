import pytest
from unittest.mock import patch

from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import Column, String, Integer, UniqueConstraint, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import InstrumentedAttribute

from aws_portal.extensions import db
from aws_portal.rbac.api import (
    RBACManager,
    rbac_required,
    with_rbac,
    with_rbac_study_permission,
)
from aws_portal.rbac.mixins import RBACAccountMixin,  RBACStudyMixin
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


@pytest.fixture(scope="module")
def test_client():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = True
    db.init_app(app)

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


#################################
# Tests for with_rbac decorator #
#################################
def test_with_rbac_no_rbac_type():
    class Invalid(db.Model):
        __tablename__ = "invalid"
        id = Column(Integer, primary_key=True)
        name = Column(String)

    with pytest.raises(ValueError, match="Invalid must inherit from an RBAC mixin"):
        with_rbac("name")(Invalid)


def test_with_rbac_no_column():
    class NoColumn(db.Model, RBACAccountMixin):
        __tablename__ = "no_column"
        id = Column(Integer, primary_key=True)
        rbac_type = "account"

    with pytest.raises(ValueError, match="NoColumn must have a email column"):
        with_rbac("email")(NoColumn)


def test_with_rbac_no_unique_constraint():
    class NoUnique(db.Model, RBACAccountMixin):
        __tablename__ = "no_unique"
        id = Column(Integer, primary_key=True)
        email = Column(String)
        rbac_type = "account"

    with pytest.raises(ValueError, match="NoUnique must have a unique constraint on email"):
        with_rbac("email")(NoUnique)


class Account(db.Model, RBACAccountMixin):
    __tablename__ = "account"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)


@with_rbac("acronym")
class Study(db.Model, RBACStudyMixin):
    __tablename__ = "study"
    id = Column(Integer, primary_key=True)
    acronym = Column(String, unique=True)


def test_with_rbac():
    assert hasattr(Study, "rbac_name")
    assert Study.rbac_name == Study.acronym
    assert RBACManager.StudyTable == Study


########################################
# Tests for with_rbac_study_permission #
########################################
class StudyData(db.Model):
    __tablename__ = "study_data"
    id = Column(Integer, primary_key=True)
    study_id = Column(Integer)


@with_rbac_study_permission("GetData")
class StudyDataWithPermission(StudyData):
    pass


def test_with_rbac_study_permission_no_user(test_client: FlaskClient):
    with patch("aws_portal.rbac.api.current_user", None):
        query = StudyDataWithPermission.select()
        assert db.session.execute(query).scalars().all() == []


def test_with_rbac_study_permission_no_study_access(test_client: FlaskClient):
    with patch("aws_portal.rbac.api.current_user", type("User", (object,), {"id": 1})):
        query = StudyDataWithPermission.select(StudyDataWithPermission.id)
        assert db.session.execute(query).scalars().all() == []


def test_with_rbac_study_permission_with_access(test_client: FlaskClient):
    db.session.add(StudyPermission(value="GetData"))
    db.session.add(StudyRole(name="Role 1"))
    db.session.add(JoinStudyRolePermission(study_role_id=1, study_permission_id=1))
    db.session.add(JoinAccountStudy(account_id=1, study_id=1, study_role_id=1))
    db.session.commit()

    with patch("aws_portal.rbac.api.current_user", type("User", (object,), {"id": 1})):
        query = StudyDataWithPermission.select(StudyDataWithPermission.id)
        assert str(db.session.execute(query).scalars().all()) == str(db.session.execute(select(StudyDataWithPermission.id)).scalars().all())


###########################
# Tests for rbac_required #
###########################
@rbac_required("GetData")
def get_data():
    return "Success", 200


def test_rbac_required_no_user(test_client: FlaskClient):
    with patch("aws_portal.rbac.api.current_user", None):
        response = get_data()
        assert response == ("Forbidden", 403)


def test_rbac_required_no_access(test_client: FlaskClient):
    with patch("aws_portal.rbac.api.current_user", type("User", (object,), {"id": 1})):
        response = get_data()
        assert response == ("Forbidden", 403)


def test_rbac_required_with_access(test_client: FlaskClient):
    db.session.add(AppPermission(value="GetData"))
    db.session.add(AppRole(name="Role 1"))
    db.session.add(JoinAppRolePermission(app_role_id=1, app_permission_id=1))
    db.session.add(JoinAccountAppRole(account_id=1, app_role_id=1))
    db.session.commit()

    with patch("aws_portal.rbac.api.current_user", type("User", (object,), {"id": 1})):
        response = get_data()
        assert response == ("Success", 200)
