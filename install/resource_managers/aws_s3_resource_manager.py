import traceback

from botocore.exceptions import ClientError

from install.aws_providers.aws_client_provider import AwsClientProvider
from install.project_config import ProjectConfigProvider
from install.resource_managers.base_resource_manager import BaseResourceManager
from install.utils import Logger, Colorizer
from install.utils.exceptions import ResourceManagerError
from install.resource_managers.resource_manager_types import S3Object


class AwsS3ResourceManager(BaseResourceManager):
    def __init__(self, *,
            logger: Logger,
            config: ProjectConfigProvider,
            aws_client_provider: AwsClientProvider,
        ):
        self.logger = logger
        self.config = config
        self.client = aws_client_provider.s3_client

    @staticmethod
    def get_versions_from_response(response: dict) -> list[S3Object]:
        try:
            return [
                {"Key": obj["Key"], "VersionId": obj["VersionId"]}
                for obj in response["Versions"]
            ]
        except KeyError:
            return []    

    @staticmethod
    def get_delete_markers_from_response(response: dict) -> list[S3Object]:
        try:
            return [
                {"Key": obj["Key"], "VersionId": obj["VersionId"]}
                for obj in response["DeleteMarkers"]
            ]
        except KeyError:
            return []

    def empty_bucket(self, bucket_name: str) -> None:
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
                    }
                )
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(f"Error emptying bucket due to ClientError: {Colorizer.white(e)}")
            raise ResourceManagerError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Error emptying bucket due to unexpected error: {Colorizer.white(e)}")
            raise ResourceManagerError(e)

    def get_objects(self, bucket_name: str) -> list[S3Object]:
        try:
            response = self.client.list_object_versions(Bucket=bucket_name)
            objects = []
            while response["IsTruncated"]:
                objects.extend(self.get_versions_from_response(response))
                objects.extend(self.get_delete_markers_from_response(response))
                response = self.client.list_object_versions(
                    Bucket=bucket_name,
                    ContinuationToken=response["NextContinuationToken"]
                )
            objects.extend(self.get_versions_from_response(response))
            objects.extend(self.get_delete_markers_from_response(response))
            return objects
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(f"Error getting object keys due to ClientError: {Colorizer.white(e)}")
            raise ResourceManagerError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Error getting object keys due to unexpected error: {Colorizer.white(e)}")
            raise ResourceManagerError(e)

    def bucket_exists(self, bucket_name: str) -> bool:
        try:
            self.client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                self.logger.warning(f"Bucket {Colorizer.blue(bucket_name)} does not exist")
                return False
            self.logger.error(f"Error checking if bucket {Colorizer.blue(bucket_name)} exists due to ClientError: {Colorizer.white(e)}")
            raise ResourceManagerError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Error checking if bucket {Colorizer.blue(bucket_name)} exists due to unexpected error: {Colorizer.white(e)}")
            raise ResourceManagerError(e)

    def delete_bucket(self, bucket_name: str) -> None:
        try:
            response = self.client.delete_bucket(Bucket=bucket_name)
            return response
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(f"Error deleting bucket due to ClientError: {Colorizer.white(e)}")
            raise ResourceManagerError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Error deleting bucket due to unexpected error: {Colorizer.white(e)}")
            raise ResourceManagerError(e)

    def dev_uninstall(self) -> None:
        try:
            if self.bucket_exists(self.config.audio_bucket_name):
                self.empty_bucket(self.config.audio_bucket_name)
                self.delete_bucket(self.config.audio_bucket_name)
                self.logger(f"S3 bucket {Colorizer.blue(self.config.audio_bucket_name)} deleted")
        except ResourceManagerError:
            raise
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Error uninstalling S3 bucket {Colorizer.blue(self.config.audio_bucket_name)} due to unexpected error: {Colorizer.white(e)}")
            raise ResourceManagerError(e)

        try:
            if self.bucket_exists(self.config.logs_bucket_name):
                self.empty_bucket(self.config.logs_bucket_name)
                self.delete_bucket(self.config.logs_bucket_name)
                self.logger(f"S3 bucket {Colorizer.blue(self.config.logs_bucket_name)} deleted")
        except ResourceManagerError:
            raise
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Error uninstalling S3 bucket {Colorizer.blue(self.config.logs_bucket_name)} due to unexpected error: {Colorizer.white(e)}")
            raise ResourceManagerError(e)


if __name__ == "__main__":
    from install.installer import Installer
    installer = Installer("dev")
    installer.uninstall()
