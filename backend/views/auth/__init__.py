from aws_portal.views.auth.participant.auth import blueprint as participant_auth_blueprint
from aws_portal.views.auth.researcher.auth import blueprint as researcher_auth_blueprint

__all__ = ["participant_auth_blueprint", "researcher_auth_blueprint"]
