import traceback
from flask import Blueprint, current_app, jsonify, send_from_directory
from aws_portal.extensions import db

blueprint = Blueprint('base', __name__)


@blueprint.route('/')
def serve():
    return send_from_directory(current_app.static_folder, 'index.html')


@blueprint.route('/login')
def login():
    return send_from_directory(current_app.static_folder, 'index.html')


@blueprint.route('/healthy')
def healthy():
    res = {'msg': 'OK'}

    try:
        db.engine.execute('SELECT 1')

    except Exception:
        res = {'msg': traceback.format_exc()}

    return jsonify(res)
