from datetime import datetime
import uuid
from flask import Blueprint, jsonify, request
from aws_portal.extensions import db
from aws_portal.models import Account
from aws_portal.utils.auth import auth_required

blueprint = Blueprint('admin', __name__, url_prefix='/admin')


@blueprint.route('/account/create', methods=['POST'])
@auth_required('Create', 'User')
def account_create():
    account = Account(
        public_id=str(uuid.uuid4()),
        created_on=datetime.utcnow(),
        first_name=request.form['first-name'],
        last_name=request.form['last-name'],
        email=request.form['email'],
    )

    db.session.flush()
    account.password = request.form['password']
    db.session.add(account)
    db.session.commit()

    return jsonify({'msg': 'Account Created Successfully'})
