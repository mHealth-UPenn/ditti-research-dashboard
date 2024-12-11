from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field, model_validator, field_serializer
from aws_portal.models import JoinStudySubjectApi, JoinStudySubjectStudy, StudySubject
from .serialization_common import common_config


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
    expires_on: Optional[datetime] = None
    data_summary: Optional[Any] = None

    model_config = common_config

    @model_validator(mode="before")
    def extract_study_fields(cls, obj):
        """
        Transforms a JoinStudySubjectStudy ORM instance into a dict
        with the required fields for ParticipantStudyModel.
        """
        if isinstance(obj, JoinStudySubjectStudy):
            return {
                "study_name": obj.study.name,
                "study_id": obj.study.id,
                "created_on": obj.created_on,
                "expires_on": obj.expires_on,
                "data_summary": getattr(obj.study, "data_summary", None)
            }
        return obj

    @field_serializer("created_on", "expires_on", mode="plain")
    def serialize_datetimes(value: Optional[datetime]) -> Optional[str]:
        return value.isoformat() if value else None


class ParticipantModel(BaseModel):
    dittiId: str
    userId: int
    apis: List[ParticipantApiModel] = Field(default_factory=list)
    studies: List[ParticipantStudyModel] = Field(default_factory=list)

    model_config = common_config

    @model_validator(mode="before")
    def extract_participant_fields(cls, obj):
        """
        Transforms a StudySubject ORM instance into a dict
        with the required fields for ParticipantModel.
        """
        if isinstance(obj, StudySubject):
            return {
                "dittiId": obj.ditti_id,
                "userId": obj.id,
                "apis": obj.apis,
                "studies": obj.studies
            }
        return obj


def serialize_participant(study_subject) -> dict[str, Any]:
    participant_model = ParticipantModel.model_validate(study_subject)
    return participant_model.model_dump(by_alias=True, exclude_unset=True)
