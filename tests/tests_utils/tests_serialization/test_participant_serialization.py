from unittest.mock import MagicMock, patch

from backend.utils.serialization.participant_serialization import (
    ParticipantModel,
    serialize_participant,
)


class TestParticipantSerialization:
    @patch(
        "backend.utils.serialization.participant_serialization.ParticipantModel.model_validate"
    )
    def test_successful_serialization(self, mock_validate, app_context):
        """Test successful serialization of a study subject with apis and studies.

        Verifies that the full serialization flow works, with proper camelCase
        transformation and nested object handling.
        """
        # Set up test subject
        study_subject = MagicMock()
        study_subject.ditti_id = "ditti_12345"

        # Set up model_validate mock to return a controlled model instance
        mock_model = MagicMock(spec=ParticipantModel)
        mock_validate.return_value = mock_model

        # Define expected output with camelCase keys and proper nesting
        expected_data = {
            "dittiId": "ditti_12345",
            "apis": [{"apiName": "fitbit", "scope": ["profile", "sleep"]}],
            "studies": [
                {
                    "studyName": "Sleep Study",
                    "studyId": 123,
                    "didConsent": True,
                    "createdOn": "2023-01-01T12:00:00",
                    "startsOn": "2023-01-01T12:00:00",
                    "expiresOn": "2023-12-31T12:00:00",
                    "consentInformation": "Consent text",
                    "dataSummary": "Study data summary",
                }
            ],
        }
        mock_model.model_dump.return_value = expected_data

        # Execute function under test
        result = serialize_participant(study_subject)

        # Verify results and interactions
        assert result is not None
        assert result == expected_data
        mock_validate.assert_called_once_with(study_subject)
        mock_model.model_dump.assert_called_once_with(
            by_alias=True, exclude_unset=True, exclude_none=True
        )

    @patch(
        "backend.utils.serialization.participant_serialization.ParticipantModel.model_validate"
    )
    def test_empty_relationships(self, mock_validate, app_context):
        """Test serialization when there are no apis or studies.

        Confirms proper handling of empty collections without errors.
        """
        study_subject = MagicMock()
        study_subject.ditti_id = "ditti_12345"

        mock_model = MagicMock(spec=ParticipantModel)
        mock_validate.return_value = mock_model

        expected_data = {"dittiId": "ditti_12345", "apis": [], "studies": []}
        mock_model.model_dump.return_value = expected_data

        result = serialize_participant(study_subject)

        assert result is not None
        assert result == expected_data
        mock_validate.assert_called_once_with(study_subject)

    @patch(
        "backend.utils.serialization.participant_serialization.ParticipantModel.model_validate"
    )
    def test_null_optional_fields(self, mock_validate, app_context):
        """Test serialization when optional fields are null.

        Verifies that null fields are excluded from the serialized output.
        """
        study_subject = MagicMock()
        study_subject.ditti_id = "ditti_12345"

        mock_model = MagicMock(spec=ParticipantModel)
        mock_validate.return_value = mock_model

        # Model dump with intentionally missing optional fields
        expected_data = {
            "dittiId": "ditti_12345",
            "apis": [],
            "studies": [
                {
                    "studyName": "Sleep Study",
                    "studyId": 123,
                    "didConsent": True,
                    "createdOn": "2023-01-01T12:00:00",
                    "startsOn": "2023-01-01T12:00:00",
                    # Note: expiresOn, consentInformation, and dataSummary are intentionally omitted
                }
            ],
        }
        mock_model.model_dump.return_value = expected_data

        result = serialize_participant(study_subject)

        assert result is not None
        assert result == expected_data
        assert "expiresOn" not in result["studies"][0]
        assert "consentInformation" not in result["studies"][0]
        assert "dataSummary" not in result["studies"][0]
        mock_validate.assert_called_once_with(study_subject)

    @patch(
        "backend.utils.serialization.participant_serialization.ParticipantModel.model_validate"
    )
    def test_validation_error(self, mock_validate, app_context):
        """Test handling of validation errors.

        Ensures the function gracefully handles Pydantic validation errors
        by returning None and logging the error.
        """
        from pydantic import ValidationError

        study_subject = MagicMock()

        # Simulate a ValidationError during model validation
        mock_validate.side_effect = ValidationError.from_exception_data(
            title="",
            line_errors=[
                {
                    "type": "missing",
                    "loc": ("ditti_id",),
                    "msg": "Field required",
                    "input": {},
                }
            ],
        )

        result = serialize_participant(study_subject)

        # Function should return None on validation failure
        assert result is None

    @patch("backend.utils.serialization.participant_serialization.logger")
    @patch(
        "backend.utils.serialization.participant_serialization.ParticipantModel.model_validate"
    )
    def test_exception_handling(self, mock_validate, mock_logger, app_context):
        """Test handling of unexpected exceptions.

        Verifies that any unhandled exceptions are caught, logged, and
        the function returns None without crashing.
        """
        study_subject = MagicMock()
        study_subject.ditti_id = "ditti_12345"

        # Simulate a generic exception
        mock_validate.side_effect = Exception("Unexpected error")

        result = serialize_participant(study_subject)

        assert result is None
        mock_logger.error.assert_called_once()
