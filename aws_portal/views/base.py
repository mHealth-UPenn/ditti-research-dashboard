import logging
import os
import traceback
from flask import (
  Blueprint, current_app, jsonify, make_response, send_from_directory
)
from aws_portal.extensions import db

blueprint = Blueprint('base', __name__)
logger = logging.getLogger(__name__)


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
        rds_res = client.describe_db_instances(DBInstanceIdentifier=rds_id)
        status = rds_res['DBInstances'][0]['DBInstanceStatus']

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
            exc = traceback.format_exc()
            msg = exc.splitlines()[-1]
            logger.warn(exc)

            return make_response({'msg': msg}, 500)

    return jsonify(res)
