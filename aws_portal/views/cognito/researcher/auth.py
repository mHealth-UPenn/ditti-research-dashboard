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
from aws_portal.models import Account
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


@blueprint.route("/callback")
def cognito_callback():
    """
    Handle Cognito's authorization callback.

    Exchange the authorization code for an ID token and access token.
    Verifies the ID token, retrieves or creates the user in the database,
    stores the study subject ID in the session, and sets the tokens as secure cookies.

    Error responses:
        400 - Error fetching tokens, expired token, or invalid token.
    """
    # Retrieve authorization code from the request
    code = request.args.get("code")
    if not code:
        logger.error("Authorization code not provided.")
        return make_response({"msg": "Authorization code not provided."}, 400)

    try:
        response = requests.post(
            f"https://{service.config.domain}/oauth2/token",
            data={
                "grant_type": "authorization_code",
                "client_id": service.config.client_id,
                "client_secret": service.config.client_secret,
                "code": code,
                "redirect_uri": service.config.redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        token_data = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching tokens: {str(e)}")
        return make_response({"msg": "Error fetching tokens."}, 400)

    # Check for Account in database or create a new one
    try:
        id_claims = service.verify_token(
            token_data["id_token"], "id")
        email = id_claims["email"]

        account = Account.query.filter_by(email=email).first()
        if account:
            if account.is_archived:
                logger.warning(
                    f"Attempt to login with archived account: {email}")
                return make_response({"msg": "Account is archived."}, 400)
        else:
            logger.warning(
                f"Attempt to login with nonexistent account: {email}")
            return make_response({"msg": "Authentication error."}, 400)

            # # If no Account exists with the given email, create a new one
            # account = Account(
            #     created_on=datetime.now(timezone.utc),
            #     email=email,
            #     is_archived=False  # Default value
            #     # public_id
            #     # first_name
            #     # last_name
            #     # nullable phone_number
            #     # account.public_id=str(uuid.uuid4())
            # )
            # # Account will have no linked access_groups or studies

            # db.session.add(account)
            # db.session.commit()

        # Store Account ID in session and prepare the response
        # TODO: Unclear if necessary
        session["account_id"] = account.id

        # Redirect to the front-end ParticipantDashboard
        response = make_response(redirect(current_app.config.get(
            'CORS_ORIGINS', 'http://localhost:3000')))

        # Set tokens in secure, HTTP-only cookies
        response.set_cookie(
            "researcher_id_token", token_data["id_token"], httponly=True, secure=True, samesite="None")
        response.set_cookie(
            "researcher_access_token", token_data["access_token"], httponly=True, secure=True, samesite="None")

        return response
    except Exception as e:
        logger.error(f"Auth error: {str(e)}")
        db.session.rollback()
        return make_response({"msg": "Authentication error."}, 400)


@blueprint.route("/logout")
def logout():
    """Log out the user, clear session, and clear Cognito cookies"""
    session.clear()

    logout_url = build_cognito_url("/logout", {
        "client_id": service.config.client_id,
        "logout_uri": service.config.logout_uri,
        "response_type": "code"
    })

    response = make_response(redirect(logout_url))
    response.set_cookie("researcher_id_token", "", expires=0,
                        httponly=True, secure=True, samesite="None")
    response.set_cookie("researcher_access_token", "", expires=0,
                        httponly=True, secure=True, samesite="None")
    return response
