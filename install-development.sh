#!/bin/bash

RED='\033[0;31m'
GREEN=['\033[]0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
RESET='\033[0m'

########################################################
# AWS CLI setup                                        #
########################################################
echo -e "\n${CYAN}[AWS CLI Setup]${RESET}"
aws configure

aws_access_key_id=$(aws configure get aws_access_key_id)
aws_secret_access_key=$(aws configure get aws_secret_access_key)
aws_region=$(aws configure get region)

########################################################
# Project setup                                       #
########################################################
# Prompt the user for a name for their project
echo -e "\n${CYAN}[Project Setup]${RESET}"
read -ep "Enter a name for your project: " project_name

# Prompt the user for fitbit credentials
echo -e "\n${CYAN}[Fitbit Setup]${RESET}"
read -ep "Enter your Fitbit client ID: " fitbit_client_id
read -ep "Enter your Fitbit client secret: " fitbit_client_secret

# Prompt the user for an email to login as admin
echo -e "\n${CYAN}[Admin Setup]${RESET}"
read -ep "Enter an email to login as admin: " admin_email
echo -n "Enter a temporary password for the admin user: "
read -s admin_password
echo
echo -n "Confirm the temporary password for the admin user: "
read -s admin_password_confirm
echo

if [ "$admin_password" != "$admin_password_confirm" ]; then
    echo -e "${RED}Passwords do not match${RESET}"
    exit 1
fi

########################################################
# Python setup                                         #
########################################################
echo -e "\n${CYAN}[Python Setup]${RESET}"

if [ ! -f env/bin/activate ]; then
    echo "Initializing Python virtual environment..."
    python3.13 -m venv env
fi

if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Entering Python virtual environment..."
    source env/bin/activate
fi

echo "Installing Python packages"
pip install -r requirements.txt | tail -n 10

if [ $? -ne 0 ]; then
    echo -e "${RED}Python setup failed${RESET}"
    exit 1
fi

echo -e "${GREEN}[Python setup complete]${RESET}"

########################################################
# Cognito setup                                        #
########################################################
echo -e "\n${CYAN}[Cognito Setup]${RESET}"

# Create a participant Cognito user pool
echo "Creating a participant Cognito user pool"
participant_user_pool_response=$(
    aws cognito-idp create-user-pool \
        --pool-name "$project_name-participant-pool-dev" \
        --policies "PasswordPolicy={
            MinimumLength=8,
            RequireUppercase=false,
            RequireLowercase=false,
            RequireNumbers=false,
            RequireSymbols=false
        }" \
        --alias-attributes "preferred_username" \
        --mfa-configuration "OFF" \
        --admin-create-user-config "AllowAdminCreateUserOnly=True" \
        --account-recovery-setting "RecoveryMechanisms=[
            {
                Priority=1,
                Name=admin_only
            }
        ]" \
        --user-pool-tags Key=Project,Value=$project_name
)

if [ $? -ne 0 ]; then
    echo -e "${RED}Participant Cognito user pool creation failed${RESET}"
    exit 1
fi

participant_user_pool_id=$(echo "$participant_user_pool_response" | jq -r '.UserPool.Id')
participant_user_pool_name=$(echo "$participant_user_pool_response" | jq -r '.UserPool.Name')
participant_user_pool_domain="$project_name-participant-dev"

aws cognito-idp create-user-pool-domain \
    --user-pool-id "$participant_user_pool_id" \
    --domain $participant_user_pool_domain

if [ $? -ne 0 ]; then
    echo -e "${RED}Participant Cognito user pool domain creation failed${RESET}"
    exit 1
fi

participant_client_response=$(
    aws cognito-idp create-user-pool-client \
        --user-pool-id "$participant_user_pool_id" \
        --client-name "$project_name-participant-client-dev" \
        --generate-secret \
        --callback-urls "[\"http://localhost:5000/auth/participant/callback\"]" \
        --logout-urls "[\"http://localhost:3000/login\"]"
)

if [ $? -ne 0 ]; then
    echo -e "${RED}Participant Cognito user pool client update failed${RESET}"
    exit 1
fi

participant_client_id=$(echo "$participant_client_response" | jq -r '.UserPoolClient.ClientId')
participant_client_secret=$(echo "$participant_client_response" | jq -r '.UserPoolClient.ClientSecret')

echo -e "Created participant user pool ${BLUE}$participant_user_pool_name${RESET} with ID ${BLUE}$participant_user_pool_id${RESET} at ${BLUE}$participant_user_pool_domain${RESET}"

# Create a researcher Cognito user pool
echo "Creating a researcher Cognito user pool"
researcher_user_pool_response=$(
    aws cognito-idp create-user-pool \
        --pool-name "$project_name-researcher-pool-dev" \
        --policies "PasswordPolicy={
            MinimumLength=8,
            RequireUppercase=true,
            RequireLowercase=true,
            RequireNumbers=true,
            RequireSymbols=true,
            TemporaryPasswordValidityDays=7
        }" \
        --schema "[
            {
                \"Name\": \"first_name\",
                \"AttributeDataType\": \"String\",
                \"Mutable\": true
            },
            {
                \"Name\": \"last_name\",
                \"AttributeDataType\": \"String\",
                \"Mutable\": true
            }
        ]" \
        --auto-verified-attributes "[\"email\"]" \
        --username-attributes "[\"phone_number\", \"email\"]" \
        --mfa-configuration "OFF" \
        --email-configuration "EmailSendingAccount=COGNITO_DEFAULT" \
        --username-configuration "CaseSensitive=false" \
        --account-recovery-setting \
            "RecoveryMechanisms=[
                {
                    Priority=1,
                    Name=verified_email
                }
            ]" \
        --user-pool-tags Key=Project,Value=$project_name
)

if [ $? -ne 0 ]; then
    echo -e "${RED}Researcher Cognito user pool creation failed${RESET}"
    exit 1
fi

researcher_user_pool_id=$(echo "$researcher_user_pool_response" | jq -r '.UserPool.Id')
researcher_user_pool_name=$(echo "$researcher_user_pool_response" | jq -r '.UserPool.Name')
researcher_user_pool_domain="$project_name-researcher-dev"

aws cognito-idp create-user-pool-domain \
    --user-pool-id "$researcher_user_pool_id" \
    --domain $researcher_user_pool_domain

if [ $? -ne 0 ]; then
    echo -e "${RED}Researcher Cognito user pool domain creation failed${RESET}"
    exit 1
fi

researcher_client_response=$(
    aws cognito-idp create-user-pool-client \
        --user-pool-id "$researcher_user_pool_id" \
        --client-name "$project_name-researcher-client-dev" \
        --generate-secret \
        --callback-urls "[\"http://localhost:5000/auth/researcher/callback\"]" \
        --logout-urls "[\"http://localhost:3000/coordinator/login\"]"
)

if [ $? -ne 0 ]; then
    echo -e "${RED}Researcher Cognito user pool client creation failed${RESET}"
    exit 1
fi

researcher_client_id=$(echo "$researcher_client_response" | jq -r '.UserPoolClient.ClientId')
researcher_client_secret=$(echo "$researcher_client_response" | jq -r '.UserPoolClient.ClientSecret')

echo -e "Created researcher user pool ${BLUE}$researcher_user_pool_name${RESET} with ID ${BLUE}$researcher_user_pool_id${RESET} at ${BLUE}$researcher_user_pool_domain${RESET}"

# Create a Cognito user in the researcher user pool
echo "Creating a Cognito user in the researcher user pool"
researcher_admin_response=$(
    aws cognito-idp admin-create-user \
        --user-pool-id "$researcher_user_pool_id" \
        --username "$admin_email" \
        --temporary-password "$admin_password"
)

if [ $? -ne 0 ]; then
    echo -e "${RED}Researcher Cognito user creation failed${RESET}"
    exit 1
fi

researcher_admin_id=$(echo "$researcher_admin_response" | jq -r '.User.Username')
echo -e "Created researcher admin user ${BLUE}$researcher_admin_id${RESET}"

########################################################
# S3 setup                                             #
########################################################
echo -e "\n${CYAN}[S3 Setup]${RESET}"

echo "Creating a S3 bucket for wearable data retrieval logs"
logs_bucket_response=$(
    aws s3 create-bucket \
        --bucket "$project_name-wearable-data-retrieval-logs" \
        --region $aws_region
)

if [ $? -ne 0 ]; then
    echo -e "${RED}S3 bucket creation failed${RESET}"
    exit 1
fi

logs_bucket_name=$(echo "$logs_bucket_response" | jq -r '.Bucket.Name')
echo -e "Created S3 bucket ${BLUE}$logs_bucket_name${RESET}"

echo "Creating a S3 bucket for audio files"
audio_bucket_response=$(
    aws s3 create-bucket \
        --bucket "$project_name-audio-files" \
        --region $aws_region
)

if [ $? -ne 0 ]; then
    echo -e "${RED}S3 bucket creation failed${RESET}"
    exit 1
fi

audio_bucket_name=$(echo "$audio_bucket_response" | jq -r '.Bucket.Name')
echo -e "Created S3 bucket ${BLUE}$audio_bucket_name${RESET}"

echo -e "${GREEN}[S3 setup complete]${RESET}"

########################################################
# .env files setup                                     #
########################################################
echo -e "\n${CYAN}[.env Files Setup]${RESET}"

# Read postgres.env
if [ -f postgres.env ]; then
    source postgres.env
else
    echo -e "${RED}postgres.env file not found${RESET}"
    exit 1
fi

touch functions/wearable_data_retrieval/.env

if [ $? -ne 0 ]; then
    echo -e "${RED}wearable_data_retrieval .env file creation failed${RESET}"
    exit 1
fi

cat <<EOF > functions/wearable_data_retrieval/.env
DB_URI=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$project_name-postgres:$POSTGRES_PORT/$POSTGRES_DB
S3_BUCKET=$logs_bucket_name
AWS_CONFIG_SECRET_NAME=$project_name-dev-secret
AWS_ACCESS_KEY_ID=$aws_access_key_id
AWS_SECRET_ACCESS_KEY=$aws_secret_access_key
AWS_DEFAULT_REGION=$aws_region
EOF

touch .env

if [ $? -ne 0 ]; then
    echo -e "${RED}.env file creation failed${RESET}"
    exit 1
fi

cat <<EOF > .env
FLASK_DB=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$project_name-postgres:$POSTGRES_PORT/$POSTGRES_DB
APP_SYNC_HOST=""
APPSYNC_ACCESS_KEY=""
APPSYNC_SECRET_KEY=""
AWS_AUDIO_FILE_BUCKET=$audio_bucket_name
AWS_TABLENAME_AUDIO_FILE=""
AWS_TABLENAME_AUDIO_TAP=""
AWS_TABLENAME_TAP=""
AWS_TABLENAME_USER=""
COGNITO_PARTICIPANT_CLIENT_ID=$participant_client_id
COGNITO_PARTICIPANT_CLIENT_SECRET=$participant_client_secret
COGNITO_PARTICIPANT_DOMAIN="$participant_user_pool_domain.$aws_region.amazoncognito.com"
COGNITO_PARTICIPANT_REGION=$aws_region
COGNITO_PARTICIPANT_USER_POOL_ID=$participant_user_pool_id
COGNITO_RESEARCHER_CLIENT_ID=$researcher_client_id
COGNITO_RESEARCHER_CLIENT_SECRET=$researcher_client_secret
COGNITO_RESEARCHER_DOMAIN="$researcher_user_pool_domain.$aws_region.amazoncognito.com"
COGNITO_RESEARCHER_REGION=$aws_region
COGNITO_RESEARCHER_USER_POOL_ID=$researcher_user_pool_id
TM_FSTRING=$project_name-dev-tokens
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}.env file creation failed${RESET}"
    exit 1
fi

echo -e "${GREEN}[.env files setup complete]${RESET}"

########################################################
# Docker setup                                         #
########################################################
echo -e "\n${CYAN}[Docker Setup]${RESET}"

docker network create $project_name-network

if [ $? -ne 0 ]; then
    echo -e "${RED}Docker network creation failed${RESET}"
    exit 1
fi

echo "Creating a postgres container"

docker run \
    -ditp 5432:5432 \
    --name $project_name-postgres \
    --env-file postgres.env \
    --network $project_name-network \
    postgres

if [ $? -ne 0 ]; then
    echo -e "${RED}postgres container creation failed${RESET}"
    exit 1
fi

flask db upgrade

if [ $? -ne 0 ]; then
    echo -e "${RED}database upgrade failed${RESET}"
    exit 1
fi

flask db init-integration-testing-db

if [ $? -ne 0 ]; then
    echo -e "${RED}integration testing database initialization failed${RESET}"
    exit 1
fi

flask db create-researcher-account --email $admin_email

if [ $? -ne 0 ]; then
    echo -e "${RED}researcher account creation failed${RESET}"
    exit 1
fi

echo "Creating wearable data retrieval container"

if [ -f shared ]; then
    cp -r shared functions/wearable_data_retrieval/shared
else
    echo -e "${RED}shared directory not found${RESET}"
    exit 1
fi

docker build \
    --platform linux/amd64 \
    -t $project_name-wearable-data-retrieval \
    functions/wearable_data_retrieval

if [ $? -ne 0 ]; then
    echo -e "${RED}wearable data retrieval container creation failed${RESET}"
    exit 1
fi

rm -rf functions/wearable_data_retrieval/shared

docker run --rm \
    --platform linux/amd64 \
    --name $project_name-wearable-data-retrieval \
    --network $project_name-network \
    -p 9000:8080 \
    --env-file functions/wearable_data_retrieval/.env \
    -e TESTING=true \
    $project_name-wearable-data-retrieval

if [ $? -ne 0 ]; then
    echo -e "${RED}wearable data retrieval container creation failed${RESET}"
    exit 1
fi

echo -e "${GREEN}[Docker setup complete]${RESET}"

########################################################
# Secrets Manager setup                                #
########################################################
echo -e "\n${CYAN}[Secrets Manager Setup]${RESET}"

# Create an empty development secret on Secrets Manager
echo "Creating a development secret on Secrets Manager"
dev_secret_response=$(
    aws secretsmanager create-secret \
        --name "$project_name-dev-secret" \
        --secret-string "{
            "FITBIT_CLIENT_ID": "$fitbit_client_id",
            "FITBIT_CLIENT_SECRET": "$fitbit_client_secret"
        }" \
        --tags Key=Project,Value=$project_name
)

if [ $? -ne 0 ]; then
    echo -e "${RED}development secret creation failed${RESET}"
    exit 1
fi

dev_secret_name=$(echo "$dev_secret_response" | jq -r '.Secret.Name')
echo -e "Created development secret ${BLUE}$dev_secret_name${RESET}"

# Create an empty tokens secret on Secrets Manager
echo "Creating a tokens secret on Secrets Manager"
tokens_secret_response=$(
    aws secretsmanager create-secret \
        --name "$project_name-dev-Fitbit-tokens" \
        --tags Key=Project,Value=$project_name
)

if [ $? -ne 0 ]; then
    echo -e "${RED}tokens secret creation failed${RESET}"
    exit 1
fi

tokens_secret_name=$(echo "$tokens_secret_response" | jq -r '.Secret.Name')
echo -e "Created tokens secret ${BLUE}$tokens_secret_name${RESET}"

echo -e "${GREEN}[Installation complete]${RESET}"
echo -e "You can now start the development server with ${BLUE}npm run start${RESET} and ${BLUE}flask run${RESET}"
