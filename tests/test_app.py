from datetime import timedelta
from time import sleep
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
import pytest
from aws_portal.app import create_app
from aws_portal.extensions import db
from aws_portal.models import init_db
from tests.testing_utils import (
    create_joins, create_tables, get_cookie_from_response, login_test_account
)

blueprint = Blueprint('test', __name__, url_prefix='/test')


@blueprint.route('/get')
@jwt_required()
def get():
    return jsonify({'msg': 'OK'})


@pytest.fixture
def app():
    app = create_app(testing=True)
    app.register_blueprint(blueprint)
    with app.app_context():
        init_db()
        create_tables()
        create_joins()
        db.session.commit()

        yield app


@pytest.fixture
def timeout_client(app):
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
    with app.test_client() as client:
        yield client


def test_refresh_expiring_jwts(timeout_client):
    res = login_test_account('foo', timeout_client)
    old_token = res.json["jwt"]
    headers = {"Authorization": "Bearer " + old_token}
    res = timeout_client.get('/test/get', headers=headers)
    new_token = res.json["jwt"]
    assert old_token != new_token
