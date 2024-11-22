import logging
import time
from typing import Any, Dict

from oauthlib.oauth2 import WebApplicationClient
import requests

import utils.tokens_manager as tm

logger = logging.getLogger()


def get_fitbit_oauth_session(join_entry, config, tokens):
    """
    Creates an OAuth2Session for Fitbit API, using stored tokens.

    Args:
        join_entry (JoinStudySubjectApi): JoinStudySubjectApi instance.

    Returns:
        OAuth2SessionWithRefresh: An OAuth2Session instance ready to make requests to Fitbit API.

    Raises:
        Exception: If there is an error retrieving or refreshing tokens.
    """
    fitbit_client_secret = config["FITBIT_CLIENT_SECRET"]
    fitbit_client_id = config["FITBIT_CLIENT_ID"]
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    expires_at = tokens.get("expires_at")

    token = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_at": expires_at,
        "expires_in": expires_at - int(time.time())
    }

    # Initialize the OAuth2 WebApplicationClient
    client = WebApplicationClient(client_id=fitbit_client_id, token=token)

    def token_updater(new_token: Dict[str, Any]) -> None:
        """
        Updates the tokens in Secrets Manager.

        Args:
            new_token (Dict[str, Any]): The new token data obtained from Fitbit.

        Raises:
            Exception: If there is an error updating the tokens in Secrets Manager.
        """
        try:
            expires_in = new_token.get("expires_in")
            if expires_in:
                new_expires_at = int(time.time()) + int(expires_in)
            else:
                new_expires_at = int(time.time()) + 28800  # Default to 8 hours

            updated_token_data = {
                "access_token": new_token["access_token"],
                "refresh_token": new_token.get("refresh_token", refresh_token),
                "expires_at": new_expires_at
            }

            # Store the updated tokens
            tm.add_or_update_api_token(
                api_name="Fitbit",
                study_subject_id=join_entry.study_subject_id,
                tokens=updated_token_data
            )
        except Exception as e:
            logger.error(f"Error updating tokens in Secrets Manager: {e}")
            raise

    def refresh_token_func() -> None:
        """
        Refreshes the access token using the refresh token.

        Raises:
            Exception: If the token refresh fails.
        """
        token_issuer_endpoint = "https://api.fitbit.com/oauth2/token"
        auth = requests.auth.HTTPBasicAuth(
            fitbit_client_id, fitbit_client_secret)
        refresh_params = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        try:
            response = requests.post(
                token_issuer_endpoint, data=refresh_params, auth=auth)
            response.raise_for_status()
            new_token = response.json()

            token_updater(new_token)
            client.token = new_token
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise

    # Wrapper around requests to handle token expiration
    class OAuth2SessionWithRefresh:
        """
        A wrapper around the OAuth2 WebApplicationClient to handle automatic token refresh.
        """

        def __init__(self, client: WebApplicationClient):
            self.client = client

        def request(self, method: str, url: str, **kwargs) -> requests.Response:
            """
            Makes an HTTP request using the OAuth2 session, handling token refresh on 401 responses.

            Args:
                method (str): HTTP method (e.g., 'GET', 'POST').
                url (str): The URL to make the request to.
                **kwargs: Additional arguments for the requests.request method.

            Returns:
                requests.Response: The HTTP response received.
            """
            headers = kwargs.pop("headers", {})
            headers["Authorization"] = f"Bearer {
                self.client.token['access_token']}"
            kwargs["headers"] = headers
            response = requests.request(method, url, **kwargs)
            if response.status_code == 401:
                # Token expired, refresh it
                refresh_token_func()
                # Retry the request with the new token
                headers["Authorization"] = f"Bearer {
                    self.client.token['access_token']}"
                kwargs["headers"] = headers
                response = requests.request(method, url, **kwargs)
            return response

        def get(self, url: str, **kwargs) -> requests.Response:
            """
            Convenience method for making GET requests.

            Args:
                url (str): The URL to make the GET request to.
                **kwargs: Additional arguments for the requests.get method.

            Returns:
                requests.Response: The HTTP response received.
            """
            return self.request("GET", url, **kwargs)

        def post(self, url: str, **kwargs) -> requests.Response:
            """
            Convenience method for making POST requests.

            Args:
                url (str): The URL to make the POST request to.
                **kwargs: Additional arguments for the requests.post method.

            Returns:
                requests.Response: The HTTP response received.
            """
            return self.request("POST", url, **kwargs)

    return OAuth2SessionWithRefresh(client)
