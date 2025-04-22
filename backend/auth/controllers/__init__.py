"""
Authentication controllers for backend.

These controllers handle the business logic for authentication, independent
of the specific authentication provider implementation.
"""

from backend.auth.controllers.base import AuthControllerBase
from backend.auth.controllers.participant import ParticipantAuthController
from backend.auth.controllers.researcher import ResearcherAuthController

__all__ = [
    "AuthControllerBase",
    "ParticipantAuthController",
    "ResearcherAuthController",
]
