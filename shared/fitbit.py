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
import hashlib
import logging
import os
import time
from typing import Any, Dict

import requests
from oauthlib.oauth2 import WebApplicationClient

from shared.tokens_manager import TokensManager

logger = logging.getLogger(__name__)


def generate_code_verifier(length: int = 128) -> str:
    """
    Generates a high-entropy cryptographic random string for PKCE (Proof Key for Code Exchange).

    Args:
        length (int, optional): Length of the code verifier. Must be between 43 and 128 characters.
                                Defaults to 128.

    Returns:
        str: A securely generated code verifier string.

    Raises:
        ValueError: If the specified length is not within the allowed range.
    """
    if not 43 <= length <= 128:
        raise ValueError("length must be between 43 and 128 characters")
    code_verifier = (
        base64.urlsafe_b64encode(os.urandom(length))
        .rstrip(b"=")
        .decode("utf-8")
    )
    return code_verifier[:length]


def create_code_challenge(code_verifier: str) -> str:
    """
    Creates a S256 code challenge from the provided code verifier.

    Args:
        code_verifier (str): The code verifier string.

    Returns:
        str: The generated code challenge string.
    """
    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = (
        base64.urlsafe_b64encode(code_challenge).rstrip(b"=").decode("utf-8")
    )
    return code_challenge


def get_fitbit_oauth_session(ditti_id: str, config, tokens=None, tm=None):
    """
    Creates an OAuth2Session for Fitbit API, using stored tokens.

    Args:
        ditti_id (str): The Ditti ID fo the subject that the OAuth session will be used to retrieve data for.

    Returns:
        OAuth2SessionWithRefresh: An OAuth2Session instance ready to make requests to Fitbit API.

    Raises:
        Exception: If there is an error retrieving or refreshing tokens.
    """
    fitbit_client_secret = config["FITBIT_CLIENT_SECRET"]
    fitbit_client_id = config["FITBIT_CLIENT_ID"]

    if tm is None:
        tm = TokensManager()

    if tokens is None:
        try:
            # Retrieve tokens using TokensManager
            tokens = tm.get_api_tokens(api_name="Fitbit", ditti_id=ditti_id)
        except KeyError as e:
            logger.error(f"Tokens not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving tokens: {e}")
            raise

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    expires_at = tokens.get("expires_at")

    token = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_at": expires_at,
        "expires_in": expires_at - int(time.time()),
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
                "expires_at": new_expires_at,
            }

            # Store the updated tokens
            tm.add_or_update_api_token(
                api_name="Fitbit", ditti_id=ditti_id, tokens=updated_token_data
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
            fitbit_client_id, fitbit_client_secret
        )
        refresh_params = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        try:
            response = requests.post(
                token_issuer_endpoint, data=refresh_params, auth=auth
            )
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
            headers["Authorization"] = (
                f"Bearer {self.client.token['access_token']}"
            )
            kwargs["headers"] = headers
            response = requests.request(method, url, **kwargs)
            if response.status_code == 401:
                # Token expired, refresh it
                refresh_token_func()
                # Retry the request with the new token
                headers["Authorization"] = (
                    f"Bearer {self.client.token['access_token']}"
                )
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
