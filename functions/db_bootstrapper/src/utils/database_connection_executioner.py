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


from sqlalchemy import Connection, text


class DbConnectionExecutioner:
    GET_USER_EXISTS = "SELECT 1 FROM pg_roles WHERE rolname = :iam_username"
    GET_CURRENT_DATABASE = "SELECT current_database()"
    CREATE_USER = "CREATE USER {iam_username} WITH LOGIN"
    GRANT_IAM_TO_USER = "GRANT rds_iam TO {iam_username}"
    GRANT_CONNECT_TO_DATABASE = (
        "GRANT CONNECT ON DATABASE {database} TO {iam_username}"
    )
    GRANT_USAGE_TO_SCHEMA = "GRANT USAGE ON SCHEMA public TO {iam_username}"
    GRANT_ALL_PRIVILEGES_TO_TABLES = (
        "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {iam_username}"
    )
    GRANT_ALL_PRIVILEGES_TO_SEQUENCES = (
        "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {iam_username}"
    )
    ALTER_DEFAULT_PRIVILEGES_TO_TABLES = "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {iam_username}"
    TEST_IAM_CONNECTION = (
        "SELECT 1 as test, current_user as user, current_database() as db"
    )

    def __init__(self, connection: Connection):
        self.connection = connection

    def get_user_exists(self, iam_username: str) -> str:
        return self.connection.execute(
            text(self.GET_USER_EXISTS),
            {"iam_username": iam_username},
        )

    def get_current_database(self) -> str:
        return self.connection.execute(
            text(self.GET_CURRENT_DATABASE)
        ).fetchone()[0]

    def create_user(self, iam_username: str) -> str:
        return self.connection.execute(
            text(self.CREATE_USER),
            {"iam_username": iam_username},
        )

    def grant_iam_to_user(self, iam_username: str) -> str:
        return self.connection.execute(
            text(self.GRANT_IAM_TO_USER),
            {"iam_username": iam_username},
        )

    def grant_connect_to_database(self, database: str, iam_username: str) -> str:
        return self.connection.execute(
            text(self.GRANT_CONNECT_TO_DATABASE),
            {"database": database, "iam_username": iam_username},
        )

    def grant_usage_to_schema(self, iam_username: str) -> str:
        return self.connection.execute(
            text(self.GRANT_USAGE_TO_SCHEMA),
            {"iam_username": iam_username},
        )

    def grant_all_privileges_to_tables(self, iam_username: str) -> str:
        return self.connection.execute(
            text(self.GRANT_ALL_PRIVILEGES_TO_TABLES),
            {"iam_username": iam_username},
        )

    def grant_all_privileges_to_sequences(self, iam_username: str) -> str:
        return self.connection.execute(
            text(self.GRANT_ALL_PRIVILEGES_TO_SEQUENCES),
            {"iam_username": iam_username},
        )

    def alter_default_privileges_to_tables(self, iam_username: str) -> str:
        return self.connection.execute(
            text(self.ALTER_DEFAULT_PRIVILEGES_TO_TABLES),
            {"iam_username": iam_username},
        )

    def test_iam_connection(self) -> str:
        return self.connection.execute(text(self.TEST_IAM_CONNECTION)).fetchone()
