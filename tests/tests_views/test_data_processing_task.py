from unittest.mock import MagicMock, patch

import pytest

from tests.testing_utils import mock_researcher_auth_for_testing

# Add fixtures for researcher authentication


@pytest.fixture
def researcher_headers(client):
    """Fixture providing researcher authentication headers"""
    return mock_researcher_auth_for_testing(client, is_admin=False)


@pytest.fixture
def researcher_get(client, researcher_headers):
    """Create a test GET request function with researcher authentication"""

    def _get(url, query_string=None, **kwargs):
        return client.get(
            url, query_string=query_string, headers=researcher_headers, **kwargs
        )

    return _get


@pytest.fixture
def researcher_post(client, researcher_headers):
    """Create a test POST request function with researcher authentication"""

    def _post(url, data=None, json=None, **kwargs):
        return client.post(
            url,
            data=data,
            json=json,
            content_type="application/json",
            headers=researcher_headers,
            **kwargs,
        )

    return _post


# ---------------------------
# Tests for GET /data_processing_task/
# ---------------------------


@patch("backend.views.data_processing_task.LambdaTask")
def test_get_data_processing_tasks_success(
    mock_lambda_task_model, client, researcher_get
):
    """
    Test successful retrieval of data processing tasks.
    """
    mock_desc = MagicMock()
    mock_lambda_task_model.created_on.desc.return_value = mock_desc

    mock_task1 = MagicMock()
    mock_task1.meta = {
        "id": 1,
        "status": "Success",
        "billedMs": 1500,
        "createdOn": "2024-12-01T12:00:00Z",
        "updatedOn": "2024-12-01T12:30:00Z",
        "completedOn": "2024-12-01T12:45:00Z",
        "logFile": "log1.txt",
        "errorCode": None,
    }

    mock_task2 = MagicMock()
    mock_task2.meta = {
        "id": 2,
        "status": "Failed",
        "billedMs": 2000,
        "createdOn": "2024-11-30T09:00:00Z",
        "updatedOn": "2024-11-30T09:15:00Z",
        "completedOn": "2024-11-30T09:30:00Z",
        "logFile": None,
        "errorCode": "Error123",
    }

    mock_lambda_task_model.query.order_by.return_value.all.return_value = [
        mock_task1,
        mock_task2,
    ]

    response = researcher_get(
        "/data_processing_task/", query_string={"app": "1"}
    )

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == [mock_task1.meta, mock_task2.meta]
    mock_lambda_task_model.query.order_by.assert_called_once_with(mock_desc)


@patch("backend.views.data_processing_task.LambdaTask")
def test_get_data_processing_tasks_internal_error(
    mock_lambda_task_model, client, researcher_get
):
    """
    Test internal server error during retrieval of data processing tasks.
    """
    mock_desc = MagicMock()
    mock_lambda_task_model.created_on.desc.return_value = mock_desc
    mock_lambda_task_model.query.order_by.return_value.all.side_effect = (
        Exception("Database error")
    )

    response = researcher_get(
        "/data_processing_task/", query_string={"app": "1"}
    )

    assert response.status_code == 500
    assert response.is_json
    assert response.get_json() == {
        "msg": "Internal server error when retrieving data processing tasks."
    }
    mock_lambda_task_model.query.order_by.assert_called_once_with(mock_desc)
    mock_lambda_task_model.query.order_by.return_value.all.assert_called_once()


@patch("backend.views.data_processing_task.LambdaTask")
def test_get_data_processing_tasks_empty_list(
    mock_lambda_task_model, client, researcher_get
):
    """
    Test retrieval when no data processing tasks exist.
    """
    mock_desc = MagicMock()
    mock_lambda_task_model.created_on.desc.return_value = mock_desc
    mock_lambda_task_model.query.order_by.return_value.all.return_value = []

    response = researcher_get(
        "/data_processing_task/", query_string={"app": "1"}
    )

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == []
    mock_lambda_task_model.query.order_by.assert_called_once_with(mock_desc)


# ---------------------------------
# Tests for POST /data_processing_task/invoke
# ---------------------------------


@patch("backend.views.data_processing_task.create_and_invoke_lambda_task")
def test_invoke_data_processing_task_success(
    mock_create_and_invoke, client, researcher_post
):
    """
    Test successful invocation of a new data processing task.
    """
    mock_task = MagicMock()
    mock_task.meta = {
        "id": 3,
        "status": "InProgress",
        "billedMs": 0,
        "createdOn": "2024-12-02T08:00:00Z",
        "updatedOn": "2024-12-02T08:00:00Z",
        "completedOn": None,
        "logFile": None,
        "errorCode": None,
    }
    mock_create_and_invoke.return_value = mock_task

    response = researcher_post(
        "/data_processing_task/invoke", json={"app": "1"}
    )

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == {
        "msg": "Data processing task invoked successfully",
        "task": mock_task.meta,
    }
    mock_create_and_invoke.assert_called_once()


@patch("backend.views.data_processing_task.create_and_invoke_lambda_task")
def test_invoke_data_processing_task_failure(
    mock_create_and_invoke, client, researcher_post
):
    """
    Test invocation failure when create_and_invoke_lambda_task returns None.
    """
    mock_create_and_invoke.return_value = None

    response = researcher_post(
        "/data_processing_task/invoke", json={"app": "1"}
    )

    assert response.status_code == 500
    assert response.is_json
    assert response.get_json() == {
        "msg": "Internal server error when invoking data processing task."
    }
    mock_create_and_invoke.assert_called_once()


@patch("backend.views.data_processing_task.create_and_invoke_lambda_task")
def test_invoke_data_processing_task_exception(
    mock_create_and_invoke, client, researcher_post
):
    """
    Test invocation failure when create_and_invoke_lambda_task raises an exception.
    """
    mock_create_and_invoke.side_effect = Exception("Invocation error")

    response = researcher_post(
        "/data_processing_task/invoke", json={"app": "1"}
    )

    assert response.status_code == 500
    assert response.is_json
    assert response.get_json() == {
        "msg": "Internal server error when invoking data processing task."
    }
    mock_create_and_invoke.assert_called_once()


@patch("backend.views.data_processing_task.create_and_invoke_lambda_task")
def test_invoke_data_processing_task_invalid_data(
    mock_create_and_invoke, client, researcher_post
):
    """
    Since the POST /invoke route expects an 'app' field, this test ensures that sending unexpected data does not break the route.
    """
    mock_task = MagicMock()
    mock_task.meta = {
        "id": 4,
        "status": "InProgress",
        "billedMs": 0,
        "createdOn": "2024-12-03T10:00:00Z",
        "updatedOn": "2024-12-03T10:00:00Z",
        "completedOn": None,
        "logFile": None,
        "errorCode": None,
    }
    mock_create_and_invoke.return_value = mock_task

    response = researcher_post(
        "/data_processing_task/invoke", json={"app": "1", "unexpected": "data"}
    )

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == {
        "msg": "Data processing task invoked successfully",
        "task": mock_task.meta,
    }
    mock_create_and_invoke.assert_called_once()


@patch("backend.views.data_processing_task.LambdaTask")
@patch("backend.views.data_processing_task.db")
def test_force_stop_data_processing_task_success(
    mock_db, mock_lambda_task_model, client, researcher_post
):
    """
    Test successful force stopping of a data processing task.
    """
    mock_task = MagicMock()

    mock_lambda_task_model.query.filter.return_value.first.return_value = (
        mock_task
    )
    mock_db.session.commit.return_value = None

    response = researcher_post(
        "/data_processing_task/force-stop", json={"function_id": 1}
    )

    assert mock_task.status == "Failed"
    assert mock_task.completed_on is not None
    assert mock_task.error_code == "ForceStopped"

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == {
        "msg": "Data processing task stopped successfully"
    }


def test_force_stop_data_processing_task_no_function_id(
    client, researcher_post
):
    """
    Test force stopping of a data processing task with no function_id.
    """
    response = researcher_post("/data_processing_task/force-stop", json={})
    assert response.status_code == 400
    assert response.is_json
    assert response.get_json() == {"msg": "function_id is required"}


@patch("backend.views.data_processing_task.LambdaTask")
def test_force_stop_data_processing_task_nonexistent_function_id(
    mock_lambda_task_model, client, researcher_post
):
    """
    Test force stopping of a data processing task with a nonexistent function_id.
    """
    mock_lambda_task_model.query.filter.return_value.first.return_value = None

    response = researcher_post(
        "/data_processing_task/force-stop", json={"function_id": 1}
    )
    assert response.status_code == 404
    assert response.is_json
    assert response.get_json() == {
        "msg": "Data processing task with id 1 not found."
    }


@patch("backend.views.data_processing_task.LambdaTask")
def test_force_stop_data_processing_task_internal_error(
    mock_lambda_task_model, client, researcher_post
):
    """
    Test internal server error when force stopping a data processing task.
    """
    mock_lambda_task_model.query.filter.return_value.first.side_effect = (
        Exception("Internal server error")
    )

    response = researcher_post(
        "/data_processing_task/force-stop", json={"function_id": 1}
    )
    assert response.status_code == 500
    assert response.is_json
    assert response.get_json() == {
        "msg": "Internal server error when stopping data processing task."
    }
