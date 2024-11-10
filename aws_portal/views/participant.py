import logging
from flask import Blueprint, jsonify, make_response, request
import jwt
import boto3
from aws_portal.extensions import db
from aws_portal.models import Api, StudySubject, JoinStudySubjectApi
from aws_portal.utils.cognito import cognito_auth_required
from aws_portal.utils.serialization import serialize_participant
from aws_portal.extensions import tm

blueprint = Blueprint('participant', __name__, url_prefix='/participant')
logger = logging.getLogger(__name__)


@blueprint.route('', methods=['GET'])
@cognito_auth_required
def get_participant():
    """
    Endpoint to retrieve a participant's data.

    Returns:
        JSON response containing serialized participant data or an error message.
    """
    try:
        # Get ID token from cookies
        id_token = request.cookies.get('id_token')
        if not id_token:
            return make_response({"msg": "Missing ID token."}, 401)

        # Decode ID token without verification to extract email
        claims = jwt.decode(id_token, options={"verify_signature": False})
        email = claims.get('email')
        if not email:
            return make_response({"msg": "Email not found in token."}, 400)

        # Retrieve the StudySubject
        study_subject = StudySubject.query.filter_by(
            email=email, is_archived=False).first()
        if not study_subject:
            return make_response({"msg": "User not found or is archived."}, 404)

        # Serialize the StudySubject data to only include required fields
        participant_data = serialize_participant(study_subject)

        return jsonify(participant_data)

    except Exception as e:
        logger.error(f"Error retrieving participant data: {str(e)}")
        return make_response({"msg": "Error retrieving participant data."}, 500)


@blueprint.route('/api/<string:api_name>', methods=['DELETE'])
@cognito_auth_required
def revoke_api_access(api_name):
    """
    Endpoint to revoke a participant's access to a specified API.
    Deletes tokens associated with the API from Secrets Manager,
    removes API access, and commits changes to the database.

    Args:
        api_name (str): Name of the API to revoke access for.

    Returns:
        JSON response indicating success or failure of API access revocation.
    """
    try:
        # Get tokens and claims
        id_token = request.cookies.get('id_token')

        if not id_token:
            return make_response({"msg": "Missing authentication tokens."}, 401)

        # Decode ID token to get claims
        claims = jwt.decode(id_token, options={"verify_signature": False})
        email = claims.get('email')
        if not email:
            return make_response({"msg": "Email not found in token"}, 400)

        study_subject = StudySubject.query.filter_by(
            email=email, is_archived=False).first()
        if not study_subject:
            return make_response({"msg": "User not found"}, 404)

        # Get the API by name
        api = Api.query.filter_by(name=api_name, is_archived=False).first()
        if not api:
            return make_response({"msg": "API not found"}, 404)

        # Find the JoinStudySubjectApi entry
        join_api = JoinStudySubjectApi.query.get((study_subject.id, api.id))
        if not join_api:
            return make_response({"msg": "API access not found"}, 404)

        # Delete tokens from Secrets Manager
        try:
            tm.delete_api_tokens(
                api_name=api_name, study_subject_id=study_subject.id)
        except KeyError:
            logger.warning(f"Tokens for API '{api_name}' and StudySubject ID {
                study_subject.id} not found.")

        # Remove API access
        db.session.delete(join_api)
        db.session.commit()

        return jsonify({"msg": "API access revoked successfully"})

    except Exception as e:
        logger.error(f"Error revoking API access: {str(e)}")
        db.session.rollback()
        return make_response({"msg": "Error revoking API access"}, 500)


@blueprint.route('', methods=['DELETE'])
@cognito_auth_required
def delete_participant():
    """
    Endpoint to delete a participant's account and all associated API data.
    Deletes API tokens and data, archives the StudySubject in the database,
    and removes the user from AWS Cognito.

    Returns:
        JSON response confirming account deletion or an error message.
    """
    try:
        # Get tokens from cookies
        id_token = request.cookies.get('id_token')
        access_token = request.cookies.get('access_token')

        if not id_token or not access_token:
            return make_response({"msg": "Missing authentication tokens."}, 401)

        # Decode ID token to get claims
        claims = jwt.decode(id_token, options={"verify_signature": False})
        email = claims.get('email')
        if not email:
            return make_response({"msg": "Email not found in token."}, 400)

        # Retrieve the StudySubject
        study_subject = StudySubject.query.filter_by(
            email=email, is_archived=False).first()
        if not study_subject:
            return make_response({"msg": "User not found or already archived."}, 404)
        study_subject_id = study_subject.id

        # TODO: Delete API data (DIT-16)

        # Delete associated JoinStudySubjectApi entries
        for api_entry in list(study_subject.apis):
            api_name = api_entry.api.name

            # Delete tokens from Secrets Manager
            try:
                tm.delete_api_tokens(
                    api_name=api_name, study_subject_id=study_subject_id)
            except KeyError:
                logger.warning(f"Tokens for API '{api_name}' and StudySubject ID {
                               study_subject_id} not found.")
            except Exception as e:
                logger.error(f"Error deleting tokens for API '{
                             api_name}': {str(e)}")
                return make_response({"msg": "Error deleting API tokens."}, 500)

            # Remove API access
            db.session.delete(api_entry)

        # Archive the StudySubject
        study_subject.is_archived = True

        # Commit the changes
        db.session.commit()

        # Delete user from AWS Cognito
        client = boto3.client('cognito-idp')
        try:
            # Requires aws.cognito.signin.user.admin OpenID Connect scope
            client.delete_user(
                AccessToken=access_token
            )
        except client.exceptions.NotAuthorizedException:
            logger.error("Not authorized to delete user in Cognito.")
            return make_response({"msg": "Not authorized to delete user."}, 403)
        except Exception as e:
            logger.error(f"Error deleting user from Cognito: {str(e)}")
            return make_response({"msg": "Error deleting user from Cognito."}, 500)

        # Clear cookies
        response = make_response({"msg": "Account deleted successfully."})
        response.delete_cookie('id_token')
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

    except Exception as e:
        logger.error(f"Error deleting participant: {str(e)}")
        db.session.rollback()
        return make_response({"msg": "Error deleting account."}, 500)
