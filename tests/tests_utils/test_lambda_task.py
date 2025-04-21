from datetime import datetime, timedelta, UTC
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from freezegun import freeze_time

from backend.models import LambdaTask
from backend.utils.lambda_task import (
    check_and_invoke_lambda_task,
    create_and_invoke_lambda_task,
    invoke_lambda_task,
)


@pytest.fixture
def app():
    """
    Creates a Flask app instance for testing and pushes an application context.
    """
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["ENV"] = "testing"
    app.config["LAMBDA_FUNCTION_NAME"] = "test_lambda_function"
    app.config["LOCAL_LAMBDA_ENDPOINT"] = (
        "http://localhost:9000/2015-03-31/functions/function/invocations"
    )

    with app.app_context():
        yield app


@pytest.fixture
def mock_db_session():
    with patch("backend.utils.lambda_task.db.session") as mock_session:
        yield mock_session


@pytest.fixture
def mock_query():
    with patch("backend.utils.lambda_task.LambdaTask.query") as mock_query:
        yield mock_query


@pytest.fixture
def mock_boto3_client():
    with patch("backend.utils.lambda_task.boto3.client") as mock_client:
        yield mock_client


@pytest.fixture
def fixed_datetime():
    fixed_time = datetime(2024, 12, 1, 12, 0, 0, tzinfo=UTC)
    with freeze_time(fixed_time):
        yield fixed_time


def test_create_and_invoke_lambda_task_success(
    app, mock_db_session, mock_query, mock_boto3_client, fixed_datetime
):
    # Create a mock LambdaTask instance
    mock_task_instance = MagicMock(spec=LambdaTask)
    mock_task_instance.id = 123
    mock_task_instance.created_on = fixed_datetime
    mock_task_instance.updated_on = fixed_datetime

    # Mock the LambdaTask constructor to return the mock_task_instance
    with patch(
        "backend.utils.lambda_task.LambdaTask", return_value=mock_task_instance
    ) as mock_lambda_task_constructor:
        # Set LambdaTask.query to mock_query to preserve the query chain
        mock_lambda_task_constructor.query = mock_query

        # Mock boto3 Lambda client
        mock_lambda_client = MagicMock()
        mock_boto3_client.return_value = mock_lambda_client
        mock_lambda_client.invoke.return_value = {"StatusCode": 202}

        # Mock LambdaTask.query.get to return the mock_task_instance when invoked with id=123
        mock_query.get.return_value = mock_task_instance

        result = create_and_invoke_lambda_task()

        assert result == mock_task_instance
        mock_lambda_task_constructor.assert_called_once_with(
            status="Pending",
            created_on=fixed_datetime,
            updated_on=fixed_datetime,
        )
        mock_db_session.add.assert_called_once_with(mock_task_instance)
        assert mock_db_session.commit.call_count == 2  # Called twice

        mock_boto3_client.assert_called_once_with("lambda")
        mock_lambda_client.invoke.assert_called_once_with(
            FunctionName=app.config["LAMBDA_FUNCTION_NAME"],
            InvocationType="Event",
            Payload=b'{"function_id": 123}',
        )

        # Verify that the task status was updated to 'InProgress'
        mock_task_instance.status = "InProgress"
        mock_task_instance.updated_on = fixed_datetime
        mock_db_session.commit.assert_called_with()


def test_create_and_invoke_lambda_task_exception(
    app, mock_db_session, mock_query, mock_boto3_client, fixed_datetime
):
    with patch(
        "backend.utils.lambda_task.LambdaTask"
    ) as mock_lambda_task_constructor:
        mock_lambda_task_instance = MagicMock(spec=LambdaTask)
        mock_lambda_task_constructor.return_value = mock_lambda_task_instance

        # Set LambdaTask.query to mock_query to preserve the query chain
        mock_lambda_task_constructor.query = mock_query

        mock_db_session.commit.side_effect = Exception("DB commit failed")

        result = create_and_invoke_lambda_task()

        assert result is None
        mock_db_session.add.assert_called_once_with(mock_lambda_task_instance)
        mock_db_session.commit.assert_called_once()
        mock_db_session.rollback.assert_called_once()


def test_check_and_invoke_lambda_task_already_run_today(
    app, mock_db_session, mock_query, mock_boto3_client, fixed_datetime
):
    # Create a mock latest_task that was created today
    mock_latest_task = MagicMock(spec=LambdaTask)
    mock_latest_task.created_on.date.return_value = fixed_datetime.date()

    # Set up the query chain
    mock_filter = mock_query.filter.return_value
    mock_order_by = mock_filter.order_by.return_value
    mock_order_by.first.return_value = mock_latest_task

    result = check_and_invoke_lambda_task()

    assert result == mock_latest_task
    mock_query.filter.assert_called_once()
    mock_filter.order_by.assert_called_once()
    mock_order_by.first.assert_called_once()

    # Ensure no new task was created or Lambda was invoked
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()
    mock_boto3_client.assert_not_called()


def test_check_and_invoke_lambda_task_not_run_today(
    app, mock_db_session, mock_query, mock_boto3_client, fixed_datetime
):
    # Create a mock latest_task that was created yesterday
    mock_latest_task = MagicMock(spec=LambdaTask)
    mock_latest_task.created_on.date.return_value = (
        fixed_datetime - timedelta(days=1)
    ).date()

    # Set up the query chain to return the mock_latest_task
    mock_filter = mock_query.filter.return_value
    mock_order_by = mock_filter.order_by.return_value
    mock_order_by.first.return_value = mock_latest_task

    # Create a new mock task to be created and invoked
    new_task = MagicMock(spec=LambdaTask)
    new_task.id = 456
    new_task.created_on = fixed_datetime
    new_task.updated_on = fixed_datetime

    with patch(
        "backend.utils.lambda_task.LambdaTask", return_value=new_task
    ) as mock_lambda_task_constructor:
        # Set LambdaTask.query to mock_query to preserve the query chain
        mock_lambda_task_constructor.query = mock_query

        # Mock boto3 Lambda client
        mock_lambda_client = MagicMock()
        mock_boto3_client.return_value = mock_lambda_client
        mock_lambda_client.invoke.return_value = {"StatusCode": 202}

        # Mock LambdaTask.query.get to return the new_task when invoked with id=456
        mock_query.get.return_value = new_task

        result = check_and_invoke_lambda_task()

        assert result == new_task
        mock_query.filter.assert_called_once()
        mock_filter.order_by.assert_called_once()
        mock_order_by.first.assert_called_once()

        # Verify that a new task was created and added to the session
        mock_lambda_task_constructor.assert_called_once_with(
            status="Pending",
            created_on=fixed_datetime,
            updated_on=fixed_datetime,
        )
        mock_db_session.add.assert_called_once_with(new_task)
        # One for adding, one for updating status
        assert mock_db_session.commit.call_count == 2

        mock_boto3_client.assert_called_once_with("lambda")
        mock_lambda_client.invoke.assert_called_once_with(
            FunctionName=app.config["LAMBDA_FUNCTION_NAME"],
            InvocationType="Event",
            Payload=b'{"function_id": 456}',
        )

        # Verify that the task status was updated to 'InProgress'
        new_task.status = "InProgress"
        new_task.updated_on = fixed_datetime
        mock_db_session.commit.assert_called_with()


def test_check_and_invoke_lambda_task_no_tasks(
    app, mock_db_session, mock_query, mock_boto3_client, fixed_datetime
):
    # Set up the query chain to return None, indicating no tasks have been run
    mock_filter = mock_query.filter.return_value
    mock_order_by = mock_filter.order_by.return_value
    mock_order_by.first.return_value = None

    # Create a new mock task to be created and invoked
    new_task = MagicMock(spec=LambdaTask)
    new_task.id = 789
    new_task.created_on = fixed_datetime
    new_task.updated_on = fixed_datetime

    with patch(
        "backend.utils.lambda_task.LambdaTask", return_value=new_task
    ) as mock_lambda_task_constructor:
        # Set LambdaTask.query to mock_query to preserve the query chain
        mock_lambda_task_constructor.query = mock_query

        # Mock boto3 Lambda client
        mock_lambda_client = MagicMock()
        mock_boto3_client.return_value = mock_lambda_client
        mock_lambda_client.invoke.return_value = {"StatusCode": 202}

        # Mock LambdaTask.query.get to return the new_task when invoked with id=789
        mock_query.get.return_value = new_task

        result = check_and_invoke_lambda_task()

        assert result == new_task
        mock_query.filter.assert_called_once()
        mock_filter.order_by.assert_called_once()
        mock_order_by.first.assert_called_once()

        # Verify that a new task was created and added to the session
        mock_lambda_task_constructor.assert_called_once_with(
            status="Pending",
            created_on=fixed_datetime,
            updated_on=fixed_datetime,
        )
        mock_db_session.add.assert_called_once_with(new_task)
        # One for adding, one for updating status
        assert mock_db_session.commit.call_count == 2

        mock_boto3_client.assert_called_once_with("lambda")
        mock_lambda_client.invoke.assert_called_once_with(
            FunctionName=app.config["LAMBDA_FUNCTION_NAME"],
            InvocationType="Event",
            Payload=b'{"function_id": 789}',
        )

        # Verify that the task status was updated to 'InProgress'
        new_task.status = "InProgress"
        new_task.updated_on = fixed_datetime
        mock_db_session.commit.assert_called_with()


def test_check_and_invoke_lambda_task_exception(
    app, mock_db_session, mock_query, mock_boto3_client, fixed_datetime
):
    # Set up the query chain to raise an exception
    mock_filter = mock_query.filter.return_value
    mock_order_by = mock_filter.order_by.return_value
    mock_order_by.first.side_effect = Exception("DB query failed")

    result = check_and_invoke_lambda_task()

    assert result is None
    mock_query.filter.assert_called_once()
    mock_filter.order_by.assert_called_once()
    mock_order_by.first.assert_called_once()

    mock_db_session.rollback.assert_called_once()
    mock_boto3_client.assert_not_called()
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()


def test_invoke_lambda_task_success(
    app, mock_db_session, mock_query, mock_boto3_client, fixed_datetime
):
    function_id = 101

    # Create a mock LambdaTask instance to be returned by query.get()
    mock_task = MagicMock(spec=LambdaTask)
    mock_task.id = function_id
    mock_task.status = "Pending"
    mock_task.updated_on = fixed_datetime

    mock_query.get.return_value = mock_task

    # Mock boto3 Lambda client
    mock_lambda_client = MagicMock()
    mock_boto3_client.return_value = mock_lambda_client
    mock_lambda_client.invoke.return_value = {"StatusCode": 202}

    result = invoke_lambda_task(function_id)

    assert result == mock_task
    mock_query.get.assert_called_once_with(function_id)

    mock_boto3_client.assert_called_once_with("lambda")
    mock_lambda_client.invoke.assert_called_once_with(
        FunctionName=app.config["LAMBDA_FUNCTION_NAME"],
        InvocationType="Event",
        Payload=b'{"function_id": 101}',
    )

    # Verify that the task status was updated to 'InProgress'
    mock_task.status = "InProgress"
    mock_task.updated_on = fixed_datetime
    mock_db_session.commit.assert_called_once()


def test_invoke_lambda_task_missing_function_name(
    app, mock_db_session, mock_query, mock_boto3_client, fixed_datetime
):
    function_id = 202
    app.config["LAMBDA_FUNCTION_NAME"] = None

    # Create a mock LambdaTask instance to be returned by query.get()
    mock_task = MagicMock(spec=LambdaTask)
    mock_task.id = function_id
    mock_task.status = "Pending"
    mock_task.updated_on = fixed_datetime

    mock_query.get.return_value = mock_task

    result = invoke_lambda_task(function_id)

    assert result == mock_task
    mock_query.get.assert_called_once_with(function_id)

    # Since LAMBDA_FUNCTION_NAME is not configured, boto3 client should not be called
    mock_boto3_client.assert_called_once_with("lambda")
    mock_boto3_client.return_value.invoke.assert_not_called()

    # Verify that the task status was updated to 'Failed'
    mock_task.status = "Failed"
    mock_task.error_code = "LAMBDA_FUNCTION_NAME is not configured."
    mock_task.updated_on = fixed_datetime
    mock_db_session.commit.assert_called_once()


def test_invoke_lambda_task_lambda_invoke_exception(
    app, mock_db_session, mock_query, mock_boto3_client, fixed_datetime
):
    function_id = 303

    # Create a mock LambdaTask instance to be returned by query.get()
    mock_task = MagicMock(spec=LambdaTask)
    mock_task.id = function_id
    mock_task.status = "Pending"
    mock_task.updated_on = fixed_datetime

    mock_query.get.return_value = mock_task

    # Mock boto3 Lambda client to raise an exception on invoke
    mock_lambda_client = MagicMock()
    mock_boto3_client.return_value = mock_lambda_client
    mock_lambda_client.invoke.side_effect = Exception(
        "Lambda invocation failed"
    )

    result = invoke_lambda_task(function_id)

    assert result == mock_task
    mock_query.get.assert_called_once_with(function_id)

    mock_boto3_client.assert_called_once_with("lambda")
    mock_lambda_client.invoke.assert_called_once_with(
        FunctionName=app.config["LAMBDA_FUNCTION_NAME"],
        InvocationType="Event",
        Payload=b'{"function_id": 303}',
    )

    # Verify that the task status was updated to 'Failed' with the error code
    mock_task.status = "Failed"
    mock_task.error_code = "Lambda invocation failed"
    mock_task.updated_on = fixed_datetime
    mock_db_session.commit.assert_called_once()
