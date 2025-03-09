import pytest
from unittest.mock import MagicMock
from datetime import datetime
from aws_portal.utils.serialization.participant_serialization import serialize_participant
from aws_portal.models import StudySubject, JoinStudySubjectApi, JoinStudySubjectStudy, Api


@pytest.fixture
def mock_study_subject_with_data():
    # Mock Api
    mock_api = MagicMock(spec=Api)
    mock_api.name = "Fitbit"

    # Mock JoinStudySubjectApi
    mock_api_join = MagicMock(spec=JoinStudySubjectApi)
    mock_api_join.scope = ["sleep", "activity"]
    mock_api_join.api = mock_api

    # Mock Study
    mock_study = MagicMock()
    mock_study.name = "Sleep Study"
    mock_study.id = 101
    mock_study.data_summary = {"totalNights": 14, "averageAsleep": 420}

    # Mock JoinStudySubjectStudy
    mock_study_join = MagicMock(spec=JoinStudySubjectStudy)
    mock_study_join.study = mock_study
    mock_study_join.created_on = datetime(2024, 1, 1, 10, 0, 0)
    mock_study_join.expires_on = datetime(2024, 12, 31, 23, 59, 59)

    # Mock StudySubject
    mock_subject = MagicMock(spec=StudySubject)
    mock_subject.ditti_id = "test-user"
    mock_subject.id = 999
    mock_subject.apis = [mock_api_join]
    mock_subject.studies = [mock_study_join]

    return mock_subject


@pytest.fixture
def mock_study_subject_empty():
    # StudySubject with no apis and no studies
    mock_subject = MagicMock(spec=StudySubject)
    mock_subject.ditti_id = "empty-user"
    mock_subject.id = 123
    mock_subject.apis = []
    mock_subject.studies = []
    return mock_subject


@pytest.fixture
def mock_study_subject_missing_expires_on():
    # Mock a study without expires_on set
    mock_study = MagicMock()
    mock_study.name = "No Expiry Study"
    mock_study.id = 202
    mock_study.data_summary = None

    mock_study_join = MagicMock(spec=JoinStudySubjectStudy)
    mock_study_join.study = mock_study
    mock_study_join.created_on = datetime(2024, 2, 2, 12, 0, 0)
    mock_study_join.expires_on = None  # Missing expires_on

    mock_subject = MagicMock(spec=StudySubject)
    mock_subject.ditti_id = "no-expiry-user"
    mock_subject.id = 456
    mock_subject.apis = []
    mock_subject.studies = [mock_study_join]

    return mock_subject


def test_serialize_participant_with_data(app, mock_study_subject_with_data):
    serialized = serialize_participant(mock_study_subject_with_data)
    assert isinstance(serialized, dict)

    # Check top-level fields
    assert serialized["dittiId"] == "test-user"

    # Check apis
    assert "apis" in serialized
    assert len(serialized["apis"]) == 1
    api_data = serialized["apis"][0]
    assert api_data["apiName"] == "Fitbit"
    assert api_data["scope"] == ["sleep", "activity"]

    # Check studies
    assert "studies" in serialized
    assert len(serialized["studies"]) == 1
    study_data = serialized["studies"][0]
    assert study_data["studyName"] == "Sleep Study"
    assert study_data["studyId"] == 101
    assert study_data["createdOn"] == "2024-01-01T10:00:00"
    assert study_data["expiresOn"] == "2024-12-31T23:59:59"
    assert study_data["dataSummary"] == {
        "totalNights": 14, "averageAsleep": 420}


def test_serialize_participant_empty(app, mock_study_subject_empty):
    serialized = serialize_participant(mock_study_subject_empty)
    assert isinstance(serialized, dict)
    assert serialized["dittiId"] == "empty-user"
    assert serialized["apis"] == []
    assert serialized["studies"] == []


@pytest.mark.skip("This test should raise an error, log, and return None. Investigate caplog to ensure error is logged.")
def test_serialize_participant_missing_expires_on(app, mock_study_subject_missing_expires_on):
    serialized = serialize_participant(mock_study_subject_missing_expires_on)
    assert isinstance(serialized, dict)
    assert serialized["dittiId"] == "no-expiry-user"
    assert serialized["apis"] == []
    assert len(serialized["studies"]) == 1
    study_data = serialized["studies"][0]
    assert study_data["studyName"] == "No Expiry Study"
    assert study_data["studyId"] == 202
    assert study_data["createdOn"] == "2024-02-02T12:00:00"
    # excluded due to None and exclude_none=True
    assert study_data.get("expiresOn") is None
    assert study_data.get("dataSummary") is None
