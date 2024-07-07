from datetime import datetime, timedelta, timezone
import os
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from flask_jwt_extended.utils import (
    create_access_token, current_user, get_jwt, set_access_cookies
)
from aws_portal.commands import (
    init_admin_app_click, init_admin_group_click, init_admin_account_click,
    init_db_click
)
from aws_portal.extensions import bcrypt, db, jwt, migrate
from aws_portal.views import admin, aws_requests, base, db_requests, iam


def create_app(testing=False):
    if testing:
        flask_config = 'Testing'

    else:
        flask_config = os.getenv('FLASK_CONFIG', 'Development')

    # set the static folder as the react frontend
    app = Flask(__name__, static_url_path='', static_folder='frontend/build')

    # configure CORS
    CORS(
      app,
      allow_headers=['Authorization', 'Content-Type', 'X-CSRF-Token'],
      origins=os.getenv('AWS_CLOUDFRONT_DOMAIN_NAME', 'http://localhost:3000'),
      supports_credentials=True
    )

    # configure and initialize the app
    app.config.from_object('aws_portal.config.%s' % flask_config)
    register_blueprints(app)
    register_commands(app)
    register_extensions(app)

    # after each request refresh JWTs that expire within 15 minutes
    @app.after_request
    def refresh_expiring_jwts(response):
        try:
            exp_timestamp = get_jwt()['exp']
            now = datetime.now(timezone.utc)
            exp = now + timedelta(minutes=15)
            target_timestamp = int(datetime.timestamp(exp))

            # if the user's JWT expires within 15 minutes
            if target_timestamp > exp_timestamp:

                # create a new token for the user
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
    app.cli.add_command(init_admin_app_click)
    app.cli.add_command(init_admin_group_click)
    app.cli.add_command(init_admin_account_click)
    app.cli.add_command(init_db_click)


def register_extensions(app):
    bcrypt.init_app(app)
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
