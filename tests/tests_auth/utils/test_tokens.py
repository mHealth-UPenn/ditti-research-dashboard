import re
from unittest.mock import patch, MagicMock
from backend.auth.utils.tokens import (
    generate_code_verifier,
    create_code_challenge,
    get_cognito_jwks
)


def test_generate_code_verifier():
    """Test PKCE code verifier meets OAuth 2.0 RFC 7636 requirements."""
    verifier = generate_code_verifier()

    assert isinstance(verifier, str)
    assert len(verifier) >= 43  # Min length per RFC 7636
    assert len(verifier) <= 128  # Max length per RFC 7636
    assert re.match(r"^[A-Za-z0-9-._~]+$", verifier)  # URL-safe chars only


def test_generate_code_verifier_custom_length():
    """Test code verifier generation with non-default length."""
    verifier = generate_code_verifier(length=64)

    assert len(verifier) == 64
    assert re.match(r"^[A-Za-z0-9-._~]+$", verifier)


def test_create_code_challenge():
    """Test PKCE code challenge meets S256 transformation requirements."""
    verifier = "test_verifier"
    challenge = create_code_challenge(verifier)

    # Verify challenge is URL-safe base64 encoded
    assert isinstance(challenge, str)
    assert re.match(r"^[A-Za-z0-9-._~]+$", challenge)

    # Verify deterministic transformation
    assert challenge == create_code_challenge(verifier)
    assert challenge != create_code_challenge("different_verifier")


@patch("requests.get")
def test_get_cognito_jwks(mock_get):
    """Test successful JWKS retrieval and response parsing."""
    get_cognito_jwks.cache_clear()

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "keys": [
            {
                "kid": "test-kid",
                "kty": "RSA",
                "n": "test-n",
                "e": "AQAB",
                "use": "sig"
            }
        ]
    }
    mock_get.return_value = mock_response

    jwks = get_cognito_jwks("https://example.com/.well-known/jwks.json")

    assert jwks == mock_response.json.return_value
    mock_get.assert_called_once_with(
        "https://example.com/.well-known/jwks.json")


@patch("requests.get")
def test_get_cognito_jwks_error(mock_get):
    """Test JWKS retrieval gracefully handles HTTP errors."""
    get_cognito_jwks.cache_clear()

    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    result = get_cognito_jwks("https://example.com/.well-known/jwks.json")
    assert result is None

    mock_get.assert_called_once_with(
        "https://example.com/.well-known/jwks.json")


@patch("requests.get")
def test_get_cognito_jwks_caching(mock_get):
    """Test JWKS responses are properly cached to minimize HTTP requests."""
    get_cognito_jwks.cache_clear()

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "keys": [
            {
                "kid": "test-kid",
                "kty": "RSA",
                "n": "test-n",
                "e": "AQAB",
                "use": "sig"
            }
        ]
    }
    mock_get.return_value = mock_response

    # Multiple calls should use cached response
    jwks1 = get_cognito_jwks("https://example.com/.well-known/jwks.json")
    jwks2 = get_cognito_jwks("https://example.com/.well-known/jwks.json")

    mock_get.assert_called_once_with(
        "https://example.com/.well-known/jwks.json")
    assert jwks1 == jwks2
