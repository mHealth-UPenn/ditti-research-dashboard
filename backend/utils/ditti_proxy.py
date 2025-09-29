from typing import Any, Literal

import requests
from flask import Flask
from pydantic import BaseModel, Field, ValidationError

from shared.lambda_secrets_provider import SecretProvider

type DittiProxyEndpoint = Literal[
    "audio_file",
    "audio_tap",
    "tap",
    "user_permission",
]


class DittiProxyError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"DittiProxyError: {self.message}"


class DittiProxyGetResponse(BaseModel):
    data: list[dict[str, Any]] = Field(alias="data")
    num_results: int = Field(alias="numResults")
    message: str = Field(alias="message")


class DittiProxy:
    def __init__(self, app: Flask | None = None):
        self.client_id: str | None = None
        self.client_secret_name: str | None = None
        self.ditti_endpoint: str | None = None
        self.__secret_provider: SecretProvider | None = None

        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        self.client_id = app.config.get("DITTI_CLIENT_ID")
        self.client_secret_name = app.config.get("DITTI_CLIENT_SECRET_NAME")
        self.ditti_endpoint = app.config.get("DITTI_ENDPOINT")

        if not (
            self.client_id and self.client_secret_name and self.ditti_endpoint
        ):
            raise ValueError(
                "DITTI_CLIENT_ID, DITTI_CLIENT_SECRET_NAME, and DITTI_ENDPOINT must be set"
            )

        self.__secret_provider = SecretProvider(self.client_secret_name)

    def get(
        self,
        endpoint: DittiProxyEndpoint,
        *,
        query: str,
        attributes: list[str],
        timeout: int = 20,
    ) -> DittiProxyGetResponse:
        response = requests.get(
            self._get_url(endpoint),
            headers=self._get_auth_header(),
            params={"query": query, "attributes": str(attributes)},
            timeout=timeout,
        )

        if response.status_code != 200:
            self._handle_error(response.json())

        return self._parse_get_response(response.json())

    def _get_url(self, endpoint: DittiProxyEndpoint) -> str:
        return f"{self.ditti_endpoint}/{endpoint}"

    def _get_client_secret(self) -> str:
        return self.__secret_provider.get_secret().secret_string

    def _get_auth_header(self) -> dict[str, str]:
        return {"Authorization": f"{self.client_id}:{self._get_client_secret()}"}

    def _handle_error(self, response: dict[str, Any]) -> None:
        if "message" in response:
            raise DittiProxyError(response["message"])
        if "Message" in response:
            raise DittiProxyError(response["Message"])
        raise DittiProxyError("An unknown error occurred")

    def _parse_get_response(
        self, response: dict[str, Any]
    ) -> DittiProxyGetResponse:
        try:
            return DittiProxyGetResponse(**response)
        except ValidationError as e:
            raise DittiProxyError(f"Invalid response: {e}") from e
