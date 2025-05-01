import json

import pytest
from flask import Flask

from backend.auth.utils.responses import (
    create_error_response,
    create_success_response,
)


@pytest.fixture
def mock_app():
    """Create a minimal Flask app for testing without database dependencies."""
    app = Flask(__name__)
    return app


def test_create_error_response_basic(mock_app):
    """
    Test creating a basic error response.

    Verifies the default status code (401) and error message formatting.
    """
    with mock_app.app_context():
        response = create_error_response("Test error message")

        # Verify response properties
        assert response.status_code == 401  # Default status code

        # Parse and verify the response data
        data = json.loads(response.data)
        assert data["msg"] == "Test error message"
        assert "code" not in data


def test_create_error_response_with_status_code(mock_app):
    """
    Test creating an error response with custom status code.

    Verifies that a provided status code overrides the default.
    """
    with mock_app.app_context():
        response = create_error_response("Test error message", status_code=403)

        # Verify response properties
        assert response.status_code == 403

        # Parse and verify the response data
        data = json.loads(response.data)
        assert data["msg"] == "Test error message"
        assert "code" not in data


def test_create_error_response_with_error_code(mock_app):
    """
    Test creating an error response with error code.

    Verifies that an error code is included in the response when provided.
    """
    with mock_app.app_context():
        response = create_error_response(
            "Test error message", status_code=400, error_code="VALIDATION_ERROR"
        )

        # Verify response properties
        assert response.status_code == 400

        # Parse and verify the response data
        data = json.loads(response.data)
        assert data["msg"] == "Test error message"
        assert data["code"] == "VALIDATION_ERROR"


def test_create_error_response_with_special_chars(mock_app):
    """
    Test creating an error response with special characters in the message.

    Verifies proper handling of messages with special characters.
    """
    with mock_app.app_context():
        special_message = "Error! @#$%^&*() <script>alert('xss')</script> エラー"
        response = create_error_response(special_message)

        # Parse and verify the response data
        data = json.loads(response.data)
        assert data["msg"] == special_message


def test_create_error_response_with_empty_message(mock_app):
    """
    Test creating an error response with an empty message.

    Verifies the API handles empty messages properly.
    """
    with mock_app.app_context():
        response = create_error_response("")

        # Parse and verify the response data
        data = json.loads(response.data)
        assert data["msg"] == ""


def test_create_success_response_basic():
    """
    Test creating a basic success response.

    Verifies the default values for a success response with no parameters.
    """
    # Success responses return a tuple of (response_dict, status_code)
    response_dict, status_code = create_success_response()

    # Verify the tuple components
    assert status_code == 200  # Default status code
    assert response_dict["msg"] == "Operation successful"
    assert len(response_dict) == 1  # Only contains message


def test_create_success_response_with_data():
    """
    Test creating a success response with data.

    Verifies that provided data is properly merged into the response.
    """
    test_data = {"key": "value", "nested": {"inner": "data"}}
    response_dict, status_code = create_success_response(data=test_data)

    # Verify the tuple components
    assert status_code == 200
    assert response_dict["msg"] == "Operation successful"
    assert response_dict["key"] == "value"
    assert response_dict["nested"]["inner"] == "data"


def test_create_success_response_with_custom_message():
    """
    Test creating a success response with custom message.

    Verifies that a provided message overrides the default.
    """
    response_dict, status_code = create_success_response(
        message="Custom success message"
    )

    # Verify the tuple components
    assert status_code == 200
    assert response_dict["msg"] == "Custom success message"
    assert len(response_dict) == 1  # Only contains message


def test_create_success_response_with_custom_status():
    """
    Test creating a success response with custom status code.

    Verifies that a provided status code overrides the default.
    """
    response_dict, status_code = create_success_response(status_code=201)

    # Verify the tuple components
    assert status_code == 201
    assert response_dict["msg"] == "Operation successful"
    assert len(response_dict) == 1  # Only contains message


def test_create_success_response_complete():
    """
    Test creating a complete success response with all parameters.

    Verifies that all customizations are applied correctly.
    """
    test_data = {"id": 123, "name": "Test"}
    response_dict, status_code = create_success_response(
        data=test_data, message="Created successfully", status_code=201
    )

    # Verify the tuple components
    assert status_code == 201
    assert response_dict["msg"] == "Created successfully"
    assert response_dict["id"] == 123
    assert response_dict["name"] == "Test"


def test_create_success_response_with_msg_key_conflict():
    """
    Test creating a success response with data containing a 'msg' key.

    Verifies how key conflicts are handled when data contains reserved keys.
    """
    test_data = {"msg": "This should be overwritten", "id": 456}
    response_dict, status_code = create_success_response(
        data=test_data, message="This message should win"
    )

    # Verify the tuple components - the explicit message parameter should take precedence
    assert status_code == 200
    assert response_dict["msg"] == "This message should win"
    assert response_dict["id"] == 456


def test_create_success_response_with_none_message():
    """
    Test creating a success response with None as the message.

    Verifies how the API handles None messages.
    """
    response_dict, status_code = create_success_response(message=None)

    # Verify behavior - implementation may vary, but we should get a valid response
    assert status_code == 200
    # Should still have a message key, even if value is None
    assert "msg" in response_dict


def test_create_success_response_with_none_data():
    """
    Test creating a success response with None as the data.

    Verifies explicit None handling matches default behavior.
    """
    response_dict, status_code = create_success_response(data=None)

    # Verify the tuple components
    assert status_code == 200
    assert response_dict["msg"] == "Operation successful"
    assert len(response_dict) == 1  # Only contains message


def test_create_success_response_with_special_chars():
    """
    Test creating a success response with special characters in the message.

    Verifies proper handling of messages with special characters.
    """
    special_message = "Success! @#$%^&*() 成功"
    response_dict, status_code = create_success_response(message=special_message)

    # Verify the tuple components
    assert status_code == 200
    assert response_dict["msg"] == special_message
