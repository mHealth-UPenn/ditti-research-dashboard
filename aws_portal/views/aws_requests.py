import re
from flask import Blueprint, jsonify, request
from aws_portal.utils.auth import auth_required
from aws_portal.utils.aws import Query

blueprint = Blueprint('aws', __name__, url_prefix='/aws')


@blueprint.route('/scan')
@auth_required('Read')
def scan():
    app = request.args.get('app')
    key = request.args.get('key')
    query = request.args.get('query')

    if re.search(Query.invalid_chars, query) is not None:
        return jsonify({'msg': 'Invalid Query'})

    res = Query(app, key, query).scan()
    res = {
        'msg': 'Scan Successful',
        'res': res['Items']
    }

    return jsonify(res)


@blueprint.route('/user/create')
@auth_required('Create', 'User')
def user_create():
    return jsonify({})


@blueprint.route('/user/edit')
@auth_required('Edit', 'User')
def user_edit():
    return jsonify({})


@blueprint.route('/user/archive')
@auth_required('Archive', 'User')
def user_archive():
    return jsonify({})
