import logging
import traceback

from flask import Blueprint, jsonify, make_response, request
from sqlalchemy.sql import tuple_

from aws_portal.extensions import db
from aws_portal.models import (
    AboutSleepTemplate, AccessGroup, Account, App, JoinAccountAccessGroup,
    JoinAccountStudy, Study
)
from aws_portal.auth.decorators import researcher_auth_required
from aws_portal.utils.db import populate_model

blueprint = Blueprint("db", __name__, url_prefix="/db")
logger = logging.getLogger(__name__)


@blueprint.route("/get-apps")
@researcher_auth_required
def get_apps(account):
    apps = App.query\
        .join(AccessGroup, AccessGroup.app_id == App.id)\
        .join(JoinAccountAccessGroup)\
        .filter(JoinAccountAccessGroup.account_id == account.id)\
        .all()

    return jsonify([a.meta for a in apps])


@blueprint.route("/get-studies")
@researcher_auth_required("View", "Ditti App Dashboard")
def get_studies(account):  # TODO rewrite unit test
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
@researcher_auth_required("View", "Ditti App Dashboard")
def get_study_details(account):
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
@researcher_auth_required("View", "Ditti App Dashboard")
def get_study_contacts(account):
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


@blueprint.route("/edit-account-details", methods=["POST"])
@researcher_auth_required("View", "Ditti App Dashboard")
def edit_account_details(account):
    """
    Edit the current user"s account details

    Request Syntax
    --------------
    {
        ...Account data,
        app: 2 (required) - The app ID is required for permission validation
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
        account_data = dict(request.json)
        if "app" in account_data:
            del account_data["app"]

        populate_model(account, account_data)
        db.session.commit()

        # Update Cognito user to keep account details in sync
        from aws_portal.auth.controllers.researcher import ResearcherAuthController
        auth_controller = ResearcherAuthController()
        success, message = auth_controller.update_account_in_cognito({
            "email": account.email,
            "first_name": account.first_name,
            "last_name": account.last_name,
            "phone_number": account.phone_number
        })

        if not success:
            return make_response({"msg": f"Account updated in database but failed to update in Cognito: {message}"}, 400)

        msg = "Account details updated successfully"

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when editing account details."}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/get-about-sleep-templates")
@researcher_auth_required("View", "Ditti App Dashboard")
def get_about_sleep_templates(account):
    """
    Get all about sleep templates

    Options
    -------
    app: 2 | 3 (required) - The app ID is required for permission validation

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
        # Extract all non-archived sleep templates
        about_sleep_templates = AboutSleepTemplate.query.filter(
            ~AboutSleepTemplate.is_archived
        ).all()

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        return make_response({"msg": "Internal server error when retrieving about sleep templates."}, 500)

    res = [a.meta for a in about_sleep_templates]
    return jsonify(res)
