# Ditti Research Dashboard
# Copyright (C) 2025 the Trustees of the University of Pennsylvania
#
# Ditti Research Dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Ditti Research Dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import logging
import sys
from datetime import date, datetime


# Custom JSON formatter
class JsonFormatter(logging.Formatter):
    """
    Custom formatter that outputs log records as JSON.

    Formats log records as JSON objects, excluding specified fields
    and adding custom fields as needed.
    """

    exclude = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "taskName",
    }

    def format(self, record):
        """
        Format the specified record as JSON.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to format.

        Returns
        -------
        dict
            A dictionary representation of the log record.
        """
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # Add any extra fields in record if they exist
        for k, v in record.__dict__.items():
            if k in self.exclude:
                continue
            if isinstance(v, (datetime, date)):
                log_entry[k] = v.isoformat()
            else:
                log_entry[k] = v

        return log_entry  # Return a dictionary instead of a JSON string


class StreamFormatter(JsonFormatter):
    """
    JSON formatter for console output with pretty printing.

    Extends JsonFormatter to provide indented JSON output
    suitable for console viewing.
    """

    def format(self, record: logging.LogRecord):
        """
        Format the log record as indented JSON.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to format.

        Returns
        -------
        str
            A JSON string representation of the log record with indentation.
        """
        entry = super().format(record)
        return json.dumps(entry, indent=4)


class JsonFileHandler(logging.Handler):
    """
    Custom log handler that saves records to a JSON file.

    Collects log records in memory and writes them to a JSON file
    when explicitly requested.
    """

    def __init__(self, log_filename):
        super().__init__()
        self.log_filename = log_filename
        self.log_entries = []  # Keep track of all log entries in memory

    def emit(self, record):
        """
        Process a log record by adding it to the in-memory collection.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to process.

        Returns
        -------
        None
        """
        # Format the record and append it to the in-memory list
        formatter = self.formatter
        if formatter:
            formatted_record = formatter.format(record)
            self.log_entries.append(formatted_record)

        with open(self.log_filename, "w") as log_file:
            json.dump(self.log_entries, log_file, indent=4)


class LambdaLogger(logging.Logger):
    """
    Specialized logger for AWS Lambda functions.

    Provides structured logging capabilities with both console
    and file outputs in JSON format.
    """

    def __init__(self, job_timestamp: str, /, *, level=logging.INFO):
        self.job_timestamp = job_timestamp
        self.log_filename = f"/tmp/log_{self.job_timestamp}.json"  # noqa: S108

        # Set up logger
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(level)

        # JSON Formatter
        json_formatter = JsonFormatter()
        stream_formatter = StreamFormatter()

        # Stream handler for console output
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(level)
        stream_handler.setFormatter(stream_formatter)
        self.__logger.addHandler(stream_handler)

        # Custom JSON file handler for structured logging
        json_file_handler = JsonFileHandler(self.log_filename)
        json_file_handler.setLevel(level)
        json_file_handler.setFormatter(json_formatter)
        self.__logger.addHandler(json_file_handler)

    def debug(self, *args, **kwargs):
        """
        Log a message with DEBUG level.

        Parameters
        ----------
        *args : tuple
            Positional arguments to pass to the logger.
        **kwargs : dict
            Keyword arguments to pass to the logger.

        Returns
        -------
        None
        """
        self.__logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        """
        Log a message with INFO level.

        Parameters
        ----------
        *args : tuple
            Positional arguments to pass to the logger.
        **kwargs : dict
            Keyword arguments to pass to the logger.

        Returns
        -------
        None
        """
        self.__logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        """
        Log a message with WARNING level.

        Parameters
        ----------
        *args : tuple
            Positional arguments to pass to the logger.
        **kwargs : dict
            Keyword arguments to pass to the logger.

        Returns
        -------
        None
        """
        self.__logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        """
        Log a message with ERROR level.

        Parameters
        ----------
        *args : tuple
            Positional arguments to pass to the logger.
        **kwargs : dict
            Keyword arguments to pass to the logger.

        Returns
        -------
        None
        """
        self.__logger.error(*args, **kwargs)

    def critical(self, *args, **kwargs):
        """
        Log a message with CRITICAL level.

        Parameters
        ----------
        *args : tuple
            Positional arguments to pass to the logger.
        **kwargs : dict
            Keyword arguments to pass to the logger.

        Returns
        -------
        None
        """
        self.__logger.critical(*args, **kwargs)
