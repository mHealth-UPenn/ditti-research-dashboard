"""
Password validation utilities for aws_portal.

This module is deprecated. It provides backward compatibility for the password validation
functions that were previously in aws_portal.utils.auth.
"""


def validate_password(password):
    """
    Validates whether a given password is 8-64 characters long.

    DEPRECATED: This function is maintained for backward compatibility.

    Args
    ----
    password: str
        The password to validate

    Returns
    -------
    str: "valid" or an error message
    """
    if len(password) < 8:
        return "Minimum password length is 8 characters"

    if 64 < len(password):
        return "Maximum password length is 64 characters"

    return "valid"
