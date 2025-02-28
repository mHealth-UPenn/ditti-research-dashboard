"""
This module is maintained for backward compatibility.
All authentication functionality has been moved to more appropriate locations:
- auth_required: aws_portal.auth.decorators.jwt
- validate_password: aws_portal.auth.utils.password
"""

from aws_portal.auth.decorators import auth_required
from aws_portal.auth.utils import validate_password

__all__ = ["auth_required", "validate_password"]
