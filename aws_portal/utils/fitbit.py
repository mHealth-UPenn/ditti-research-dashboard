import secrets
import hashlib
import base64
from aws_portal.utils.secrets_manager import secrets_manager
import logging
import requests
from flask import current_app
from aws_portal.extensions import db

logger = logging.getLogger(__name__)


def generate_pkce_pair():
    code_verifier = secrets.token_urlsafe(64)[:128]
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip("=")
    return code_verifier, code_challenge


def refresh_fitbit_token(join_entry):
    try:
        refresh_token = secrets_manager.get_secret(join_entry.refresh_key_uuid)
        client_credentials = f"{current_app.config['FITBIT_CLIENT_ID']}:{
            current_app.config['FITBIT_CLIENT_SECRET']}"
        b64_client_credentials = base64.b64encode(
            client_credentials.encode()).decode()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {b64_client_credentials}"
        }
        data = {
            "client_id": current_app.config["FITBIT_CLIENT_ID"],
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        token_url = "https://api.fitbit.com/oauth2/token"
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()  # This will raise an HTTPError for bad responses
        token_data = response.json()

        if "errors" in token_data:
            logger.error(f"Error refreshing tokens: {token_data["errors"]}")
            raise Exception("Token refresh failed.")

        # Update tokens in Secrets Manager
        secrets_manager.store_secret(
            join_entry.access_key_uuid, token_data["access_token"])
        secrets_manager.store_secret(
            join_entry.refresh_key_uuid, token_data["refresh_token"])

        # Update scope
        scope = token_data.get("scope", "").strip()
        join_entry.scope = scope.split()
        db.session.commit()

        logger.info("Fitbit tokens refreshed successfully.")
    except Exception as e:
        logger.error(f"Failed to refresh Fitbit tokens: {str(e)}")
        raise
