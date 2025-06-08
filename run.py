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
from logging.config import dictConfig

from dotenv import load_dotenv

from shared.secrets import get_secret

load_dotenv(override=True)

# Set up logging before importing the app
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

# if the app is running in a production environment
if os.getenv("FLASK_CONFIG") in {"Production", "Staging"}:
    # In a deployed environment, secrets are managed by AWS Secrets Manager.
    secret_id = os.getenv("AWS_SECRET_NAME")
    if secret_id:
        secret = get_secret(secret_id).secret_dict

        # Export the secret's values as environment variables
        for k, v in secret.items():
            os.environ[k] = str(v)

# import the app after the environment variables are exported
from backend.app import create_app  # noqa: E402

# NOTE: Zappa wraps the app object in production-ready WSGI middleware
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
