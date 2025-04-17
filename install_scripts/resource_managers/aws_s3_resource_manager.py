import traceback

from botocore.exceptions import ClientError

from install_scripts.aws_providers.aws_client_provider import AwsClientProvider
from install_scripts.project_config import ProjectConfigProvider
from install_scripts.resource_managers.base_resource_manager import BaseResourceManager
from install_scripts.utils import Logger
from install_scripts.utils.exceptions import ResourceManagerError


class AwsS3ResourceManager(BaseResourceManager):
    def __init__(self, *,
            logger: Logger,
            settings: ProjectConfigProvider,
            aws_client_provider: AwsClientProvider,
        ):
        self.logger = logger
        self.settings = settings
        self.client = aws_client_provider.s3_client

    def empty_bucket(self, bucket_name: str) -> None:
        try:
            keys = self.get_object_keys(bucket_name)
            for key in keys:
                self.client.delete_object(Bucket=bucket_name, Key=key)
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(f"Error emptying bucket due to ClientError: {bucket_name}: {e}")
            raise ResourceManagerError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Error emptying bucket due to unexpected error: {bucket_name}: {e}")
            raise ResourceManagerError(e)

    def get_object_keys(self, bucket_name: str) -> list[str]:
        try:
            keys = []
            response = self.client.list_objects_v2(Bucket=bucket_name)
            while response["IsTruncated"]:
                keys.extend([obj["Key"] for obj in response["Contents"]])
                response = self.client.list_objects_v2(
                    Bucket=bucket_name,
                    ContinuationToken=response["NextContinuationToken"]
                )
            keys.extend([obj["Key"] for obj in response["Contents"]])
            return keys
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(f"Error getting object keys due to ClientError: {bucket_name}: {e}")
            raise ResourceManagerError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Error getting object keys due to unexpected error: {bucket_name}: {e}")
            raise ResourceManagerError(e)

    def bucket_is_empty(self, bucket_name: str) -> bool:
        try:
            response = self.client.list_objects_v2(Bucket=bucket_name)
            return response["KeyCount"] == 0
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(f"Error checking if bucket {bucket_name} is empty due to ClientError: {e}")
            raise ResourceManagerError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Error checking if bucket {bucket_name} is empty due to unexpected error: {e}")
            raise ResourceManagerError(e)

    def delete_bucket(self, bucket_name: str) -> None:
        try:
            response = self.client.delete_bucket(Bucket=bucket_name)
            return response
        except ClientError as e:
            traceback.print_exc()
            self.logger.error(f"Error deleting bucket due to ClientError: {bucket_name}: {e}")
            raise ResourceManagerError(e)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Error deleting bucket due to unexpected error: {bucket_name}: {e}")
            raise ResourceManagerError(e)

    def dev_uninstall(self) -> None:
        try:
            self.empty_bucket(self.settings.audio_bucket_name)
            self.delete_bucket(self.settings.audio_bucket_name)
            self.logger.blue(f"S3 bucket {self.settings.audio_bucket_name} deleted")
        except ResourceManagerError:
            raise
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Error uninstalling S3 bucket {self.settings.audio_bucket_name} due to unexpected error: {e}")
            raise ResourceManagerError(e)

        try:
            self.empty_bucket(self.settings.logs_bucket_name)
            self.delete_bucket(self.settings.logs_bucket_name)
            self.logger.blue(f"S3 bucket {self.settings.logs_bucket_name} deleted")
        except ResourceManagerError:
            raise
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Error uninstalling S3 bucket {self.settings.logs_bucket_name} due to unexpected error: {e}")
            raise ResourceManagerError(e)
