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
from botocore.exceptions import ClientError
from flask import current_app

logger = logging.getLogger(__name__)


def get_researcher_cognito_client():
    """
    Initialize and return a boto3 Cognito IDP client for the researcher user pool.

    Returns:
        boto3.client: Cognito IDP client configured for researcher operations
    """
    region = current_app.config["COGNITO_RESEARCHER_REGION"]
    return boto3.client("cognito-idp", region_name=region)


def create_researcher(email, temp_password=None, attributes=None):
    """
    Create a new researcher in the Cognito user pool with a temporary password.
    Cognito will send an invitation email with the temporary password.

    Args:
        email (str): Researcher's email address (used as username)
        temp_password (str, optional): Custom temporary password. If None, a random one is generated.
        attributes (dict, optional): Additional user attributes to set

    Returns:
        tuple: (bool, str) - (success, message)
    """
    try:
        # Initialize Cognito client
        client = get_researcher_cognito_client()
        user_pool_id = current_app.config["COGNITO_RESEARCHER_USER_POOL_ID"]

        # Prepare user attributes
        user_attributes = []
        if attributes:
            for key, value in attributes.items():
                # Only include attributes with non-empty values
                if value is not None and value.strip() != "":
                    user_attributes.append({
                        "Name": key,
                        "Value": str(value)
                    })

        # Always include email and email_verified attributes
        user_attributes.extend([
            {
                "Name": "email",
                "Value": email
            },
            {
                "Name": "email_verified",
                "Value": "true"
            }
        ])

        # Create user in Cognito
        if temp_password:
            # Create user with specified temporary password
            response = client.admin_create_user(
                UserPoolId=user_pool_id,
                Username=email,
                UserAttributes=user_attributes,
                TemporaryPassword=temp_password,
                MessageAction="SUPPRESS"  # Don't send automatic email
            )
        else:
            # Let Cognito generate a temporary password and send invitation
            response = client.admin_create_user(
                UserPoolId=user_pool_id,
                Username=email,
                UserAttributes=user_attributes
            )

        logger.info(f"Created Cognito user: {email}")
        return True, "User created successfully in Cognito"

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        if error_code == "UsernameExistsException":
            logger.warning(f"User {email} already exists in Cognito")
            return False, "User already exists"
        elif error_code == "InvalidPasswordException":
            logger.warning(f"Invalid password for user {email}")
            return False, "Password does not meet requirements"
        elif error_code == "LimitExceededException":
            logger.warning("Cognito rate limit exceeded")
            return False, "Rate limit exceeded. Please try again later."
        else:
            logger.error(f"Cognito error: {error_code} - {error_message}")
            return False, f"Error creating user: {error_message}"

    except Exception as e:
        logger.error(f"Unexpected error creating Cognito user: {str(e)}")
        return False, "Unexpected error creating user"


def update_researcher(email, attributes=None, attributes_to_delete=None):
    """
    Update a researcher's attributes in the Cognito user pool.

    This function supports both adding/updating attributes and removing attributes.
    For attributes that should be updated, provide them in the attributes dictionary.
    For attributes that should be removed, list them in attributes_to_delete.

    Note: Only non-required attributes can be deleted. Required attributes like email
    cannot be removed but can be updated.

    Args:
        email (str): Researcher's email address (used as username)
        attributes (dict, optional): User attributes to update. Keys should match
                                    Cognito attribute names (e.g., 'given_name', 'family_name', 'phone_number').
        attributes_to_delete (list, optional): Attribute names to delete from the user's profile.
                                              Standard Cognito attribute names should be used.

    Returns:
        tuple: (bool, str) - (success, message)
            success: True if the operations completed successfully, False otherwise
            message: A descriptive success or error message
    """
    try:
        # Initialize Cognito client
        client = get_researcher_cognito_client()
        user_pool_id = current_app.config["COGNITO_RESEARCHER_USER_POOL_ID"]

        # Process attributes to update
        if attributes:
            # Prepare user attributes for update
            user_attributes = []
            for key, value in attributes.items():
                # Never allow updating the email attribute
                if key == "email":
                    logger.warning(
                        f"Attempt to update email attribute for user {email} was blocked")
                    continue

                # Only include attributes with non-empty values
                if value is not None and value.strip() != "":
                    user_attributes.append({
                        "Name": key,
                        "Value": str(value)
                    })

            # If we have valid attributes to update, update them
            if user_attributes:
                # Update user attributes in Cognito
                client.admin_update_user_attributes(
                    UserPoolId=user_pool_id,
                    Username=email,
                    UserAttributes=user_attributes
                )
                logger.info(f"Updated Cognito user attributes for {email}")

        # Process attributes to delete
        if attributes_to_delete:
            for attr_name in attributes_to_delete:
                # Never allow deleting the email attribute (critical security measure)
                if attr_name == "email":
                    logger.warning(
                        f"Attempt to delete email attribute for user {email} was blocked")
                    continue

                try:
                    # Delete specific attribute
                    client.admin_delete_user_attributes(
                        UserPoolId=user_pool_id,
                        Username=email,
                        UserAttributeNames=[attr_name]
                    )
                    logger.info(
                        f"Deleted attribute {attr_name} for user {email}")
                except ClientError as attr_error:
                    # Log the error but continue processing other attributes
                    # This prevents a single attribute failure from blocking other operations
                    logger.warning(
                        f"Failed to delete attribute {attr_name} for user {email}: {str(attr_error)}")

        return True, "User attributes updated successfully"

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        if error_code == "UserNotFoundException":
            logger.warning(f"User {email} not found in Cognito")
            return False, "User not found"
        elif error_code == "LimitExceededException":
            logger.warning("Cognito rate limit exceeded")
            return False, "Rate limit exceeded. Please try again later."
        else:
            logger.error(f"Cognito error: {error_code} - {error_message}")
            return False, f"Error updating user: {error_message}"

    except Exception as e:
        logger.error(f"Unexpected error updating Cognito user: {str(e)}")
        return False, "Unexpected error updating user"


def delete_researcher(email):
    """
    Delete a researcher from the Cognito user pool.

    Args:
        email (str): Researcher's email address (used as username)

    Returns:
        tuple: (bool, str) - (success, message)
    """
    try:
        # Initialize Cognito client
        client = get_researcher_cognito_client()
        user_pool_id = current_app.config["COGNITO_RESEARCHER_USER_POOL_ID"]

        # Delete user from Cognito
        client.admin_delete_user(
            UserPoolId=user_pool_id,
            Username=email
        )

        logger.info(f"Deleted Cognito user: {email}")
        return True, "User deleted successfully"

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        if error_code == "UserNotFoundException":
            logger.warning(f"User {email} not found in Cognito")
            return False, "User not found"
        elif error_code == "LimitExceededException":
            logger.warning("Cognito rate limit exceeded")
            return False, "Rate limit exceeded. Please try again later."
        else:
            logger.error(f"Cognito error: {error_code} - {error_message}")
            return False, f"Error deleting user: {error_message}"

    except Exception as e:
        logger.error(f"Unexpected error deleting Cognito user: {str(e)}")
        return False, "Unexpected error deleting user"


def get_researcher(email):
    """
    Get researcher information from Cognito.

    Args:
        email (str): Researcher's email address (used as username)

    Returns:
        tuple: (user_info, error_message)
            user_info: Researcher information dictionary if successful, None otherwise
            error_message: Error message if user_info is None, None otherwise
    """
    try:
        # Initialize Cognito client
        client = get_researcher_cognito_client()
        user_pool_id = current_app.config["COGNITO_RESEARCHER_USER_POOL_ID"]

        # Get user from Cognito
        response = client.admin_get_user(
            UserPoolId=user_pool_id,
            Username=email
        )

        # Extract user attributes
        user_info = {
            "username": response.get("Username"),
            "user_status": response.get("UserStatus"),
            "enabled": response.get("Enabled", False),
            "attributes": {}
        }

        # Convert list of attributes to dictionary
        for attr in response.get("UserAttributes", []):
            user_info["attributes"][attr["Name"]] = attr["Value"]

        return user_info, None

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_message = e.response["Error"]["Message"]

        if error_code == "UserNotFoundException":
            logger.warning(f"User {email} not found in Cognito")
            return None, "User not found"
        else:
            logger.error(f"Cognito error: {error_code} - {error_message}")
            return None, f"Error getting user: {error_message}"

    except Exception as e:
        logger.error(f"Unexpected error getting Cognito user: {str(e)}")
        return None, "Unexpected error getting user"
