from datetime import datetime
from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import (
    create_access_token, get_jwt, jwt_required, set_access_cookies,
    unset_jwt_cookies, verify_jwt_in_request
)
from aws_portal.extensions import db
from aws_portal.models import Account, BlockedToken

blueprint = Blueprint('iam', __name__, url_prefix='/iam')


@blueprint.route('/check-login')
def check_login():
    check = verify_jwt_in_request(optional=True)

    if check is None:
        return make_response('Unauthorized', 401)

    res = {'msg': 'User is logged in'}
    return jsonify(res)


@blueprint.route('/login', methods=['POST'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Login credentials are required', 401)

    account = Account.query.filter(
        (Account.email == auth.username) &
        ~Account.is_archived
    ).first()

    if account is not None and account.check_password(auth.password):
        access_token = create_access_token(account)
        res = jsonify({'msg': 'Login Successful'})
        set_access_cookies(res, access_token)

        return res

    return make_response('Invalid login credentials',  403)


@blueprint.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    blocked_token = BlockedToken(jti=jti, created_on=datetime.utcnow())
    db.session.add(blocked_token)
    db.session.commit()

    res = jsonify({'msg': 'Logout Successful'})
    unset_jwt_cookies(res)

    return res
