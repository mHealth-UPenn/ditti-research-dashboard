from datetime import datetime, timedelta, UTC
import logging
import os
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def stop():
    logs = boto3.client("logs")

    # get all HTTP requests from the last two hours
    name = "/aws/lambda/aws-portal-app"
    pattern = (
        "[level, utc, id, ip, user, username, timestamp, request=*HTTP*, sta" +
        "tus, bytes]"
    )
    start = int((datetime.now() - timedelta(hours=2)).timestamp() * 1000)
    res = logs.filter_log_events(
        logGroupName=name,
        filterPattern=pattern,
        startTime=start
    )
    events = res["events"]

    # iteratively get all log events
    while "nextToken" in res:
        res = logs.filter_log_events(
            logGroupName=name,
            filterPattern=pattern,
            nextToken=res["nextToken"],
            startTime=start
        )
        events.extend(res["events"])

    logger.info("Current time: %s" % datetime.now())

    # if there was a request in the last two hours
    if events:

        # log the timestamp of the last event
        timestamps = map(lambda x: x["timestamp"], events)
        last = sorted(list(timestamps))[-1]
        last = datetime.fromtimestamp(last // 1000)

        logger.info("Last request timestamp: %s" % last)

    else:
        logger.info("No requests in the last two hours")

        # get the database"s status
        rds = boto3.client("rds")
        instance = os.getenv("AWS_DB_INSTANCE_IDENTIFIER")
        res = rds.describe_db_instances(DBInstanceIdentifier=instance)
        status = res["DBInstances"][0]["DBInstanceStatus"]

        logger.info("Current DB status: %s" % status)

        # if the database is running
        if status == "available":
            logger.info("Stopping DB instance: %s" % instance)

            # stop the database
            rds.stop_db_instance(DBInstanceIdentifier=instance)


if __name__ == "__main__":
    logger = logging
    stop()
