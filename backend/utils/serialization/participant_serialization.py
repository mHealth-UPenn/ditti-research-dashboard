# Ditti Research Dashboard
# Copyright (C) 2025 the Trustees of the University of Pennsylvania
#
# Ditti Research Dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Ditti Research Dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    field_serializer,
    model_validator,
)

from backend.models import (
    JoinStudySubjectApi,
    JoinStudySubjectStudy,
    StudySubject,
)

from .serialization_common import common_config

logger = logging.getLogger(__name__)


class ParticipantApiModel(BaseModel):
    scope: list[str] = Field(default_factory=list)
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
                "api_name": obj.api.name if obj.api else None,
            }
        return obj


class ParticipantStudyModel(BaseModel):
    study_name: str
    study_id: int
    did_consent: bool
    created_on: datetime
    starts_on: datetime
    expires_on: datetime | None
    consent_information: str | None
    data_summary: str | None

    model_config = common_config

    @model_validator(mode="before")
    def extract_study_fields(cls, obj):
        if isinstance(obj, JoinStudySubjectStudy):
            return {
                "study_name": obj.study.name,
                "study_id": obj.study.id,
                "did_consent": obj.did_consent,
                "created_on": obj.created_on,
                "starts_on": obj.created_on,
                "expires_on": getattr(obj, "expires_on", None),
                "consent_information": getattr(
                    obj.study, "consent_information", None
                ),
                "data_summary": getattr(obj.study, "data_summary", None),
            }
        return obj

    @field_serializer("created_on", "expires_on", mode="plain")
    def serialize_datetimes(value: datetime | None) -> str | None:
        return value.isoformat() if value else None


class ParticipantModel(BaseModel):
    ditti_id: str
    apis: list[ParticipantApiModel] = Field(default_factory=list)
    studies: list[ParticipantStudyModel] = Field(default_factory=list)

    model_config = common_config


def serialize_participant(
    study_subject: StudySubject,
) -> dict[str, Any] | None:
    """
    Serialize a StudySubject ORM instance into a suitable dictionary.

    Args:
        study_subject (StudySubject): The study subject to serialize.

    Returns
    -------
        Optional[Dict[str, Any]]: The serialized participant data if successful,
            otherwise None.
    """
    try:
        participant_model = ParticipantModel.model_validate(study_subject)
        serialized_data = participant_model.model_dump(
            by_alias=True, exclude_unset=True, exclude_none=True
        )

        return serialized_data

    except ValidationError as ve:
        logger.error(
            f"Validation error in ParticipantModel for StudySubject {
                study_subject.ditti_id
            }: {ve}"
        )
        return None

    except Exception as e:
        logger.error(
            f"Unexpected error during serialization of StudySubject {
                study_subject.ditti_id
            }: {e}"
        )
        return None
