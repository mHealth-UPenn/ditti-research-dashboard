import jwt
import logging
import requests
from datetime import datetime, timezone
from flask import (
    Blueprint, current_app, make_response, redirect, request, session
)
from urllib.parse import urlencode
from aws_portal.extensions import db
from aws_portal.models import StudySubject
from aws_portal.utils.cognito import verify_token

blueprint = Blueprint("cognito", __name__, url_prefix="/cognito")
logger = logging.getLogger(__name__)


def build_cognito_url(path: str, params: dict) -> str:
    """
    Constructs a full URL for AWS Cognito by combining the base domain, path, and query parameters.
    """
    base_url = f"https://{current_app.config['COGNITO_DOMAIN']}"
    query_string = urlencode(params)
    return f"{base_url}{path}?{query_string}"


@blueprint.route("/login")
def login():
    """
    Redirect users to the Cognito login page.
    """
    cognito_auth_url = build_cognito_url("/login", {
        "client_id": current_app.config['COGNITO_CLIENT_ID'],
        "response_type": "code",
        # TODO: Make user reauthenticate to add scope to delete account
        "scope": "openid email aws.cognito.signin.user.admin",
        "redirect_uri": current_app.config['COGNITO_REDIRECT_URI'],
    })
    return redirect(cognito_auth_url)


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

    # Construct token endpoint and request parameters
    cognito_domain = current_app.config['COGNITO_DOMAIN']
    token_issuer_endpoint = f"https://{cognito_domain}/oauth2/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": current_app.config["COGNITO_CLIENT_ID"],
        "client_secret": current_app.config["COGNITO_CLIENT_SECRET"],
        "code": code,
        "redirect_uri": current_app.config["COGNITO_REDIRECT_URI"],
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # Request tokens from Cognito
    response = requests.post(token_issuer_endpoint, data=data, headers=headers)
    response.raise_for_status()
    token_data = response.json()

    # Validate response and ensure required tokens are present
    if "id_token" not in token_data or "access_token" not in token_data:
        logger.error("Error fetching tokens.")
        return make_response({"msg": "Error fetching tokens."}, 400)

    id_token = token_data["id_token"]
    access_token = token_data["access_token"]

    # Decode and verify ID token
    try:
        claims = verify_token(id_token, token_use="id")

    except jwt.ExpiredSignatureError:
        return make_response({"msg": "Token has expired."}, 400)
    except jwt.InvalidTokenError as e:
        return make_response({"msg": f"Invalid token: {str(e)}"}, 400)

    # Get the user's email from token claims
    email = claims.get("email")

    # Check for study subject in database or create a new one
    study_subject = StudySubject.query.filter_by(email=email).first()
    if study_subject:
        if study_subject.is_archived:
            return make_response({"msg": f"Account archived: {str(e)}"}, 400)
    else:
        # If no StudySubject exists with the given email, create a new one
        study_subject = StudySubject(
            created_on=datetime.now(timezone.utc),
            email=email,
            is_confirmed=True  # handled by Cognito already
        )
        db.session.add(study_subject)
        db.session.commit()

    # Store study subject ID in session and prepare the response
    session["study_subject_id"] = study_subject.id

    # Redirect to the front-end PartitipantDashboard
    frontend_base_url = current_app.config.get(
        'CORS_ORIGINS', 'http://localhost:3000')
    redirect_url = f"{frontend_base_url}/participant"

    response = make_response(redirect(redirect_url))

    # Set tokens in secure, HTTP-only cookies
    response.set_cookie(
        "id_token", id_token, httponly=True, secure=True, samesite="Lax"
    )
    response.set_cookie(
        "access_token", access_token, httponly=True, secure=True, samesite="Lax"
    )

    return response


@blueprint.route("/logout")
def logout():
    """
    Log out the user from the application and Cognito.

    Clears the session, redirects to the Cognito logout URL, and removes
    ID and access tokens from cookies by setting their expiration to zero.
    """
    session.clear()

    cognito_logout_url = build_cognito_url("/logout", {
        "client_id": current_app.config['COGNITO_CLIENT_ID'],
        "logout_uri": current_app.config['COGNITO_LOGOUT_URI'],
        "response_type": "code"
    })

    response = make_response(redirect(cognito_logout_url))

    # Remove cookies by setting them to expire immediately
    response.set_cookie("id_token", "", expires=0)
    response.set_cookie("access_token", "", expires=0)

    return response


@blueprint.route("/check-login", methods=["GET"])
def check_login():
    """
    Checks if the user is authenticated via Cognito.
    """
    id_token = request.cookies.get('id_token')
    if not id_token:
        return make_response({"msg": "Not authenticated"}, 401)

    try:
        claims = verify_token(id_token, token_use="id")
        return make_response({"msg": "Login successful"}, 200)
    except jwt.ExpiredSignatureError:
        return make_response({"msg": "Token has expired."}, 401)
    except jwt.InvalidTokenError as e:
        return make_response({"msg": f"Invalid token: {str(e)}"}, 401)
