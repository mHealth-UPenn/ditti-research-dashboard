# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may]
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock
from urllib.parse import urlparse

import pytest
from flask import Flask
from sqlalchemy import Dialect, event, text
from sqlalchemy.pool import ConnectionPoolEntry

from shared.iam_sqlalchemy import IamSqlAlchemy


@pytest.fixture
def mock_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("FLASK_DB")
    return app


@pytest.fixture
def mock_db():
    db = IamSqlAlchemy()
    db.client.generate_db_auth_token = MagicMock()
    return db


@pytest.fixture
def db_uri_params():
    uri = os.getenv("FLASK_DB")
    parsed = urlparse(uri)
    return {
        "hostname": parsed.hostname,
        "port": parsed.port,
        "database": parsed.path.lstrip("/"),
        "username": parsed.username,
        "password": parsed.password,
    }


def set_connection_test(app: Flask, db: IamSqlAlchemy, test_func: Callable):
    with app.app_context():

        @event.listens_for(db.engine, "do_connect")
        def test_do_connect(
            dialect: Dialect,
            conn_rec: ConnectionPoolEntry,
            cargs: tuple[Any, ...],
            cparams: dict[str, Any],
        ):
            test_func(cparams)


class TestIamSqlAlchemy:
    """Test cases for the IamSqlAlchemy class."""

    def test_init_app_without_iam(
        self,
        mock_app: Flask,
        mock_db: IamSqlAlchemy,
        db_uri_params: dict[str, Any],
    ):
        """Test init_app when use_iam is False."""
        mock_db.init_app(mock_app, use_iam=False)

        def test_func(cparams: dict[str, Any]):
            assert cparams.get("sslmode") is None
            assert cparams["password"] == db_uri_params["password"]

        set_connection_test(mock_app, mock_db, test_func)

        with mock_app.app_context():
            mock_db.session.execute(text("SELECT 1"))

        mock_db.client.generate_db_auth_token.assert_not_called()

    def test_init_app_with_iam(
        self,
        mock_app: Flask,
        mock_db: IamSqlAlchemy,
        db_uri_params: dict[str, Any],
    ):
        """Test init_app when use_iam is True."""
        mock_db.init_app(mock_app, use_iam=True)

        def test_func(cparams: dict[str, Any]):
            assert cparams["sslmode"] == "require"
            assert cparams["password"] != db_uri_params["password"]
            # Reset auth to avoid an authentication error
            del cparams["sslmode"]
            cparams["password"] = db_uri_params["password"]

        set_connection_test(mock_app, mock_db, test_func)

        with mock_app.app_context():
            mock_db.session.execute(text("SELECT 1"))

        mock_db.client.generate_db_auth_token.assert_called_once_with(
            DBHostname=db_uri_params["hostname"],
            Port=db_uri_params["port"],
            DBUsername=db_uri_params["username"],
        )

    def test_init_app_with_custom_ssl_mode(
        self,
        mock_app: Flask,
        mock_db: IamSqlAlchemy,
        db_uri_params: dict[str, Any],
    ):
        """Test init_app with custom SSL mode."""
        mock_db.init_app(mock_app, use_iam=True, iam_sslmode="prefer")

        def test_func(cparams: dict[str, Any]):
            assert cparams["sslmode"] == "prefer"
            # Reset auth to avoid an authentication error
            del cparams["sslmode"]
            cparams["password"] = db_uri_params["password"]

        set_connection_test(mock_app, mock_db, test_func)

        with mock_app.app_context():
            mock_db.session.execute(text("SELECT 1"))

    def test_create_auth_token_exception_propagation(
        self,
        mock_app: Flask,
        mock_db: IamSqlAlchemy,
        db_uri_params: dict[str, Any],
    ):
        """Test that exceptions from boto3 are properly propagated."""
        mock_db.init_app(mock_app, use_iam=True)

        # Create a mock RDS client that raises an exception
        mock_db.client.generate_db_auth_token.side_effect = Exception("AWS Error")

        with pytest.raises(Exception, match="AWS Error"), mock_app.app_context():
            mock_db.session.execute(text("SELECT 1"))

    def test_init_app_with_additional_kwargs(
        self, mock_app: Flask, db_uri_params: dict[str, Any]
    ):
        """Test that additional kwargs are passed to the parent init_app method."""
        db = IamSqlAlchemy(
            engine_options={"connect_args": {"dbname": "test-dbname"}}
        )
        db.init_app(mock_app)

        def test_func(cparams: dict[str, Any]):
            assert cparams["dbname"] == "test-dbname"
            # Reset auth to avoid an authentication error
            cparams["dbname"] = db_uri_params["database"]

        set_connection_test(mock_app, db, test_func)

        with mock_app.app_context():
            db.session.execute(text("SELECT 1"))
