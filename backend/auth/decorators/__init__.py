"""
Authentication decorators for aws_portal.

These decorators handle the authentication and authorization of users.
"""

from aws_portal.auth.decorators.jwt import auth_required
from aws_portal.auth.decorators.participant import participant_auth_required
from aws_portal.auth.decorators.researcher import researcher_auth_required

__all__ = [
    "auth_required",  # Deprecated, maintained for backward compatibility
    "participant_auth_required",
    "researcher_auth_required"
]
