from functools import wraps
import logging
from flask import make_response, request
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy import select, func
from aws_portal.extensions import db
from aws_portal.models import Account
from aws_portal.utils.cognito.service import get_researcher_service

logger = logging.getLogger(__name__)


def researcher_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        service = get_researcher_service()
        id_token = request.cookies.get("researcher_id_token")
        access_token = request.cookies.get("researcher_access_token")
        refresh_token = request.cookies.get("researcher_refresh_token")

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
                    "researcher_access_token", new_access_token, httponly=True, secure=True)
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
            email = claims.get("email")

            if not email:
                return make_response({"msg": "email not found in token."}, 400)

            # Cognito stores ditti IDs in lowercase, so retrieve actual ditti ID from the database instead.
            # TODO: Check if necessary
            try:
                stmt = select(Account.email).where(
                    func.lower(Account.email) == email)
                email = db.session.execute(stmt).scalar()
            except Exception as e:
                logger.error(f"Database error: {str(e)}")
                return make_response({"msg": f"Database error."}, 500)

            if not email:
                logger.error(f"Researcher {email} not found.")
                return make_response({"msg": "Researcher not found."}, 400)

            # Pass `email` to the decorated function
            return f(*args, email=email, **kwargs)
        except ExpiredSignatureError as e:
            logger.error(f"Token expired: {str(e)}")
            return make_response({"msg": "Token expired."}, 401)
        except InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            return make_response({"msg": f"Invalid token."}, 401)

    return decorated


def researcher_db_auth_required(action, resource=None):
    """
    Verifies Cognito tokens (via researcher_auth_required) and then checks 
    the old DB-based permissions for the given action/resource.
    """
    def decorator(f):
        @researcher_auth_required
        def wrapper(*args, email=None, **kwargs):
            # Fetch the Account for the verified email
            account = db.session.query(Account)\
                .filter_by(email=email, is_archived=False)\
                .first()
            if not account:
                return make_response({"msg": "User account not found."}, 404)

            # Just like in auth_required, gather app_id / study_id
            # from request.args or request.json (adjust as needed)
            data = request.args or request.json or {}
            app_id = data.get("app")
            study_id = data.get("study")
            # If resource was not passed, we might read resource from the request
            this_resource = resource or data.get("resource")

            # Check if user has needed permissions
            try:
                permissions = account.get_permissions(app_id, study_id)
                account.validate_ask(action, this_resource, permissions)

            except ValueError:
                # The user doesn't have permission
                return make_response({"msg": "Unauthorized"}, 403)

            # If everything is okay, call the original endpoint
            return f(*args, **kwargs)
        return wrapper
    return decorator
