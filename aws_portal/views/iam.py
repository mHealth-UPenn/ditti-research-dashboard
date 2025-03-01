from datetime import datetime
from flask import Blueprint, jsonify, make_response, request, redirect, url_for
from flask_cors import cross_origin
from aws_portal.auth.decorators import researcher_auth_required
import io
import json
import logging

logger = logging.getLogger(__name__)

blueprint = Blueprint("iam", __name__, url_prefix="/iam")


@blueprint.route("/check-login")
@researcher_auth_required
def check_login(account):
    """
    DEPRECATED: Use /auth/researcher/check-login instead.

    This endpoint now redirects to the new implementation.
    """
    logger.warning(
        "Deprecated endpoint /iam/check-login used. Use /auth/researcher/check-login instead.")
    return redirect(url_for("researcher_auth.check_login"))


@blueprint.route("/login", methods=["POST"])
@cross_origin(
    allow_headers=["Authorization", "Content-Type", "X-CSRF-TOKEN"],
    supports_credentials=True
)
def login():
    """
    DEPRECATED: Use /auth/researcher/login instead.

    This login method is no longer supported. The application now uses Cognito authentication.
    """
    logger.warning(
        "Deprecated endpoint /iam/login used. Use /auth/researcher/login instead.")
    return make_response({
        "msg": "This login method is deprecated. Please use Cognito authentication at /auth/researcher/login"
    }, 410)  # 410 Gone


@blueprint.route("/logout", methods=["POST"])
@researcher_auth_required
def logout(account):
    """
    DEPRECATED: Use /auth/researcher/logout instead.

    This endpoint now redirects to the new implementation.
    """
    logger.warning(
        "Deprecated endpoint /iam/logout used. Use /auth/researcher/logout instead.")
    return redirect(url_for("researcher_auth.logout"))


@blueprint.route("/set-password", methods=["POST"])
@researcher_auth_required
def set_password(account):
    """
    DEPRECATED: Use /auth/researcher/change-password instead.

    This endpoint transforms the request to match the new API and redirects to it.
    """
    logger.warning(
        "Deprecated endpoint /iam/set-password used. Use /auth/researcher/change-password instead.")

    # Convert the old request format to the new format
    if request.json and request.json.get("password"):
        # Transform the request to match the new expected format
        # Create a new request body in the format expected by the new endpoint
        new_body = {
            "newPassword": request.json.get("password")
        }

        # Convert to JSON string and create a custom response object
        request.environ["wsgi.input"] = io.BytesIO(
            json.dumps(new_body).encode("utf-8"))
        request.environ["CONTENT_LENGTH"] = len(json.dumps(new_body))
        request.environ["CONTENT_TYPE"] = "application/json"

        # Redirect to the new endpoint, preserving the method
        return redirect(url_for("researcher_auth.change_password"), code=307)
    else:
        return make_response({"msg": "Password is required"}, 400)


@blueprint.route("/get-access")
@researcher_auth_required
def get_access(account):
    """
    DEPRECATED: Use /auth/researcher/get-access instead.

    This endpoint now redirects to the new implementation.
    """
    logger.warning(
        "Deprecated endpoint /iam/get-access used. Use /auth/researcher/get-access instead.")
    return redirect(url_for("researcher_auth.get_access", **request.args))
