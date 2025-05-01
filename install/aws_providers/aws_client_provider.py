# Ditti Research Dashboard
# Copyright (C) 2025 the Trustees of the University of Pennsylvania
#
# Ditti Research Dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Ditti Research Dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Any

import boto3


class AwsClientProvider:
    """
    Provider for AWS service clients.

    Creates and manages clients for various AWS services used
    during installation and configuration.
    """

    sts_client: Any
    cognito_client: Any
    s3_client: Any
    secrets_manager_client: Any
    cloudformation_client: Any
    ecr_client: Any

    # Unit test: boto3.client is initialized with expected arguments
    def __init__(self):
        self.sts_client = boto3.client("sts")
        self.cognito_client = boto3.client("cognito-idp")
        self.s3_client = boto3.client("s3")
        self.secrets_manager_client = boto3.client("secretsmanager")
        self.cloudformation_client = boto3.client("cloudformation")
        self.ecr_client = boto3.client("ecr")
