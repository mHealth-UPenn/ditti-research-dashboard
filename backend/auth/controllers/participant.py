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
from backend.auth.utils.responses import (
    create_error_response,
    create_success_response,
)
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
        """Get the OAuth scope.

        Returns
        -------
            str: The OAuth scope
        """
        # Check if elevated scope is requested
        elevated = request.args.get("elevated") == "true"
        return "openid" + (" aws.cognito.signin.user.admin" if elevated else "")

    def get_login_url(self):
        """Get the login URL.

        Returns
        -------
            str: The login URL
        """
        return f"{self.get_frontend_url()}/login"

    def get_or_create_user(self, _token, userinfo):
        """Get or create study subject from token.

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
            return None, create_error_response(
                AUTH_ERROR_MESSAGES["auth_failed"],
                status_code=401,
                error_code="MISSING_USERNAME",
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
                    return None, create_error_response(
                        AUTH_ERROR_MESSAGES["account_archived"],
                        status_code=403,
                        error_code="ACCOUNT_ARCHIVED",
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
            return None, create_error_response(
                AUTH_ERROR_MESSAGES["system_error"],
                status_code=500,
                error_code="DATABASE_ERROR",
            )

    def get_user_from_token(self, id_token):
        """Get ditti_id from token.

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
                if error_msg == "User profile not found":
                    return None, create_error_response(
                        AUTH_ERROR_MESSAGES["not_found"],
                        status_code=404,
                        error_code="USER_NOT_FOUND",
                    )
                elif error_msg == "Account unavailable. Please contact support.":
                    return None, create_error_response(
                        AUTH_ERROR_MESSAGES["account_archived"],
                        status_code=403,
                        error_code="ACCOUNT_ARCHIVED",
                    )
                else:
                    return None, create_error_response(
                        AUTH_ERROR_MESSAGES["auth_failed"],
                        status_code=401,
                        error_code="AUTH_FAILED",
                    )
            # If error_msg is already a response, return it
            return None, error_msg

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
