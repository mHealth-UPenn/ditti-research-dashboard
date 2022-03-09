import re
from flask import Blueprint, jsonify, request
from aws_portal.models import Study
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
    app = request.json.get('app')
    user_permission_id = request.args.get('user_permission_id')

    acronym = re.sub(r'[\d]+', '', user_permission_id)
    study_id = request.json.get('study')
    study = Study.query.get(study_id)

    if acronym != study.ditti_id:
        return jsonify({'msg': 'Invalid study acronym: %s' % acronym})

    if re.search(r'[^\dA-Za-z]', user_permission_id) is not None:
        return jsonify({'msg': 'Invalid Ditti ID: %s' % user_permission_id})

    query = 'user_permission_id==' % user_permission_id
    res = Query(app, 'User', query).scan()

    if not res['Items']:
        return jsonify({'msg': 'Ditti ID not found: %s' % user_permission_id})

    return jsonify({})


@blueprint.route('/user/edit')
@auth_required('Edit', 'User')
def user_edit():
    return jsonify({})


@blueprint.route('/user/archive')
@auth_required('Archive', 'User')
def user_archive():
    return jsonify({})
