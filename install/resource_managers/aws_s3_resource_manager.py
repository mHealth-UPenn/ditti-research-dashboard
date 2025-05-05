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

import traceback

from botocore.exceptions import ClientError

from install.aws_providers.aws_client_provider import AwsClientProvider
from install.project_config import ProjectConfigProvider
from install.resource_managers.base_resource_manager import BaseResourceManager
from install.resource_managers.resource_manager_types import S3Object
from install.utils import Colorizer, Logger
from install.utils.exceptions import ResourceManagerError


class AwsS3ResourceManager(BaseResourceManager):
    """
    Resource manager for AWS S3 operations.

    Manages S3 bucket creation, deletion, and object operations
    for application storage needs.
    """

    def __init__(
        self,
        *,
        logger: Logger,
        config: ProjectConfigProvider,
        aws_client_provider: AwsClientProvider,
    ):
        self.logger = logger
        self.config = config
        self.client = aws_client_provider.s3_client

    @staticmethod
    def get_versions_from_response(response: dict) -> list[S3Object]:
        """
        Extract version information from S3 list_object_versions response.

        Parameters
        ----------
        response : dict
            The response from S3 list_object_versions API call.

        Returns
        -------
        list[S3Object]
            List of S3 object versions.
        """
        try:
            return [
                {"Key": obj["Key"], "VersionId": obj["VersionId"]}
                for obj in response["Versions"]
            ]
        except KeyError:
            return []

    @staticmethod
    def get_delete_markers_from_response(response: dict) -> list[S3Object]:
        """
        Extract delete markers from S3 list_object_versions response.

        Parameters
        ----------
        response : dict
            The response from S3 list_object_versions API call.

        Returns
        -------
        list[S3Object]
            List of S3 delete markers.
        """
        try:
            return [
                {"Key": obj["Key"], "VersionId": obj["VersionId"]}
                for obj in response["DeleteMarkers"]
            ]
        except KeyError:
            return []

    def empty_bucket(self, bucket_name: str) -> None:
        """
        Remove all objects from an S3 bucket.

        Parameters
        ----------
        bucket_name : str
            The name of the bucket to empty.

        Returns
        -------
        None
        """
        try:
            objects = self.get_objects(bucket_name)
            if objects:
                self.client.delete_objects(
                    Bucket=bucket_name,
                    Delete={
                        "Objects": [
                            {"Key": obj["Key"], "VersionId": obj["VersionId"]}
                            for obj in objects
                        ]
                    },
                )
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(
                f"Error emptying bucket due to ClientError: {Colorizer.white(e)}"
            )
            raise ResourceManagerError(e) from e
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"Error emptying bucket due to unexpected error: "
                f"{Colorizer.white(e)}"
            )
            raise ResourceManagerError(e) from e

    def get_objects(self, bucket_name: str) -> list[S3Object]:
        """
        Get all objects in an S3 bucket.

        Parameters
        ----------
        bucket_name : str
            The name of the bucket to get objects from.

        Returns
        -------
        list[S3Object]
            List of objects in the bucket.
        """
        try:
            response = self.client.list_object_versions(Bucket=bucket_name)
            objects = []
            while response["IsTruncated"]:
                objects.extend(self.get_versions_from_response(response))
                objects.extend(self.get_delete_markers_from_response(response))
                response = self.client.list_object_versions(
                    Bucket=bucket_name,
                    ContinuationToken=response["NextContinuationToken"],
                )
            objects.extend(self.get_versions_from_response(response))
            objects.extend(self.get_delete_markers_from_response(response))
            return objects
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(
                f"Error getting object keys due to ClientError: "
                f"{Colorizer.white(e)}"
            )
            raise ResourceManagerError(e) from e
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"Error getting object keys due to unexpected error: "
                f"{Colorizer.white(e)}"
            )
            raise ResourceManagerError(e) from e

    def bucket_exists(self, bucket_name: str) -> bool:
        """
        Check if an S3 bucket exists.

        Parameters
        ----------
        bucket_name : str
            The name of the bucket to check.

        Returns
        -------
        bool
            True if the bucket exists, False otherwise.
        """
        try:
            self.client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                self.logger.warning(
                    f"Bucket {Colorizer.blue(bucket_name)} does not exist"
                )
                return False
            self.logger.error(
                f"Error checking if bucket {Colorizer.blue(bucket_name)} exists"
                f" due to ClientError: {Colorizer.white(e)}"
            )
            raise ResourceManagerError(e) from e
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"Error checking if bucket {Colorizer.blue(bucket_name)} exists"
                f" due to unexpected error: {Colorizer.white(e)}"
            )
            raise ResourceManagerError(e) from e

    def delete_bucket(self, bucket_name: str) -> None:
        """
        Delete an S3 bucket.

        Parameters
        ----------
        bucket_name : str
            The name of the bucket to delete.

        Returns
        -------
        None
        """
        try:
            response = self.client.delete_bucket(Bucket=bucket_name)
            return response
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(
                f"Error deleting bucket due to ClientError: {Colorizer.white(e)}"
            )
            raise ResourceManagerError(e) from e
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"Error deleting bucket due to unexpected error: "
                f"{Colorizer.white(e)}"
            )
            raise ResourceManagerError(e) from e

    def dev_uninstall(self) -> None:
        """
        Clean up S3 resources for development environment.

        Removes buckets created for the development environment.

        Returns
        -------
        None
        """
        try:
            if self.bucket_exists(self.config.audio_bucket_name):
                self.empty_bucket(self.config.audio_bucket_name)
                self.delete_bucket(self.config.audio_bucket_name)
                self.logger(
                    "S3 bucket "
                    f"{Colorizer.blue(self.config.audio_bucket_name)} deleted"
                )
        except ResourceManagerError:
            raise
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"Error uninstalling S3 bucket "
                f"{Colorizer.blue(self.config.audio_bucket_name)} due "
                f"to unexpected error: {Colorizer.white(e)}"
            )
            raise ResourceManagerError(e) from e

        try:
            if self.bucket_exists(self.config.logs_bucket_name):
                self.empty_bucket(self.config.logs_bucket_name)
                self.delete_bucket(self.config.logs_bucket_name)
                self.logger(
                    f"S3 bucket {Colorizer.blue(self.config.logs_bucket_name)}"
                    " deleted"
                )
        except ResourceManagerError:
            raise
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"Error uninstalling S3 bucket "
                f"{Colorizer.blue(self.config.logs_bucket_name)} due "
                f"to unexpected error: {Colorizer.white(e)}"
            )
            raise ResourceManagerError(e) from e


if __name__ == "__main__":
    from install.installer import Installer

    installer = Installer("dev")
    installer.uninstall()
