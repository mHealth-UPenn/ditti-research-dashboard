from base64 import b64encode
from datetime import datetime, UTC
import json
from typing import TypedDict
from unittest.mock import patch
import uuid

from flask import Flask, Response, make_response
from flask.testing import FlaskClient
from sqlalchemy import select, tuple_


# Mock endpoints that return 200 OK on all authorized requests
def return_200_on_auth():
    return make_response({"msg": "Authorized request."}, 200)


patch("aws_portal.views.admin.account", return_200_on_auth)
patch("aws_portal.views.admin.account_create", return_200_on_auth)
patch("aws_portal.views.admin.account_edit", return_200_on_auth)
patch("aws_portal.views.admin.account_archive", return_200_on_auth)
patch("aws_portal.views.admin.study", return_200_on_auth)
patch("aws_portal.views.admin.study_create", return_200_on_auth)
patch("aws_portal.views.admin.study_edit", return_200_on_auth)
patch("aws_portal.views.admin.study_archive", return_200_on_auth)
patch("aws_portal.views.admin.access_group", return_200_on_auth)
patch("aws_portal.views.admin.access_group_create", return_200_on_auth)
patch("aws_portal.views.admin.access_group_edit", return_200_on_auth)
patch("aws_portal.views.admin.access_group_archive", return_200_on_auth)
patch("aws_portal.views.admin.role", return_200_on_auth)
patch("aws_portal.views.admin.role_create", return_200_on_auth)
patch("aws_portal.views.admin.role_edit", return_200_on_auth)
patch("aws_portal.views.admin.role_archive", return_200_on_auth)
patch("aws_portal.views.admin.app", return_200_on_auth)
patch("aws_portal.views.admin.app_create", return_200_on_auth)
patch("aws_portal.views.admin.app_edit", return_200_on_auth)
patch("aws_portal.views.admin.action", return_200_on_auth)
patch("aws_portal.views.admin.resource", return_200_on_auth)
patch("aws_portal.views.admin.about_sleep_template", return_200_on_auth)
patch("aws_portal.views.admin.about_sleep_template_create", return_200_on_auth)
patch("aws_portal.views.admin.about_sleep_template_edit", return_200_on_auth)
patch("aws_portal.views.admin.about_sleep_template_archive", return_200_on_auth)
patch("aws_portal.views.admin.study_subject", return_200_on_auth)
patch("aws_portal.views.admin.study_subject_create", return_200_on_auth)
patch("aws_portal.views.admin.study_subject_archive", return_200_on_auth)
patch("aws_portal.views.admin.study_subject_edit", return_200_on_auth)
patch("aws_portal.views.admin.api", return_200_on_auth)
patch("aws_portal.views.admin.api_create", return_200_on_auth)
patch("aws_portal.views.admin.api_edit", return_200_on_auth)
patch("aws_portal.views.admin.api_archive", return_200_on_auth)

from aws_portal.app import create_app
from aws_portal.extensions import db
import aws_portal.models as m


class Permission(TypedDict):
    action: str
    resource: str


class PermissionList:
    def __init__(self, permissions: list[Permission]):
        self._permissions = permissions
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._permissions):
            permission = self._permissions[self._index]
            self._index += 1
            return permission['action'], permission['resource']
        else:
            raise StopIteration


def blue(text: str) -> str:
    return f"\033[34m{text}\033[0m"


def yellow(text: str) -> str:
    return f"\033[33m{text}\033[0m"


def green(text: str) -> str:
    return f"\033[32m{text}\033[0m"


def red(text: str) -> str:
    return f"\033[31m{text}\033[0m"


def handle_response(res: Response):
    print(res)
    data = json.loads(res.data)
    try:
        print(data["msg"])
    except TypeError:
        print(f"Response with {len(data)} entries.")
    except KeyError:
        print(f"'msg' not in response with keys: {data.keys()}.")
    except Exception:
        print("Getting response data failed.")


def get(client: FlaskClient, app: int, headers: dict, url: str):
    print(f"\n{yellow("GET")} {blue(url)}")
    res = client.get(f"{url}?app={app}", headers=headers)
    handle_response(res)


def post(client: FlaskClient, body: dict, headers: dict, url: str):
    print(f"\n{green("POST")} {blue(url)}")
    res = client.post(url, data=body, headers=headers)
    handle_response(res)


def login(app: Flask, client: FlaskClient):
    auth = "fooemail.com:abc123"
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


class AccountContext:
    access_groups: list[m.AccessGroup]
    account: m.Account

    def __enter__(self):
        self.access_groups = []
        self.account = m.Account()
        self.account.first_name = "foo"
        self.account.last_name = "bar"
        self.account.email = "fooemail.com"
        self.account.is_confirmed = True
        self.account.public_id = str(uuid.uuid4())
        self.account.created_on = datetime.now(UTC)
        self.account.password = "abc123"
        db.session.add(self.account)
        db.session.commit()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        db.session.delete(self.account)
        for access_group in self.access_groups:
            db.session.delete(access_group)
        db.session.commit()

    def add_access_group(self, name: str, permissions: list[Permission], app_id: int):
        access_group = m.AccessGroup(name=name, app_id=app_id)
        self.access_groups.append(access_group)

        for action, resource in PermissionList(permissions):
            query = select(m.Permission)\
                .where(m.Permission.definition == tuple_(action, resource))
            permission = db.session.execute(query).scalars().first()
            if not permission:
                permission = m.Permission(action=action, resource=resource)
            join = m.JoinAccessGroupPermission()
            join.permission = permission
            access_group.permissions.append(join)

        join = m.JoinAccountAccessGroup()
        join.access_group = access_group
        self.account.access_groups.append(join)
        db.session.add(access_group)
        db.session.commit()



def main(app: Flask, client: FlaskClient, account: AccountContext):
    print(f"\n\n{"=" * 40} STARTING TESTS {"=" * 40}\n\n")
    headers = login(app, client)

    # 1. Admin - No Authorization
    print(red("\n\nTesting Admin - No Authorization"))
    admin(client, 1, headers)

    # 2. Admin - With Ditti Admin Authorization, From Admin Dashboard
    print(red("\n\nTesting Admin - With Ditti Admin Authorization"))
    permissions: list[Permission] = [
        {"action": "View", "resource": "Ditti Dashboard"},
        {"action": "*", "resource": "*"},
    ]
    account.add_access_group("Test Ditti Admin", permissions, 2)
    admin(client, 1, headers)

    # 3. Admin - With Ditti Admin Authorization, From Ditti Dashboard
    print(red("\n\nAdmin - With Ditti Admin Authorization, From Ditti Dashboard"))
    admin(client, 2, headers)

    # 4. Admin - With Ditti Admin Authorization, From Wearable Dashboard
    print(red("\n\nAdmin - With Ditti Admin Authorization, From Wearable Dashboard"))
    admin(client, 3, headers)

    # 5. Admin - With Admin Authorization
    print(red("\n\nTesting Admin - With Admin Authorization"))
    permissions: list[Permission] = [
        {"action": "View", "resource": "Admin Dashboard"},
        {"action": "*", "resource": "*"},
    ]
    account.add_access_group("Test Admin", permissions, 1)
    admin(client, 1, headers)


if __name__ == "__main__":
    app = create_app(testing=True)
    with app.app_context():
        with AccountContext() as account:
            with app.test_client() as client:
                main(app, client, account)
