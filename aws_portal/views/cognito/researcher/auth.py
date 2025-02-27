from datetime import datetime, timezone
import logging
from urllib.parse import urlencode
import boto3
import csv
import io
from botocore.exceptions import ClientError
from flask import Blueprint, current_app, make_response, redirect, request, session, jsonify
import secrets
from aws_portal.extensions import db, oauth
from aws_portal.models import Account
from aws_portal.utils.cognito.researcher.auth_utils import (
    init_researcher_oauth_client, validate_token_for_authenticated_route, get_account_from_email, ResearcherAuth
)
from aws_portal.utils.cognito.common import generate_code_verifier, create_code_challenge
from aws_portal.utils.cognito.researcher.decorators import researcher_auth_required

blueprint = Blueprint("researcher_cognito", __name__,
                      url_prefix="/researcher_cognito")
logger = logging.getLogger(__name__)
auth = ResearcherAuth()


def _get_cognito_logout_url():
    """Build the Cognito logout URL with appropriate parameters."""
    domain = current_app.config["COGNITO_RESEARCHER_DOMAIN"]
    client_id = current_app.config["COGNITO_RESEARCHER_CLIENT_ID"]
    logout_uri = current_app.config["COGNITO_RESEARCHER_LOGOUT_URI"]

    params = {
        "client_id": client_id,
        "logout_uri": logout_uri,
        "response_type": "code"
    }
    return f"https://{domain}/logout?{urlencode(params)}"


def _get_account_from_token(id_token):
    """
    Extract account from a validated ID token.

    Validates the token and ensures the account exists and is not archived.

    Args:
        id_token (str): The ID token to validate

    Returns:
        tuple: (account, error_response)
            account: The researcher's Account object if valid, None otherwise
            error_response: Error response object if error occurred, None otherwise
    """
    try:
        # Validate token
        success, userinfo = validate_token_for_authenticated_route(id_token)

        if not success:
            return None, make_response({"msg": "Authentication failed"}, 401)

        # Extract email
        email = userinfo.get("email")
        if not email:
            logger.warning("No email found in ID token")
            return None, make_response({"msg": "Authentication failed"}, 401)

        # Check if an account with this email exists, regardless of archived status
        any_account = Account.query.filter_by(email=email).first()

        # If account exists but is archived
        if any_account and any_account.is_archived:
            logger.warning(f"Attempt to access with archived account: {email}")
            return None, make_response({"msg": "Account unavailable. Please contact support."}, 403)

        # Get active account from database (not archived)
        account = auth.get_account_from_email(email)
        if not account:
            if any_account:  # This shouldn't happen given the check above, but just for defensive coding
                logger.warning(
                    f"Attempt to access with archived account: {email}")
                return None, make_response({"msg": "Account unavailable. Please contact support."}, 403)
            else:
                logger.warning(f"No account found for email: {email}")
                return None, make_response({"msg": "Invalid credentials"}, 401)

        return account, None

    except Exception as e:
        logger.error(f"Error retrieving account from token: {str(e)}")
        return None, make_response({"msg": "System error. Please try again later."}, 500)


@blueprint.route("/login")
def login():
    """
    Redirect researchers to the Cognito login page.

    This endpoint:
    1. Generates a secure nonce for ID token validation
    2. Generates a secure state parameter for CSRF protection
    3. Generates PKCE code_verifier and code_challenge for authorization code security
    4. Redirects to the Cognito authorization endpoint with all security parameters

    Returns:
        Redirect to Cognito login page
    """
    init_researcher_oauth_client()

    # Generate and store nonce for ID token validation
    nonce = secrets.token_urlsafe(32)
    session["cognito_nonce"] = nonce
    session["cognito_nonce_generated"] = int(
        datetime.now(timezone.utc).timestamp())

    # Generate and store state for CSRF protection
    state = secrets.token_urlsafe(32)
    session["cognito_state"] = state

    # Generate and store PKCE code_verifier and code_challenge
    code_verifier = generate_code_verifier()
    code_challenge = create_code_challenge(code_verifier)
    session["cognito_code_verifier"] = code_verifier

    # Redirect to Cognito authorization endpoint with all security parameters
    return oauth.researcher_oidc.authorize_redirect(
        current_app.config["COGNITO_RESEARCHER_REDIRECT_URI"],
        scope="openid email profile",
        nonce=nonce,
        state=state,
        code_challenge=code_challenge,
        code_challenge_method="S256"
    )


@blueprint.route("/callback")
def cognito_callback():
    """
    Handle Cognito's authorization callback for researchers.

    This endpoint:
    1. Validates the state parameter to prevent CSRF attacks
    2. Provides the code_verifier for PKCE validation
    3. Exchanges the authorization code for tokens
    4. Validates the ID token with the stored nonce
    5. Retrieves the researcher in the database
    6. Sets secure cookies with the tokens
    7. Redirects to the frontend application

    Returns:
        Redirect to frontend with tokens set in cookies, or
        400 Bad Request on authentication errors
        403 Forbidden if account is archived
    """
    init_researcher_oauth_client()

    try:
        # Validate state parameter to prevent CSRF attacks
        state = session.pop("cognito_state", None)
        state_in_request = request.args.get("state")
        if not state or state != state_in_request:
            logger.warning("Invalid state parameter in callback")
            return make_response({"msg": "Invalid authentication request"}, 401)

        # Get code_verifier for PKCE
        code_verifier = session.pop("cognito_code_verifier", None)
        if not code_verifier:
            logger.warning("Missing code_verifier in session")
            return make_response({"msg": "Authentication request rejected"}, 401)

        # Validate nonce
        nonce = session.pop("cognito_nonce", None)
        nonce_generated = session.pop("cognito_nonce_generated", 0)

        # Check if nonce is valid
        nonce_age = int(datetime.now(
            timezone.utc).timestamp()) - nonce_generated
        if not nonce or nonce_age > 300:  # 5 minutes expiration
            logger.warning(f"Invalid or expired nonce. Age: {nonce_age}s")
            return make_response({"msg": "Authentication session expired"}, 401)

        # Exchange code for tokens with PKCE code_verifier
        token = oauth.researcher_oidc.authorize_access_token(
            code_verifier=code_verifier)

        # Parse ID token with nonce validation
        try:
            userinfo = oauth.researcher_oidc.parse_id_token(token, nonce=nonce)
        except Exception as e:
            logger.error(f"Failed to validate ID token: {str(e)}")
            return make_response({"msg": "Authentication failed"}, 401)

        # Extract account using ID token (which includes validation and archive checks)
        account, error = _get_account_from_token(token["id_token"])
        if error:
            return error

        # Set session data
        session["account_id"] = account.id
        session["user"] = userinfo

        # Create response with redirect to frontend
        frontend_url = current_app.config.get(
            "CORS_ORIGINS", "http://localhost:3000")
        admin_url = f"{frontend_url}/coordinator"
        response = make_response(redirect(admin_url))

        # Set tokens in secure cookies
        response.set_cookie(
            "id_token", token["id_token"],
            httponly=True, secure=True, samesite="None"
        )
        response.set_cookie(
            "access_token", token["access_token"],
            httponly=True, secure=True, samesite="None"
        )
        if "refresh_token" in token:
            response.set_cookie(
                "refresh_token", token["refresh_token"],
                httponly=True, secure=True, samesite="None"
            )

        return response

    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        db.session.rollback()
        return make_response({"msg": "Authentication failed"}, 400)


@blueprint.route("/logout")
def logout():
    """
    Log out the researcher from the application and Cognito.

    This endpoint:
    1. Clears the session data
    2. Builds a logout URL for Cognito
    3. Clears authentication cookies
    4. Redirects to Cognito logout

    Returns:
        Redirect to Cognito logout URL with cookies cleared
    """
    init_researcher_oauth_client()

    # Clear session
    session.clear()

    # Create response with redirect to Cognito logout
    response = make_response(redirect(_get_cognito_logout_url()))

    # Clear all auth cookies
    for cookie_name in ["id_token", "access_token", "refresh_token"]:
        response.set_cookie(
            cookie_name, "", expires=0,
            httponly=True, secure=True, samesite="None"
        )

    return response


@blueprint.route("/check-login", methods=["GET"])
def check_login():
    """
    Verify active login status and return the researcher's info.

    This endpoint:
    1. Checks if the ID token exists in cookies
    2. Validates the token and extracts the email
    3. Returns the account info on success

    Returns:
        200 OK with account info on success
        401 Unauthorized if not authenticated or token invalid
        403 Forbidden if account is archived
        404 Not Found if account doesn't exist
    """
    init_researcher_oauth_client()

    # Check for ID token
    id_token = request.cookies.get("id_token")
    if not id_token:
        return make_response({"msg": "Authentication required"}, 401)

    # Get email from token
    account, error = _get_account_from_token(id_token)
    if error:
        return error

    # Return success with account info
    return jsonify({
        "msg": "Login successful",
        "email": account.email,
        "firstName": account.first_name,
        "lastName": account.last_name,
        "accountId": account.id
    }), 200


@blueprint.route("/upload-researchers", methods=["POST"])
@researcher_auth_required("Create", "Accounts")
def upload_researchers(account):
    """
    Upload researchers to Cognito via CSV.

    This endpoint:
    1. Accepts a CSV file with researcher information
    2. Creates the users in the Cognito user pool
    3. Returns a summary of the operation

    CSV format:
    email,given_name,family_name,phone_number

    Request Body:
        file: The CSV file containing researcher information

    Returns:
        200 OK with summary of operation on success
        400 Bad Request if file is missing or invalid
        500 Internal Server Error on AWS errors
    """
    client = boto3.client("cognito-idp",
                          region_name=current_app.config["COGNITO_RESEARCHER_REGION"])

    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({"msg": "Missing required information"}), 400

    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({"msg": "Missing required information"}), 400

    # Process CSV file
    try:
        # Read CSV file
        csv_content = file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))

        # Check for required fields
        required_fields = ['email', 'given_name', 'family_name']
        for field in required_fields:
            if field not in csv_reader.fieldnames:
                return jsonify({"msg": "File format invalid. Missing required fields."}), 400

        # Track results
        results = {
            "success": 0,
            "failed": 0,
            "errors": []
        }

        # Process each row
        for row in csv_reader:
            try:
                # Extract data
                email = row['email'].strip()
                given_name = row['given_name'].strip()
                family_name = row['family_name'].strip()
                phone_number = row.get('phone_number', '').strip()

                # Validate required fields
                if not email or not given_name or not family_name:
                    results["failed"] += 1
                    results["errors"].append(
                        f"Row with email {email}: Missing required field")
                    continue

                # Temporary password generation
                temp_password = f"Temp{secrets.token_hex(4)}!"

                # Create user attributes
                user_attributes = [
                    {'Name': 'email', 'Value': email},
                    {'Name': 'email_verified', 'Value': 'true'},
                    {'Name': 'given_name', 'Value': given_name},
                    {'Name': 'family_name', 'Value': family_name},
                ]

                # Add phone if provided
                if phone_number:
                    user_attributes.append(
                        {'Name': 'phone_number', 'Value': phone_number})

                # Create user in Cognito
                user_pool_id = current_app.config["COGNITO_RESEARCHER_USER_POOL_ID"]
                client.admin_create_user(
                    UserPoolId=user_pool_id,
                    Username=email,
                    UserAttributes=user_attributes,
                    TemporaryPassword=temp_password,
                    MessageAction="SUPPRESS"
                )

                results["success"] += 1

            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                error_message = e.response["Error"]["Message"]
                results["failed"] += 1
                results["errors"].append(
                    f"Error with {email}: {error_code} - {error_message}")
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Error with {email}: {str(e)}")

        return jsonify({
            "msg": "File processed successfully",
            "summary": results
        }), 200

    except Exception as e:
        logger.error(f"CSV processing error: {str(e)}")
        return jsonify({"msg": "File processing failed"}), 500
