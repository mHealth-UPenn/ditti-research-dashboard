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
