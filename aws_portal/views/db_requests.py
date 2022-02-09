from flask import Blueprint, jsonify
from flask_jwt_extended import current_user, jwt_required
from aws_portal.models import AccessGroup, App, JoinAccountAccessGroup

blueprint = Blueprint('db', __name__, url_prefix='/db')


@blueprint.route('/apps')
@jwt_required()
def apps():
    app = App.query\
        .join(AccessGroup, AccessGroup.app_id == App.id)\
        .join(JoinAccountAccessGroup)\
        .filter(JoinAccountAccessGroup.account_id == current_user.id)\
        .all()

    return jsonify([a.meta for a in app])


@blueprint.route('/studies')
def studies():
    return jsonify({})


@blueprint.route('/study-details')
def study_details():
    return jsonify({})


@blueprint.route('/study-contacts')
def study_contacts():
    return jsonify({})


@blueprint.route('/account-details')
def account_details():
    return jsonify({})
