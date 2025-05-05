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

import json
from unittest.mock import MagicMock

import pytest
from flask import Flask, Response, jsonify

from backend.auth.decorators import (
    participant_auth_required,
    researcher_auth_required,
)


def create_mock_response(data, status_code=200):
    """
    Create a simplified mock response for testing.

    This utility function creates a mock Response object that simulates
    Flask responses without requiring a full app context. Useful for
    creating mock error and success responses in tests.

    Parameters
    ----------
        data: The response data to be JSON-serialized
        status_code: HTTP status code for the response

    Returns
    -------
        A mock Response object with appropriate methods
    """
    response = MagicMock(spec=Response)
    response.status_code = status_code
    response.get_data.return_value = json.dumps(data).encode("utf-8")
    response.get_json.return_value = data
    return response


@pytest.fixture
def test_app():
    """
    Create a test Flask app with routes for auth decorator testing.

    This fixture provides a minimal Flask application with test routes
    configured with both participant_auth_required and researcher_auth_required
    decorators, allowing tests to verify the decorators' behavior in a
    realistic Flask context.

    Returns
    -------
        A configured Flask app for testing
    """
    app = Flask(__name__)
    app.config["TESTING"] = True

    # Create test routes for participant auth
    @app.route("/test-participant")
    @participant_auth_required
    def test_participant_route(ditti_id):
        return jsonify({"msg": "OK", "ditti_id": ditti_id})

    # Create test routes for researcher auth
    @app.route("/test-researcher")
    @researcher_auth_required
    def test_researcher_route(account):
        return jsonify({"msg": "OK", "account_id": account.id})

    @app.route("/test-researcher-permission")
    @researcher_auth_required("Create", "Accounts")
    def test_researcher_with_permission(account):
        return jsonify({"msg": "OK", "account_id": account.id})

    return app
