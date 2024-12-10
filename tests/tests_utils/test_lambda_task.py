import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
from aws_portal.utils.lambda_task import (
    create_and_invoke_lambda_task,
    check_and_invoke_lambda_task,
    invoke_lambda_task
)
from aws_portal.models import LambdaTask
from flask import Flask
from freezegun import freeze_time


@pytest.fixture
def app():
    """
    Creates a Flask app instance for testing and pushes an application context.
    """
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['ENV'] = 'testing'
    app.config['LAMBDA_FUNCTION_NAME'] = 'test_lambda_function'

    with app.app_context():
        yield app


@pytest.fixture
def mock_db_session():
    with patch('aws_portal.utils.lambda_task.db.session') as mock_session:
        yield mock_session


@pytest.fixture
def mock_lambda_task_model():
    with patch('aws_portal.utils.lambda_task.LambdaTask') as mock_model:
        yield mock_model


@pytest.fixture
def mock_boto3_client():
    with patch('aws_portal.utils.lambda_task.boto3.client') as mock_client:
        yield mock_client


@pytest.fixture
def fixed_datetime():
    fixed_time = datetime(2024, 12, 1, 12, 0, 0, tzinfo=timezone.utc)
    with freeze_time(fixed_time):
        yield fixed_time


def test_create_and_invoke_lambda_task_success(
    app, mock_db_session, mock_lambda_task_model, mock_boto3_client, fixed_datetime
):
    mock_task_instance = MagicMock(spec=LambdaTask)
    mock_task_instance.id = 123
    mock_lambda_task_model.return_value = mock_task_instance

    mock_lambda_client = MagicMock()
    mock_boto3_client.return_value = mock_lambda_client
    mock_lambda_client.invoke.return_value = {"StatusCode": 202}

    result = create_and_invoke_lambda_task()

    assert result == mock_task_instance
    mock_db_session.add.assert_called_once_with(mock_task_instance)
    # One in create_and_invoke_lambda_task and one in invoke_lambda_task
    assert mock_db_session.commit.call_count == 2
    mock_boto3_client.assert_called_once_with("lambda")
    mock_lambda_client.invoke.assert_called_once_with(
        FunctionName=app.config['LAMBDA_FUNCTION_NAME'],
        InvocationType="Event",
        Payload=b'{"function_id": 123}'
    )
    mock_lambda_task_model.assert_called_once_with(
        status="Pending",
        created_on=fixed_datetime,
        updated_on=fixed_datetime
    )


def test_create_and_invoke_lambda_task_exception(
    app, mock_db_session, mock_lambda_task_model, mock_boto3_client, fixed_datetime
):
    mock_db_session.commit.side_effect = Exception("DB commit failed")

    result = create_and_invoke_lambda_task()

    assert result is None
    mock_db_session.rollback.assert_called_once()


def test_check_and_invoke_lambda_task_already_run_today(
    app, mock_db_session, mock_lambda_task_model, mock_boto3_client, fixed_datetime
):
    mock_latest_task = MagicMock(spec=LambdaTask)
    mock_latest_task.created_on.date.return_value = fixed_datetime.date()
    mock_lambda_task_model.query.order_by.return_value.first.return_value = mock_latest_task

    result = check_and_invoke_lambda_task()

    assert result == mock_latest_task
    mock_lambda_task_model.query.order_by.assert_called_once()
    # Assuming that the code calls .order_by().first()
    mock_lambda_task_model.query.first.assert_not_called()
    mock_boto3_client.return_value.invoke.assert_not_called()
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()


def test_check_and_invoke_lambda_task_not_run_today(
    app, mock_db_session, mock_lambda_task_model, mock_boto3_client, fixed_datetime
):
    mock_latest_task = MagicMock(spec=LambdaTask)
    mock_latest_task.created_on.date.return_value = (
        fixed_datetime - timedelta(days=1)).date()
    mock_lambda_task_model.query.order_by.return_value.first.return_value = mock_latest_task

    new_task = MagicMock(spec=LambdaTask)
    new_task.id = 456
    mock_lambda_task_model.return_value = new_task

    mock_lambda_client = MagicMock()
    mock_boto3_client.return_value = mock_lambda_client
    mock_lambda_client.invoke.return_value = {"StatusCode": 202}

    result = check_and_invoke_lambda_task()

    assert result == new_task
    mock_lambda_task_model.query.order_by.assert_called_once()
    mock_db_session.add.assert_called_once_with(new_task)
    # One for adding the new task, one in invoke_lambda_task
    assert mock_db_session.commit.call_count == 2
    mock_boto3_client.assert_called_once_with("lambda")
    mock_lambda_client.invoke.assert_called_once_with(
        FunctionName=app.config['LAMBDA_FUNCTION_NAME'],
        InvocationType="Event",
        Payload=b'{"function_id": 456}'
    )
    mock_lambda_task_model.assert_called_once_with(
        status="Pending",
        created_on=fixed_datetime,
        updated_on=fixed_datetime
    )


def test_check_and_invoke_lambda_task_no_tasks(
    app, mock_db_session, mock_lambda_task_model, mock_boto3_client, fixed_datetime
):
    mock_lambda_task_model.query.order_by.return_value.first.return_value = None

    new_task = MagicMock(spec=LambdaTask)
    new_task.id = 789
    mock_lambda_task_model.return_value = new_task

    mock_lambda_client = MagicMock()
    mock_boto3_client.return_value = mock_lambda_client
    mock_lambda_client.invoke.return_value = {"StatusCode": 202}

    result = check_and_invoke_lambda_task()

    assert result == new_task
    mock_lambda_task_model.query.order_by.assert_called_once()
    mock_db_session.add.assert_called_once_with(new_task)
    # One for adding the new task, one in invoke_lambda_task
    assert mock_db_session.commit.call_count == 2
    mock_boto3_client.assert_called_once_with("lambda")
    mock_lambda_client.invoke.assert_called_once_with(
        FunctionName=app.config['LAMBDA_FUNCTION_NAME'],
        InvocationType="Event",
        Payload=b'{"function_id": 789}'
    )
    mock_lambda_task_model.assert_called_once_with(
        status="Pending",
        created_on=fixed_datetime,
        updated_on=fixed_datetime
    )


def test_check_and_invoke_lambda_task_exception(
    app, mock_db_session, mock_lambda_task_model, mock_boto3_client, fixed_datetime
):
    mock_lambda_task_model.query.order_by.side_effect = Exception(
        "DB query failed")

    result = check_and_invoke_lambda_task()

    assert result is None
    mock_db_session.rollback.assert_called_once()


def test_invoke_lambda_task_success(
    app, mock_db_session, mock_lambda_task_model, mock_boto3_client, fixed_datetime
):
    function_id = 101
    mock_task = MagicMock(spec=LambdaTask)
    mock_lambda_task_model.query.get.return_value = mock_task

    mock_lambda_client = MagicMock()
    mock_boto3_client.return_value = mock_lambda_client
    mock_lambda_client.invoke.return_value = {"StatusCode": 202}

    result = invoke_lambda_task(function_id)

    assert result == mock_task
    mock_boto3_client.assert_called_once_with("lambda")
    mock_lambda_client.invoke.assert_called_once_with(
        FunctionName=app.config['LAMBDA_FUNCTION_NAME'],
        InvocationType="Event",
        Payload=b'{"function_id": 101}'
    )
    mock_task.status = "InProgress"
    mock_task.updated_on = fixed_datetime
    mock_db_session.commit.assert_called_once()


def test_invoke_lambda_task_missing_function_name(
    app, mock_db_session, mock_lambda_task_model, mock_boto3_client, fixed_datetime
):
    function_id = 202
    app.config["LAMBDA_FUNCTION_NAME"] = None

    mock_task = MagicMock(spec=LambdaTask)
    mock_lambda_task_model.query.get.return_value = mock_task

    result = invoke_lambda_task(function_id)

    assert result == mock_task
    mock_lambda_task_model.query.get.assert_called_once_with(function_id)
    mock_boto3_client.assert_called_once_with("lambda")
    mock_lambda_client = mock_boto3_client.return_value
    mock_lambda_client.invoke.assert_not_called()
    mock_task.status = "Failed"
    mock_task.error_code = "LAMBDA_FUNCTION_NAME is not configured."
    mock_task.updated_on = fixed_datetime
    mock_db_session.commit.assert_called_once()


def test_invoke_lambda_task_lambda_invoke_exception(
    app, mock_db_session, mock_lambda_task_model, mock_boto3_client, fixed_datetime
):
    function_id = 303
    mock_task = MagicMock(spec=LambdaTask)
    mock_lambda_task_model.query.get.return_value = mock_task

    mock_lambda_client = MagicMock()
    mock_boto3_client.return_value = mock_lambda_client
    mock_lambda_client.invoke.side_effect = Exception(
        "Lambda invocation failed")

    result = invoke_lambda_task(function_id)

    assert result == mock_task
    mock_boto3_client.assert_called_once_with("lambda")
    mock_lambda_client.invoke.assert_called_once_with(
        FunctionName=app.config['LAMBDA_FUNCTION_NAME'],
        InvocationType="Event",
        Payload=b'{"function_id": 303}'
    )
    mock_task.status = "Failed"
    mock_task.error_code = "Lambda invocation failed"
    mock_task.updated_on = fixed_datetime
    mock_db_session.commit.assert_called_once()
