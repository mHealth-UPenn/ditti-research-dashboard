from datetime import datetime, timezone
import json
import logging
import requests
from flask import Blueprint, current_app, jsonify, make_response, request, redirect, session
from aws_portal.extensions import db
from aws_portal.models import StudySubject
import jwt
from functools import lru_cache

blueprint = Blueprint("cognito", __name__, url_prefix="/cognito")
logger = logging.getLogger(__name__)


@lru_cache()
def get_cognito_jwks():
    keys_url = f"https://cognito-idp.{current_app.config['COGNITO_DOMAIN'].split(
        ".")[2]}.amazonaws.com/{current_app.config['COGNITO_USER_POOL_ID']}/.well-known/jwks.json"
    response = requests.get(keys_url)
    response.raise_for_status()
    return response.json()


def get_public_key(token):
    try:
        jwks = get_cognito_jwks()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header["kid"]
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if key is None:
            # Possible key rotation, clear cache and retry
            get_cognito_jwks.cache_clear()
            jwks = get_cognito_jwks()
            key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
            if key is None:
                raise jwt.exceptions.InvalidTokenError(
                    "Public key not found in JWKS after cache clear.")
        return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
    except Exception as e:
        logger.error(f"Error retrieving public key: {str(e)}")
        raise


@blueprint.route("/login")
def login():
    cognito_auth_url = (
        f"https://{current_app.config['COGNITO_DOMAIN']}/login"
        f"?client_id={current_app.config['COGNITO_CLIENT_ID']}"
        f"&response_type=code"
        f"&scope=openid+email"
        f"&redirect_uri={current_app.config['COGNITO_REDIRECT_URI']}"
    )
    # msg = "Token has expired."
    # return make_response({"msg": msg}, 400)
    return redirect(cognito_auth_url)


# TODO: Align more with Lexica code
# TODO: somewhere add Cognito token to cookies for API authorization route
# https://github.com/JStover95/lexica
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
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(token_url, data=data, headers=headers)
    token_data = response.json()

    if "id_token" not in token_data:
        msg = "Error fetching tokens."
        logger.error(f"Token data: {token_data}")
        return make_response({"msg": msg}, 400)

    # Decode and verify ID token using PyJWT
    id_token = token_data.get("id_token")
    try:
        public_key = get_public_key(id_token)
        claims = jwt.decode(
            id_token,
            public_key,
            algorithms=["RS256"],
            audience=current_app.config["COGNITO_CLIENT_ID"],
            issuer=f"https://cognito-idp.{current_app.config["COGNITO_DOMAIN"].split(
                ".")[2]}.amazonaws.com/{current_app.config["COGNITO_USER_POOL_ID"]}"
        )

        # Verify the token_use claim
        if claims.get("token_use") != "id":
            raise jwt.InvalidTokenError("Invalid token_use. Expected \"id\".")
    except jwt.ExpiredSignatureError:
        msg = "Token has expired."
        logger.error(msg)
        return make_response({"msg": msg}, 400)
    except jwt.InvalidTokenError as e:
        msg = f"Invalid token: {str(e)}"
        logger.error(msg)
        return make_response({"msg": msg}, 400)

    email = claims.get("email")

    if not email:
        msg = "Email not found in token."
        logger.error(msg)
        return make_response({"msg": msg}, 400)

    # Check if the study subject exists in your database
    study_subject = StudySubject.query.filter_by(email=email).first()
    if not study_subject:
        # Create a new study subject
        study_subject = StudySubject(
            created_on=datetime.now(timezone.utc),
            email=email,
            is_confirmed=True
        )
        db.session.add(study_subject)
        db.session.commit()

    # Log the user in (set session variables)
    session["study_subject_id"] = study_subject.id

    # TODO: Redirect back to user settings page to choose which API to link
    # Add cookie headers to response with access and refresh tokens

    # Redirect to the Fitbit authorization route
    return redirect("/cognito/fitbit/authorize")


@blueprint.route("/logout")
def logout():
    session.clear()
    return redirect(
        f"https://{current_app.config['COGNITO_DOMAIN']}/logout"
        f"?client_id={current_app.config['COGNITO_CLIENT_ID']}"
        f"&logout_uri={current_app.config['COGNITO_LOGOUT_REDIRECT_URI']}"
    )


@blueprint.route("/logout_success")
def logout_success():
    return jsonify({"msg": "Successfully logged out."})
