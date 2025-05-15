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

from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from install.resource_managers.aws_s3_resource_manager import (
    AwsS3ResourceManager,
)
from install.utils.exceptions import ResourceManagerError
from tests.tests_install.tests_resource_managers.mock_aws_s3_resource_manager import (
    aws_s3_resource_manager,
)


@pytest.fixture
def aws_s3_resource_manager_mock():
    return aws_s3_resource_manager()


def test_get_versions_from_response():
    response = {
        "Versions": [
            {"Key": "test.txt", "VersionId": "v1"},
            {"Key": "test2.txt", "VersionId": "v2"},
        ]
    }
    result = AwsS3ResourceManager.get_versions_from_response(response)
    assert result == [
        {"Key": "test.txt", "VersionId": "v1"},
        {"Key": "test2.txt", "VersionId": "v2"},
    ]


def test_get_versions_from_response_empty():
    response = {}
    result = AwsS3ResourceManager.get_versions_from_response(response)
    assert result == []


def test_get_delete_markers_from_response():
    response = {
        "DeleteMarkers": [
            {"Key": "test.txt", "VersionId": "v1"},
            {"Key": "test2.txt", "VersionId": "v2"},
        ]
    }
    result = AwsS3ResourceManager.get_delete_markers_from_response(response)
    assert result == [
        {"Key": "test.txt", "VersionId": "v1"},
        {"Key": "test2.txt", "VersionId": "v2"},
    ]


def test_get_delete_markers_from_response_empty():
    response = {}
    result = AwsS3ResourceManager.get_delete_markers_from_response(response)
    assert result == []


def test_empty_bucket(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.get_objects = MagicMock(
        return_value=[
            {"Key": "test.txt", "VersionId": "v1"},
            {"Key": "test2.txt", "VersionId": "v2"},
        ]
    )
    aws_s3_resource_manager_mock.client.delete_objects = MagicMock()
    aws_s3_resource_manager_mock.empty_bucket("test_bucket")
    aws_s3_resource_manager_mock.client.delete_objects.assert_called_with(
        Bucket="test_bucket",
        Delete={
            "Objects": [
                {"Key": "test.txt", "VersionId": "v1"},
                {"Key": "test2.txt", "VersionId": "v2"},
            ]
        },
    )


def test_empty_bucket_empty_list(
    aws_s3_resource_manager_mock: AwsS3ResourceManager,
):
    aws_s3_resource_manager_mock.get_objects = MagicMock(return_value=[])
    aws_s3_resource_manager_mock.client.delete_objects = MagicMock()
    aws_s3_resource_manager_mock.empty_bucket("test_bucket")
    aws_s3_resource_manager_mock.client.delete_objects.assert_not_called()


def test_empty_bucket_client_error(
    aws_s3_resource_manager_mock: AwsS3ResourceManager,
):
    aws_s3_resource_manager_mock.get_objects = MagicMock(
        return_value=[{"Key": "test.txt", "VersionId": "v1"}]
    )
    aws_s3_resource_manager_mock.client.delete_objects = MagicMock(
        side_effect=ClientError({"Error": {"Code": "404"}}, "DeleteObjects")
    )
    with pytest.raises(ResourceManagerError, match="DeleteObjects"):
        aws_s3_resource_manager_mock.empty_bucket("test_bucket")


def test_empty_bucket_unexpected_error(
    aws_s3_resource_manager_mock: AwsS3ResourceManager,
):
    aws_s3_resource_manager_mock.get_objects = MagicMock(
        return_value=[{"Key": "test.txt", "VersionId": "v1"}]
    )
    aws_s3_resource_manager_mock.client.delete_objects = MagicMock(
        side_effect=Exception("Unexpected error")
    )
    with pytest.raises(ResourceManagerError, match="Unexpected error"):
        aws_s3_resource_manager_mock.empty_bucket("test_bucket")


def test_get_objects(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.client.list_object_versions = MagicMock(
        return_value={
            "Versions": [{"Key": "test.txt", "VersionId": "v1"}],
            "DeleteMarkers": [{"Key": "test2.txt", "VersionId": "v2"}],
            "IsTruncated": False,
        }
    )
    result = aws_s3_resource_manager_mock.get_objects("test_bucket")
    assert result == [
        {"Key": "test.txt", "VersionId": "v1"},
        {"Key": "test2.txt", "VersionId": "v2"},
    ]


def test_get_objects_with_truncated_response(
    aws_s3_resource_manager_mock: AwsS3ResourceManager,
):
    aws_s3_resource_manager_mock.client.list_object_versions = MagicMock(
        side_effect=[
            {
                "Versions": [{"Key": "test.txt", "VersionId": "v1"}],
                "DeleteMarkers": [],
                "IsTruncated": True,
                "NextContinuationToken": "token",
            },
            {
                "Versions": [{"Key": "test2.txt", "VersionId": "v2"}],
                "DeleteMarkers": [],
                "IsTruncated": False,
            },
        ]
    )
    result = aws_s3_resource_manager_mock.get_objects("test_bucket")
    assert result == [
        {"Key": "test.txt", "VersionId": "v1"},
        {"Key": "test2.txt", "VersionId": "v2"},
    ]


def test_get_objects_client_error(
    aws_s3_resource_manager_mock: AwsS3ResourceManager,
):
    aws_s3_resource_manager_mock.client.list_object_versions = MagicMock(
        side_effect=ClientError({"Error": {"Code": "404"}}, "ListObjectVersions")
    )
    with pytest.raises(ResourceManagerError, match="ListObjectVersions"):
        aws_s3_resource_manager_mock.get_objects("test_bucket")


def test_get_objects_unexpected_error(
    aws_s3_resource_manager_mock: AwsS3ResourceManager,
):
    aws_s3_resource_manager_mock.client.list_object_versions = MagicMock(
        side_effect=Exception("Unexpected error")
    )
    with pytest.raises(ResourceManagerError, match="Unexpected error"):
        aws_s3_resource_manager_mock.get_objects("test_bucket")


def test_bucket_exists(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.client.head_bucket = MagicMock()
    assert aws_s3_resource_manager_mock.bucket_exists("test_bucket")


def test_bucket_not_exists(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.client.head_bucket = MagicMock(
        side_effect=ClientError({"Error": {"Code": "404"}}, "HeadBucket")
    )
    assert not aws_s3_resource_manager_mock.bucket_exists("test_bucket")


def test_bucket_exists_client_error(
    aws_s3_resource_manager_mock: AwsS3ResourceManager,
):
    aws_s3_resource_manager_mock.client.head_bucket = MagicMock(
        side_effect=ClientError({"Error": {"Code": "403"}}, "HeadBucket")
    )
    with pytest.raises(ResourceManagerError, match="HeadBucket"):
        aws_s3_resource_manager_mock.bucket_exists("test_bucket")


def test_bucket_exists_unexpected_error(
    aws_s3_resource_manager_mock: AwsS3ResourceManager,
):
    aws_s3_resource_manager_mock.client.head_bucket = MagicMock(
        side_effect=Exception("Unexpected error")
    )
    with pytest.raises(ResourceManagerError, match="Unexpected error"):
        aws_s3_resource_manager_mock.bucket_exists("test_bucket")


def test_delete_bucket(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.client.delete_bucket = MagicMock()
    aws_s3_resource_manager_mock.delete_bucket("test_bucket")
    aws_s3_resource_manager_mock.client.delete_bucket.assert_called_with(
        Bucket="test_bucket"
    )


def test_delete_bucket_client_error(
    aws_s3_resource_manager_mock: AwsS3ResourceManager,
):
    aws_s3_resource_manager_mock.client.delete_bucket = MagicMock(
        side_effect=ClientError({"Error": {"Code": "404"}}, "DeleteBucket")
    )
    with pytest.raises(ResourceManagerError, match="DeleteBucket"):
        aws_s3_resource_manager_mock.delete_bucket("test_bucket")


def test_delete_bucket_unexpected_error(
    aws_s3_resource_manager_mock: AwsS3ResourceManager,
):
    aws_s3_resource_manager_mock.client.delete_bucket = MagicMock(
        side_effect=Exception("Unexpected error")
    )
    with pytest.raises(ResourceManagerError, match="Unexpected error"):
        aws_s3_resource_manager_mock.delete_bucket("test_bucket")


def test_dev_uninstall(aws_s3_resource_manager_mock: AwsS3ResourceManager):
    aws_s3_resource_manager_mock.bucket_exists = MagicMock(return_value=True)
    aws_s3_resource_manager_mock.empty_bucket = MagicMock()
    aws_s3_resource_manager_mock.delete_bucket = MagicMock()
    aws_s3_resource_manager_mock.dev_uninstall()
    aws_s3_resource_manager_mock.empty_bucket.assert_any_call(
        aws_s3_resource_manager_mock.config.audio_bucket_name
    )
    aws_s3_resource_manager_mock.delete_bucket.assert_any_call(
        aws_s3_resource_manager_mock.config.audio_bucket_name
    )
    aws_s3_resource_manager_mock.empty_bucket.assert_any_call(
        aws_s3_resource_manager_mock.config.logs_bucket_name
    )
    aws_s3_resource_manager_mock.delete_bucket.assert_any_call(
        aws_s3_resource_manager_mock.config.logs_bucket_name
    )


def test_dev_uninstall_bucket_not_exists(
    aws_s3_resource_manager_mock: AwsS3ResourceManager,
):
    aws_s3_resource_manager_mock.bucket_exists = MagicMock(return_value=False)
    aws_s3_resource_manager_mock.empty_bucket = MagicMock()
    aws_s3_resource_manager_mock.delete_bucket = MagicMock()
    aws_s3_resource_manager_mock.dev_uninstall()
    aws_s3_resource_manager_mock.empty_bucket.assert_not_called()
    aws_s3_resource_manager_mock.delete_bucket.assert_not_called()


def test_dev_uninstall_resource_manager_error(
    aws_s3_resource_manager_mock: AwsS3ResourceManager,
):
    aws_s3_resource_manager_mock.bucket_exists = MagicMock(return_value=True)
    aws_s3_resource_manager_mock.empty_bucket = MagicMock(
        side_effect=ResourceManagerError("Resource manager error")
    )
    with pytest.raises(ResourceManagerError, match="Resource manager error"):
        aws_s3_resource_manager_mock.dev_uninstall()


def test_dev_uninstall_unexpected_error(
    aws_s3_resource_manager_mock: AwsS3ResourceManager,
):
    aws_s3_resource_manager_mock.bucket_exists = MagicMock(return_value=True)
    aws_s3_resource_manager_mock.empty_bucket = MagicMock(
        side_effect=Exception("Unexpected error")
    )
    with pytest.raises(ResourceManagerError, match="Unexpected error"):
        aws_s3_resource_manager_mock.dev_uninstall()
