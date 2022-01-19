import pytest
from aws_portal.app import create_app
from aws_portal.models import (
    init_admin_account, init_admin_app, init_admin_group, init_db
)


@pytest.fixture
def app():
    app = create_app(testing=True)
    with app.app_context():
        init_db()
        init_admin_app()
        init_admin_group()
        init_admin_account()
        yield app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


def test_apps():
    raise Exception


def test_studies():
    raise Exception


def test_study_details():
    raise Exception


def test_study_contacts():
    raise Exception


def test_account_details():
    raise Exception
