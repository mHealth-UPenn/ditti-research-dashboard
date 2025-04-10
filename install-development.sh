#!/bin/bash

########################################################
# Project setup                                       #
########################################################
# Prompt the user for a name for their project
read -p "Enter a name for your project: " project_name

# Prompt the user for fitbit credentials
read -p "Enter your Fitbit client ID: " fitbit_client_id
read -p "Enter your Fitbit client secret: " fitbit_client_secret

########################################################
# Python setup                                         #
########################################################
echo "Running Python setup"

if [ ! -f env/bin/activate ]; then
    echo "Initializing Python virtual environment..."
    python3.13 -m venv env
fi

if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Entering Python virtual environment..."
    source env/bin/activate
fi

echo "Installing Python packages"
pip install -r requirements.txt

echo "\033[32mPython setup complete\033[0m"

########################################################
# AWS CLI setup                                        #
########################################################
echo "Configuring the AWS CLI"
aws configure

aws_access_key_id=$(aws configure get aws_access_key_id)
aws_secret_access_key=$(aws configure get aws_secret_access_key)
aws_region=$(aws configure get region)

########################################################
# Cognito setup                                        #
########################################################
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

participant_user_pool_id=$(echo "$participant_user_pool_response" | jq -r '.UserPool.Id')
participant_user_pool_name=$(echo "$participant_user_pool_response" | jq -r '.UserPool.Name')
participant_user_pool_domain=$(echo "$participant_user_pool_response" | jq -r '.UserPool.Domain')

participant_client=$(
    aws cognito-idp list-user-pool-clients \
        --user-pool-id "$participant_user_pool_id" \
        | jq -r '.UserPoolClients[0]'
)

participant_client_id=$(echo "$participant_client" | jq -r '.ClientId')
participant_client_secret=$(echo "$participant_client" | jq -r '.ClientSecret')

aws cognito-idp update-user-pool-client \
    --user-pool-id "$participant_user_pool_id" \
    --client-id "$participant_client_id" \
    --callback-urls "[http://localhost:5000/auth/participant/callback]" \
    --logout-urls "[http://localhost:3000/login]"

echo "Created participant user pool \033[36m$participant_user_pool_name\033[0m with ID \033[36m$participant_user_pool_id\033[0m at \033[36m$participant_user_pool_domain\033[0m"

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
                Name=first_name,
                AttributeDataType=String,
                Required=true,
                Mutable=true
            },
            {
                Name=last_name,
                AttributeDataType=String,
                Required=true,
                Mutable=true
            }
        ]" \
        --auto-verified-attributes "[phone_number, email]" \
        --username-attributes "[phone_number, email]" \
        --mfa-configuration "OFF" \
        --email-configuration "EmailSendingAccount=COGNITO_DEFAULT" \
        --username-configuration "CaseSensitive=false" \
        --account-recovery-setting \
            "RecoveryMechanisms=[
                {
                    Priority=1,
                    Name=verified_email
                },
                {
                    Priority=2,
                    Name=verified_phone_number
                }
            ]" \
        --user-pool-tags Key=Project,Value=$project_name
)

researcher_user_pool_id=$(echo "$researcher_user_pool_response" | jq -r '.UserPool.Id')
researcher_user_pool_name=$(echo "$researcher_user_pool_response" | jq -r '.UserPool.Name')
researcher_user_pool_domain=$(echo "$researcher_user_pool_response" | jq -r '.UserPool.Domain')

researcher_client=$(
    aws cognito-idp list-user-pool-clients \
        --user-pool-id "$researcher_user_pool_id" \
        | jq -r '.UserPoolClients[0]'
)

researcher_client_id=$(echo "$researcher_client" | jq -r '.ClientId')
researcher_client_secret=$(echo "$researcher_client" | jq -r '.ClientSecret')
aws cognito-idp update-user-pool-client \
    --user-pool-id "$researcher_user_pool_id" \
    --client-id "$researcher_client_id" \
    --callback-urls "[http://localhost:5000/auth/researcher/callback]" \
    --logout-urls "[http://localhost:3000/coordinator/login]"

echo "Created researcher user pool \033[36m$researcher_user_pool_name\033[0m with ID \033[36m$researcher_user_pool_id\033[0m at \033[36m$researcher_user_pool_domain\033[0m"

# Prompt the user for an email to login as admin
read -p "Enter an email to login as admin: " admin_email
read -p "Enter a phone number for the admin user: " admin_phone_number
read -p "Enter a temporary password for the admin user: " admin_password
read -p "Enter a first name for the admin user: " admin_first_name
read -p "Enter a last name for the admin user: " admin_last_name

# Create a Cognito user in the researcher user pool
echo "Creating a Cognito user in the researcher user pool"
researcher_admin_response=$(
    aws cognito-idp admin-create-user \
        --user-pool-id "$researcher_user_pool_id" \
        --username "$admin_email" \
        --user-attributes "[
            {
                Name=email,
                Value=$admin_email
            },
            {
                Name=phone_number,
                Value=$admin_phone_number
            },
            {
                Name=first_name,
                Value=$admin_first_name
            },
            {
                Name=last_name,
                Value=$admin_last_name
            }
        ]" \
        --temporary-password "$admin_password"
)

researcher_admin_id=$(echo "$researcher_admin_response" | jq -r '.User.Username')
echo "Created researcher admin user \033[36m$researcher_admin_id\033[0m"

########################################################
# S3 setup                                             #
########################################################
echo "Creating a S3 bucket for wearable data retrieval logs"
logs_bucket_response=$(
    aws s3 create-bucket \
        --bucket "$project_name-wearable-data-retrieval-logs" \
        --region $aws_region
)

logs_bucket_name=$(echo "$logs_bucket_response" | jq -r '.Bucket.Name')
echo "Created S3 bucket \033[36m$logs_bucket_name\033[0m"

########################################################
# .env files setup                                     #
########################################################
echo "Setting up .env files"

# Read postgres.env
source postgres.env

touch functions/wearable_data_retrieval/.env

cat <<EOF > functions/wearable_data_retrieval/.env
DB_URI=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$project_name-postgres:$POSTGRES_PORT/$POSTGRES_DB
S3_BUCKET=$logs_bucket_name
AWS_CONFIG_SECRET_NAME=$project_name-dev-secret
AWS_ACCESS_KEY_ID=$aws_access_key_id
AWS_SECRET_ACCESS_KEY=$aws_secret_access_key
AWS_DEFAULT_REGION=$aws_region
EOF

touch .env

cat <<EOF > .env
FLASK_DB=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$project_name-postgres:$POSTGRES_PORT/$POSTGRES_DB
APP_SYNC_HOST=""
APPSYNC_ACCESS_KEY=""
APPSYNC_SECRET_KEY=""
AWS_AUDIO_FILE_BUCKET=""
AWS_TABLENAME_AUDIO_FILE=""
AWS_TABLENAME_AUDIO_TAP=""
AWS_TABLENAME_TAP=""
AWS_TABLENAME_USER=""
COGNITO_PARTICIPANT_CLIENT_ID=$participant_client_id
COGNITO_PARTICIPANT_CLIENT_SECRET=$participant_client_secret
COGNITO_PARTICIPANT_DOMAIN=$participant_user_pool_domain
COGNITO_PARTICIPANT_REGION=$aws_region
COGNITO_PARTICIPANT_USER_POOL_ID=$participant_user_pool_id
COGNITO_RESEARCHER_CLIENT_ID=$researcher_client_id
COGNITO_RESEARCHER_CLIENT_SECRET=$researcher_client_secret
COGNITO_RESEARCHER_DOMAIN=$researcher_user_pool_domain
COGNITO_RESEARCHER_REGION=$aws_region
COGNITO_RESEARCHER_USER_POOL_ID=$researcher_user_pool_id
TM_FSTRING=$project_name-dev-tokens
EOF

########################################################
# Docker setup                                         #
########################################################
echo "Setting up Docker"

docker network create $project_name-network

echo "Creating a postgres container"

docker run \
    -ditp 5432:5432 \
    --name $project_name-postgres \
    --env-file postgres.env \
    --network $project_name-network \
    postgres

flask db upgrade
flask db init-integration-testing-db
flask db create-researcher-account \
    --email $admin_email \
    --phone-number $admin_phone_number \
    --password $admin_password \
    --first-name $admin_first_name \
    --last-name $admin_last_name

echo "Creating wearable data retrieval container"

cp -r shared functions/wearable_data_retrieval/shared

docker build \
    --platform linux/amd64 \
    -t $project_name-wearable-data-retrieval \
    functions/wearable_data_retrieval

rm -rf functions/wearable_data_retrieval/shared

docker run --rm \
    --platform linux/amd64 \
    --name $project_name-wearable-data-retrieval \
    --network $project_name-network \
    -p 9000:8080 \
    --env-file functions/wearable_data_retrieval/.env \
    -e TESTING=true \
    $project_name-wearable-data-retrieval

echo "\033[32mDocker setup complete\033[0m"

########################################################
# Secrets Manager setup                                #
########################################################
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

dev_secret_name=$(echo "$dev_secret_response" | jq -r '.Secret.Name')
echo "Created development secret \033[36m$dev_secret_name\033[0m"

# Create an empty tokens secret on Secrets Manager
echo "Creating a tokens secret on Secrets Manager"
tokens_secret_response=$(
    aws secretsmanager create-secret \
        --name "$project_name-dev-Fitbit-tokens" \
        --tags Key=Project,Value=$project_name
)

tokens_secret_name=$(echo "$tokens_secret_response" | jq -r '.Secret.Name')
echo "Created tokens secret \033[36m$tokens_secret_name\033[0m"

echo "\033[32mInstallation complete\033[0m"
