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
from datetime import UTC, datetime

from flask import request

from backend.auth.controllers.base import AuthControllerBase
from backend.auth.providers.cognito import (
    AUTH_ERROR_MESSAGES,
    ParticipantAuth,
    init_participant_oauth_client,
)
from backend.auth.utils import create_error_response, create_success_response
from backend.extensions import db
from backend.models import StudySubject

logger = logging.getLogger(__name__)


class ParticipantAuthController(AuthControllerBase):
    """Authentication controller for participants."""

    def __init__(self):
        """Initialize the participant auth controller."""
        super().__init__("participant")
        self.auth_manager = ParticipantAuth()

    def init_oauth_client(self):
        """Initialize the OAuth client."""
        init_participant_oauth_client()

    def get_scope(self):
        """
        Get the OAuth scope.

        Returns
        -------
            str: The OAuth scope
        """
        # Check if elevated scope is requested
        elevated = request.args.get("elevated") == "true"
        return "openid" + (" aws.cognito.signin.user.admin" if elevated else "")

    def get_redirect_url(self):
        """
        Get the URL to redirect to after login.

        Returns
        -------
            str: The redirect URL
        """
        frontend_url = self.get_frontend_url()
        return f"{frontend_url}"

    def get_login_url(self):
        """
        Get the login URL.

        Returns
        -------
            str: The login URL
        """
        return f"{self.get_frontend_url()}/login"

    def get_or_create_user(self, _token, userinfo):
        """
        Get or create study subject from token.

        Parameters
        ----------
            token (dict): The token from Cognito
            userinfo (dict): The user info from Cognito

        Returns
        -------
            tuple: (study_subject, error_response)
                study_subject: The StudySubject object if successful, else None
                error_response: Error response if error occurred, else None
        """
        # Extract ditti_id from userinfo
        ditti_id = userinfo.get("cognito:username")
        if not ditti_id:
            logger.warning("No cognito:username found in userinfo")
            return (
                None,
                create_error_response(
                    message_key="missing_username",
                    status_code=401,
                ),
            )

        return self._create_or_get_study_subject(ditti_id)

    def _create_or_get_study_subject(self, ditti_id):
        """
        Find an existing study subject or create a new one.

        Parameters
        ----------
            ditti_id (str): The participant's ditti ID

        Returns
        -------
            tuple: (study_subject, error_response)
                study_subject: The StudySubject object
                    if found/created successfully, else None
                error_response: Error response object
                    if error occurred, else None
        """
        try:
            # Check for existing study subject
            study_subject = StudySubject.query.filter_by(
                ditti_id=ditti_id
            ).first()

            if study_subject:
                if study_subject.is_archived:
                    logger.warning(
                        f"Attempt to login with archived account: {ditti_id}"
                    )
                    return (
                        None,
                        create_error_response(
                            message_key="account_archived",
                            status_code=403,
                        ),
                    )
                return study_subject, None

            # Create new study subject
            study_subject = StudySubject(
                created_on=datetime.now(UTC),
                ditti_id=ditti_id,
                is_archived=False,
            )
            db.session.add(study_subject)
            db.session.commit()

            return study_subject, None

        except Exception as e:
            logger.error(f"Database error with study subject: {e!s}")
            db.session.rollback()
            return (
                None,
                create_error_response(
                    message_key="database_error",
                    status_code=500,
                ),
            )

    def get_user_from_token(self, id_token):
        """
        Get ditti_id from ID token.

        Parameters
        ----------
            id_token (str): The ID token

        Returns
        -------
            tuple: (ditti_id, error_response)
                ditti_id: The ditti_id if successful, None otherwise
                error_response: Error response if error occurred, None otherwise
        """
        study_subject, error_msg = self.auth_manager.get_study_subject_from_token(
            id_token
        )

        if not study_subject:
            # Convert string error messages to proper error responses
            if isinstance(error_msg, str):
                # Handle not found
                if error_msg == AUTH_ERROR_MESSAGES["not_found"]:
                    return (
                        None,
                        create_error_response(
                            message_key="not_found",
                            status_code=404,
                        ),
                    )
                # Handle archived accounts
                elif error_msg == AUTH_ERROR_MESSAGES["account_archived"]:
                    return (
                        None,
                        create_error_response(
                            message_key="account_archived",
                            status_code=403,
                        ),
                    )
                # Handle invalid token
                elif error_msg == AUTH_ERROR_MESSAGES["invalid_token_format"]:
                    return (
                        None,
                        create_error_response(
                            message_key="invalid_token_format",
                            status_code=401,
                        ),
                    )
                # Default to generic auth failed
                else:
                    return (
                        None,
                        create_error_response(
                            message_key="auth_failed",
                            status_code=401,
                        ),
                    )
            # If error_msg is already a response, return it
            # If error_msg is None, provide a default error response
            return (
                None,
                error_msg
                or create_error_response(
                    message_key="auth_failed",
                    status_code=401,
                ),
            )

        return study_subject.ditti_id, None

    def create_login_success_response(self, ditti_id):
        """Create success response for check-login.

        Parameters
        ----------
            ditti_id: The ditti ID

        Returns
        -------
            Response: JSON response with ditti ID
        """
        return create_success_response(
            data={"dittiId": ditti_id},
            message=AUTH_ERROR_MESSAGES["login_successful"],
        )
