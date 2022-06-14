from datetime import datetime, timedelta
import logging
import os
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def stop():
    logs = boto3.client('logs')
    streams = logs.describe_log_streams(
        logGroupName='/aws/lambda/aws-portal-app',
        orderBy='LastEventTime',
        descending=True
    )
    last = streams['logStreams'][0]['lastEventTimestamp']
    last = datetime.fromtimestamp(last // 1000)

    logger.info('Last event timestamp: %s' % last)
    logger.info('Current time: %s' % datetime.now())

    if last + timedelta(hours=2) < datetime.now():
        rds = boto3.client('rds')
        instance = os.getenv('AWS_DB_INSTANCE_IDENTIFIER')
        res = rds.describe_db_instances(DBInstanceIdentifier=instance)
        status = res['DBInstances'][0]['DBInstanceStatus']

        logger.info('Current DB status: %s' % status)

        if status == 'available':
            logger.info('Stopping DB instance: %s' % instance)
            rds.stop_db_instance(DBInstanceIdentifier=instance)


if __name__ == '__main__':
    logger = logging
    stop()
