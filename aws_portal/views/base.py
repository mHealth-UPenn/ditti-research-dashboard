import os
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
    available = True

    if current_app.config['ENV'] == 'production':
        import boto3
        client = boto3.client('rds')
        rds_id = os.getenv('AWS_DB_INSTANCE_IDENTIFIER')
        res = client.describe_db_instances(DBInstanceIdentifier=rds_id)
        status = res['DBInstances'][0]['DBInstanceStatus']

        if status != 'available':
            available = False

            if status == 'starting':
                res['msg'] = 'STARTING'

            else:
                res['msg'] = 'STATUS: %s' % status

    if available:
        try:
            db.engine.execute('SELECT 1')

        except Exception:
            res = {'msg': traceback.format_exc()}

    return jsonify(res)
