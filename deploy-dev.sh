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
    # Parse the JSON and export key-value pairs as environment variables
    echo "$secret_json" | jq -r 'to_entries | .[] | "export \(.key)=\(.value)"' | while read -r env_var; do
    eval "$env_var"
    done
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

flask run
