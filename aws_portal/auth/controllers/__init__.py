"""
Authentication controllers for aws_portal.
These controllers handle the business logic for authentication, independent
of the specific authentication provider implementation.
"""

from aws_portal.auth.controllers.base import AuthControllerBase
from aws_portal.auth.controllers.participant import ParticipantAuthController
from aws_portal.auth.controllers.researcher import ResearcherAuthController

__all__ = ["AuthControllerBase",
           "ParticipantAuthController", "ResearcherAuthController"]
