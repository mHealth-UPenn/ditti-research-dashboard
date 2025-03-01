import pytest
from sqlalchemy.orm import InstrumentedAttribute
from aws_portal.rbac.api import with_rbac, RBACManager
from aws_portal.rbac.models import RBACAccountMixin, RBACAppMixin, RBACStudyMixin, Role
from sqlalchemy import Column, String, Integer, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from unittest.mock import patch
from aws_portal.rbac.api import with_rbac_study_permission
from aws_portal.rbac.models import JoinAccountStudy, JoinRolePermission, Permission
from sqlalchemy import select
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask.testing import FlaskClient
from aws_portal.extensions import db


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


@with_rbac("email")
class Account(db.Model, RBACAccountMixin):
    __tablename__ = "account"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    rbac_type = "account"


@with_rbac("name")
class App(db.Model, RBACAppMixin):
    __tablename__ = "app"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    rbac_type = "app"


@with_rbac("acronym")
class Study(db.Model, RBACStudyMixin):
    __tablename__ = "study"
    id = Column(Integer, primary_key=True)
    acronym = Column(String, unique=True)
    rbac_type = "study"


class StudyData(db.Model):
    __tablename__ = "study_data"
    id = Column(Integer, primary_key=True)
    study_id = Column(Integer)
    rbac_type = "study"


@with_rbac_study_permission("GetData")
class StudyDataWithPermission(StudyData):
    pass


def test_with_rbac_account():
    assert hasattr(Account, "rbac_name")
    assert Account.rbac_name == Account.email
    assert RBACManager.AccountTable == Account


def test_with_rbac_app():
    assert hasattr(App, "rbac_name")
    assert App.rbac_name == App.name
    assert RBACManager.AppTable == App


def test_with_rbac_study():
    assert hasattr(Study, "rbac_name")
    assert Study.rbac_name == Study.acronym
    assert RBACManager.StudyTable == Study


def test_with_rbac_study_permission_no_user(test_client: FlaskClient):
    with patch("aws_portal.rbac.api.current_user", None):
        query = StudyDataWithPermission.select()
        assert db.session.execute(query).scalars().all() == []


def test_with_rbac_study_permission_no_study_access(test_client: FlaskClient):
    with patch("aws_portal.rbac.api.current_user", type("User", (object,), {"id": 1})):
        query = StudyDataWithPermission.select(StudyDataWithPermission.id)
        assert db.session.execute(query).scalars().all() == []


def test_with_rbac_study_permission_with_access(test_client: FlaskClient):
    db.session.add(Permission(value="GetData"))
    db.session.add(Role(name="Role 1"))
    db.session.add(JoinRolePermission(role_id=1, permission_id=1))
    db.session.add(JoinAccountStudy(account_id=1, study_id=1, role_id=1))
    db.session.commit()

    with patch("aws_portal.rbac.api.current_user", type("User", (object,), {"id": 1})):
        query = StudyDataWithPermission.select(StudyDataWithPermission.id)
        assert str(db.session.execute(query).scalars().all()) == str(db.session.execute(select(StudyDataWithPermission.id)).scalars().all())
