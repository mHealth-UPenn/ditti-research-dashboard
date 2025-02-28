from flask import make_response


def create_error_response(message, status_code=401, error_code=None):
    """
    Create a standardized error response.

    Args:
        message (str): The user-friendly error message
        status_code (int): The HTTP status code (default: 401)
        error_code (str, optional): An optional error code for the client

    Returns:
        Response: A Flask response with standardized error format
    """
    response = {
        "msg": message
    }

    if error_code:
        response["code"] = error_code

    return make_response(response, status_code)


def create_success_response(data=None, message="Operation successful", status_code=200):
    """
    Create a standardized success response.

    Args:
        data (dict, optional): The response data
        message (str): The success message (default: "Operation successful")
        status_code (int): The HTTP status code (default: 200)

    Returns:
        tuple: (response_dict, status_code) for Flask to convert to a JSON response
    """
    response = {
        "msg": message
    }

    if data:
        # Merge data directly into response instead of nesting it
        response.update(data)

    return response, status_code
