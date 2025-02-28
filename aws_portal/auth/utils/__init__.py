"""
Authentication utilities for aws_portal.
These utilities are used across different authentication implementations
and provide common functionality for cookies, tokens, sessions, and responses.
"""

from aws_portal.auth.utils.cookies import (
    set_auth_cookies,
    clear_auth_cookies,
)
from aws_portal.auth.utils.responses import (
    create_error_response,
    create_success_response,
)
from aws_portal.auth.utils.session import (
    AuthFlowSession
)
from aws_portal.auth.utils.tokens import (
    get_cognito_jwks,
    generate_code_verifier,
    create_code_challenge,
)

__all__ = [
    "set_auth_cookies",
    "clear_auth_cookies",
    "create_error_response",
    "create_success_response",
    "AuthFlowSession",
    "get_cognito_jwks",
    "generate_code_verifier",
    "create_code_challenge",
]
