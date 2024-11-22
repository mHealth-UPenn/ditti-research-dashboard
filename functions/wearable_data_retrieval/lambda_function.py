import boto3
from datetime import datetime
import json
import logging
import os
import sys
import time

import boto3
from sqlalchemy import create_engine, Table, MetaData, insert, select, update
from sqlalchemy.orm import aliased

from shared.fitbit import get_fitbit_oauth_session

TESTING = os.getenv("TESTING") is not None

# Use a common timestamp across the whole job
job_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

# Custom JSON formatter
class JsonFormatter(logging.Formatter):
    exclude = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "taskName"
    }

    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # Add any extra fields in record if they exist
        log_entry.update(
            {
                k: v for k, v in record.__dict__.items()
                if k not in self.exclude
            }
        )

        return json.dumps(log_entry, indent=4)

# Set up logger to write JSON log entries to a file
logger = logging.getLogger("logger")
logger.setLevel(logging.INFO)

# JSON Formatter
json_formatter = JsonFormatter()

# Stream handler for console output
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(json_formatter)
logger.addHandler(stream_handler)

# File handler for JSON log file output
log_filename = f"log_{job_timestamp}.json"
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(json_formatter)
logger.addHandler(file_handler)


def get_secret(secret_name):
    # Initialize a session using environment variables
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name=os.getenv("AWS_REGION")
    )

    try:
        # Fetch the secret
        response = client.get_secret_value(SecretId=secret_name)

        # Parse and return the secret
        if "SecretString" in response:
            secret = response["SecretString"]
            config = json.loads(secret)
        else:
            # Decode binary secret if it"s not a string
            config = json.loads(response["SecretBinary"].decode("utf-8"))

        logger.info(
            "Secret retrieved from SecretsManager",
            extra={"secret_name": secret_name, "num_keys": len(config.keys())}
        )

        return config

    except Exception as e:
        logger.error(f"Error retrieving secret: {e}")
        raise RuntimeError(e)


# Load secrets
config_secret_name = os.getenv("AWS_CONFIG_SECRET_NAME")
tokens_secret_name = os.getenv("AWS_KEYS_SECRET_NAME")
config = get_secret(config_secret_name)
tokens_config = get_secret(tokens_secret_name)


def handler(event, context):
    start_time = event["requestContext"]["timeEpoch"]  # Assuming start time comes from the event context in milliseconds
    logger.info("Starting wearable data retrieval job", extra={"job_timestamp": job_timestamp})

    # Retrieve function_id from the lambda function invocation event
    function_id = event.get("function_id")
    logger.info("Retrieved function_id", extra={"function_id": function_id})

    # Database connection setup
    db_uri = config["DB_URI"]
    engine = create_engine(db_uri)
    metadata = MetaData(bind=engine)

    # Reflect existing database into a new model
    metadata.reflect(only=["lambda_function"])
    
    # Access the `lambda_function` table
    lambda_function_table = Table("lambda_function", metadata, autoload_with=engine)

    # Query the table for the specific function_id and update status
    try:
        with engine.connect() as connection:
            # Retrieve the record
            query = select(lambda_function_table).where(lambda_function_table.c.id == function_id)
            result = connection.execute(query).first()
            
            if result:
                logger.info("Query result", extra=dict(result))
                
                # Update the status to "IN_PROGRESS"
                update_stmt = (
                    update(lambda_function_table).
                    where(lambda_function_table.c.id == function_id).
                    values(status="IN_PROGRESS")
                )
                connection.execute(update_stmt)
                connection.commit()
                logger.info("Updated status to IN_PROGRESS", extra={"function_id": function_id})

            else:
                logger.warning("No entry found for function_id", extra={"function_id": function_id})

    except Exception as e:
        logger.error("Error updating the database", extra={"error": str(e)})

    # Reflect existing tables into models
    metadata.reflect(only=["join_study_subject_api", "study_subject", "join_study_subject_study"])

    # Aliased tables for readability
    api = aliased(Table("join_study_subject_api", metadata, autoload_with=engine))
    subject = aliased(Table("study_subject", metadata, autoload_with=engine))
    study = aliased(Table("join_study_subject_study", metadata, autoload_with=engine))
    sleep_log_table = Table("sleep_log", metadata, autoload_with=engine)
    sleep_level_table = Table("sleep_level", metadata, autoload_with=engine)
    sleep_summary_table = Table("sleep_summary", metadata, autoload_with=engine)

    try:
        with engine.connect() as connection:
            # Perform the query with joins and conditions
            query = (
                select(
                    subject.c.id,
                    api.c.api_user_uuid,
                    api.c.last_sync_date,
                    study.c.expires_on
                )
                .select_from(api
                    .join(subject, api.c.study_subject_id == subject.c.id)
                    .join(study, subject.c.id == study.c.study_subject_id)
                )
                .where(study.c.expires_on > api.c.last_sync_date)
            )
            result = connection.execute(query).fetchall()

            # Log or process the result as needed
            logger.info("Fetched study subject API data", extra={"result_count": len(result)})

            # Iterate over each result to query the Fitbit API
            for entry in result:
                try:
                    # Retrieve OAuth tokens for the subject
                    subject_id = entry.id
                    tokens = tokens_config[subject_id]

                    # Initialize Fitbit OAuth session
                    fitbit_session = get_fitbit_oauth_session(entry, tokens)

                    # Construct the URL for Fitbit API call
                    user_id = entry.api_user_uuid
                    start_date = entry.last_sync_date.strftime("%Y-%m-%d")
                    end_date = min(entry.expires_on, datetime.strptime(job_timestamp, "%Y-%m-%d_%H:%M:%S")).strftime("%Y-%m-%d")

                    url = f"https://api.fitbit.com/1.2/user/{user_id}/sleep/date/{start_date}/{end_date}.json"
                    
                    # Query the Fitbit API
                    response = fitbit_session.request(url)
                    data = response.json()

                    logger.info("Fitbit API data retrieved", extra={"user_id": user_id, "data": data})

                except Exception as api_error:
                    error_code = "API_ERROR"
                    logger.error("Error querying the Fitbit API", extra={"error": str(api_error), "user_id": user_id})

                for sleep_record in data.get("sleep", []):
                    # Create sleep log entry
                    insert_stmt = insert(sleep_log_table).values(
                        study_subject_id=subject_id,
                        log_id=sleep_record["logId"],
                        date_of_sleep=datetime.strptime(sleep_record["dateOfSleep"], "%Y-%m-%d").date(),
                        duration=sleep_record["duration"],
                        efficiency=sleep_record["efficiency"],
                        end_time=datetime.strptime(sleep_record["endTime"], "%Y-%m-%dT%H:%M:%S.%f"),
                        info_code=sleep_record.get("infoCode"),
                        is_main_sleep=sleep_record["isMainSleep"],
                        minutes_after_wakeup=sleep_record["minutesAfterWakeup"],
                        minutes_asleep=sleep_record["minutesAsleep"],
                        minutes_awake=sleep_record["minutesAwake"],
                        minutes_to_fall_asleep=sleep_record["minutesToFallAsleep"],
                        log_type=sleep_record["type"],
                        start_time=datetime.strptime(sleep_record["startTime"], "%Y-%m-%dT%H:%M:%S.%f"),
                        time_in_bed=sleep_record["timeInBed"],
                        type=sleep_record["type"]
                    )
                    result_proxy = connection.execute(insert_stmt)
                    sleep_log_id = result_proxy.inserted_primary_key[0]  # Get the inserted ID

                    # Insert sleep levels and summaries
                    for level_data in sleep_record.get("levels", {}).get("data", []):
                        insert_level_stmt = insert(sleep_level_table).values(
                            sleep_log_id=sleep_log_id,
                            date_time=datetime.strptime(level_data["dateTime"], "%Y-%m-%dT%H:%M:%S.%f"),
                            level=level_data["level"],
                            seconds=level_data["seconds"],
                            is_short=level_data.get("isShort", False)
                        )
                        connection.execute(insert_level_stmt)

                    for summary_data in sleep_record.get("levels", {}).get("summary", []):
                        insert_summary_stmt = insert(sleep_summary_table).values(
                            sleep_log_id=sleep_log_id,
                            level=summary_data["level"],
                            count=summary_data["count"],
                            minutes=summary_data["minutes"],
                            thirty_day_avg_minutes=summary_data.get("thirtyDayAvgMinutes")
                        )
                        connection.execute(insert_summary_stmt)

                # Update `api.last_sync_date` to the current `job_timestamp`
                updated_timestamp = datetime.strptime(job_timestamp, "%Y-%m-%d_%H:%M:%S")
                
                connection.execute(
                    update(api)
                    .where(api.c.study_subject_id == subject_id)
                    .values(last_sync_date=updated_timestamp)
                )
                connection.commit()

                logger.info("Updated last_sync_date", extra={"study_subject_id": subject_id})

    except Exception as e:
        error_code = "DB_ERROR"
        logger.error("Error querying the study subject API data", extra={"error": str(e)})

    # Upload log file to S3
    try:
        s3_client = boto3.client("s3")
        bucket_name = config["S3_BUCKET"]
        # Prepare the S3 filename including function_id
        s3_filename = f"logs/{function_id}_log_{job_timestamp}.json"

        s3_client.upload_file(log_filename, bucket_name, s3_filename)
        
        logger.info("Log file successfully uploaded to S3", extra={"s3_filename": s3_filename, "bucket": bucket_name})

    except Exception as s3_error:
        logger.error("Error uploading log file to S3", extra={"error": str(s3_error)})

    s3_uri = f"s3://{bucket_name}/{s3_filename}"
    end_time = int(time.time() * 1000)  # Current time in milliseconds
    ms_billed = end_time - start_time

    # Update the lambda_function table with completion information
    try:
        with engine.connect() as connection:
            update_stmt = (
                update(lambda_function_table)
                .where(lambda_function_table.c.id == function_id)
                .values(
                    completed_on=datetime.now(),
                    ms_billed=ms_billed,
                    logfile=s3_uri,
                    status="FAILED" if error_code else "COMPLETE",
                    error_code=error_code
                )
            )
            connection.execute(update_stmt)
            connection.commit()
            logger.info("Updated lambda_function with completion information", extra={"function_id": function_id})

    except Exception as db_error:
        logger.error("Error updating lambda_function with completion information", extra={"error": str(db_error)})
