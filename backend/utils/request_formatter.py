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
        if self._has_request_context():
            context = self._get_request().environ.get("lambda.context", None)
            if context:
                record.request_id = context.aws_request_id
            else:
                record.request_id = None
        else:
            record.request_id = None

        return super().format(record)

    def _get_request(self):
        return request

    def _has_request_context(self):
        return has_request_context()
