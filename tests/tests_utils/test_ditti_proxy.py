from unittest.mock import patch

import pytest

from backend.utils.ditti_proxy import (
    DittiProxy,
    DittiProxyCreateResponse,
    DittiProxyDeleteResponse,
    DittiProxyEditResponse,
    DittiProxyEndpoint,
    DittiProxyError,
    DittiProxyGetResponse,
)

DITTI_CLIENT_ID = "test_client_id"
DITTI_CLIENT_SECRET_NAME = "test_client_secret_name"
DITTI_ENDPOINT = "test_endpoint"
DITTI_CLIENT_SECRET = "test_client_secret"


class MockFlask:
    def __init__(self, mock_config: dict[str, str]):
        self.config = mock_config


class MockSecretPayload:
    def __init__(self, mock_secret: str):
        self.secret_string = mock_secret


class MockSecretProvider:
    def get_secret(self) -> MockSecretPayload:
        return MockSecretPayload(DITTI_CLIENT_SECRET)


class MockDittiProxy(DittiProxy):
    def __init__(self, mock_flask: MockFlask):
        super().__init__(mock_flask)
        self._secret_provider = MockSecretProvider()


def mock_get_responses() -> list[dict[str, str]]:
    return [
        {"data": [{"id": "test_id"}], "numResults": 1, "message": "test_message"},
        {"data": [], "numResults": 0, "message": "test_message"},
    ]


def mock_create_responses() -> list[dict[str, str]]:
    return [
        {"id": "test_id_1", "message": "test_message"},
        {"id": "test_id_2", "message": "test_message"},
    ]


def mock_edit_responses() -> list[dict[str, str]]:
    return [
        {"id": "test_id_1", "message": "test_message"},
        {"id": "test_id_2", "message": "test_message"},
    ]


def mock_delete_responses() -> list[dict[str, str]]:
    return [
        {"id": "test_id_1", "message": "test_message"},
        {"id": "test_id_2", "message": "test_message"},
    ]


@pytest.fixture
def mock_config() -> dict[str, str]:
    return {
        "DITTI_CLIENT_ID": DITTI_CLIENT_ID,
        "DITTI_CLIENT_SECRET_NAME": DITTI_CLIENT_SECRET_NAME,
        "DITTI_ENDPOINT": DITTI_ENDPOINT,
    }


@pytest.fixture
def mock_flask(mock_config: dict[str, str]) -> MockFlask:
    return MockFlask(mock_config)


@pytest.fixture
def mock_ditti_proxy(mock_flask: MockFlask) -> MockDittiProxy:
    return MockDittiProxy(mock_flask)


def test_validate_app(mock_ditti_proxy: MockDittiProxy, mock_flask: MockFlask):
    assert mock_ditti_proxy._validate_app(mock_flask) is True


@pytest.mark.parametrize(
    "mock_config",
    [
        {},
        {"DITTI_CLIENT_ID": DITTI_CLIENT_ID},
        {"DITTI_CLIENT_SECRET_NAME": DITTI_CLIENT_SECRET_NAME},
        {"DITTI_ENDPOINT": DITTI_ENDPOINT},
        {
            "DITTI_CLIENT_ID": DITTI_CLIENT_ID,
            "DITTI_CLIENT_SECRET_NAME": DITTI_CLIENT_SECRET_NAME,
        },
        {"DITTI_CLIENT_ID": DITTI_CLIENT_ID, "DITTI_ENDPOINT": DITTI_ENDPOINT},
        {
            "DITTI_CLIENT_SECRET_NAME": DITTI_CLIENT_SECRET_NAME,
            "DITTI_ENDPOINT": DITTI_ENDPOINT,
        },
    ],
)
def test_validate_app_invalid_config(mock_config: dict[str, str]):
    with pytest.raises(ValueError, match="Missing required configuration:"):
        DittiProxy._validate_app(MockFlask(mock_config))


@pytest.mark.parametrize(
    "endpoint",
    [
        "audio_file",
        "audio_tap",
        "tap",
        "user_permission",
    ],
)
def test_get_url(mock_ditti_proxy: MockDittiProxy, endpoint: DittiProxyEndpoint):
    assert mock_ditti_proxy._get_url(endpoint) == f"{DITTI_ENDPOINT}/{endpoint}"


def test_get_client_secret(mock_ditti_proxy: MockDittiProxy):
    assert mock_ditti_proxy._get_client_secret() == DITTI_CLIENT_SECRET


def test_get_auth_header(mock_ditti_proxy: MockDittiProxy):
    assert mock_ditti_proxy._get_auth_header() == {
        "Authorization": f"{DITTI_CLIENT_ID}:{DITTI_CLIENT_SECRET}"
    }


@pytest.mark.parametrize(
    ("mock_response", "expected_error"),
    [
        ({"message": "test_message"}, "test_message"),
        ({"Message": "test_message"}, "test_message"),
        (
            {"unknown_key": "test_message"},
            "An unknown error occurred",
        ),
    ],
)
def test_handle_error(
    mock_ditti_proxy: MockDittiProxy,
    mock_response: dict[str, str],
    expected_error: str,
):
    with pytest.raises(DittiProxyError, match=expected_error):
        mock_ditti_proxy._handle_error(mock_response)


@pytest.mark.parametrize("mock_response", mock_get_responses())
def test_parse_get_response(
    mock_ditti_proxy: MockDittiProxy,
    mock_response: dict[str, str],
):
    expected_response = DittiProxyGetResponse(**mock_response)
    actual_response = mock_ditti_proxy._parse_get_response(mock_response)
    assert actual_response == expected_response


def test_parse_get_response_invalid_response(mock_ditti_proxy: MockDittiProxy):
    with pytest.raises(DittiProxyError, match="Invalid response:"):
        mock_ditti_proxy._parse_get_response(
            {"invalid_response": "test_response"}
        )


@pytest.mark.parametrize("mock_response", mock_create_responses())
def test_parse_create_response(
    mock_ditti_proxy: MockDittiProxy, mock_response: dict[str, str]
):
    expected_response = DittiProxyCreateResponse(**mock_response)
    actual_response = mock_ditti_proxy._parse_create_response(mock_response)
    assert actual_response == expected_response


def test_parse_create_response_invalid_response(mock_ditti_proxy: MockDittiProxy):
    with pytest.raises(DittiProxyError, match="Invalid response:"):
        mock_ditti_proxy._parse_create_response(
            {"invalid_response": "test_response"}
        )


@pytest.mark.parametrize("mock_response", mock_edit_responses())
def test_parse_edit_response(
    mock_ditti_proxy: MockDittiProxy, mock_response: dict[str, str]
):
    expected_response = DittiProxyEditResponse(**mock_response)
    actual_response = mock_ditti_proxy._parse_edit_response(mock_response)
    assert actual_response == expected_response


def test_parse_edit_response_invalid_response(mock_ditti_proxy: MockDittiProxy):
    with pytest.raises(DittiProxyError, match="Invalid response:"):
        mock_ditti_proxy._parse_edit_response(
            {"invalid_response": "test_response"}
        )


@pytest.mark.parametrize("mock_response", mock_delete_responses())
def test_parse_delete_response(
    mock_ditti_proxy: MockDittiProxy, mock_response: dict[str, str]
):
    expected_response = DittiProxyDeleteResponse(**mock_response)
    actual_response = mock_ditti_proxy._parse_delete_response(mock_response)
    assert actual_response == expected_response


def test_parse_delete_response_invalid_response(mock_ditti_proxy: MockDittiProxy):
    with pytest.raises(DittiProxyError, match="Invalid response:"):
        mock_ditti_proxy._parse_delete_response(
            {"invalid_response": "test_response"}
        )


@pytest.mark.parametrize("mock_response", mock_get_responses())
def test_get(mock_ditti_proxy: MockDittiProxy, mock_response: dict[str, str]):
    expected_response = DittiProxyGetResponse(**mock_response)

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response
        actual_response = mock_ditti_proxy.get(
            "audio_file",
            query="test_query",
            attributes=["test_attribute"],
        )
        assert actual_response == expected_response


def test_get_invalid_response(mock_ditti_proxy: MockDittiProxy):
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 400
        mock_get.return_value.json.return_value = {"message": "test_response"}
        with pytest.raises(DittiProxyError, match="test_response"):
            mock_ditti_proxy.get(
                "audio_file",
                query="test_query",
                attributes=["test_attribute"],
            )


@pytest.mark.parametrize("mock_response", mock_create_responses())
def test_create(mock_ditti_proxy: MockDittiProxy, mock_response: dict[str, str]):
    expected_response = DittiProxyCreateResponse(**mock_response)
    with patch("requests.put") as mock_put:
        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = mock_response
        actual_response = mock_ditti_proxy.create(
            "audio_file", data={"test_data": "test_data"}
        )
        assert actual_response == expected_response


def test_create_invalid_response(mock_ditti_proxy: MockDittiProxy):
    with patch("requests.put") as mock_put:
        mock_put.return_value.status_code = 400
        mock_put.return_value.json.return_value = {"message": "test_response"}
        with pytest.raises(DittiProxyError, match="test_response"):
            mock_ditti_proxy.create("audio_file", data={"test_data": "test_data"})


@pytest.mark.parametrize("mock_response", mock_edit_responses())
def test_edit(mock_ditti_proxy: MockDittiProxy, mock_response: dict[str, str]):
    expected_response = DittiProxyEditResponse(**mock_response)
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response
        actual_response = mock_ditti_proxy.edit(
            "audio_file", data={"test_data": "test_data"}
        )
        assert actual_response == expected_response


def test_edit_invalid_response(mock_ditti_proxy: MockDittiProxy):
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {"message": "test_response"}
        with pytest.raises(DittiProxyError, match="test_response"):
            mock_ditti_proxy.edit("audio_file", data={"test_data": "test_data"})


@pytest.mark.parametrize("mock_response", mock_delete_responses())
def test_delete(mock_ditti_proxy: MockDittiProxy, mock_response: dict[str, str]):
    expected_response = DittiProxyDeleteResponse(**mock_response)
    with patch("requests.delete") as mock_delete:
        mock_delete.return_value.status_code = 200
        mock_delete.return_value.json.return_value = mock_response
        actual_response = mock_ditti_proxy.delete(
            "audio_file", delete_id="test_delete_id"
        )
        assert actual_response == expected_response


def test_delete_invalid_response(mock_ditti_proxy: MockDittiProxy):
    with patch("requests.delete") as mock_delete:
        mock_delete.return_value.status_code = 400
        mock_delete.return_value.json.return_value = {"message": "test_response"}
        with pytest.raises(DittiProxyError, match="test_response"):
            mock_ditti_proxy.delete("audio_file", delete_id="test_delete_id")
