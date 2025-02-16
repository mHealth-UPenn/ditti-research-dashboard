from base64 import b64encode
from datetime import datetime, UTC
import json
import uuid

from flask import Flask
from flask.testing import FlaskClient

from aws_portal.app import create_app
from aws_portal.extensions import db
import aws_portal.models as m


def blue(text: str) -> str:
    return f"\033[34m{text}\033[0m"


def yellow(text: str) -> str:
    return f"\033[33m{text}\033[0m"


def green(text: str) -> str:
    return f"\033[32m{text}\033[0m"


def get(client: FlaskClient, app: int, headers: dict, url: str):
    print(f"\n{yellow("GET")} {blue(url)}")
    res = client.get(f"{url}?app={app}", headers=headers)
    print(res)
    print(json.loads(res.data))


def post(client: FlaskClient, body: dict, headers: dict, url: str):
    print(f"\n{green("POST")} {blue(url)}")
    res = client.post(url, data=body, headers=headers)
    print(res)
    print(json.loads(res.data))


def login(app: Flask, client: FlaskClient):
    auth = "foo@email.com:abc123"
    auth = b64encode(auth.encode("utf-8"))
    headers = {"Authorization": f"Basic {auth.decode()}"}
    res = client.post("/iam/login", headers=headers)

    csrf_token = res.json.get("csrfAccessToken")
    if not csrf_token:
        raise ValueError("CSRF token not found in response.")

    headers = {app.config["JWT_ACCESS_CSRF_HEADER_NAME"]: csrf_token}
    jwt_token = res.json.get("jwt")
    if jwt_token:
        headers.update({"Authorization": f"Bearer {jwt_token}"})

    return headers


def admin(client: FlaskClient, app_id: int, headers: dict):
    post_headers = {"Content-Type": "application/json", **headers}
    create_body = json.dumps({"app": app_id, "create": {}})
    edit_body = json.dumps({"app": app_id, "edit": {}})
    archive_body = json.dumps({"app": app_id, "id": 0})

    get(client, app_id, headers, "/admin/account")
    post(client, create_body, post_headers, "/admin/account/create")
    post(client, edit_body, post_headers, "/admin/account/edit")
    post(client, archive_body, post_headers, "/admin/account/archive")
    get(client, app_id, headers, "/admin/study")
    post(client, create_body, post_headers, "/admin/study/create")
    post(client, edit_body, post_headers, "/admin/study/edit")
    post(client, archive_body, post_headers, "/admin/study/archive")
    get(client, app_id, headers, "/admin/access-group")
    post(client, create_body, post_headers, "/admin/access-group/create")
    post(client, edit_body, post_headers, "/admin/access-group/edit")
    post(client, archive_body, post_headers, "/admin/access-group/archive")
    get(client, app_id, headers, "/admin/role")
    post(client, create_body, post_headers, "/admin/role/create")
    post(client, edit_body, post_headers, "/admin/role/edit")
    post(client, archive_body, post_headers, "/admin/role/archive")
    get(client, app_id, headers, "/admin/app")
    post(client, create_body, post_headers, "/admin/app/create")
    post(client, edit_body, post_headers, "/admin/app/edit")
    get(client, app_id, headers, "/admin/action")
    get(client, app_id, headers, "/admin/resource")
    get(client, app_id, headers, "/admin/about-sleep-template")
    post(client, create_body, post_headers, "/admin/about-sleep-template/create")
    post(client, edit_body, post_headers, "/admin/about-sleep-template/edit")
    post(client, archive_body, post_headers, "/admin/about-sleep-template/archive")
    get(client, app_id, headers, "/admin/study_subject")
    post(client, create_body, post_headers, "/admin/study_subject/create")
    post(client, archive_body, post_headers, "/admin/study_subject/archive")
    post(client, edit_body, post_headers, "/admin/study_subject/edit")
    get(client, app_id, headers, "/admin/api")
    post(client, create_body, post_headers, "/admin/api/create")
    post(client, edit_body, post_headers, "/admin/api/edit")
    post(client, archive_body, post_headers, "/admin/api/archive")


class AccountManager:
    def __enter__(self):
        self.account = m.Account()
        self.account.first_name = "foo"
        self.account.last_name = "bar"
        self.account.email = "foo@email.com"
        self.account.is_confirmed = True
        self.account.public_id = str(uuid.uuid4())
        self.account.created_on = datetime.now(UTC)
        self.account.password = "abc123"
        db.session.add(self.account)
        db.session.commit()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        db.session.delete(self.account)
        db.session.commit()


if __name__ == "__main__":
    app = create_app(testing=True)
    with app.app_context():
        with AccountManager() as account:
            with app.test_client() as client:
                headers = login(app, client)

                # 1. Admin - No Authorization
                admin(client, 1, headers)
