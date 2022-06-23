from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy.sql import tuple_
from aws_portal.models import (
    AccessGroup, Account, App, JoinAccountAccessGroup, JoinAccountStudy, Study
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
    app_id = request.args['app']

    studies = Study.query.join(JoinAccountStudy)\
        .filter(JoinAccountStudy.account_id == current_user.id)\
        .join(Account).join(JoinAccountAccessGroup).join(AccessGroup)\
        .filter(AccessGroup.app_id == app_id)\
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
        ).first()

    res = study.meta if study is not None else {}
    return jsonify(res)


@blueprint.route('/get-study-contacts')
@jwt_required()
def get_study_contacts():
    study_id = request.args['study']
    study = Study.query\
        .join(JoinAccountStudy)\
        .filter(
            JoinAccountStudy.primary_key == tuple_(current_user.id, study_id)
        ).first()

    res = []
    if study is None:
        return jsonify(res)

    joins = JoinAccountStudy.query.filter(
        JoinAccountStudy.study_id == study_id
    ).all()

    for join in joins:
        account = {
            'FullName': join.account.full_name,
            'Email': join.account.email,
            'PhoneNumber': None,
            'Role': join.role.name
        }

        res.append(account)

    return jsonify(res)


@blueprint.route('/get-account-details')
@jwt_required()
def get_account_details():
    res = {
        'FirstName': current_user.first_name,
        'LastName': current_user.last_name,
        'Email': current_user.email,
        'PhoneNumber': None
    }

    return jsonify(res)
