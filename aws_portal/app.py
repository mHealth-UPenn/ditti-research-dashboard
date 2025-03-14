from logging.config import dictConfig
import os

from flask import Flask, Response, request

from aws_portal.commands import (
    init_admin_app_click, init_admin_group_click, init_admin_account_click,
    init_db_click, init_api_click, init_integration_testing_db_click, reset_db_click,
    init_study_subject_click, clear_cache_click, init_lambda_task_click,
    delete_lambda_tasks_click, export_accounts_to_cognito_click
)
from aws_portal.extensions import bcrypt, cors, db, jwt, migrate, cache, tm, oauth
from aws_portal.views import (
    admin, aws_requests, base, data_processing_task, db_requests,
    participant, fitbit_data
)
from aws_portal.views.auth import participant_auth_blueprint, researcher_auth_blueprint
from aws_portal.views.api import fitbit


dictConfig({
    "version": 1,
    "formatters": {"default": {
        "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    }},
    "handlers": {"wsgi": {
        "class": "logging.StreamHandler",
        "stream": "ext://flask.logging.wsgi_errors_stream",
        "formatter": "default"
    }},
    "root": {
        "level": "INFO",
        "handlers": ["wsgi"]
    }
})


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

    # @app.before_request
    # def log_request():

    @app.after_request
    def log_response(response: Response):
        app.logger.info(f"Request: [{request.method}] {
                        request.url} {response.status}")
        return response

    return app


def register_blueprints(app):
    app.register_blueprint(admin.blueprint)
    app.register_blueprint(aws_requests.blueprint)
    app.register_blueprint(base.blueprint)
    app.register_blueprint(db_requests.blueprint)
    app.register_blueprint(participant_auth_blueprint)
    app.register_blueprint(researcher_auth_blueprint)
    app.register_blueprint(fitbit.blueprint)
    app.register_blueprint(participant.blueprint)
    app.register_blueprint(data_processing_task.blueprint)
    app.register_blueprint(fitbit_data.admin_fitbit_blueprint)
    app.register_blueprint(fitbit_data.participant_fitbit_blueprint)


def register_commands(app):
    app.cli.add_command(init_admin_app_click)
    app.cli.add_command(init_admin_group_click)
    app.cli.add_command(init_admin_account_click)
    app.cli.add_command(init_db_click)
    app.cli.add_command(init_api_click)
    app.cli.add_command(init_integration_testing_db_click)
    app.cli.add_command(reset_db_click)
    app.cli.add_command(init_study_subject_click)
    app.cli.add_command(clear_cache_click)
    app.cli.add_command(init_lambda_task_click)
    app.cli.add_command(delete_lambda_tasks_click)
    app.cli.add_command(export_accounts_to_cognito_click)


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
    tm.init_app(app)
    oauth.init_app(app)
    # scheduler.init_app(app)
    # scheduler.start()
    cache.init_app(app)
