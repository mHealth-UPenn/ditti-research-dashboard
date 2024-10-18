from datetime import datetime, UTC
import logging
import traceback
import uuid
from flask import Blueprint, jsonify, make_response, request
from sqlalchemy import tuple_
from aws_portal.extensions import db
from aws_portal.models import (
    AboutSleepTemplate, AccessGroup, Account, Action, App, Api,
    JoinAccessGroupPermission, JoinAccountAccessGroup, JoinAccountStudy,
    JoinRolePermission, Permission, Resource, Role, Study, StudySubject,
    JoinStudySubjectStudy, JoinStudySubjectApi
)
from aws_portal.utils.auth import auth_required, validate_password
from aws_portal.utils.db import populate_model

blueprint = Blueprint("admin", __name__, url_prefix="/admin")
logger = logging.getLogger(__name__)


@blueprint.route("/account")
@auth_required("View", "Admin Dashboard")
def account():
    """
    Get one account or a list of all accounts. This will return one account if
    the account"s database primary key is passed as a URL option

    Options
    -------
    app: 1
    id: str

    Response syntax (200)
    ---------------------
    [
        {
            ...Account data
        },
        ...
    ]

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        i = request.args.get("id")

        if i:
            q = Account.query.filter(
                ~Account.is_archived & (Account.id == int(i))
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

        return make_response({"msg": msg}, 500)


@blueprint.route("/account/create", methods=["POST"])
@auth_required("View", "Admin Dashboard")
@auth_required("Create", "Accounts")
def account_create():
    """
    Create a new account.
    
    Request syntax
    --------------
    {
        app: 1,
        create: {
            ...Account data,
            access_groups: [
                {
                    id: int
                },
                ...
            ],
            studies: [
                {
                    id: int,
                    role: {
                        id: inte
                    }
                },
                ...
            ]
        }
    }

    Response syntax (200)
    ---------------------
    {
        msg: "Account Created Successfully"
    }

    Response syntax (400)
    ---------------------
    {
        msg: "A password was not provided" or
            "Minimum password length is 8 characters" or
            "Maximum password length is 64 characters"
    }

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        data = request.json["create"]
        password = data["password"]

        # a password must be included
        if not password:
            msg = "A password was not provided."
            return make_response({"msg": msg}, 400)

        # the password must be valid
        valid = validate_password(password)
        if valid != "valid":
            return make_response({"msg": valid}, 400)

        account = Account()

        populate_model(account, data)
        account.public_id = str(uuid.uuid4())
        account.created_on = datetime.now(UTC)

        # add access groups
        for entry in data["access_groups"]:
            access_group = AccessGroup.query.get(entry["id"])
            JoinAccountAccessGroup(access_group=access_group, account=account)

        # add studies
        for entry in data["studies"]:
            study = Study.query.get(entry["id"])
            role = Role.query.get(entry["role"]["id"])
            JoinAccountStudy(account=account, role=role, study=study)

        db.session.add(account)
        db.session.commit()
        msg = "Account Created Successfully"

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/account/edit", methods=["POST"])
@auth_required("View", "Admin Dashboard")
@auth_required("Edit", "Accounts")
def account_edit():
    """
    Edit an existing account
    
    Request syntax
    --------------
    {
        app: 1,
        id: int,
        edit: {
            ...Account data,
            access_groups: [
                {
                    id: int
                },
                ...
            ],
            studies: [
                {
                    id: int,
                    role: {
                        id: inte
                    }
                },
                ...
            ]
        }
    }

    All data in the request body are optional. Any attributes that are excluded
    from the request body will not be changed.

    Response syntax (200)
    ---------------------
    {
        msg: "Account Edited Successfully"
    }

    Response syntax (400)
    ---------------------
    {
        msg: "A password was not provided" or
            "Minimum password length is 8 characters" or
            "Maximum password length is 64 characters"
    }

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        data = request.json["edit"]
        account_id = request.json["id"]
        account = Account.query.get(account_id)

        try:
            password = data["password"]
            # avoid updating the account with an empty password
            if not password:
                del data["password"]
        except KeyError:
            pass

        # if there is a new password, it must be valid
        else:
            valid = validate_password(password)

            if valid != "valid":
                return make_response({"msg": valid}, 400)

        populate_model(account, data)

        # if a list of access groups were provided
        if "access_groups" in data:

            # remove access groups that are not in the new list
            for join in account.access_groups:
                a_ids = [a["id"] for a in data["access_groups"]]

                if join.access_group_id not in a_ids:
                    db.session.delete(join)

            # add new access groups
            a_ids = [join.access_group_id for join in account.access_groups]
            for entry in data["access_groups"]:
                if entry["id"] not in a_ids:
                    access_group = AccessGroup.query.get(entry["id"])
                    JoinAccountAccessGroup(
                        access_group=access_group,
                        account=account
                    )

        # if a list of studies were provided
        if "studies" in data:

            # remove studies that are not in the new list
            for join in account.studies:
                s_ids = [s["id"] for s in data["studies"]]

                if join.study_id not in s_ids:
                    db.session.delete(join)

            s_ids = [join.study_id for join in account.studies]
            for entry in data["studies"]:
                study = Study.query.get(entry["id"])

                # if the study is not new
                if entry["id"] in s_ids:
                    join = JoinAccountStudy.query.get((account.id, study.id))

                    # update the role
                    if join.role.id != int(entry["role"]["id"]):
                        join.role = Role.query.get(entry["role"]["id"])

                # add the study
                else:
                    role = Role.query.get(entry["role"]["id"])
                    JoinAccountStudy(account=account, role=role, study=study)

        db.session.commit()
        msg = "Account Edited Successfully"

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/account/archive", methods=["POST"])
@auth_required("View", "Admin Dashboard")
@auth_required("Archive", "Accounts")
def account_archive():
    """
    Archive an account. This action has the same effect as deleting an entry
    from the database. However, archived items are only filtered from queries
    and can be retrieved.

    Request syntax
    --------------
    {
        app: 1,
        id: int
    }

    Response syntax (200)
    ---------------------
    {
        msg: "Account Archived Successfully"
    }

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        account_id = request.json["id"]
        account = Account.query.get(account_id)
        account.is_archived = True
        db.session.commit()
        msg = "Account Archived Successfully"

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/study")
@auth_required("View", "Admin Dashboard")
def study():
    """
    Get one study or a list of all studies. This will return one study if the
    study"s database primary key is passed as a URL option

    Options
    -------
    app: 1
    id: str

    Response syntax (200)
    ---------------------
    [
        {
            ...Study data
        },
        ...
    ]

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        i = request.args.get("id")

        if i:
            q = Study.query.filter(~Study.is_archived & (Study.id == int(i)))

        else:
            q = Study.query.filter(~Study.is_archived)

        res = [s.meta for s in q.all()]
        return jsonify(res)

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)


@blueprint.route("/study/create", methods=["POST"])
@auth_required("View", "Admin Dashboard")
@auth_required("Create", "Studies")
def study_create():
    """
    Create a new study.
    
    Request syntax
    --------------
    {
        app: 1,
        create: {
            ...Study data
        }
    }

    Response syntax (200)
    ---------------------
    {
        msg: "Study Created Successfully"
    }

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        data = request.json["create"]
        study = Study()

        populate_model(study, data)
        db.session.add(study)
        db.session.commit()
        msg = "Study Created Successfully"

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/study/edit", methods=["POST"])
@auth_required("View", "Admin Dashboard")
@auth_required("Edit", "Studies")
def study_edit():
    """
    Edit an existing study
    
    Request syntax
    --------------
    {
        app: 1,
        id: int,
        edit: {
            ...Study data
        }
    }

    All data in the request body are optional. Any attributes that are excluded
    from the request body will not be changed.

    Response syntax (200)
    ---------------------
    {
        msg: "Study Edited Successfully"
    }

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        data = request.json["edit"]
        study_id = request.json["id"]
        study = Study.query.get(study_id)

        populate_model(study, data)
        db.session.commit()
        msg = "Study Edited Successfully"

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/study/archive", methods=["POST"])
@auth_required("View", "Admin Dashboard")
@auth_required("Archive", "Studies")
def study_archive():
    """
    Archive a study. This action has the same effect as deleting an entry
    from the database. However, archived items are only filtered from queries
    and can be retrieved.

    Request syntax
    --------------
    {
        app: 1,
        id: int
    }

    Response syntax (200)
    ---------------------
    {
        msg: "Study Archived Successfully"
    }

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        study_id = request.json["id"]
        study = Study.query.get(study_id)
        study.is_archived = True
        db.session.commit()
        msg = "Study Archived Successfully"

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/access-group")
@auth_required("View", "Admin Dashboard")
def access_group():
    """
    Get one access group or a list of all studies. This will return one access
    group if the access groups"s database primary key is passed as a URL option

    Options
    -------
    app: 1
    id: str

    Response syntax (200)
    ---------------------
    [
        {
            ...Access group data
        },
        ...
    ]

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        i = request.args.get("id")

        if i:
            q = AccessGroup.query.filter(
                ~AccessGroup.is_archived & (AccessGroup.id == int(i))
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

        return make_response({"msg": msg}, 500)


@blueprint.route("/access-group/create", methods=["POST"])
@auth_required("View", "Admin Dashboard")
@auth_required("Create", "Access Groups")
def access_group_create():
    """
    Create a new access group.
    
    Request syntax
    --------------
    {
        app: 1,
        create: {
            ...Access group data
            permissions: [
                {
                    action: str,
                    resource: str
                },
                ...
            ]
        }
    }

    Response syntax (200)
    ---------------------
    {
        msg: "Access Group Created Successfully"
    }

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        data = request.json["create"]
        access_group = AccessGroup()

        populate_model(access_group, data)
        app = App.query.get(data["app"])
        access_group.app = app

        # add permissions
        for entry in data["permissions"]:
            action = entry["action"]
            resource = entry["resource"]
            q = Permission.definition == tuple_(action, resource)
            permission = Permission.query.filter(q).first()

            # only create a permission if it does not already exist
            if permission is None:
                permission = Permission()
                permission.action = entry["action"]
                permission.resource = entry["resource"]

            JoinAccessGroupPermission(
                access_group=access_group,
                permission=permission
            )

        db.session.add(access_group)
        db.session.commit()
        msg = "Access Group Created Successfully"

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/access-group/edit", methods=["POST"])
@auth_required("View", "Admin Dashboard")
@auth_required("Edit", "Access Groups")
def access_group_edit():
    """
    Edit an existing access group.
    
    Request syntax
    --------------
    {
        app: 1,
        id: int,
        edit: {
            ...Access group data
            permissions: [
                {
                    action: str,
                    resource: str
                },
                ...
            ]
        }
    }

    All data in the request body are optional. Any attributes that are excluded
    from the request body will not be changed.

    Response syntax (200)
    ---------------------
    {
        msg: "Access Group Created Successfully"
    }

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        data = request.json["edit"]
        access_group_id = request.json["id"]
        access_group = AccessGroup.query.get(access_group_id)

        populate_model(access_group, data)

        # if a new app is provided
        if "app" in data:
            app = App.query.get(data["app"])
            access_group.app = app

        # if new permissions are provided
        if "permissions" in data:

            # remove all existing permissions without deleting them
            access_group.permissions = []

            for entry in data["permissions"]:
                action = entry["action"]
                resource = entry["resource"]
                q = Permission.definition == tuple_(action, resource)
                permission = Permission.query.filter(q).first()

                # only create a new permission if it doens"t already exist
                if permission is None:
                    permission = Permission()
                    permission.action = entry["action"]
                    permission.resource = entry["resource"]

                JoinAccessGroupPermission(
                    access_group=access_group,
                    permission=permission
                )

        db.session.commit()
        msg = "Access Group Edited Successfully"

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/access-group/archive", methods=["POST"])
@auth_required("View", "Admin Dashboard")
@auth_required("Archive", "Access Groups")
def access_group_archive():
    """
    Archive an access group. This action has the same effect as deleting an entry
    from the database. However, archived items are only filtered from queries
    and can be retrieved.

    Request syntax
    --------------
    {
        app: 1,
        id: int
    }

    Response syntax (200)
    ---------------------
    {
        msg: "Access Group Archived Successfully"
    }

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        access_group_id = request.json["id"]
        access_group = AccessGroup.query.get(access_group_id)
        access_group.is_archived = True
        db.session.commit()
        msg = "Access Group Archived Successfully"

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/role")
@auth_required("View", "Admin Dashboard")
def role():
    """
    Get one role or a list of all studies. This will return one role if the
    role"s database primary key is passed as a URL option

    Options
    -------
    app: 1
    id: str

    Response syntax (200)
    ---------------------
    [
        {
            ...Role data
        },
        ...
    ]

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        i = request.args.get("id")

        if i:
            q = Role.query.filter(~Role.is_archived & (Role.id == int(i)))

        else:
            q = Role.query.filter(~Role.is_archived)

        res = [r.meta for r in q.all()]
        return jsonify(res)

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)


@blueprint.route("/role/create", methods=["POST"])
@auth_required("View", "Admin Dashboard")
@auth_required("Create", "Roles")
def role_create():
    """
    Create a new role.
    
    Request syntax
    --------------
    {
        app: 1,
        create: {
            ...Role data,
            permissions: [
                {
                    action: str,
                    resource: str
                },
                ...
            ]
        }
    }

    Response syntax (200)
    ---------------------
    {
        msg: "Role Created Successfully"
    }

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        data = request.json["create"]
        role = Role()

        populate_model(role, data)

        # add permissions
        for entry in data["permissions"]:
            action = entry["action"]
            resource = entry["resource"]
            q = Permission.definition == tuple_(action, resource)
            permission = Permission.query.filter(q).first()

            # only create a permission if it does not already exist
            if permission is None:
                permission = Permission()
                permission.action = entry["action"]
                permission.resource = entry["resource"]

            JoinRolePermission(role=role, permission=permission)

        db.session.add(role)
        db.session.commit()
        msg = "Role Created Successfully"

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/role/edit", methods=["POST"])
@auth_required("View", "Admin Dashboard")
@auth_required("Edit", "Roles")
def role_edit():
    """
    Edit an existing role.
    
    Request syntax
    --------------
    {
        app: 1,
        id: int,
        edit: {
            ...Role data,
            permissions: [
                {
                    action: str,
                    resource: str
                },
                ...
            ]
        }
    }

    Permissions are required and other data is optional. If no permissions are
    provided, then the role will be updated with no permissions

    Response syntax (200)
    ---------------------
    {
        msg: "Role Edited Successfully"
    }

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        data = request.json["edit"]
        role_id = request.json["id"]
        role = Role.query.get(role_id)

        populate_model(role, data)

        # remove all existing permissions without deleting them
        role.permissions = []

        # add permissions
        for entry in data["permissions"]:
            action = entry["action"]
            resource = entry["resource"]
            q = Permission.definition == tuple_(action, resource)
            permission = Permission.query.filter(q).first()

            # only create a permission if it does not already exist
            if permission is None:
                permission = Permission()
                permission.action = entry["action"]
                permission.resource = entry["resource"]

            JoinRolePermission(role=role, permission=permission)

        db.session.add(role)
        db.session.commit()
        msg = "Role Edited Successfully"

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/role/archive", methods=["POST"])
@auth_required("View", "Admin Dashboard")
@auth_required("Archive", "Role")
def role_archive():  # TODO: create unit test
    """
    Archive a role. This action has the same effect as deleting an entry
    from the database. However, archived items are only filtered from queries
    and can be retrieved.

    Request syntax
    --------------
    {
        app: 1,
        id: int
    }

    Response syntax (200)
    ---------------------
    {
        msg: "Role Archived Successfully"
    }

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        role_id = request.json["id"]
        role = Role.query.get(role_id)
        role.is_archived = True
        db.session.commit()
        msg = "Role Archived Successfully"

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/app")
@auth_required("View", "Admin Dashboard")
def app():
    apps = App.query.all()
    res = [a.meta for a in apps]
    return jsonify(res)


@blueprint.route("/app/create", methods=["POST"])
@auth_required("View", "Admin Dashboard")
@auth_required("Create", "Apps")
def app_create():
    data = request.json["create"]
    app = App()

    try:
        populate_model(app, data)
        db.session.add(app)
        db.session.commit()
        msg = "App Created Successfully"

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/app/edit", methods=["POST"])
@auth_required("View", "Admin Dashboard")
@auth_required("Edit", "Apps")
def app_edit():
    data = request.json["edit"]
    app_id = request.json["id"]
    app = App.query.get(app_id)

    try:
        populate_model(app, data)
        db.session.add(app)
        db.session.commit()
        msg = "App Edited Successfully"

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/action")
@auth_required("View", "Admin Dashboard")
def action():  # TODO: write unit test
    """
    Get all actions

    Response syntax (200)
    ---------------------
    [
        {
            ...Action data
        },
        ...
    ]

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        actions = Action.query.all()
        res = [a.meta for a in actions]
        return jsonify(res)

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)


@blueprint.route("/resource")
@auth_required("View", "Admin Dashboard")
def resource():  # TODO: write unit test
    """
    Get all resources

    Response syntax (200)
    ---------------------
    [
        {
            ...Resource data
        },
        ...
    ]

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        resources = Resource.query.all()
        res = [r.meta for r in resources]
        return jsonify(res)

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)


@blueprint.route("/about-sleep-template")
@auth_required("View", "Admin Dashboard")
def about_sleep_template():
    """
    Get one about sleep template or a list of all studies. This will return one
    about sleep template if the about sleep template"s database primary key is
    passed as a URL option

    Options
    -------
    app: 1
    id: str

    Response syntax (200)
    ---------------------
    [
        {
            ...About Sleep Template data
        },
        ...
    ]

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        i = request.args.get("id")

        if i:
            q = AboutSleepTemplate.query.filter(
              ~AboutSleepTemplate.is_archived &
              (AboutSleepTemplate.id == int(i))
            )

        else:
            q = AboutSleepTemplate.query.filter(
              ~AboutSleepTemplate.is_archived
            )

        res = [s.meta for s in q.all()]
        return jsonify(res)

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)


@blueprint.route("/about-sleep-template/create", methods=["POST"])
@auth_required("View", "Admin Dashboard")
@auth_required("Create", "Studies")
def about_sleep_template_create():
    """
    Create a new about sleep template.
    
    Request syntax
    --------------
    {
        app: 1,
        create: {
            ...About sleep template data
        }
    }

    Response syntax (200)
    ---------------------
    {
        msg: "About sleep template Created Successfully"
    }

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        data = request.json["create"]
        about_sleep_template = AboutSleepTemplate()

        populate_model(about_sleep_template, data)
        db.session.add(about_sleep_template)
        db.session.commit()
        msg = "About sleep template Created Successfully"

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/about-sleep-template/edit", methods=["POST"])
@auth_required("View", "Admin Dashboard")
@auth_required("Edit", "Studies")
def about_sleep_template_edit():
    """
    Edit an existing about sleep template
    
    Request syntax
    --------------
    {
        app: 1,
        id: int,
        edit: {
            ...About sleep template data
        }
    }

    All data in the request body are optional. Any attributes that are excluded
    from the request body will not be changed.

    Response syntax (200)
    ---------------------
    {
        msg: "About sleep template Edited Successfully"
    }

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        data = request.json["edit"]
        about_sleep_template_id = request.json["id"]
        about_sleep_template = AboutSleepTemplate.query.get(
          about_sleep_template_id
        )

        populate_model(about_sleep_template, data)
        db.session.commit()
        msg = "About sleep template Edited Successfully"

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/about-sleep-template/archive", methods=["POST"])
@auth_required("View", "Admin Dashboard")
@auth_required("Archive", "Studies")
def about_sleep_template_archive():
    """
    Archive an about sleep template. This action has the same effect as
    deleting an entry from the database. However, archived items are only
    filtered from queries and can be retrieved.

    Request syntax
    --------------
    {
        app: 1,
        id: int
    }

    Response syntax (200)
    ---------------------
    {
        msg: "About sleep template Archived Successfully"
    }

    Response syntax (500)
    ---------------------
    {
        msg: a formatted traceback if an uncaught error was thrown
    }
    """
    try:
        about_sleep_template_id = request.json["id"]
        about_sleep_template = AboutSleepTemplate.query.get(
          about_sleep_template_id
        )
        about_sleep_template.is_archived = True
        db.session.commit()
        msg = "About sleep template Archived Successfully"

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warn(exc)
        db.session.rollback()

        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg})

@blueprint.route("/study_subject/create", methods=["POST"])
@auth_required("View", "Admin Dashboard")
@auth_required("Create", "Study Subjects")
def study_subject_create():
    """
    Create a new study subject.

    Request syntax
    --------------
    {
        app: 1,
        create: {
            email: str,
            studies: [
                { 
                    id: int,
                    expires_o": str,
                    did_consent: bool
                },
                ...
            ],
            apis: [
                {
                    id: int,
                    api_user_uuid: str,
                    scope: str[],
                    access_key_uuid: str,
                    refresh_key_uuid: str
                },
                ...
            ]
        }
    }

    Response syntax (200)
    ---------------------
    {
        msg: "Study Subject Created Successfully"
    }

    Response syntax (400)
    ---------------------
    {
        msg:    "Email was not provided" or
                "Email already exists" or
                "Invalid study ID: X" or
                "Invalid API ID: Y" or
                "Invalid date format for expires_on: YYYY-MM-DDTHH:MM:SSZ"
    }

    Response syntax (500)
    ---------------------
    {
        msg: "Internal server error message"
    }
    """
    try:
        data = request.json.get("create")
        if not data:
            return make_response({"msg": "No data provided"}, 400)

        email = data.get("email")
        if not email:
            return make_response({"msg": "Email was not provided"}, 400)

        if StudySubject.query.filter(StudySubject.email == email).first():
            return make_response({"msg": "Email already exists"}, 400)

        # Initialize StudySubject instance
        study_subject = StudySubject()
        
        # Populate non-relationship fields using populate_model
        populate_model(study_subject, data)

        # Set default values if not provided
        study_subject.created_on = datetime.now(UTC)
        study_subject.is_confirmed = False
        study_subject.is_archived = False

        # Add study associations
        studies_data = data.get("studies", [])
        for study_entry in studies_data:
            study_id = study_entry.get("id")
            if not study_id:
                return make_response({"msg": "Study ID is required in studies"}, 400)
            study = Study.query.get(study_id)
            if study is None:
                return make_response({"msg": f"Invalid study ID: {study_id}"}, 400)
            if study.is_archived:
                return make_response({"msg": f"Cannot associate with archived study ID: {study_id}"}, 400)

            did_consent = study_entry.get("did_consent", False)
            expires_on_str = study_entry.get("expires_on")
            if not expires_on_str:
                return make_response({"msg": f"'expires_on' is required for study ID {study_id}"}, 400)
            try:
                expires_on = datetime.fromisoformat(expires_on_str.replace("Z", "+00:00"))
            except ValueError:
                return make_response({"msg": f"Invalid date format for expires_on: {expires_on_str}"}, 400)

            join_study = JoinStudySubjectStudy(
                study_subject=study_subject,
                study=study,
                did_consent=did_consent,
                expires_on=expires_on
            )
            db.session.add(join_study)

        # Add API associations
        apis_data = data.get("apis", [])
        for api_entry in apis_data:
            api_id = api_entry.get("id")
            if not api_id:
                return make_response({"msg": "API ID is required in apis"}, 400)
            api = Api.query.get(api_id)
            if api is None:
                return make_response({"msg": f"Invalid API ID: {api_id}"}, 400)
            if api.is_archived:
                return make_response({"msg": f"Cannot associate with archived API ID: {api_id}"}, 400)

            api_user_uuid = api_entry.get("api_user_uuid")
            if not api_user_uuid:
                return make_response({"msg": f"'api_user_uuid' is required in apis {api_id}"}, 400)
            scope = api_entry.get("scope", [])
            access_key_uuid = api_entry.get("access_key_uuid")
            refresh_key_uuid = api_entry.get("refresh_key_uuid")

            join_api = JoinStudySubjectApi(
                study_subject=study_subject,
                api=api,
                api_user_uuid=api_user_uuid,
                scope=scope,
                access_key_uuid=access_key_uuid,
                refresh_key_uuid=refresh_key_uuid
            )
            db.session.add(join_api)

        db.session.add(study_subject)
        db.session.commit()

        return jsonify({"msg": "Study Subject Created Successfully"}), 200

    # Other server errors return 500
    except Exception as e:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warning(exc)
        db.session.rollback()
        return make_response({"msg": msg}, 500)

@blueprint.route("/study_subject/archive", methods=["POST"])
@auth_required("View", "Admin Dashboard")
@auth_required("Archive", "Study Subjects")
def study_subject_archive():
    """
    Archive a study subject.

    Request syntax
    --------------
    {
        app: int,
        id: int
    }

    Response syntax (200)
    ---------------------
    {
        msg: "Study Subject Archived Successfully"
    }

    Response syntax (400)
    ---------------------
    {
        msg:    "Study Subject ID not provided" or
                "Study Subject with ID X does not exist"
    }

    Response syntax (500)
    ---------------------
    {
        msg: "Internal server error message"
    }
    """
    try:
        study_subject_id = request.json.get("id")
        if not study_subject_id:
            return make_response({"msg": "Study Subject ID not provided"}, 400)

        study_subject = StudySubject.query.get(study_subject_id)
        if study_subject is None:
            return make_response({"msg": f"Study Subject with ID {study_subject_id} does not exist"}, 400)

        study_subject.is_archived = True
        db.session.commit()
        msg = "Study Subject Archived Successfully"

    except Exception:
        exc = traceback.format_exc()
        msg = exc.splitlines()[-1]
        logger.warning(exc)
        db.session.rollback()
        return make_response({"msg": msg}, 500)

    return jsonify({"msg": msg}), 200