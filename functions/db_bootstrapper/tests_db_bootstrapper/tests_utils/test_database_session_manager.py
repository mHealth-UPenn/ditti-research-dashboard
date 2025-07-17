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
from src.utils import DatabaseSessionManager


class TestDatabaseSessionManager:
    """Test the DatabaseSessionManager class."""

    def test_get_session_creates_new_session(self, test_client: Flask):
        """Test that get_session creates a new session when none exists."""
        manager = DatabaseSessionManager(test_client)

        session = manager.get_session()

        assert session is not None
        assert manager._session is session

    def test_get_session_returns_existing_session(self, test_client: Flask):
        """Test that get_session returns existing session."""
        manager = DatabaseSessionManager(test_client)
        first_session = manager.get_session()

        second_session = manager.get_session()

        assert second_session is first_session

    def test_close_session(self, test_client: Flask):
        """Test that close_session properly closes the session."""
        manager = DatabaseSessionManager(test_client)
        session = manager.get_session()
        assert manager._session is session

        manager.close_session()

        assert manager._session is None
