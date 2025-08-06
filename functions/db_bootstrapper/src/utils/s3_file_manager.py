# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# Disable linter warnings for print statements (quick fix for logging issues with alembic)
# ruff: noqa: T201

import boto3


class S3FileManager:
    """AWS S3 file manager implementation."""

    def __init__(self):
        """
        Initialize the AWS S3 file manager.

        Args:
            client: Boto3 S3 client instance.
        """
        self.client = boto3.client("s3")

    def download_file(self, data_arn: str, local_path: str) -> str:
        """
        Download a file from S3 to local storage.

        Args:
            data_arn: The S3 ARN of the file to download.
            local_path: The local path where the file should be saved.

        Returns
        -------
            The local path where the file was saved.
        """
        try:
            bucket, key = data_arn.split(":")[-1].split("/")
            self.client.download_file(
                Bucket=bucket,
                Key=key,
                Filename=local_path,
            )
            return local_path
        except Exception as e:
            print(f"Error saving data file: {e}")
            raise
