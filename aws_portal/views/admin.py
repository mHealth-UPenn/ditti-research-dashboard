from datetime import datetime
import uuid
from flask import Blueprint, jsonify, request
from aws_portal.extensions import db
from aws_portal.models import Account, Study
from aws_portal.utils.auth import auth_required

blueprint = Blueprint('admin', __name__, url_prefix='/admin')


@blueprint.route('/account')
@auth_required('Read', 'Account')
def account():
    accounts = Account.query.all()
    res = [a.meta for a in accounts]
    return jsonify(res)


@blueprint.route('/account/create', methods=['POST'])
@auth_required('Create', 'Account')
def account_create():
    account = Account(
        public_id=str(uuid.uuid4()),
        created_on=datetime.utcnow(),
        first_name=request.json['first_name'],
        last_name=request.json['last_name'],
        email=request.json['email'],
    )

    db.session.flush()
    account.password = request.json['password']
    db.session.add(account)
    db.session.commit()

    return jsonify({'msg': 'Account Created Successfully'})


@blueprint.route('/account/edit', methods=['POST'])
@auth_required('Edit', 'Account')
def account_edit():
    account_id = request.json['id']
    account = Account.query.get(account_id)

    try:
        for k, v in request.json['edit'].items():
            if hasattr(account, k):
                setattr(account, k, v)

            else:
                raise ValueError

        msg = 'Account Edited Successfully'
        db.session.commit()

    except ValueError:
        msg = 'Invalid attribute: %s' % k
        db.session.rollback()

    return jsonify({'msg': msg})


@blueprint.route('/account/archive', methods=['POST'])
def account_archive():
    return jsonify({})


@blueprint.route('/study')
def study():
    studies = Study.query.all()
    res = [a.meta for a in studies]
    return jsonify(res)


@blueprint.route('/study/create', methods=['POST'])
def study_create():
    return jsonify({})


@blueprint.route('/study/edit', methods=['POST'])
def study_edit():
    return jsonify({})


@blueprint.route('/study/archive', methods=['POST'])
def study_archive():
    return jsonify({})


@blueprint.route('/access-group')
def access_group():
    return jsonify({})


@blueprint.route('/access-group/create', methods=['POST'])
def access_group_create():
    return jsonify({})


@blueprint.route('/access-group/edit', methods=['POST'])
def access_group_edit():
    return jsonify({})


@blueprint.route('/access-group/archive', methods=['POST'])
def access_group_archive():
    return jsonify({})


@blueprint.route('/role')
def role():
    return jsonify({})


@blueprint.route('/role/create', methods=['POST'])
def role_create():
    return jsonify({})


@blueprint.route('/role/edit', methods=['POST'])
def role_edit():
    return jsonify({})


@blueprint.route('/role/archive', methods=['POST'])
def role_archive():
    return jsonify({})


@blueprint.route('/permission')
def permission():
    return jsonify({})


@blueprint.route('/permission/create', methods=['POST'])
def permission_create():
    return jsonify({})


@blueprint.route('/permission/edit', methods=['POST'])
def permission_edit():
    return jsonify({})


@blueprint.route('/permission/archive', methods=['POST'])
def permission_archive():
    return jsonify({})


@blueprint.route('/app')
def app():
    return jsonify({})


@blueprint.route('/app/create', methods=['POST'])
def app_create():
    return jsonify({})


@blueprint.route('/app/edit', methods=['POST'])
def app_edit():
    return jsonify({})


@blueprint.route('/app/archive', methods=['POST'])
def app_archive():
    return jsonify({})
