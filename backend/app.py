# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may]
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os

from flask import Flask, Response, request

from backend.commands import (
    clear_cache_click,
    create_researcher_account_click,
    delete_lambda_tasks_click,
    init_admin_account_click,
    init_admin_app_click,
    init_admin_group_click,
    init_api_click,
    init_db_click,
    init_integration_testing_db_click,
    init_lambda_task_click,
    init_study_subject_click,
    reset_db_click,
)
from backend.extensions import cache, cors, db, jwt, migrate, oauth, tm
from backend.views import (
    admin,
    aws_requests,
    base,
    data_processing_task,
    db_requests,
    fitbit_data,
    participant,
)
from backend.views.api import fitbit
from backend.views.api.auth import blueprint as api_auth_blueprint
from backend.views.auth import (
    participant_auth_blueprint,
    researcher_auth_blueprint,
)


def create_app(testing=False):
    """
    Create and configure the Flask application.

    Parameters
    ----------
        testing (bool): Flag to indicate if app should use testing configuration.

    Returns
    -------
        Flask: Configured Flask application.
    """
    app = Flask(__name__)

    flask_config = "Testing" if testing else os.getenv("FLASK_CONFIG", "Default")

    # configure and initialize the app
    app.config.from_object(f"backend.config.{flask_config}")
    register_blueprints(app)
    register_commands(app)
    register_extensions(app)

    @app.after_request
    def log_response(response: Response):
        app.logger.info(
            f"Request: [{request.method}] {request.url} {response.status}"
        )
        return response

    @app.after_request
    def add_security_headers(response: Response):
        """Add security headers to every response."""
        # Content Security Policy - restrict sources of content
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; font-src 'self';"
        )
        # X-Content-Type-Options - prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # X-Frame-Options - prevents site from being framed and clickjacked
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        # Strict-Transport-Security - force HTTPS (in production)
        if not app.debug and not app.testing:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response

    return app


def register_blueprints(app):
    """
    Register all blueprint routes with the application.

    Parameters
    ----------
        app (Flask): The Flask application instance.
    """
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
    app.register_blueprint(api_auth_blueprint)


def register_commands(app):
    """
    Register CLI commands with the application.

    Parameters
    ----------
        app (Flask): The Flask application instance.
    """
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
    app.cli.add_command(create_researcher_account_click)


def register_extensions(app):
    """
    Initialize and register Flask extensions with the application.

    Parameters
    ----------
        app (Flask): The Flask application instance.
    """
    cors.init_app(
        app,
        origins=app.config.get("CORS_ORIGINS", "*"),
        allow_headers=app.config.get("CORS_ALLOW_HEADERS"),
        expose_headers=app.config.get("CORS_EXPOSE_HEADERS"),
        supports_credentials=app.config.get("CORS_SUPPORTS_CREDENTIALS", True),
    )
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    tm.init_app(app)
    oauth.init_app(app)
    cache.init_app(app)
