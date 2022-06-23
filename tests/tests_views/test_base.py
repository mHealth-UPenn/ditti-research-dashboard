import json
import pytest
from aws_portal.app import create_app
from aws_portal.models import init_db


@pytest.fixture
def app():
    app = create_app(testing=True)
    with app.app_context():
        init_db()
        yield app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


def test_healthy(client):
    res = client.get('/healthy')
    data = json.loads(res.data)
    assert res.status_code == 200
    assert 'msg' in data
    assert data['msg'] == 'OK'
