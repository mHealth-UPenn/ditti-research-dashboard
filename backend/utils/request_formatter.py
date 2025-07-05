import logging

from flask import has_request_context, request


class RequestFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        if has_request_context():
            context = request.environ.get("lambda.context", None)
            if context:
                record.request_id = context.aws_request_id
            else:
                record.request_id = None
        else:
            record.request_id = None

        return super().format(record)
