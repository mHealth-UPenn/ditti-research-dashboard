# Ditti Research Dashboard
# Copyright (C) 2025 the Trustees of the University of Pennsylvania
#
# Ditti Research Dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Ditti Research Dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import base64
import logging
import os
import time

import requests
from flask import (
    Blueprint,
    current_app,
    jsonify,
    make_response,
    redirect,
    request,
    session,
)
from oauthlib.oauth2 import WebApplicationClient

from backend.auth.decorators import participant_auth_required
from backend.extensions import db, tm
from backend.models import Api, JoinStudySubjectApi, StudySubject
from shared.fitbit import (
    create_code_challenge,
    generate_code_verifier,
    get_fitbit_oauth_session,
)

blueprint = Blueprint("api_fitbit", __name__, url_prefix="/api/fitbit")
logger = logging.getLogger(__name__)


@blueprint.route("/authorize")
@participant_auth_required
def fitbit_authorize():
    """
    Initiate the OAuth2 authorization flow with Fitbit.

    Generates a code verifier and code challenge for PKCE,
    saves them along with a state parameter in the session,
    constructs the Fitbit authorization URL,
    and redirects the user to Fitbit's login page.

    Returns
    -------
        Any: A redirect response to Fitbit's authorization URL.
    """
    try:
        fitbit_client_id = current_app.config["FITBIT_CLIENT_ID"]
        fitbit_redirect_uri = current_app.config["FITBIT_REDIRECT_URI"]
        scopes = ["sleep"]  # Only request sleep data permission

        # Initialize the OAuth2 client
        client = WebApplicationClient(fitbit_client_id)

        # Generate PKCE code_verifier and code_challenge
        code_verifier = generate_code_verifier()
        code_challenge = create_code_challenge(code_verifier)

        # Generate a random state string for CSRF protection
        state = (
            base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode("utf-8")
        )

        # Save code_verifier and state in session for later verification
        session["oauth_code_verifier"] = code_verifier
        session["oauth_state"] = state

        # Prepare the Fitbit authorization URL with necessary parameters
        authorization_url = client.prepare_request_uri(
            "https://www.fitbit.com/oauth2/authorize",
            redirect_uri=fitbit_redirect_uri,
            scope=scopes,
            state=state,
            code_challenge=code_challenge,
            code_challenge_method="S256",
        )

        return redirect(authorization_url)
    except Exception as e:
        logger.error(f"Error initiating Fitbit authorization: {e!s}")
        return make_response(
            {"msg": "Failed to initiate Fitbit authorization."}, 500
        )


@blueprint.route("/callback")
@participant_auth_required
def fitbit_callback(ditti_id: str):
    """
    Handle the OAuth2 callback from Fitbit after user authorization.

    Exchanges the authorization code for access and refresh tokens,
    verifies the ID token, associates the tokens with the user's
    study subject record, stores the tokens securely,
    and redirects the user to a success page.

    Args:
        ditti_id (str): The username of the study subject,
            provided by the decorator.

    Returns
    -------
        Any: A redirect response to the Fitbit authorization success page
            or an error response.
    """
    try:
        fitbit_client_id = current_app.config["FITBIT_CLIENT_ID"]
        fitbit_client_secret = current_app.config["FITBIT_CLIENT_SECRET"]
        fitbit_redirect_uri = current_app.config["FITBIT_REDIRECT_URI"]

        # Retrieve the saved state and code_verifier
        state = session.get("oauth_state")
        code_verifier = session.get("oauth_code_verifier")

        if not state or not code_verifier:
            logger.error("Authorization failed: Missing state or code_verifier")
            return make_response({"msg": "Authorization failed."}, 400)

        # Verify the state parameter to prevent CSRF attacks
        state_in_request = request.args.get("state")
        if state_in_request != state:
            logger.error("State mismatch during Fitbit callback")
            return make_response({"msg": "Invalid authorization state."}, 400)

        # Retrieve the authorization code from the request
        code = request.args.get("code")
        if not code:
            logger.error("Authorization code not found in Fitbit callback")
            return make_response({"msg": "Authorization code missing."}, 400)

        # Initialize the OAuth2 client
        client = WebApplicationClient(fitbit_client_id)

        # Prepare the token request parameters
        token_url, headers, body = client.prepare_token_request(
            "https://api.fitbit.com/oauth2/token",
            code=code,
            redirect_url=fitbit_redirect_uri,
            code_verifier=code_verifier,
        )

        # Fitbit requires HTTP Basic Authentication for the token request
        auth = requests.auth.HTTPBasicAuth(fitbit_client_id, fitbit_client_secret)

        # Send the token request to Fitbit
        try:
            response = requests.post(
                token_url, headers=headers, data=body, auth=auth, timeout=30
            )
            response.raise_for_status()
            token = client.parse_request_body_response(response.text)
        except Exception as e:
            logger.error(f"Failed to fetch Fitbit tokens: {e!s}")
            return make_response(
                {"msg": "Failed to retrieve Fitbit tokens."}, 400
            )

        # Retrieve the Fitbit API record from the database
        fitbit_api = Api.query.filter_by(name="Fitbit").first()
        if not fitbit_api:
            logger.error("Fitbit API not configured in the database.")
            return make_response(
                {"msg": "Fitbit integration not available."}, 500
            )

        # Retrieve the StudySubject using ditti_id
        study_subject = StudySubject.query.filter_by(ditti_id=ditti_id).first()
        if not study_subject:
            logger.error(f"StudySubject with ditti_id {ditti_id} not found.")
            return make_response({"msg": "Study subject not found."}, 400)

        # Associate the tokens with the study subject's Fitbit API entry
        join_entry = JoinStudySubjectApi.query.filter_by(
            study_subject_id=study_subject.id, api_id=fitbit_api.id
        ).first()

        if not join_entry:
            # Create a new association entry if it doesn't exist
            join_entry = JoinStudySubjectApi(
                study_subject_id=study_subject.id,
                api_id=fitbit_api.id,
                api_user_uuid=token.get("user_id"),
                scope=token.get("scope"),
            )
            db.session.add(join_entry)
        else:
            # Update the existing association entry
            join_entry.api_user_uuid = token.get("user_id")
            if token.get("scope"):
                join_entry.scope = token.get("scope")

        db.session.commit()

        # Prepare the token data
        expires_in = token.get("expires_in")
        if expires_in:
            expires_at = int(time.time()) + int(expires_in)
        else:
            expires_at = int(time.time()) + 28800  # Default to 8 hours

        access_token = token.get("access_token")
        refresh_token = token.get("refresh_token")

        if not access_token or not refresh_token:
            logger.error(
                "Missing access_token or refresh_token in Fitbit response"
            )
            return make_response(
                {"msg": "Incomplete Fitbit token response."}, 400
            )

        token_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
        }

        # Store tokens securely using TokensManager
        try:
            tm.add_or_update_api_token(
                api_name="Fitbit",
                ditti_id=study_subject.ditti_id,
                tokens=token_data,
            )
        except Exception as e:
            logger.error(f"Error storing Fitbit tokens: {e!s}")
            return make_response({"msg": "Failed to store Fitbit tokens."}, 500)

        # Clear OAuth session variables
        session.pop("oauth_code_verifier", None)
        session.pop("oauth_state", None)

        # Redirect the user to the participant dashboard
        return redirect(current_app.config.get("API_AUTHORIZE_REDIRECT"))

    except Exception as e:
        logger.error(f"Unhandled error in fitbit_callback: {e!s}")
        return make_response({"msg": "An unexpected error occurred."}, 500)


@blueprint.route("/sleep_list")
@participant_auth_required
def fitbit_sleep_list(ditti_id: str):
    """
    Test: Retrieves the user's sleep data from Fitbit.

    Fetches the study subject's Fitbit API session, makes a request
    to the Fitbit API for sleep data, and returns the data as a JSON response.

    Args:
        ditti_id (str): The unique ID of the study subject,
            provided by the decorator.

    Returns
    -------
        Any: A JSON response containing the sleep data or an error response.
    """
    try:
        fitbit_api = Api.query.filter_by(name="Fitbit").first()
        if not fitbit_api:
            logger.error("Fitbit API not configured in the database.")
            return make_response(
                {"msg": "Fitbit integration not available."}, 500
            )

        # Retrieve the StudySubject using ditti_id
        study_subject = StudySubject.query.filter_by(ditti_id=ditti_id).first()
        if not study_subject:
            logger.error(f"StudySubject with ditti_id {ditti_id} not found.")
            return make_response({"msg": "Study subject not found."}, 404)

        study_subject_fitbit = JoinStudySubjectApi.query.filter_by(
            study_subject_id=study_subject.id, api_id=fitbit_api.id
        ).first()

        if study_subject_fitbit:
            try:
                fitbit_session = get_fitbit_oauth_session(
                    study_subject.ditti_id, config=current_app.config, tm=tm
                )
            except Exception as e:
                logger.error(
                    f"OAuth Session Error for ditti_id {ditti_id}: {e!s}"
                )
                return make_response(
                    {"msg": "Failed to create Fitbit session."}, 401
                )
            try:
                # Example: Fetch sleep data from Fitbit API
                sleep_list_data = fitbit_session.get(
                    "https://api.fitbit.com/1.2/user/-/sleep/list.json",
                    params={
                        "afterDate": "2024-01-01",
                        "sort": "asc",
                        "offset": 0,
                        "limit": 100,
                    },
                ).json()
            except Exception as e:
                logger.error(
                    f"Fitbit Data Request Error for ditti_id {ditti_id}: {e!s}"
                )
                return make_response(
                    {"msg": "Failed to retrieve sleep data."}, 401
                )
        else:
            logger.warning(f"Fitbit API not linked for ditti_id {ditti_id}")
            return make_response(
                {"msg": "Fitbit API not linked to your account."}, 401
            )

        return jsonify(sleep_list_data)

    except Exception as e:
        logger.error(
            f"Unhandled error in fitbit_sleep_list for ditti_id {ditti_id}: {e!s}"
        )
        return make_response({"msg": "An unexpected error occurred."}, 500)
