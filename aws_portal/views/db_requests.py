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
from aws_portal.utils.db import populate_model

blueprint = Blueprint('db', __name__, url_prefix='/db')
logger = logging.getLogger(__name__)


@blueprint.route('/get-apps')
@jwt_required()
def get_apps():
    apps = App.query\
        .join(AccessGroup, AccessGroup.app_id == App.id)\
        .join(JoinAccountAccessGroup)\
        .filter(JoinAccountAccessGroup.account_id == current_user.id)\
        .all()

    return jsonify([a.meta for a in apps])


@blueprint.route('/get-studies')
@jwt_required()
def get_studies():  # TODO rewrite unit test
    try:
        app_id = request.args['app']
        permissions = current_user.get_permissions(app_id)
        current_user.validate_ask('View', 'All Studies', permissions)
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

        return make_response({'msg': msg}, 500)

    res = [s.meta for s in q.all()]
    return jsonify(res)


@blueprint.route('/get-study-details')
@jwt_required()
def get_study_details():
    study_id = request.args['study']
    app_id = request.args['app']

    try:
        permissions = current_user.get_permissions(app_id)
        current_user.validate_ask('View', 'All Studies', permissions)
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


@blueprint.route('/get-study-contacts')
@jwt_required()
def get_study_contacts():
    study_id = request.args['study']
    app_id = request.args['app']

    try:
        permissions = current_user.get_permissions(app_id)
        current_user.validate_ask('View', 'All Studies', permissions)
        study = Study.query.get(study_id)

    except ValueError:
        study = Study.query\
            .join(JoinAccountStudy)\
            .filter(
                JoinAccountStudy.primary_key == tuple_(
                    current_user.id, study_id
                )
            ).first()

    res = []
    if study is None:
        return jsonify(res)

    joins = JoinAccountStudy.query\
        .filter(JoinAccountStudy.study_id == study_id)\
        .join(Account)\
        .filter(~Account.is_archived)\
        .all()

    for join in joins:
        account = {
            'fullName': join.account.full_name,
            'email': join.account.email,
            'phoneNumber': join.account.phone_number,
            'role': join.role.name
        }

        res.append(account)

    return jsonify(res)


@blueprint.route('/get-account-details')
@jwt_required()
def get_account_details():
    res = {
        'firstName': current_user.first_name,
        'lastName': current_user.last_name,
        'email': current_user.email,
        'phoneNumber': current_user.phone_number
    }

    return jsonify(res)


@blueprint.route('/edit-account-details', methods=['POST'])
@jwt_required()
def edit_account_details():
    try:
        populate_model(current_user, request.json)
        db.session.commit()
        msg = 'Account details updated successfully'

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)

    return jsonify({'msg': msg})


@blueprint.route('/get-about-sleep-templates')
@jwt_required()
def get_about_sleep_templates():
    try:
        about_sleep_templates = AboutSleepTemplate.query.filter(
            ~AboutSleepTemplate.is_archived
        )

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)

        return make_response({'msg': msg}, 500)

    res = [a.meta for a in about_sleep_templates]
    return jsonify(res)
