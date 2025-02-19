from datetime import datetime, timezone
import logging
from urllib.parse import urlencode
import boto3
from botocore.exceptions import ClientError
from flask import Blueprint, current_app, make_response, redirect, request, session, jsonify
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import requests
from sqlalchemy import select, func
from aws_portal.extensions import db
from aws_portal.models import StudySubject
from aws_portal.utils.cognito.service import get_participant_service
from aws_portal.utils.auth import auth_required

blueprint = Blueprint("participant_cognito", __name__, url_prefix="/cognito")
logger = logging.getLogger(__name__)
service = get_participant_service()


def build_cognito_url(path: str, params: dict) -> str:
    """
    Constructs a full URL for Cognito by combining the base domain, path, and query parameters.
    """
    base_url = f"https://{service.config.domain}"
    return f"{base_url}{path}?{urlencode(params)}"


@blueprint.route("/login")
def login():
    """
    Redirect users to the Cognito login page.
    """
    elevated = request.args.get("elevated") == "true"
    scope = "openid" + (" aws.cognito.signin.user.admin" if elevated else "")

    return redirect(build_cognito_url("/login", {
        "client_id": service.config.client_id,
        "response_type": "code",
        "scope": scope,
        "redirect_uri": service.config.redirect_uri,
    }))


@blueprint.route("/callback")
def cognito_callback():
    """
    Handle Cognito's authorization callback.

    Exchange the authorization code for an ID token and access token.
    Verifies the ID token, retrieves or creates the user in the database,
    stores the study subject ID in the session, and sets the tokens as secure cookies.

    Error responses:
        400 - Error fetching tokens, expired token, or invalid token.
    """
    # Retrieve authorization code from the request
    code = request.args.get("code")
    if not code:
        logger.error("Authorization code not provided.")
        return make_response({"msg": "Authorization code not provided."}, 400)

    try:
        response = requests.post(
            f"https://{service.config.domain}/oauth2/token",
            data={
                "grant_type": "authorization_code",
                "client_id": service.config.client_id,
                "client_secret": service.config.client_secret,
                "code": code,
                "redirect_uri": service.config.redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        token_data = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching tokens: {str(e)}")
        return make_response({"msg": "Error fetching tokens."}, 400)

    # Check for study subject in database or create a new one
    try:
        id_claims = service.verify_token(token_data["id_token"], "id")
        ditti_id = id_claims["cognito:username"]

        study_subject = StudySubject.query.filter_by(ditti_id=ditti_id).first()
        if study_subject:
            if study_subject.is_archived:
                logger.warning(
                    f"Attempt to login with archived account: {ditti_id}")
                return make_response({"msg": "Account is archived."}, 400)
        else:
            # If no StudySubject exists with the given ditti_id, create a new one
            study_subject = StudySubject(
                created_on=datetime.now(timezone.utc),
                ditti_id=ditti_id,
                is_archived=False  # Default value
            )
            db.session.add(study_subject)
            db.session.commit()

        # Store study subject ID in session and prepare the response
        session["study_subject_id"] = study_subject.id

        # Redirect to the front-end ParticipantDashboard
        response = make_response(redirect(current_app.config.get(
            'CORS_ORIGINS', 'http://localhost:3000')))

        # Set tokens in secure, HTTP-only cookies
        response.set_cookie(
            "id_token", token_data["id_token"], httponly=True, secure=True, samesite="None")
        response.set_cookie(
            "access_token", token_data["access_token"], httponly=True, secure=True, samesite="None")

        return response
    except Exception as e:
        logger.error(f"Auth error: {str(e)}")
        db.session.rollback()
        return make_response({"msg": "Authentication error."}, 400)


@blueprint.route("/logout")
def logout():
    """Log out the user, clear session, and clear Cognito cookies"""
    session.clear()

    logout_url = build_cognito_url("/logout", {
        "client_id": service.config.client_id,
        "logout_uri": service.config.logout_uri,
        "response_type": "code"
    })

    # TODO: Fix id_token and access_token overlap with two user pools
    response = make_response(redirect(logout_url))
    response.set_cookie("id_token", "", expires=0,
                        httponly=True, secure=True, samesite="None")
    response.set_cookie("access_token", "", expires=0,
                        httponly=True, secure=True, samesite="None")
    return response

# TODO: Some issue with this endpoint


@blueprint.route("/check-login", methods=["GET"])
def check_login():
    """Verify active login status and return ditti id"""
    id_token = request.cookies.get("id_token")
    if not id_token:
        return make_response({"msg": "Not authenticated"}, 401)

    try:
        claims = service.verify_token(id_token, "id")
        cognito_ditti_id = claims.get("cognito:username")

        if not cognito_ditti_id:
            return make_response({"msg": "cognito:username not found in token."}, 400)

        # Cognito stores ditti IDs in lowercase, so retrieve actual ditti ID from the database instead.
        stmt = select(StudySubject.ditti_id).where(
            func.lower(StudySubject.ditti_id) == cognito_ditti_id
        )
        ditti_id = db.session.execute(stmt).scalar()

        if ditti_id is None:
            logger.warning(f"Participant with cognito:username {
                           ditti_id} not found in database.")
            return make_response({"msg": f"Participant {ditti_id} not found."}, 400)

        return jsonify({
            "msg": "Login successful",
            "dittiId": ditti_id
        }), 200

    except ExpiredSignatureError as e:
        logger.warning(f"ID token expired: {str(e)}")
        return make_response({"msg": "ID Token expired."}, 401)
    except InvalidTokenError as e:
        logger.error(f"Invalid ID token: {str(e)}")
        return make_response({"msg": f"Invalid ID token."}, 401)


@blueprint.route("/register/participant", methods=["POST"])
@auth_required("Create", "Participants")
def register_participant():
    """
    Registers a study participant in AWS Cognito with a temporary password.

    This endpoint allows a research coordinator to create a new participant account
    in the AWS Cognito user pool. The research coordinator provides a Cognito username
    and a temporary password that the participant will use to log in initially.

    The temporary password will require the participant to reset their password
    upon first login.

    Request Body:
        app (int): The app where the request is being made from.
        study (int): The ID of the study the participant is being enrolled for.
        data (dict): A JSON object containing the following fields:
            - cognitoUsername (str): The unique username for the participant.
            - temporaryPassword (str): A temporary password for the participant.

    Returns:
        Response: A JSON response with one of the following:
            - 201 Created: Participant registered successfully.
            - 400 Bad Request: Missing required fields.
            - 500 Internal Server Error: AWS Cognito or other server-side errors.

    Example:
        POST /cognito/register/participant
        {
            "app": 2,
            "study": 1,
            "data": {
                "cognitoUsername": "testuser",
                "temporaryPassword": "TempPass123!"
            }
        }

    Response (201):
        {
            "msg": "Participant registered with AWS Cognito successfully."
        }
    """
    client = boto3.client("cognito-idp")
    data = request.json.get("data", {})

    try:
        cognito_username = data.get("cognitoUsername")
        temporary_password = data.get("temporaryPassword")

        if not cognito_username or not temporary_password:
            return jsonify({"error": "Missing required field."}), 400

        # Create user in Cognito
        client.admin_create_user(
            UserPoolId=current_app.config["COGNITO_PARTICIPANT_USER_POOL_ID"],
            Username=cognito_username,
            TemporaryPassword=temporary_password,
            MessageAction="SUPPRESS"
        )

        return jsonify({"msg": "Participant registered successfully."}), 200

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        logger.error(f"Cognito registration error: {error_code}")
        return jsonify({"msg": f"Cognito registration error."}), 500
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({"msg": "Registration error."}), 500
