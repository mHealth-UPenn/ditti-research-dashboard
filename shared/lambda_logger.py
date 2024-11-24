from datetime import datetime
import json
import logging
import sys


# Custom JSON formatter
class JsonFormatter(logging.Formatter):
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
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # Add any extra fields in record if they exist
        log_entry.update(
            {
                k: v for k, v in record.__dict__.items()
                if k not in self.exclude
            }
        )

        return log_entry  # Return a dictionary instead of a JSON string


class StreamFormatter(JsonFormatter):
    def format(self, record: logging.LogRecord):
        entry = super().format(record)
        return json.dumps(entry, indent=4)


class JsonFileHandler(logging.Handler):
    def __init__(self, log_filename):
        super(JsonFileHandler, self).__init__()
        self.log_filename = log_filename
        self.log_entries = []  # Keep track of all log entries in memory

    def emit(self, record):
        # Format the record and append it to the in-memory list
        formatter = self.formatter
        if formatter:
            formatted_record = formatter.format(record)
            self.log_entries.append(formatted_record)

        with open(self.log_filename, "w") as log_file:
            json.dump(self.log_entries, log_file, indent=4)


class LambdaLogger(logging.Logger):
    def __init__(self, job_timestamp: str):
        self.job_timestamp = job_timestamp
        self.log_filename = f"log_{self.job_timestamp}.json"

        # Set up logger
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.INFO)

        # JSON Formatter
        json_formatter = JsonFormatter()
        stream_formatter = StreamFormatter()

        # Stream handler for console output
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(stream_formatter)
        self.__logger.addHandler(stream_handler)

        # Custom JSON file handler for structured logging
        json_file_handler = JsonFileHandler(self.log_filename)
        json_file_handler.setLevel(logging.INFO)
        json_file_handler.setFormatter(json_formatter)
        self.__logger.addHandler(json_file_handler)

    def debug(self, *args, **kwargs):
        self.__logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        self.__logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        self.__logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        self.__logger.error(*args, **kwargs)

    def critical(self, *args, **kwargs):
        self.__logger.critical(*args, **kwargs)
