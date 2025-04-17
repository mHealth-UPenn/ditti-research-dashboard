from unittest.mock import MagicMock

from botocore.exceptions import ClientError
import pytest

from install_scripts.resource_managers.aws_s3_resource_manager import AwsS3ResourceManager
from install_scripts.utils.exceptions import ResourceManagerError
from tests.tests_install_scripts.tests_resource_managers.mock_aws_s3_resource_manager import aws_s3_resource_manager


@pytest.fixture
def aws_s3_resource_manager_mock():
    return aws_s3_resource_manager()


def test_empty_bucket(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.get_object_keys = MagicMock(return_value=["test.txt"])
    aws_s3_resource_manager_mock.client.delete_object = MagicMock()
    aws_s3_resource_manager_mock.empty_bucket("test_bucket")
    aws_s3_resource_manager_mock.client.delete_object.assert_called_with(Bucket="test_bucket", Key="test.txt")


def test_empty_bucket_client_error(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.get_object_keys = MagicMock(return_value=["test.txt"])
    aws_s3_resource_manager_mock.client.delete_object = MagicMock(side_effect=ClientError({"Error": {"Code": "404"}}, "DeleteObject"))
    with pytest.raises(ResourceManagerError, match="DeleteObject"):
        aws_s3_resource_manager_mock.empty_bucket("test_bucket")


def test_empty_bucket_unexpected_error(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.get_object_keys = MagicMock(return_value=["test.txt"])
    aws_s3_resource_manager_mock.client.delete_object = MagicMock(side_effect=Exception("Unexpected error"))
    with pytest.raises(ResourceManagerError, match="Unexpected error"):
        aws_s3_resource_manager_mock.empty_bucket("test_bucket")


def test_get_object_keys(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.client.list_objects_v2 = MagicMock(return_value={"Contents": [{"Key": "test.txt"}], "IsTruncated": False})
    assert aws_s3_resource_manager_mock.get_object_keys("test_bucket") == ["test.txt"]


def test_get_object_keys_with_truncated_response(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.client.list_objects_v2 = MagicMock(side_effect=[
        {"Contents": [{"Key": "test.txt"}], "IsTruncated": True, "NextContinuationToken": "test_token"},
        {"Contents": [{"Key": "test2.txt"}], "IsTruncated": False},
    ])
    assert aws_s3_resource_manager_mock.get_object_keys("test_bucket") == ["test.txt", "test2.txt"]


def test_get_object_keys_client_error(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.client.list_objects_v2 = MagicMock(side_effect=ClientError({"Error": {"Code": "404"}}, "ListObjectsV2"))
    with pytest.raises(ResourceManagerError, match="ListObjectsV2"):
        aws_s3_resource_manager_mock.get_object_keys("test_bucket")


def test_get_object_keys_unexpected_error(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.client.list_objects_v2 = MagicMock(side_effect=Exception("Unexpected error"))
    with pytest.raises(ResourceManagerError, match="Unexpected error"):
        aws_s3_resource_manager_mock.get_object_keys("test_bucket")


def test_bucket_is_empty(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.client.list_objects_v2 = MagicMock(return_value={"KeyCount": 0})
    assert aws_s3_resource_manager_mock.bucket_is_empty("test_bucket")


def test_bucket_is_not_empty(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.client.list_objects_v2 = MagicMock(return_value={"KeyCount": 1})
    assert not aws_s3_resource_manager_mock.bucket_is_empty("test_bucket")


def test_bucket_is_empty_client_error(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.client.list_objects_v2 = MagicMock(side_effect=ClientError({"Error": {"Code": "404"}}, "ListObjectsV2"))
    with pytest.raises(ResourceManagerError, match="ListObjectsV2"):
        aws_s3_resource_manager_mock.bucket_is_empty("test_bucket")


def test_bucket_is_empty_unexpected_error(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.client.list_objects_v2 = MagicMock(side_effect=Exception("Unexpected error"))
    with pytest.raises(ResourceManagerError, match="Unexpected error"):
        aws_s3_resource_manager_mock.bucket_is_empty("test_bucket")


def test_delete_bucket(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.client.delete_bucket = MagicMock()
    aws_s3_resource_manager_mock.delete_bucket("test_bucket")
    aws_s3_resource_manager_mock.client.delete_bucket.assert_called_with(Bucket="test_bucket")


def test_delete_bucket_client_error(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.client.delete_bucket = MagicMock(side_effect=ClientError({"Error": {"Code": "404"}}, "DeleteBucket"))
    with pytest.raises(ResourceManagerError, match="DeleteBucket"):
        aws_s3_resource_manager_mock.delete_bucket("test_bucket")


def test_delete_bucket_unexpected_error(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.client.delete_bucket = MagicMock(side_effect=Exception("Unexpected error"))
    with pytest.raises(ResourceManagerError, match="Unexpected error"):
        aws_s3_resource_manager_mock.delete_bucket("test_bucket")


def test_dev_uninstall(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.empty_bucket = MagicMock()
    aws_s3_resource_manager_mock.delete_bucket = MagicMock()
    aws_s3_resource_manager_mock.dev_uninstall()
    aws_s3_resource_manager_mock.empty_bucket.assert_any_call(aws_s3_resource_manager_mock.settings.audio_bucket_name)
    aws_s3_resource_manager_mock.delete_bucket.assert_any_call(aws_s3_resource_manager_mock.settings.audio_bucket_name)
    aws_s3_resource_manager_mock.empty_bucket.assert_any_call(aws_s3_resource_manager_mock.settings.logs_bucket_name)
    aws_s3_resource_manager_mock.delete_bucket.assert_any_call(aws_s3_resource_manager_mock.settings.logs_bucket_name)


def test_dev_uninstall_resource_manager_error(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.empty_bucket = MagicMock(side_effect=ResourceManagerError("Resource manager error"))
    with pytest.raises(ResourceManagerError, match="Resource manager error"):
        aws_s3_resource_manager_mock.dev_uninstall()


def test_dev_uninstall_unexpected_error(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.empty_bucket = MagicMock(side_effect=Exception("Unexpected error"))
    with pytest.raises(ResourceManagerError, match="Unexpected error"):
        aws_s3_resource_manager_mock.dev_uninstall()
