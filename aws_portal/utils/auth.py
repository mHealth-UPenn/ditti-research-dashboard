from functools import wraps
import logging
from flask import jsonify, request
from flask_jwt_extended import current_user, verify_jwt_in_request
from aws_portal.models import App, Study

logger = logging.getLogger(__name__)


def validate_password(data, password):
    if len(password) < 8:
        return 'Minimum password length is 8 characters'

    if 64 < len(password):
        return 'Maximum password length is 64 characters'

    for k, v in data.items():
        if type(v) is not str or k == 'password':
            continue

        if password in v.lower():
            return f'The password is too similar to "{k}:" {v}'

    return 'valid'


def auth_required(action, _resource=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            data = request.args or request.json
            app_id = data.get('app')
            study_id = data.get('study')
            resource = _resource or data.get('resource')

            try:
                permissions = current_user.get_permissions(app_id, study_id)
                current_user.validate_ask(action, resource, permissions)

            except ValueError:
                app = App.query.get(app_id) if study_id else None
                study = Study.query.get(study_id) if study_id else None
                ask = '%s -> %s -> %s -> %s' % (app, study, action, resource)
                s = current_user, ask
                logger.warning('Unauthorized request from %s: %s' % s)

                return jsonify({'msg': 'Unauthorized Request'})

            return func(*args, **kwargs)

        return wrapper

    return decorator
