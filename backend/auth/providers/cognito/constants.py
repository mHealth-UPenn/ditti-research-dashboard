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

# Standard error messages
AUTH_ERROR_MESSAGES = {
    # Authentication and session errors
    "auth_failed": "Authentication failed",
    "auth_required": "Authentication required",
    "invalid_request": "Invalid request parameters",
    "session_expired": "Session expired. Please login again",
    "account_archived": "Account unavailable. Please contact support",
    "system_error": "System error. Please try again later",
    "not_found": "Resource not found",
    "invalid_credentials": "Invalid credentials",
    "no_token": "No authentication token found",
    "no_refresh_token": "No refresh token found",
    "no_id_token": "No ID token found",
    "token_validation_failed": "Failed to validate token",
    "refresh_failed": "Failed to refresh authentication tokens",
    "invalid_token_format": "Invalid token format",
    "new_token_validation_failed": "Failed to validate new tokens",
    "csrf_error": "CSRF token validation failed",
    # Password related errors
    "missing_password": "New password is required",
    "missing_previous_password": "Current password is required",
    "incorrect_password": "Incorrect current password",
    "invalid_password": "Password does not meet Cognito requirements. Password must be at least 8 characters, include uppercase and lowercase letters, numbers, and special characters.",
    "invalid_password_format": "Invalid password format",
    "password_change_error": "Failed to change password",
    "password_change_success": "Password changed successfully",
    "password_history_violation": "Your new password cannot match recently used passwords. Please choose a different password.",
    "password_reset_required": "Password reset is required. Please use the forgot password flow.",
    # User account errors
    "user_not_found": "User account not found",
    "user_not_confirmed": "User account is not confirmed",
    "account_not_found": "Account not found",
    "missing_username": "Username is missing from token or account information",
    "missing_email": "Email is required for account operations",
    "account_disabled": "Account disabled successfully",
    "account_disable_error": "Failed to disable account",
    # Request handling errors
    "too_many_requests": "Too many requests. Please try again later.",
    "limit_exceeded": "Request limit exceeded. Please try again later.",
    "forbidden": "Access denied by security rules",
    "invalid_parameters": "Invalid request parameters",
    "resource_not_found": "Required resource not found",
    "internal_service_error": "An internal service error occurred. Please try again later.",
    "database_error": "A database error occurred. Please try again later.",
    "authentication_error": "An error occurred during the authentication process",
    # Account management errors
    "missing_required_fields": "Email, first name, and last name are required",
    "missing_fields": "Required fields are missing",
    "registration_error": "An error occurred during registration",
    # Success messages
    "login_successful": "Login successful",
    "registration_successful": "Registration successful",
}


# Function to get the standard error code for a message key
def get_error_code(message_key):
    """
    Get the standardized error code for a message key.

    Parameters
    ----------
        message_key (str): The key in AUTH_ERROR_MESSAGES

    Returns
    -------
        str: The uppercase version of the message key to use as error_code
    """
    return message_key.upper()
