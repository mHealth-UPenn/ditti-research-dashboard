from base64 import b64encode
import logging
import requests
import uuid
from flask import Blueprint, current_app, jsonify, make_response, request, redirect, session
from aws_portal.extensions import db
from aws_portal.models import (
    Api, JoinStudySubjectApi
)
from aws_portal.utils.fitbit import generate_pkce_pair
from aws_portal.utils.secrets_manager import secrets_manager

blueprint = Blueprint("cognito_fitbit", __name__, url_prefix="/cognito/fitbit")
logger = logging.getLogger(__name__)


# TODO: Protected: check for cognito token
@blueprint.route("/authorize")
def fitbit_authorize():
    # Check if user is authenticated
    if "study_subject_id" not in session:
        return redirect("/cognito/login")

    # Generate code verifier and code challenge
    code_verifier, code_challenge = generate_pkce_pair()

    # Save code verifier in session
    session["fitbit_code_verifier"] = code_verifier

    # Build the authorization URL
    fitbit_auth_url = (
        f"https://www.fitbit.com/oauth2/authorize"
        f"?client_id={current_app.config['FITBIT_CLIENT_ID']}"
        f"&response_type=code"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
        f"&scope=sleep%20activity%20heartrate"  # Adjust scopes as needed
        f"&redirect_uri={current_app.config['FITBIT_REDIRECT_URI']}"
    )

    return redirect(fitbit_auth_url)


@blueprint.route("/callback")
def fitbit_callback():
    code = request.args.get("code")
    code_verifier = session.get("fitbit_code_verifier")
    study_subject_id = session.get("study_subject_id")

    if not code or not code_verifier or not study_subject_id:
        msg = "Authorization failed"
        return make_response({"msg": msg}, 400)

    # Exchange authorization code for tokens

    client_credentials = f"{current_app.config["FITBIT_CLIENT_ID"]}:{
        current_app.config["FITBIT_CLIENT_SECRET"]}"
    b64_client_credentials = b64encode(client_credentials.encode()).decode()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {b64_client_credentials}"
    }
    data = {
        "client_id": current_app.config["FITBIT_CLIENT_ID"],
        "grant_type": "authorization_code",
        "code": code,
        "code_verifier": code_verifier,
        "redirect_uri": current_app.config["FITBIT_REDIRECT_URI"]
    }
    token_url = "https://api.fitbit.com/oauth2/token"
    try:
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
    except requests.exceptions.HTTPError as http_err:
        msg = f"HTTP error occurred: {http_err}"
        logger.error(msg)
        return make_response({"msg": msg}, 400)
    except Exception as err:
        msg = f"An error occurred: {err}"
        logger.error(msg)
        return make_response({"msg": msg}, 500)

    if "errors" in token_data:
        msg = f"Error fetching tokens: {token_data["errors"]}"
        return make_response({"msg": msg}, 400)

    # Save tokens to AWS Secrets Manager
    fitbit_api = Api.query.filter_by(name="Fitbit").first()
    if not fitbit_api:
        msg = "Fitbit API not configured."
        logger.error(msg)
        return make_response({"msg": msg}, 500)

    join_entry = JoinStudySubjectApi.query.filter_by(
        study_subject_id=study_subject_id,
        api_id=fitbit_api.id
    ).first()

    if not join_entry:
        # Create new JoinStudySubjectApi entry
        join_entry = JoinStudySubjectApi(
            study_subject_id=study_subject_id,
            api_id=fitbit_api.id,
            api_user_uuid=token_data["user_id"],
            access_key_uuid=str(uuid.uuid4()),
            refresh_key_uuid=str(uuid.uuid4()),
            scope=token_data.get("scope", "")
        )
        db.session.add(join_entry)
    else:
        # Update existing entry
        join_entry.api_user_uuid = token_data["user_id"]
        join_entry.scope = token_data.get("scope", join_entry.scope)

    db.session.commit()

    # Store tokens in Secrets Manager using existing UUIDs
    access_key_uuid = join_entry.access_key_uuid
    refresh_key_uuid = join_entry.refresh_key_uuid

    try:
        secrets_manager.store_secret(
            access_key_uuid, token_data["access_token"])
        secrets_manager.store_secret(
            refresh_key_uuid, token_data["refresh_token"])
    except Exception as e:
        msg = f"Error storing tokens: {str(e)}"
        logger.error(msg)
        return make_response({"msg": msg}, 500)

    # Update scope if necessary (optional)
    join_entry.scope = token_data.get("scope", "")
    db.session.commit()

    # Optionally, store other token metadata if needed (e.g., expires_in, token_type)
    # Since schema cannot be modified, consider using existing fields or AWS Secrets Manager metadata

    msg = "Fitbit Authorized Successfully"
    return redirect("/cognito/fitbit/success")  # Redirect to a success page


@blueprint.route("/success")
def fitbit_success():
    return jsonify({"msg": "Fitbit authorization successful."})
