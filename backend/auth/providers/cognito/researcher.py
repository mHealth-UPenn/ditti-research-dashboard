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

from backend.auth.providers.cognito.base import CognitoAuthBase
from backend.auth.providers.cognito.constants import AUTH_ERROR_MESSAGES
from backend.extensions import oauth
from backend.models import Account

logger = logging.getLogger(__name__)


class ResearcherAuth(CognitoAuthBase):
    """Specialized authentication class for researchers."""

    def __init__(self):
        super().__init__("researcher")
        logger.debug("Initialized ResearcherAuth class")

    def get_account_from_email(self, email, include_archived=False):
        """
        Get Account object from email address.

        Parameters
        ----------
            email (str): The email address to search for
            include_archived (bool, optional): Include archived accounts?

        Returns
        -------
            Account or None: The matching account or None if not found
        """
        logger.debug(
            f"Getting researcher account from email: {email}, include_archived: {include_archived}"
        )

        if not email:
            logger.debug("No email provided for researcher account lookup")
            return None

        query = Account.query.filter_by(email=email)

        if not include_archived:
            query = query.filter_by(is_archived=False)
            logger.debug("Filtering out archived accounts")

        account = query.first()
        if account:
            logger.debug(
                f"Found researcher account: {account.id} (archived: {account.is_archived})"
            )
        else:
            logger.debug(f"No researcher account found for email: {email}")

        return account

    def get_account_from_token(self, id_token, include_archived=False):
        """
        Get an account from an ID token.

        Parameters
        ----------
            id_token (str): The ID token
            include_archived (bool, optional): Include archived accounts?

        Returns
        -------
            tuple: (account, error_message)
                account: The Account object if successful, None otherwise
                error_message: Error message if account is None, None otherwise
        """
        logger.debug(
            f"Getting researcher account from token, include_archived: {include_archived}"
        )

        success, claims = self.validate_token_for_authenticated_route(id_token)

        if not success:
            logger.warning(f"Token validation failed for researcher: {claims}")
            return None, claims  # claims here is the error message

        logger.debug(
            f"Token validation successful for researcher, claims: {claims}"
        )

        email = claims.get("email")
        if not email:
            logger.warning("No email found in researcher token claims")
            return None, AUTH_ERROR_MESSAGES["invalid_token_format"]

        logger.debug(f"Extracted email from researcher token: {email}")

        # First check if account exists regardless of archived status
        any_account = self.get_account_from_email(email, include_archived=True)

        if any_account and any_account.is_archived and not include_archived:
            logger.warning(
                f"Attempt to access with archived researcher account: {email}"
            )
            return (
                None,
                AUTH_ERROR_MESSAGES["account_archived"],
            )

        account = self.get_account_from_email(email, include_archived)

        if not account:
            logger.warning(
                f"No active researcher account found for email: {email}"
            )
            return None, AUTH_ERROR_MESSAGES["not_found"]

        logger.debug(f"Successfully retrieved researcher account: {account.id}")
        return account, None


def init_researcher_oauth_client():
    """
    Initialize OAuth client for Researcher Cognito if not already configured.

    This configures the OAuth client with all necessary endpoints and credentials
    for interacting with AWS Cognito.
    """
    from flask import current_app

    logger.debug("Initializing researcher OAuth client")

    if "researcher_oidc" not in oauth._clients:
        logger.debug(
            "Researcher OAuth client not found, creating new configuration"
        )

        region = current_app.config["COGNITO_RESEARCHER_REGION"]
        user_pool_id = current_app.config["COGNITO_RESEARCHER_USER_POOL_ID"]
        domain = current_app.config["COGNITO_RESEARCHER_DOMAIN"]
        client_id = current_app.config["COGNITO_RESEARCHER_CLIENT_ID"]
        client_secret = current_app.config["COGNITO_RESEARCHER_CLIENT_SECRET"]

        logger.debug(
            f"Researcher OAuth configuration - Region: {region}, User Pool: {user_pool_id}, Domain: {domain}"
        )

        oauth.register(
            name="researcher_oidc",
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url=f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/openid-configuration",
            client_kwargs={
                "scope": "openid email profile aws.cognito.signin.user.admin"
            },
            authorize_url=f"https://{domain}/oauth2/authorize",
            access_token_url=f"https://{domain}/oauth2/token",
            userinfo_endpoint=f"https://{domain}/oauth2/userInfo",
            jwks_uri=f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json",
        )

        logger.debug("Researcher OAuth client registered successfully")
    else:
        logger.debug("Researcher OAuth client already exists")
