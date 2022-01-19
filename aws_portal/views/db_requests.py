from flask import Blueprint, jsonify

blueprint = Blueprint('db', __name__, url_prefix='/db')


@blueprint.route('/apps')
def apps():
    return jsonify({})


@blueprint.route('/studies')
def studies():
    return jsonify({})
