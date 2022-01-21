from functools import wraps
import logging
from flask import jsonify, request
from flask_jwt_extended import current_user, verify_jwt_in_request
from aws_portal.models import AccessGroup, Study

logger = logging.getLogger(__name__)


def auth_required(action, _resource=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            data = request.args or request.json
            group_id = data.get('group')
            study_id = data.get('study')
            resource = _resource or data.get('resource')

            try:
                permissions = current_user.get_permissions(group_id, study_id)
                current_user.validate_ask(action, resource, permissions)

            except ValueError:
                group = AccessGroup.query.get(group_id)
                study = Study.query.get(study_id) if study_id else None
                ask = '%s -> %s -> %s -> %s' % (group, study, action, resource)
                s = current_user, ask
                logger.warning('Unauthorized request from %s: %s' % s)

                return jsonify({'msg': 'Unauthorized Request'})

            return func(*args, **kwargs)

        return wrapper

    return decorator
