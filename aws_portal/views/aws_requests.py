# Ditti Research Dashboard
# Copyright (C) 2025 the Trustees of the University of Pennsylvania
#
# Ditti Research Dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Ditti Research Dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from functools import reduce
import json
import logging
import os
import re
import traceback

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from flask import Blueprint, current_app, jsonify, make_response, request
import pandas as pd

from aws_portal.models import JoinAccountStudy, Study
from aws_portal.auth.decorators import researcher_auth_required
from aws_portal.utils.aws import MutationClient, Query, Updater

blueprint = Blueprint("aws", __name__, url_prefix="/aws")
logger = logging.getLogger(__name__)


@blueprint.route("/get-taps")
@researcher_auth_required("View", "Ditti App Dashboard")
def get_taps(account):  # TODO update unit test
    """
    Get tap data. If the user has permissions to view all studies, this will
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

    # add expressions to the query to return all taps for multiple studies
    def f(left, right):
        q = "user_permission_idBEGINS\"%s\"" % right
        return left + ("OR" if left else "") + q

    try:

        # if the user has permission to view all studies, get all users
        app_id = request.args["app"]
        permissions = account.get_permissions(app_id)
        account.validate_ask("View", "All Studies", permissions)
        users = Query("User").scan()["Items"]

    except ValueError:

        # get users only for the studies the user as access to
        studies = Study.query\
            .join(JoinAccountStudy)\
            .filter(JoinAccountStudy.account_id == account.id)\
            .all()

        prefixes = [s.ditti_id for s in studies]
        query = reduce(f, prefixes, "")
        users = Query("User", query).scan()["Items"]

    except Exception as e:
        exc = traceback.format_exc()
        logger.warning(exc)

        return make_response({"msg": "Query failed due to internal server error."}, 500)

    # get all taps
    taps = Query("Tap").scan()["Items"]
    df_users = pd.DataFrame(users, columns=["id", "user_permission_id"])\
        .rename(columns={"user_permission_id": "dittiId"})

    df_taps = pd.DataFrame(taps, columns=["tapUserId", "time", "timeZone"])\
        .rename(columns={"tapUserId": "id", "timeZone": "timezone"})

    # Old versions of the app record UTC timestamps
    # Fill missing timezone values with the UTC timezone
    df_taps["timezone"] = df_taps["timezone"]\
        .fillna("GMT Universal Coordinated Time")

    # merge on only the users that were returned earlier
    res = pd.merge(df_users, df_taps, on="id")\
        .drop("id", axis=1)\
        .to_dict("records")

    return jsonify(res)


@blueprint.route("/get-audio-taps")
@researcher_auth_required("View", "Ditti App Dashboard")
def get_audio_taps(account):  # TODO write unit test
    # add expressions to the query to return all taps for multiple studies
    def f(left, right):
        q = "user_permission_idBEGINS\"%s\"" % right
        return left + ("OR" if left else "") + q

    try:
        # if the user has permission to view all studies, get all users
        app_id = request.args["app"]
        permissions = account.get_permissions(app_id)
        account.validate_ask("View", "All Studies", permissions)
        users = Query("User").scan()["Items"]

    except ValueError:
        # get users only for the studies the user as access to
        studies = Study.query\
            .join(JoinAccountStudy)\
            .filter(JoinAccountStudy.account_id == account.id)\
            .all()

        prefixes = [s.ditti_id for s in studies]
        query = reduce(f, prefixes, "")
        users = Query("User", query).scan()["Items"]

    except Exception as e:
        exc = traceback.format_exc()
        logger.warning(exc)

        return make_response({"msg": "Query failed due to internal server error."}, 500)

    # Get all audio files
    audio_files = Query("AudioFile").scan()["Items"]

    # Get all taps
    audio_taps = Query("AudioTap").scan()["Items"]

    df_users = pd.DataFrame(users, columns=["id", "user_permission_id"])\
        .rename(columns={"id": "userId", "user_permission_id": "dittiId"})

    df_audio_files = pd.DataFrame(audio_files, columns=["id", "title"])\
        .rename(columns={"id": "audioFileId", "title": "audioFileTitle"})

    df_audio_taps = pd.DataFrame(
        audio_taps,
        columns=[
            "audioTapUserId",
            "audioTapAudioFileId",
            "time",
            "timeZone",
            "action",
        ]
    ).rename(columns={
        "audioTapUserId": "userId",
        "audioTapAudioFileId": "audioFileId",
        "timeZone": "timezone",
    })

    # Merge on only the users that were returned earlier
    res = df_users.merge(df_audio_taps, on="userId")\
        .merge(df_audio_files, on="audioFileId")\
        .drop(["userId", "audioFileId"], axis=1)\
        .to_dict("records")

    return jsonify(res)


@blueprint.route("/get-users")
@researcher_auth_required("View", "Ditti App Dashboard")
def get_users(account):  # TODO: create unit test
    """
    Get user data. If the user has permissions to view all studies, this will
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

    # add expressions to the query to return all users for multiple studies
    def f(left, right):
        q = "user_permission_idBEGINS\"%s\"" % right
        return left + ("OR" if left else "") + q

    # gets only useful user data
    def map_users(user):

        # if information is empty, use an empty string instead of None
        information = user["information"] if "information" in user else ""

        return {
            "tapPermission": user["tap_permission"],
            "information": information,
            "userPermissionId": user["user_permission_id"],
            "expTime": user["exp_time"],
            "teamEmail": user["team_email"],
            "createdAt": user["createdAt"]
        }

    users = None

    try:

        # if the user has permission to view all studies, get all studies
        app_id = request.args["app"]
        permissions = account.get_permissions(app_id)
        account.validate_ask("View", "All Studies", permissions)
        users = Query("User").scan()["Items"]
        res = map(map_users, users)

        return jsonify(list(res))

    except ValueError:

        # get only the studies the user has access to
        studies = Study.query\
            .join(JoinAccountStudy)\
            .filter(JoinAccountStudy.account_id == account.id)\
            .all()

    except Exception as e:
        exc = traceback.format_exc()
        logger.warning(exc)

        return make_response({"msg": "Query failed due to internal server error."}, 500)

    # get all users for the studies that were returned earlier
    prefixes = [s.ditti_id for s in studies]

    # If no studies were found, return an empty list
    if not prefixes:
        return jsonify([])

    query = reduce(f, prefixes, "")
    users = Query("User", query).scan()["Items"]
    res = map(map_users, users)

    return jsonify(list(res))


@blueprint.route("/user/create", methods=["POST"])
@researcher_auth_required("View", "Ditti App Dashboard")
@researcher_auth_required("Create", "Participants")
def user_create(account):
    """
    Create a new user

    Request Syntax
    --------------
    {
        app: 2,
        study: int,
        create: {
            exp_time: iso-formatted timestamp,
            tap_permission: boolean,
            team_email: str,
            user_permission_id: str,
            information: str
        }
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
        client = MutationClient()
        client.open_connection()
        client.set_mutation(
            "CreateUserPermissionInput",
            "createUserPermission",
            request.json.get("create")
        )

        client.post_mutation()

    except Exception as e:
        exc = traceback.format_exc()
        logger.warning(exc)

        return make_response({"msg": "User creation failed due to internal server error."}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/user/edit", methods=["POST"])
@researcher_auth_required("View", "Ditti App Dashboard")
@researcher_auth_required("Edit", "Participants")
def user_edit(account):
    """
    Edit an exisitng user

    Request Syntax
    --------------
    {
        app: 2,
        study: int,
        user_permission_id: str,
        edit: {
            exp_time: iso-formatted timestamp,
            tap_permission: boolean,
            team_email: str,
            user_permission_id: str,
            information: str
        }
    }

    All data in the request body are optional. Any attributes that are excluded
    from the request body will not be changed.

    Response syntax (200)
    ---------------------
    {
        msg: "User Successfully Edited" or
            "Invalid Ditti ID: ..." or
            "Invalid Ditti ID: ..." or
            "Ditti ID not found: ..."
    }

    Response syntax (500)
    ---------------------
    {
        msg: "User edit failed due to internal server error."
    }
    """
    msg = "User Successfully Edited"

    # Handle request.json whether it's a string or already parsed
    request_data = request.json
    if isinstance(request_data, str):
        request_data = json.loads(request_data)

    user_permission_id = request_data.get("user_permission_id")

    # check that the ditti id is valid
    if re.search(r"[^\dA-Za-z]", user_permission_id) is not None:
        return jsonify({"msg": "Invalid Ditti ID: %s" % user_permission_id})

    study_ditti_id = re.sub(r"[\d]+", "", user_permission_id)
    study_id = request_data.get("study")
    study = Study.query.get(study_id)

    # check that the study acronym of the ditti id is valid
    if study_ditti_id != study.ditti_id:
        return jsonify({"msg": "Invalid Ditti ID: %s" % study_ditti_id})

    query = "user_permission_id==\"%s\"" % user_permission_id
    res = Query("User", query).scan()

    # if the ditti id does not exist
    if not res["Items"]:
        return jsonify({"msg": "Ditti ID not found: %s" % user_permission_id})

    try:
        updater = Updater("User")
        updater.set_key_from_query(query)
        updater.set_expression(request_data.get("edit"))
        updater.update()

    except Exception as e:
        exc = traceback.format_exc()
        logger.warning(exc)

        return make_response({"msg": "User edit failed due to internal server error."}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/get-audio-files")
@researcher_auth_required("View", "Ditti App Dashboard")
@researcher_auth_required("View", "Audio Files")
def get_audio_files(account):  # TODO update unit test
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
    res = []

    try:
        result = Query("AudioFile").scan()["Items"]
        for item in result:

            # Skip deleted audio files
            try:
                if item["_deleted"]:
                    continue
            except KeyError:
                pass

            audio_file = dict()
            try:
                audio_file["id"] = item["id"]
            except KeyError:
                pass
            try:
                audio_file["_version"] = item["_version"]
            except KeyError:
                pass
            try:
                audio_file["fileName"] = item["fileName"]
            except KeyError:
                pass
            try:
                audio_file["title"] = item["title"]
            except KeyError:
                pass
            try:
                audio_file["category"] = item["category"]
            except KeyError:
                pass
            try:
                audio_file["availability"] = item["availability"]
            except KeyError:
                pass
            try:
                audio_file["studies"] = item["studies"]
            except KeyError:
                pass
            try:
                audio_file["length"] = int(item["length"])
            except KeyError:
                pass
            res.append(audio_file)

    except Exception as e:
        exc = traceback.format_exc()
        logger.warning(exc)
        return make_response({"msg": "Query failed due to internal server error."}, 500)

    return jsonify(res)


@blueprint.route("/audio-file/create", methods=["POST"])
@researcher_auth_required("View", "Ditti App Dashboard")
@researcher_auth_required("Create", "Audio File")
def audio_file_create(account):
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
        items = request.json.get("create")

        # Add the bucket name the mutation body
        for item in items:
            item["bucket"] = current_app.config["AWS_AUDIO_FILE_BUCKET"]

        client = MutationClient()
        client.open_connection()
        client.set_mutation_v2(items)
        res = client.post_mutation()
        data = json.loads(res)

        if "data" not in data or not data["data"]:
            raise Exception(data["errors"][0]["message"])

    except Exception as e:
        exc = traceback.format_exc()
        logger.warning(exc)
        return make_response({"msg": "Creation of audio file failed due to internal server error."}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/audio-file/delete", methods=["POST"])
@researcher_auth_required("View", "Ditti App Dashboard")
@researcher_auth_required("Delete", "Audio File")
def audio_file_delete(account):
    """
    Permanently deletes an audio file. This endpoint first deletes the audio
    file from S3 then deletes the audio file from DynamoDB. If the deletion from
    S3 fails, the audio file is not deleted from DynamoDB.

    Request syntax
    --------------
    {
        app: 2,
        id: str,
        _version: int
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

        # Get the audio file
        audio_file_id = request.json["id"]
        version = request.json["_version"]
        audio_file = Query("AudioFile", f"id==\"{audio_file_id}\"").scan()[
            "Items"][0]

        # Try deleting the audio file from S3
        try:
            key = audio_file["fileName"]
            bucket = os.getenv("AWS_AUDIO_FILE_BUCKET")
            client = boto3.client("s3")
            deleted = client.delete_object(Bucket=bucket, Key=key)[
                "DeleteMarker"]

            # Return an error if the audio file was not deleted
            if not deleted:
                msg = "Audio file not deleted"
                return make_response({"msg": msg}, 500)

        # Automatically delete entries with no fileName
        except KeyError:
            pass

        # Delete the audio file from DynamoDB
        client = MutationClient()
        client.open_connection()
        client.set_mutation(
            "DeleteAudioFileInput",
            "deleteAudioFile",
            {"id": audio_file_id, "_version": int(version)}
        )

        client.post_mutation()

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        return make_response({"msg": "Deletion of audio file failed due to internal server error."}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/audio-file/get-presigned-urls", methods=["POST"])
@researcher_auth_required("View", "Ditti App Dashboard")
@researcher_auth_required("Create", "Audio File")
def audio_file_generate_presigned_urls(account):
    """
    Generates a list of presigned URLs for a given set of files. The request
    body must include a key for uploading to S3 and its MIME type.

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
    try:
        client = boto3.client("s3")
        files = request.json["files"]
        urls = []

        for file in files:
            presigned_url = client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": current_app.config["AWS_AUDIO_FILE_BUCKET"],
                    "Key": file["key"],
                    "ContentType": file["type"]
                },
                ExpiresIn=3600,
            )
            urls.append(presigned_url)

        return jsonify({"urls": urls})

    except NoCredentialsError:
        return jsonify({"msg": "AWS credentials not available"}), 500

    except ClientError:
        return jsonify({"msg": "Unknown error while generating presigned URLs"}), 500
