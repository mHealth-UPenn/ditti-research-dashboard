# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may]
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

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
    """
    Model for participant API access information.

    Contains information about API access granted to study participants,
    including access scopes and identification.
    """

    scope: list[str] = Field(default_factory=list)
    api_name: str

    model_config = common_config

    @model_validator(mode="before")
    @classmethod
    def extract_api_name(cls, data):
        """Transform ORM instance into dict with ParticipantApiModel fields."""
        if isinstance(data, JoinStudySubjectApi):
            return {
                "scope": data.scope,
                "apiName": data.api.name if data.api else None,
            }
        return data


class ParticipantStudyModel(BaseModel):
    """
    Model for participant study enrollment information.

    Contains information about studies a participant is enrolled in,
    including study metadata and enrollment details.
    """

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
    @classmethod
    def extract_study_fields(cls, data):
        """
        Extract study fields from the join model.

        Converts a JoinStudySubjectStudy database object to a dictionary
        format suitable for this model.

        Parameters
        ----------
        obj : Any
            The input object (typically a JoinStudySubjectStudy instance).

        Returns
        -------
        dict
            A dictionary with extracted field values.
        """
        if isinstance(data, JoinStudySubjectStudy):
            return {
                "studyName": data.study.name,
                "studyId": data.study.id,
                "didConsent": data.did_consent,
                "createdOn": data.created_on,
                "startsOn": data.created_on,
                "expiresOn": getattr(data, "expires_on", None),
                "consentInformation": getattr(
                    data.study, "consent_information", None
                ),
                "dataSummary": getattr(data.study, "data_summary", None),
            }
        return data

    @field_serializer("created_on", "expires_on", mode="plain")
    def serialize_datetimes(self, value: datetime | None) -> str | None:
        """
        Serialize datetime fields to ISO format strings.

        Parameters
        ----------
        value : datetime or None
            The datetime object to serialize, or None.

        Returns
        -------
        str or None
            ISO-formatted datetime string or None if input is None.
        """
        return value.isoformat() if value else None


class ParticipantModel(BaseModel):
    """
    Model for participant information.

    Represents a study participant with their Ditti ID and associated
    API access and study enrollments.
    """

    ditti_id: str
    apis: list[ParticipantApiModel] = Field(default_factory=list)
    studies: list[ParticipantStudyModel] = Field(default_factory=list)

    model_config = common_config


def serialize_participant(
    study_subject: StudySubject,
) -> dict[str, Any] | None:
    """
    Serialize a StudySubject ORM instance into a suitable dictionary.

    Parameters
    ----------
    study_subject : StudySubject
        The study subject to serialize.

    Returns
    -------
    dict[str, Any] or None
        The serialized participant data if successful, otherwise None.
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
