import logging
from sqlalchemy import func
from aws_portal.extensions import oauth
from aws_portal.models import StudySubject
from aws_portal.auth.providers.cognito import CognitoAuthBase

logger = logging.getLogger(__name__)


class ParticipantAuth(CognitoAuthBase):
    """Specialized authentication class for participants."""

    def __init__(self):
        super().__init__("participant")

    def get_user_from_claims(self, claims):
        """Extract user information from ID token claims."""
        return {
            "id": claims.get("cognito:username"),
            "email": claims.get("email"),
            "name": claims.get("name", "")
        }

    def get_study_subject_from_ditti_id(self, ditti_id, include_archived=False):
        """
        Get a study subject by ditti_id.

        Args:
            ditti_id (str): The ditti ID to search for
            include_archived (bool, optional): Whether to include archived study subjects

        Returns:
            StudySubject or None: The matching study subject or None if not found
        """
        if not ditti_id:
            return None

        query = StudySubject.query.filter(
            func.lower(StudySubject.ditti_id) == ditti_id.lower()
        )

        if not include_archived:
            query = query.filter(StudySubject.is_archived == False)

        return query.first()

    def get_study_subject_from_token(self, id_token, include_archived=False):
        """
        Get a study subject from an ID token.

        Args:
            id_token (str): The ID token
            include_archived (bool, optional): Whether to include archived study subjects

        Returns:
            tuple: (study_subject, error_message)
                study_subject: The StudySubject object if successful, None otherwise
                error_message: Error message if study_subject is None, None otherwise
        """
        success, claims = self.validate_token_for_authenticated_route(id_token)

        if not success:
            return None, claims

        ditti_id = claims.get("cognito:username")
        if not ditti_id:
            logger.warning("No cognito:username found in token claims")
            return None, "Invalid token"

        study_subject = self.get_study_subject_from_ditti_id(
            ditti_id, include_archived)

        if not study_subject:
            logger.warning(f"No study subject found for ID: {ditti_id}")
            return None, "User profile not found"

        if study_subject.is_archived:
            logger.warning(
                f"Attempt to access with archived study subject: {ditti_id}")
            return None, "Account unavailable. Please contact support."

        return study_subject, None


def init_participant_oauth_client():
    """
    Initialize OAuth client for Cognito if not already configured.

    This configures the OAuth client with all necessary endpoints and credentials
    for interacting with AWS Cognito.
    """
    from flask import current_app

    if "oidc" not in oauth._clients:
        region = current_app.config["COGNITO_PARTICIPANT_REGION"]
        user_pool_id = current_app.config["COGNITO_PARTICIPANT_USER_POOL_ID"]
        domain = current_app.config["COGNITO_PARTICIPANT_DOMAIN"]
        client_id = current_app.config["COGNITO_PARTICIPANT_CLIENT_ID"]
        client_secret = current_app.config["COGNITO_PARTICIPANT_CLIENT_SECRET"]

        oauth.register(
            name="oidc",
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url=f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/openid-configuration",
            client_kwargs={"scope": "openid aws.cognito.signin.user.admin"},
            authorize_url=f"https://{domain}/oauth2/authorize",
            access_token_url=f"https://{domain}/oauth2/token",
            userinfo_endpoint=f"https://{domain}/oauth2/userInfo",
            jwks_uri=f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
        )
