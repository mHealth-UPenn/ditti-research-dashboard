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

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
RESET='\033[0m'

# Read the project-settings-dev.json file
if [[ ! -f "project-config.json" ]]; then
    echo -e "${RED}Project settings file not found${RESET}"
    echo "Did you run install-dev.sh?"
    exit 1
fi

project_settings=$(cat "project-config.json")
dev_secret_name=$(echo "$project_settings" | jq -r '.aws.secrets_manager.secret_name')
postgres_container_name=$(echo "$project_settings" | jq -r '.docker.postgres_container_name')
wearable_data_retrieval_container_name=$(echo "$project_settings" | jq -r '.docker.wearable_data_retrieval_container_name')

# Enter the python virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Entering Python virtual environment..."
    source env/bin/activate
fi

# Retrieve secret value using AWS CLI
secret_json=$(aws secretsmanager get-secret-value --secret-id "$dev_secret_name" --query 'SecretString' --output text)

if [[ -z "$secret_json" ]]; then
    echo -e "${RED}Failed to retrieve secret or secret is empty.${RESET}"
else
    # Create a temporary file to store the environment variables
    temp_env_file=$(mktemp)
    
    # Parse the JSON and write environment variable assignments to the temporary file
    echo "$secret_json" | jq -r 'to_entries | .[] | "\(.key)=\(.value)"' > "$temp_env_file"
    
    # Source the temporary file to set environment variables in the current shell
    set -a
    source "$temp_env_file"
    set +a
    
    # Clean up the temporary file
    rm "$temp_env_file"
fi

echo -e "Loaded environment variables from ${BLUE}$dev_secret_name${RESET}"

# Start docker containers

postgres_container_status=$(docker inspect $postgres_container_name | jq -r '.[0].State.Status')

if [[ $? -ne 0 ]]; then
    echo -e "${RED}Failed to get postgres container status${RESET}"
    echo "Did you run install-dev.sh?"
    exit 1
fi

if [[ "$postgres_container_status" == "exited" ]]; then
    postgres_container_start_response=$(docker start $postgres_container_name)
    if [[ $? -ne 0 ]]; then
        echo "$postgres_container_start_response"
        echo -e "${RED}Failed to start postgres container${RESET}"
        exit 1
    fi
fi

echo -e "Started ${BLUE}$postgres_container_name${RESET}"

wearable_data_retrieval_container_status=$(docker inspect $wearable_data_retrieval_container_name | jq -r '.[0].State.Status')

if [[ $? -ne 0 ]]; then
    echo -e "${RED}Failed to get wearable data retrieval container status${RESET}"
    echo "Did you run install-dev.sh?"
    exit 1
fi

if [[ "$wearable_data_retrieval_container_status" == "exited" ]]; then
    wearable_data_retrieval_container_start_response=$(docker start $wearable_data_retrieval_container_name)
    if [[ $? -ne 0 ]]; then
        echo "$wearable_data_retrieval_container_start_response"
        echo -e "${RED}Failed to start wearable data retrieval container${RESET}"
        exit 1
    fi
fi

echo -e "Started ${BLUE}$wearable_data_retrieval_container_name${RESET}"

echo -e "${GREEN}Dev environment deployed${RESET}"

# Enable SQLAlchemy 2.0 deprecation warnings
export SQLALCHEMY_WARN_20=1

# Run Flask with warnings enabled for SQLAlchemy 2.0 deprecations
# You can change 'always' to 'error' (e.g., -W error::sqlalchemy.exc.RemovedIn20Warning) 
# to treat these warnings as exceptions for easier debugging.
python -W always::DeprecationWarning -m flask run
