from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy.sql import tuple_
from aws_portal.models import (
    AccessGroup, App, JoinAccessGroupStudy, JoinAccountAccessGroup,
    JoinAccountStudy, Study
)

blueprint = Blueprint('db', __name__, url_prefix='/db')


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
def get_studies():
    access_group_id = request.args['group']

    studies = Study.query\
        .join(JoinAccessGroupStudy)\
        .filter(JoinAccessGroupStudy.access_group_id == access_group_id)\
        .join(JoinAccountStudy)\
        .filter(JoinAccountStudy.account_id == current_user.id)\
        .all()

    return jsonify([s.meta for s in studies])


@blueprint.route('/get-study-details')
@jwt_required()
def get_study_details():
    study_id = request.args['study']
    study = Study.query\
        .join(JoinAccountStudy)\
        .filter(
            JoinAccountStudy.primary_key == tuple_(current_user.id, study_id)
        )\
        .first()

    res = study.meta if study is not None else {}
    return jsonify(res)


@blueprint.route('/get-study-contacts')
def get_study_contacts():
    return jsonify({})


@blueprint.route('/get-account-details')
def get_account_details():
    return jsonify({})
