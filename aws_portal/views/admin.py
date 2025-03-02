from datetime import datetime, UTC
import logging
import traceback
import uuid

from flask import Blueprint, jsonify, make_response, request
from sqlalchemy import tuple_

from aws_portal.extensions import db, sanitizer
from aws_portal.models import (
    AboutSleepTemplate,
    Account,
    App,
    Api,
    JoinStudySubjectApi,
    JoinStudySubjectStudy,
    Study,
    StudySubject,
)
from aws_portal.rbac.api import rbac_required
from aws_portal.rbac.models import (
    AppPermission,
    AppRole,
    JoinAccountAppRole,
    JoinAccountStudy,
    JoinAppRolePermission,
    JoinStudyRolePermission,
    StudyPermission,
    StudyRole
)
from aws_portal.utils.db import populate_model

blueprint = Blueprint("admin", __name__, url_prefix="/admin")
logger = logging.getLogger(__name__)


@blueprint.route("/account")
@rbac_required("AdminGetAccount")
def account():
    """
    Get one account or a list of all accounts. This will return one account if
    the account's database primary key is passed as a URL option

    Options
    -------
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
        msg: "Internal server error when retriving accounts"
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
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when retriving accounts"}, 500)


@blueprint.route("/account/create", methods=["POST"])
@rbac_required("AdminCreateAccount")
def account_create():
    """
    Create a new account.

    Request syntax
    --------------
    {
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
                        id: int
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
        msg: "Internal server error when creating account."
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
        if len(password) < 8:
            return make_response({"msg": "Minimum password length is 8 characters"}, 400)

        account = Account()

        populate_model(account, data)
        account.public_id = str(uuid.uuid4())
        account.created_on = datetime.now(UTC)

        # Add app roles
        for entry in data.get("app_roles", []):
            db.session.add(JoinAccountAppRole(
                account_id=account.id,
                app_role_id=int(entry["id"]),
            ))

        # Add studies
        for entry in data.get("studies", []):
            db.session.add(JoinAccountStudy(
                account_id=account.id,
                study_id=int(entry["study_id"]),
                role_id=int(entry["role_id"]),
            ))

        db.session.add(account)
        db.session.commit()
        msg = "Account Created Successfully"

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when creating account."}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/account/edit", methods=["POST"])
@rbac_required("AdminEditAccount")
def account_edit():
    """
    Edit an existing account

    Request syntax
    --------------
    {
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
                        id: int
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
        msg: "Internal server error when updating account."
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
            if len(password) < 8:
                return make_response({"msg": "Minimum password length is 8 characters"}, 400)

        populate_model(account, data)

        # If a list of app roles were provided
        if "app_roles" in data:
            old_ids = set(join.app_role_id for join in account.app_roles)
            new_ids = set(int(entry["id"]) for entry in data["app_roles"])
            ids_to_remove = old_ids - new_ids
            ids_to_add = new_ids - old_ids

            for join in account.app_roles:
                if join.app_role_id in ids_to_remove:
                    db.session.delete(join)

            for app_role_id in ids_to_add:
                db.session.add(JoinAccountAppRole(
                    account_id=account.id,
                    app_role_id=app_role_id,
                ))

        # If a list of studies were provided
        if "studies" in data:
            old_ids = set((join.study_id, join.role_id) for join in account.studies)
            new_ids = set((int(entry["study_id"]), int(entry["role_id"])) for entry in data["studies"])
            ids_to_remove = old_ids - new_ids
            ids_to_add = new_ids - old_ids

            for join in account.studies:
                if (join.study_id, join.role_id) in ids_to_remove:
                    db.session.delete(join)

            for study_id, role_id in ids_to_add:
                db.session.add(JoinAccountStudy(
                    account_id=account.id,
                    study_id=study_id,
                    role_id=role_id,
                ))

        db.session.commit()
        msg = "Account Edited Successfully"

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when updating account."}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/account/archive", methods=["POST"])
@rbac_required("AdminArchiveAccount")
def account_archive():
    """
    Archive an account. This action has the same effect as deleting an entry
    from the database. However, archived items are only filtered from queries
    and can be retrieved.

    Request syntax
    --------------
    {
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
        msg: "Internal server error when archiving account."
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
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when archiving account."}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/study")
@rbac_required("AdminGetStudy")
def study():
    """
    Get one study or a list of all studies. This will return one study if the
    study's database primary key is passed as a URL option

    Options
    -------
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
        msg: "Internal server error when retrieving studies."
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
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when retrieving studies."}, 500)


@blueprint.route("/study/create", methods=["POST"])
@rbac_required("AdminCreateStudy")
def study_create():
    """
    Create a new study.

    Request syntax
    --------------
    {
        create: {
            name: str,
            acronym: str,
            ditti_id: str,
            email: str,
            default_expiry_delta: int,
            consent_information: str (optional),
            data_summary: str (optional),
            is_qi: bool (optional)
        }
    }

    Response syntax (200)
    ---------------------
    {
        msg: "Study Created Successfully"
    }

    Response syntax (400)
    ---------------------
    {
        msg: "default_expiry_delta was not provided" or other validation errors
    }

    Response syntax (500)
    ---------------------
    {
        msg: "Internal server error when creating study."
    }
    """
    try:
        data = request.json.get("create")
        if not data:
            return make_response({"msg": "No data provided"}, 400)

        if "defaultExpiryDelta" not in data:
            return make_response({"msg": "defaultExpiryDelta was not provided"}, 400)

        study = Study()

        # Ensure `consent_summary` and `data_summary` HTML are sanitized
        try:
            study.consent_information = sanitizer.sanitize(data["consentInformation"])
            del data["consentInformation"]
        except KeyError:
            pass
        try:
            study.data_summary = sanitizer.sanitize(data["dataSummary"])
            del data["dataSummary"]
        except KeyError:
            pass

        populate_model(study, data, use_camel_to_snake=True)
        db.session.add(study)
        db.session.commit()
        msg = "Study Created Successfully"

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when creating study."}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/study/edit", methods=["POST"])
@rbac_required("AdminEditStudy")
def study_edit():
    """
    Edit an existing study

    Request syntax
    --------------
    {
        id: int,
        edit: {
            name: str,
            acronym: str,
            dittiId: str,
            email: str,
            defaultExpiryDelta: int (optional),
            consentInformation: str (optional),
            dataSummary: str (optional),
            isQi: bool (optional)
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
        msg: "Internal server error when updating study."
    }
    """
    try:
        data = request.json["edit"]
        study_id = request.json["id"]
        study = Study.query.get(study_id)

        # Ensure `consent_summary` and `data_summary` HTML are sanitized
        try:
            study.consent_information = sanitizer.sanitize(data["consentInformation"])
            del data["consentInformation"]
        except KeyError:
            pass
        try:
            study.data_summary = sanitizer.sanitize(data["dataSummary"])
            del data["dataSummary"]
        except KeyError:
            pass

        populate_model(study, data, use_camel_to_snake=True)
        db.session.commit()
        msg = "Study Edited Successfully"

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when updating study."}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/study/archive", methods=["POST"])
@rbac_required("AdminArchiveStudy")
def study_archive():
    """
    Archive a study. This action has the same effect as deleting an entry
    from the database. However, archived items are only filtered from queries
    and can be retrieved.

    Request syntax
    --------------
    {
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
        msg: "Internal server error when archiving study."
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
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when archiving study."}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/role")
@rbac_required("AdminGetRole")
def role():
    """
    Get one role or a list of all studies. This will return one role if the
    role's database primary key is passed as a URL option

    Options
    -------
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
        msg: "Internal server error when retrieving roles."
    }
    """
    try:
        i = request.args.get("id")
        role_type = request.args.get("type")
        table = AppRole if role_type == "app" else StudyRole

        if i:
            q = table.query.filter(~table.is_archived & (table.id == int(i)))

        else:
            q = table.query.filter(~table.is_archived)

        res = [r.meta for r in q.all()]
        return jsonify(res)

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when retrieving roles."}, 500)


@blueprint.route("/role/create", methods=["POST"])
@rbac_required("AdminCreateRole")
def role_create():
    """
    Create a new role.

    Request syntax
    --------------
    {
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
        msg: "Internal server error when creating role."
    }
    """
    try:
        data = request.json["create"]
        role_table = AppRole if data["type"] == "app" else StudyRole
        perm_table = AppPermission if data["type"] == "app" else StudyPermission
        join_table = JoinAppRolePermission if data["type"] == "app" \
            else JoinStudyRolePermission
        role = role_table()

        populate_model(role, data)

        # add permissions
        for entry in data["permissions"]:
            action = entry["action"]
            resource = entry["resource"]
            q = perm_table.definition == tuple_(action, resource)
            permission = perm_table.query.filter(q).first()

            # only create a permission if it does not already exist
            if permission is None:
                permission = perm_table()
                permission.action = entry["action"]
                permission.resource = entry["resource"]

            join_table(role=role, permission=permission)

        db.session.add(role)
        db.session.commit()
        msg = "Role Created Successfully"

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when creating role."}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/role/edit", methods=["POST"])
@rbac_required("AdminEditRole")
def role_edit():
    """
    Edit an existing role.

    Request syntax
    --------------
    {
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
        msg: "Internal server error when updating role."
    }
    """
    try:
        data = request.json["edit"]
        role_id = request.json["id"]
        role_table = AppRole if data["type"] == "app" else StudyRole
        perm_table = AppPermission if data["type"] == "app" else StudyPermission
        join_table = JoinAppRolePermission if data["type"] == "app" \
            else JoinStudyRolePermission
        role = role_table.query.get(role_id)

        populate_model(role, data)

        # remove all existing permissions without deleting them
        role.permissions = []

        # add permissions
        for entry in data["permissions"]:
            action = entry["action"]
            resource = entry["resource"]
            q = perm_table.definition == tuple_(action, resource)
            permission = perm_table.query.filter(q).first()

            # only create a permission if it does not already exist
            if permission is None:
                permission = perm_table()
                permission.action = entry["action"]
                permission.resource = entry["resource"]

            join_table(role=role, permission=permission)

        db.session.add(role)
        db.session.commit()
        msg = "Role Edited Successfully"

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when updating role."}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/role/archive", methods=["POST"])
@rbac_required("AdminArchiveRole")
def role_archive():
    """
    Archive a role. This action has the same effect as deleting an entry
    from the database. However, archived items are only filtered from queries
    and can be retrieved.

    Request syntax
    --------------
    {
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
        msg: "Internal server error when archiving role."
    }
    """
    try:
        role_id = request.json["id"]
        table = AppRole if request.json["type"] == "app" else StudyRole
        role = table.query.get(role_id)
        role.is_archived = True
        db.session.commit()
        msg = "Role Archived Successfully"

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when archiving role."}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/about-sleep-template")
@rbac_required("AdminGetAboutSleepTemplate")
def about_sleep_template():
    """
    Get one about sleep template or a list of all studies. This will return one
    about sleep template if the about sleep template"s database primary key is
    passed as a URL option

    Options
    -------
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
        msg: "Internal server error when retrieving about sleep templates."
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
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when retrieving about sleep templates."}, 500)


@blueprint.route("/about-sleep-template/create", methods=["POST"])
@rbac_required("AdminCreateAboutSleepTemplate")
def about_sleep_template_create():
    """
    Create a new about sleep template.

    Request syntax
    --------------
    {
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
        msg: "Internal server error when creating about sleep template."
    }
    """
    try:
        data = request.json["create"]
        about_sleep_template = AboutSleepTemplate()

        data["text"] = sanitizer.sanitize(data["text"])
        populate_model(about_sleep_template, data)
        db.session.add(about_sleep_template)
        db.session.commit()
        msg = "About sleep template Created Successfully"

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when creating about sleep template."}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/about-sleep-template/edit", methods=["POST"])
@rbac_required("AdminEditAboutSleepTemplate")
def about_sleep_template_edit():
    """
    Edit an existing about sleep template

    Request syntax
    --------------
    {
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
        msg: "Internal server error when updating about sleep template."
    }
    """
    try:
        data = request.json["edit"]
        about_sleep_template_id = request.json["id"]
        about_sleep_template = AboutSleepTemplate.query.get(
            about_sleep_template_id
        )

        try:
            data["text"] = sanitizer.sanitize(data["text"])
        except KeyError:
            pass

        populate_model(about_sleep_template, data)
        db.session.commit()
        msg = "About sleep template Edited Successfully"

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when updating about sleep template."}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/about-sleep-template/archive", methods=["POST"])
@rbac_required("AdminArchiveAboutSleepTemplate")
def about_sleep_template_archive():
    """
    Archive an about sleep template. This action has the same effect as
    deleting an entry from the database. However, archived items are only
    filtered from queries and can be retrieved.

    Request syntax
    --------------
    {
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
        msg: "Internal server error when archiving about sleep template."
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
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when archiving about sleep template."}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/study_subject")
@rbac_required("GetParticipant")
def study_subject():
    """
    Get one study subject or a list of all study subjects. This will return one
    study subject if the study subject's database primary key is passed as a URL option.

    Options
    -------
    id: str

    Response syntax (200)
    ---------------------
    [
        {
            ...Study Subject data
        },
        ...
    ]

    Response syntax (500)
    ---------------------
    {
        msg: "Internal server error when retrieving study subjects"
    }
    """
    try:
        # Retrieve the 'id' parameter from the query string
        study_subject_id = request.args.get("id")

        if study_subject_id:
            # Attempt to convert 'id' to integer
            try:
                study_subject_id = int(study_subject_id)
            except ValueError:
                return make_response({"msg": "Invalid ID format. ID must be an integer."}, 400)

            # Query for the specific StudySubject, excluding archived entries
            query = StudySubject.query.filter(
                ~StudySubject.is_archived & (
                    StudySubject.id == study_subject_id)
            )
        else:
            # Query for all non-archived StudySubjects
            query = StudySubject.query.filter(~StudySubject.is_archived)

        # Execute the query and serialize the results
        res = [a.meta for a in query.all()]
        return jsonify(res)

    except Exception:
        # Capture and log the traceback
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when retrieving study subjects"}, 500)


@blueprint.route("/study_subject/create", methods=["POST"])
@rbac_required("CreateParticipant")
def study_subject_create():
    """
    Create a new study subject.

    Request syntax
    --------------
    {
        create: {
            ditti_id: str,
            studies: [
                {
                    id: int,
                    starts_on: str (optional),
                    expires_on: str (optional),
                    did_consent: bool
                },
                ...
            ],
            apis: [
                {
                    id: int,
                    api_user_uuid: str,
                    scope: str[]
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
        msg:    "ditti_id was not provided" or
                "ditti_id already exists" or
                "Invalid study ID: X" or
                "Invalid API ID: Y" or
                "Invalid date format for expires_on: YYYY-MM-DDTHH:MM:SSZ"
    }

    Response syntax (500)
    ---------------------
    {
        msg: "Internal server error when creating study subject"
    }
    """
    try:
        data = request.json.get("create")
        if not data:
            return make_response({"msg": "No data provided"}, 400)

        ditti_id = data.get("ditti_id")
        if not ditti_id:
            return make_response({"msg": "ditti_id was not provided"}, 400)

        if StudySubject.query.filter(StudySubject.ditti_id == ditti_id).first():
            return make_response({"msg": "ditti_id already exists"}, 400)

        # Initialize StudySubject instance
        study_subject = StudySubject()

        # Populate non-relationship fields using populate_model
        populate_model(study_subject, {"ditti_id": ditti_id})

        # Set default values if not provided
        study_subject.created_on = datetime.now(UTC)
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
            if expires_on_str:
                try:
                    expires_on = datetime.fromisoformat(
                        expires_on_str.replace("Z", "+00:00"))
                except ValueError:
                    return make_response({"msg": f"Invalid date format for expires_on: {expires_on_str}"}, 400)
            else:
                expires_on = None  # Let the event listener set it

            join_study = JoinStudySubjectStudy(
                study_subject=study_subject,
                study=study,
                did_consent=did_consent,
                starts_on=study_entry.get("starts_on"),
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
                return make_response({"msg": f"'api_user_uuid' is required for API ID {api_id}"}, 400)
            scope = api_entry.get("scope", [])
            if isinstance(scope, str):
                scope = [scope]
            elif not isinstance(scope, list):
                scope = []

            join_api = JoinStudySubjectApi(
                study_subject=study_subject,
                api=api,
                api_user_uuid=api_user_uuid,
                scope=scope
            )
            db.session.add(join_api)

        db.session.add(study_subject)
        db.session.commit()

        return jsonify({"msg": "Study Subject Created Successfully"}), 200

    except Exception as e:
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()
        return make_response({"msg": "Internal server error when creating study subject"}, 500)


@blueprint.route("/study_subject/archive", methods=["POST"])
@rbac_required("ArchiveParticipant")
def study_subject_archive():
    """
    Archive a study subject.

    Request syntax
    --------------
    {
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
        msg: "Internal server error when archiving study subject"
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
        logger.warning(exc)
        db.session.rollback()
        return make_response({"msg": "Internal server error when archiving study subject"}, 500)

    return jsonify({"msg": msg}), 200


@blueprint.route("/study_subject/edit", methods=["POST"])
@rbac_required("EditParticipant")
def study_subject_edit():
    """
    Edit an existing study subject

    Request syntax
    --------------
    {
        id: int,
        edit: {
            ditti_id: str,  # Optional
            studies: [
                {
                    id: int,
                    expires_on: str (optional),
                    did_consent: bool
                },
                ...
            ],
            apis: [
                {
                    id: int,
                    api_user_uuid: str,
                    scope: str[]
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
        msg: "Study Subject Edited Successfully"
    }

    Response syntax (400)
    ---------------------
    {
        msg: "Study Subject with ID X does not exist" or
             "ditti_id already exists" or
             "Invalid study ID: Y" or
             "Invalid API ID: Z" or
             "Invalid date format for expires_on: YYYY-MM-DDTHH:MM:SSZ"
    }

    Response syntax (500)
    ---------------------
    {
        msg: "Internal server error when editing study subject"
    }
    """
    try:
        data = request.json.get("edit")
        study_subject_id = request.json.get("id")

        if not study_subject_id:
            return make_response({"msg": "Study Subject ID not provided"}, 400)

        study_subject = StudySubject.query.get(study_subject_id)
        if not study_subject:
            return make_response({"msg": f"Study Subject with ID {study_subject_id} does not exist"}, 400)

        # Update ditti_id if provided
        if data and "ditti_id" in data:
            new_ditti_id = data["ditti_id"]
            if new_ditti_id != study_subject.ditti_id:
                if StudySubject.query.filter(StudySubject.ditti_id == new_ditti_id, StudySubject.id != study_subject_id).first():
                    return make_response({"msg": "ditti_id already exists"}, 400)
                study_subject.ditti_id = new_ditti_id

        # Update other non-relationship fields using populate_model
        if data:
            populate_model(study_subject, data)

        # Update studies if provided
        if data and "studies" in data:
            # Remove studies not in the new list
            try:
                new_study_ids = [s["id"] for s in data["studies"]]
            except KeyError:
                return make_response({"msg": "Study ID is required in studies"}, 400)
            for join in list(study_subject.studies):
                if join.study_id not in new_study_ids:
                    db.session.delete(join)

            # Add or update studies
            for study_entry in data["studies"]:
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
                if expires_on_str:
                    try:
                        expires_on = datetime.fromisoformat(
                            expires_on_str.replace("Z", "+00:00"))
                    except ValueError:
                        return make_response({"msg": f"Invalid date format for expires_on: {expires_on_str}"}, 400)
                else:
                    expires_on = None  # Let the event listener set it

                starts_on_str = study_entry.get("starts_on")
                if starts_on_str:
                    try:
                        starts_on = datetime.fromisoformat(
                            starts_on_str.replace("Z", "+00:00"))
                    except ValueError:
                        return make_response({"msg": f"Invalid date format for starts_on: {starts_on_str}"}, 400)

                join = JoinStudySubjectStudy.query.get(
                    (study_subject_id, study_id))
                if join:
                    # Update existing association
                    join.did_consent = did_consent
                    join.expires_on = expires_on
                    join.starts_on = starts_on
                else:
                    # Create new association
                    new_join = JoinStudySubjectStudy(
                        study_subject=study_subject,
                        study=study,
                        did_consent=did_consent,
                        expires_on=expires_on,
                        starts_on=starts_on,
                    )
                    db.session.add(new_join)

        # Update APIs if provided
        if data and "apis" in data:
            # Remove APIs not in the new list
            try:
                new_api_ids = [a["id"] for a in data["apis"]]
            except KeyError:
                return make_response({"msg": "API ID is required in apis"}, 400)
            for join in list(study_subject.apis):
                if join.api_id not in new_api_ids:
                    db.session.delete(join)

            # Add or update APIs
            for api_entry in data["apis"]:
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
                    return make_response({"msg": f"'api_user_uuid' is required for API ID {api_id}"}, 400)
                scope = api_entry.get("scope", [])
                if isinstance(scope, str):
                    scope = [scope]
                elif not isinstance(scope, list):
                    scope = []

                join_api = JoinStudySubjectApi.query.get(
                    (study_subject_id, api_id))
                if join_api:
                    # Update existing association
                    join_api.api_user_uuid = api_user_uuid
                    join_api.scope = scope
                else:
                    # Create new association
                    new_join_api = JoinStudySubjectApi(
                        study_subject=study_subject,
                        api=api,
                        api_user_uuid=api_user_uuid,
                        scope=scope
                    )
                    db.session.add(new_join_api)

        db.session.commit()
        msg = "Study Subject Edited Successfully"

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()
        return make_response({"msg": "Internal server error when editing study subject"}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/api")
@rbac_required("AdminGetApi")
def api():
    """
    Get one API or a list of all APIs. This will return one API if the API's
    database primary key is passed as a URL option.

    Options
    -------
    id: str

    Response syntax (200)
    ---------------------
    [
        {
            ...API data
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
        api_id = request.args.get("id")

        if api_id:
            query = Api.query.filter(
                ~Api.is_archived & (Api.id == int(api_id))
            )
        else:
            query = Api.query.filter(~Api.is_archived)

        res = [api.meta for api in query.all()]
        return jsonify(res)

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when retrieving APIs"}, 500)


@blueprint.route("/api/create", methods=["POST"])
@rbac_required("AdminCreateApi")
def api_create():
    """
    Create a new API.

    Request syntax
    --------------
    {
        create: {
            name: str
        }
    }

    Response syntax (200)
    ---------------------
    {
        msg: "API Created Successfully"
    }

    Response syntax (400)
    ---------------------
    {
        msg: "API name was not provided" or "API name already exists"
    }

    Response syntax (500)
    ---------------------
    {
        msg: "Internal server error when creating API"
    }
    """
    try:
        data = request.json.get("create")
        if not data:
            return make_response({"msg": "No data provided"}, 400)

        name = data.get("name")
        if not name:
            return make_response({"msg": "API name was not provided"}, 400)

        # Check if an API with the same name already exists
        if Api.query.filter_by(name=name).first():
            return make_response({"msg": "API name already exists"}, 400)

        api = Api()
        populate_model(api, data)
        db.session.add(api)
        db.session.commit()
        msg = "API Created Successfully"

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()

        return make_response({"msg": "Internal server error when creating API"}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/api/edit", methods=["POST"])
@rbac_required("AdminEditApi")
def api_edit():
    """
    Edit an existing API.

    Request syntax
    --------------
    {
        id: int,
        edit: {
            name: str
        }
    }

    All data in the request body are optional. Any attributes that are excluded
    from the request body will not be changed.

    Response syntax (200)
    ---------------------
    {
        msg: "API Edited Successfully"
    }

    Response syntax (400)
    ---------------------
    {
        msg: "API with the same name already exists" or "API with ID X does not exist"
    }

    Response syntax (500)
    ---------------------
    {
        msg: "Internal server error when editing API"
    }
    """
    try:
        data = request.json.get("edit")
        api_id = request.json.get("id")
        if not api_id:
            return make_response({"msg": "API ID not provided"}, 400)

        api = Api.query.get(api_id)
        if not api:
            return make_response({"msg": f"API with ID {api_id} does not exist"}, 400)

        if data and "name" in data:
            new_name = data["name"]
            if new_name != api.name:
                # Check if another API with the same name exists
                existing_api = Api.query.filter(
                    Api.name == new_name, Api.id != api_id
                ).first()
                if existing_api:
                    return make_response({"msg": "API with the same name already exists"}, 400)

        populate_model(api, data)
        db.session.commit()
        msg = "API Edited Successfully"

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()
        return make_response({"msg": "Internal server error when editing API"}, 500)

    return jsonify({"msg": msg})


@blueprint.route("/api/archive", methods=["POST"])
@rbac_required("AdminArchiveApi")
def api_archive():
    """
    Archive an API. This action has the same effect as deleting an entry
    from the database. However, archived items are only filtered from queries
    and can be retrieved.

    Request syntax
    --------------
    {
        id: int
    }

    Response syntax (200)
    ---------------------
    {
        msg: "API Archived Successfully"
    }

    Response syntax (400)
    ---------------------
    {
        msg: "API with ID X does not exist"
    }

    Response syntax (500)
    ---------------------
    {
        msg: "Internal server error when archiving API"
    }
    """
    try:
        api_id = request.json.get("id")
        if not api_id:
            return make_response({"msg": "API ID not provided"}, 400)

        api = Api.query.get(api_id)
        if not api:
            return make_response({"msg": f"API with ID {api_id} does not exist"}, 400)

        api.is_archived = True
        db.session.commit()
        msg = "API Archived Successfully"

    except Exception:
        exc = traceback.format_exc()
        logger.warning(exc)
        db.session.rollback()
        return make_response({"msg": "Internal server error when archiving API"}, 500)

    return jsonify({"msg": msg})
