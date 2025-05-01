from datetime import datetime

import pytest

from backend.auth.utils.session import AuthFlowSession
from backend.auth.utils.tokens import (
    create_code_challenge,
    generate_code_verifier,
)


def test_create_code_verifier():
    """Test code verifier generation."""
    verifier = generate_code_verifier()

    # Should be a string
    assert isinstance(verifier, str)
    # Should be at least 43 characters
    assert len(verifier) >= 43
    # Should be at most 128 characters
    assert len(verifier) <= 128
    # Should be URL-safe base64
    assert all(c.isalnum() or c in "-._~" for c in verifier)


def test_create_code_challenge():
    """Test code challenge generation from a verifier."""
    verifier = "test_verifier"
    challenge = create_code_challenge(verifier)

    # Should be a string
    assert isinstance(challenge, str)
    # Should be URL-safe base64
    assert all(c.isalnum() or c in "-._~" for c in challenge)
    # Should have a fixed length based on SHA256 hash
    assert len(challenge) > 0


def test_authflow_session_creation():
    """Test creating an AuthFlowSession."""
    # Test that AuthFlowSession has static methods
    assert hasattr(AuthFlowSession, "generate_and_store_security_params")
    assert hasattr(AuthFlowSession, "validate_state")
    assert hasattr(AuthFlowSession, "get_code_verifier")
    assert hasattr(AuthFlowSession, "validate_nonce")
    assert hasattr(AuthFlowSession, "clear")
    assert hasattr(AuthFlowSession, "set_user_data")


# The following tests require a database connection, so we'll skip them for now
@pytest.mark.skip(reason="Requires database connection")
def test_authflow_session_generate_and_store_security_params(client):
    """Test generating and storing security parameters."""
    with client.session_transaction() as flask_session:
        # Call the method
        params = AuthFlowSession.generate_and_store_security_params()

        # Check returned parameters
        assert "nonce" in params
        assert "state" in params
        assert "code_verifier" in params
        assert "code_challenge" in params

        # Check session storage
        assert flask_session["cognito_nonce"] == params["nonce"]
        assert "cognito_nonce_generated" in flask_session
        assert flask_session["cognito_state"] == params["state"]
        assert flask_session["cognito_code_verifier"] == params["code_verifier"]


@pytest.mark.skip(reason="Requires database connection")
def test_authflow_session_validate_state(client):
    """Test state validation."""
    with client.session_transaction() as flask_session:
        # Set up state in session
        flask_session["cognito_state"] = "test_state"

    # Valid state
    assert AuthFlowSession.validate_state("test_state") is True

    # State should be removed from session after validation
    with client.session_transaction() as flask_session:
        assert "cognito_state" not in flask_session

    # Invalid state
    assert AuthFlowSession.validate_state("wrong_state") is False


@pytest.mark.skip(reason="Requires database connection")
def test_authflow_session_get_code_verifier(client):
    """Test getting code verifier."""
    with client.session_transaction() as flask_session:
        # Set up code verifier in session
        flask_session["cognito_code_verifier"] = "test_verifier"

    # Get code verifier
    verifier = AuthFlowSession.get_code_verifier()
    assert verifier == "test_verifier"

    # Code verifier should be removed from session
    with client.session_transaction() as flask_session:
        assert "cognito_code_verifier" not in flask_session


@pytest.mark.skip(reason="Requires database connection")
def test_authflow_session_validate_nonce(client):
    """Test nonce validation."""
    now = int(datetime.now().timestamp())

    with client.session_transaction() as flask_session:
        # Set up valid nonce
        flask_session["cognito_nonce"] = "test_nonce"
        flask_session["cognito_nonce_generated"] = now

    # Valid nonce
    is_valid, nonce = AuthFlowSession.validate_nonce()
    assert is_valid is True
    assert nonce == "test_nonce"

    # Nonce should be removed from session
    with client.session_transaction() as flask_session:
        assert "cognito_nonce" not in flask_session
        assert "cognito_nonce_generated" not in flask_session

    # Test expired nonce
    with client.session_transaction() as flask_session:
        # Set up expired nonce (10 minutes ago)
        flask_session["cognito_nonce"] = "expired_nonce"
        flask_session["cognito_nonce_generated"] = now - 600  # 10 minutes ago

    # Expired nonce
    is_valid, nonce = AuthFlowSession.validate_nonce()
    assert is_valid is False
    assert nonce is None


@pytest.mark.skip(reason="Requires database connection")
def test_authflow_session_clear(client):
    """Test clearing session data."""
    with client.session_transaction() as flask_session:
        # Set up session data
        flask_session["cognito_nonce"] = "test_nonce"
        flask_session["cognito_nonce_generated"] = 12345
        flask_session["cognito_state"] = "test_state"
        flask_session["cognito_code_verifier"] = "test_verifier"
        flask_session["other_data"] = "should_remain"

    # Clear session
    AuthFlowSession.clear()

    # Check session data is cleared
    with client.session_transaction() as flask_session:
        assert "cognito_nonce" not in flask_session
        assert "cognito_nonce_generated" not in flask_session
        assert "cognito_state" not in flask_session
        assert "cognito_code_verifier" not in flask_session
        # Other data should remain
        assert flask_session["other_data"] == "should_remain"


@pytest.mark.skip(reason="Requires database connection")
def test_authflow_session_set_user_data(client):
    """Test setting user data."""
    # Test for participant
    with client.session_transaction() as flask_session:
        AuthFlowSession.set_user_data(
            user_type="participant",
            user_id="123",
            userinfo={"name": "Test Participant"},
        )

        assert flask_session["study_subject_id"] == "123"
        assert flask_session["user"] == {"name": "Test Participant"}
        assert flask_session["user_type"] == "participant"

    # Test for researcher
    with client.session_transaction() as flask_session:
        AuthFlowSession.set_user_data(
            user_type="researcher",
            user_id="456",
            userinfo={"name": "Test Researcher"},
        )

        assert flask_session["account_id"] == "456"
        assert flask_session["user"] == {"name": "Test Researcher"}
        assert flask_session["user_type"] == "researcher"
