from datetime import datetime, timezone
import logging
from urllib.parse import urlencode

import boto3
from botocore.exceptions import ClientError
from flask import Blueprint, current_app, make_response, redirect, request, session, jsonify
import jwt
import requests
from sqlalchemy import select, func

from aws_portal.extensions import db
from aws_portal.models import StudySubject
from aws_portal.utils.cognito import verify_token
from aws_portal.utils.auth import auth_required

blueprint = Blueprint("cognito", __name__, url_prefix="/cognito")
logger = logging.getLogger(__name__)


def build_cognito_url(participant_pool: bool, path: str, params: dict) -> str:
    """
    Constructs a full URL for AWS Cognito by combining the base domain, path, and query parameters.
    """
    if not participant_pool:
        raise ValueError("Only participant pool is supported at this time.")
    base_url = f"https://{current_app.config['COGNITO_PARTICIPANT_DOMAIN']}"
    query_string = urlencode(params)
    return f"{base_url}{path}?{query_string}"


@blueprint.route("/login")
def login():
    """
    Redirect users to the Cognito login page.
    """
    elevated = request.args.get("elevated") == "true"
    scope = "openid"
    if elevated:
        scope += " aws.cognito.signin.user.admin"

    cognito_auth_url = build_cognito_url(True, "/login", {
        "client_id": current_app.config['COGNITO_PARTICIPANT_CLIENT_ID'],
        "response_type": "code",
        "scope": scope,
        "redirect_uri": current_app.config['COGNITO_PARTICIPANT_REDIRECT_URI'],
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
    if not code:
        logger.error("Authorization code not provided.")
        return make_response({"msg": "Authorization code not provided."}, 400)

    # Construct token endpoint and request parameters
    cognito_domain = current_app.config["COGNITO_PARTICIPANT_DOMAIN"]
    token_issuer_endpoint = f"https://{cognito_domain}/oauth2/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": current_app.config["COGNITO_PARTICIPANT_CLIENT_ID"],
        "client_secret": current_app.config["COGNITO_PARTICIPANT_CLIENT_SECRET"],
        "code": code,
        "redirect_uri": current_app.config["COGNITO_PARTICIPANT_REDIRECT_URI"],
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        # Request tokens from Cognito
        response = requests.post(
            token_issuer_endpoint, data=data, headers=headers)
        response.raise_for_status()
        token_data = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching tokens: {str(e)}")
        return make_response({"msg": "Error fetching tokens."}, 400)

    # Validate response and ensure required tokens are present
    if "id_token" not in token_data or "access_token" not in token_data:
        logger.error("Missing tokens in response.")
        return make_response({"msg": "Error fetching tokens."}, 400)

    id_token = token_data["id_token"]
    access_token = token_data["access_token"]

    # Decode and verify ID token
    try:
        claims = verify_token(True, id_token, token_use="id")
    except jwt.ExpiredSignatureError:
        logger.warning("ID token has expired.")
        return make_response({"msg": "Token has expired."}, 400)
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid ID token: {str(e)}")
        return make_response({"msg": f"Invalid token: {str(e)}"}, 400)

    # Get the user's ditti_id from token claims
    ditti_id = claims.get("cognito:username")
    if not ditti_id:
        logger.error("ditti_id not found in token claims.")
        return make_response({"msg": "ditti_id not found in token claims."}, 400)

    # Check for study subject in database or create a new one
    try:
        study_subject = StudySubject.query.filter_by(ditti_id=ditti_id).first()
        if study_subject:
            if study_subject.is_archived:
                logger.warning(
                    f"Attempt to login with archived account: {ditti_id}")
                return make_response({"msg": "Account is archived."}, 400)
        else:
            # If no StudySubject exists with the given ditti_id, create a new one
            study_subject = StudySubject(
                created_on=datetime.now(timezone.utc),
                ditti_id=ditti_id,
                is_archived=False  # Default value
            )
            db.session.add(study_subject)
            db.session.commit()
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        db.session.rollback()
        return make_response({"msg": "Database error."}, 500)

    # Store study subject ID in session and prepare the response
    session["study_subject_id"] = study_subject.id

    # Redirect to the front-end ParticipantDashboard
    frontend_base_url = current_app.config.get(
        'CORS_ORIGINS', 'http://localhost:3000')
    redirect_url = frontend_base_url

    response = make_response(redirect(redirect_url))

    # Set tokens in secure, HTTP-only cookies
    response.set_cookie(
        "id_token", id_token, httponly=True, secure=True, samesite="None"
    )
    response.set_cookie(
        "access_token", access_token, httponly=True, secure=True, samesite="None"
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

    cognito_logout_url = build_cognito_url(True, "/logout", {
        "client_id": current_app.config["COGNITO_PARTICIPANT_CLIENT_ID"],
        "logout_uri": current_app.config["COGNITO_PARTICIPANT_LOGOUT_URI"],
        "response_type": "code"
    })

    response = make_response(redirect(cognito_logout_url))

    # Remove cookies by setting them to expire immediately
    response.set_cookie("id_token", "", expires=0,
                        httponly=True, secure=True, samesite="None")
    response.set_cookie("access_token", "", expires=0,
                        httponly=True, secure=True, samesite="None")

    return response


@blueprint.route("/check-login", methods=["GET"])
def check_login():
    """
    Checks if the user is authenticated via Cognito.

    If they are authenticated, returns the user's ditti_id from the database.
    """
    id_token = request.cookies.get("id_token")
    if not id_token:
        return make_response({"msg": "Not authenticated"}, 401)

    try:
        claims = verify_token(True, id_token, token_use="id")
        cognito_ditti_id = claims.get("cognito:username")

        if not cognito_ditti_id:
            return make_response({"msg": "cognito:username not found in token."}, 400)

        # Cognito stores ditti IDs in lowercase, so retrieve actual ditti ID from the database instead.
        stmt = select(StudySubject.ditti_id)\
            .where(func.lower(StudySubject.ditti_id) == cognito_ditti_id)
        ditti_id = db.session.execute(stmt).scalar()

        if ditti_id is None:
            logger.warning(f"Participant with cognito:username {cognito_ditti_id} not found in database.")
            return make_response({"msg": f"Participant {cognito_ditti_id} not found."}, 400)

        body = {
            "msg": "Login successful",
            "dittiId": ditti_id,
        }

        return make_response(body, 200)
    except jwt.ExpiredSignatureError:
        logger.warning("ID token has expired.")
        return make_response({"msg": "Token has expired."}, 401)
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid ID token: {str(e)}")
        return make_response({"msg": f"Invalid token: {str(e)}"}, 401)


@blueprint.route("/register/participant", methods=["POST"])
@auth_required("Create", "Participants")
def register_participant():
    client = boto3.client("cognito-idp")
    try:
        # Validate incoming request
        data = request.json.get("data")
        cognito_username = data.get("cognitoUsername")
        temporary_password = data.get("temporaryPassword")

        if not cognito_username or not temporary_password:
            return jsonify({"error": "Cognito username and temporary password are required."}), 400

        # Create user in Cognito
        client.admin_create_user(
            UserPoolId=current_app.config["COGNITO_PARTICIPANT_USER_POOL_ID"],
            Username=cognito_username,
            TemporaryPassword=temporary_password,
            MessageAction="SUPPRESS"
        )

        return jsonify({"msg": "Participant registered with AWS Cognito successfully."}), 201

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        return jsonify({"msg": f"AWS Cognito error: {error_code}"}), 500
    except Exception as e:
        return jsonify({"msg": "An unexpected error occurred."}), 500
