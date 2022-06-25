import re
from flask import Blueprint, jsonify, request
from aws_portal.models import Study
from aws_portal.utils.auth import auth_required
from aws_portal.utils.aws import MutationClient, Query, Updater

blueprint = Blueprint('aws', __name__, url_prefix='/aws')


@blueprint.route('/scan')
@auth_required('Read')
def scan():  # TODO update unit test
    app = 'DittiApp'  # TODO fix hard-coded app
    key = request.args.get('key')
    query = request.args.get('query')

    if re.search(Query.invalid_chars, query) is not None:
        return jsonify({'msg': 'Invalid Query'})

    res = Query(app, key, query).scan()
    return jsonify(res['Items'])


@blueprint.route('/user/create', methods=['POST'])
@auth_required('Create', 'User')
def user_create():
    msg = 'User Created Successfully'

    try:
        client = MutationClient()
        client.open_connection()
        client.set_mutation(
            'CreateUserPermissionInput',
            'createUserPermission',
            request.json.get('create')
        )

        client.post_mutation()

    except Exception as e:
        msg = 'User creation failed: %s' % e

    return jsonify({'msg': msg})


@blueprint.route('/user/edit', methods=['POST'])
@auth_required('Edit', 'User')
def user_edit():
    msg = 'User Successfully Edited'
    app = 'DittiApp'  # TODO fix hard-coded app
    user_permission_id = request.json.get('user_permission_id')

    if re.search(r'[^\dA-Za-z]', user_permission_id) is not None:
        return jsonify({'msg': 'Invalid Ditti ID: %s' % user_permission_id})

    acronym = re.sub(r'[\d]+', '', user_permission_id)
    study_id = request.json.get('study')
    study = Study.query.get(study_id)

    if acronym != study.ditti_id:
        return jsonify({'msg': 'Invalid study acronym: %s' % acronym})

    query = 'user_permission_id=="%s"' % user_permission_id
    res = Query(app, 'User', query).scan()

    if not res['Items']:
        return jsonify({'msg': 'Ditti ID not found: %s' % user_permission_id})

    try:
        updater = Updater(app, 'User')
        updater.set_key_from_query(query)
        updater.set_expression(request.json.get('edit'))
        updater.update()

    except Exception as e:
        msg = 'User Edit Failed: %s' % e

    return jsonify({'msg': msg})
