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

#!/bin/bash
# This script sets up environment variables for the deployed Flask staging environment
# Usage: source flask-staging.sh

# Set the local environment to staging
export FLASK_CONFIG=Production
export AWS_SECRET_NAME=secret-aws-portal-staging

# Export AWS secrets
export $(aws secretsmanager get-secret-value --secret-id $AWS_SECRET_NAME --query SecretString --output text | jq -r 'to_entries | map("\(.key)=\(.value|tostring)") | .[]')

# Export staging env file
export $(cat secret-staging.env | xargs)

echo "Environment variables set for staging."