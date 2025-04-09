# Standard error messages
AUTH_ERROR_MESSAGES = {
    "auth_failed": "Authentication failed",
    "auth_required": "Authentication required",
    "invalid_request": "Invalid request parameters",
    "session_expired": "Session expired. Please login again",
    "account_archived": "Account unavailable. Please contact support",
    "system_error": "System error. Please try again later",
    "not_found": "Resource not found",
    "invalid_credentials": "Invalid credentials",

    # Password change specific messages
    "missing_password": "New password is required",
    "missing_previous_password": "Current password is required",
    "incorrect_password": "Incorrect current password",
    "invalid_password": "Password does not meet Cognito requirements. Password must be at least 8 characters, include uppercase and lowercase letters, numbers, and special characters.",
    "invalid_password_format": "Invalid password format",
    "password_change_error": "Failed to change password",
    "password_change_success": "Password changed successfully",
    "password_history_violation": "Your new password cannot match recently used passwords. Please choose a different password.",
    "user_not_found": "User account not found",
    "user_not_confirmed": "User account is not confirmed",
    "password_reset_required": "Password reset is required. Please use the forgot password flow.",
    "too_many_requests": "Too many requests. Please try again later.",
    "limit_exceeded": "Request limit exceeded. Please try again later.",
    "forbidden": "Access denied by security rules",
    "invalid_parameters": "Invalid request parameters",
    "resource_not_found": "Required resource not found",
    "internal_service_error": "An internal service error occurred. Please try again later.",

    # Account management messages
    "missing_required_fields": "Email, first name, and last name are required",
    "missing_email": "Email is required for updating an account",
    "account_disabled": "Account disabled successfully",
    "account_disable_error": "Failed to disable account",
    "login_successful": "Login successful",
    "registration_successful": "Registration successful"
}
