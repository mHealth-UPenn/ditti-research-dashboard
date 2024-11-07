import base64
import logging
import os
import uuid
import time
import requests
from flask import current_app, Blueprint, jsonify, make_response, redirect, request, session
from oauthlib.oauth2 import WebApplicationClient
from aws_portal.extensions import db, sm
from aws_portal.models import Api, JoinStudySubjectApi
from aws_portal.utils.cognito import cognito_auth_required
from aws_portal.utils.fitbit import (
    generate_code_verifier,
    create_code_challenge,
    get_fitbit_oauth_session
)

blueprint = Blueprint("cognito_fitbit", __name__, url_prefix="/cognito/fitbit")
logger = logging.getLogger(__name__)


@blueprint.route("/authorize")
@cognito_auth_required
def fitbit_authorize():
    """
    Initiates the OAuth2 authorization flow with Fitbit.

    Generates a code verifier and code challenge for PKCE, saves them along with a state parameter in the session,
    constructs the Fitbit authorization URL, and redirects the user to Fitbit's login page.

    Returns:
        Any: A redirect response to Fitbit's authorization URL.
    """
    fitbit_client_id = current_app.config['FITBIT_CLIENT_ID']
    fitbit_redirect_uri = current_app.config['FITBIT_REDIRECT_URI']
    scopes = ['sleep']  # Only request sleep data permission

    # Initialize the OAuth2 client
    client = WebApplicationClient(fitbit_client_id)

    # Generate PKCE code_verifier and code_challenge
    code_verifier = generate_code_verifier()
    code_challenge = create_code_challenge(code_verifier)

    # Generate a random state string for CSRF protection
    state = base64.urlsafe_b64encode(os.urandom(32))\
        .rstrip(b'=')\
        .decode('utf-8')

    # Save code_verifier and state in session for later verification
    session['oauth_code_verifier'] = code_verifier
    session['oauth_state'] = state

    # Prepare the Fitbit authorization URL with necessary parameters
    authorization_url = client.prepare_request_uri(
        "https://www.fitbit.com/oauth2/authorize",
        redirect_uri=fitbit_redirect_uri,
        scope=scopes,
        state=state,
        code_challenge=code_challenge,
        code_challenge_method='S256',
    )

    return redirect(authorization_url)


@blueprint.route("/callback")
@cognito_auth_required
def fitbit_callback():
    """
    Handles the OAuth2 callback from Fitbit after user authorization.

    Exchanges the authorization code for access and refresh tokens, verifies the ID token,
    associates the tokens with the user's study subject record, stores the tokens securely,
    and redirects the user to a success page.

    Returns:
        Any: A redirect response to the Fitbit authorization success page or an error response.
    """
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

    # Verify the state parameter to prevent CSRF attacks
    state_in_request = request.args.get('state')
    if state_in_request != state:
        msg = "State mismatch"
        logger.error(msg)
        return make_response({"msg": msg}, 400)

    # Retrieve the authorization code from the request
    code = request.args.get('code')
    if not code:
        msg = "Authorization code not found"
        logger.error(msg)
        return make_response({"msg": msg}, 400)

    # Initialize the OAuth2 client
    client = WebApplicationClient(fitbit_client_id)

    # Prepare the token request parameters
    token_url, headers, body = client.prepare_token_request(
        "https://api.fitbit.com/oauth2/token",
        code=code,
        redirect_url=fitbit_redirect_uri,
        code_verifier=code_verifier
    )

    # Fitbit requires HTTP Basic Authentication for the token request
    auth = requests.auth.HTTPBasicAuth(fitbit_client_id, fitbit_client_secret)

    # Send the token request to Fitbit
    try:
        response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=auth
        )
        response.raise_for_status()
        token = client.parse_request_body_response(response.text)
    except Exception as e:
        msg = f"Failed to fetch token: {e}"
        logger.error(msg)
        return make_response({"msg": msg}, 400)

    # Retrieve the Fitbit API record from the database
    fitbit_api = Api.query.filter_by(name="Fitbit").first()
    if not fitbit_api:
        msg = "Fitbit API not configured."
        logger.error(msg)
        return make_response({"msg": msg}, 500)

    # Associate the tokens with the study subject's Fitbit API entry
    join_entry = JoinStudySubjectApi.query.filter_by(
        study_subject_id=study_subject_id,
        api_id=fitbit_api.id
    ).first()

    if not join_entry:
        # Create a new association entry if it doesn't exist
        join_entry = JoinStudySubjectApi(
            study_subject_id=study_subject_id,
            api_id=fitbit_api.id,
            api_user_uuid=token.get("user_id"),
            scope=token.get("scope", "")
        )
        db.session.add(join_entry)
    else:
        # Update the existing association entry
        join_entry.api_user_uuid = token.get("user_id")
        join_entry.scope = token.get("scope", join_entry.scope)

    db.session.commit()

    # Prepare the token data
    expires_in = token.get("expires_in")
    if expires_in:
        expires_at = int(time.time()) + int(expires_in)
    else:
        expires_at = int(time.time()) + 28800  # Default to 8 hours

    access_token = token["access_token"]
    refresh_token = token["refresh_token"]

    token_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at
    }

    # Store tokens securely using the updated SecretsManager
    try:
        sm.add_or_update_api_token(
            api_name="Fitbit",
            study_subject_id=study_subject_id,
            tokens=token_data
        )
    except Exception as e:
        msg = f"Error storing tokens: {str(e)}"
        logger.error(msg)
        return make_response({"msg": msg}, 500)

    # Redirect the user to the Fitbit authorization success page
    return redirect("/cognito/fitbit/success")


@blueprint.route("/success")
@cognito_auth_required
def fitbit_success():
    """
    Provides a success message after successful Fitbit authorization.

    Returns:
        Any: A JSON response indicating successful authorization.
    """
    return jsonify({"msg": "Fitbit authorization successful. Try /cognito/fitbit/sleep_list now."})


@blueprint.route("/sleep_list")
@cognito_auth_required
def fitbit_sleep_list():
    """
    Test: Retrieves the user's sleep data from Fitbit.

    Fetches the study subject's Fitbit API session, makes a request to the Fitbit API for sleep data,
    and returns the data as a JSON response.

    Returns:
        Any: A JSON response containing the sleep data.

    Raises:
        Exception: If there is an error retrieving the sleep data.
    """
    study_subject_id = session.get('study_subject_id')
    fitbit_api = Api.query.filter_by(name="Fitbit").first()
    study_subject_fitbit = JoinStudySubjectApi.query.filter_by(
        study_subject_id=study_subject_id,
        api_id=fitbit_api.id
    ).first()
    fitbit_session = get_fitbit_oauth_session(study_subject_fitbit)
    sleep_list_data = fitbit_session.request(
        'GET', 'https://api.fitbit.com/1.2/user/-/sleep/list.json?afterDate=2024-01-01&sort=asc&offset=0&limit=100').json()

    return jsonify(sleep_list_data)
