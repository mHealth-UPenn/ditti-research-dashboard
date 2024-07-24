from functools import reduce
import logging
import re
import traceback
from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import current_user
import pandas as pd
from aws_portal.models import JoinAccountStudy, Study
from aws_portal.utils.auth import auth_required
from aws_portal.utils.aws import MutationClient, Query, Updater

blueprint = Blueprint("aws", __name__, url_prefix="/aws")
logger = logging.getLogger(__name__)


@blueprint.route("/scan")
@auth_required("View", "Ditti App Dashboard")
def scan():  # TODO update unit test
    """
    Query a dynamodb table

    Options
    -------
    app: 2
    key: str 
        The short name of the table (User, Tap, etc.)
    query: str (optional)
        The expression to query the table with, for example:
            "(a=="a"ORa=="b")AND(b=="a"AND(b=="b"ORb=="c"))"
        Valid conditionals include:
            == - equals
            != - not equals
            <= - less than or equal to
            >= - greater than or equal to
            << - less than
            >> - greater than
            BETWEEN - between two values, e.g., "fooBETWEEN"bar""baz""
            BEGINS - will return results that begin with a given value
            CONTAINS - will return results that contain a given value
            ~~ - will return results that are true
            ~ - will return results that are false
        Expressions are evaluated by paranthetical sub-expressions first, then
        from left to right. Expressions can only contain these characters:
            a-zA-Z0-9_-=":.<>()~!
    
    Response Syntax (200)
    ---------------------
    [
        ...Table data
    ]

    Response Syntax (200)
    ---------------------
    {
        msg: "Invalid Query"
    }
    """
    key = request.args.get("key")
    query = request.args.get("query")

    if re.search(Query.invalid_chars, query) is not None:
        return jsonify({"msg": "Invalid Query"})

    res = Query(key, query).scan()
    return jsonify(res["Items"])


@blueprint.route("/get-taps")
@auth_required("View", "Ditti App Dashboard")
@auth_required("View", "Taps")
def get_taps():  # TODO update unit test
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
        msg: a formatted traceback if an uncaught error was thrown
    }
    """

    # add expressions to the query to return all taps for multiple studies
    def f(left, right):
        q = "user_permission_idBEGINS\"%s\"" % right
        return left + ("OR" if left else "") + q

    try:

        # if the user has permission to view all studies, get all users
        app_id = request.args["app"]
        permissions = current_user.get_permissions(app_id)
        current_user.validate_ask("View", "All Studies", permissions)
        users = Query("User").scan()["Items"]

    except ValueError:

        # get users only for the studies the user as access to
        studies = Study.query\
            .join(JoinAccountStudy)\
            .filter(JoinAccountStudy.account_id == current_user.id)\
            .all()

        prefixes = [s.ditti_id for s in studies]
        query = reduce(f, prefixes, "")
        users = Query("User", query).scan()["Items"]

    except Exception as e:
        exc = traceback.format_exc()
        logger.warn(exc)
        msg = "Query failed: %s" % e

        return make_response({"msg": msg}, 500)

    # get all taps
    taps = Query("Tap").scan()["Items"]

    df_users = pd.DataFrame(users, columns=["id", "user_permission_id"])\
        .rename(columns={"user_permission_id": "dittiId"})

    df_taps = pd.DataFrame(taps, columns=["tapUserId", "time", "timeZone"])\
        .rename(columns={"tapUserId": "id"})

    # merge on only the users that were returned earlier
    res = pd.merge(df_users, df_taps, on="id")\
        .drop("id", axis=1)\
        .to_dict("records")

    return jsonify(res)


@blueprint.route("/get-users")
@auth_required("View", "Ditti App Dashboard")
@auth_required("View", "Users")
def get_users():  # TODO: create unit test
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
        msg: a formatted traceback if an uncaught error was thrown
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
        permissions = current_user.get_permissions(app_id)
        current_user.validate_ask("View", "All Studies", permissions)
        users = Query("User").scan()["Items"]
        res = map(map_users, users)

        return jsonify(list(res))

    except ValueError:

        # get only the studies the user has access to
        studies = Study.query\
            .join(JoinAccountStudy)\
            .filter(JoinAccountStudy.account_id == current_user.id)\
            .all()

    except Exception as e:
        exc = traceback.format_exc()
        logger.warn(exc)
        msg = "Query failed: %s" % e

        return make_response({"msg": msg}, 500)

    # get all users for the studies that were returned earlier
    prefixes = [s.ditti_id for s in studies]
    query = reduce(f, prefixes, "")
    users = Query("User", query).scan()["Items"]
    res = map(map_users, users)

    return jsonify(list(res))


@blueprint.route("/user/create", methods=["POST"])
@auth_required("View", "Ditti App Dashboard")
@auth_required("Create", "Users")
def user_create():
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
        msg: a formatted traceback if an uncaught error was thrown
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
        logger.warn(exc)
        msg = "User creation failed: %s" % e

        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/user/edit", methods=["POST"])
@auth_required("View", "Ditti App Dashboard")
@auth_required("Edit", "Users")
def user_edit():
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
            "Invalid study acronym: ..." or
            "Ditti ID not found: ..."
    }

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    msg = "User Successfully Edited"
    user_permission_id = request.json.get("user_permission_id")

    # check that the ditti id is valid
    if re.search(r"[^\dA-Za-z]", user_permission_id) is not None:
        return jsonify({"msg": "Invalid Ditti ID: %s" % user_permission_id})

    acronym = re.sub(r"[\d]+", "", user_permission_id)
    study_id = request.json.get("study")
    study = Study.query.get(study_id)

    # check that the study acronym of the ditti id is valid
    if acronym != study.ditti_id:
        return jsonify({"msg": "Invalid study acronym: %s" % acronym})

    query = "user_permission_id==\"%s\"" % user_permission_id
    res = Query("User", query).scan()

    # if the ditti id does not exist
    if not res["Items"]:
        return jsonify({"msg": "Ditti ID not found: %s" % user_permission_id})

    try:
        updater = Updater("User")
        updater.set_key_from_query(query)
        updater.set_expression(request.json.get("edit"))
        updater.update()

    except Exception as e:
        exc = traceback.format_exc()
        logger.warn(exc)
        msg = "User Edit Failed: %s" % e

        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg})
