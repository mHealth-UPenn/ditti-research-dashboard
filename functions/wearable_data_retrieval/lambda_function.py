import boto3
from datetime import datetime
from functools import partial
import json
import logging
import os
import traceback

import boto3
from sqlalchemy import create_engine, Table, MetaData, insert, select, update
from sqlalchemy.engine import Row
from sqlalchemy.orm import aliased

from shared.fitbit import get_fitbit_oauth_session
from shared.lambda_logger import LambdaLogger
from shared.utils.sleep_logs import generate_sleep_logs

TESTING = os.getenv("TESTING") is not None
DEBUG = os.getenv("DEBUG") is not None

# Use a common timestamp across the whole job
job_timestamp = datetime.now().isoformat()

logger = LambdaLogger(
    job_timestamp,
    level=logging.DEBUG if DEBUG else logging.INFO
)


class NestedError(Exception):
    pass


class DBService:
    def __init__(self, db_uri: str):
        self.engine = create_engine(db_uri, future=True)
        self.metadata = MetaData(bind=self.engine)


class StudySubjectService:
    def __init__(self, service: DBService):
        self.__service = service
        m = service.metadata
        e = service.engine

        # Reflect existing tables into models
        m.reflect(only=["join_study_subject_api", "study_subject", "join_study_subject_study"])

        # Aliased tables for readability
        self.api_table = Table("join_study_subject_api", m, autoload_with=e)
        self.api = aliased(self.api_table)
        self.subject = aliased(Table("study_subject", m, autoload_with=e))
        self.study = aliased(Table("join_study_subject_study", m, autoload_with=e))
        self.sleep_log_table = Table("sleep_log", m, autoload_with=e)
        self.sleep_level_table = Table("sleep_level", m, autoload_with=e)
        self.sleep_summary_table = Table("sleep_summary", m, autoload_with=e)

        self.__connection = None
        self.__entries = None
        self.__index = None

    def connect(self):
        with self.service.engine.connect() as connection:
            with connection.begin():
                self.__connection = connection
                yield connection
        self.__connection = None

    def get_entries(self):
        query = (
            select(
                self.subject.c.id,
                self.api.c.api_user_uuid,
                self.api.c.api_id,
                self.api.c.last_sync_date,
                self.study.c.expires_on
            )
            .select_from(self.api
                .join(self.subject, self.api.c.study_self.subject_id == self.subject.c.id)
                .join(self.study, self.subject.c.id == self.study.c.study_subject_id)
            )
            .where(self.study.c.expires_on > self.api.c.last_sync_date)
        )
        self.__entries = self.__connection.execute(query).fetchall()

        logger.info(
            "Fetched participant API data from database",
            extra={"result_count": len(self.__entries)}
        )

    def iter_entries(self):
        for i in range(len(self.__entries)):
            self.__index = i
            yield self.__entries[i]

        self.__index = None

    def insert_data(self, data):
        entry = self.__entries[self.__index]

        for sleep_record in data.get("sleep", []):
            # Create sleep log entry
            insert_stmt = insert(self.sleep_log_table).values(
                study_subject_id=entry.id,
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
                log_type=sleep_record["logType"],
                start_time=datetime.strptime(sleep_record["startTime"], "%Y-%m-%dT%H:%M:%S.%f"),
                time_in_bed=sleep_record["timeInBed"],
                type=sleep_record["type"]
            )
            result_proxy = self.__connection.execute(insert_stmt)
            sleep_log_id = result_proxy.inserted_primary_key[0]

            logger.debug(
                "Sleep log created",
                extra={
                    "study_subject_id": entry.id,
                    "sleep_log_id": sleep_log_id
                }
            )

            # Insert sleep levels
            for level_data in sleep_record.get("levels", {}).get("data", []):
                insert_level_stmt = insert(self.sleep_level_table).values(
                    sleep_log_id=sleep_log_id,
                    date_time=datetime.strptime(level_data["dateTime"], "%Y-%m-%dT%H:%M:%S.%f"),
                    level=level_data["level"],
                    seconds=level_data["seconds"],
                    is_short=level_data.get("isShort", False)
                )
                self.__connection.execute(insert_level_stmt)
                sleep_level_id = result_proxy.inserted_primary_key[0]

                logger.debug(
                    "Sleep level created",
                    extra={
                        "study_subject_id": entry.id,
                        "sleep_log_id": sleep_log_id,
                        "sleep_level_id": sleep_level_id
                    }
                )

            # Insert summaries
            for summary_data in sleep_record.get("levels", {}).get("summary", []):
                insert_summary_stmt = insert(self.sleep_summary_table).values(
                    sleep_log_id=sleep_log_id,
                    level=summary_data["level"],
                    count=summary_data["count"],
                    minutes=summary_data["minutes"],
                    thirty_day_avg_minutes=summary_data.get("thirtyDayAvgMinutes")
                )
                self.__connection.execute(insert_summary_stmt)
                sleep_summary_id = result_proxy.inserted_primary_key[0]

                logger.debug(
                    "Sleep summary created",
                    extra={
                        "study_subject_id": entry.id,
                        "sleep_log_id": sleep_log_id,
                        "sleep_summary_id": sleep_summary_id
                    }
                )

    def update_last_sync_date(self):
        entry = self.__entries[self.__index]

        self.__connection.execute(
            update(self.api_table)
            .where(self.api_table.c.study_subject_id == entry.id)
            .values(last_sync_date=datetime.strptime(job_timestamp, "%Y-%m-%dT%H:%M:%S.%f"))
        )

        logger.info(
            "Updated last_sync_date",
            extra={"study_subject_id": entry.id}
        )


def get_secret(secret_name):
    # Initialize a session using environment variables
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name=os.getenv("AWS_REGION")
    )

    # Fetch the secret
    response = client.get_secret_value(SecretId=secret_name)

    # Parse and return the secret
    if "SecretString" in response:
        secret = response["SecretString"]
        secret_data = json.loads(secret)
    else:
        # Decode binary secret if it"s not a string
        secret_data = json.loads(response["SecretBinary"].decode("utf-8"))

    logger.info(
        "Secret retrieved from SecretsManager",
        extra={"secret_name": secret_name, "num_keys": len(secret_data.keys())}
    )

    return secret_data


def build_url(entry):
    study_subject_id = entry.api_user_uuid
    start_date = entry.last_sync_date.strftime("%Y-%m-%d")
    timestamp = datetime.strptime(job_timestamp, "%Y-%m-%dT%H:%M:%S.%f")
    end_date = min(entry.expires_on, timestamp).strftime("%Y-%m-%d")
    url = f"https://api.fitbit.com/1.2/user/{study_subject_id}/sleep/date/{start_date}/{end_date}.json"

    logger.debug("Fitbit URL generated", extra={"url": url})

    return url


def handler(event, context):
    logger.info("Starting wearable data retrieval job", extra={"job_timestamp": job_timestamp})
    error_code = None

    # Load secrets
    if TESTING:
        config = {
            "DB_URI": os.getenv("DB_URI")
        }
        tokens_config = {}
    else:
        try:
            config_secret_name = os.getenv("AWS_CONFIG_SECRET_NAME")
            tokens_secret_name = os.getenv("AWS_KEYS_SECRET_NAME")
            config = get_secret(config_secret_name)
            tokens_config = get_secret(tokens_secret_name)
        except Exception as e:
            logger.error(
                f"Error retrieving secret",
                extra={"error": traceback.format_exc()}
            )
            error_code = "AWS_ERROR"
            raise

    # # Retrieve function_id from the lambda function invocation event
    function_id = event.get("function_id")
    logger.info("Retrieved function_id", extra={"function_id": function_id})

    # Database connection setup
    db_service = DBService(config["DB_URI"])

    # # Reflect existing database into a new model
    # metadata.reflect(only=["lambda_function"])

    # # Access the `lambda_function` table
    # lambda_function_table = Table(
    #     "lambda_function", metadata, autoload_with=engine
    # )

    # # Query the table for the specific function_id and update status
    # try:
    #     with engine.connect() as connection:
    #         # Retrieve the record
    #         query = select(lambda_function_table)\
    #             .where(lambda_function_table.c.id == function_id)
    #         result = connection.execute(query).first()

    #         if result:
    #             logger.info(
    #                 "Query for `lambda_function` result", extra=dict(result)
    #             )

    #             # Update the status to "IN_PROGRESS"
    #             update_stmt = (
    #                 update(lambda_function_table).
    #                 where(lambda_function_table.c.id == function_id).
    #                 values(status="IN_PROGRESS")
    #             )
    #             connection.execute(update_stmt)
    #             connection.commit()
    #             logger.info(
    #                 "Updated status to IN_PROGRESS",
    #                 extra={"function_id": function_id}
    #             )

    #         else:
    #             logger.warning(
    #                 "No entry found for function_id",
    #                 extra={"function_id": function_id}
    #             )

    # except Exception as e:
    #     logger.error("Error updating the database", extra={"error": traceback.format_exc()})
    #     raise

    # Reflect existing tables into models
    study_subject_service = StudySubjectService(db_service)

    with study_subject_service.connect() as connection:
        # Try querying study subject api joins that are not expired
        try:
            study_subject_service.get_entries()

        # On error raise exception and exit
        except Exception:
            error_code = "DB_ERROR"
            logger.error(
                "Error fetching participant API data from database",
                extra={"error": traceback.format_exc()}
            )
            raise

        # Iterate over each result to query the Fitbit API
        for entry in study_subject_service.iter_entries():
            logger.debug(
                "Fetching participant Fitbit data",
                extra=entry._asdict()
            )

            # Construct the URL for Fitbit API call
            url = build_url(entry)

            # Try querying the fitbit API for this study subject
            data = {"sleep": []}
            try:
                if TESTING:
                    data = generate_sleep_logs()
                else:
                    # Retrieve OAuth tokens for the subject
                    tokens = tokens_config[entry.id]

                    # Query the Fitbit API
                    fitbit_session = get_fitbit_oauth_session(entry, tokens)
                    response = fitbit_session.request(url)
                    data = response.json()

                logger.info(
                    "Participant data retrieved from Fibit API",
                    extra={"study_subject_id": entry.id, "result_count": len(data["sleep"])}
                )

            # On error continue to next study subject
            except Exception:
                logger.error(
                    "Error retrieving participant data from Fitbit API",
                    extra={
                        "error": traceback.format_exc(),
                        "study_subject_id": entry.id,
                        "url": url
                    }
                )
                continue

            try:
                with connection.begin_nested():
                    # Try inserting Fitbit data into the database
                    try:
                        study_subject_service.insert_data(data)

                    # On error continue to next study subject
                    except Exception:
                        logger.error(
                            "Error inserting Fitbit data to database",
                            extra={
                                "study_subject_id": entry.id,
                                "error": traceback.format_exc()
                            }
                        )
                        raise NestedError

                    # Try updating `api.last_sync_date` to the current `job_timestamp`
                    try:
                        study_subject_service.update_last_sync_date()

                    # On error continue to next study subject
                    except Exception:
                        logger.error(
                            "Error updating `last_sync_date`",
                            extra={
                                "study_subject_id": entry.id,
                                "api_id": entry.api_id,
                                "error": traceback.format_exc()
                            }
                        )
                        raise NestedError

            # Continue to next study subject in case of handled error
            except NestedError:
                logger.error(
                    "Updating study subject failed. Changes not committed.",
                    extra={"study_subject_id": entry.id}
                )
                continue

            # Log error and exit in case of unhandled error
            except Exception:
                error_code = "DB_ERROR"
                logger.error(
                    "Unhandled error when updating study subject. Exiting.",
                    extra={
                        "study_subject_id": entry.id,
                        "error": traceback.format_exc(),
                    }
                )
                raise

    # # Upload log file to S3
    # try:
    #     s3_client = boto3.client("s3")
    #     bucket_name = config["S3_BUCKET"]
    #     # Prepare the S3 filename including function_id
    #     s3_filename = f"logs/{function_id}_{logger.log_filename}.json"

    #     s3_client.upload_file(logger.log_filename, bucket_name, s3_filename)

    #     logger.info("Log file successfully uploaded to S3", extra={"s3_filename": s3_filename, "bucket": bucket_name})

    # except Exception as s3_error:
    #     logger.error("Error uploading log file to S3", extra={"error": str(s3_error)})

    # s3_uri = f"s3://{bucket_name}/{s3_filename}"
    # end_time = int(time.time() * 1000)  # Current time in milliseconds
    # ms_billed = end_time - start_time

    # # Update the lambda_function table with completion information
    # try:
    #     with engine.connect() as connection:
    #         update_stmt = (
    #             update(lambda_function_table)
    #             .where(lambda_function_table.c.id == function_id)
    #             .values(
    #                 completed_on=datetime.now(),
    #                 ms_billed=ms_billed,
    #                 logfile=s3_uri,
    #                 status="FAILED" if error_code else "COMPLETE",
    #                 error_code=error_code
    #             )
    #         )
    #         connection.execute(update_stmt)
    #         connection.commit()
    #         logger.info("Updated lambda_function with completion information", extra={"function_id": function_id})

    # except Exception as db_error:
    #     logger.error("Error updating lambda_function with completion information", extra={"error": str(db_error)})
