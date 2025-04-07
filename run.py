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

# if the app is running in a production environment
if os.getenv("FLASK_CONFIG") in {"Production", "Staging"}:
    import json
    import boto3

    # get the secret"s values
    client = boto3.client("secretsmanager")
    secret_id = os.getenv("AWS_SECRET_NAME")
    res = client.get_secret_value(SecretId=secret_id)
    secret = json.loads(res["SecretString"])

    # export the secret"s values as envirnoment variables
    for k, v in secret.items():
        os.environ[k] = v

# import the app after the environment variables are exported
from aws_portal.app import create_app

# NOTE: Zappa wraps the app object in production-ready WSGI middleware
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)