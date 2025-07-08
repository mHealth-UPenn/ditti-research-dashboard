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

from typing import Any

import boto3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Dialect, event
from sqlalchemy.pool import ConnectionPoolEntry


class IamSqlAlchemy(SQLAlchemy):
    def init_app(
        self,
        app: Flask,
        use_iam: bool = False,
        iam_sslmode: str = "require",
        **kwargs,
    ):
        """
        Initialize the SQLAlchemy extension.

        This extends the SQLAlchemy extension to use IAM authentication when
        use_iam is True.

        Args
        ----
            app: The Flask application instance.
            use_iam: Whether to use IAM authentication.
            sslmode: The SSL mode to use.
            **kwargs: Additional keyword arguments to pass to the SQLAlchemy
                extension.

        Example Usage
        -------------
        >>> from flask import Flask
        >>> from shared.iam_sqlalchemy import IamSqlAlchemy

        >>> app = Flask(__name__)
        >>> db = IamSqlAlchemy()
        >>> db.init_app(app, use_iam=True)
        """
        super().init_app(app, **kwargs)
        self.client = boto3.client("rds")

        with app.app_context():

            @event.listens_for(self.engine, "do_connect")
            def provide_token(
                dialect: Dialect,  # noqa: ARG001
                conn_rec: ConnectionPoolEntry,  # noqa: ARG001
                cargs: tuple[Any, ...],  # noqa: ARG001
                cparams: dict[str, Any],
            ):
                if use_iam:
                    cparams["sslmode"] = iam_sslmode
                    cparams["password"] = self.create_auth_token(
                        hostname=cparams["host"],
                        port=cparams["port"],
                        username=cparams["user"],
                    )

    def create_auth_token(
        self, *, hostname: str, port: int, username: str
    ) -> str:
        """Create an IAM authentication token for the given database URI and username."""
        try:
            auth_token = self.client.generate_db_auth_token(
                DBHostname=hostname,
                Port=port,
                DBUsername=username,
            )
        except Exception:
            raise

        return auth_token
