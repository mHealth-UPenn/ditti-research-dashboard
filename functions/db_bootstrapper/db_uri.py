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

from urllib.parse import quote_plus


class DbUri:
    """A database URI.

    This class is used to store the database URI and the username and password
    and enable simplified access to URI components.

    Args
    ----
        hostname: The hostname of the database.
        port: The port of the database.
        database: The name of the database.
        username: The username to use to connect to the database.
        password: The password to use to connect to the database.
    """

    def __init__(
        self,
        *,
        hostname: str,
        port: str,
        database: str,
        username: str,
        password: str | None = None,
    ):
        if password is None:
            self.uri = f"postgresql://{username}@{hostname}:{port}/{database}"
        else:
            # URL-encode the password to handle special characters like @, :, etc.
            encoded_password = quote_plus(password)
            self.uri = f"postgresql://{username}:{encoded_password}@{hostname}:{port}/{database}"
        self.has_password = password is not None
        self.hostname = hostname
        self.port = int(port)
        self.database = database
        self.username = username

    def __str__(self):
        if not self.has_password:
            return self.uri
        return f"postgresql://{self.username}:***@{self.hostname}:{self.port}/{self.database}"
