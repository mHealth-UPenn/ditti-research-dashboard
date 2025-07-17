from collections.abc import Generator

import pytest
from flask import Flask
from src.backend.extensions import db, migrate
from src.utils import FileReader

from tests_db_bootstrapper.tests_utils.mock_file_reader import (
    create_mock_file_reader,
)


class MockTable(db.Model):
    __tablename__ = "mock_table"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=True)


@pytest.fixture
def test_client() -> Generator[Flask, None, None]:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = True

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        yield app


@pytest.fixture
def mock_file_reader() -> FileReader:
    return create_mock_file_reader()
