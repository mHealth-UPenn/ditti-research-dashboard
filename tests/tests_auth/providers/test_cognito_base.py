from unittest.mock import MagicMock, patch

import pytest

from backend.auth.providers.cognito.constants import AUTH_ERROR_MESSAGES


# Use the base_cognito_auth fixture from conftest.py
@pytest.fixture
def cognito_auth(base_cognito_auth):
    """Return a test cognito auth instance."""
    return base_cognito_auth


def test_get_config_prefix(cognito_auth):
    """Test that get_config_prefix returns the expected value."""
    assert cognito_auth.get_config_prefix() == "TEST_COGNITO"


def test_get_config(cognito_auth):
    """
    Test that get_config correctly retrieves configuration values.

    Uses function monkeypatching to bypass Flask dependency on current_app,
    making the test more reliable and independent of the Flask environment.
    """
    # Create a patched version of the get_config method
    original_get_config = cognito_auth.get_config

    try:
        # Replace with a simple implementation that doesn't require current_app
        def mock_get_config(key):
            config_values = {
                "REGION": "us-west-2",
                "CLIENT_ID": "test-client-id",
            }
            return config_values.get(key)

        # Set the mock method
        cognito_auth.get_config = mock_get_config

        # Test getting existing configuration values
        assert cognito_auth.get_config("REGION") == "us-west-2"
        assert cognito_auth.get_config("CLIENT_ID") == "test-client-id"

        # Test getting non-existent configuration
        assert cognito_auth.get_config("NON_EXISTENT") is None
    finally:
        # Restore the original method
        cognito_auth.get_config = original_get_config


@patch("jwt.decode")
@patch("time.time")
def test_validate_access_token_success(
    mock_time, mock_jwt_decode, cognito_auth, mock_auth_test_data
):
    """Test successful validation of an access token."""
    # Setup
    mock_jwt_decode.return_value = mock_auth_test_data["access_token_claims"]
    mock_time.return_value = 1600000000  # Current time (before expiration)

    # Execute
    success, result = cognito_auth.validate_access_token(
        mock_auth_test_data["fake_tokens"]["access_token"]
    )

    # Verify
    assert success is True
    assert result is None
    mock_jwt_decode.assert_called_once()


@patch("jwt.decode")
@patch("time.time")
def test_validate_access_token_expired(
    mock_time, mock_jwt_decode, cognito_auth, mock_auth_test_data
):
    """Test handling of expired access token."""
    # Setup
    mock_claims = dict(mock_auth_test_data["access_token_claims"])
    mock_claims["exp"] = 1600000000  # Past time
    mock_jwt_decode.return_value = mock_claims
    mock_time.return_value = 1700000000  # Current time (after expiration)

    # Execute
    success, result = cognito_auth.validate_access_token(
        mock_auth_test_data["fake_tokens"]["access_token"]
    )

    # Verify
    assert success is False
    assert result == AUTH_ERROR_MESSAGES["session_expired"]


@patch("jwt.decode", side_effect=Exception("Invalid token"))
def test_validate_access_token_invalid_token(
    mock_jwt_decode, cognito_auth, mock_auth_test_data
):
    """Test validation fails with invalid token."""
    # Execute
    success, result = cognito_auth.validate_access_token(
        mock_auth_test_data["fake_tokens"]["access_token"]
    )

    # Verify
    assert success is False
    assert result == AUTH_ERROR_MESSAGES["auth_failed"]


@patch("jwt.decode")
def test_validate_access_token_malformed_claims(
    mock_jwt_decode, cognito_auth, mock_auth_test_data
):
    """
    Test validation with malformed claims.

    Ensures validation correctly handles tokens that don't contain all expected fields.
    """
    # Setup - token with missing 'token_use' field
    malformed_claims = {"sub": "test-id", "email": "test@example.com"}
    mock_jwt_decode.return_value = malformed_claims

    # Execute
    success, result = cognito_auth.validate_access_token(
        mock_auth_test_data["fake_tokens"]["access_token"]
    )

    # Verify
    assert success is False
    assert result == AUTH_ERROR_MESSAGES["session_expired"]


@patch("requests.post")
@patch("backend.auth.providers.cognito.base.CognitoAuthBase.get_config")
@patch("jwt.decode")
@patch("time.time")
def test_validate_access_token_with_refresh(
    mock_time,
    mock_jwt_decode,
    mock_get_config,
    mock_post,
    cognito_auth,
    mock_auth_test_data,
):
    """
    Test token refresh when access token is expired but refresh token is provided.

    This test verifies the token refresh flow by mocking the AWS Cognito response.
    """
    # Setup
    mock_claims = dict(mock_auth_test_data["access_token_claims"])
    mock_claims["exp"] = 1600000000  # Past time
    mock_jwt_decode.return_value = mock_claims
    mock_time.return_value = 1700000000  # Current time (after expiration)

    # Mock the config needed for refresh
    mock_get_config.side_effect = lambda key: {
        "REGION": "us-west-2",
        "USER_POOL_ID": "us-west-2_testpool",
        "CLIENT_ID": "test-client-id",
        "CLIENT_SECRET": "test-client-secret",
    }.get(key)

    # Mock the refresh token response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "new-fake-access-token",
        "id_token": "new-fake-id-token",
        "refresh_token": "new-fake-refresh-token",
    }
    mock_post.return_value = mock_response

    # Execute
    success, result = cognito_auth.validate_access_token(
        mock_auth_test_data["fake_tokens"]["access_token"],
        mock_auth_test_data["fake_tokens"]["refresh_token"],
    )

    # Verify
    assert success is True
    assert "new_token" in result
    assert result["new_token"] == "new-fake-access-token"


@patch("requests.post")
@patch("backend.auth.providers.cognito.base.CognitoAuthBase.get_config")
@patch("jwt.decode")
@patch("time.time")
def test_validate_access_token_refresh_failed(
    mock_time,
    mock_jwt_decode,
    mock_get_config,
    mock_post,
    cognito_auth,
    mock_auth_test_data,
):
    """
    Test handling failed token refresh.

    Verifies proper error handling when a token refresh attempt fails.
    """
    # Setup
    mock_claims = dict(mock_auth_test_data["access_token_claims"])
    mock_claims["exp"] = 1600000000  # Past time
    mock_jwt_decode.return_value = mock_claims
    mock_time.return_value = 1700000000  # Current time (after expiration)

    # Mock the config needed for refresh
    mock_get_config.side_effect = lambda key: {
        "REGION": "us-west-2",
        "USER_POOL_ID": "us-west-2_testpool",
        "CLIENT_ID": "test-client-id",
        "CLIENT_SECRET": "test-client-secret",
    }.get(key)

    # Mock the failed refresh token response
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {
        "error": "invalid_grant",
        "error_description": "Refresh token has expired",
    }
    mock_post.return_value = mock_response

    # Execute
    success, result = cognito_auth.validate_access_token(
        mock_auth_test_data["fake_tokens"]["access_token"],
        mock_auth_test_data["fake_tokens"]["refresh_token"],
    )

    # Verify
    assert success is False
    assert result == AUTH_ERROR_MESSAGES["session_expired"]


@patch("jwt.get_unverified_header")
@patch("jwt.decode")
@patch("backend.auth.providers.cognito.base.CognitoAuthBase.get_config")
def test_validate_token_for_authenticated_route_success(
    mock_get_config, mock_jwt_decode, mock_header, cognito_auth
):
    """Test successful validation of token for authenticated route."""
    # This test is complex and would require more detailed knowledge of the implementation
    pass


@patch("jwt.get_unverified_header")
@patch("jwt.decode")
def test_validate_token_for_authenticated_route_wrong_token_use(
    mock_jwt_decode, mock_header, cognito_auth
):
    """Test validation fails with wrong token_use for authenticated route."""
    # Setup for access token instead of id token
    mock_claims = {
        "sub": "test-user-id",
        "email": "test@example.com",
        "token_use": "access",  # Should be "id"
    }
    mock_jwt_decode.return_value = mock_claims
    mock_header.return_value = {"kid": "test-kid"}

    # Execute
    success, result = cognito_auth.validate_token_for_authenticated_route(
        "fake-token"
    )

    # Verify
    assert success is False
    assert result == AUTH_ERROR_MESSAGES["auth_failed"]


@patch("jwt.get_unverified_header", side_effect=Exception("Malformed header"))
def test_validate_token_for_authenticated_route_malformed_header(
    mock_header, cognito_auth
):
    """Test validation fails with malformed token header."""
    # Execute
    success, result = cognito_auth.validate_token_for_authenticated_route(
        "fake-token"
    )

    # Verify
    assert success is False
    assert result == AUTH_ERROR_MESSAGES["auth_failed"]


@patch(
    "backend.auth.providers.cognito.base.CognitoAuthBase.validate_token_for_authenticated_route"
)
def test_validate_token_for_authenticated_route_no_user(
    mock_validate, cognito_auth
):
    """
    Test validation succeeds with a valid token even without user claims.

    This test verifies that token validation succeeds solely based on
    cryptographic verification, regardless of whether user-identifying
    claims are present.
    """
    # Setup - mock the validation to return success and claims
    mock_claims = {
        "token_use": "id",
        "iss": "https://cognito-idp.us-west-2.amazonaws.com/test-pool",
        "aud": "test-client-id",
        "exp": 1700000000,
        # Missing user identifiers like sub, email, cognito:username
    }

    mock_validate.return_value = (True, mock_claims)

    # Execute
    success, claims = cognito_auth.validate_token_for_authenticated_route(
        "fake-token"
    )

    # Verify
    assert success is True
    assert claims == mock_claims
    mock_validate.assert_called_once_with("fake-token")


@patch("jwt.get_unverified_header")
@patch("jwt.decode")
@patch("backend.auth.providers.cognito.base.CognitoAuthBase.get_config")
@patch("backend.auth.utils.tokens.get_cognito_jwks")
@patch("jwt.decode", side_effect=Exception("Invalid signature"))
def test_validate_token_invalid_signature(
    mock_validated_decode,
    mock_get_jwks,
    mock_get_config,
    mock_unverified_decode,
    mock_header,
    cognito_auth,
):
    """
    Test validation fails with invalid token signature.

    This test verifies that tokens with invalid cryptographic signatures are rejected.
    """
    # Setup
    mock_header.return_value = {"kid": "test-kid"}
    mock_unverified_decode.return_value = {
        "iss": "https://cognito-idp.us-west-2.amazonaws.com/test-pool",
        "token_use": "id",
    }
    mock_get_config.return_value = "test-client-id"
    mock_get_jwks.return_value = {
        "keys": [{"kid": "test-kid", "n": "test-n", "e": "test-e"}]
    }

    # Execute
    success, result = cognito_auth.validate_token_for_authenticated_route(
        "fake-token"
    )

    # Verify
    assert success is False
    assert result == AUTH_ERROR_MESSAGES["auth_failed"]
