import logging
import traceback
from flask import Blueprint, jsonify, make_response, request
from sqlalchemy.sql import tuple_
from aws_portal.extensions import db
from aws_portal.models import (
    AboutSleepTemplate, AccessGroup, Account, App, JoinAccountAccessGroup,
    JoinAccountStudy, Study
)
from aws_portal.utils.cognito.researcher.decorators import (
    researcher_auth_required, researcher_db_auth_required
)
from aws_portal.utils.db import populate_model

blueprint = Blueprint("db", __name__, url_prefix="/db")
logger = logging.getLogger(__name__)


@blueprint.route("/get-apps")
@researcher_auth_required
def get_apps(email=None):
    account = Account.query.filter_by(email=email, is_archived=False).first()
    apps = (
        App.query
        .join(AccessGroup, AccessGroup.app_id == App.id)
        .join(JoinAccountAccessGroup)
        .filter(JoinAccountAccessGroup.account_id == account.id)
        .all()
    )
    return jsonify([a.meta for a in apps])


@blueprint.route("/get-studies")
@researcher_auth_required
# @researcher_db_auth_required("View", "Ditti App Dashboard")
def get_studies(email=None):
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
        msg: "Internal server error when retrieving studies."
    }
    """
    try:
        app_id = request.args["app"]
        account = Account.query.filter_by(
            email=email, is_archived=False).first()
        permissions = account.get_permissions(app_id)
        account.validate_ask("View", "All Studies", permissions)
        q = Study.query.filter(~Study.is_archived)

    except ValueError:
        q = Study.query\
            .filter(~Study.is_archived)\
            .join(JoinAccountStudy)\
            .filter(JoinAccountStudy.account_id == account.id)

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)

        return make_response({"msg": "Internal server error when retrieving studies."}, 500)

    res = [s.meta for s in q.all()]
    return jsonify(res)


@blueprint.route("/get-study-details")
@researcher_auth_required
# @researcher_db_auth_required("View", "Ditti App Dashboard")
def get_study_details(email=None):
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
        account = Account.query.filter_by(
            email=email, is_archived=False).first()
        permissions = account.get_permissions(app_id)
        account.validate_ask("View", "All Studies", permissions)
        study = Study.query.get(study_id)

    except ValueError:
        study = Study.query\
            .join(JoinAccountStudy)\
            .filter(
                JoinAccountStudy.primary_key == tuple_(
                    account.id, study_id
                )
            ).first()

    res = study.meta if study is not None else {}
    return jsonify(res)


@blueprint.route("/get-study-contacts")
@researcher_auth_required
# @researcher_db_auth_required("View", "Ditti App Dashboard")
def get_study_contacts(email=None):
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
        account = Account.query.filter_by(
            email=email, is_archived=False).first()
        permissions = account.get_permissions(app_id)
        account.validate_ask("View", "All Studies", permissions)
        study = Study.query.get(study_id)

    except ValueError:
        study = Study.query\
            .join(JoinAccountStudy)\
            .filter(
                JoinAccountStudy.primary_key == tuple_(
                    account.id, study_id
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
@researcher_auth_required
# @researcher_db_auth_required("View", "Ditti App Dashboard")
def get_account_details(email=None):
    """
    Get the current user's account details

    Response Syntax (200)
    ---------------------
    {
        firstName: str,
        lastName: str,
        email: str,
        phoneNumber: str
    }
    """
    account = Account.query.filter_by(email=email, is_archived=False).first()
    if not account:
        return make_response({"msg": "Account not found"}, 404)
    res = {
        "firstName": account.first_name,
        "lastName": account.last_name,
        "email": account.email,
        "phoneNumber": account.phone_number
    }

    return jsonify(res)


@blueprint.route("/edit-account-details", methods=["POST"])
@researcher_auth_required
# @researcher_db_auth_required("View", "Ditti App Dashboard")
def edit_account_details(email=None):
    """
    Edit the current user's account details

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
        msg: "Internal server error when editing account details."
    }
    """
    try:
        account = Account.query.filter_by(
            email=email, is_archived=False).first()
        if not account:
            return make_response({"msg": "Account not found"}, 404)
        populate_model(account, request.json)
        db.session.commit()
        msg = "Account details updated successfully"

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when editing account details."}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/get-about-sleep-templates")
@researcher_auth_required
# @researcher_db_auth_required("View", "Ditti App Dashboard")
def get_about_sleep_templates(email=None):
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
        msg: "Internal server error when retrieving about sleep templates."
    }
    """
    try:
        about_sleep_templates = AboutSleepTemplate.query.filter(
            ~AboutSleepTemplate.is_archived
        )

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)

        return make_response({"msg": "Internal server error when retrieving about sleep templates."}, 500)

    res = [a.meta for a in about_sleep_templates]
    return jsonify(res)
