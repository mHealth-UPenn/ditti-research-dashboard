from datetime import datetime
import logging
import traceback
import uuid
from flask import Blueprint, jsonify, make_response, request
from aws_portal.extensions import db
from aws_portal.models import (
    AccessGroup, Account, Action, App, JoinAccessGroupPermission,
    JoinAccountAccessGroup, JoinAccountStudy, JoinRolePermission, Permission,
    Resource, Role, Study
)
from aws_portal.utils.auth import auth_required, validate_password
from aws_portal.utils.db import populate_model

blueprint = Blueprint('admin', __name__, url_prefix='/admin')
logger = logging.getLogger(__name__)


@blueprint.route('/account')
@auth_required('View', 'Admin Dashboard')
def account():
    try:
        i = request.args.get('id')

        if i:
            q = Account.query.filter(
                ~Account.is_archived & Account.id == int(i)
            )

        else:
            q = Account.query.filter(~Account.is_archived)

        res = [a.meta for a in q.all()]
        return jsonify(res)

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)


@blueprint.route('/account/create', methods=['POST'])
@auth_required('View', 'Admin Dashboard')
@auth_required('Create', 'Accounts')
def account_create():
    try:
        data = request.json['create']
        password = data['password']

        if not password:
            msg = 'A password was not provided.'
            return make_response({'msg': msg}, 400)

        valid = validate_password(data, password)
        if valid != 'valid':
            return make_response({'msg': valid}, 400)

        account = Account()

        populate_model(account, data)
        account.public_id = str(uuid.uuid4())
        account.created_on = datetime.utcnow()

        for entry in data['access_groups']:
            access_group = AccessGroup.query.get(entry['id'])
            JoinAccountAccessGroup(access_group=access_group, account=account)

        for entry in data['studies']:
            study = Study.query.get(entry['id'])
            role = Role.query.get(entry['role']['id'])
            JoinAccountStudy(account=account, role=role, study=study)

        db.session.add(account)
        db.session.commit()
        msg = 'Account Created Successfully'

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)

    return jsonify({'msg': msg})


@blueprint.route('/account/edit', methods=['POST'])
@auth_required('View', 'Admin Dashboard')
@auth_required('Edit', 'Accounts')
def account_edit():
    try:
        data = request.json['edit']
        account_id = request.json['id']
        account = Account.query.get(account_id)
        password = data['password']

        if not password:
            del data['password']

        else:
            valid = validate_password(data, password)

            if valid != 'valid':
                return make_response({'msg': valid}, 400)

        populate_model(account, data)

        if 'access_groups' in data:
            for join in account.access_groups:
                a_ids = [a['id'] for a in data['access_groups']]

                if join.access_group_id not in a_ids:
                    db.session.delete(join)

            a_ids = [join.access_group_id for join in account.access_groups]
            for entry in data['access_groups']:
                if entry['id'] not in a_ids:
                    access_group = AccessGroup.query.get(entry['id'])
                    JoinAccountAccessGroup(
                        access_group=access_group,
                        account=account
                    )

        if 'studies' in data:
            for join in account.studies:
                s_ids = [s['id'] for s in data['studies']]

                if join.study_id not in s_ids:
                    db.session.delete(join)

            s_ids = [join.study_id for join in account.studies]
            for entry in data['studies']:
                study = Study.query.get(entry['id'])

                if entry['id'] in s_ids:
                    join = JoinAccountStudy.query.get((account.id, study.id))

                    if join.role.id != int(entry['role']['id']):
                        join.role = Role.query.get(entry['role']['id'])

                else:
                    role = Role.query.get(entry['role']['id'])
                    JoinAccountStudy(account=account, role=role, study=study)

        db.session.commit()
        msg = 'Account Edited Successfully'

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)

    return jsonify({'msg': msg})


@blueprint.route('/account/archive', methods=['POST'])
@auth_required('View', 'Admin Dashboard')
@auth_required('Archive', 'Accounts')
def account_archive():
    try:
        account_id = request.json['id']
        account = Account.query.get(account_id)
        account.is_archived = True
        db.session.commit()
        msg = 'Account Archived Successfully'

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)

    return jsonify({'msg': msg})


@blueprint.route('/study')
@auth_required('View', 'Admin Dashboard')
def study():
    try:
        i = request.args.get('id')

        if i:
            q = Study.query.filter(~Study.is_archived & Study.id == int(i))

        else:
            q = Study.query.filter(~Study.is_archived)

        res = [s.meta for s in q.all()]
        return jsonify(res)

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)


@blueprint.route('/study/create', methods=['POST'])
@auth_required('View', 'Admin Dashboard')
@auth_required('Create', 'Studies')
def study_create():
    try:
        data = request.json['create']
        study = Study()

        populate_model(study, data)
        db.session.add(study)
        db.session.commit()
        msg = 'Study Created Successfully'

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)

    return jsonify({'msg': msg})


@blueprint.route('/study/edit', methods=['POST'])
@auth_required('View', 'Admin Dashboard')
@auth_required('Edit', 'Studies')
def study_edit():
    try:
        data = request.json['edit']
        study_id = request.json['id']
        study = Study.query.get(study_id)

        populate_model(study, data)
        db.session.commit()
        msg = 'Study Edited Successfully'

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)

    return jsonify({'msg': msg})


@blueprint.route('/study/archive', methods=['POST'])
@auth_required('View', 'Admin Dashboard')
@auth_required('Archive', 'Studies')
def study_archive():
    try:
        study_id = request.json['id']
        study = Study.query.get(study_id)
        study.is_archived = True
        db.session.commit()
        msg = 'Study Archived Successfully'

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)

    return jsonify({'msg': msg})


@blueprint.route('/access-group')
@auth_required('View', 'Admin Dashboard')
def access_group():
    try:
        i = request.args.get('id')

        if i:
            q = AccessGroup.query.filter(
                ~AccessGroup.is_archived & AccessGroup.id == int(i)
            )

        else:
            q = AccessGroup.query.filter(~AccessGroup.is_archived)

        res = [a.meta for a in q.all()]
        return jsonify(res)

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)


@blueprint.route('/access-group/create', methods=['POST'])
@auth_required('View', 'Admin Dashboard')
@auth_required('Create', 'Access Groups')
def access_group_create():
    try:
        data = request.json['create']
        access_group = AccessGroup()

        populate_model(access_group, data)
        app = App.query.get(data['app'])
        access_group.app = app

        for entry in data['permissions']:
            action = entry['action']
            resource = entry['resource']
            q = Permission.definition == (action, resource)
            permission = Permission.query.filter(q).first()

            if permission is None:
                permission = Permission()
                permission.action = entry['action']
                permission.resource = entry['resource']

            JoinAccessGroupPermission(
                access_group=access_group,
                permission=permission
            )

        db.session.add(access_group)
        db.session.commit()
        msg = 'Access Group Created Successfully'

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)

    return jsonify({'msg': msg})


@blueprint.route('/access-group/edit', methods=['POST'])
@auth_required('View', 'Admin Dashboard')
@auth_required('Edit', 'Access Groups')
def access_group_edit():
    try:
        data = request.json['edit']
        access_group_id = request.json['id']
        access_group = AccessGroup.query.get(access_group_id)

        populate_model(access_group, data)

        if 'app' in data:
            app = App.query.get(data['app'])
            access_group.app = app

        if 'permissions' in data:
            access_group.permissions = []

            for entry in data['permissions']:
                action = entry['action']
                resource = entry['resource']
                q = Permission.definition == (action, resource)
                permission = Permission.query.filter(q).first()

                if permission is None:
                    permission = Permission()
                    permission.action = entry['action']
                    permission.resource = entry['resource']

                JoinAccessGroupPermission(
                    access_group=access_group,
                    permission=permission
                )

        db.session.commit()
        msg = 'Access Group Edited Successfully'

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)

    return jsonify({'msg': msg})


@blueprint.route('/access-group/archive', methods=['POST'])
@auth_required('View', 'Admin Dashboard')
@auth_required('Archive', 'Access Groups')
def access_group_archive():
    try:
        access_group_id = request.json['id']
        access_group = AccessGroup.query.get(access_group_id)
        access_group.is_archived = True
        db.session.commit()
        msg = 'Access Group Archived Successfully'

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)

    return jsonify({'msg': msg})


@blueprint.route('/role')
@auth_required('View', 'Admin Dashboard')
def role():
    try:
        i = request.args.get('id')

        if i:
            q = Role.query.filter(~Role.is_archived & Role.id == int(i))

        else:
            q = Role.query.filter(~Role.is_archived)

        res = [r.meta for r in q.all()]
        return jsonify(res)

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)


@blueprint.route('/role/create', methods=['POST'])
@auth_required('View', 'Admin Dashboard')
@auth_required('Create', 'Roles')
def role_create():
    try:
        data = request.json['create']
        role = Role()

        populate_model(role, data)

        for entry in data['permissions']:
            action = entry['action']
            resource = entry['resource']
            q = Permission.definition == (action, resource)
            permission = Permission.query.filter(q).first()

            if permission is None:
                permission = Permission()
                permission.action = entry['action']
                permission.resource = entry['resource']

            JoinRolePermission(role=role, permission=permission)

        db.session.add(role)
        db.session.commit()
        msg = 'Role Created Successfully'

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)

    return jsonify({'msg': msg})


@blueprint.route('/role/edit', methods=['POST'])
@auth_required('View', 'Admin Dashboard')
@auth_required('Edit', 'Roles')
def role_edit():
    try:
        data = request.json['edit']
        role_id = request.json['id']
        role = Role.query.get(role_id)

        populate_model(role, data)

        role.permissions = []
        for entry in data['permissions']:
            action = entry['action']
            resource = entry['resource']
            q = Permission.definition == (action, resource)
            permission = Permission.query.filter(q).first()

            if permission is None:
                permission = Permission()
                permission.action = entry['action']
                permission.resource = entry['resource']

            JoinRolePermission(role=role, permission=permission)

        db.session.add(role)
        db.session.commit()
        msg = 'Role Edited Successfully'

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)

    return jsonify({'msg': msg})


@blueprint.route('/role/archive', methods=['POST'])
@auth_required('View', 'Admin Dashboard')
@auth_required('Archive', 'Role')
def role_archive():  # TODO: create unit test
    try:
        role_id = request.json['id']
        role = Role.query.get(role_id)
        role.is_archived = True
        db.session.commit()
        msg = 'Role Archived Successfully'

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)

    return jsonify({'msg': msg})


@blueprint.route('/app')
@auth_required('View', 'Admin Dashboard')
def app():
    apps = App.query.all()
    res = [a.meta for a in apps]
    return jsonify(res)


@blueprint.route('/app/create', methods=['POST'])
@auth_required('View', 'Admin Dashboard')
@auth_required('Create', 'Apps')
def app_create():
    data = request.json['create']
    app = App()

    try:
        populate_model(app, data)
        db.session.add(app)
        db.session.commit()
        msg = 'App Created Successfully'

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)

    return jsonify({'msg': msg})


@blueprint.route('/app/edit', methods=['POST'])
@auth_required('View', 'Admin Dashboard')
@auth_required('Edit', 'Apps')
def app_edit():
    data = request.json['edit']
    app_id = request.json['id']
    app = App.query.get(app_id)

    try:
        populate_model(app, data)
        db.session.add(app)
        db.session.commit()
        msg = 'App Edited Successfully'

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)

    return jsonify({'msg': msg})


@blueprint.route('/action')
@auth_required('View', 'Admin Dashboard')
def action():  # TODO: write unit test
    try:
        actions = Action.query.all()
        res = [a.meta for a in actions]
        return jsonify(res)

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)


@blueprint.route('/resource')
@auth_required('View', 'Admin Dashboard')
def resource():  # TODO: write unit test
    try:
        resources = Resource.query.all()
        res = [r.meta for r in resources]
        return jsonify(res)

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({'msg': msg}, 500)
