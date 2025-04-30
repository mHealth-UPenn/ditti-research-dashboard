import pytest
from moto import mock_aws
from shared.tokens_manager import TokensManager
from botocore.exceptions import ClientError
import json


@pytest.fixture(scope="function")
def tokens_manager():
    """
    Pytest fixture to initialize TokensManager within a mocked AWS Secrets Manager context.
    """
    with mock_aws():
        # Instantiate TokensManager within the mocked context
        tm = TokensManager(fstr="{api_name}-tokens-testing")
        yield tm


def test_add_and_get_api_token(tokens_manager):
    """
    Test adding a new API token and retrieving it.
    """
    api_name = "Fitbit"
    ditti_id = "123"
    tokens = {
        "access_token": "access123",
        "refresh_token": "refresh123",
        "expires_at": 1700000000
    }

    # Add the API token
    tokens_manager.add_or_update_api_token(api_name, ditti_id, tokens)

    # Retrieve the API token
    retrieved_tokens = tokens_manager.get_api_tokens(
        api_name, ditti_id)

    assert retrieved_tokens == tokens


def test_update_api_token(tokens_manager):
    """
    Test updating an existing API token for a study subject.
    """
    api_name = "Fitbit"
    ditti_id = "456"
    initial_tokens = {
        "access_token": "initial_access",
        "refresh_token": "initial_refresh",
        "expires_at": 1700000000
    }
    updated_tokens = {
        "access_token": "updated_access",
        "refresh_token": "updated_refresh",
        "expires_at": 1700003600
    }

    # Add the initial API token
    tokens_manager.add_or_update_api_token(
        api_name, ditti_id, initial_tokens)

    # Update the API token
    tokens_manager.add_or_update_api_token(
        api_name, ditti_id, updated_tokens)

    # Retrieve the updated API token
    retrieved_tokens = tokens_manager.get_api_tokens(
        api_name, ditti_id)

    assert retrieved_tokens == updated_tokens


def test_get_nonexistent_api_token(tokens_manager):
    """
    Test retrieving tokens for a non-existent study subject.
    """
    api_name = "Fitbit"
    ditti_id = "789"

    with pytest.raises(KeyError) as excinfo:
        tokens_manager.get_api_tokens(api_name, ditti_id)

    assert f"Tokens for Study Subject {
        ditti_id} not found in API '{api_name}'." in str(excinfo.value)


def test_delete_api_token(tokens_manager):
    """
    Test deleting an existing API token for a study subject.
    """
    api_name = "Fitbit"
    ditti_id = "321"
    tokens = {
        "access_token": "access321",
        "refresh_token": "refresh321",
        "expires_at": 1700007200
    }

    # Add the API token
    tokens_manager.add_or_update_api_token(api_name, ditti_id, tokens)

    # Ensure the token exists
    retrieved_tokens = tokens_manager.get_api_tokens(
        api_name, ditti_id)
    assert retrieved_tokens == tokens

    # Delete the API token
    tokens_manager.delete_api_tokens(api_name, ditti_id)

    # Attempt to retrieve the deleted token
    with pytest.raises(KeyError) as excinfo:
        tokens_manager.get_api_tokens(api_name, ditti_id)

    assert f"Tokens for Study Subject {
        ditti_id} not found in API '{api_name}'." in str(excinfo.value)


def test_delete_nonexistent_api_token(tokens_manager):
    """
    Test deleting tokens for a non-existent study subject.
    """
    api_name = "Fitbit"
    ditti_id = "654"

    with pytest.raises(KeyError) as excinfo:
        tokens_manager.delete_api_tokens(api_name, ditti_id)

    assert f"Tokens for Study Subject {
        ditti_id} not found in API '{api_name}'." in str(excinfo.value)


def test_add_api_token_creates_new_secret(tokens_manager):
    """
    Test that adding a token for a new API creates a new secret in Secrets Manager.
    """
    api_name = "Garmin"
    ditti_id = "111"
    tokens = {
        "access_token": "garmin_access",
        "refresh_token": "garmin_refresh",
        "expires_at": 1700010800
    }

    # Add the API token
    tokens_manager.add_or_update_api_token(api_name, ditti_id, tokens)

    # Retrieve the secret directly using boto3 to verify its existence
    client = tokens_manager.client
    secret_name = f"{api_name}-tokens-testing"

    response = client.get_secret_value(SecretId=secret_name)
    secret_data = json.loads(response["SecretString"])

    assert str(ditti_id) in secret_data
    assert secret_data[str(ditti_id)] == tokens


def test_get_api_tokens_with_no_secret_string(tokens_manager):
    """
    Test retrieving tokens when the secret exists but contains no SecretString.
    """
    api_name = "Fitbit"
    ditti_id = "999"
    secret_name = f"{api_name}-tokens-testing"

    # Create a secret with SecretBinary instead of SecretString
    tokens_manager.client.create_secret(
        Name=secret_name,
        SecretBinary=b"binarydata"
    )

    with pytest.raises(KeyError) as excinfo:
        tokens_manager.get_api_tokens(api_name, ditti_id)

    assert f"Secret '{
        secret_name}' does not contain a SecretString." in str(excinfo.value)


def test_add_api_token_client_error(monkeypatch, tokens_manager):
    """
    Test handling of ClientError when adding/updating an API token.
    """
    api_name = "Fitbit"
    ditti_id = "222"
    tokens = {
        "access_token": "access222",
        "refresh_token": "refresh222",
        "expires_at": 1700014400
    }

    def mock_put_secret_value(*args, **kwargs):
        raise ClientError(
            error_response={
                "Error": {
                    "Code": "AccessDeniedException",
                    "Message": "Access denied"
                }
            },
            operation_name="PutSecretValue"
        )

    # Monkeypatch the put_secret_value method to raise ClientError
    monkeypatch.setattr(tokens_manager.client,
                        "put_secret_value", mock_put_secret_value)

    with pytest.raises(ClientError) as excinfo:
        tokens_manager.add_or_update_api_token(
            api_name, ditti_id, tokens)

    assert "Access denied" in str(excinfo.value)


def test_get_api_tokens_client_error(monkeypatch, tokens_manager):
    """
    Test handling of ClientError when retrieving an API token.
    """
    api_name = "Fitbit"
    ditti_id = "333"

    def mock_get_secret_value(*args, **kwargs):
        raise ClientError(
            error_response={
                "Error": {
                    "Code": "InternalServiceError",
                    "Message": "Internal service error"
                }
            },
            operation_name="GetSecretValue"
        )

    # Monkeypatch the get_secret_value method to raise ClientError
    monkeypatch.setattr(tokens_manager.client,
                        "get_secret_value", mock_get_secret_value)

    with pytest.raises(ClientError) as excinfo:
        tokens_manager.get_api_tokens(api_name, ditti_id)

    assert "Internal service error" in str(excinfo.value)


def test_delete_api_tokens_client_error(monkeypatch, tokens_manager):
    """
    Test handling of ClientError when deleting an API token.
    """
    api_name = "Fitbit"
    ditti_id = "444"

    def mock_put_secret_value(*args, **kwargs):
        raise ClientError(
            error_response={
                "Error": {
                    "Code": "ResourceNotFoundException",
                    "Message": "Secret not found"
                }
            },
            operation_name="PutSecretValue"
        )

    # First, add a token normally
    tokens = {
        "access_token": "access444",
        "refresh_token": "refresh444",
        "expires_at": 1700018000
    }
    tokens_manager.add_or_update_api_token(api_name, ditti_id, tokens)

    # Monkeypatch the put_secret_value method to raise ClientError during deletion
    monkeypatch.setattr(tokens_manager.client,
                        "put_secret_value", mock_put_secret_value)

    with pytest.raises(ClientError) as excinfo:
        tokens_manager.delete_api_tokens(api_name, ditti_id)

    assert "Secret not found" in str(excinfo.value)


def test_add_multiple_tokens_for_different_study_subjects(tokens_manager):
    """
    Test adding tokens for multiple study subjects within the same API.
    """
    api_name = "Fitbit"
    study_subjects_tokens = {
        "101": {
            "access_token": "access101",
            "refresh_token": "refresh101",
            "expires_at": 1700021600
        },
        "202": {
            "access_token": "access202",
            "refresh_token": "refresh202",
            "expires_at": 1700025200
        },
        "303": {
            "access_token": "access303",
            "refresh_token": "refresh303",
            "expires_at": 1700028800
        }
    }

    # Add tokens for each study subject
    for ditti_id, tokens in study_subjects_tokens.items():
        tokens_manager.add_or_update_api_token(api_name, ditti_id, tokens)

    # Retrieve and verify each token
    for ditti_id, tokens in study_subjects_tokens.items():
        retrieved_tokens = tokens_manager.get_api_tokens(api_name, ditti_id)
        assert retrieved_tokens == tokens


def test_overwrite_tokens_with_partial_data(tokens_manager):
    """
    Test updating tokens with partial data (e.g., missing refresh_token).
    """
    api_name = "Fitbit"
    ditti_id = "555"
    initial_tokens = {
        "access_token": "initial_access555",
        "refresh_token": "initial_refresh555",
        "expires_at": 1700032400
    }
    partial_update = {
        "access_token": "updated_access555",
        # Missing 'refresh_token'
        "expires_at": 1700036000
    }
    expected_tokens = {
        "access_token": "updated_access555",
        "refresh_token": "initial_refresh555",  # Should remain unchanged
        "expires_at": 1700036000
    }

    # Add the initial API token
    tokens_manager.add_or_update_api_token(
        api_name, ditti_id, initial_tokens)

    # Update the API token with partial data
    tokens_manager.add_or_update_api_token(
        api_name, ditti_id, partial_update)

    # Retrieve the updated API token
    retrieved_tokens = tokens_manager.get_api_tokens(
        api_name, ditti_id)

    assert retrieved_tokens == expected_tokens


def test_add_api_token_with_invalid_api_name(tokens_manager):
    """
    Test adding an API token with an invalid API name (e.g., empty string).
    """
    api_name = ""
    ditti_id = "777"
    tokens = {
        "access_token": "access777",
        "refresh_token": "refresh777",
        "expires_at": 1700043600
    }

    with pytest.raises(Exception) as excinfo:
        tokens_manager.add_or_update_api_token(
            api_name, ditti_id, tokens)

    assert "api_name must be a non-empty string." in str(
        excinfo.value)


def test_get_api_tokens_with_invalid_api_name(tokens_manager):
    """
    Test retrieving tokens with an invalid API name (e.g., None).
    """
    api_name = None
    ditti_id = "888"

    with pytest.raises(KeyError) as excinfo:
        tokens_manager.get_api_tokens(api_name, ditti_id)

    assert f"Tokens for Study Subject {
        ditti_id} not found in API '{api_name}'." in str(excinfo.value)
