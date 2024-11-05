import pytest
from moto import mock_aws
from aws_portal.utils.secrets_manager import SecretsManager
from botocore.exceptions import ClientError


@pytest.fixture(scope="function")
def secrets_manager():
    with mock_aws():
        # Instantiate SecretsManager within the mocked context
        sm = SecretsManager()
        yield sm


def test_store_and_get_secret(secrets_manager):
    secret_uuid = "test-secret"
    secret_value = "my-secret-value"

    secrets_manager.store_secret(secret_uuid, secret_value)
    retrieved_value = secrets_manager.get_secret(secret_uuid)

    assert retrieved_value == secret_value


def test_store_and_get_secret_dict(secrets_manager):
    secret_uuid = "test-secret-dict"
    secret_value = {"username": "admin", "password": "secret"}

    secrets_manager.store_secret(secret_uuid, secret_value)
    retrieved_value = secrets_manager.get_secret(secret_uuid)

    assert retrieved_value == secret_value


def test_get_nonexistent_secret(secrets_manager):
    secret_uuid = "nonexistent-secret"
    with pytest.raises(KeyError) as excinfo:
        secrets_manager.get_secret(secret_uuid)
    assert f"Secret with UUID {secret_uuid} not found." in str(excinfo.value)


def test_store_secret_error(secrets_manager, monkeypatch):
    secret_uuid = "test-secret"
    secret_value = "my-secret-value"

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

    # Monkeypatch the client to raise an exception
    monkeypatch.setattr(secrets_manager.client,
                        "put_secret_value", mock_put_secret_value)

    with pytest.raises(ClientError) as excinfo:
        secrets_manager.store_secret(secret_uuid, secret_value)

    assert "Access denied" in str(excinfo.value)


def test_get_secret_without_secret_string(secrets_manager):
    secret_uuid = "test-secret-no-secret-string"

    # Create a secret with SecretBinary instead of SecretString
    secrets_manager.client.create_secret(
        Name=secret_uuid,
        SecretBinary=b"foobar"
    )

    with pytest.raises(KeyError) as excinfo:
        secrets_manager.get_secret(secret_uuid)
    assert f"Secret with UUID {
        secret_uuid} does not contain a SecretString." in str(excinfo.value)
