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

import logging
from unittest.mock import MagicMock

import pytest

from backend.utils.request_formatter import RequestFormatter


@pytest.fixture
def mock_request_formatter():
    """Mock RequestFormatter class for testing."""
    formatter = RequestFormatter(
        fmt="[%(asctime)s] RequestId: %(request_id)s - %(levelname)s in %(module)s: %(message)s"
    )
    formatter._get_request = MagicMock()
    formatter._has_request_context = MagicMock()
    return formatter


class TestRequestFormatter:
    """Test cases for the RequestFormatter class."""

    def test_format_with_lambda_context(
        self, mock_request_formatter: RequestFormatter
    ):
        """Test formatting when Lambda context is available."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Mock Lambda context with request ID
        mock_context = MagicMock()
        mock_context.aws_request_id = "test-request-id-123"
        mock_request_formatter._get_request().environ = {
            "lambda.context": mock_context
        }

        result = mock_request_formatter.format(record)
        assert record.request_id == "test-request-id-123"
        assert "test-request-id-123" in result

    def test_format_without_lambda_context(
        self, mock_request_formatter: RequestFormatter
    ):
        """Test formatting when request context exists but no Lambda context."""
        mock_request_formatter._has_request_context.return_value = True
        mock_request_formatter._get_request().environ = {}  # No lambda.context
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = mock_request_formatter.format(record)

        assert record.request_id is None
        assert "None" in result

    def test_format_without_request_context(
        self, mock_request_formatter: RequestFormatter
    ):
        """Test formatting when no request context is available."""
        mock_request_formatter._has_request_context.return_value = False
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = mock_request_formatter.format(record)

        assert record.request_id is None
        assert "None" in result

    def test_format_with_none_lambda_context(
        self, mock_request_formatter: RequestFormatter
    ):
        """Test formatting when Lambda context is explicitly None."""
        mock_request_formatter._get_request().environ = {"lambda.context": None}
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = mock_request_formatter.format(record)

        assert record.request_id is None
        assert "None" in result

    def test_format_with_missing_lambda_context_key(
        self, mock_request_formatter: RequestFormatter
    ):
        """Test formatting when lambda.context key is missing from environ."""
        mock_request_formatter._get_request().environ = {
            "other_key": "value"
        }  # No lambda.context
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = mock_request_formatter.format(record)

        assert record.request_id is None
        assert "None" in result

    def test_format_with_empty_environ(
        self, mock_request_formatter: RequestFormatter
    ):
        """Test formatting when environ is empty."""
        mock_request_formatter._get_request().environ = {}
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = mock_request_formatter.format(record)

        assert record.request_id is None
        assert "None" in result

    def test_format_with_different_log_levels(
        self, mock_request_formatter: RequestFormatter
    ):
        """Test formatting with different log levels."""
        for level in [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ]:
            mock_context = MagicMock()
            mock_context.aws_request_id = f"request-id-{level}"
            mock_request_formatter._get_request().environ = {
                "lambda.context": mock_context
            }
            record = logging.LogRecord(
                name="test",
                level=level,
                pathname="test.py",
                lineno=1,
                msg=f"Test message for {level}",
                args=(),
                exc_info=None,
            )

            result = mock_request_formatter.format(record)

            assert record.request_id == f"request-id-{level}"
            assert f"request-id-{level}" in result
            assert record.levelname in result

    def test_format_with_exception_info(
        self, mock_request_formatter: RequestFormatter
    ):
        """Test formatting when log record has exception info."""
        import sys

        mock_context = MagicMock()
        mock_context.aws_request_id = "exception-request-id"

        mock_request_formatter._get_request().environ = {
            "lambda.context": mock_context
        }
        try:
            raise ValueError("Test exception")
        except ValueError:
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=1,
                msg="Test message with exception",
                args=(),
                exc_info=sys.exc_info(),
            )

            result = mock_request_formatter.format(record)

            assert record.request_id == "exception-request-id"
            assert "exception-request-id" in result
            assert "Test message with exception" in result

    def test_format_preserves_original_record_attributes(
        self, mock_request_formatter: RequestFormatter
    ):
        """Test that formatting preserves original record attributes."""
        mock_context = MagicMock()
        mock_context.aws_request_id = "preserve-request-id"

        mock_request_formatter._get_request().environ = {
            "lambda.context": mock_context
        }
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Store original attributes
        original_name = record.name
        original_level = record.levelno
        original_msg = record.msg

        mock_request_formatter.format(record)

        # Check that request_id was added
        assert record.request_id == "preserve-request-id"

        # Check that original attributes are preserved
        assert record.name == original_name
        assert record.levelno == original_level
        assert record.msg == original_msg
