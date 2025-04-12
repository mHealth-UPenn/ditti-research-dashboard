#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
RESET='\033[0m'

if [ ! -f project-settings-dev.json ]; then
    echo -e "${RED}Project settings file not found${RESET}"
    echo "Did you run install-dev.sh?"
    exit 1
fi

echo
echo "This script will uninstall the development environment for the project."
echo -e "${MAGENTA}The following will be removed:${RESET}"
echo "- Docker containers"
echo "- Docker network"
echo "- AWS Cognito user pools and clients"
echo "- AWS S3 buckets"
echo "- AWS Secrets Manager secret"
echo "- Local .env files"
echo "- Project settings file"
echo "- Virtual environment"
echo "- Frontend build"
echo "- Frontend node_modules"
echo "- Frontend output.css"

read -ep "Do you want to continue? (y/n): " continue

if [ "$continue" != "y" ]; then
    echo -e "${RED}Uninstallation cancelled${RESET}"
    exit 1
fi

# Load project settings
project_settings=$(cat project-settings-dev.json)
participant_user_pool_domain=$(echo "$project_settings" | jq -r '.aws.cognito.participant_user_pool_domain')
researcher_user_pool_domain=$(echo "$project_settings" | jq -r '.aws.cognito.researcher_user_pool_domain')
participant_user_pool_id=$(echo "$project_settings" | jq -r '.aws.cognito.participant_user_pool_id')
researcher_user_pool_id=$(echo "$project_settings" | jq -r '.aws.cognito.researcher_user_pool_id')
logs_bucket_name=$(echo "$project_settings" | jq -r '.aws.s3.logs_bucket_name')
audio_bucket_name=$(echo "$project_settings" | jq -r '.aws.s3.audio_bucket_name')
dev_secret_name=$(echo "$project_settings" | jq -r '.aws.secrets_manager.dev_secret_name')
tokens_secret_name=$(echo "$project_settings" | jq -r '.aws.secrets_manager.tokens_secret_name')
network_name=$(echo "$project_settings" | jq -r '.docker.network')
postgres_container_name=$(echo "$project_settings" | jq -r '.docker.postgres_container_name')
wearable_data_retrieval_container_name=$(echo "$project_settings" | jq -r '.docker.wearable_data_retrieval_container_name')

has_errors=false

# Delete aws cognito domain and user pools
aws cognito-idp delete-user-pool-domain --user-pool-id $participant_user_pool_id --domain $participant_user_pool_domain

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to delete participant user pool domain${RESET}"
    has_errors=true
else
    echo -e "Deleted participant user pool domain ${BLUE}$participant_user_pool_domain${RESET}"
fi

aws cognito-idp delete-user-pool-domain --user-pool-id $researcher_user_pool_id --domain $researcher_user_pool_domain

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to delete researcher user pool domain${RESET}"
    has_errors=true
else
    echo -e "Deleted researcher user pool domain ${BLUE}$researcher_user_pool_domain${RESET}"
fi

aws cognito-idp delete-user-pool --user-pool-id $participant_user_pool_id

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to delete participant user pool${RESET}"
    has_errors=true
else
    echo -e "Deleted participant user pool ${BLUE}$participant_user_pool_id${RESET}"
fi

aws cognito-idp delete-user-pool --user-pool-id $researcher_user_pool_id

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to delete researcher user pool${RESET}"
    has_errors=true
else
    echo -e "Deleted researcher user pool ${BLUE}$researcher_user_pool_id${RESET}"
fi

# Delete aws s3 buckets
aws s3api delete-bucket --bucket $logs_bucket_name

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to delete logs bucket${RESET}"
    has_errors=true
else
    echo -e "Deleted logs bucket ${BLUE}$logs_bucket_name${RESET}"
fi

aws s3api delete-bucket --bucket $audio_bucket_name

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to delete audio bucket${RESET}"
    has_errors=true
else
    echo -e "Deleted audio bucket ${BLUE}$audio_bucket_name${RESET}"
fi

# Delete aws secrets manager secret
aws secretsmanager delete-secret --secret-id $dev_secret_name &> /dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to delete dev secret${RESET}"
    has_errors=true
else
    echo -e "Deleted dev secret ${BLUE}$dev_secret_name${RESET}"
fi

aws secretsmanager delete-secret --secret-id $tokens_secret_name &> /dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to delete tokens secret${RESET}"
    has_errors=true
else
    echo -e "Deleted tokens secret ${BLUE}$tokens_secret_name${RESET}"
fi

# Stop and remove containers
docker stop $postgres_container_name $wearable_data_retrieval_container_name

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to stop containers${RESET}"
    has_errors=true
fi

docker rm $postgres_container_name $wearable_data_retrieval_container_name

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to remove containers${RESET}"
    has_errors=true
else
    echo -e "Removed containers ${BLUE}$postgres_container_name${RESET} and ${BLUE}$wearable_data_retrieval_container_name${RESET}"
fi

# Delete docker network
docker network rm $network_name

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to delete network${RESET}"
    has_errors=true
else
    echo -e "Deleted network ${BLUE}$network_name${RESET}"
fi

# Delete project settings file
rm project-settings-dev.json

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to delete project settings file${RESET}"
    has_errors=true
else
    echo -e "Deleted project settings file ${BLUE}project-settings-dev.json${RESET}"
fi

# Delete virtual environment
rm -rf env

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to delete virtual environment${RESET}"
    has_errors=true
else
    echo -e "Deleted virtual environment ${BLUE}env${RESET}"
fi

# Delete .env files
rm .env

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to delete .env files${RESET}"
    has_errors=true
else
    echo -e "Deleted env file ${BLUE}.env${RESET}"
fi

rm functions/wearable_data_retrieval/.env

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to delete .env files${RESET}"
    has_errors=true
else
    echo -e "Deleted env file ${BLUE}functions/wearable_data_retrieval/.env${RESET}"
fi

# Delete frontend build
rm -rf frontend/build

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to delete frontend build${RESET}"
    has_errors=true
else
    echo -e "Deleted frontend build ${BLUE}frontend/build${RESET}"
fi

# Delete frontend node_modules
rm -rf frontend/node_modules

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to delete frontend node_modules${RESET}"
    has_errors=true
else
    echo -e "Deleted frontend node_modules ${BLUE}frontend/node_modules${RESET}"
fi

# Delete frontend output.css
rm frontend/src/output.css

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to delete frontend output.css${RESET}"
    has_errors=true
else
    echo -e "Deleted frontend output.css ${BLUE}frontend/src/output.css${RESET}"
fi

if [ $has_errors = false ]; then
    echo -e "${GREEN}Development environment uninstalled${RESET}"
else
    echo -e "${YELLOW}Uninstall completed with errors${RESET}"
fi
