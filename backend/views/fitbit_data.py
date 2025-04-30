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

import io
import logging
import traceback
from datetime import datetime

import pandas as pd
from flask import Blueprint, jsonify, make_response, request, send_file
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from backend.auth.decorators import (
    participant_auth_required,
    researcher_auth_required,
)
from backend.extensions import cache, db
from backend.models import SleepLevel, SleepLog, Study, StudySubject
from backend.utils.fitbit_data import (
    cache_key_admin,
    cache_key_participant,
    get_fitbit_data_for_subject,
    validate_date_range,
)

admin_fitbit_blueprint = Blueprint(
    "admin_fitbit_data", __name__, url_prefix="/admin/fitbit_data"
)

participant_fitbit_blueprint = Blueprint(
    "participant_fitbit_data", __name__, url_prefix="/participant/fitbit_data"
)

logger = logging.getLogger(__name__)


@admin_fitbit_blueprint.route("/<string:ditti_id>", methods=["GET"])
@researcher_auth_required("View", "Wearable Dashboard")
@researcher_auth_required("View", "Wearable Data")
def admin_get_fitbit_data(account, ditti_id: str):
    """
    Retrieve Fitbit data for a specific study subject as an admin.

    URL Parameters:
        ditti_id (str): The unique ID of the study subject.

    Query Parameters:
        start_date (str): The start date in 'YYYY-MM-DD' format (required).
        end_date (str, optional): The end date in 'YYYY-MM-DD' format.

    Returns
    -------
        JSON Response: Serialized Fitbit data if found and valid.
        HTTP 400: If input validation fails.
        HTTP 404: If the study subject is not found or archived.
        HTTP 500: If a database or server error occurs.
    """
    try:
        # Extract and validate query parameters
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")

        if not start_date_str:
            return make_response({"msg": "start_date is required."}, 400)

        try:
            start_date, end_date = validate_date_range(
                start_date_str, end_date_str
            )
        except ValueError as ve:
            return make_response({"msg": str(ve)}, 400)

        # Check cache
        cache_key = cache_key_admin(ditti_id, start_date, end_date)
        cached_data = cache.get(cache_key)
        if cached_data:
            return jsonify(cached_data)

        # Retrieve and serialize data
        serialized_data = get_fitbit_data_for_subject(
            ditti_id, start_date, end_date
        )
        if serialized_data is None:
            return make_response(
                {"msg": "StudySubject not found or is archived."}, 404
            )

        # Cache the result for 2 hours
        cache.set(cache_key, serialized_data)

        return jsonify(serialized_data)

    except SQLAlchemyError as db_err:
        logger.error(
            f"Database error retrieving Fitbit data for ditti_id {ditti_id}: "
            f"{db_err!s}"
        )
        return make_response(
            {"msg": "Database error retrieving Fitbit data."}, 500
        )
    except Exception as e:
        logger.error(f"Unhandled error in admin_get_fitbit_data: {e!s}")
        return make_response({"msg": "Unexpected server error."}, 500)


@participant_fitbit_blueprint.route("", methods=["GET"])
@participant_auth_required
def participant_get_fitbit_data(ditti_id: str):
    """
    Retrieve Fitbit data for the authenticated participant.

    Query Parameters:
        start_date (str): The start date in 'YYYY-MM-DD' format (required).
        end_date (str, optional): The end date in 'YYYY-MM-DD' format.

    Args:
        ditti_id (str): The study subject's username,
            passed from participant_auth_required.

    Returns
    -------
        JSON Response: Serialized Fitbit data if found and valid.
        HTTP 400: If input validation or token decoding fails.
        HTTP 401: If the ID token is missing or expired.
        HTTP 404: If the study subject is not found or archived.
        HTTP 500: If a database or server error occurs.
    """
    try:
        # Extract and validate query parameters
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")

        if not start_date_str:
            return make_response({"msg": "start_date is required."}, 400)

        try:
            start_date, end_date = validate_date_range(
                start_date_str, end_date_str
            )
        except ValueError as ve:
            return make_response({"msg": str(ve)}, 400)

        # Check cache
        cache_key = cache_key_participant(ditti_id, start_date, end_date)
        cached_data = cache.get(cache_key)
        if cached_data:
            return jsonify(cached_data)

        # Retrieve and serialize data
        serialized_data = get_fitbit_data_for_subject(
            ditti_id, start_date, end_date
        )
        if serialized_data is None:
            return make_response(
                {"msg": "StudySubject not found or is archived."}, 404
            )

        # Cache the result for 2 hours
        cache.set(cache_key, serialized_data)

        return jsonify(serialized_data)

    except SQLAlchemyError as db_err:
        logger.error(
            f"Database error retrieving Fitbit data for ditti_id {ditti_id}: "
            f"{db_err!s}"
        )
        return make_response(
            {"msg": "Database error retrieving Fitbit data."}, 500
        )
    except Exception as e:
        logger.error(f"Unhandled error in participant_get_fitbit_data: {e!s}")
        return make_response({"msg": "Unexpected server error."}, 500)


@admin_fitbit_blueprint.route(
    "/download/participant/<string:ditti_id>", methods=["GET"]
)
@researcher_auth_required("View", "Wearable Dashboard")
@researcher_auth_required("View", "Wearable Data")
def download_fitbit_participant(account, ditti_id: str):
    """
    Download Fitbit API data for a single study participant as an Excel file.

    This endpoint retrieves all Fitbit-related data for a participant identified
    by their Ditti ID (`ditti_id`). The data includes details such as sleep logs
    and sleep levels, formatted for analysis in an Excel file. The Excel file is
    generated with a timestamped filename and returned to the client
    as a downloadable file.

    Args:
        ditti_id (str): The unique identifier for the participant.

    Returns
    -------
        Response: A downloadable Excel file containing
            the participant's data or an error response in case of failure.
    """
    try:
        stmt = (
            select(
                StudySubject.ditti_id.label("Ditti ID"),
                SleepLog.date_of_sleep.label("Sleep Log Date"),
                SleepLevel.date_time.label("Sleep Level Timestamp"),
                SleepLevel.level.label("Sleep Level Level"),
                SleepLevel.seconds.label("Sleep Level Length (s)"),
            )
            .join(SleepLog, SleepLog.study_subject_id == StudySubject.id)
            .join(SleepLevel, SleepLevel.sleep_log_id == SleepLog.id)
            .where(StudySubject.ditti_id == ditti_id)
            .order_by(StudySubject.ditti_id, SleepLevel.date_time)
        )

        # Execute the query and fetch the results
        results = db.session.execute(stmt).all()

        if len(results) == 0:
            return make_response(
                {"msg": f"Participant with Ditti ID {ditti_id} not found."}, 200
            )

    except Exception:
        logger.error(traceback.format_exc())
        return make_response(
            {"msg": "Internal server error when querying database."}, 500
        )

    try:
        # Convert the results to a Pandas DataFrame
        data = [
            {**dict(row), "Sleep Level Level": row["Sleep Level Level"].value}
            for row in results
        ]
        df = pd.DataFrame(data)

        # Save the DataFrame to a BytesIO object as an Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Participant Data")
        output.seek(0)

        # Generate a timestamped filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Return the Excel file as a response
        return send_file(
            output,
            as_attachment=True,
            download_name=f"{ditti_id}_Fitbit_{timestamp}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except Exception:
        logger.error(traceback.format_exc())
        return make_response("Internal server error when processing data.", 500)


@admin_fitbit_blueprint.route("/download/study/<int:study_id>", methods=["GET"])
@researcher_auth_required("View", "Wearable Dashboard")
@researcher_auth_required("View", "Wearable Data")
def download_fitbit_study(account, study_id: int):
    """
    Download all participant Fitbit API data for a study as an Excel file.

    This endpoint retrieves all Fitbit-related data for participants within a
    study identified by its unique `study_id`. The data includes details such as
    sleep logs and sleep levels for all participants with Ditti IDs that match
    the study's prefix. The results are formatted for analysis in an Excel file.
    The file is generated with a timestamped filename and returned to the client
    as a downloadable file.

    Args:
        study_id (int): The unique identifier for the study.

    Returns
    -------
        Response: A downloadable Excel file containing the study's
        participants' data or an error response in case of failure.
    """
    try:
        stmt = select(Study.ditti_id, Study.acronym).where(Study.id == study_id)

        result = db.session.execute(stmt).first()

        if result is None:
            return make_response(
                {"msg": f"Study with ID {study_id} not found."}, 200
            )

        ditti_prefix = result.ditti_id
        acronym = result.acronym

        stmt = (
            select(
                StudySubject.ditti_id.label("Ditti ID"),
                SleepLog.date_of_sleep.label("Sleep Log Date"),
                SleepLevel.date_time.label("Sleep Level Timestamp"),
                SleepLevel.level.label("Sleep Level Level"),
                SleepLevel.seconds.label("Sleep Level Length (s)"),
            )
            .join(SleepLog, SleepLog.study_subject_id == StudySubject.id)
            .join(SleepLevel, SleepLevel.sleep_log_id == SleepLog.id)
            # Return only exact ditti_prefix matches
            .where(text(f"study_subject.ditti_id ~ '^{ditti_prefix}[0-9]'"))
            .order_by(StudySubject.ditti_id, SleepLevel.date_time)
        )

        results = db.session.execute(stmt).all()

    except Exception:
        logger.error(traceback.format_exc())
        return make_response(
            {"msg": "Internal server error when querying database."}, 500
        )

    try:
        # Convert the results to a Pandas DataFrame
        data = [
            {**dict(row), "Sleep Level Level": row["Sleep Level Level"].value}
            for row in results
        ]
        df = pd.DataFrame(data)

        # Save the DataFrame to a BytesIO object as an Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Participant Data")
        output.seek(0)

        # Generate a timestamped filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Return the Excel file as a response
        return send_file(
            output,
            as_attachment=True,
            download_name=f"{acronym}_Fitbit_{timestamp}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except Exception:
        logger.error(traceback.format_exc())
        return make_response("Internal server error when processing data.", 500)
