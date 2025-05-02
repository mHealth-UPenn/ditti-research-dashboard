# Ditti Research Dashboard
# Copyright (C) 2025 the Trustees of the University of Pennsylvania
#
# Ditti Research Dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Ditti Research Dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging

from sqlalchemy import func

from backend.auth.providers.cognito import CognitoAuthBase
from backend.auth.providers.cognito.constants import AUTH_ERROR_MESSAGES
from backend.extensions import oauth
from backend.models import StudySubject

logger = logging.getLogger(__name__)


class ParticipantAuth(CognitoAuthBase):
    """Specialized authentication class for participants."""

    def __init__(self):
        super().__init__("participant")

    def get_study_subject_from_ditti_id(self, ditti_id, include_archived=False):
        """
        Get a study subject by ditti_id.

        Parameters
        ----------
            ditti_id (str): The ditti ID to search for
            include_archived (bool, optional): Whether to include archived
                study subjects

        Returns
        -------
            StudySubject or None: The matching study subject or None if not found
        """
        if not ditti_id:
            return None

        query = StudySubject.query.filter(
            func.lower(StudySubject.ditti_id) == ditti_id.lower()
        )

        if not include_archived:
            query = query.filter(~StudySubject.is_archived)

        return query.first()

    def get_study_subject_from_token(self, id_token, include_archived=False):
        """
        Get a study subject from an ID token.

        Parameters
        ----------
            id_token (str): The ID token
            include_archived (bool, optional): Whether to include archived
                study subjects

        Returns
        -------
            tuple: (study_subject, error_message)
                study_subject: The StudySubject object if successful, else None
                error_message: Error message if study_subject is None, else None
        """
        success, claims = self.validate_token_for_authenticated_route(id_token)

        if not success:
            return None, claims

        ditti_id = claims.get("cognito:username")
        if not ditti_id:
            logger.warning("No cognito:username found in token claims")
            return None, "Invalid token"

        study_subject = self.get_study_subject_from_ditti_id(
            ditti_id, include_archived
        )
        if not study_subject:
            logger.warning(f"No study subject found for ID: {ditti_id}")
            return None, AUTH_ERROR_MESSAGES["not_found"]

        if study_subject.is_archived:
            logger.warning(
                f"Attempt to access with archived study subject: {ditti_id}"
            )
            return None, AUTH_ERROR_MESSAGES["account_archived"]

        return study_subject, None


def init_participant_oauth_client():
    """
    Initialize OAuth client for Cognito if not already configured.

    This configures the OAuth client with all necessary endpoints and credentials
    for interacting with AWS Cognito.
    """
    from flask import current_app

    if "participant_oidc" not in oauth._clients:
        region = current_app.config["COGNITO_PARTICIPANT_REGION"]
        user_pool_id = current_app.config["COGNITO_PARTICIPANT_USER_POOL_ID"]
        domain = current_app.config["COGNITO_PARTICIPANT_DOMAIN"]
        client_id = current_app.config["COGNITO_PARTICIPANT_CLIENT_ID"]
        client_secret = current_app.config["COGNITO_PARTICIPANT_CLIENT_SECRET"]

        oauth.register(
            name="participant_oidc",
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url=f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/openid-configuration",
            client_kwargs={"scope": "openid aws.cognito.signin.user.admin"},
            authorize_url=f"https://{domain}/oauth2/authorize",
            access_token_url=f"https://{domain}/oauth2/token",
            userinfo_endpoint=f"https://{domain}/oauth2/userInfo",
            jwks_uri=f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json",
        )
