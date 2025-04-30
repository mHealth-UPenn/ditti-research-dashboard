# Ditti Research Dashboard
# Copyright (C) 2025 the Trustees of the University of Pennsylvania
#
# Ditti Research Dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Ditti Research Dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
from logging.config import dictConfig

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
from backend.views.auth import (
    participant_auth_blueprint,
    researcher_auth_blueprint,
)

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)


def create_app(testing=False):
    app = Flask(__name__)

    if testing:
        flask_config = "Testing"
    else:
        flask_config = os.getenv("FLASK_CONFIG", "Default")

    # configure and initialize the app
    app.config.from_object("backend.config.%s" % flask_config)
    register_blueprints(app)
    register_commands(app)
    register_extensions(app)

    @app.after_request
    def log_response(response: Response):
        app.logger.info(
            f"Request: [{request.method}] {request.url} {response.status}"
        )
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
    app.cli.add_command(create_researcher_account_click)


def register_extensions(app):
    cors.init_app(
        app,
        origins=app.config.get("CORS_ORIGINS", "*"),
        allow_headers=app.config.get("CORS_ALLOW_HEADERS", ["Content-Type"]),
        supports_credentials=app.config.get("CORS_SUPPORTS_CREDENTIALS", True),
    )
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    tm.init_app(app)
    oauth.init_app(app)
    cache.init_app(app)
