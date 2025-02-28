import logging
import os
import base64
import hashlib
import requests
from functools import lru_cache

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_cognito_jwks(jwks_url):
    """
    Retrieve and cache the JSON Web Key Set (JWKS) from Cognito.

    Args:
        jwks_url (str): The URL to the JWKS endpoint

    Returns:
        dict: The JWKS response or None if request failed
    """
    try:
        response = requests.get(jwks_url)
        if response.ok:
            return response.json()
        logger.error(f"Failed to fetch JWKS: {response.status_code}")
        return None
    except Exception as e:
        logger.error(f"Error fetching JWKS: {str(e)}")
        return None


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
    code_verifier = base64.urlsafe_b64encode(os.urandom(length))\
        .rstrip(b"=")\
        .decode("utf-8")
    return code_verifier[:length]


def create_code_challenge(code_verifier: str) -> str:
    """
    Creates a S256 code challenge from the provided code verifier for PKCE.

    Args:
        code_verifier (str): The code verifier string.

    Returns:
        str: The generated code challenge string.
    """
    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge)\
        .rstrip(b"=")\
        .decode("utf-8")
    return code_challenge
