from datetime import datetime, timedelta, timezone
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended.utils import (
    create_access_token, current_user, get_jwt, set_access_cookies
)
from aws_portal.commands import (
    init_admin_group_click, init_admin_account_click, init_db_click
)
from aws_portal.extensions import bcrypt, db, jwt, migrate
from aws_portal.views import admin, aws_requests, base, db_requests, iam


def create_app(testing=False):
    if testing:
        flask_config = 'Testing'

    else:
        flask_config = os.getenv('FLASK_CONFIG', 'Development')

    app = Flask(__name__, static_url_path='', static_folder='frontend/build')
    CORS(app)
    app.config.from_object('aws_portal.config.%s' % flask_config)

    if app.config['ENV'] == 'production':
        import boto3
        client = boto3.client('rds')
        rds_id = os.getenv('AWS_DB_INSTANCE_IDENTIFIER')
        res = client.describe_db_instances(DBInstanceIdentifier=rds_id)
        status = res['DBInstances'][0]['DBInstanceStatus']

        if status not in ['available', 'starting']:
            client.start_db_instance(DBInstanceIdentifier=rds_id)

    register_blueprints(app)
    register_commands(app)
    register_extensions(app)

    @app.after_request
    def refresh_expiring_jwts(response):
        try:
            exp_timestamp = get_jwt()['exp']
            now = datetime.now(timezone.utc)
            exp = now + timedelta(minutes=15)
            target_timestamp = datetime.timestamp(exp)

            if target_timestamp > exp_timestamp:
                access_token = create_access_token(current_user)
                set_access_cookies(response, access_token)

            return response

        except (RuntimeError, KeyError):
            return response

    return app


def register_blueprints(app):
    app.register_blueprint(admin.blueprint)
    app.register_blueprint(aws_requests.blueprint)
    app.register_blueprint(base.blueprint)
    app.register_blueprint(db_requests.blueprint)
    app.register_blueprint(iam.blueprint)


def register_commands(app):
    app.cli.add_command(init_admin_group_click)
    app.cli.add_command(init_admin_account_click)
    app.cli.add_command(init_db_click)


def register_extensions(app):
    bcrypt.init_app(app)
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app)
