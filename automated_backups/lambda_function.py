import boto3
from datetime import datetime, timedelta
import json
import logging
import os
import requests
import sys

import boto3
from botocore.exceptions import ClientError
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

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


def get_secret():
    # Initialize a session using environment variables
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name=os.getenv("AWS_REGION")
    )

    try:
        # Fetch the secret
        secret_name = os.getenv("AWS_SECRET_NAME")
        response = client.get_secret_value(SecretId=secret_name)

        # Parse and return the secret
        if "SecretString" in response:
            secret = response["SecretString"]
            config = json.loads(secret)
        else:
            # Decode binary secret if it's not a string
            config = json.loads(response["SecretBinary"].decode("utf-8"))

        logger.info(
            "Configuration retrieved from SecretsManager",
            extra={"secret_name": secret_name, "num_keys": len(config.keys())}
        )

        return config

    except Exception as e:
        logger.error(f"Error retrieving secret: {e}")
        raise RuntimeError(e)

# Load secret into config variable
config = get_secret()


def get_all_items(table_name, dynamodb):
    try:
        # Scan the table to get all items
        response = dynamodb.scan(TableName=table_name)
        items = response["Items"]

        # Handle pagination if needed
        while "LastEvaluatedKey" in response:
            response = dynamodb.scan(
                TableName=table_name,
                ExclusiveStartKey=response["LastEvaluatedKey"]
            )
            items.extend(response["Items"])

        logger.info(
            "Items retrieved from DynamoDB",
            extra={"table_name": table_name, "num_items": len(items)}
        )

        return items

    except Exception as e:
        logger.error(f"Error retrieving items from table {table_name}: {e}")
        raise RuntimeError(e)


def save_and_upload_backup(df, bucket_name):
    # Generate timestamped file name
    file_name = f"Backup_{job_timestamp}.xlsx"
    df.to_excel(file_name, index=False)

    try:
        # Initialize S3 client and upload the file
        s3 = boto3.client("s3")
        s3.upload_file(file_name, bucket_name, file_name)
        logger.info(
            "File uploaded to bucket",
            extra={"file_name": file_name, "bucket_name": bucket_name}
        )

        return file_name

    except ClientError as e:
        logger.error(
            f"Error uploading file to bucket due to client error",
            extra={
                "file_name": file_name,
                "bucket_name": bucket_name,
                "client_error_message": e.response["Error"]["Message"]
            }
        )

        raise RuntimeError(e)


def get_item_value(item, key, item_type="S"):
    try:
        return item[key][item_type]
    except KeyError:
        return None


def create_dataframe(user_permissions, taps, audio_taps, audio_files):
    user_df = pd.DataFrame([{
        "user_id": get_item_value(item, "id"),
        "User ID": get_item_value(item, "user_permission_id"),
    } for item in user_permissions])

    tap_df = pd.DataFrame([{
        "user_id": get_item_value(item, "tapUserId"),
        "Timestamp": get_item_value(item, "time"),
        "Timezone": get_item_value(item, "timeZone"),
    } for item in taps])

    audio_tap_df = pd.DataFrame([{
        "user_id": get_item_value(item, "audioTapUserId"),
        "audio_file_id": get_item_value(item, "audioTapAudioFileId"),
        "Timestamp": get_item_value(item, "time"),
        "Timezone": get_item_value(item, "timeZone"),
        "Audio Action": get_item_value(item, "action"),
    } for item in audio_taps])

    audio_file_df = pd.DataFrame([{
        "audio_file_id": get_item_value(item, "id"),
        "Audio Filename": get_item_value(item, "fileName"),
    } for item in audio_files])

    # Join data by "User ID"
    tap_df = tap_df.merge(user_df, on="user_id")

    # Join audiofiles by "Audio File ID"
    audio_tap_df = audio_tap_df.merge(user_df, on="user_id")\
        .merge(audio_file_df, on="audio_file_id")

    # Stack taps and audio taps into a single dataframe
    df = pd.concat([tap_df, audio_tap_df])\
        .sort_values(by=["User ID", "Timestamp"])\
        .drop(columns=["user_id", "audio_file_id"])

    return df


def delete_old_data(appsync_host, table_name, id_list):
    url = f"{appsync_host}/graphql"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": config["APP_SYNC_API_KEY"]
    }
    delete_query = """
    mutation DeleteItem($id: ID!) {
      delete{tableName}(input: { id: $id }) {
        id
      }
    }
    """.replace("{tableName}", table_name)

    for item_id in id_list:
        variables = {"id": item_id}
        response = requests.post(
            url,
            headers=headers,
            json={"query": delete_query, "variables": variables}
        )
        if response.status_code == 200:
            print(f"Deleted item with ID {item_id} from {table_name}")
        else:
            print(f"Failed to delete item with ID {item_id} from {table_name}: {response.text}")


def get_ids_to_delete(items, date_field, days=90):
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    ids_to_delete = [
        item["id"]["S"] for item in items if item[date_field]["S"] < cutoff_date
    ]

    logger.info(
        "Retrieved IDs of items to delete",
        extra={
            "items": items[0]["__typename"]["S"],
            "cutoff_date": cutoff_date,
            "num_items": len(ids_to_delete),
        }
    )

    return ids_to_delete


# TODO: Implement when database is always available
# def query_emails(db_uri):
#     try:
#         # Connect to the PostgreSQL database
#         conn = psycopg2.connect(db_uri)
#         cursor = conn.cursor(cursor_factory=RealDictCursor)

#         # Execute the query
#         cursor.execute("SELECT email FROM account")
#         emails = cursor.fetchall()

#         # Extract email addresses from query result
#         email_list = [row["email"] for row in emails]

#         # Close the connection
#         cursor.close()
#         conn.close()

#         logger.info(
#             "Emails retrieved from database",
#             extra={"num_emails": len(email_list)}
#         )

#         return email_list

#     except Exception as e:
#         logger.error(f"Error retrieving emails: {e}")
#         raise RuntimeError(e)


# Temporary workaround for getting research coordinator emails
def query_emails(db_uri):
    emails = config["STUDY_COORDINATOR_EMAILS"].split(",")
    logger.warning("Emails retrieved from Secrets Manager. Update email retrieval to query database in future when database is always available.")

    if TESTING:
        emails = [os.getenv("TEST_EMAIL")]

    return emails


def send_email_with_attachment(recipients, subject, body_text, file_name):
    ses_client = boto3.client("ses", region_name=config["AWS_REGION"])

    # Read the file content
    with open(file_name, "rb") as file:
        attachment_data = file.read()

    # Define email content and attachment details
    for recipient in recipients:
        msg = {
            "Source": config["SES_EMAIL_SOURCE"],
            "Destination": {
                "ToAddresses": [recipient]
            },
            "Message": {
                "Subject": {
                    "Data": subject
                },
                "Body": {
                    "Text": {
                        "Data": body_text
                    }
                }
            },
            "Attachments": [
                {
                    "ContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "Filename": file_name,
                    "Data": attachment_data
                }
            ]
        }

        try:
            # Send email
            response = ses_client.send_raw_email(
                Source=msg["Source"],
                Destinations=msg["Destination"]["ToAddresses"],
                RawMessage={"Data": msg}
            )

            logger.info(
                "Email sent",
                extra={
                    "recipient": recipient,
                    "message_id": response["MessageId"]
                }
            )

        except ClientError as e:
            logger.warning(
                "Failed to send email due to client error",
                extra={
                    "recipient": recipient,
                    "client_error_message": e.response["Error"]["Message"]
                }
            )


# Function to upload log file to S3
def upload_log_to_s3(bucket_name, s3_log_filename):
    s3 = boto3.client("s3")
    try:
        s3.upload_file(log_filename, bucket_name, s3_log_filename)
        logger.info(f"Log file {log_filename} uploaded to S3 bucket {bucket_name} as {s3_log_filename}")
    except Exception as e:
        logger.error(f"Failed to upload log file to S3: {e}")


def handler(event, context):
    logger.info("Starting data backup job", extra={"job_timestamp": job_timestamp})
    # # Initialize DynamoDB client
    # dynamodb = boto3.client("dynamodb", region_name=os.getenv("AWS_REGION"))

    # # Retrieve all items from each table
    # user_permissions = get_all_items(config["AWS_TABLENAME_USER"], dynamodb)
    # taps = get_all_items(config["AWS_TABLENAME_TAP"], dynamodb)
    # audio_taps = get_all_items(config["AWS_TABLENAME_AUDIO_TAP"], dynamodb)
    # audio_files = get_all_items(config["AWS_TABLENAME_AUDIO_FILE"], dynamodb)

    # # Convert DynamoDB items to pandas DataFrames and handle necessary type conversions
    # df = create_dataframe(user_permissions, taps, audio_taps, audio_files)

    # # Call the function to save and upload the final DataFrame
    df = pd.DataFrame()
    file_name = save_and_upload_backup(df, config["AWS_BACKUP_BUCKET"])

    # # Get IDs of old items in Tap and AudioTap tables
    # old_tap_ids = get_ids_to_delete(taps, "time")
    # old_audio_tap_ids = get_ids_to_delete(audio_taps, "time")

    # # Delete old items
    # delete_old_data(config["APP_SYNC_HOST"], "Tap", old_tap_ids)
    # delete_old_data(config["APP_SYNC_HOST"], "AudioTap", old_audio_tap_ids)

    # Retrieve emails from the account table
    emails = query_emails(config["FLASK_DB"])

    # Define the email subject and body text
    email_subject = "[Ditti] Data Download Notification"
    email_body = "This is your latest data download from the Penn Ditti app. Data will be deleted from AWS after 90 days. Please save this file."

    # Send emails with attachment
    send_email_with_attachment(emails, email_subject, email_body, file_name)

    # upload_log_to_s3(bucket_name=config["AWS_BACKUP_BUCKET"], s3_log_filename=f"{log_filename}")