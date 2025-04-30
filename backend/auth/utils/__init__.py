"""
Authentication utilities for backend.

These utilities are used across different authentication implementations
and provide common functionality for cookies, tokens, sessions, and responses.
"""

from backend.auth.utils.auth_helpers import (
    check_permissions,
    get_token_from_request,
)
from backend.auth.utils.cookies import clear_auth_cookies, set_auth_cookies
from backend.auth.utils.researcher_cognito import (
    create_researcher,
    delete_researcher,
    get_researcher,
    get_researcher_cognito_client,
    update_researcher,
)
from backend.auth.utils.responses import (
    create_error_response,
    create_success_response,
)
from backend.auth.utils.session import AuthFlowSession
from backend.auth.utils.tokens import (
    create_code_challenge,
    generate_code_verifier,
    get_cognito_jwks,
)

__all__ = [
    "AuthFlowSession",
    "check_permissions",
    "clear_auth_cookies",
    "create_code_challenge",
    "create_error_response",
    "create_researcher",
    "create_success_response",
    "delete_researcher",
    "generate_code_verifier",
    "get_cognito_jwks",
    "get_researcher",
    "get_researcher_cognito_client",
    "get_token_from_request",
    "set_auth_cookies",
    "update_researcher",
]
