from time import sleep
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from tests.testing_utils import login_test_account

blueprint = Blueprint('test', __name__, url_prefix='/test')


@blueprint.route('/get')
@jwt_required()
def get():
    return jsonify({'msg': 'OK'})


def test_refresh_expiring_jwts(timeout_client):
    res = login_test_account('foo', timeout_client)
    old_token = res.json["jwt"]
    headers = {"Authorization": "Bearer " + old_token}
    sleep(1)
    res = timeout_client.get('/test/get', headers=headers)
    new_token = res.json["jwt"]
    assert old_token != new_token
