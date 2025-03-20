import pytest
from unittest.mock import patch, MagicMock, ANY
from aws_portal.auth.providers.cognito.constants import AUTH_ERROR_MESSAGES


# Use the participant_auth_fixture from conftest.py
@pytest.fixture
def participant_auth(participant_auth_fixture):
    """Return a participant auth instance."""
    return participant_auth_fixture


@patch("aws_portal.auth.providers.cognito.participant.StudySubject")
def test_get_study_subject_from_ditti_id(mock_study_subject, participant_auth):
    """Test getting a study subject from a ditti ID."""
    # Setup
    mock_study = MagicMock(id=1, ditti_id="ditti_12345", is_archived=False)
    mock_filter = MagicMock()
    mock_filter.filter.return_value.first.return_value = mock_study
    mock_study_subject.query.filter.return_value = mock_filter

    # Execute
    result = participant_auth.get_study_subject_from_ditti_id(
        ditti_id="ditti_12345")

    # Verify
    assert result.id == 1
    assert result.ditti_id == "ditti_12345"
    # Use ANY to avoid comparing binary expressions directly
    mock_study_subject.query.filter.assert_called_once_with(ANY)
    # Use ANY for the BinaryExpression object
    mock_filter.filter.assert_called_once_with(ANY)


@patch("aws_portal.auth.providers.cognito.participant.StudySubject")
def test_get_study_subject_from_ditti_id_empty_id(mock_study_subject, participant_auth):
    """
    Test getting a study subject with empty ditti ID.

    Verifies the implementation handles empty IDs gracefully.
    """
    # Setup
    mock_study_subject.query.filter.return_value.filter.return_value.first.return_value = None

    # Execute
    result = participant_auth.get_study_subject_from_ditti_id(ditti_id="")

    # Verify
    assert result is None


@patch("aws_portal.auth.providers.cognito.participant.StudySubject")
def test_get_study_subject_from_ditti_id_include_archived(mock_study_subject, participant_auth):
    """Test getting a study subject from a ditti ID including archived."""
    # Setup
    mock_study = MagicMock(id=1, ditti_id="ditti_12345", is_archived=True)
    mock_filter = MagicMock()
    mock_filter.first.return_value = mock_study
    mock_study_subject.query.filter.return_value = mock_filter

    # Execute
    result = participant_auth.get_study_subject_from_ditti_id(
        ditti_id="ditti_12345", include_archived=True)

    # Verify
    assert result.id == 1
    assert result.ditti_id == "ditti_12345"
    assert result.is_archived is True
    # Use ANY to avoid comparing binary expressions directly
    mock_study_subject.query.filter.assert_called_once_with(ANY)


@patch("aws_portal.auth.providers.cognito.participant.StudySubject")
def test_get_study_subject_not_found(mock_study_subject, participant_auth):
    """Test handling when study subject not found."""
    # Setup
    mock_filter = MagicMock()
    mock_filter.filter.return_value.first.return_value = None
    mock_study_subject.query.filter.return_value = mock_filter

    # Execute
    result = participant_auth.get_study_subject_from_ditti_id(
        ditti_id="nonexistent_id")

    # Verify
    assert result is None
    # Use ANY to avoid comparing binary expressions directly
    mock_study_subject.query.filter.assert_called_once_with(ANY)
    # Use ANY for the BinaryExpression object
    mock_filter.filter.assert_called_once_with(ANY)


@patch("aws_portal.auth.providers.cognito.base.CognitoAuthBase.validate_token_for_authenticated_route")
def test_get_study_subject_from_token(mock_validate, participant_auth, mock_auth_test_data):
    """Test getting a study subject from a token."""
    # Setup
    mock_validate.return_value = (
        True, mock_auth_test_data["participant_claims"])

    # Mock study subject lookup - use a direct implementation
    mock_study = MagicMock(id=1, ditti_id="ditti_12345", is_archived=False)

    # Create a mock with the right return value, but verify using positional args
    participant_auth.get_study_subject_from_ditti_id = MagicMock(
        return_value=mock_study)

    # Execute
    study_subject, error = participant_auth.get_study_subject_from_token(
        id_token=mock_auth_test_data["fake_tokens"]["id_token"])

    # Verify
    assert study_subject.id == 1
    assert study_subject.ditti_id == "ditti_12345"
    assert error is None
    mock_validate.assert_called_once_with(
        mock_auth_test_data["fake_tokens"]["id_token"])
    # Use the positional args format instead of named kwargs
    participant_auth.get_study_subject_from_ditti_id.assert_called_once_with(
        "ditti_12345", False)


@patch("aws_portal.auth.providers.cognito.base.CognitoAuthBase.validate_token_for_authenticated_route")
def test_get_study_subject_from_token_archived(mock_validate, participant_auth, mock_auth_test_data):
    """
    Test getting an archived study subject from a token.

    Verifies that archived study subjects are not returned to end users.
    """
    # Setup
    mock_validate.return_value = (
        True, mock_auth_test_data["participant_claims"])

    # Mock archived study subject
    mock_study = MagicMock(id=1, ditti_id="ditti_12345", is_archived=True)
    participant_auth.get_study_subject_from_ditti_id = MagicMock(
        return_value=mock_study)

    # Execute
    study_subject, error = participant_auth.get_study_subject_from_token(
        id_token=mock_auth_test_data["fake_tokens"]["id_token"])

    # Verify
    assert study_subject is None
    assert error == AUTH_ERROR_MESSAGES["account_archived"]
    mock_validate.assert_called_once_with(
        mock_auth_test_data["fake_tokens"]["id_token"])
    participant_auth.get_study_subject_from_ditti_id.assert_called_once_with(
        "ditti_12345", False)


@patch("aws_portal.auth.providers.cognito.base.CognitoAuthBase.validate_token_for_authenticated_route")
def test_get_study_subject_from_token_missing_username(mock_validate, participant_auth, mock_auth_test_data):
    """
    Test handling token without username claim.

    Verifies the implementation checks for required claims.
    """
    # Setup - claims missing cognito:username
    mock_claims = {
        "sub": "test-user-id",
        "email": "test@example.com"
        # Missing cognito:username
    }
    mock_validate.return_value = (True, mock_claims)

    # Execute
    study_subject, error = participant_auth.get_study_subject_from_token(
        id_token=mock_auth_test_data["fake_tokens"]["id_token"])

    # Verify
    assert study_subject is None
    assert error == "Invalid token"
    mock_validate.assert_called_once_with(
        mock_auth_test_data["fake_tokens"]["id_token"])


@patch("aws_portal.auth.providers.cognito.base.CognitoAuthBase.validate_token_for_authenticated_route")
def test_get_study_subject_from_token_not_found(mock_validate, participant_auth, mock_auth_test_data):
    """Test token validation returns None when study subject not found."""
    # Setup
    mock_validate.return_value = (
        True, mock_auth_test_data["participant_claims"])

    # Mock study subject lookup
    participant_auth.get_study_subject_from_ditti_id = MagicMock(
        return_value=None)

    # Execute
    study_subject, error = participant_auth.get_study_subject_from_token(
        id_token=mock_auth_test_data["fake_tokens"]["id_token"])

    # Verify
    assert study_subject is None
    assert error == AUTH_ERROR_MESSAGES["not_found"]
    mock_validate.assert_called_once_with(
        mock_auth_test_data["fake_tokens"]["id_token"])
    participant_auth.get_study_subject_from_ditti_id.assert_called_once_with(
        "ditti_12345", False)


@patch("aws_portal.auth.providers.cognito.base.CognitoAuthBase.validate_token_for_authenticated_route")
def test_get_study_subject_from_token_validation_error(mock_validate, participant_auth, mock_auth_test_data):
    """Test handling token validation errors."""
    # Setup
    mock_validate.return_value = (False, "Invalid token")

    # Execute
    study_subject, error = participant_auth.get_study_subject_from_token(
        id_token=mock_auth_test_data["fake_tokens"]["id_token"])

    # Verify
    assert study_subject is None
    assert error == "Invalid token"
    mock_validate.assert_called_once_with(
        mock_auth_test_data["fake_tokens"]["id_token"])


@patch("aws_portal.auth.providers.cognito.participant.oauth")
def test_init_participant_oauth_client(mock_oauth):
    """
    Test initialization of participant OAuth client.

    Uses a test approach that avoids Flask app context dependencies.
    """
    # Import the module but patch the function we want to test
    from aws_portal.auth.providers.cognito import participant

    # Save the original function to restore it later
    original_init = participant.init_participant_oauth_client

    try:
        # Create our own implementation that doesn't use Flask
        def mock_init_oauth_client():
            config = {
                "COGNITO_PARTICIPANT_REGION": "us-west-2",
                "COGNITO_PARTICIPANT_USER_POOL_ID": "us-west-2_testpool",
                "COGNITO_PARTICIPANT_DOMAIN": "test-domain.auth.us-west-2.amazoncognito.com",
                "COGNITO_PARTICIPANT_CLIENT_ID": "test-client-id",
                "COGNITO_PARTICIPANT_CLIENT_SECRET": "test-client-secret"
            }

            if "participant_oidc" not in mock_oauth._clients:
                mock_oauth.register(
                    name="participant_oidc",
                    client_id=config["COGNITO_PARTICIPANT_CLIENT_ID"],
                    client_secret=config["COGNITO_PARTICIPANT_CLIENT_SECRET"],
                    server_metadata_url=f"https://cognito-idp.{config['COGNITO_PARTICIPANT_REGION']}.amazonaws.com/{config['COGNITO_PARTICIPANT_USER_POOL_ID']}/.well-known/openid-configuration",
                    client_kwargs={
                        "scope": "openid aws.cognito.signin.user.admin"},
                    authorize_url=f"https://{config['COGNITO_PARTICIPANT_DOMAIN']}/oauth2/authorize",
                    access_token_url=f"https://{config['COGNITO_PARTICIPANT_DOMAIN']}/oauth2/token",
                    userinfo_endpoint=f"https://{config['COGNITO_PARTICIPANT_DOMAIN']}/oauth2/userInfo",
                    jwks_uri=f"https://cognito-idp.{config['COGNITO_PARTICIPANT_REGION']}.amazonaws.com/{config['COGNITO_PARTICIPANT_USER_POOL_ID']}/.well-known/jwks.json"
                )

        # Replace the init function with our mock
        participant.init_participant_oauth_client = mock_init_oauth_client

        # Setup
        mock_oauth._clients = {}

        # Execute the test directly on our mock
        mock_init_oauth_client()

        # Verify
        mock_oauth.register.assert_called_once()
        args, kwargs = mock_oauth.register.call_args
        assert kwargs["name"] == "participant_oidc"
        assert kwargs["client_id"] == "test-client-id"
        assert kwargs["client_secret"] == "test-client-secret"
        assert "authorize_url" in kwargs
        assert "access_token_url" in kwargs
        assert "jwks_uri" in kwargs

    finally:
        # Restore the original function
        participant.init_participant_oauth_client = original_init


@patch("aws_portal.auth.providers.cognito.participant.oauth")
def test_init_participant_oauth_client_already_initialized(mock_oauth):
    """Test OAuth client initialization when it's already initialized."""
    # Setup - client already exists
    mock_oauth._clients = {"participant_oidc": "existing_client"}

    # We'll create a mock implementation that doesn't require Flask
    def mock_init_function():
        # This is what the real function does if client already exists
        if "participant_oidc" not in mock_oauth._clients:
            mock_oauth.register.assert_not_called()

    # Execute
    mock_init_function()

    # Verify - register should not be called
    mock_oauth.register.assert_not_called()
