from datetime import datetime, UTC, timedelta
from sqlalchemy import select, event

from .joins import JoinStudySubjectStudy
from .study_model import Study


@event.listens_for(JoinStudySubjectStudy, "before_insert")
def set_expires_on(mapper, connection, target):
    """
    Automatically set the expires_on field based on the Study's default_expiry_delta
    if expires_on is not provided.
    """
    if not target.expires_on:
        if target.study_id:
            # Use a raw SQL query to fetch default_expiry_delta
            stmt = select(Study.default_expiry_delta).where(
                Study.id == target.study_id
            )
            result = connection.execute(stmt).scalar_one_or_none()
            if result is not None:
                target.expires_on = datetime.now(UTC) + timedelta(days=result)
            else:
                raise ValueError(
                    f"Cannot set expires_on: Study with id {
                        target.study_id} not found or default_expiry_delta is missing."
                )
        else:
            raise ValueError("Cannot set expires_on: study_id is missing.")
