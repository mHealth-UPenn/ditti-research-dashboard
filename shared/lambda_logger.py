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
        "taskName"
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

        return json.dumps(log_entry, indent=4)


class LambdaLogger(logging.Logger):
    def __init__(self, job_timestamp: str):
        self.job_timestamp = job_timestamp
        self.log_filename = f"log_{self.job_timestamp}.json"

        # Set up logger to write JSON log entries to a file
        self.__logger = logging.getLogger("logger")
        self.__logger.setLevel(logging.INFO)

        # JSON Formatter
        json_formatter = JsonFormatter()

        # Stream handler for console output
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(json_formatter)
        self.__logger.addHandler(stream_handler)

        # File handler for JSON log file output
        file_handler = logging.FileHandler(self.log_filename)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(json_formatter)
        self.__logger.addHandler(file_handler)

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
