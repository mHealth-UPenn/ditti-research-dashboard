from datetime import datetime, date
from typing import Tuple, Optional, List
from aws_portal.models import StudySubject, SleepLog

MAX_DATE_RANGE_DAYS = 30


def validate_date_range(start_date_str: str, end_date_str: Optional[str] = None) -> Tuple[date, date]:
    """
    Validates the provided date range.

    Parameters:
        start_date_str (str): The start date in 'YYYY-MM-DD' format.
        end_date_str (str, optional): The end date in 'YYYY-MM-DD' format. Defaults to None.

    Returns:
        tuple: A tuple containing the validated start_date and end_date as `datetime.date` objects.

    Raises:
        ValueError: If the dates are invalid, the end date is earlier than the start date, 
                    or the date range exceeds the allowed maximum.
    """
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Invalid start_date format. Expected YYYY-MM-DD.")

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid end_date format. Expected YYYY-MM-DD.")
    else:
        end_date = start_date

    if end_date < start_date:
        raise ValueError("end_date cannot be earlier than start_date.")

    if (end_date - start_date).days > MAX_DATE_RANGE_DAYS:
        raise ValueError(
            f"Date range cannot exceed {MAX_DATE_RANGE_DAYS} days."
        )

    return start_date, end_date


def cache_key_admin(ditti_id: str, start_date: date, end_date: date) -> str:
    """
    Generates a cache key for admin Fitbit data requests.

    Parameters:
        ditti_id (str): The unique ID of the study subject.
        start_date (datetime.date): The start date of the data request.
        end_date (datetime.date): The end date of the data request.

    Returns:
        str: The generated cache key string.
    """
    return f"admin_fitbit_data:{ditti_id}:{start_date}:{end_date}"


def cache_key_participant(ditti_id: str, start_date: date, end_date: date) -> str:
    """
    Generates a cache key for participant Fitbit data requests.

    Parameters:
        ditti_id (str): The unique ID of the participant.
        start_date (datetime.date): The start date of the data request.
        end_date (datetime.date): The end date of the data request.

    Returns:
        str: The generated cache key string.
    """
    return f"participant_fitbit_data:{ditti_id}:{start_date}:{end_date}"


def get_fitbit_data_for_subject(ditti_id: str, start_date: date, end_date: date) -> Optional[List[dict]]:
    """
    Retrieves and serializes Fitbit data for a specific study subject within a given date range.

    Parameters:
        ditti_id (str): The unique ID of the study subject.
        start_date (datetime.date): The start date for the query.
        end_date (datetime.date): The end date for the query.

    Returns:
        list: A list of serialized sleep log data if found.
        None: If the study subject is not found or is archived.
    """
    # Retrieve StudySubject
    study_subject = StudySubject.query.filter_by(
        ditti_id=ditti_id, is_archived=False).first()
    if not study_subject:
        return None

    # Query SleepLogs within date range
    sleep_logs = SleepLog.query.filter(
        SleepLog.study_subject_id == study_subject.id,
        SleepLog.date_of_sleep >= start_date,
        SleepLog.date_of_sleep <= end_date
    ).all()

    # Serialize data
    serialized_data = [sleep_log.meta for sleep_log in sleep_logs]
    return serialized_data
