import logging

from flask import Blueprint, jsonify, make_response, request
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
import jwt

from aws_portal.extensions import cache, db
from aws_portal.models import Study, StudySubject, SleepLog, SleepLevel
from aws_portal.utils.cognito import cognito_auth_required, verify_token
from aws_portal.utils.auth import auth_required
from aws_portal.utils.fitbit_data import (
    validate_date_range,
    cache_key_admin,
    cache_key_participant,
    get_fitbit_data_for_subject
)

admin_fitbit_blueprint = Blueprint(
    "admin_fitbit_data",
    __name__,
    url_prefix="/admin/fitbit_data"
)

participant_fitbit_blueprint = Blueprint(
    "participant_fitbit_data",
    __name__,
    url_prefix="/participant/fitbit_data"
)

logger = logging.getLogger(__name__)


@admin_fitbit_blueprint.route("/<string:ditti_id>", methods=["GET"])
@auth_required("View", "Admin Dashboard")
@auth_required("View", "Fitbit Data")
def admin_get_fitbit_data(ditti_id: str):
    """
    Retrieves Fitbit data for a specific study subject as an admin.

    URL Parameters:
        ditti_id (str): The unique ID of the study subject.

    Query Parameters:
        start_date (str): The start date in 'YYYY-MM-DD' format (required).
        end_date (str, optional): The end date in 'YYYY-MM-DD' format.

    Returns:
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
            f"{str(db_err)}"
        )
        return make_response(
            {"msg": "Database error retrieving Fitbit data."}, 500
        )
    except Exception as e:
        logger.error(f"Unhandled error in admin_get_fitbit_data: {str(e)}")
        return make_response({"msg": "Unexpected server error."}, 500)


@participant_fitbit_blueprint.route("", methods=["GET"])
@cognito_auth_required
def participant_get_fitbit_data(ditti_id: str):
    """
    Retrieves Fitbit data for the authenticated participant.

    Query Parameters:
        start_date (str): The start date in 'YYYY-MM-DD' format (required).
        end_date (str, optional): The end date in 'YYYY-MM-DD' format.

    Args:
        ditti_id (str): The study subject's username, passed from cognito_auth_required.

    Returns:
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
            f"{str(db_err)}"
        )
        return make_response(
            {"msg": "Database error retrieving Fitbit data."}, 500
        )
    except Exception as e:
        logger.error(
            f"Unhandled error in participant_get_fitbit_data: {str(e)}"
        )
        return make_response({"msg": "Unexpected server error."}, 500)


@admin_fitbit_blueprint.route("/download/participant/<string:ditti_id>", methods=["GET"])
# @auth_required("View", "Wearable Dashboard")
# @auth_required("View", "Wearable Data")
def download_fitbit_participant(ditti_id: str):
    """
    Fetch all Fitbit API data from the database for either one study or one study subject. Return the fetched data
    in a format prepared for rapid analysis via Excel download.
    """
    stmt = (
        select(
            StudySubject.ditti_id,
            SleepLog.date_of_sleep,
            SleepLevel.date_time.label("level_date_time"),
            SleepLevel.level.label("level_level"),
            SleepLevel.seconds.label("level_seconds")
        )
        .where(StudySubject.ditti_id == ditti_id)
        .order_by(StudySubject.ditti_id, SleepLevel.date_time)
    )

    results = db.session.execute(stmt).all()

    print(len(results))
    for res in results[:5]:
        print(res)

    return make_response(str(len(results)), 200)


@admin_fitbit_blueprint.route("/download/study/<int:study_id>", methods=["GET"])
# @auth_required("View", "Wearable Dashboard")
# @auth_required("View", "Wearable Data")
def download_fitbit_study(study_id: int):
    """
    """
    stmt = (
        select(Study.ditti_id)
        .where(Study.id == study_id)
    )

    ditti_prefix = db.session.execute(stmt).scalar()

    stmt = (
        select(
            StudySubject.ditti_id,
            SleepLog.date_of_sleep,
            SleepLevel.date_time.label("level_date_time"),
            SleepLevel.level.label("level_level"),
            SleepLevel.seconds.label("level_seconds")
        )
        .where(text(f"study_subject.ditti_id ~ '^{ditti_prefix}[0-9]'"))
        .order_by(StudySubject.ditti_id, SleepLevel.date_time)
    )

    results = db.session.execute(stmt).all()

    print(len(results))
    for res in results[:5]:
        print(res)

    return make_response(str(len(results)), 200)
