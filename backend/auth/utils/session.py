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
import secrets
from datetime import datetime, timezone

from flask import session

from backend.auth.utils.tokens import (
    create_code_challenge,
    generate_code_verifier,
)

logger = logging.getLogger(__name__)


class AuthFlowSession:
    """Class to encapsulate authentication flow session management."""

    @staticmethod
    def generate_and_store_security_params():
        """Generate and store security parameters for OAuth flow.

        Returns:
            dict: Dictionary containing the generated security parameters
        """
        # Generate and store nonce for ID token validation
        nonce = secrets.token_urlsafe(32)
        session["cognito_nonce"] = nonce
        session["cognito_nonce_generated"] = int(
            datetime.now(timezone.utc).timestamp()
        )

        # Generate and store state for CSRF protection
        state = secrets.token_urlsafe(32)
        session["cognito_state"] = state

        # Generate and store PKCE code_verifier and code_challenge
        code_verifier = generate_code_verifier()
        code_challenge = create_code_challenge(code_verifier)
        session["cognito_code_verifier"] = code_verifier

        # Return all security parameters
        return {
            "nonce": nonce,
            "state": state,
            "code_verifier": code_verifier,
            "code_challenge": code_challenge,
        }

    @staticmethod
    def validate_state(request_state):
        """Validate the state parameter from callback.

        Args:
            request_state (str): The state parameter from the request

        Returns:
            bool: True if state is valid, False otherwise
        """
        state = session.pop("cognito_state", None)
        return state and state == request_state

    @staticmethod
    def get_code_verifier():
        """Get and remove the code verifier from the session.

        Returns:
            str: The code verifier or None if not found
        """
        return session.pop("cognito_code_verifier", None)

    @staticmethod
    def validate_nonce():
        """Validate the stored nonce.

        Returns:
            tuple: (is_valid, nonce)
                is_valid (bool): Whether the nonce is valid
                nonce (str): The nonce value if valid, None otherwise
        """
        nonce = session.pop("cognito_nonce", None)
        nonce_generated = session.pop("cognito_nonce_generated", 0)

        # Check if nonce is valid
        nonce_age = (
            int(datetime.now(timezone.utc).timestamp()) - nonce_generated
        )
        if not nonce or nonce_age > 300:  # 5 minutes expiration
            logger.warning(f"Invalid or expired nonce. Age: {nonce_age}s")
            return False, None

        return True, nonce

    @staticmethod
    def clear():
        """Clear all authentication-related session data."""
        session.pop("cognito_nonce", None)
        session.pop("cognito_nonce_generated", None)
        session.pop("cognito_state", None)
        session.pop("cognito_code_verifier", None)

    @staticmethod
    def set_user_data(user_type, user_id, userinfo):
        """Set user session data.

        Args:
            user_type (str): "participant" or "researcher"
            user_id: ID of the user (either account_id or study_subject_id)
            userinfo (dict): User info from Cognito
        """
        if user_type == "participant":
            session["study_subject_id"] = user_id
        else:
            session["account_id"] = user_id

        session["user"] = userinfo
        session["user_type"] = user_type
