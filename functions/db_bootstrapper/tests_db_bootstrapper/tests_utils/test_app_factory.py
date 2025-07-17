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


from src.backend.extensions import db, migrate
from src.utils import AppFactory, DbUri


class TestAppFactory:
    """Test the AppFactory class."""

    def test_create_app(self):
        """Test Flask app creation."""
        db_uri = DbUri(
            username="user",
            password="pass",
            hostname="host",
            port="5432",
            database="db",
        )

        app = AppFactory.create_app(db_uri, use_iam=True)

        with app.app_context():
            assert app.config["SQLALCHEMY_DATABASE_URI"] == db_uri.uri
            assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False
            assert db.engine is not None
            assert migrate.db.engine is not None
