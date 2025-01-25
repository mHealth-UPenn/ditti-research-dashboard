from pprint import pprint
import re
from typing import Optional, TypedDict

from sqlalchemy import select

from aws_portal.app import create_app
import aws_portal.models as m
from aws_portal.utils.aws import Query


class User(TypedDict):
    __typename: str
    _lastChangedAt: int
    _version: int
    createdAt: str
    exp_time: Optional[str]
    id: str
    tap_permission: Optional[bool]
    team_email: Optional[str]
    updatedAt: str
    user_permission_id: Optional[str]


if __name__ == "__main__":
    app = create_app()
    users: list[User] = Query("User").scan()["Items"]

    for user in users:
        match = re.match(r"^[A-Za-z]+(?=\d)", user["user_permission_id"])

        if not match:
            continue

        study_prefix = match[0]

        with app.app_context():
            study = m.Study.query.filter(m.Study.ditti_id == study_prefix).first()
            print(user["user_permission_id"], study)
