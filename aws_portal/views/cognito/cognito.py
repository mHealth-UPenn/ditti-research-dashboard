import jwt
import logging
import requests
from datetime import datetime, timezone
from flask import Blueprint, current_app, make_response, redirect, request, session
from aws_portal.extensions import db
from aws_portal.models import StudySubject
from aws_portal.utils.cognito import get_public_key, decode_token

blueprint = Blueprint("cognito", __name__, url_prefix="/cognito")
logger = logging.getLogger(__name__)


@blueprint.route("/login")
def login():
    cognito_auth_url = (
        f"https://{current_app.config['COGNITO_DOMAIN']}/login"
        f"?client_id={current_app.config['COGNITO_CLIENT_ID']}"
        f"&response_type=code"
        f"&scope=openid+email"
        f"&redirect_uri={current_app.config['COGNITO_REDIRECT_URI']}"
    )
    return redirect(cognito_auth_url)


@blueprint.route("/callback")
def cognito_callback():
    code = request.args.get("code")

    token_url = f"https://{current_app.config['COGNITO_DOMAIN']}/oauth2/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": current_app.config["COGNITO_CLIENT_ID"],
        "client_secret": current_app.config["COGNITO_CLIENT_SECRET"],
        "code": code,
        "redirect_uri": current_app.config["COGNITO_REDIRECT_URI"],
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(token_url, data=data, headers=headers)
    response.raise_for_status()
    token_data = response.json()

    if "id_token" not in token_data or "access_token" not in token_data:
        logger.error("Error fetching tokens.")
        return make_response({"msg": "Error fetching tokens."}, 400)

    id_token = token_data["id_token"]
    access_token = token_data["access_token"]

    # Decode and verify ID token
    try:
        public_key = get_public_key(id_token)
        issuer = f"https://cognito-idp.{current_app.config['COGNITO_DOMAIN'].split(
            '.')[2]}.amazonaws.com/{current_app.config['COGNITO_USER_POOL_ID']}"
        claims = decode_token(
            id_token,
            public_key,
            audience=current_app.config["COGNITO_CLIENT_ID"],
            issuer=issuer
        )
        if claims.get("token_use") != "id":
            raise jwt.InvalidTokenError('Invalid token_use. Expected "id".')

    except jwt.ExpiredSignatureError:
        return make_response({"msg": "Token has expired."}, 400)
    except jwt.InvalidTokenError as e:
        return make_response({"msg": f"Invalid token: {str(e)}"}, 400)

    email = claims.get("email")

    # Check for study subject in database or create a new one
    study_subject = StudySubject.query.filter_by(email=email).first()
    if not study_subject:
        study_subject = StudySubject(created_on=datetime.now(
            timezone.utc), email=email, is_confirmed=True)
        db.session.add(study_subject)
        db.session.commit()

    session["study_subject_id"] = study_subject.id
    response = make_response(redirect("/cognito/fitbit/authorize"))

    # Set tokens in secure cookies
    response.set_cookie("id_token", id_token, httponly=True,
                        secure=True, samesite="Lax")
    response.set_cookie("access_token", access_token,
                        httponly=True, secure=True, samesite="Lax")

    return response


@blueprint.route("/logout")
def logout():
    session.clear()
    response = make_response(
        redirect(
            f"https://{current_app.config['COGNITO_DOMAIN']}/logout"
            f"?client_id={current_app.config['COGNITO_CLIENT_ID']}"
            f"&response_type=code"
            f"&scope=openid+email"
            f"&redirect_uri={current_app.config['COGNITO_REDIRECT_URI']}"
        )
    )
    response.set_cookie("id_token", "", expires=0)
    response.set_cookie("access_token", "", expires=0)
    return response
