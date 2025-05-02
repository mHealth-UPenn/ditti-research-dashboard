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
from datetime import datetime, timedelta

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def stop():
    """
    Check for recent activity and stop RDS instance if inactive.

    Retrieves HTTP request logs from CloudWatch and checks for activity
    in the past two hours. If no activity is detected, checks the status
    of the RDS instance and stops it if it's running.

    Returns
    -------
    None
    """
    logs = boto3.client("logs")

    # get all HTTP requests from the last two hours
    name = os.getenv("AWS_LOG_GROUP_NAME")
    pattern = os.getenv("AWS_LOG_PATTERN")
    start = int((datetime.now() - timedelta(hours=2)).timestamp() * 1000)
    res = logs.filter_log_events(
        logGroupName=name, filterPattern=pattern, startTime=start
    )
    events = res["events"]

    # iteratively get all log events
    while "nextToken" in res:
        res = logs.filter_log_events(
            logGroupName=name,
            filterPattern=pattern,
            nextToken=res["nextToken"],
            startTime=start,
        )
        events.extend(res["events"])

    logger.info(f"Current time: {datetime.now()}")

    # if there was a request in the last two hours
    if events:
        # log the timestamp of the last event
        timestamps = (event["timestamp"] for event in events)
        last = sorted(timestamps)[-1]
        last = datetime.fromtimestamp(last // 1000)

        logger.info(f"Last request timestamp: {last}")

    else:
        logger.info("No requests in the last two hours")

        # get the database"s status
        rds = boto3.client("rds")
        instance = os.getenv("AWS_DB_INSTANCE_IDENTIFIER")
        res = rds.describe_db_instances(DBInstanceIdentifier=instance)
        status = res["DBInstances"][0]["DBInstanceStatus"]

        logger.info(f"Current DB status: {status}")

        # if the database is running
        if status == "available":
            logger.info(f"Stopping DB instance: {instance}")

            # stop the database
            rds.stop_db_instance(DBInstanceIdentifier=instance)


if __name__ == "__main__":
    logger = logging
    stop()
