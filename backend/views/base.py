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

import logging
import os
import traceback

from flask import Blueprint, current_app, jsonify, make_response
from sqlalchemy import text

from backend.extensions import db
from backend.utils.lambda_task import check_and_invoke_lambda_task

blueprint = Blueprint("base", __name__)
logger = logging.getLogger(__name__)


@blueprint.route("/health")
def health_check():
    """
    Health check endpoint to verify the service is running.

    Response Syntax (200)
    ---------------------
    {
        msg: "Service is healthy."
    }

    Response syntax (500)
    ---------------------
    {
        msg: "Service is unhealthy."
    }
    """
    try:
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return jsonify({"msg": "Service is healthy."})
    except Exception:
        exc = traceback.format_exc()
        logger.error(exc)
        return make_response({"msg": "Service is unhealthy."}, 500)


@blueprint.route("/touch")
def touch():
    """
    Send an empty request to the server to see the status of the database.

    If the database was stopped, this will start the database. This returns OK
    if the database is running, STARTING if it was stopped or is current
    starting, or STATUS: ... if a different status arises.

    Response Syntax (200)
    ---------------------
    {
        msg: "OK" or
            "STARTING" or
            "STATUS: ..."
    }

    Response syntax (500)
    ---------------------
    {
        msg: "Internal server error when getting database status."
    }
    """
    res = {"msg": "OK"}
    available = True

    if current_app.config["ENV"] == "production":
        import boto3

        # get the database's status
        client = boto3.client("rds")
        rds_id = os.getenv("AWS_DB_INSTANCE_IDENTIFIER")
        rds_res = client.describe_db_instances(DBInstanceIdentifier=rds_id)
        status = rds_res["DBInstances"][0]["DBInstanceStatus"]

        if status != "available":
            available = False

            if status == "stopped":
                client.start_db_instance(DBInstanceIdentifier=rds_id)
                res["msg"] = "STARTING"

            elif status == "starting":
                res["msg"] = "STARTING"

            else:
                res["msg"] = f"STATUS: {status}"

    if available:
        # check that the database is healthy
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            # After confirming the database is available, retrieve sleep data
            check_and_invoke_lambda_task()

        except Exception:
            exc = traceback.format_exc()
            logger.warning(exc)

            return make_response(
                {"msg": "Internal server error when getting database status."},
                500,
            )

    return jsonify(res)
