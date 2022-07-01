from functools import reduce
import logging
import re
import traceback
from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import current_user
import pandas as pd
from aws_portal.models import JoinAccountStudy, Study
from aws_portal.utils.auth import auth_required
from aws_portal.utils.aws import MutationClient, Query, Updater

blueprint = Blueprint('aws', __name__, url_prefix='/aws')
logger = logging.getLogger(__name__)


@blueprint.route('/scan')
@auth_required('View', 'Ditti App Dashboard')
def scan():  # TODO update unit test
    app = 'DittiApp'  # TODO fix hard-coded app
    key = request.args.get('key')
    query = request.args.get('query')

    if re.search(Query.invalid_chars, query) is not None:
        return jsonify({'msg': 'Invalid Query'})

    res = Query(app, key, query).scan()
    return jsonify(res['Items'])


@blueprint.route('/get-taps')
@auth_required('View', 'Ditti App Dashboard')
def get_taps():  # TODO update unit test
    def f(left, right):
        q = 'user_permission_idBEGINS"%s"' % right
        return left + ('OR' if left else '') + q

    try:
        app_id = request.args['app']
        permissions = current_user.get_permissions(app_id)
        current_user.validate_ask('View', 'All Studies', permissions)
        users = Query('DittiApp', 'User').scan()

    except ValueError:
        studies = Study.query\
            .join(JoinAccountStudy)\
            .filter(JoinAccountStudy.account_id == current_user.id)\
            .all()

        prefixes = [s.ditti_id for s in studies]
        query = reduce(f, prefixes, '')
        users = Query('DittiApp', 'User', query).scan()['Items']

    except Exception as e:
        exc = traceback.format_exc()
        logger.warn(exc)
        msg = 'Query failed: %s' % e

        return make_response({'msg': msg}, 500)

    taps = Query('DittiApp', 'Tap').scan()['Items']

    df_users = pd.DataFrame(users, columns=['id', 'user_permission_id'])\
        .rename(columns={'user_permission_id': 'dittiId'})

    df_taps = pd.DataFrame(taps, columns=['tapUserId', 'time'])\
        .rename(columns={'tapUserId': 'id'})

    res = pd.merge(df_users, df_taps, on='id')\
        .drop('id', axis=1)\
        .to_dict('records')

    return jsonify(res)


@blueprint.route('/get-users')
@auth_required('View', 'Ditti App Dashboard')
def get_users():  # TODO: create unit test
    def f(left, right):
        q = 'user_permission_idBEGINS"%s"' % right
        return left + ('OR' if left else '') + q

    def map_users(user):
        information = user['information'] if 'information' in user else ''

        return {
            'tapPermission': user['tap_permission'],
            'information': information,
            'userPermissionId': user['user_permission_id'],
            'expTime': user['exp_time'],
            'teamEmail': user['team_email'],
            'createdAt': user['createdAt']
        }

    users = None

    try:
        app_id = request.args['app']
        permissions = current_user.get_permissions(app_id)
        current_user.validate_ask('View', 'All Studies', permissions)
        users = Query('DittiApp', 'User').scan()['Items']
        res = map(map_users, users)

        return jsonify(list(res))

    except ValueError:
        studies = Study.query\
            .join(JoinAccountStudy)\
            .filter(JoinAccountStudy.account_id == current_user.id)\
            .all()

    except Exception as e:
        exc = traceback.format_exc()
        logger.warn(exc)
        msg = 'Query failed: %s' % e

        return make_response({'msg': msg}, 500)

    prefixes = [s.ditti_id for s in studies]
    query = reduce(f, prefixes, '')
    users = Query('DittiApp', 'User', query).scan()['Items']
    res = map(map_users, users)

    return jsonify(list(res))


@blueprint.route('/user/create', methods=['POST'])
@auth_required('View', 'Ditti App Dashboard')
@auth_required('Create', 'Users')
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
        exc = traceback.format_exc()
        logger.warn(exc)
        msg = 'User creation failed: %s' % e

        return make_response({'msg': msg}, 500)

    return jsonify({'msg': msg})


@blueprint.route('/user/edit', methods=['POST'])
@auth_required('View', 'Ditti App Dashboard')
@auth_required('Edit', 'Users')
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
        exc = traceback.format_exc()
        logger.warn(exc)
        msg = 'User Edit Failed: %s' % e

        return make_response({'msg': msg}, 500)

    return jsonify({'msg': msg})
