from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field
from .serialization_common import common_config


class ParticipantApiModel(BaseModel):
    scope: List[str] = Field(default_factory=list)
    api_name: str

    model_config = common_config

    __original_obj__: Any = Field(init=False)

    @classmethod
    def model_validate(cls, obj):
        # obj is a JoinStudySubjectApi instance
        model = super().model_validate(obj)

        # Construct the api_name from the related Api object
        return cls.model_construct(
            **model.__dict__,
            api_name=obj.api.name
        )


class ParticipantStudyModel(BaseModel):
    study_name: str
    study_id: int
    created_on: datetime
    expires_on: Optional[datetime] = None
    data_summary: Optional[Any] = None

    model_config = common_config

    __original_obj__: Any = Field(init=False)

    @classmethod
    def model_validate(cls, obj):
        # obj is a JoinStudySubjectStudy instance
        study = obj.study
        return cls.model_construct(
            study_name=study.name,
            study_id=study.id,
            created_on=obj.created_on,
            expires_on=obj.expires_on,
            data_summary=getattr(study, "data_summary", None)
        )


class ParticipantModel(BaseModel):
    dittiId: str
    userId: int
    apis: List[ParticipantApiModel] = Field(default_factory=list)
    studies: List[ParticipantStudyModel] = Field(default_factory=list)

    model_config = common_config

    __original_obj__: Any = Field(init=False)

    @classmethod
    def model_validate(cls, obj):
        # obj is a StudySubject instance
        apis_list = []
        for api in obj.apis:
            validated_api = ParticipantApiModel.model_validate(api)
            apis_list.append(validated_api)

        studies_list = []
        for study in obj.studies:
            validated_study = ParticipantStudyModel.model_validate(study)
            studies_list.append(validated_study)

        return cls.model_construct(
            dittiId=obj.ditti_id,
            userId=obj.id,
            apis=apis_list,
            studies=studies_list
        )


def serialize_participant(study_subject) -> dict[str, Any]:
    participant_model = ParticipantModel.model_validate(study_subject)
    return participant_model.model_dump(by_alias=True, exclude_unset=True)
