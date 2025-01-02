from pydantic import ValidationError
from typing import Any, Dict, Optional
import logging
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field, field_serializer, model_validator
from aws_portal.models import JoinStudySubjectApi, JoinStudySubjectStudy, StudySubject
from .serialization_common import common_config

logger = logging.getLogger(__name__)


class ParticipantApiModel(BaseModel):
    scope: List[str] = Field(default_factory=list)
    api_name: str

    model_config = common_config

    @model_validator(mode="before")
    def extract_api_name(cls, obj):
        """
        Transforms a JoinStudySubjectApi ORM instance into a dict
        with the required fields for ParticipantApiModel.
        """
        if isinstance(obj, JoinStudySubjectApi):
            return {
                "scope": obj.scope,
                "api_name": obj.api.name if obj.api else None
            }
        return obj


class ParticipantStudyModel(BaseModel):
    study_name: str
    study_id: int
    created_on: datetime
    starts_on: datetime
    expires_on: Optional[datetime] = None
    consent_information: Optional[str] = None
    data_summary: Optional[str] = None

    model_config = common_config

    @model_validator(mode="before")
    def extract_study_fields(cls, obj):
        if isinstance(obj, JoinStudySubjectStudy):
            return {
                "study_name": obj.study.name,
                "study_id": obj.study.id,
                "created_on": obj.created_on,
                "starts_on": obj.created_on,  # TODO: Different format than created_on
                "expires_on": obj.expires_on,
                "consent_information": getattr(obj.study, "consent_information", None),
                "data_summary": getattr(obj.study, "data_summary", None)
            }
        return obj

    @field_serializer("created_on", "expires_on", mode="plain")
    def serialize_datetimes(value: Optional[datetime]) -> Optional[str]:
        return value.isoformat() if value else None


class ParticipantModel(BaseModel):
    ditti_id: str
    apis: List[ParticipantApiModel] = Field(default_factory=list)
    studies: List[ParticipantStudyModel] = Field(default_factory=list)

    model_config = common_config


def serialize_participant(study_subject: StudySubject) -> Optional[Dict[str, Any]]:
    """
    Serializes a StudySubject ORM instance into a dictionary suitable for JSON responses.

    Args:
        study_subject (StudySubject): The study subject to serialize.

    Returns:
        Optional[Dict[str, Any]]: The serialized participant data if successful, otherwise None.
    """
    try:
        participant_model = ParticipantModel.model_validate(study_subject)
        serialized_data = participant_model.model_dump(
            by_alias=True,
            exclude_unset=True,
            exclude_none=True
        )

        return serialized_data

    except ValidationError as ve:
        logger.error(
            f"Validation error in ParticipantModel for StudySubject {
                study_subject.ditti_id}: {ve}"
        )
        return None

    except Exception as e:
        logger.error(
            f"Unexpected error during serialization of StudySubject {
                study_subject.ditti_id}: {e}"
        )
        return None
