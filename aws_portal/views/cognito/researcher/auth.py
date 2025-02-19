from datetime import datetime, timezone
import logging
from urllib.parse import urlencode
import boto3
from botocore.exceptions import ClientError
from flask import Blueprint, current_app, make_response, redirect, request, session, jsonify
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import requests
from sqlalchemy import select, func
from aws_portal.extensions import db
from aws_portal.models import StudySubject
from aws_portal.utils.cognito.service import get_researcher_service
from aws_portal.utils.auth import auth_required

blueprint = Blueprint("participant_cognito", __name__, url_prefix="/cognito")
logger = logging.getLogger(__name__)
service = get_researcher_service()


def build_cognito_url(path: str, params: dict) -> str:
    """
    Constructs a full URL for Cognito by combining the base domain, path, and query parameters.
    """
    base_url = f"https://{service.config.domain}"
    return f"{base_url}{path}?{urlencode(params)}"


@blueprint.route("/login")
def login():
    """
    Redirect users to the Cognito login page.
    """
    elevated = request.args.get("elevated") == "true"
    scope = "openid" + (" aws.cognito.signin.user.admin" if elevated else "")

    return redirect(build_cognito_url("/login", {
        "client_id": service.config.client_id,
        "response_type": "code",
        "scope": scope,
        "redirect_uri": service.config.redirect_uri,
    }))
