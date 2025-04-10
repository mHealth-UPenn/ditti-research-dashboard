"""
Authentication decorators for backend.

These decorators handle the authentication and authorization of users.
"""

from backend.auth.decorators.jwt import auth_required
from backend.auth.decorators.participant import participant_auth_required
from backend.auth.decorators.researcher import researcher_auth_required

__all__ = [
    "auth_required",  # Deprecated, maintained for backward compatibility
    "participant_auth_required",
    "researcher_auth_required"
]
