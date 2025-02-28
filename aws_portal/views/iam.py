from datetime import datetime, UTC
from flask import Blueprint, jsonify, make_response, request
from flask_cors import cross_origin
from flask_jwt_extended import (
    create_access_token, current_user, get_csrf_token, get_jwt, jwt_required
)
from aws_portal.extensions import db
from aws_portal.models import Account, BlockedToken
from aws_portal.utils.auth import validate_password
from aws_portal.auth.decorators import researcher_auth_required

blueprint = Blueprint("iam", __name__, url_prefix="/iam")


@blueprint.route("/check-login")
@jwt_required()
def check_login():
    """
    Check whether the user is confirmed. This also returns a CSRF token for the
    user"s session

    Response Syntax
    ---------------
    {
        msg: "Login successful" or
            "First login",
        csrfAccessToken: str
    }
    """
    msg = "Login successful" if current_user.is_confirmed else "First login"
    return jsonify({"msg": msg, "csrfAccessToken": get_jwt()["csrf"]})


@blueprint.route("/login", methods=["POST"])
@cross_origin(
    allow_headers=["Authorization", "Content-Type", "X-CSRF-TOKEN"],
    supports_credentials=True
)
def login():
    """
    Login the user and return a CSRF token for the user"s session. This
    requires an authorization header

    Response Syntax (200) 
    ---------------------
    {
        msg: "Login successful" or
            "First login",
        csrfAccessToken: str
    }

    Request Syntax (401)
    --------------------
    {
        msg: "Login credentials are required"
    }

    Request Syntax (403)
    --------------------
    {
        msg: "Invalid login credentials"
    }
    """
    auth = request.authorization

    # if the authorization header is missing or incomplete
    if not auth or not auth.username or not auth.password:
        return make_response({"msg": "Login credentials are required"}, 401)

    account = Account.query.filter(
        (Account.email == auth.username) &
        ~Account.is_archived
    ).first()

    # if the account with a matching email exists and is not archived and the
    # password is correct
    if account is not None and account.check_password(auth.password):

        # log the user in
        access_token = create_access_token(account)
        account.last_login = datetime.now()
        db.session.commit()

        msg = "Login successful" if account.is_confirmed else "First login"
        csrf_access_token = get_csrf_token(access_token)
        res = {
            "msg": msg,
            "csrfAccessToken": csrf_access_token,
            "jwt": access_token
        }

        return jsonify(res)

    return make_response({"msg": "Invalid login credentials"},  403)


@blueprint.route("/logout", methods=["POST"])
@jwt_required()
def logout():  # TODO: remove
    """
    Log the user out

    Response Syntax (200)
    ---------------------
    {
        msg: "Logout Successful"
    }
    """

    # block the user"s token
    jti = get_jwt()["jti"]
    blocked_token = BlockedToken(jti=jti, created_on=datetime.now(UTC))
    db.session.add(blocked_token)
    db.session.commit()

    res = jsonify({"msg": "Logout Successful"})
    return res


@blueprint.route("/set-password", methods=["POST"])
@jwt_required()
def set_password():
    """
    Set a new password for the user and set is_confirmed to True

    Request Syntax
    --------------
    {
        password: str
    }

    Response syntax (200)
    ---------------------
    {
        msg: "Password set successful"
    }

    Response syntax (400)
    ---------------------
    {
        msg: "A different password must be entered" or
            "Minimum password length is 8 characters" or
            "Maximum password length is 64 characters"
    }
    """
    password = request.json["password"]
    valid = validate_password(password)

    if current_user.check_password(password):
        msg = "A different password must be entered"
        return make_response({"msg": msg}, 400)

    if valid != "valid":
        return make_response({"msg": valid}, 400)

    current_user.password = password
    current_user.is_confirmed = True
    db.session.commit()
    return jsonify({"msg": "Password set successful"})


@blueprint.route("/get-access")
@researcher_auth_required
def get_access(account):
    """
    Check whether the user has permissions for an action and resource for a
    given app and study

    Options
    -------
    app: 1 | 2 | 3
    study: int
    action: str
    resource: str

    Response Syntax (200)
    ---------------------
    {
        msg: "Authorized" or
            "Unauthorized"
    }
    """
    msg = "Authorized"
    app_id = request.args.get("app")
    study_id = request.args.get("study")
    action = request.args.get("action")
    resource = request.args.get("resource")
    permissions = account.get_permissions(app_id, study_id)

    try:
        account.validate_ask(action, resource, permissions)
    except ValueError:
        msg = "Unauthorized"

    return jsonify({"msg": msg})
