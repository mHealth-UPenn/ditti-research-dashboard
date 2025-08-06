# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# Disable linter warnings for print statements (quick fix for logging issues with alembic)
# ruff: noqa: T201

import os
from typing import Any

import cfnresponse

from src.db_bootstrapper_agent import DBBootstrapperAgent


def lambda_handler(event: dict[str, Any], context: Any) -> None:
    """
    AWS Lambda handler function.

    Args:
        event: The CloudFormation event.
        context: The Lambda context.
    """
    print(f"Received event: {event}")

    # Determine if using local database
    local_db = os.getenv("LOCAL_DB", "false").lower() == "true"
    if local_db:
        print("Using local database! IAM authentication is disabled.")

    # Create agent and handle request
    agent = DBBootstrapperAgent(local_db=local_db)

    try:
        response_data = agent.handle_request(event)
        response = {"Data": response_data["Data"]}
        cfnresponse.send(event, context, cfnresponse.SUCCESS, response)
    except Exception as e:
        print(f"Error in lambda handler: {e}")
        response = {"Data": f"Error in lambda handler: {e}"}
        cfnresponse.send(event, context, cfnresponse.FAILED, response)
