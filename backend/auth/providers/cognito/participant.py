# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may]
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

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
        logger.debug("Initialized ParticipantAuth class")

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
        logger.debug(
            f"Getting study subject from ditti_id: {ditti_id}, include_archived: {include_archived}"
        )

        if not ditti_id:
            logger.debug("No ditti_id provided for study subject lookup")
            return None

        query = StudySubject.query.filter(
            func.lower(StudySubject.ditti_id) == ditti_id.lower()
        )

        if not include_archived:
            query = query.filter(~StudySubject.is_archived)
            logger.debug("Filtering out archived study subjects")

        study_subject = query.first()
        if study_subject:
            logger.debug(
                f"Found study subject: {study_subject.id} (archived: {study_subject.is_archived})"
            )
        else:
            logger.debug(f"No study subject found for ditti_id: {ditti_id}")

        return study_subject

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
        logger.debug(
            f"Getting study subject from token, include_archived: {include_archived}"
        )

        success, claims = self.validate_token_for_authenticated_route(id_token)

        if not success:
            logger.warning(f"Token validation failed for participant: {claims}")
            return None, claims  # claims here is the error message

        logger.debug(
            f"Token validation successful for participant, claims: {claims}"
        )

        ditti_id = claims.get("cognito:username")
        if not ditti_id:
            logger.warning("No cognito:username found in token claims")
            return (
                None,
                AUTH_ERROR_MESSAGES["invalid_token_format"],
            )

        logger.debug(f"Extracted ditti_id from participant token: {ditti_id}")

        # Check if subject exists regardless of archived status
        any_subject = self.get_study_subject_from_ditti_id(
            ditti_id, include_archived=True
        )

        # If found but archived and not including archived subjects, return archived error
        if any_subject and any_subject.is_archived and not include_archived:
            logger.warning(
                f"Attempt to access with archived study subject: {ditti_id}"
            )
            return (
                None,
                AUTH_ERROR_MESSAGES["account_archived"],
            )

        # Get subject with respect to include_archived parameter
        study_subject = self.get_study_subject_from_ditti_id(
            ditti_id, include_archived
        )

        if not study_subject:
            logger.warning(
                f"No active study subject found for ditti_id: {ditti_id}"
            )
            return (
                None,
                AUTH_ERROR_MESSAGES["not_found"],
            )

        logger.debug(f"Successfully retrieved study subject: {study_subject.id}")
        return study_subject, None


def init_participant_oauth_client():
    """
    Initialize OAuth client for Cognito if not already configured.

    This configures the OAuth client with all necessary endpoints and credentials
    for interacting with AWS Cognito.
    """
    from flask import current_app

    logger.debug("Initializing participant OAuth client")

    if "participant_oidc" not in oauth._clients:
        logger.debug(
            "Participant OAuth client not found, creating new configuration"
        )

        region = current_app.config["COGNITO_PARTICIPANT_REGION"]
        user_pool_id = current_app.config["COGNITO_PARTICIPANT_USER_POOL_ID"]
        domain = current_app.config["COGNITO_PARTICIPANT_DOMAIN"]
        client_id = current_app.config["COGNITO_PARTICIPANT_CLIENT_ID"]
        client_secret = current_app.config["COGNITO_PARTICIPANT_CLIENT_SECRET"]

        logger.debug(
            f"Participant OAuth configuration - Region: {region}, User Pool: {user_pool_id}, Domain: {domain}"
        )

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

        logger.debug("Participant OAuth client registered successfully")
    else:
        logger.debug("Participant OAuth client already exists")
