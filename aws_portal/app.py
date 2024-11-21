from datetime import datetime, timedelta, timezone, UTC
import json
import os
from flask import Flask, Response
from flask_jwt_extended.utils import create_access_token, current_user, get_jwt
from aws_portal.commands import (
    init_admin_app_click, init_admin_group_click, init_admin_account_click,
    init_db_click, init_api_click, init_integration_testing_db_click, reset_db_click,
    init_demo_db_click
)
from aws_portal.extensions import bcrypt, cors, db, jwt, migrate
from aws_portal.views import admin, aws_requests, base, db_requests, iam, participant
from aws_portal.views.cognito import cognito, fitbit


def create_app(testing=False):
    # set the static folder as the react frontend
    app = Flask(__name__, static_url_path="", static_folder="frontend/build")

    if testing:
        flask_config = "Testing"
    else:
        flask_config = os.getenv("FLASK_CONFIG", "Default")

    # configure and initialize the app
    app.config.from_object("aws_portal.config.%s" % flask_config)
    register_blueprints(app)
    register_commands(app)
    register_extensions(app)

    # after each request refresh JWTs that expire within 15 minutes
    @app.after_request
    def refresh_expiring_jwts(response: Response):
        try:
            exp_timestamp = get_jwt()["exp"]
            now = datetime.now(timezone.utc)
            exp = now + timedelta(minutes=15)
            target_timestamp = int(datetime.timestamp(exp))

            # if the user"s JWT expires within 15 minutes
            if target_timestamp > exp_timestamp:

                # create a new token for the user
                access_token = create_access_token(current_user)
                data = response.json
                data["jwt"] = access_token
                response.data = json.dumps(data)

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
    app.register_blueprint(cognito.blueprint)
    app.register_blueprint(fitbit.blueprint)
    app.register_blueprint(participant.blueprint)


def register_commands(app):
    app.cli.add_command(init_admin_app_click)
    app.cli.add_command(init_admin_group_click)
    app.cli.add_command(init_admin_account_click)
    app.cli.add_command(init_db_click)
    app.cli.add_command(init_api_click)
    app.cli.add_command(init_integration_testing_db_click)
    app.cli.add_command(reset_db_click)
    app.cli.add_command(init_demo_db_click)


def register_extensions(app):
    bcrypt.init_app(app)
    cors.init_app(
        app,
        origins=app.config.get("CORS_ORIGINS", "*"),
        allow_headers=app.config.get("CORS_ALLOW_HEADERS", ["Content-Type"]),
        supports_credentials=app.config.get("CORS_SUPPORTS_CREDENTIALS", True)
    )
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
