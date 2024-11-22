import boto3
from datetime import datetime
import json
import logging
import os
import sys

import boto3

# from utils import get_fitbit_oauth_session

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
            # Decode binary secret if it's not a string
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
    logger.info("Starting wearable data retrieval job", extra={"job_timestamp": job_timestamp})

    # 1. Retrieve `function_id` from the lambda function invocation

    # 2. Query the `lambda_function` SQL table where `lambda_function.id = function_id`
    #     -Use config["DB_URI"] as the database URI

    # 3. Update `lambda_function.status` to `IN_PROGRESS`

    # 4. Query all entries in the `join_study_subject_api as api` SQL table
    #     -Use config["DB_URI"] as the database URI
    #     -Join `study_subject as subject` on `api.study_subject_id` and `subject.id`
    #     -Join `join_study_subject_study as study` on `subject.id` and `study.study_subject_id`
    #     -Where `study.expires_on` (datetime) is after `api.last_sync_date` (date)
    #     -Select `subject.id api.api_user_uuid api.last_sync_date study.expires_on`
    #     -On error save `DB_ERROR` in the variable `error_code`

    # 5. Query the Fitbit API for each query result
    #     -Initialize a Fitbit oauth session using `get_fitbit_oauth_session`
    #      -Example usage: `session = get_fitbit_oauth_session(entry, tokens)`
    #      -Retrieve `tokens` from `tokens_config` using `subject.id` as the key: `tokens = tokens_config[subject_id]`
    #     -Query the Fitbit API using `session`
    #      -Example usage: `data = fitbit_session.request(url)`
    #      -For `url` use `https://api.fitbit.com/1.2/user/[user-id]/sleep/date/[startDate]/[endDate].json`
    #      -Use `api.api_user_uuid` as `user-id`
    #      -Use `api.last_sync_date` as `startDate`
    #      -If `study.expires_on` is before `job_timestamp` use `study.expires_on` as `endDate`
    #      -Else use `job_timestamp` as `endDate`
    #     -On error save `API_ERROR` in the variable `error_code`

    # 6. Store each API query result in the following SQL schema as defined by SQLAlchemy. The schema reflects the data
    #    structed expected from each API query
    #     -On error save `DB_ERROR` in the variable `error_code`
    # class SleepLog(db.Model):
    #     __tablename__ = "sleep_log"

    #     id = db.Column(db.Integer, primary_key=True)
    #     study_subject_id = db.Column(
    #         db.Integer,
    #         db.ForeignKey("study_subject.id"),
    #         nullable=False,
    #         index=True
    #     )

    #     log_id = db.Column(db.BigInteger, nullable=False, unique=True, index=True)
    #     date_of_sleep = db.Column(db.Date, nullable=False, index=True)
    #     duration = db.Column(db.Integer)
    #     efficiency = db.Column(db.Integer)
    #     end_time = db.Column(db.DateTime)
    #     info_code = db.Column(db.Integer)
    #     is_main_sleep = db.Column(db.Boolean)
    #     minutes_after_wakeup = db.Column(db.Integer)
    #     minutes_asleep = db.Column(db.Integer)
    #     minutes_awake = db.Column(db.Integer)
    #     minutes_to_fall_asleep = db.Column(db.Integer)
    #     log_type = db.Column(Enum(SleepLogTypeEnum), nullable=False)
    #     start_time = db.Column(db.DateTime)
    #     time_in_bed = db.Column(db.Integer)
    #     type = db.Column(Enum(SleepCategoryTypeEnum), nullable=False)

    #     study_subject = db.relationship(
    #         "StudySubject",
    #         back_populates="sleep_logs"
    #     )
    #     levels = db.relationship(
    #         "SleepLevel",
    #         back_populates="sleep_log",
    #         cascade="all, delete-orphan",
    #         lazy="selectin"  # Efficient loading of related objects
    #     )
    #     summaries = db.relationship(
    #         "SleepSummary",
    #         back_populates="sleep_log",
    #         cascade="all, delete-orphan",
    #         lazy="joined"  # Eagerly load summaries
    #     )


    # class SleepLevel(db.Model):
    #     __tablename__ = "sleep_level"
    #     __table_args__ = (
    #         db.Index("idx_sleep_level_sleep_log_id_date_time",
    #                  "sleep_log_id", "date_time"),
    #     )

    #     id = db.Column(db.Integer, primary_key=True)
    #     sleep_log_id = db.Column(
    #         db.Integer,
    #         db.ForeignKey("sleep_log.id"),
    #         nullable=False
    #     )
    #     date_time = db.Column(db.DateTime, nullable=False, index=True)
    #     level = db.Column(Enum(SleepLevelEnum), nullable=False)
    #     seconds = db.Column(db.Integer, nullable=False)
    #     is_short = db.Column(db.Boolean, default=False, nullable=True)

    #     sleep_log = db.relationship("SleepLog", back_populates="levels")

    # class SleepSummary(db.Model):
    #     __tablename__ = "sleep_summary"

    #     id = db.Column(db.Integer, primary_key=True)
    #     sleep_log_id = db.Column(
    #         db.Integer,
    #         db.ForeignKey("sleep_log.id"),
    #         nullable=False
    #     )
    #     level = db.Column(Enum(SleepLevelEnum), nullable=False)
    #     count = db.Column(db.Integer)
    #     minutes = db.Column(db.Integer)
    #     thirty_day_avg_minutes = db.Column(db.Integer, nullable=True)

    #     sleep_log = db.relationship("SleepLog", back_populates="summaries")

    # 7. Update `api.last_sync_date` to `job_timestamp`

    # 8. Upload the log file to S3
    #     -Use config["S3_BUCKET"] as the bucket to upload to
    #     -Include `function_id` in the log filename on S3

    # 9. Update `lambda_function`
    #     -Update `lambda_function.completed_on` to the current time
    #     -Update `lambda_function.ms_billed` to the number of milliseconds the function ran
    #     -Update `lambda_function.logfile` to the full S3 URI of the logfile
    #     -If any error occured update `lambda_function.status` to `FAILED` and `lambda_function.error_code` to `error_code`
    #     -Else set `lambda_function.status` to `COMPLETE`
