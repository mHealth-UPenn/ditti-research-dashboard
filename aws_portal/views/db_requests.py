from flask import Blueprint, jsonify

blueprint = Blueprint('db', __name__, url_prefix='/db')


@blueprint.route('/apps')
def apps():
    return jsonify({})


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
