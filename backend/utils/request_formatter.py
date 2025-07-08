import logging

from flask import has_request_context, request


class RequestFormatter(logging.Formatter):
    """
    Retrieves the request ID from the request context and adds it to the log record.

    If there is no request context, the request ID is set to None.

    Example Usage
    -------------
    >>> dictConfig(
    >>>     {
    >>>         "formatters": {
    >>>             "request": {
    >>>                 "()": "backend.utils.request_formatter.RequestFormatter",
    >>>                 "format": "[%(asctime)s] RequestId: %(request_id)s - %(levelname)s in %(module)s: %(message)s",
    >>>             },
    >>>         },
    >>>         "handlers": {
    >>>             "wsgi": {
    >>>                 "class": "logging.StreamHandler",
    >>>                 "stream": "ext://flask.logging.wsgi_errors_stream",
    >>>                 "formatter": "request",
    >>>             }
    >>>         },
    >>>     }
    >>> )
    """

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
