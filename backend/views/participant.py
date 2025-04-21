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

import boto3
from flask import Blueprint, current_app, jsonify, make_response, request
from sqlalchemy.exc import SQLAlchemyError

from backend.auth.decorators import (
    participant_auth_required,
    researcher_auth_required,
)
from backend.extensions import db, tm
from backend.models import (
    Api,
    JoinStudySubjectApi,
    JoinStudySubjectStudy,
    StudySubject,
)
from backend.utils.serialization import serialize_participant

blueprint = Blueprint("participant", __name__, url_prefix="/participant")
logger = logging.getLogger(__name__)


@blueprint.route("", methods=["GET"])
@participant_auth_required
def get_participant(ditti_id: str):
    """
    Endpoint to retrieve a participant's data.

    Args:
        ditti_id (str): The unique ID of the study subject, provided by the decorator.

    Returns:
        JSON response containing serialized participant data or an error message.
    """
    try:
        # Retrieve the StudySubject by ditti_id
        study_subject = StudySubject.query.filter_by(
            ditti_id=ditti_id, is_archived=False
        ).first()
        if not study_subject:
            logger.info(
                f"StudySubject with ditti_id {ditti_id} not found or is archived."
            )
            return make_response({"msg": "User not found or is archived."}, 404)

        # Serialize the StudySubject data to include required fields
        try:
            participant_data = serialize_participant(study_subject)
        except Exception as serialize_err:
            logger.error(
                f"Error serializing participant data for ditti_id {ditti_id}: {
                    str(serialize_err)
                }"
            )
            return make_response(
                {"msg": "Error processing participant data."}, 500
            )

        return jsonify(participant_data)

    except SQLAlchemyError as db_err:
        logger.error(
            f"Database error retrieving participant data for ditti_id {
                ditti_id
            }: {str(db_err)}"
        )
        return make_response(
            {"msg": "Database error retrieving participant data."}, 500
        )
    except Exception as e:
        logger.error(
            f"Unhandled error retrieving participant data for ditti_id {
                ditti_id
            }: {str(e)}"
        )
        return make_response({"msg": "Unexpected server error."}, 500)


@blueprint.route("/study/<int:study_id>/consent", methods=["PATCH"])
@participant_auth_required
def update_consent(study_id: int, ditti_id: str):
    """
    Endpoint to update a participant's consent status for a specific study.

    Args:
        study_id (int): The ID of the study.
        ditti_id (str): The unique ID of the study subject, provided by the decorator.

    Request Body:
        {
            "didConsent": true  // or false
        }

    Returns:
        JSON response indicating success or failure of the consent update.
    """
    try:
        # Parse JSON request body
        data = request.get_json()
        if not data or "didConsent" not in data:
            logger.warning(
                f"Missing 'didConsent' in request body for ditti_id {
                    ditti_id
                }, study_id {study_id}."
            )
            return make_response({"msg": "Field 'didConsent' is required."}, 400)

        did_consent = data["didConsent"]
        if not isinstance(did_consent, bool):
            logger.warning(
                f"Invalid 'did_consent' type for ditti_id {ditti_id}, study_id {
                    study_id
                }. Expected boolean."
            )
            return make_response({"msg": "'didConsent' must be a boolean."}, 400)

        # Retrieve the StudySubject by ditti_id
        study_subject = StudySubject.query.filter_by(
            ditti_id=ditti_id, is_archived=False
        ).first()
        if not study_subject:
            logger.info(
                f"StudySubject with ditti_id {ditti_id} not found or is archived."
            )
            return make_response({"msg": "User not found or is archived."}, 404)

        # Retrieve the JoinStudySubjectStudy entry
        join_entry = JoinStudySubjectStudy.query.filter_by(
            study_subject_id=study_subject.id, study_id=study_id
        ).first()

        if not join_entry:
            logger.info(
                f"JoinStudySubjectStudy entry not found for ditti_id {
                    ditti_id
                }, study_id {study_id}."
            )
            return make_response({"msg": "Study enrollment not found."}, 404)

        # Update the did_consent field
        join_entry.did_consent = did_consent
        db.session.commit()

        logger.info(
            f"Updated did_consent to {did_consent} for ditti_id {
                ditti_id
            }, study_id {study_id}."
        )
        return jsonify({"msg": "Consent status updated successfully."})

    except SQLAlchemyError as db_err:
        logger.error(
            f"Database error updating consent for ditti_id {ditti_id}, study_id {
                study_id
            }: {str(db_err)}"
        )
        db.session.rollback()
        return make_response(
            {"msg": "Database error updating consent status."}, 500
        )
    except Exception as e:
        logger.error(
            f"Unhandled error updating consent for ditti_id {ditti_id}, study_id {
                study_id
            }: {str(e)}"
        )
        db.session.rollback()
        return make_response({"msg": "Unexpected server error."}, 500)


@blueprint.route("/api/<string:api_name>", methods=["DELETE"])
@participant_auth_required
def revoke_api_access(api_name: str, ditti_id: str):
    """
    Endpoint to revoke a participant's access to a specified API.
    Deletes tokens associated with the API from Secrets Manager,
    removes API access, and commits changes to the database.

    Args:
        api_name (str): Name of the API to revoke access for.
        ditti_id (str): The unique ID of the study subject, provided by the decorator.

    Returns:
        JSON response indicating success or failure of API access revocation.
    """
    try:
        # Retrieve the StudySubject by ditti_id
        study_subject = StudySubject.query.filter_by(
            ditti_id=ditti_id, is_archived=False
        ).first()
        if not study_subject:
            logger.info(
                f"StudySubject with ditti_id {ditti_id} not found or is archived."
            )
            return make_response({"msg": "User not found."}, 404)

        # Get the API by name
        api = Api.query.filter_by(name=api_name, is_archived=False).first()
        if not api:
            logger.info(f"API '{api_name}' not found.")
            return make_response({"msg": "API not found."}, 404)

        # Find the JoinStudySubjectApi entry
        join_api = JoinStudySubjectApi.query.get((study_subject.id, api.id))
        if not join_api:
            logger.info(
                f"API access for API '{api_name}' and StudySubject ID {
                    study_subject.id
                } not found."
            )
            return make_response({"msg": "API access not found."}, 404)

        # Delete tokens from Secrets Manager
        try:
            tm.delete_api_tokens(
                api_name=api_name, ditti_id=study_subject.ditti_id
            )
        except KeyError:
            logger.warning(
                f"Tokens for API '{api_name}' and StudySubject {
                    study_subject.ditti_id
                } not found."
            )
        except Exception as e:
            logger.error(f"Error deleting tokens for API '{api_name}': {str(e)}")
            return make_response({"msg": "Error deleting API tokens."}, 500)

        # Remove API access
        db.session.delete(join_api)
        db.session.commit()

        return jsonify({"msg": "API access revoked successfully"})

    except SQLAlchemyError as db_err:
        logger.error(
            f"Database error revoking API access for ditti_id {ditti_id}: {
                str(db_err)
            }"
        )
        db.session.rollback()
        return make_response({"msg": "Database error revoking API access."}, 500)
    except Exception as e:
        logger.error(
            f"Error revoking API access for ditti_id {ditti_id}: {str(e)}"
        )
        db.session.rollback()
        return make_response({"msg": "Error revoking API access."}, 500)


@blueprint.route("<string:ditti_id>", methods=["DELETE"])
@researcher_auth_required("View", "Admin Dashboard")
@researcher_auth_required("Archive", "Participants")
@researcher_auth_required("Delete", "Wearable Data")
def delete_participant(account, ditti_id: str):
    """
    Endpoint to delete a participant's account and all associated API data.
    Deletes API tokens and data, archives the StudySubject in the database,
    and removes the user from AWS Cognito.

    Args:
        ditti_id (str): ditti_id of the StudySubject to delete.

    Returns:
        JSON response confirming account deletion or an error message.
    """
    try:
        # Retrieve the StudySubject by ditti_id
        study_subject = StudySubject.query.filter_by(
            ditti_id=ditti_id, is_archived=False
        ).first()
        if not study_subject:
            logger.info(
                f"StudySubject with ditti_id {ditti_id} not found or is archived."
            )
            return make_response(
                {"msg": "User not found or already archived."}, 404
            )
        study_subject_id = study_subject.id

        # Delete all sleep logs associated with the StudySubject
        try:
            # Fetch all SleepLog entries for the StudySubject
            sleep_logs = study_subject.sleep_logs.all()
            logger.info(
                f"Deleting {len(sleep_logs)} sleep logs for StudySubject ID {
                    study_subject_id
                }."
            )

            for sleep_log in sleep_logs:
                db.session.delete(sleep_log)

        except SQLAlchemyError as db_err:
            logger.error(
                f"Database error deleting sleep logs for StudySubject ID {
                    study_subject_id
                }: {str(db_err)}"
            )
            return make_response({"msg": "Error deleting sleep data."}, 500)
        except Exception as e:
            logger.error(
                f"Error deleting sleep logs for StudySubject ID {
                    study_subject_id
                }: {str(e)}"
            )
            return make_response({"msg": "Error deleting sleep data."}, 500)

        # Delete associated JoinStudySubjectApi entries
        for api_entry in list(study_subject.apis):
            api_name = api_entry.api.name

            # Delete tokens from Secrets Manager
            try:
                tm.delete_api_tokens(
                    api_name=api_name, ditti_id=study_subject.ditti_id
                )
            except KeyError:
                logger.warning(
                    f"Tokens for API '{api_name}' and StudySubject {
                        study_subject.ditti_id
                    } not found."
                )
            except Exception as e:
                logger.error(
                    f"Error deleting tokens for API '{api_name}': {str(e)}"
                )
                return make_response({"msg": "Error deleting API tokens."}, 500)

            # Remove API access
            db.session.delete(api_entry)

        # Archive the StudySubject
        study_subject.is_archived = True

        # Commit the changes
        db.session.commit()

        # Delete user from AWS Cognito
        client = boto3.client("cognito-idp")
        try:
            # Requires aws.cognito.signin.user.admin OpenID Connect scope
            client.admin_delete_user(
                UserPoolId=current_app.config["COGNITO_PARTICIPANT_USER_POOL_ID"],
                Username=ditti_id,
            )
        except client.exceptions.NotAuthorizedException:
            logger.error("Not authorized to delete user in Cognito.")
            return make_response({"msg": "Not authorized to delete user."}, 403)
        except client.exceptions.UserNotFoundException:
            logger.warning(f"User '{ditti_id}' not found in Cognito.")
            pass
        except Exception as e:
            logger.error(f"Error deleting user from Cognito: {str(e)}")
            return make_response(
                {"msg": "Error deleting user from Cognito."}, 500
            )

        # Clear cookies
        response = make_response({"msg": "Account deleted successfully."})
        response.delete_cookie("id_token")
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response

    except SQLAlchemyError as db_err:
        logger.error(
            f"Database error deleting participant {ditti_id}: {str(db_err)}"
        )
        db.session.rollback()
        return make_response({"msg": "Database error deleting account."}, 500)
    except Exception as e:
        logger.error(f"Unhandled error deleting participant {ditti_id}: {str(e)}")
        db.session.rollback()
        return make_response({"msg": "Error deleting account."}, 500)
