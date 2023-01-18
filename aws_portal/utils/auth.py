from functools import wraps
import logging
from flask import make_response, request
from flask_jwt_extended import current_user, verify_jwt_in_request
from aws_portal.models import App, Study

logger = logging.getLogger(__name__)


def validate_password(password):
    """
    Validates whether a given password is 8-64 characters long

    Args
    ----
    password: str
        The password to validate
    
    Returns
    -------
    str: 'valid' or an error message
    """
    if len(password) < 8:
        return 'Minimum password length is 8 characters'

    if 64 < len(password):
        return 'Maximum password length is 64 characters'

    return 'valid'


def auth_required(action, _resource=None):
    """
    Wraps a view that requires permissions for a given action and resource

    Args
    ----
    action: str
        The action to check permissions for
    _resource: str (optional)
        The resource to check permissions for
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            data = request.args or request.json
            app_id = data.get('app')
            study_id = data.get('study')
            resource = _resource or data.get('resource')

            # check whether the user has permissions
            try:
                permissions = current_user.get_permissions(app_id, study_id)
                current_user.validate_ask(action, resource, permissions)

            # when the user does not have permission
            except ValueError:

                # log an error
                app = App.query.get(app_id) if study_id else None
                study = Study.query.get(study_id) if study_id else None
                ask = '%s -> %s -> %s -> %s' % (app, study, action, resource)
                s = current_user, ask
                logger.warning('Unauthorized request from %s: %s' % s)

                # return 403
                return make_response({'msg': 'Unauthorized Request'}, 403)

            # return the view as normal
            return func(*args, **kwargs)

        return wrapper

    return decorator
