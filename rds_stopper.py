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

import logging
import os
from datetime import datetime, timedelta

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def stop():
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
        timestamps = map(lambda x: x["timestamp"], events)
        last = sorted(list(timestamps))[-1]
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
