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
from functools import lru_cache

import requests

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_cognito_jwks(jwks_url):
    """
    Retrieve and cache the JSON Web Key Set (JWKS) from Cognito.

    Parameters
    ----------
        jwks_url (str): The URL to the JWKS endpoint

    Returns
    -------
        dict: The JWKS response or None if request failed
    """
    try:
        response = requests.get(jwks_url, timeout=30)
        if response.ok:
            return response.json()
        logger.error(f"Failed to fetch JWKS: {response.status_code}")
        return None
    except Exception as e:
        logger.error(f"Error fetching JWKS: {e!s}")
        return None


def generate_code_verifier(length: int = 128) -> str:
    """
    Generate a high-entropy cryptographic random string for PKCE.

    Parameters
    ----------
        length (int, optional): Length of the code verifier.
            Must be between 43 and 128 characters.
            Defaults to 128.

    Returns
    -------
        str: A securely generated code verifier string.

    Raises
    ------
        ValueError: If the specified length is not within the allowed range.
    """
    if not 43 <= length <= 128:
        raise ValueError("length must be between 43 and 128 characters")
    code_verifier = (
        base64.urlsafe_b64encode(os.urandom(length)).rstrip(b"=").decode("utf-8")
    )
    return code_verifier[:length]


def create_code_challenge(code_verifier: str) -> str:
    """
    Create a S256 code challenge from the provided code verifier for PKCE.

    Parameters
    ----------
        code_verifier (str): The code verifier string.

    Returns
    -------
        str: The generated code challenge string.
    """
    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = (
        base64.urlsafe_b64encode(code_challenge).rstrip(b"=").decode("utf-8")
    )
    return code_challenge
