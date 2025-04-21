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

from datetime import date, datetime
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import load_only, selectinload

from backend.extensions import db
from backend.models import SleepLevel, SleepLog, StudySubject
from backend.utils.serialization import serialize_fitbit_data

MAX_DATE_RANGE_DAYS = 30


def validate_date_range(
    start_date_str: str, end_date_str: Optional[str] = None
) -> Tuple[date, date]:
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


def cache_key_participant(
    ditti_id: str, start_date: date, end_date: date
) -> str:
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


def get_fitbit_data_for_subject(
    ditti_id: str, start_date: date, end_date: date
) -> Optional[List[dict]]:
    """
    Retrieves and serializes Fitbit data for a specific study subject within a given date range.

    Parameters:
        ditti_id (str): The unique ID of the study subject.
        start_date (datetime.date): The start date for the query.
        end_date (datetime.date): The end date for the query.

    Returns:
        list: A list of serialized sleep log data dictionaries if found.
        None: If the study subject is not found or is archived.
    """
    study_subject = StudySubject.query.filter_by(
        ditti_id=ditti_id, is_archived=False
    ).first()
    if not study_subject:
        return None

    stmt = (
        select(SleepLog)
        .options(
            load_only(SleepLog.date_of_sleep, SleepLog.log_type, SleepLog.type),
            selectinload(SleepLog.levels).options(
                load_only(
                    SleepLevel.date_time,
                    SleepLevel.level,
                    SleepLevel.seconds,
                    SleepLevel.is_short,
                )
            ),
        )
        .where(
            SleepLog.study_subject_id == study_subject.id,
            SleepLog.date_of_sleep >= start_date,
            SleepLog.date_of_sleep <= end_date,
        )
        .order_by(SleepLog.id)
    )

    results = db.session.execute(stmt).unique().scalars().all()

    serialized_data = serialize_fitbit_data(results)

    return serialized_data
