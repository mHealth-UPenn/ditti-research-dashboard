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

import json
import logging
import os
import traceback
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Literal

import boto3
from sqlalchemy import (
    MetaData,
    Table,
    and_,
    create_engine,
    func,
    insert,
    or_,
    select,
    update,
)
from sqlalchemy.orm import aliased

from shared.fitbit import get_fitbit_oauth_session
from shared.lambda_logger import LambdaLogger
from shared.utils.sleep_logs import generate_sleep_logs

TESTING = os.getenv("TESTING") is not None
STAGING = os.getenv("STAGING") is not None
DEBUG = os.getenv("DEBUG") is not None

# Use a common timestamp across the whole function
function_timestamp = datetime.now().isoformat()

logger = LambdaLogger(
    function_timestamp, level=logging.DEBUG if DEBUG else logging.INFO
)


class NestedError(Exception):
    """Exception for error on a nested database transaction."""


class DBInitializationError(Exception):
    """Exception for error on initialization of database engine and connection."""


class ConfigFetchError(Exception):
    """Exception for error on fetching config from AWS Secrets Manager."""


class DBFetchError(Exception):
    """Exception for error on fetching any data from the database."""


class DBUpdateError(Exception):
    """Exception for error on updating or inserting any data to the database."""


class S3UploadError(Exception):
    """Exception for error on uploading the log file to S3."""


class DB:
    """
    Helper class for initializing a database connection.

    Parameters
    ----------
    - db_uri (str): The URI for securely connecting to the database.
    """

    def __init__(self, db_uri: str):
        self.engine = create_engine(db_uri, future=True)
        self.metadata = MetaData(bind=self.engine)


class DBService:
    """
    Base database service class for providing a database connection context.

    Parameters
    ----------
    - db (DB): A database connection class.
    """

    def __init__(self, db: DB):
        self.db = db
        self.connection = None

    @contextmanager
    def connect(self):
        """
        Context manager for establishing and managing a database connection.

        This method provides a transactional scope for database operations.
        It ensures that the connection is properly managed, beginning a
        transaction on entry and committing or rolling back as needed on exit.

        Usage:
        ```python
        db_service = DBService(db_instance)
        with db_service.connect() as connection:
            # Perform database operations using the `connection`
        ```

        Yields
        ------
        - connection: An active database connection to be used for
            database operations.

        Ensures:
        - The connection is properly closed and cleaned up after use.
        """
        try:
            with self.db.engine.connect() as connection, connection.begin():
                self.connection = connection
                yield connection
        finally:
            self.connection = None


# Typing for the database-defined lambda_task task status enum
type TaskStatus = Literal[
    "Pending", "InProgress", "Success", "Failed", "CompletedWithErrors"
]


@dataclass
class LambdaTaskEntry:
    """
    Represents a row from the `lambda_task` table.

    Reflects the status and details of a Lambda function.

    Attributes
    ----------
    - id (int): The unique identifier of the Lambda function.
    - status (TaskStatus): The current status of the function,
        which can be one of the following:
        - "Pending"
        - "InProgress"
        - "Success"
        - "Failed"
        - "CompletedWithErrors"
    - billed_ms (int | None): The number of milliseconds billed
        for the function's execution.
    - created_on (datetime): The timestamp when the function was created.
    - updated_on (datetime): The timestamp when the function was last updated.
    - completed_on (datetime | None): The timestamp when the function
        was completed. `None` if the function is Pending or InProcess.
    - log_file (str | None): The S3 URI location of the function's log file.
        `None` if no log file exists
    - error_code (str | None): The error code (if any) returned
        during function execution. `None` if no error occurred.
    """

    id: int
    status: TaskStatus
    billed_ms: int | None
    created_on: datetime
    updated_on: datetime
    completed_on: datetime | None
    log_file: str | None
    error_code: str | None


class LambdaTaskService(DBService):
    """
    A database service for interacting with the `lambda_task` table.

    This class provides methods to query and update entries in the table,
    specifically designed for managing Lambda task statuses and related metadata.

    Inherits:
        DBService: Base database service class.

    Attributes
    ----------
        table (Table): SQLAlchemy Table object for the `lambda_task` table.
        __entry (LambdaTaskEntry | None): The current task entry being managed,
            or None if no entry is loaded.

    Methods
    -------
        get_entry(entry_id: int):
            Queries the `lambda_task` table for a specific entry by ID and loads
            it as a `LambdaTaskEntry` instance.

        update_status(status: TaskStatus, **kwargs):
            Updates the status and optional additional fields
            of the current task entry.
    """

    def __init__(self, db: DB):
        """
        Initialize the LambdaTaskService.

        Parameters
        ----------
            db (DB): An instance of the `DB` helper class
                to manage database connections.

        Raises
        ------
            RuntimeError: If the table reflection fails
                or the database schema is inconsistent.
        """
        super().__init__(db)
        m = self.db.metadata
        e = self.db.engine

        # Reflect existing database into a new model
        m.reflect(only=["lambda_task"])

        # Access the `lambda_task` table
        self.table = Table("lambda_task", m, autoload_with=e)
        self.__entry: LambdaTaskEntry | None = None

    def get_entry(self, entry_id: int):
        """
        Query `lambda_task` table for entry by ID and store as `LambdaTaskEntry`.

        Parameters
        ----------
            entry_id (int): The ID of the Lambda task to query.

        Raises
        ------
            RuntimeError: If called outside the `connect` context
                or if no entry is found.

        Side Effects:
            - Logs the result of the query.
            - Stores the retrieved entry in the `__entry` attribute.

        Example:
            ```python
            with service.connect():
                service.get_entry(42)
                print(service.__entry)
            ```
        """
        if self.connection is None:
            raise RuntimeError(
                "`get_entry` must be called within `connect` context."
            )

        # Query the table for the specific function_id and update status
        query = select(self.table).where(self.table.c.id == entry_id)
        entry = self.connection.execute(query).first()
        self.__entry = LambdaTaskEntry(**entry._asdict())

        if self.__entry is not None:
            logger.info(
                "Query for `lambda_task` result", extra=self.__entry.__dict__
            )

        else:
            logger.warning(
                "No entry found for function_id", extra={"function_id": entry_id}
            )

            raise RuntimeError(f"No entry found for function_id {entry_id}")

    def update_status(self, status: TaskStatus, **kwargs):
        """
        Update the currently loaded Lambda task entry status and optional fields.

        Parameters
        ----------
            status (TaskStatus): The new status to set for the task.
            **kwargs: Additional fields to update in the `lambda_task` table.

        Raises
        ------
            RuntimeError: If called outside the `connect` context or
                if no entry is loaded.

        Side Effects:
            - Executes an update statement on the `lambda_task` table.
            - Logs the updated status and additional fields.

        Example:
            ```python
            with service.connect():
                service.get_entry(42)
                service.update_status("InProgress", billed_ms=1500)
            ```
        """
        if self.connection is None:
            raise RuntimeError(
                "`update_status` must be called within `connect` context."
            )

        if self.__entry is None:
            raise RuntimeError("Entry not found. Call `get_entry` first.")

        logger.info("update_status", extra=dict(status=status, **kwargs))

        # Update the status
        update_stmt = (
            update(self.table)
            .where(self.table.c.id == self.__entry.id)
            .values(status=status, **kwargs)
        )

        self.connection.execute(update_stmt)

        logger.info(
            "Updated lambda function status",
            extra={"function_id": self.__entry.id, "status": status},
        )


@dataclass
class StudySubjectEntry:
    """
    Represents entries in the `study_subject` table and its relevant joins.

    Attributes
    ----------
        id (int): Unique identifier for the study subject.
        ditti_id (str): A study subject's Ditti ID.
        api_user_uuid (str): UUID of the user in the associated API system.
        api_id (int): Identifier for the associated API.
        last_sync_date (str | None): Timestamp of the last synchronization
            with the API, if any.
        starts_on (datetime): Start date for the subject's enrollment in
            a study. This attribute is the earliest `starts_on` value for all
            `join_study_subject_study` entries.
        expires_on (str): Expiration date for the subject's enrollment in
            a study. This attribute is the latest `expires_on` value for all
            `join_study_subject_study` entries.
        earliest_sleep_log (date | None): Earliest date of sleep logs available
            for the study subject.
    """

    id: int
    ditti_id: str
    api_user_uuid: str
    api_id: int
    last_sync_date: str | None
    starts_on: datetime
    expires_on: str
    earliest_sleep_log: date | None


class StudySubjectService(DBService):
    """
    Manage the `study_subject` table and associated tables.

    Includes APIs, studies, sleep logs, sleep levels, and sleep summaries.

    This class provides methods to query study subject data, manage
    sleep-related data, and handle synchronization with APIs.

    Methods
    -------
        get_entries(): Fetches all entries of study subjects
            requiring API synchronization.
        iter_entries(): Yields each study subject entry for iterative processing.
        insert_data(data): Inserts sleep log, level,
            and summary data into the database for the current entry.
        update_last_sync_date(): Updates the `last_sync_date`
            for the current study subject.
    """

    def __init__(self, *args):
        """
        Initialize the StudySubjectService with the db connection and metadata.

        Parameters
        ----------
            *args: Positional arguments to be passed to the
                base `DBService` class.
        """
        super().__init__(*args)
        m = self.db.metadata
        e = self.db.engine

        # Reflect existing tables into models
        m.reflect(
            only=[
                "join_study_subject_api",
                "study_subject",
                "join_study_subject_study",
            ]
        )

        # Aliased tables for readability
        self.api_table = Table("join_study_subject_api", m, autoload_with=e)
        self.api = aliased(self.api_table)
        self.subject = aliased(Table("study_subject", m, autoload_with=e))
        self.study = aliased(
            Table("join_study_subject_study", m, autoload_with=e)
        )
        self.sleep_log_table = Table("sleep_log", m, autoload_with=e)
        self.sleep_level_table = Table("sleep_level", m, autoload_with=e)
        self.sleep_summary_table = Table("sleep_summary", m, autoload_with=e)

        self.__entries: list[StudySubjectEntry] = []
        self.__index = None

    def get_entries(self):
        """
        Retrieve all study subject entries that require API association.

        Populates the `__entries` attribute with `StudySubjectEntry` instances,
        representing the consolidated data for each study subject.

        Raises
        ------
            RuntimeError: If called outside of a `connect` context.
        """
        if self.connection is None:
            raise RuntimeError(
                "`get_entries` must be called within `connect` context."
            )

        # Subquery for a study subject's earliest sleep log
        earliest_sleep_log_subquery = (
            select(func.min(self.sleep_log_table.c.date_of_sleep))
            .where(self.sleep_log_table.c.study_subject_id == self.subject.c.id)
            .scalar_subquery()
        )

        query = (
            select(
                self.subject.c.id,
                self.subject.c.ditti_id,
                self.api.c.api_user_uuid,
                self.api.c.api_id,
                self.api.c.last_sync_date,
                self.study.c.starts_on,
                self.study.c.expires_on,
                self.study.c.did_consent,
                earliest_sleep_log_subquery.label("earliest_sleep_log"),
            )
            .select_from(
                self.api.join(
                    self.subject,
                    self.api.c.study_subject_id == self.subject.c.id,
                ).join(
                    self.study,
                    self.subject.c.id == self.study.c.study_subject_id,
                )
            )
            .where(
                and_(
                    # Get only studies that have been consented
                    self.study.c.did_consent,
                    or_(
                        self.api.c.last_sync_date
                        is None,  # Get any entries without a `last_sync_date`
                        # Get any entries with a `last_sync_date` before today
                        # and before the `expires_on` date
                        and_(
                            self.api.c.last_sync_date < date.today(),
                            self.study.c.expires_on > self.api.c.last_sync_date,
                        ),
                        # Get any entries with past data that was not pulled
                        self.study.c.starts_on < earliest_sleep_log_subquery,
                        earliest_sleep_log_subquery
                        is None,  # Get any entries where no sleep logs exist
                    ),
                )
            )
        )

        self.__entries = []
        result = self.connection.execute(query).fetchall()

        # Merge multiple results for a subject into one
        result_map: dict[int, dict] = {}
        for entry in result:
            entry_id = entry.id

            try:
                # Query APIs starting from the study subject's earliest
                # start date (if `last_sync_date` is null)
                result_map[entry_id]["starts_on"] = min(
                    result_map[entry_id]["starts_on"], entry.starts_on
                )
                # Query APIs until the study subject's latest expiry date
                result_map[entry_id]["expires_on"] = max(
                    result_map[entry_id]["expires_on"], entry.expires_on
                )
            except KeyError:
                result_map[entry_id] = entry._asdict()

        for entry in result_map.values():
            self.__entries.append(
                StudySubjectEntry(
                    id=entry["id"],
                    ditti_id=entry["ditti_id"],
                    api_user_uuid=entry["api_user_uuid"],
                    api_id=entry["api_id"],
                    last_sync_date=entry["last_sync_date"],
                    starts_on=entry["starts_on"],
                    expires_on=entry["expires_on"],
                    earliest_sleep_log=entry["earliest_sleep_log"],
                )
            )

        logger.info(
            "Fetched participant API data from database",
            extra={"result_count": len(self.__entries)},
        )

        for entry in self.__entries:
            logger.debug(f"Data for entry {entry.id}", extra=entry.__dict__)

    def iter_entries(self):
        """
        Iterate over all fetched study subject entries.

        Yields
        ------
            StudySubjectEntry: The next entry in the sequence.

        Raises
        ------
            RuntimeError: If no entries are available
                or if called outside of a `connect` context.
        """
        if self.connection is None:
            raise RuntimeError(
                "`iter_entries` must be called within `connect` context."
            )

        if self.__entries is None:
            raise RuntimeError("No entries to iterate. Call `get_entries` first.")

        for i in range(len(self.__entries)):
            self.__index = i
            yield self.__entries[i]

        self.__index = None

    def insert_data(self, data: list[dict]):
        """
        Insert sleep-related data into current study subject entry.

        Parameters
        ----------
            data (list[dict]): A list of sleep record dictionaries containing
                log, level, and summary details.

        Raises
        ------
            RuntimeError: If called outside of the `iter_entries` block
                or without a valid index.
        """
        if self.__index is None:
            raise RuntimeError(
                "No index found. `insert_data` must be called "
                "inside `iter_entries` block."
            )

        entry = self.__entries[self.__index]

        for sleep_record in data:
            # Create sleep log entry
            insert_stmt = insert(self.sleep_log_table).values(
                study_subject_id=entry.id,
                log_id=sleep_record["logId"],
                date_of_sleep=datetime.strptime(
                    sleep_record["dateOfSleep"], "%Y-%m-%d"
                ).date(),
                duration=sleep_record["duration"],
                efficiency=sleep_record["efficiency"],
                end_time=datetime.strptime(
                    sleep_record["endTime"], "%Y-%m-%dT%H:%M:%S.%f"
                ),
                info_code=sleep_record.get("infoCode"),
                is_main_sleep=sleep_record["isMainSleep"],
                minutes_after_wakeup=sleep_record["minutesAfterWakeup"],
                minutes_asleep=sleep_record["minutesAsleep"],
                minutes_awake=sleep_record["minutesAwake"],
                minutes_to_fall_asleep=sleep_record["minutesToFallAsleep"],
                log_type=sleep_record["logType"],
                start_time=datetime.strptime(
                    sleep_record["startTime"], "%Y-%m-%dT%H:%M:%S.%f"
                ),
                time_in_bed=sleep_record["timeInBed"],
                type=sleep_record["type"],
            )
            result_proxy = self.connection.execute(insert_stmt)
            sleep_log_id = result_proxy.inserted_primary_key[0]

            logger.debug(
                "Sleep log created",
                extra={
                    "study_subject_id": entry.id,
                    "sleep_log_id": sleep_log_id,
                },
            )

            # Insert sleep levels
            for level_data in sleep_record.get("levels", {}).get("data", []):
                insert_level_stmt = insert(self.sleep_level_table).values(
                    sleep_log_id=sleep_log_id,
                    date_time=datetime.strptime(
                        level_data["dateTime"], "%Y-%m-%dT%H:%M:%S.%f"
                    ),
                    level=level_data["level"],
                    seconds=level_data["seconds"],
                    is_short=False,
                )
                self.connection.execute(insert_level_stmt)
            for level_data in sleep_record.get("levels", {}).get("shortData", []):
                insert_level_stmt = insert(self.sleep_level_table).values(
                    sleep_log_id=sleep_log_id,
                    date_time=datetime.strptime(
                        level_data["dateTime"], "%Y-%m-%dT%H:%M:%S.%f"
                    ),
                    level=level_data["level"],
                    seconds=level_data["seconds"],
                    is_short=True,
                )
                self.connection.execute(insert_level_stmt)

            # Insert summaries
            for level, summary_data in (
                sleep_record.get("levels", {}).get("summary", {}).items()
            ):
                insert_summary_stmt = insert(self.sleep_summary_table).values(
                    sleep_log_id=sleep_log_id,
                    level=level,
                    count=summary_data["count"],
                    minutes=summary_data["minutes"],
                    thirty_day_avg_minutes=summary_data.get(
                        "thirtyDayAvgMinutes"
                    ),
                )
                self.connection.execute(insert_summary_stmt)

    def update_last_sync_date(self, last_sync_date: str | None = None):
        """
        Update the current study subject `last_sync_date` to now.

        Parameters
        ----------
        - last_sync_date (str, optional): The date to set last sync to.
            If not passed, `function_timestamp` is used by default.

        Raises
        ------
            RuntimeError: If called outside of the `iter_entries` block
                or without a valid index.
        """
        if self.__index is None:
            raise RuntimeError(
                "No index found. `insert_data` must be called "
                "inside `iter_entries` block."
            )

        if last_sync_date is None:
            last_sync_date = function_timestamp

        entry = self.__entries[self.__index]

        self.connection.execute(
            update(self.api_table)
            .where(self.api_table.c.study_subject_id == entry.id)
            .values(
                last_sync_date=datetime.strptime(
                    last_sync_date, "%Y-%m-%dT%H:%M:%S.%f"
                )
            )
        )

        logger.info(
            "Updated last_sync_date",
            extra={
                "study_subject_id": entry.id,
                "last_sync_date": datetime.strptime(
                    last_sync_date, "%Y-%m-%dT%H:%M:%S.%f"
                ),
            },
        )


def get_secret(secret_name: str) -> dict:
    """
    Retrieve a secret from AWS Secrets Manager.

    Parameters
    ----------
    - secret_name (str): The name of the secret to retrieve a value from.

    Returns
    -------
    - dict: The secret's value.
    """
    # Initialize a session using environment variables
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager", region_name=os.getenv("AWS_REGION")
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
        extra={"secret_name": secret_name, "num_keys": len(secret_data.keys())},
    )

    return secret_data


def build_url(
    entry: StudySubjectEntry,
    /,
    *,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """
    Build a URL for querying the Fitbit API.

    This function constructs a URL to fetch sleep data for a given study subject
    from the Fitbit API. The URL is based on the study subject's API user UUID,
    start date, and end date. If `start_date` or `end_date` are not provided,
    they are derived from the `StudySubjectEntry` object.

    Parameters
    ----------
        entry (StudySubjectEntry): The entry containing details about the study
            subject, including API user UUID, last sync date, start date, and
            expiry date.
        start_date (str | None): Optional. The start date for the data query in
            "YYYY-MM-DD" format. Defaults to the subject's last sync date or
            start date if the last sync date is not available.
        end_date (str | None): Optional. The end date for the data query in
            "YYYY-MM-DD" format. Defaults to the earlier of the subject's expiry
            date or the current timestamp.

    Returns
    -------
        str: The constructed URL for querying the Fitbit API.

    Raises
    ------
        ValueError: If the `start_date` is on or after the `end_date`.

    Example:
        >>> entry = StudySubjectEntry(
                id=1,
                api_user_uuid="user123",
                api_id=101,
                last_sync_date=None,
                starts_on=datetime(2023, 1, 1),
                expires_on="2023-12-31",
                did_consent=True,
                earliest_sleep_log=None
            )
        >>> build_url(entry, start_date="2023-05-01")
        'https://api.fitbit.com/1.2/user/user123/sleep/date/2023-05-01/2023-12-31.json'
    """
    study_subject_id = entry.api_user_uuid

    if start_date is None:
        try:
            start_date = entry.last_sync_date.strftime("%Y-%m-%d")
        except AttributeError:
            start_date = entry.starts_on.strftime("%Y-%m-%d")

    if end_date is None:
        timestamp = datetime.strptime(function_timestamp, "%Y-%m-%dT%H:%M:%S.%f")
        end_date = min(entry.expires_on, timestamp).strftime("%Y-%m-%d")

    if start_date >= end_date:
        logger.error(
            "Error building URL: `start_date` is on or after `end_date`.",
            extra={
                "start_date": start_date,
                "end_date": end_date,
            },
        )
        raise ValueError(
            "Error building URL: `start_date` is on or after `end_date`."
        )

    url = f"https://api.fitbit.com/1.2/user/{study_subject_id}/sleep/date/{start_date}/{end_date}.json"

    logger.debug("Fitbit URL generated", extra={"url": url})

    return url


def handler(event, _context):
    """
    AWS Lambda handler function for wearable data retrieval.

    Processes wearable data retrieval requests initiated by the Lambda service.
    Fetches data from wearable APIs and stores it in the database.

    Parameters
    ----------
    event : dict
        The event data passed to the Lambda function.
    _context : object
        AWS Lambda context object (unused).

    Returns
    -------
    dict
        Response object containing status and execution details.
    """
    logger.info(
        "Starting wearable data retrieval job",
        extra={"function_timestamp": function_timestamp},
    )
    log_file = None
    error_code = None
    has_errors = False

    # Retrieve function_id from the lambda function invocation event
    function_id = event.get("function_id")
    logger.info("Retrieved function_id", extra={"function_id": function_id})

    try:
        config = {"S3_BUCKET": os.getenv("S3_BUCKET")}
        tokens_config = {}

        # Load secrets
        if TESTING or STAGING:
            config = {
                "FLASK_DB": os.getenv("FLASK_DB"),
                "S3_BUCKET": os.getenv("S3_BUCKET"),
            }

        if (not TESTING) or STAGING:
            try:
                config_secret_name = os.getenv("AWS_CONFIG_SECRET_NAME")
                tokens_secret_name = os.getenv("AWS_KEYS_SECRET_NAME")
                config.update(get_secret(config_secret_name))
                tokens_config = get_secret(tokens_secret_name)
            except Exception as err:
                logger.error(
                    "Error retrieving secret",
                    extra={"error": traceback.format_exc()},
                )
                raise ConfigFetchError from err

        # Database connection setup
        try:
            db = DB(config["FLASK_DB"])
            lambda_task_service = LambdaTaskService(db)
            study_subject_service = StudySubjectService(db)

        except Exception as err:
            logger.error(
                "Error initializing database services",
                extra={"error": traceback.format_exc()},
            )
            raise DBInitializationError from err

        # Get and update the `lambda_task` database entry
        with lambda_task_service.connect() as connection:
            try:
                lambda_task_service.get_entry(function_id)

            # On error raise exception and exit
            except Exception as err:
                logger.error(
                    "Error fetching lambda function from database",
                    extra={"error": traceback.format_exc()},
                )
                raise DBFetchError from err

            try:
                lambda_task_service.update_status("InProgress")

            # On error raise exception and exit
            except Exception as err:
                logger.error(
                    "Error updating lambda function status from database",
                    extra={"error": traceback.format_exc()},
                )
                raise DBUpdateError from err

        # Get and update participant data
        with study_subject_service.connect() as connection:
            # Try querying study subjects and their join data
            try:
                study_subject_service.get_entries()

            # On error raise exception and exit
            except Exception as err:
                logger.error(
                    "Error fetching participant API data from database",
                    extra={"error": traceback.format_exc()},
                )
                raise DBFetchError from err

            # Iterate over each result to query the Fitbit API
            for entry in study_subject_service.iter_entries():
                logger.debug(
                    "Fetching participant Fitbit data", extra=entry.__dict__
                )

                # Construct the URL for Fitbit API call
                try:
                    urls = [build_url(entry)]
                except ValueError:
                    urls = []

                # Handle edge case when a participant's `starts_on`
                # changes to an earlier date
                # Generate an additional URL for fetching retroactive data
                if (entry.earliest_sleep_log is None) or (
                    entry.earliest_sleep_log
                    and entry.starts_on.date()
                    < entry.earliest_sleep_log - timedelta(days=1)
                ):
                    logger.info(
                        "Participant's `starts_on` value is before their"
                        "earliest sleep log. Generating extra URL for fetching "
                        "retroactive data.",
                        extra={
                            "study_subject_id": entry.id,
                            "starts_on": entry.starts_on,
                            "earliest_sleep_log": entry.earliest_sleep_log,
                        },
                    )

                    end_date = None
                    if entry.earliest_sleep_log is not None:
                        end_date = str(
                            entry.earliest_sleep_log - timedelta(days=1)
                        )

                    try:
                        urls.append(
                            build_url(
                                entry,
                                start_date=str(entry.starts_on.date()),
                                end_date=end_date,
                            )
                        )
                    except ValueError:
                        logger.warning(
                            "Error building URL for retroactive data. "
                            "Continuing to next study subject.",
                            extra={"error": traceback.format_exc()},
                        )
                        continue

                # Try querying the fitbit API for this study subject
                data = []
                if TESTING:
                    data += generate_sleep_logs()["sleep"]
                else:
                    # Retrieve OAuth tokens for the subject
                    try:
                        tokens = tokens_config[entry.ditti_id]
                    except KeyError:
                        logger.info(
                            "Participant not found in API tokens secret.",
                            extra={"ditti_id": entry.ditti_id},
                        )
                        has_errors = True
                        continue

                    try:
                        for url in urls:
                            logger.info(
                                "Querying Fitbit API",
                                extra={
                                    "ditti_id": entry.ditti_id,
                                    "url": url,
                                },
                            )

                            # Query the Fitbit API
                            fitbit_session = get_fitbit_oauth_session(
                                entry.ditti_id, config, tokens
                            )
                            response = fitbit_session.request("GET", url)
                            data += response.json()["sleep"]

                        logger.info(
                            "Participant data retrieved from Fibit API",
                            extra={
                                "study_subject_id": entry.id,
                                "result_count": len(data),
                            },
                        )

                    # On error continue to next study subject
                    except Exception:
                        logger.error(
                            "Error retrieving participant data from Fitbit API",
                            extra={
                                "error": traceback.format_exc(),
                                "study_subject_id": entry.id,
                                "url": url,
                            },
                        )
                        has_errors = True
                        continue

                # Try inserting new data into the database.
                try:
                    with connection.begin_nested():
                        # Try inserting Fitbit data into the database
                        try:
                            study_subject_service.insert_data(data)

                        # On error continue to next study subject
                        except Exception as err:
                            logger.error(
                                "Error inserting Fitbit data to database",
                                extra={
                                    "study_subject_id": entry.id,
                                    "error": traceback.format_exc(),
                                },
                            )
                            raise NestedError from err

                        # Try updating `api.last_sync_date` to the
                        # latest `dateOfSleep` in `data`
                        last_sync_date = None
                        try:
                            last_sync_date = max(
                                sleep_record["dateOfSleep"]
                                for sleep_record in data
                            )

                            # Set last sync date to midnight next day
                            last_sync_date = datetime.fromisoformat(
                                last_sync_date
                            )
                            last_sync_date += timedelta(days=1)
                            last_sync_date = last_sync_date.strftime("%Y-%m-%d")
                            last_sync_date = datetime.strptime(
                                last_sync_date, "%Y-%m-%d"
                            )

                            # Convert to string matching the same format
                            # as `function_timestamp`
                            last_sync_date = last_sync_date.isoformat(
                                timespec="milliseconds"
                            )

                        except Exception:
                            logger.warning(
                                "Error parsing `last_sync_date` from sleep "
                                "data. Falling back to `function_timestamp`.",
                                extra={
                                    "study_subject_id": entry.id,
                                    "error": traceback.format_exc(),
                                },
                            )
                        try:
                            study_subject_service.update_last_sync_date(
                                last_sync_date
                            )

                        # On error continue to next study subject
                        except Exception as err:
                            logger.error(
                                "Error updating `last_sync_date`",
                                extra={
                                    "study_subject_id": entry.id,
                                    "api_id": entry.api_id,
                                    "error": traceback.format_exc(),
                                },
                            )
                            raise NestedError from err

                # Continue to next study subject in case of handled error
                except NestedError:
                    logger.error(
                        "Updating study subject failed. Changes not committed.",
                        extra={"study_subject_id": entry.id},
                    )
                    has_errors = True
                    continue

                # Log error and exit in case of unhandled error
                except Exception as err:
                    logger.error(
                        "Unhandled error when updating study subject. Exiting.",
                        extra={
                            "study_subject_id": entry.id,
                            "error": traceback.format_exc(),
                        },
                    )
                    raise DBUpdateError from err

        # Upload log file to S3
        try:
            s3_client = boto3.client("s3")
            bucket_name = config["S3_BUCKET"]

            # Prepare the S3 filename including function_id
            log_file = f"{function_id}_{os.path.split(logger.log_filename)[1]}"
            s3_client.upload_file(logger.log_filename, bucket_name, log_file)

            logger.info(
                "Log file successfully uploaded to S3",
                extra={"log_file": log_file, "bucket": bucket_name},
            )

        except Exception as s3_error:
            logger.error(
                "Error uploading log file to S3", extra={"error": str(s3_error)}
            )

            raise S3UploadError from s3_error

    except ConfigFetchError:
        error_code = "ConfigFetchError"
    except DBInitializationError:
        error_code = "DBInitializationError"
    except DBFetchError:
        error_code = "DBFetchError"
    except DBUpdateError:
        error_code = "DBUpdateError"
    except S3UploadError:
        error_code = "S3UploadError"
    except Exception:
        logger.info(
            "Exiting on unknown error.", extra={"error": traceback.format_exc()}
        )
        error_code = "UnknownError"

    # Update the lambda_task table with completion information
    try:
        with lambda_task_service.connect() as connection:
            status = "Success"
            if error_code:
                status = "Failed"
            elif has_errors:
                status = "CompletedWithErrors"

            lambda_task_service.update_status(
                status=status,
                completed_on=datetime.now(),
                log_file=log_file,
                error_code=error_code,
            )

            logger.info(
                "Updated lambda_task with completion information",
                extra={"function_id": function_id},
            )

    except Exception:
        logger.error(
            "Error updating lambda_task with completion information",
            extra={
                "function_id": function_id,
                "error_code": error_code,
                "error": traceback.format_exc(),
            },
        )
