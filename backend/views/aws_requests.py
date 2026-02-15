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

import logging
import traceback
from functools import reduce

import pandas as pd
from flask import Blueprint, jsonify, make_response, request

from backend.auth.decorators import researcher_auth_required
from backend.extensions import ditti
from backend.models import JoinAccountStudy, Study

blueprint = Blueprint("aws", __name__, url_prefix="/aws")
logger = logging.getLogger(__name__)


@blueprint.route("/get-taps")
@researcher_auth_required("View", "Ditti App Dashboard")
def get_taps(account):
    """
    Get tap data.

    If the user has permissions to view all studies, this will
    return all tap data. Otherwise, this will return tap data for only the
    studies the user has access to

    Options
    -------
    app: 2

    Response Syntax (200)
    ---------------------
    [
        {
            user_permission_id: str,
            time: iso-formatted timestamp
        },
        ...
    ]

    Response syntax (500)
    ---------------------
    {
        msg: "Query failed due to internal server error."
    }
    """

    # Add expressions to the query to return all taps for multiple studies
    def f(left, right):
        q = f'user_permission_id^"{right}"'
        return left + ("|" if left else "") + q

    try:
        # If the user has permission to view all studies, get all users
        app_id = request.args["app"]
        permissions = account.get_permissions(app_id)
        account.validate_ask("View", "All Studies", permissions)
        users = ditti.get(
            "user_permission", query="", attributes=["id", "user_permission_id"]
        ).data

    except ValueError:
        # Get users only for the studies the user as access to
        studies = (
            Study.query.join(JoinAccountStudy)
            .filter(JoinAccountStudy.account_id == account.id)
            .all()
        )

        prefixes = [s.ditti_id for s in studies]
        query = reduce(f, prefixes, "")
        users = ditti.get(
            "user_permission",
            query=query,
            attributes=["id", "user_permission_id"],
        ).data

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)

        return make_response(
            {"msg": "Query failed due to internal server error."}, 500
        )

    # Get all taps
    taps = ditti.get(
        "tap",
        query="",
        attributes=["id", "tapUserId", "time", "timeZone"],
    ).data

    df_users = pd.DataFrame(users, columns=["id", "user_permission_id"]).rename(
        columns={"user_permission_id": "dittiId"}
    )

    df_taps = pd.DataFrame(
        taps, columns=["tapUserId", "time", "timeZone"]
    ).rename(columns={"tapUserId": "id", "timeZone": "timezone"})

    # Old versions of the app record UTC timestamps
    # Fill missing timezone values with the UTC timezone
    df_taps["timezone"] = df_taps["timezone"].fillna(
        "GMT Universal Coordinated Time"
    )

    # Merge on only the users that were returned earlier
    res = (
        pd.merge(df_users, df_taps, on="id").drop("id", axis=1).to_dict("records")
    )

    return jsonify(res)


@blueprint.route("/get-audio-taps")
@researcher_auth_required("View", "Ditti App Dashboard")
def get_audio_taps(account):
    """
    Get audio taps data from the database.

    Retrieves audio tap data for studies the researcher has access to.

    Parameters
    ----------
    account : Account
        The authenticated researcher account.

    Returns
    -------
    flask.Response
        JSON response containing audio taps data.
    """

    # Add expressions to the query to return all taps for multiple studies
    def f(left: str, right: str) -> str:
        q = f'user_permission_id^"{right}"'
        return left + ("|" if left else "") + q

    try:
        # If the user has permission to view all studies, get all users
        app_id = request.args["app"]
        permissions = account.get_permissions(app_id)
        account.validate_ask("View", "All Studies", permissions)
        users = ditti.get("user_permission", query="", attributes=["id"]).data

    except ValueError:
        # Get users only for the studies the user as access to
        studies = (
            Study.query.join(JoinAccountStudy)
            .filter(JoinAccountStudy.account_id == account.id)
            .all()
        )

        prefixes = [s.ditti_id for s in studies]
        users = ditti.get(
            "user_permission",
            query=reduce(f, prefixes, ""),
            attributes=["id"],
        ).data

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)

        return make_response(
            {"msg": "Query failed due to internal server error."}, 500
        )

    # Get all audio files
    audio_files = ditti.get(
        "audio_file",
        query="",
        attributes=["id", "title"],
    ).data

    # Get all taps
    audio_taps = ditti.get(
        "audio_tap",
        query="",
        attributes=[
            "id",
            "audioTapAudioFileId",
            "audioTapUserId",
            "time",
            "timeZone",
            "action",
        ],
    ).data

    df_users = pd.DataFrame(users, columns=["id", "user_permission_id"]).rename(
        columns={"id": "userId", "user_permission_id": "dittiId"}
    )

    df_audio_files = pd.DataFrame(audio_files, columns=["id", "title"]).rename(
        columns={"id": "audioFileId", "title": "audioFileTitle"}
    )

    df_audio_taps = pd.DataFrame(
        audio_taps,
        columns=[
            "audioTapUserId",
            "audioTapAudioFileId",
            "time",
            "timeZone",
            "action",
        ],
    ).rename(
        columns={
            "audioTapUserId": "userId",
            "audioTapAudioFileId": "audioFileId",
            "timeZone": "timezone",
        }
    )

    # Merge on only the users that were returned earlier
    res = (
        df_users.merge(df_audio_taps, on="userId")
        .merge(df_audio_files, on="audioFileId")
        .drop(["userId", "audioFileId"], axis=1)
        .to_dict("records")
    )

    return jsonify(res)


@blueprint.route("/get-users")
@researcher_auth_required("View", "Ditti App Dashboard")
def get_users(account):
    """
    Get user data.

    If the user has permissions to view all studies, this will
    return all user data. Otherwise, this will return user data for only the
    studies the user has access to

    Options
    -------
    app: 2

    Response Syntax (200)
    ---------------------
    [
        {
            tapPermission: bool
            information: str
            userPermissionId: str
            expTime: iso-formatted timestamp
            teamEmail: str
            createdAt: iso-formatted timestamp
        },
        ...
    ]

    Response syntax (500)
    ---------------------
    {
        msg: "Query failed due to internal server error."
    }
    """

    # Add expressions to the query to return all users for multiple studies
    def f(left, right):
        q = f'user_permission_id^"{right}"'
        return left + ("|" if left else "") + q

    # Gets only useful user data
    def map_users(user):
        # If information is empty, use an empty string instead of None
        information = user.get("information", "")

        return {
            "id": user.get("id", ""),
            "tapPermission": user.get("tap_permission", False),
            "information": information,
            "userPermissionId": user.get("user_permission_id", ""),
            "expTime": user.get("exp_time", ""),
            "teamEmail": user.get("team_email", ""),
        }

    users = None

    try:
        # If the user has permission to view all studies, get all studies
        app_id = request.args["app"]
        permissions = account.get_permissions(app_id)
        account.validate_ask("View", "All Studies", permissions)
        users = ditti.get(
            "user_permission",
            query="",
            attributes=[
                "id",
                "information",
                "tap_permission",
                "user_permission_id",
                "exp_time",
                "team_email",
            ],
        ).data
        res = map(map_users, users)

        return jsonify(list(res))

    except ValueError:
        # Get only the studies the user has access to
        studies = (
            Study.query.join(JoinAccountStudy)
            .filter(JoinAccountStudy.account_id == account.id)
            .all()
        )

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)

        return make_response(
            {"msg": "Query failed due to internal server error."}, 500
        )

    # Get all users for the studies that were returned earlier
    prefixes = [s.ditti_id for s in studies]

    # If no studies were found, return an empty list
    if not prefixes:
        return jsonify([])

    query = reduce(f, prefixes, "")
    users = ditti.get(
        "user_permission",
        query=query,
        attributes=[
            "id",
            "information",
            "tap_permission",
            "user_permission_id",
            "exp_time",
            "team_email",
        ],
    ).data
    res = map(map_users, users)

    return jsonify(list(res))


@blueprint.route("/user/create", methods=["POST"])
@researcher_auth_required("View", "Ditti App Dashboard")
@researcher_auth_required("Create", "Participants")
def user_create():
    """
    Create a new user.

    Request Syntax
    --------------
    {
        app: 2,
        study: int,
        create: [
            {
                exp_time: iso-formatted timestamp,
                tap_permission: boolean,
                team_email: str,
                user_permission_id: str,
                information: str
            },
            ...
        ]
    }

    Response syntax (200)
    ---------------------
    {
        msg: "User Created Successfully"
    }

    Response syntax (500)
    ---------------------
    {
        msg: "User creation failed due to internal server error."
    }
    """
    msg = "User Created Successfully"

    try:
        data = request.json.get("create")
        response = ditti.create("user_permission", data=data)
        msg = response.message

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)

        return make_response(
            {"msg": "User creation failed due to internal server error."}, 500
        )

    return jsonify({"msg": msg})


@blueprint.route("/user/edit", methods=["POST"])
@researcher_auth_required("View", "Ditti App Dashboard")
@researcher_auth_required("Edit", "Participants")
def user_edit():
    """
    Edit an exisitng user.

    Request Syntax
    --------------
    {
        app: 2,
        study: int,
        edit: [
            {
                id: str,
                exp_time: iso-formatted timestamp,
                tap_permission: boolean,
                team_email: str,
                user_permission_id: str,
                information: str
            }
        ]
    }

    All data in the request body are optional. Any attributes that are excluded
    from the request body will not be changed.

    Response syntax (200)
    ---------------------
    {
        msg: "User Successfully Edited" or
            "Invalid study or study subject Ditti ID: ..." or
            "Invalid study Ditti ID: ..." or
            "Ditti ID not found: ..."
    }

    Response syntax (500)
    ---------------------
    {
        msg: "User edit failed due to internal server error."
    }
    """
    msg = "User Successfully Edited"

    try:
        data = request.json.get("edit")
        response = ditti.edit("user_permission", data=data)
        msg = response.message

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)

        return make_response(
            {"msg": "User edit failed due to internal server error."}, 500
        )

    return jsonify({"msg": msg})


@blueprint.route("/get-audio-files")
@researcher_auth_required("View", "Ditti App Dashboard")
@researcher_auth_required("View", "Audio Files")
def get_audio_files():
    """
    Get all audio files from DynamoDB.

    Options
    -------
    app: 2

    Response Syntax (200)
    ---------------------
    [
        {
            id: str,
            _version: int,
            fileName: str,
            title: str,
            category: str,
            availability: str,
            studies: list[str],
            length: int,
        },
        ...
    ]

    Response syntax (500)
    ---------------------
    {
        msg: "Query failed due to internal server error."
    }
    """
    try:
        result = ditti.get(
            "audio_file",
            query="",
            attributes=[
                "id",
                "fileName",
                "title",
                "category",
                "availability",
                "studies",
                "length",
            ],
        ).data

        return jsonify(result)

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        return make_response(
            {"msg": "Query failed due to internal server error."}, 500
        )


@blueprint.route("/audio-file/create", methods=["POST"])
@researcher_auth_required("View", "Ditti App Dashboard")
@researcher_auth_required("Create", "Audio File")
def audio_file_create():
    """
    Insert new audio files into DynamoDB.

    Request Syntax
    --------------
    {
        app: 2,
        create: [
            {
                fileName: str,
                title: str,
                category: str,
                availability: str,
                studies: list[str],
                length: int,
            },
            ...
        ]
    }

    Response syntax (200)
    ---------------------
    {
        msg: "Audio File Created Successfully"
    }

    Response syntax (500)
    ---------------------
    {
        msg: "Creation of audio file failed due to internal server error."
    }
    """
    msg = "Audio File Created Successfully"

    try:
        data = request.json.get("create")
        response = ditti.create("audio_file", data=data)
        msg = response.message

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        return make_response(
            {
                "msg": "Creation of audio file failed "
                "due to internal server error."
            },
            500,
        )

    return jsonify({"msg": msg})


@blueprint.route("/audio-file/delete", methods=["POST"])
@researcher_auth_required("View", "Ditti App Dashboard")
@researcher_auth_required("Delete", "Audio File")
def audio_file_delete():
    """
    Permanently deletes an audio file.

    This endpoint first deletes the audio
    file from S3 then deletes the audio file from DynamoDB. If the deletion from
    S3 fails, the audio file is not deleted from DynamoDB.

    Request syntax
    --------------
    {
        app: 2,
        ids: list[str]
    }

    Response syntax (200)
    ---------------------
    {
        msg: "Audio File Deleted Successfully"
    }

    Response syntax (500)
    ---------------------
    {
        msg: "Deletion of audio file failed due to internal server error."
    }
    """
    msg = "Audio file successfully deleted."

    try:
        ids = request.json["ids"]
        response = ditti.delete("audio_file", delete_ids=ids)
        msg = response.message

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        return make_response(
            {
                "msg": "Deletion of audio file failed "
                "due to internal server error."
            },
            500,
        )

    return jsonify({"msg": msg})


@blueprint.route("/audio-file/get-presigned-urls", methods=["POST"])
@researcher_auth_required("View", "Ditti App Dashboard")
@researcher_auth_required("Create", "Audio File")
def audio_file_generate_presigned_urls():
    """
    Generate a list of presigned URLs for a given set of files.

    The request body must include a key for uploading to S3 and its MIME type.

    Request syntax
    --------------
    {
        app: 2,
        files: [
            {
                key: str,
                type: str
            }
        ]
    }

    Response syntax (200)
    ---------------------
    {
        urls: [
            str,
            ...
        ]
    }

    Response syntax (500)
    ---------------------
    {
        msg: AWS credentials not available
    }
    {
        msg: Unknown error while generating presigned URLs.
    }
    """
    msg = "Presigned URLs successfully generated."

    try:
        data = request.json.get("files")
        response = ditti.get_presigned_urls(data=data)
        urls = response.urls

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        return make_response(
            {
                "msg": "Generation of presigned URLs failed "
                "due to internal server error."
            },
            500,
        )

    return jsonify({"msg": msg, "urls": urls})
