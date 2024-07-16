import logging
import traceback
from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy.sql import tuple_
from aws_portal.extensions import db
from aws_portal.models import (
    AboutSleepTemplate, AccessGroup, Account, App, JoinAccountAccessGroup,
    JoinAccountStudy, Study
)
# from aws_portal.utils.auth import auth_required
from aws_portal.utils.db import populate_model

blueprint = Blueprint("db", __name__, url_prefix="/db")
logger = logging.getLogger(__name__)


@blueprint.route("/get-apps")
@jwt_required()
def get_apps():
    apps = App.query\
        .join(AccessGroup, AccessGroup.app_id == App.id)\
        .join(JoinAccountAccessGroup)\
        .filter(JoinAccountAccessGroup.account_id == current_user.id)\
        .all()

    return jsonify([a.meta for a in apps])


@blueprint.route("/get-studies")
@jwt_required()
# @auth_required("View", "Ditti App Dashboard")
def get_studies():  # TODO rewrite unit test
    """
    Get the data of all studies that the user has access to

    Options
    -------
    app: 2

    Response Syntax (200)
    ---------------
    [
        {
            ...Study data
        },
        ...
    ]

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        app_id = request.args["app"]
        permissions = current_user.get_permissions(app_id)
        current_user.validate_ask("View", "All Studies", permissions)
        q = Study.query.filter(~Study.is_archived)

    except ValueError:
        q = Study.query\
            .filter(~Study.is_archived)\
            .join(JoinAccountStudy)\
            .filter(JoinAccountStudy.account_id == current_user.id)

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)

        return make_response({"msg": msg}, 500)

    res = [s.meta for s in q.all()]
    return jsonify(res)


@blueprint.route("/get-study-details")
@jwt_required()
# @auth_required("View", "Ditti App Dashboard")
def get_study_details():
    """
    Get the details of a given study

    Options
    -------
    app: 2
    study: int

    Response Syntax (200)
    ---------------------
    {
        ...Study data
    }
    """
    study_id = request.args["study"]
    app_id = request.args["app"]

    try:

        # if the user has permissions to view all studies, a join table might
        # not exist. Just get the study
        permissions = current_user.get_permissions(app_id)
        current_user.validate_ask("View", "All Studies", permissions)
        study = Study.query.get(study_id)

    except ValueError:
        study = Study.query\
            .join(JoinAccountStudy)\
            .filter(
                JoinAccountStudy.primary_key == tuple_(
                  current_user.id, study_id
                )
            ).first()

    res = study.meta if study is not None else {}
    return jsonify(res)


@blueprint.route("/get-study-contacts")
@jwt_required()
# @auth_required("View", "Ditti App Dashboard")
def get_study_contacts():
    """
    Get the contacts of a given study. This will return the contact information
    of only accounts that are explictly given access to a study. Accounts that
    can access a study through permission to view all studies only will not be
    included

    Options
    -------
    app: 2
    study: int

    Response Syntax (200)
    ---------------------
    [
        {
            fullName: str,
            email: str,
            phoneNumber: str,
            role: str
        },
        ...
    ]
    """
    study_id = request.args["study"]
    app_id = request.args["app"]

    try:

        # if the user has permissions to view all studies, a join table might
        # not exist. Just get the study
        permissions = current_user.get_permissions(app_id)
        current_user.validate_ask("View", "All Studies", permissions)
        study = Study.query.get(study_id)

    except ValueError:
        study = Study.query\
            .join(JoinAccountStudy)\
            .filter(
                JoinAccountStudy.primary_key == tuple_(
                    current_user.id, study_id
                )
            ).first()

    # if the user does not have access to the study, return an empty list
    res = []
    if study is None:
        return jsonify(res)

    # get all accounts that have access to this study
    joins = JoinAccountStudy.query\
        .filter(JoinAccountStudy.study_id == study_id)\
        .join(Account)\
        .filter(~Account.is_archived)\
        .all()

    for join in joins:
        account = {
            "fullName": join.account.full_name,
            "email": join.account.email,
            "phoneNumber": join.account.phone_number,
            "role": join.role.name
        }

        res.append(account)

    return jsonify(res)


@blueprint.route("/get-account-details")
@jwt_required()
# @auth_required("View", "Ditti App Dashboard")
def get_account_details():
    """
    Get the current user"s account details

    Response Syntax (200)
    ---------------------
    {
        firstName: str,
        lastName: str,
        email: str,
        phoneNumber: str
    }
    """
    res = {
        "firstName": current_user.first_name,
        "lastName": current_user.last_name,
        "email": current_user.email,
        "phoneNumber": current_user.phone_number
    }

    return jsonify(res)


@blueprint.route("/edit-account-details", methods=["POST"])
@jwt_required()
# @auth_required("View", "Ditti App Dashboard")
def edit_account_details():
    """
    Edit the current user"s account details

    Request Syntax
    --------------
    {
        ...Account data
    }

    All data in the request body are optional. Any attributes that are excluded
    from the request body will not be changed.

    Response Syntax (200)
    ---------------------
    {
        msg: "Account details updated successfully"
    }

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        populate_model(current_user, request.json)
        db.session.commit()
        msg = "Account details updated successfully"

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/get-about-sleep-templates")
@jwt_required()
# @auth_required("View", "Ditti App Dashboard")
def get_about_sleep_templates():
    """
    Get all about sleep templates

    Response Syntax (200)
    ---------------
    [
        {
            ...About sleep template data
        },
        ...
    ]

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        about_sleep_templates = AboutSleepTemplate.query.filter(
            ~AboutSleepTemplate.is_archived
        )

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)

        return make_response({"msg": msg}, 500)

    res = [a.meta for a in about_sleep_templates]
    return jsonify(res)
