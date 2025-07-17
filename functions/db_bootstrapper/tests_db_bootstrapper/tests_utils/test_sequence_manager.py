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

from collections.abc import Generator
from unittest.mock import Mock

import pytest
from flask import Flask
from sqlalchemy.orm import Session
from src.backend.extensions import db
from src.utils import DatabaseSessionManager, SequenceManager

from tests_db_bootstrapper.conftest import (
    MOCK_EMPTY_TABLE_NAME,
    MOCK_TABLE_NAME,
    MockTable,
)
from tests_db_bootstrapper.tests_utils.mock_file_reader import load_mock_data


@pytest.fixture
def with_mock_data(test_client: Flask) -> Generator[None, None, None]:
    db.create_all()

    for row in load_mock_data()[MOCK_TABLE_NAME]:
        db.session.add(MockTable(**row))
    db.session.commit()

    try:
        yield
    finally:
        db.drop_all()


@pytest.fixture
def mock_session(test_client: Flask) -> Generator[Session, None, None]:
    session_manager = DatabaseSessionManager(test_client)
    session = session_manager.get_session()

    try:
        yield session
    finally:
        session_manager.close_session()


class TestSequenceManager:
    """Test the SequenceManager class."""

    def test_get_tables_with_id_columns(
        self, with_mock_data: None, mock_session: Session
    ):
        """Test getting tables with ID columns."""
        manager = SequenceManager(mock_session)

        result = manager.get_tables_with_id_columns()

        assert set(result) == {MOCK_TABLE_NAME, MOCK_EMPTY_TABLE_NAME}

    def test_get_max_id_for_table_with_data(
        self, with_mock_data: None, mock_session: Session
    ):
        """Test getting max ID when table has data."""
        manager = SequenceManager(mock_session)

        result = manager.get_max_id_for_table(MOCK_TABLE_NAME)

        mock_data = load_mock_data()
        expected = max(row["id"] for row in mock_data[MOCK_TABLE_NAME])
        assert result == expected

    def test_get_max_id_for_table_empty(
        self, with_mock_data: None, mock_session: Session
    ):
        """Test getting max ID when table is empty."""
        manager = SequenceManager(mock_session)

        result = manager.get_max_id_for_table(MOCK_EMPTY_TABLE_NAME)

        assert result == 0

    def test_sequence_exists_true(
        self, with_mock_data: None, mock_session: Session
    ):
        """Test sequence_exists returns True when sequence exists."""
        manager = SequenceManager(mock_session)

        result = manager.sequence_exists(f"{MOCK_TABLE_NAME}_id_seq")

        assert result is True

    def test_sequence_exists_false(
        self, with_mock_data: None, mock_session: Session
    ):
        """Test sequence_exists returns False when sequence doesn't exist."""
        manager = SequenceManager(mock_session)

        result = manager.sequence_exists("no_such_sequence")

        assert result is False

    def test_reset_sequence(self, mock_session: Session):
        """Test reset_sequence executes the correct SQL."""
        manager = SequenceManager(mock_session)
        mock_session.execute = Mock()

        manager.reset_sequence("id_seq", 100)

        mock_session.execute.assert_called_once()
        call_args = mock_session.execute.call_args[0][0]
        assert "setval('id_seq', 100)" in str(call_args)

    def test_fix_sequences_success(
        self, with_mock_data: None, mock_session: Session
    ):
        """Test successful sequence fixing."""
        manager = SequenceManager(mock_session)
        mock_session.commit = Mock()

        result = manager.fix_sequences()

        mock_data = load_mock_data()
        expected_id = max(row["id"] for row in mock_data[MOCK_TABLE_NAME]) + 1
        assert f"Reset sequence for {MOCK_TABLE_NAME} to {expected_id}" in result
        assert "All sequences have been reset successfully!" in result
        mock_session.commit.assert_called_once()
