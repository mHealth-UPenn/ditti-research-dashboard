from flask import Blueprint, current_app, redirect, request, session, jsonify, make_response
from oauthlib.oauth2 import WebApplicationClient
from aws_portal.extensions import db, study_subject_secrets_manager
from aws_portal.models import Api, JoinStudySubjectApi
import uuid
import logging
import time
import os
import base64
import hashlib
import requests

blueprint = Blueprint("cognito_fitbit", __name__, url_prefix="/cognito/fitbit")
logger = logging.getLogger(__name__)

FITBIT_AUTHORIZATION_BASE_URL = 'https://www.fitbit.com/oauth2/authorize'
FITBIT_TOKEN_URL = 'https://api.fitbit.com/oauth2/token'


def generate_code_verifier(length=128):
    """
    Generates a high-entropy cryptographic random string for PKCE.
    """
    if not 43 <= length <= 128:
        raise ValueError("length must be between 43 and 128 characters")
    code_verifier = base64.urlsafe_b64encode(
        os.urandom(length)).rstrip(b'=').decode('utf-8')
    return code_verifier[:length]


def create_code_challenge(code_verifier):
    """
    Creates a S256 code challenge from the code_verifier.
    """
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(
        code_challenge).rstrip(b'=').decode('utf-8')
    return code_challenge


@blueprint.route("/authorize")
def fitbit_authorize():
    # Check if user is authenticated
    if "study_subject_id" not in session:
        return redirect("/cognito/login")

    fitbit_client_id = current_app.config['FITBIT_CLIENT_ID']
    fitbit_redirect_uri = current_app.config['FITBIT_REDIRECT_URI']
    # We only want sleep data so only request the 'sleep' scope
    scopes = ['sleep']

    # Create an OAuth2 WebApplicationClient
    client = WebApplicationClient(fitbit_client_id)

    # Generate code_verifier and code_challenge
    code_verifier = generate_code_verifier()
    code_challenge = create_code_challenge(code_verifier)

    # Generate a random state string
    state = base64.urlsafe_b64encode(
        os.urandom(32)).rstrip(b'=').decode('utf-8')

    # Save code_verifier and state in session
    session['oauth_code_verifier'] = code_verifier
    session['oauth_state'] = state

    # Prepare the authorization URL
    authorization_url = client.prepare_request_uri(
        FITBIT_AUTHORIZATION_BASE_URL,
        redirect_uri=fitbit_redirect_uri,
        scope=scopes,
        state=state,
        code_challenge=code_challenge,
        code_challenge_method='S256',
    )

    logger.debug(f"Authorization URL: {authorization_url}")
    return redirect(authorization_url)


@blueprint.route("/callback")
def fitbit_callback():
    fitbit_client_id = current_app.config['FITBIT_CLIENT_ID']
    fitbit_client_secret = current_app.config['FITBIT_CLIENT_SECRET']
    fitbit_redirect_uri = current_app.config['FITBIT_REDIRECT_URI']

    # Retrieve the saved state and code_verifier
    state = session.get('oauth_state')
    code_verifier = session.get('oauth_code_verifier')
    study_subject_id = session.get('study_subject_id')

    if not state or not code_verifier or not study_subject_id:
        msg = "Authorization failed: Missing state, code_verifier, or study_subject_id"
        logger.error(msg)
        return make_response({"msg": msg}, 400)

    # Check the state parameter
    state_in_request = request.args.get('state')
    if state_in_request != state:
        msg = "State mismatch"
        logger.error(msg)
        return make_response({"msg": msg}, 400)

    # Get the authorization code from the request
    code = request.args.get('code')
    if not code:
        msg = "Authorization code not found"
        logger.error(msg)
        return make_response({"msg": msg}, 400)

    # Create an OAuth2 WebApplicationClient
    client = WebApplicationClient(fitbit_client_id)

    # Prepare the token request
    token_url, headers, body = client.prepare_token_request(
        FITBIT_TOKEN_URL,
        code=code,
        redirect_url=fitbit_redirect_uri,
        code_verifier=code_verifier
    )

    # Include client authentication in the headers (Fitbit requires Basic Auth)
    auth = requests.auth.HTTPBasicAuth(fitbit_client_id, fitbit_client_secret)

    # Send the token request
    try:
        response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=auth,
        )
        response.raise_for_status()
        token = client.parse_request_body_response(response.text)
        logger.debug(f"Token response: {token}")
    except Exception as e:
        msg = f"Failed to fetch token: {e}"
        logger.error(msg)
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
        # Create new JoinStudySubjectApi entry with new UUIDs
        join_entry = JoinStudySubjectApi(
            study_subject_id=study_subject_id,
            api_id=fitbit_api.id,
            api_user_uuid=token.get("user_id"),
            access_key_uuid=str(uuid.uuid4()),
            refresh_key_uuid=str(uuid.uuid4()),
            scope=token.get("scope", "").split()
        )
        db.session.add(join_entry)
    else:
        # Update existing entry
        join_entry.api_user_uuid = token.get("user_id")
        join_entry.scope = token.get("scope", join_entry.scope)

    db.session.commit()

    # Store tokens in Secrets Manager using existing UUIDs
    access_key_uuid = join_entry.access_key_uuid
    refresh_key_uuid = join_entry.refresh_key_uuid

    try:
        # Compute expires_at
        expires_in = token.get("expires_in")
        if expires_in:
            expires_at = int(time.time()) + int(expires_in)
        else:
            expires_at = int(time.time()) + 28800  # Default to 8 hours

        # Prepare access token data
        access_token_data = {
            "access_token": token["access_token"],
            "expires_at": expires_at
        }

        # Prepare refresh token data
        refresh_token_data = {
            "refresh_token": token["refresh_token"]
        }

        # Store access token
        study_subject_secrets_manager.store_secret(
            access_key_uuid, access_token_data, "fb-access"
        )

        # Store refresh token
        study_subject_secrets_manager.store_secret(
            refresh_key_uuid, refresh_token_data, "fb-refresh"
        )
    except Exception as e:
        msg = f"Error storing tokens: {str(e)}"
        logger.error(msg)
        return make_response({"msg": msg}, 500)

    # Redirect to a success page
    return redirect("/cognito/fitbit/success")


@blueprint.route("/success")
def fitbit_success():
    return jsonify({"msg": "Fitbit authorization successful."})
