from datetime import datetime
from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import (
    create_access_token, current_user, get_jwt, jwt_required,
    set_access_cookies, unset_jwt_cookies
)
from aws_portal.extensions import db
from aws_portal.models import Account, BlockedToken
from aws_portal.utils.auth import validate_password

blueprint = Blueprint('iam', __name__, url_prefix='/iam')


@blueprint.route('/check-login')
@jwt_required()
def check_login():
    msg = 'Login successful' if current_user.is_confirmed else 'First login'
    return jsonify({'msg': msg})


@blueprint.route('/login', methods=['POST'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response({'msg': 'Login credentials are required'}, 401)

    account = Account.query.filter(
        (Account.email == auth.username) &
        ~Account.is_archived
    ).first()

    if account is not None and account.check_password(auth.password):
        access_token = create_access_token(account)
        account.last_login = datetime.now()
        db.session.commit()

        msg = 'Login successful' if account.is_confirmed else 'First login'
        res = jsonify({'msg': msg})
        set_access_cookies(res, access_token)

        return res

    return make_response({'msg': 'Invalid login credentials'},  403)


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


@blueprint.route('/set-password', methods=['POST'])
@jwt_required()
def set_password():
    password = request.json['password']
    valid = validate_password(password)

    if current_user.check_password(password):
        msg = 'A different password must be entered'
        return make_response({'msg': msg}, 400)

    if valid != 'valid':
        return make_response({'msg': valid}, 400)

    current_user.password = password
    current_user.is_confirmed = True
    db.session.commit()
    return jsonify({'msg': 'Password set successful'})


@blueprint.route('/get-access')
@jwt_required()
def get_access():  # TODO: write unit test
    msg = 'Authorized'
    app_id = request.args.get('app')
    study_id = request.args.get('study')
    action = request.args.get('action')
    resource = request.args.get('resource')
    permissions = current_user.get_permissions(app_id, study_id)

    try:
        current_user.validate_ask(action, resource, permissions)

    except ValueError:
        msg = 'Unauthorized'

    return jsonify({'msg': msg})
