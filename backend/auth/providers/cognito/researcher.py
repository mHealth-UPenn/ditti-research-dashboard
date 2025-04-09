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
from aws_portal.extensions import oauth
from aws_portal.models import Account
from aws_portal.auth.providers.cognito.base import CognitoAuthBase

logger = logging.getLogger(__name__)


class ResearcherAuth(CognitoAuthBase):
    """Specialized authentication class for researchers."""

    def __init__(self):
        super().__init__("researcher")

    def get_account_from_email(self, email, include_archived=False):
        """
        Get Account object from email address.

        Args:
            email (str): The email address to search for
            include_archived (bool, optional): Whether to include archived accounts

        Returns:
            Account or None: The matching account or None if not found
        """
        if not email:
            return None

        query = Account.query.filter_by(email=email)

        if not include_archived:
            query = query.filter_by(is_archived=False)

        return query.first()

    def get_account_from_token(self, id_token, include_archived=False):
        """
        Get an account from an ID token.

        Args:
            id_token (str): The ID token
            include_archived (bool, optional): Whether to include archived accounts

        Returns:
            tuple: (account, error_message)
                account: The Account object if successful, None otherwise
                error_message: Error message if account is None, None otherwise
        """
        success, claims = self.validate_token_for_authenticated_route(id_token)

        if not success:
            return None, claims

        email = claims.get("email")
        if not email:
            logger.warning("No email found in token claims")
            return None, "Invalid token"

        # First check if account exists regardless of archived status
        any_account = self.get_account_from_email(email, include_archived=True)

        if any_account and any_account.is_archived and not include_archived:
            logger.warning(f"Attempt to access with archived account: {email}")
            return None, "Account unavailable. Please contact support."

        account = self.get_account_from_email(email, include_archived)

        if not account:
            logger.warning(f"No active account found for email: {email}")
            return None, "Invalid credentials"

        return account, None


def init_researcher_oauth_client():
    """
    Initialize OAuth client for Researcher Cognito if not already configured.

    This configures the OAuth client with all necessary endpoints and credentials
    for interacting with AWS Cognito.
    """
    from flask import current_app

    if "researcher_oidc" not in oauth._clients:
        region = current_app.config["COGNITO_RESEARCHER_REGION"]
        user_pool_id = current_app.config["COGNITO_RESEARCHER_USER_POOL_ID"]
        domain = current_app.config["COGNITO_RESEARCHER_DOMAIN"]
        client_id = current_app.config["COGNITO_RESEARCHER_CLIENT_ID"]
        client_secret = current_app.config["COGNITO_RESEARCHER_CLIENT_SECRET"]

        oauth.register(
            name="researcher_oidc",
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url=f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/openid-configuration",
            client_kwargs={
                "scope": "openid email profile aws.cognito.signin.user.admin"},
            authorize_url=f"https://{domain}/oauth2/authorize",
            access_token_url=f"https://{domain}/oauth2/token",
            userinfo_endpoint=f"https://{domain}/oauth2/userInfo",
            jwks_uri=f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
        )
