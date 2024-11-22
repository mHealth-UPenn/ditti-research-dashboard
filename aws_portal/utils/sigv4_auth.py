import logging
import traceback
from functools import wraps
from flask import request, abort, current_app
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials

logger = logging.getLogger(__name__)


def sigv4_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Extract necessary headers
            authorization = request.headers.get("Authorization")
            amz_date = request.headers.get("X-Amz-Date")

            if not authorization or not amz_date:
                logger.warning("Missing Authorization or X-Amz-Date header.")
                abort(401, description="Missing Authorization or X-Amz-Date header.")

            # Prepare the request for SigV4 verification
            headers = dict(request.headers)

            # Exclude 'x-forwarded-*' headers added by Ngrok (used for testing)
            headers = {k: v for k, v in headers.items(
            ) if not k.lower().startswith("x-forwarded-")}

            if "Host" not in headers:
                headers["Host"] = request.host

            # Reconstruct the full URL using the scheme and host from the request
            scheme = headers.get("X-Forwarded-Proto", request.scheme)
            # Handle multiple values in 'X-Forwarded-Proto' if any
            if "," in scheme:
                scheme = scheme.split(",")[0].strip()
            host = headers.get("Host", request.host)
            path = request.full_path  # includes query string

            full_url = f"{scheme}://{host}{path}"
            if path.endswith("?"):
                full_url = full_url[:-1]  # Remove trailing '?'

            # Get the body as bytes
            body = request.get_data()

            # Create an AWSRequest object without 'x-forwarded-*' headers
            aws_request = AWSRequest(
                method=request.method,
                url=full_url,
                data=body,
                headers=headers
            )

            # Extract credentials from environment or config
            access_key = current_app.config.get("LAMBDA_ACCESS_KEY_ID")
            secret_key = current_app.config.get("LAMBDA_SECRET_ACCESS_KEY")
            region = current_app.config.get("LAMBDA_AWS_REGION")
            service = "execute-api"

            if not access_key or not secret_key:
                logger.error(
                    "LAMBDA_ACCESS_KEY_ID or LAMBDA_SECRET_ACCESS_KEY not set in config.")
                abort(500, description="Server configuration error.")

            credentials = Credentials(access_key, secret_key)

            # Sign the request using the credentials
            SigV4Auth(credentials, service, region).add_auth(aws_request)

            # Calculate Authorization header
            signed_headers = dict(aws_request.headers)
            calculated_authorization = signed_headers.get("Authorization")

            # Compare the calculated signature with the one provided
            provided_authorization = authorization

            if not provided_authorization:
                logger.warning("Authorization header missing after signing.")
                abort(401, description="Invalid Authorization header.")

            if provided_authorization != calculated_authorization:
                logger.warning("Signature mismatch.")
                abort(401, description="Invalid signature.")

        except Exception as e:
            logger.error(f"SigV4 authentication failed: {e}")
            traceback_str = traceback.format_exc()
            logger.error(traceback_str)
            abort(401, description="Unauthorized: SigV4 authentication failed.")

        return func(*args, **kwargs)
    return wrapper
