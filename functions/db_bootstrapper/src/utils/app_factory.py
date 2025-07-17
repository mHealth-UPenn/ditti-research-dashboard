# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


from flask import Flask

from src.backend.extensions import db, migrate
from src.utils.db_uri import DbUri


class AppFactory:
    """Factory for creating Flask applications."""

    @staticmethod
    def create_app(db_uri: DbUri, use_iam: bool = False) -> Flask:
        """
        Create a Flask application with database configuration.

        Args:
            db_uri: Database URI configuration.
            use_iam: Whether to use IAM authentication.

        Returns
        -------
            Configured Flask application.
        """
        app = Flask(__name__)
        app.config["SQLALCHEMY_DATABASE_URI"] = db_uri.uri
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        db.init_app(app, use_iam=use_iam)
        migrate.init_app(app, db)

        return app
