import logging

logger = logging.getLogger(__name__)


def clear_auth_cookies(response):
    """
    Clear authentication cookies from a response.

    Parameters
    ----------
        response: Flask response object to clear cookies from

    Returns
    -------
        The response object with cleared cookies
    """
    # Clear all auth cookies
    for cookie_name in ["id_token", "access_token", "refresh_token"]:
        response.set_cookie(
            cookie_name,
            "",
            expires=0,
            httponly=True,
            secure=True,
            samesite="None",
        )

    return response


def set_auth_cookies(response, token):
    """
    Set authentication cookies on a response.

    Parameters
    ----------
        response: Flask response object to set cookies on
        token: Dict containing tokens (id_token, access_token,
            and optionally refresh_token)

    Returns
    -------
        The response object with set cookies
    """
    # Set ID token cookie
    response.set_cookie(
        "id_token",
        token["id_token"],
        httponly=True,
        secure=True,
        samesite="None",
        max_age=3600,
    )

    # Set access token cookie
    response.set_cookie(
        "access_token",
        token["access_token"],
        httponly=True,
        secure=True,
        samesite="None",
        max_age=3600,
    )

    # Set refresh token cookie if present
    if "refresh_token" in token:
        response.set_cookie(
            "refresh_token",
            token["refresh_token"],
            httponly=True,
            secure=True,
            samesite="None",
            max_age=86400,
        )

    return response
