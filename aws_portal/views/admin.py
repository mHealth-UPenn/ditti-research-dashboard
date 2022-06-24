from datetime import datetime
import traceback
import uuid
from flask import Blueprint, jsonify, request
from aws_portal.extensions import db
from aws_portal.models import (
    AccessGroup, Account, App, JoinAccessGroupPermission,
    JoinAccountAccessGroup, JoinRolePermission, Permission, Role, Study
)
from aws_portal.utils.auth import auth_required
from aws_portal.utils.db import populate_model

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
    data = request.json['create']
    account = Account()

    try:
        populate_model(account, data)
        account.public_id = str(uuid.uuid4())
        account.password = str(uuid.uuid4())
        account.created_on = datetime.utcnow()
        db.session.add(account)
        db.session.commit()
        msg = 'Account Created Successfully'

    except ValueError:
        msg = traceback.format_exc()
        db.session.rollback()

    return jsonify({'msg': msg})


@blueprint.route('/account/edit', methods=['POST'])
@auth_required('Edit', 'Account')
def account_edit():
    data = request.json['edit']
    account_id = request.json['id']
    account = Account.query.get(account_id)

    try:
        populate_model(account, data)
        db.session.commit()
        msg = 'Account Edited Successfully'

    except ValueError:
        msg = traceback.format_exc()
        db.session.rollback()

    return jsonify({'msg': msg})


@blueprint.route('/account/archive', methods=['POST'])
def account_archive():
    account_id = request.json['id']

    try:
        account = Account.query.get(account_id)
        account.is_archived = True
        db.session.commit()
        msg = 'Account Archived Successfully'

    except Exception:
        msg = traceback.format_exc()
        db.session.rollback()

    return jsonify({'msg': msg})


@blueprint.route('/study')
@auth_required('Read', 'Study')
def study():
    studies = Study.query.all()
    res = [s.meta for s in studies]
    return jsonify(res)


@blueprint.route('/study/create', methods=['POST'])
@auth_required('Create', 'Study')
def study_create():
    data = request.json['create']
    study = Study()

    try:
        populate_model(study, data)
        db.session.add(study)
        db.session.commit()
        msg = 'Study Created Successfully'

    except ValueError:
        msg = traceback.format_exc()
        db.session.rollback()

    return jsonify({'msg': msg})


@blueprint.route('/study/edit', methods=['POST'])
def study_edit():
    data = request.json['edit']
    study_id = request.json['id']
    study = Study.query.get(study_id)

    try:
        populate_model(study, data)
        db.session.commit()
        msg = 'Study Edited Successfully'

    except ValueError:
        msg = traceback.format_exc()
        db.session.rollback()

    return jsonify({'msg': msg})


@blueprint.route('/study/archive', methods=['POST'])
def study_archive():
    study_id = request.json['id']

    try:
        study = Study.query.get(study_id)
        study.is_archived = True
        db.session.commit()
        msg = 'Study Archived Successfully'

    except Exception:
        msg = traceback.format_exc()
        db.session.rollback()

    return jsonify({'msg': msg})


@blueprint.route('/access-group')
def access_group():
    access_groups = AccessGroup.query.all()
    res = [a.meta for a in access_groups]
    return jsonify(res)


@blueprint.route('/access-group/create', methods=['POST'])
def access_group_create():
    data = request.json['create']
    access_group = AccessGroup()

    try:
        populate_model(access_group, data)
        app = App.query.get(data['app'])
        access_group.app = app

        for entry in data['accounts']:
            account = Account.query.get(entry)
            JoinAccountAccessGroup(account=account, access_group=access_group)

        for entry in data['permissions']:
            permission = Permission()
            populate_model(permission, entry)
            JoinAccessGroupPermission(
                access_group=access_group,
                permission=permission
            )

        db.session.add(access_group)
        db.session.commit()
        msg = 'Access Group Created Successfully'

    except ValueError:
        msg = traceback.format_exc()
        db.session.rollback()

    return jsonify({'msg': msg})


@blueprint.route('/access-group/edit', methods=['POST'])
def access_group_edit():
    data = request.json['edit']
    access_group_id = request.json['id']
    access_group = AccessGroup.query.get(access_group_id)

    try:
        populate_model(access_group, data)

        if 'app' in data:
            app = App.query.get(data['app'])
            access_group.app = app

        if 'accounts' in data:
            for join in access_group.accounts:
                if join.account_id not in data['accounts']:
                    db.session.delete(join)

            ids = [j.account_id for j in access_group.accounts]
            for entry in data['accounts']:
                if entry not in ids:
                    account = Account.query.get(entry)
                    JoinAccountAccessGroup(
                        account=account,
                        access_group=access_group
                    )

        if 'permissions' in data:
            access_group.permissions = []

            for entry in data['permissions']:
                action = entry['action']
                resource = entry['resource']
                q = Permission.definition == (action, resource)
                permission = Permission.query.filter(q).first()

                if permission is None:
                    permission = Permission()
                    populate_model(permission, entry)

                JoinAccessGroupPermission(
                    access_group=access_group,
                    permission=permission
                )

        db.session.commit()
        msg = 'Access Group Edited Successfully'

    except ValueError:
        msg = traceback.format_exc()
        db.session.rollback()

    return jsonify({'msg': msg})


@blueprint.route('/access-group/archive', methods=['POST'])
def access_group_archive():
    access_group_id = request.json['id']

    try:
        access_group = AccessGroup.query.get(access_group_id)
        access_group.is_archived = True
        db.session.commit()
        msg = 'Access Group Archived Successfully'

    except Exception:
        msg = traceback.format_exc()
        db.session.rollback()

    return jsonify({'msg': msg})


@blueprint.route('/role')
def role():
    roles = Role.query.all()
    res = [r.meta for r in roles]
    return jsonify(res)


@blueprint.route('/role/create', methods=['POST'])
def role_create():
    data = request.json['create']
    role = Role()

    try:
        populate_model(role, data)

        for entry in data['permissions']:
            action = entry['action']
            resource = entry['resource']
            q = Permission.definition == (action, resource)
            permission = Permission.query.filter(q).first()

            if permission is None:
                permission = Permission()
                populate_model(permission, entry)

            JoinRolePermission(role=role, permission=permission)

        db.session.add(role)
        db.session.commit()
        msg = 'Role Created Successfully'

    except ValueError:
        msg = traceback.format_exc()
        db.session.rollback()

    return jsonify({'msg': msg})


@blueprint.route('/role/edit', methods=['POST'])
def role_edit():
    data = request.json['edit']
    role_id = request.json['id']
    role = Role.query.get(role_id)

    try:
        populate_model(role, data)

        role.permissions = []
        for entry in data['permissions']:
            action = entry['action']
            resource = entry['resource']
            q = Permission.definition == (action, resource)
            permission = Permission.query.filter(q).first()

            if permission is None:
                permission = Permission()
                populate_model(permission, entry)

            JoinRolePermission(role=role, permission=permission)

        db.session.add(role)
        db.session.commit()
        msg = 'Role Edited Successfully'

    except ValueError:
        msg = traceback.format_exc()
        db.session.rollback()

    return jsonify({'msg': msg})


@blueprint.route('/app')
def app():
    apps = App.query.all()
    res = [a.meta for a in apps]
    return jsonify(res)


@blueprint.route('/app/create', methods=['POST'])
def app_create():
    data = request.json['create']
    app = App()

    try:
        populate_model(app, data)
        db.session.add(app)
        db.session.commit()
        msg = 'App Created Successfully'

    except ValueError:
        msg = traceback.format_exc()
        db.session.rollback()

    return jsonify({'msg': msg})


@blueprint.route('/app/edit', methods=['POST'])
def app_edit():
    data = request.json['edit']
    app_id = request.json['id']
    app = App.query.get(app_id)

    try:
        populate_model(app, data)
        db.session.add(app)
        db.session.commit()
        msg = 'App Edited Successfully'

    except ValueError:
        msg = traceback.format_exc()
        db.session.rollback()

    return jsonify({'msg': msg})
