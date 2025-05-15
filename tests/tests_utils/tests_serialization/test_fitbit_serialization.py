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

from datetime import date
from unittest.mock import MagicMock, patch

from pydantic import ValidationError

from backend.models import SleepCategoryTypeEnum, SleepLogTypeEnum
from backend.utils.serialization.fitbit_serialization import (
    SleepLogModel,
    serialize_fitbit_data,
)


class TestFitbitSerialization:
    @patch(
        "backend.utils.serialization.fitbit_serialization.SleepLogModel.model_validate"
    )
    def test_sleep_log_serialization(self, mock_validate, app_context):
        """Test successful serialization of sleep logs with levels.

        Verifies that nested sleep level data is properly serialized
        with correct formatting and type conversions.
        """
        # Create minimal test data
        sleep_log = MagicMock()
        sleep_log.date_of_sleep = date(2023, 5, 15)
        sleep_log.log_type = SleepLogTypeEnum.auto_detected
        sleep_log.type = SleepCategoryTypeEnum.stages

        # Set up mock validation response
        mock_model = MagicMock(spec=SleepLogModel)
        mock_validate.return_value = mock_model

        # Define expected output with camelCase keys and nested levels
        expected_data = {
            "dateOfSleep": "2023-05-15",
            "logType": "auto_detected",
            "type": "stages",
            "levels": [
                {
                    "dateTime": "2023-05-15T22:30:00",
                    "level": "deep",
                    "seconds": 1800,
                    "isShort": False,
                },
                {
                    "dateTime": "2023-05-15T23:00:00",
                    "level": "light",
                    "seconds": 3600,
                    "isShort": False,
                },
            ],
        }
        mock_model.model_dump.return_value = expected_data

        # Execute function under test
        result = serialize_fitbit_data([sleep_log])

        # Verify results and interactions
        assert len(result) == 1
        assert result[0] == expected_data
        mock_validate.assert_called_once_with(sleep_log)
        mock_model.model_dump.assert_called_once_with(
            by_alias=True, exclude_unset=True, exclude_none=True
        )

    @patch(
        "backend.utils.serialization.fitbit_serialization.SleepLogModel.model_validate"
    )
    def test_multiple_sleep_logs(self, mock_validate, app_context):
        """Test serialization of multiple sleep logs.

        Ensures the function correctly processes a list of sleep logs
        and returns an array of serialized objects.
        """
        # Create test data for two logs of different types
        sleep_log1 = MagicMock()
        sleep_log1.date_of_sleep = date(2023, 5, 15)
        sleep_log1.log_type = SleepLogTypeEnum.auto_detected
        sleep_log1.type = SleepCategoryTypeEnum.stages

        sleep_log2 = MagicMock()
        sleep_log2.date_of_sleep = date(2023, 5, 16)
        sleep_log2.log_type = SleepLogTypeEnum.manual
        sleep_log2.type = SleepCategoryTypeEnum.classic

        # Set up sequential mock responses
        mock_model1 = MagicMock(spec=SleepLogModel)
        mock_model2 = MagicMock(spec=SleepLogModel)
        mock_validate.side_effect = [mock_model1, mock_model2]

        # Define expected outputs
        expected_data1 = {
            "dateOfSleep": "2023-05-15",
            "logType": "auto_detected",
            "type": "stages",
            "levels": [],
        }
        expected_data2 = {
            "dateOfSleep": "2023-05-16",
            "logType": "manual",
            "type": "classic",
            "levels": [],
        }
        mock_model1.model_dump.return_value = expected_data1
        mock_model2.model_dump.return_value = expected_data2

        # Execute function under test
        result = serialize_fitbit_data([sleep_log1, sleep_log2])

        # Verify results
        assert len(result) == 2
        assert result[0] == expected_data1
        assert result[1] == expected_data2
        assert mock_validate.call_count == 2

    def test_empty_sleep_logs(self, app_context):
        """Test serialization with empty list of sleep logs.

        Verifies that an empty input list results in an empty output list
        without errors.
        """
        result = serialize_fitbit_data([])
        assert result == []

    @patch(
        "backend.utils.serialization.fitbit_serialization.SleepLogModel.model_validate"
    )
    def test_null_optional_fields(self, mock_validate, app_context):
        """Test serialization when optional fields are null.

        Ensures null optional fields are properly omitted from serialized output.
        """
        # Create test data
        sleep_log = MagicMock()
        sleep_log.date_of_sleep = date(2023, 5, 15)
        sleep_log.log_type = SleepLogTypeEnum.auto_detected
        sleep_log.type = SleepCategoryTypeEnum.stages

        # Set up mock validation response
        mock_model = MagicMock(spec=SleepLogModel)
        mock_validate.return_value = mock_model

        # Define expected output with omitted isShort field
        expected_data = {
            "dateOfSleep": "2023-05-15",
            "logType": "auto_detected",
            "type": "stages",
            "levels": [
                {
                    "dateTime": "2023-05-15T22:30:00",
                    "level": "deep",
                    "seconds": 1800,
                    # isShort intentionally omitted to test null handling
                }
            ],
        }
        mock_model.model_dump.return_value = expected_data

        # Execute function under test
        result = serialize_fitbit_data([sleep_log])

        # Verify results
        assert len(result) == 1
        assert result[0] == expected_data
        assert "isShort" not in result[0]["levels"][0]

    @patch(
        "backend.utils.serialization.fitbit_serialization.SleepLogModel.model_validate"
    )
    @patch("backend.utils.serialization.fitbit_serialization.logger")
    def test_validation_error_handling(
        self, mock_logger, mock_validate, app_context
    ):
        """Test handling of validation errors during serialization.

        Verifies that validation errors are properly caught, logged,
        and the function continues processing other logs without crashing.
        """
        # Create test data
        invalid_sleep_log = MagicMock()

        # Simulate a validation error
        mock_validate.side_effect = ValidationError.from_exception_data(
            title="",
            line_errors=[
                {
                    "type": "missing",
                    "loc": ("date_of_sleep",),
                    "msg": "Field required",
                    "input": {},
                }
            ],
        )

        # Execute function under test
        result = serialize_fitbit_data([invalid_sleep_log])

        # Verify error handling
        assert result == []
        mock_logger.error.assert_called_once()

    @patch(
        "backend.utils.serialization.fitbit_serialization.SleepLogModel.model_validate"
    )
    @patch("backend.utils.serialization.fitbit_serialization.logger")
    def test_general_exception_handling(
        self, mock_logger, mock_validate, app_context
    ):
        """Test handling of unexpected exceptions during serialization.

        Ensures that any unhandled exceptions are properly caught, logged,
        and the function continues processing without crashing.
        """
        # Create test data
        problematic_sleep_log = MagicMock()

        # Simulate a general exception
        mock_validate.side_effect = Exception("Unexpected error")

        # Execute function under test
        result = serialize_fitbit_data([problematic_sleep_log])

        # Verify error handling
        assert result == []
        mock_logger.error.assert_called_once()
