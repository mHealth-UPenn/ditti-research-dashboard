import logging
from flask import Blueprint, jsonify, make_response, request
from sqlalchemy.exc import SQLAlchemyError
import jwt
from aws_portal.extensions import cache
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
def participant_get_fitbit_data():
    """
    Retrieves Fitbit data for the authenticated participant.

    Query Parameters:
        start_date (str): The start date in 'YYYY-MM-DD' format (required).
        end_date (str, optional): The end date in 'YYYY-MM-DD' format.

    Returns:
        JSON Response: Serialized Fitbit data if found and valid.
        HTTP 400: If input validation or token decoding fails.
        HTTP 401: If the ID token is missing or expired.
        HTTP 404: If the study subject is not found or archived.
        HTTP 500: If a database or server error occurs.
    """
    try:
        # Get ID token from cookies
        id_token = request.cookies.get("id_token")
        if not id_token:
            return make_response({"msg": "Missing ID token."}, 401)

        # Verify and decode ID token to extract cognito:username
        try:
            verify_token(True, id_token, token_use="id")
            claims = jwt.decode(id_token, options={"verify_signature": False})
        except jwt.DecodeError:
            return make_response({"msg": "Invalid ID token."}, 400)
        except jwt.ExpiredSignatureError:
            return make_response({"msg": "ID token has expired."}, 401)
        except jwt.InvalidTokenError as e:
            return make_response({"msg": f"Invalid ID token: {str(e)}"}, 401)

        # Extract cognito:username from claims (ditti_id)
        ditti_id = claims.get("cognito:username")
        if not ditti_id:
            return make_response(
                {"msg": "cognito:username not found in token."}, 400
            )

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
