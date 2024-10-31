from flask import current_app
from aws_portal.extensions import study_subject_secrets_manager
import logging
import time
import requests
from oauthlib.oauth2 import OAuth2Session as OAuth2Client

logger = logging.getLogger(__name__)

FITBIT_TOKEN_URL = "https://api.fitbit.com/oauth2/token"


def get_fitbit_oauth_session(join_entry):
    """
    Creates an OAuth2Session for Fitbit API, using stored tokens.

    Args:
        join_entry (JoinStudySubjectApi): The association object for the API.

    Returns:
        OAuth2Client: An OAuth2Client instance ready to make requests to Fitbit API.
    """
    fitbit_client_id = current_app.config["FITBIT_CLIENT_ID"]
    fitbit_client_secret = current_app.config["FITBIT_CLIENT_SECRET"]

    # Load access token data
    try:
        access_token_data = study_subject_secrets_manager.get_secret(
            join_entry.access_key_uuid)
        access_token = access_token_data.get("access_token")
        expires_at = access_token_data.get("expires_at")
    except Exception as e:
        logger.error(f"Error retrieving access token: {e}")
        raise

    # Load refresh token data
    try:
        refresh_token_data = study_subject_secrets_manager.get_secret(
            join_entry.refresh_key_uuid)
        refresh_token = refresh_token_data.get("refresh_token")
    except Exception as e:
        logger.error(f"Error retrieving refresh token: {e}")
        raise

    # Create the token dict
    token = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_at": expires_at,
        "expires_in": expires_at - int(time.time())
    }

    # Create an OAuth2Client
    client = OAuth2Client(client_id=fitbit_client_id, token=token)

    # Define a method to refresh the token
    def refresh_token():
        token_url = FITBIT_TOKEN_URL
        auth = requests.auth.HTTPBasicAuth(
            fitbit_client_id, fitbit_client_secret)
        refresh_params = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        try:
            response = requests.post(
                token_url,
                data=refresh_params,
                auth=auth,
            )
            response.raise_for_status()
            new_token = response.json()
            # Update tokens in Secrets Manager
            token_updater(new_token)
            client.token = new_token
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise

    def token_updater(new_token):
        """
        Update the access_token and refresh_token in Secrets Manager.
        """
        try:
            # Compute new expires_at
            expires_in = new_token.get("expires_in")
            if expires_in:
                new_expires_at = int(time.time()) + int(expires_in)
            else:
                new_expires_at = int(time.time()) + 28800  # Default to 8 hours

            # Prepare new access token data
            new_access_token_data = {
                "access_token": new_token["access_token"],
                "expires_at": new_expires_at
            }

            # Prepare new refresh token data (if provided)
            new_refresh_token = new_token.get("refresh_token")
            if new_refresh_token:
                new_refresh_token_data = {
                    "refresh_token": new_refresh_token
                }
                # Store refresh token
                study_subject_secrets_manager.store_secret(
                    join_entry.refresh_key_uuid, new_refresh_token_data, "fb-refresh")

            # Store access token
            study_subject_secrets_manager.store_secret(
                join_entry.access_key_uuid, new_access_token_data, "fb-access")

        except Exception as e:
            logger.error(f"Error updating tokens in Secrets Manager: {e}")
            raise

    # Wrapper around requests to handle token expiration
    class OAuth2SessionWithRefresh:
        def __init__(self, client):
            self.client = client

        def request(self, method, url, **kwargs):
            headers = kwargs.pop("headers", {})
            headers["Authorization"] = f"Bearer {
                self.client.token['access_token']}"
            kwargs["headers"] = headers
            response = requests.request(method, url, **kwargs)
            if response.status_code == 401:
                # Token expired, refresh it
                refresh_token()
                # Retry the request with the new token
                headers["Authorization"] = f"Bearer {
                    self.client.token['access_token']}"
                kwargs["headers"] = headers
                response = requests.request(method, url, **kwargs)
            return response

        def get(self, url, **kwargs):
            return self.request("GET", url, **kwargs)

        def post(self, url, **kwargs):
            return self.request("POST", url, **kwargs)

    return OAuth2SessionWithRefresh(client)
