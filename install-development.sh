#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
RESET='\033[0m'

POSTGRES_USER=username
POSTGRES_PASSWORD=password
POSTGRES_PORT=5432
POSTGRES_DB=database_name

# Names are limited to 128 characters or fewer. Names may only contain alphanumeric characters, spaces, and the following special characters: + = , . @ -
is_valid_name() {
    local name="$1"
    if [[ -z "$name" ]]; then
        return 1
    fi
    if [[ "$name" =~ ^[a-zA-Z0-9\s+=\.,@_-]+$ && ${#name} -le 128 ]]; then
        return 0
    else
        echo -e "${RED}Invalid name${RESET}"
        return 1
    fi
}

is_valid_email() {
    local email="$1"
    if [[ -z "$email" ]]; then
        return 1
    fi
    if [[ "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        return 0
    else
        echo -e "${RED}Invalid email${RESET}"
        return 1
    fi
}

is_valid_password() {
    local password="$1"
    # Trim whitespace
    password=$(echo "$password" | xargs)
    if [[ -z "$password" ]]; then
        return 1
    fi
    has_number=false
    has_uppercase=false
    has_lowercase=false
    has_special=false
    if [[ "$password" =~ [0-9] ]]; then
        has_number=true
    fi
    if [[ "$password" =~ [A-Z] ]]; then
        has_uppercase=true
    fi
    if [[ "$password" =~ [a-z] ]]; then
        has_lowercase=true
    fi
    if [[ "$password" =~ [^a-zA-Z0-9] ]]; then
        has_special=true
    fi
    if [[ "$has_number" == false || "$has_uppercase" == false || "$has_lowercase" == false || "$has_special" == false ]]; then
        echo -e "${RED}Password must contain at least one number, one uppercase letter, one lowercase letter, and one special character${RESET}"
        return 1
    fi
    if [[ ${#password} -lt 8 ]]; then
        echo -e "${RED}Password must be at least 8 characters long${RESET}"
        return 1
    fi
    return 0
}

echo
echo "This script will install the development environment for the project."
echo -e "${MAGENTA}The following will be configured and installed:${RESET}"
echo "- AWS CLI"
echo "- Python 3.13"
echo "- Python packages"
echo "- Amazon Cognito user pools and clients"
echo "- Amazon S3 buckets"
echo "- Development secrets on AWS Secrets Manager"
echo "- Local .env files"
echo "- Docker containers for the project"

read -ep "Do you want to continue? (y/n): " continue

if [ "$continue" != "y" ]; then
    echo -e "${RED}Installation cancelled${RESET}"
    exit 1
fi

########################################################
# AWS CLI setup                                        #
########################################################
echo
echo -e "${CYAN}[AWS CLI Setup]${RESET}"
aws configure

aws_access_key_id=$(aws configure get aws_access_key_id)
aws_secret_access_key=$(aws configure get aws_secret_access_key)
aws_region=$(aws configure get region)

########################################################
# Project setup                                       #
########################################################
# Prompt the user for a name for their project
echo
echo -e "${CYAN}[Project Setup]${RESET}"

project_name=""
while ! is_valid_name "$project_name"; do
    read -ep "Enter a name for your project: " project_name
done

# Prompt the user for fitbit credentials
echo
echo -e "${CYAN}[Fitbit Setup]${RESET}"
read -ep "Enter your dev Fitbit client ID: " fitbit_client_id
read -ep "Enter your dev Fitbit client secret: " fitbit_client_secret

# Prompt the user for an email to login as admin
echo
echo -e "${CYAN}[Admin Setup]${RESET}"

admin_email=""
while ! is_valid_email "$admin_email"; do
    read -ep "Enter an email to login as admin: " admin_email
done

# echo
# echo "A valid password must be at least 8 characters long and contain at least one number, one uppercase letter, one lowercase letter, and one special character"
# admin_password=""
# while ! is_valid_password "$admin_password"; do
#     echo -n "Enter a temporary password for the admin user: "
#     read -s admin_password
#     echo
# done

# admin_password_confirm=""
# while ! is_valid_password "$admin_password_confirm"; do
#     echo -n "Confirm the temporary password for the admin user: "
#     read -s admin_password_confirm
#     echo
# done

# if [ "$admin_password" != "$admin_password_confirm" ]; then
#     echo -e "${RED}Passwords do not match${RESET}"
#     exit 1
# fi

########################################################
# Python setup                                         #
########################################################
echo
echo -e "${CYAN}[Python Setup]${RESET}"

if [ ! -f env/bin/activate ]; then
    echo "Initializing Python virtual environment..."
    python3.13 -m venv env
fi

if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Entering Python virtual environment..."
    source env/bin/activate
fi

echo "Installing Python packages"
pip install -qr requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}Python setup failed${RESET}"
    exit 1
fi

########################################################
# Cognito setup                                        #
########################################################
echo
echo -e "${CYAN}[Cognito Setup]${RESET}"

# Create a participant Cognito user pool
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
                \"Name\": \"given_name\",
                \"AttributeDataType\": \"String\",
                \"Mutable\": true
            },
            {
                \"Name\": \"family_name\",
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
# researcher_admin_response=$(
#     aws cognito-idp admin-create-user \
#         --user-pool-id "$researcher_user_pool_id" \
#         --username "$admin_email" \
#         --temporary-password "$admin_password"
# )
researcher_admin_response=$(
    aws cognito-idp admin-create-user \
        --user-pool-id "$researcher_user_pool_id" \
        --username "$admin_email"
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
echo
echo -e "${CYAN}[S3 Setup]${RESET}"

logs_bucket_name="$project_name-wearable-data-retrieval-logs"
aws s3api create-bucket \
    --bucket "$logs_bucket_name" \
    --region $aws_region \
    &> /dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}S3 bucket creation failed${RESET}"
    exit 1
fi

echo -e "Created S3 bucket ${BLUE}$logs_bucket_name${RESET}"

audio_bucket_name="$project_name-audio-files"
aws s3api create-bucket \
    --bucket "$audio_bucket_name" \
    --region $aws_region \
    &> /dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}S3 bucket creation failed${RESET}"
    exit 1
fi

echo -e "Created S3 bucket ${BLUE}$audio_bucket_name${RESET}"

########################################################
# .env files setup                                     #
########################################################
echo
echo -e "${CYAN}[Local .env Files Setup]${RESET}"

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

echo -e ".env file created at ${BLUE}$(pwd)/functions/wearable_data_retrieval/.env${RESET}"

cat <<EOF > .env
FLASK_CONFIG=Default
FLASK_DEBUG=True
FLASK_DB=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost:$POSTGRES_PORT/$POSTGRES_DB
FLASK_APP=run.py
LOCAL_LAMBDA_ENDPOINT=http://localhost:9000/2015-03-31/functions/function/invocations
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

echo -e ".env file created at ${BLUE}$(pwd)/.env${RESET}"

########################################################
# Docker setup                                         #
########################################################
echo
echo -e "${CYAN}[Docker Setup]${RESET}"

docker network create $project_name-network

if [ $? -ne 0 ]; then
    echo -e "${RED}Docker network creation failed${RESET}"
    exit 1
fi

echo -e "Created docker network ${BLUE}$project_name-network${RESET}"

docker run \
    -ditp 5432:5432 \
    --name $project_name-postgres \
    -e POSTGRES_USER=$POSTGRES_USER \
    -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
    -e POSTGRES_DB=$POSTGRES_DB \
    -e POSTGRES_PORT=$POSTGRES_PORT \
    --network $project_name-network \
    postgres

if [ $? -ne 0 ]; then
    echo -e "${RED}postgres container creation failed${RESET}"
    exit 1
fi

# Wait for the postgres container to be ready
while ! docker exec -t $project_name-postgres pg_isready -U $POSTGRES_USER -d $POSTGRES_DB; do
    sleep 1
done

echo -e "Created postgres container ${BLUE}$project_name-postgres${RESET}"

flask --app run.py db upgrade

if [ $? -ne 0 ]; then
    echo -e "${RED}database upgrade failed${RESET}"
    exit 1
fi

flask --app run.py init-integration-testing-db

if [ $? -ne 0 ]; then
    echo -e "${RED}integration testing database initialization failed${RESET}"
    exit 1
fi

flask --app run.py create-researcher-account --email "$admin_email"

if [ $? -ne 0 ]; then
    echo -e "${RED}researcher account creation failed${RESET}"
    exit 1
fi

echo -e "Created researcher account ${BLUE}$admin_email${RESET}"

if [ -d "./shared" ]; then
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

docker run \
    --platform linux/amd64 \
    --name $project_name-wearable-data-retrieval \
    --network $project_name-network \
    -ditp 9000:8080 \
    --env-file functions/wearable_data_retrieval/.env \
    -e TESTING=true \
    $project_name-wearable-data-retrieval

if [ $? -ne 0 ]; then
    echo -e "${RED}wearable data retrieval container creation failed${RESET}"
    exit 1
fi

echo -e "Created wearable data retrieval container ${BLUE}$project_name-wearable-data-retrieval${RESET}"

########################################################
# Secrets Manager setup                                #
########################################################
echo
echo -e "${CYAN}[Secrets Manager Setup]${RESET}"

# Create an empty development secret on Secrets Manager
dev_secret_name="$project_name-dev-secret"
aws secretsmanager create-secret \
    --name "$dev_secret_name" \
    --secret-string "{
        "FITBIT_CLIENT_ID": "$fitbit_client_id",
        "FITBIT_CLIENT_SECRET": "$fitbit_client_secret"
    }" \
    --tags Key=Project,Value=$project_name \
    &> /dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}development secret creation failed${RESET}"
    exit 1
fi

echo -e "Created development secret ${BLUE}$dev_secret_name${RESET}"

# Create an empty tokens secret on Secrets Manager
tokens_secret_name="$project_name-dev-Fitbit-tokens"
aws secretsmanager create-secret \
    --name "$tokens_secret_name" \
    --tags Key=Project,Value=$project_name \
    &> /dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}tokens secret creation failed${RESET}"
    exit 1
fi

echo -e "Created tokens secret ${BLUE}$tokens_secret_name${RESET}"

echo
echo -e "${GREEN}[Installation complete]${RESET}"
echo -e "Check your email for a temporary password for the researcher admin user"
echo -e "You can now start the development server with ${BLUE}npm run start${RESET} and ${BLUE}flask run${RESET}"
