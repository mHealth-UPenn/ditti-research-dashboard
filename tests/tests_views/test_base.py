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
from unittest.mock import patch


def test_touch(client):
    res = client.get("/touch")
    data = json.loads(res.data)
    assert res.status_code == 200
    assert "msg" in data
    assert data["msg"] == "OK"


def test_health_check(client):
    # Mock the database connection and execution
    res = client.get("/health")
    data = json.loads(res.data)
    assert res.status_code == 200
    assert "msg" in data
    assert data["msg"] == "Service is healthy."
    assert "flask_secret_key_version_id" in data


def test_health_check_failure(client):
    # Mock the database connection to raise an exception
    with patch(
        "backend.views.base.db.engine.connect",
        side_effect=Exception("DB connection error"),
    ):
        res = client.get("/health")
        data = json.loads(res.data)
        assert res.status_code == 500
        assert "msg" in data
        assert data["msg"] == "Service is unhealthy."
        assert "flask_secret_key_version_id" in data


def test_health_check_version_id(client):
    """Test the /health endpoint returns the correct version ID."""
    version_id = "abc-123-def-456"
    client.application.config["FLASK_SECRET_KEY_VERSION_ID"] = version_id
    res = client.get("/health")
    data = json.loads(res.data)
    assert res.status_code == 200
    assert data["flask_secret_key_version_id"] == version_id


def test_health_check_version_id_not_set(client):
    """Test the /health endpoint returns 'not_set' if version ID is not set."""
    if "FLASK_SECRET_KEY_VERSION_ID" in client.application.config:
        del client.application.config["FLASK_SECRET_KEY_VERSION_ID"]
    res = client.get("/health")
    data = json.loads(res.data)
    assert res.status_code == 200
    assert data["flask_secret_key_version_id"] == "not_set"
