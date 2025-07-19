import os
import sys
import time
from collections.abc import Generator
from typing import Any
from unittest.mock import Mock

# Add parent directories to Python path to find the shared package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "shared")
)

import docker
import pytest
from docker.models.containers import Container
from flask import Flask
from sqlalchemy import Connection, Result, TextClause
from src.backend.extensions import db, migrate
from src.utils.database_connection_executer import DbConnectionExecuter
from src.utils.database_manager import DatabaseManager

from tests_db_bootstrapper.tests_utils.mock_file_reader import load_mock_data

MOCK_TABLE_NAME = "mock_table"
MOCK_EMPTY_TABLE_NAME = "empty_table"
POSTGRES_PASSWORD = "password"
POSTGRES_USER = "username"
POSTGRES_DB = "db"
POSTGRES_PORT = 5433
POSTGRES_CONTAINER_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:{POSTGRES_PORT}/{POSTGRES_DB}"
IAM_USERNAME = "iam_username"
MOCK_FILENAME = "mock_filename.json"

DatabaseManager.MIGRATION_DIR = (
    "functions/db_bootstrapper/tests_db_bootstrapper/migrations"
)


class MockTable(db.Model):
    __tablename__ = MOCK_TABLE_NAME
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=True)


class MockEmptyTable(db.Model):
    __tablename__ = MOCK_EMPTY_TABLE_NAME
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=True)


class MockPostgresContainer:
    client: docker.DockerClient
    container: Container

    def __init__(self):
        self.client = docker.from_env()
        self.container = None
        self.container = self.client.containers.run(
            "postgres",
            ports={f"{POSTGRES_PORT}/tcp": POSTGRES_PORT},
            environment={
                "PGPORT": POSTGRES_PORT,
                "POSTGRES_USER": POSTGRES_USER,
                "POSTGRES_PASSWORD": POSTGRES_PASSWORD,
                "POSTGRES_DB": POSTGRES_DB,
            },
            detach=True,
        )

    def wait_for_container(self):
        # Wait for Postgres to be ready
        max_retries = 10
        retries = 0
        while True:
            try:
                response = self.container.exec_run(
                    [
                        "pg_isready",
                        "-U",
                        POSTGRES_USER,
                        "-d",
                        POSTGRES_DB,
                    ]
                )
                if (
                    response.exit_code == 0
                    and "accepting connections"
                    in response.output.decode("utf-8").strip()
                ):
                    break
                else:
                    retries += 1
                    if retries >= max_retries:
                        raise Exception(
                            "Failed to connect to the container"
                        ) from None
                    time.sleep(1)
            except docker.errors.NotFoundError:
                retries += 1
                if retries >= max_retries:
                    raise Exception(
                        "Failed to connect to the container"
                    ) from None
                time.sleep(1)
            except Exception as e:
                raise Exception(
                    "Failed to connect to the container due to unexpected error"
                ) from e

    def create_dummy_role(self):
        self.container.exec_run(
            [
                "psql",
                "-U",
                POSTGRES_USER,
                "-d",
                POSTGRES_DB,
                "-c",
                "CREATE ROLE rds_iam",
            ]
        )

    def __enter__(self):
        self.wait_for_container()
        self.create_dummy_role()
        return self.container

    def __exit__(self, exc_type, exc_value, traceback):
        self.container.stop()
        self.container.remove()


@pytest.fixture(scope="session")
def mock_postgres_container() -> Generator[MockPostgresContainer, None, None]:
    with MockPostgresContainer() as container:
        yield container


@pytest.fixture(scope="session")
def test_client(
    mock_postgres_container: MockPostgresContainer,
) -> Generator[Flask, None, None]:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = POSTGRES_CONTAINER_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = True

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        yield app
        # Clean up database engine connections
        db.engine.dispose()


@pytest.fixture
def with_mock_tables(test_client: Flask) -> Generator[None, None, None]:
    db.create_all()
    try:
        yield
    finally:
        db.drop_all()


@pytest.fixture
def with_mock_data(with_mock_tables: None) -> None:
    for row in load_mock_data()[MOCK_TABLE_NAME]:
        db.session.add(MockTable(**row))
    db.session.commit()


class MockResult(Result):
    def __init__(self, return_value: Any):
        self.fetchone = Mock(return_value=return_value)


class MockConnection(Connection):
    def __init__(self, *, user_exists: bool):
        self.user_exists = user_exists
        self.commit = Mock()
        self.close = Mock()
        self.call_args_list = []

    def execute(
        self, statement: TextClause, parameters=None, **kwargs
    ) -> MockResult:
        self.call_args_list.append(str((statement.text, parameters, kwargs)))
        if statement.text == DbConnectionExecuter.GET_USER_EXISTS:
            return MockResult(self.user_exists)
        if statement.text == DbConnectionExecuter.GET_CURRENT_DATABASE:
            return MockResult((POSTGRES_DB,))
        if statement.text == DbConnectionExecuter.TEST_IAM_CONNECTION:
            return MockResult((1, "test_user", POSTGRES_DB))
        return None
