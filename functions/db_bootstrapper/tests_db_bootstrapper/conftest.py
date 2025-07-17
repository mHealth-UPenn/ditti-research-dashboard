import time
from collections.abc import Generator

import docker
import pytest
from docker.models.containers import Container
from flask import Flask
from src.backend.extensions import db, migrate
from src.utils import FileReader

from tests_db_bootstrapper.tests_utils.mock_file_reader import (
    create_mock_file_reader,
)

MOCK_TABLE_NAME = "mock_table"
MOCK_EMPTY_TABLE_NAME = "empty_table"
POSTGRES_PASSWORD = "password"
POSTGRES_USER = "username"
POSTGRES_DB = "db"
POSTGRES_PORT = 5433
POSTGRES_CONTAINER_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:{POSTGRES_PORT}/{POSTGRES_DB}"


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

    def __enter__(self):
        self.wait_for_container()
        return self.container

    def __exit__(self, exc_type, exc_value, traceback):
        self.container.stop()
        self.container.remove()


@pytest.fixture(scope="session")
def test_client() -> Generator[Flask, None, None]:
    with MockPostgresContainer():
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


@pytest.fixture(scope="session")
def mock_file_reader() -> FileReader:
    return create_mock_file_reader()
