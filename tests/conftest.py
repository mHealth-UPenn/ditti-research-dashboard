from dotenv import load_dotenv

load_dotenv("flask.env")

from datetime import timedelta
from functools import partial
import os

import boto3
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from moto import mock_aws
import pytest

from aws_portal.app import create_app
from aws_portal.extensions import db
from aws_portal.models import (
    init_admin_account, init_admin_app, init_admin_group, init_db, init_api
)
from aws_portal.utils.auth import auth_required
from tests.testing_utils import (
    create_joins, create_tables, get_auth_headers, login_admin_account,
    login_test_account
)

os.environ["APP_SYNC_HOST"] = "https://testing"
os.environ["AWS_TABLENAME_USER"] = "testing_table_user"
os.environ["AWS_TABLENAME_TAP"] = "testing_table_tap"
os.environ["APPSYNC_ACCESS_KEY"] = "testing"
os.environ["APPSYNC_SECRET_KEY"] = "testing"

blueprint = Blueprint("test", __name__, url_prefix="/test")


@blueprint.route("/get")
@jwt_required()
def get():
    return jsonify({"msg": "OK"})


@blueprint.route("/get-auth-required-action")
@auth_required("foo")
def get_auth_required_action():
    return jsonify({"msg": "OK"})


@blueprint.route("/get-auth-required-resource")
@auth_required("bar", "baz")
def get_auth_required_resource():
    return jsonify({"msg": "OK"})


@blueprint.route("/post-auth-required-action", methods=["POST"])
@auth_required("foo")
def post_auth_required_action():
    return jsonify({"msg": "OK"})


@blueprint.route("/post-auth-required-resource", methods=["POST"])
@auth_required("bar", "baz")
def post_auth_required_resource():
    return jsonify({"msg": "OK"})


@pytest.fixture(scope="function")
def with_mocked_tables():
    with mock_aws():
        client = boto3.client("dynamodb")
        client.create_table(
            TableName="testing_table_user",
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        client.put_item(
            TableName="testing_table_user",
            Item={
                "id": {"S": "1"},
                "user_permission_id": {"S": "abc123"},
                "information": {"S": ""}
            }
        )

        yield client


@pytest.fixture
def app(with_mocked_tables):
    app = create_app(testing=True)
    app.register_blueprint(blueprint)
    with app.app_context():
        init_db()
        init_admin_app()
        init_admin_group()
        init_admin_account()
        init_api()
        create_tables()
        create_joins()
        db.session.commit()
        yield app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def get(client):
    res = login_test_account("foo", client)
    headers = get_auth_headers(res)
    get = partial(client.get, headers=headers)
    yield get


@pytest.fixture
def get_admin(client):
    res = login_admin_account(client)
    headers = get_auth_headers(res)
    get = partial(client.get, headers=headers)
    yield get


@pytest.fixture
def delete(client):
    res = login_test_account("foo", client)
    headers = get_auth_headers(res)
    delete = partial(
        client.delete,
        content_type="application/json",
        headers=headers
    )

    yield delete


@pytest.fixture
def delete_admin(client):
    res = login_admin_account(client)
    headers = get_auth_headers(res)
    delete = partial(
        client.delete,
        content_type="application/json",
        headers=headers
    )

    yield delete


@pytest.fixture
def post(client):
    res = login_test_account("foo", client)
    headers = get_auth_headers(res)
    post = partial(
        client.post,
        content_type="application/json",
        headers=headers
    )

    yield post


@pytest.fixture
def post_admin(client):
    res = login_admin_account(client)
    headers = get_auth_headers(res)
    post = partial(
        client.post,
        content_type="application/json",
        headers=headers
    )

    yield post


@pytest.fixture
def timeout_client(app):
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=1)
    with app.test_client() as client:
        yield client
