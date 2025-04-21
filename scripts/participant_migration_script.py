import os
import random
import re
import string
from datetime import datetime
from typing import TypedDict

import boto3

import backend.models as m
from backend.app import create_app
from backend.extensions import db
from backend.utils.aws import Query


class User(TypedDict):
    __typename: str
    _lastChangedAt: int
    _version: int
    createdAt: str
    exp_time: str | None
    id: str
    tap_permission: bool | None
    team_email: str | None
    updatedAt: str
    user_permission_id: str | None


def generate_temp_password(length=20):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for i in range(length))


if __name__ == "__main__":
    app = create_app()
    users: list[User] = Query("User").scan()["Items"]
    client = boto3.client("cognito-idp")

    with app.app_context():
        for user in users:
            try:
                match = re.match(
                    r"^[A-Za-z]+(?=\d)", user["user_permission_id"]
                )

                if not match:
                    continue

                study_prefix = match[0]

                study = m.Study.query.filter(
                    m.Study.ditti_id == study_prefix
                ).first()

                if not study:
                    continue

                participant = m.StudySubject(
                    ditti_id=user["user_permission_id"]
                )
                m.JoinStudySubjectStudy(
                    study_subject=participant,
                    study=study,
                    did_consent=True,
                    starts_on=datetime.fromisoformat(user["createdAt"]),
                    expires_on=datetime.fromisoformat(user["exp_time"]),
                )
                db.session.add(participant)
                db.session.commit()

                temp_password = generate_temp_password()

                client.admin_create_user(
                    UserPoolId=os.getenv("USER_POOL_ID"),
                    Username=user["user_permission_id"],
                    TemporaryPassword=temp_password,
                    MessageAction="SUPPRESS",
                )

            except Exception:
                continue
