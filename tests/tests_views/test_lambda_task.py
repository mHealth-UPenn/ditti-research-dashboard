import pytest
from unittest.mock import patch, MagicMock

# ---------------------------
# Tests for GET /lambda_task/
# ---------------------------


@patch('aws_portal.views.lambda_task.LambdaTask')
def test_get_lambda_tasks_success(mock_lambda_task_model, client, get_admin):
    """
    Test successful retrieval of Lambda tasks.
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
        "errorCode": None
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
        "errorCode": "Error123"
    }

    mock_lambda_task_model.query.order_by.return_value.all.return_value = [
        mock_task1, mock_task2]

    response = get_admin("/lambda_task/", query_string={"app": "1"})

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == [mock_task1.meta, mock_task2.meta]
    mock_lambda_task_model.query.order_by.assert_called_once_with(mock_desc)


@patch('aws_portal.views.lambda_task.LambdaTask')
def test_get_lambda_tasks_internal_error(mock_lambda_task_model, client, get_admin):
    """
    Test internal server error during retrieval of Lambda tasks.
    """
    mock_desc = MagicMock()
    mock_lambda_task_model.created_on.desc.return_value = mock_desc
    mock_lambda_task_model.query.order_by.return_value.all.side_effect = Exception(
        "Database error")

    response = get_admin("/lambda_task/", query_string={"app": "1"})

    assert response.status_code == 500
    assert response.is_json
    assert response.get_json() == {
        "msg": "Internal server error when retrieving lambda tasks."}
    mock_lambda_task_model.query.order_by.assert_called_once_with(mock_desc)
    mock_lambda_task_model.query.order_by.return_value.all.assert_called_once()


@patch('aws_portal.views.lambda_task.LambdaTask')
def test_get_lambda_tasks_empty_list(mock_lambda_task_model, client, get_admin):
    """
    Test retrieval when no Lambda tasks exist.
    """
    mock_desc = MagicMock()
    mock_lambda_task_model.created_on.desc.return_value = mock_desc
    mock_lambda_task_model.query.order_by.return_value.all.return_value = []

    response = get_admin("/lambda_task/", query_string={"app": "1"})

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == []
    mock_lambda_task_model.query.order_by.assert_called_once_with(mock_desc)


# ---------------------------------
# Tests for POST /lambda_task/invoke
# ---------------------------------

@patch('aws_portal.views.lambda_task.create_and_invoke_lambda_task')
def test_invoke_lambda_task_success(mock_create_and_invoke, client, post_admin):
    """
    Test successful invocation of a new Lambda task.
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
        "errorCode": None
    }
    mock_create_and_invoke.return_value = mock_task

    response = post_admin("/lambda_task/invoke", json={"app": "1"})

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == {
        "msg": "Lambda task invoked successfully",
        "task": mock_task.meta
    }
    mock_create_and_invoke.assert_called_once()


@patch('aws_portal.views.lambda_task.create_and_invoke_lambda_task')
def test_invoke_lambda_task_failure(mock_create_and_invoke, client, post_admin):
    """
    Test invocation failure when create_and_invoke_lambda_task returns None.
    """
    mock_create_and_invoke.return_value = None

    response = post_admin("/lambda_task/invoke", json={"app": "1"})

    assert response.status_code == 500
    assert response.is_json
    assert response.get_json() == {
        "msg": "Internal server error when invoking lambda task."}
    mock_create_and_invoke.assert_called_once()


@patch('aws_portal.views.lambda_task.create_and_invoke_lambda_task')
def test_invoke_lambda_task_exception(mock_create_and_invoke, client, post_admin):
    """
    Test invocation failure when create_and_invoke_lambda_task raises an exception.
    """
    mock_create_and_invoke.side_effect = Exception("Invocation error")

    response = post_admin("/lambda_task/invoke", json={"app": "1"})

    assert response.status_code == 500
    assert response.is_json
    assert response.get_json() == {
        "msg": "Internal server error when invoking lambda task."}
    mock_create_and_invoke.assert_called_once()


@patch('aws_portal.views.lambda_task.create_and_invoke_lambda_task')
def test_invoke_lambda_task_invalid_data(mock_create_and_invoke, client, post_admin):
    """
    Since the POST /invoke route does not expect any data, this test ensures that sending unexpected data does not break the route.
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
        "errorCode": None
    }
    mock_create_and_invoke.return_value = mock_task

    response = post_admin("/lambda_task/invoke", json={
        "app": "1",
        "unexpected": "data"
    })

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == {
        "msg": "Lambda task invoked successfully",
        "task": mock_task.meta
    }
    mock_create_and_invoke.assert_called_once()
