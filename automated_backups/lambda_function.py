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

# Use a common timestamp across the whole job
job_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

# Custom JSON formatter
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage()
        }

        # Add any extra fields in record if they exist
        exclude = {"message", "args", "levelname", "created", "exc_info", "exc_text"}
        log_entry.update(
            {
                k: v for k, v in record.__dict__.items()
                if k not in exclude
            }
        )

        return json.dumps(log_entry)

# Set up logger to write JSON log entries to a file
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# JSON Formatter
json_formatter = JsonFormatter()

# Stream handler for console output
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(json_formatter)
logger.addHandler(stream_handler)

# File handler for JSON log file output
log_filename = f"log_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
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
        secret_name = "secret-aws-portal"
        response = client.get_secret_value(SecretId=secret_name)

        # Parse and return the secret
        if "SecretString" in response:
            secret = response["SecretString"]
            config = json.loads(secret)
        else:
            # Decode binary secret if it's not a string
            config = json.loads(response["SecretBinary"].decode("utf-8"))

        return config

    except Exception as e:
        print(f"Error retrieving secret: {e}")
        return None

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

        return items

    except Exception as e:
        print(f"Error retrieving items from table {table_name}: {e}")
        return None


def save_and_upload_backup(df, bucket_name):
    # Generate timestamped file name
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"Backup_{timestamp}.xlsx"
    df.to_excel(file_name, index=False)

    # Initialize S3 client and upload the file
    s3 = boto3.client("s3")
    s3.upload_file(file_name, bucket_name, file_name)
    print(f"File {file_name} uploaded to bucket {bucket_name}")


def create_dataframe(user_permissions, taps, audio_taps, audio_files):
    user_df = pd.DataFrame([{
        "User ID": item["user_permission_id"]["S"]
    } for item in user_permissions])

    tap_df = pd.DataFrame([{
        "User ID": item["user"]["S"],
        "Timestamp": item["time"]["S"],
        "Timezone": item["timeZone"]["S"]
    } for item in taps])

    audio_tap_df = pd.DataFrame([{
        "User ID": item["user"]["S"],
        "Timestamp": item["time"]["S"],
        "Timezone": item["timeZone"]["S"],
        "Audio Action": item["action"]["S"]
    } for item in audio_taps])

    audio_file_df = pd.DataFrame([{
        "Audio Filename": item["fileName"]["S"]
    } for item in audio_files])

    # Join data by "User ID"
    merged_df = pd.merge(user_df, tap_df, on="User ID", how="left")
    merged_df = pd.merge(merged_df, audio_tap_df, on="User ID", how="left")
    merged_df = pd.merge(
        merged_df,
        audio_file_df,
        left_index=True,
        right_index=True,
        how="left"
    )

    # Final dataframe with only required columns
    final_df = merged_df[
        ["User ID", "Timestamp", "Timezone", "Audio Action", "Audio Filename"]
    ]
    return  final_df


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


def get_old_data_ids(items, date_field):
    cutoff_date = datetime.now() - timedelta(days=90)
    return [
        item["id"]["S"] for item in items
        if datetime.strptime(item[date_field]["S"], "%Y-%m-%dT%H:%M:%SZ") < cutoff_date
    ]


def query_emails(db_uri):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(db_uri)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Execute the query
        cursor.execute("SELECT email FROM account")
        emails = cursor.fetchall()
        
        # Extract email addresses from query result
        email_list = [row["email"] for row in emails]
        
        # Close the connection
        cursor.close()
        conn.close()
        
        return email_list

    except Exception as e:
        print(f"Error querying emails: {e}")
        return None


def send_email_with_attachment(
    recipients,
    subject,
    body_text,
    file_name,
    bucket_name
):
    ses_client = boto3.client("ses", region_name=config["AWS_REGION"])
    s3_client = boto3.client("s3")

    # Download the Excel file from S3
    s3_client.download_file(bucket_name, file_name, file_name)

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
                RawMessage={
                    "Data": msg
                }
            )
            print(f"Email sent to {recipient}: MessageId {response["MessageId"]}")

        except ClientError as e:
            print(f"Failed to send email to {recipient}: {e.response["Error"]["Message"]}")


# Function to upload log file to S3
def upload_log_to_s3(bucket_name, s3_log_filename):
    s3 = boto3.client("s3")
    try:
        s3.upload_file(log_filename, bucket_name, s3_log_filename)
        logger.info(f"Log file {log_filename} uploaded to S3 bucket {bucket_name} as {s3_log_filename}")
    except Exception as e:
        logger.error(f"Failed to upload log file to S3: {e}")


def handler():
    # Initialize DynamoDB client
    dynamodb = boto3.client("dynamodb", region_name=os.getenv("AWS_REGION"))

    # Retrieve all items from each table
    user_permissions = get_all_items(config["AWS_TABLENAME_USER"], dynamodb)
    taps = get_all_items(config["AWS_TABLENAME_TAP"], dynamodb)
    audio_files = get_all_items(config["AWS_TABLENAME_AUDIO_FILE"], dynamodb)
    audio_taps = get_all_items(config["AWS_TABLENAME_AUDIO_TAP"], dynamodb)

    # # Convert DynamoDB items to pandas DataFrames and handle necessary type conversions
    # df = create_dataframe(user_permissions, taps, audio_files, audio_taps)

    # # Call the function to save and upload the final DataFrame
    # save_and_upload_backup(df, config["AWS_BACKUP_BUCKET"])

    # # Get IDs of old items in Tap and AudioTap tables
    # old_tap_ids = get_old_data_ids(taps, "time")
    # old_audio_tap_ids = get_old_data_ids(audio_taps, "time")

    # # Delete old items
    # delete_old_data(config["APP_SYNC_HOST"], "Tap", old_tap_ids)
    # delete_old_data(config["APP_SYNC_HOST"], "AudioTap", old_audio_tap_ids)

    # # Retrieve emails from the account table
    # emails = query_emails(config["FLASK_DB"])

    # # Define the email subject and body text
    # email_subject = "Data Download Notification"
    # email_body = "This is your data download. In two months data will be deleted. Please save this file."

    # # Send emails with attachment
    # send_email_with_attachment(
    #     emails,
    #     email_subject,
    #     email_body,
    #     file_name="Backup_<timestamp>.xlsx",
    #     bucket_name=config["AWS_BACKUP_BUCKET"]
    # )

    # upload_log_to_s3(bucket_name=config["AWS_BACKUP_BUCKET"], s3_log_filename=f"{log_filename}")
