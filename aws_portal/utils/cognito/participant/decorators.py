from functools import wraps
import logging
from flask import current_app, make_response, request
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy import select, func
from aws_portal.extensions import db
from aws_portal.models import StudySubject
from aws_portal.utils.cognito.service import get_participant_service

logger = logging.getLogger(__name__)


def participant_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        service = get_participant_service()
        id_token = request.cookies.get("id_token")
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        if not id_token or not access_token:
            return make_response({"msg": "Missing authentication tokens."}, 401)

        # Verify access token and handle token refresh if expired
        try:
            service.verify_token(access_token, "access")
        except ExpiredSignatureError:
            # Attempt to refresh access token if expired
            if not refresh_token:
                return make_response({"msg": "Missing refresh token."}, 401)
            try:
                # Refresh the access token
                new_access_token = service.refresh_access_token(refresh_token)
                service.verify_token(new_access_token, "access")
                response = make_response()
                response.set_cookie(
                    "access_token", new_access_token, httponly=True, secure=True)
                access_token = new_access_token
            except InvalidTokenError as e:
                logger.error(f"Refresh token invalid: {str(e)}")
                return make_response({"msg": f"Invalid token: {str(e)}"}, 401)
            except Exception as e:
                logger.error(f"Failed to refresh token: {str(e)}")
                return make_response({"msg": f"Failed to refresh token."}, 401)
        except InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            return make_response({"msg": f"Invalid token: {str(e)}"}, 401)

        try:
            claims = service.verify_token(id_token, "id")
            cognito_username = claims.get("cognito:username")
            stmt = select(StudySubject.ditti_id).where(
                func.lower(StudySubject.ditti_id) == cognito_username)
            ditti_id = db.session.execute(stmt).scalar()

            if not ditti_id:
                logger.error(f"Participant {cognito_username} not found.")
                return make_response({"msg": "Participant not found."}, 400)

            return f(*args, ditti_id=ditti_id, **kwargs)
        except ExpiredSignatureError as e:
            logger.error(f"Token expired: {str(e)}")
            return make_response({"msg": "Token expired."}, 401)
        except InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            return make_response({"msg": f"Invalid token: {str(e)}"}, 401)

    return decorated
