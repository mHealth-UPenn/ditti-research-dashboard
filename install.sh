#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
RESET='\033[0m'

STAGING=0
BYO_RDS=false
BYO_WAF=false
rds_instance_identifier=""
rds_secret_arn=""
waf_id=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--staging)
            STAGING=1
            shift
            ;;
        -i|--rds-instance-identifier)
            rds_instance_identifier="$2"
            BYO_RDS=true
            shift
            shift
            ;;
        -a|--rds-secret-arn)
            rds_secret_arn="$2"
            BYO_RDS=true
            shift
            shift
            ;;
        -w|--waf-id)
            waf_id="$2"
            BYO_WAF=true
            shift
            shift
            ;;
        -*|--*)
            echo "Unknown option $1"
            # exit 1
            ;;
    esac
done

# Both rds_instance_identifier and rds_secret_arn are required when either is provided
if [ -n "$rds_instance_identifier" ] && [ -z "$rds_secret_arn" ]; then
    echo -e "${RED}RDS instance identifier and secret ARN are required when either is provided${RESET}"
    # exit 1
fi

if [ -z "$rds_instance_identifier" ] && [ -n "$rds_secret_arn" ]; then
    echo -e "${RED}RDS instance identifier and secret ARN are required when either is provided${RESET}"
    # exit 1
fi

echo
if [ "$STAGING" -eq 1 ]; then
    echo -e "${YELLOW}Staging environment selected${RESET}"
    suffix="-staging"
else
    echo -e "${GREEN}Production environment selected${RESET}"
    suffix=""
fi

is_valid_name() {
    local name="$1"
    if [[ -z "$name" ]]; then
        return 1
    fi
    if [[ "$name" =~ ^[a-zA-Z0-9_-]+$ && ${#name} -le 64 ]]; then
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

is_valid_domain() {
    local domain="$1"
    if [[ -z "$domain" ]]; then
        return 1
    fi
    if [[ "$domain" =~ ^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        return 0
    else
        echo -e "${RED}Invalid domain${RESET}"
        return 1
    fi
}

has_subdomain() {
    local domain="$1"
    if [[ "$domain" =~ ^[^\.]+\.[^\.]+\.[^\.]+$ ]]; then
        return 1
    else
        return 0
    fi
}

echo
echo "This script will install the a production environment for the project."
echo -e "${MAGENTA}The following will be configured and installed:${RESET}"
echo "- AWS CLI"
echo "- Amazon Cognito user pools and clients"
echo "- Amazon S3 buckets"
echo "- Web Application Firewall"
echo "- AWS CloudFront distribution"
echo "- AWS Relational Database Service (RDS) instance"
echo "- AWS Lambda functions"
echo "- Production secrets on AWS Secrets Manager"
echo "- Serverless application with Zappa"
read -ep "Do you want to continue? (y/n): " continue

if [ "$continue" != "y" ]; then
    echo -e "${RED}Installation cancelled${RESET}"
    # exit 1
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
aws_account_id=$(aws sts get-caller-identity --query "Account" --output text)

########################################################
# Project setup                                       #
########################################################
# Prompt the user for a name for their project
echo
echo -e "${CYAN}[Project Setup]${RESET}"

project_name=""
echo
echo "A valid project name must be 64 characters or fewer and contain only alphanumeric characters and the following special characters: _ -"
while ! is_valid_name "$project_name"; do
    read -ep "Enter a name for your project: " project_name
done
project_name="$project_name$suffix"

# Prompt the user for fitbit credentials
read -ep "Enter your dev Fitbit client ID: " fitbit_client_id
read -ep "Enter your dev Fitbit client secret: " fitbit_client_secret

# Prompt the user for an email to login as admin
admin_email=""
while ! is_valid_email "$admin_email"; do
    read -ep "Enter an email to login as admin: " admin_email
done

domain_name=""
while ! is_valid_domain "$domain_name"; do
    read -ep "Enter your domain name (e.g. www.example.com): " domain_name
done

certificate_arn=""
while [ -z "$certificate_arn" ]; do
    read -ep "Enter the ARN of the certificate for your domain: " certificate_arn
done

if [ -z "$rds_instance_identifier" ]; then
    rds_instance_identifier="$project_name-rds"
fi

participant_user_pool_name="$project_name-participant-pool"
participant_user_pool_domain="$project_name-participant"
researcher_user_pool_name="$project_name-researcher-pool"
researcher_user_pool_domain="$project_name-researcher"
logs_bucket_name="$project_name-wearable-data-retrieval-logs"
audio_bucket_name="$project_name-audio-files"
static_bucket_name="$domain_name"
secret_name="$project_name-secret"
tokens_secret_name="$project_name-Fitbit-tokens"
wearable_data_retrieval_function_name="$project_name-wearable-data-retrieval"
wearable_data_retrieval_image_name="$project_name-wearable-data-retrieval"
wearable_data_retrieval_ecr_repo_name="$aws_account_id.dkr.ecr.us-east-1.amazonaws.com/$wearable_data_retrieval_image_name"
wearable_data_retrieval_role_name="$project_name-wearable-data-retrieval-role"
wearable_data_retrieval_policy_name="$project_name-wearable-data-retrieval-policy"

if has_subdomain "$domain_name"; then
    backend_domain="app-${domain_name}"
else
    backend_domain="app.${domain_name}"
fi

frontend_endpoint="https://${domain_name}"
backend_endpoint="https://${backend_domain}"

flask_secret_key=$(python -c "import secrets; print(secrets.token_hex())")

cat <<EOF > project-settings$suffix.json
{
    "project_name": "$project_name",
    "admin_email": "$admin_email",
    "domain": "$domain_name",
    "backend_domain": "$backend_domain",
    "frontend_endpoint": "$frontend_endpoint",
    "backend_endpoint": "$backend_endpoint",
    "aws": {
        "cognito": {
            "participant_user_pool_name": "$participant_user_pool_name",
            "participant_user_pool_domain": "$participant_user_pool_domain",
            "participant_user_pool_id": "",
            "participant_client_id": "",
            "researcher_user_pool_name": "$researcher_user_pool_name",
            "researcher_user_pool_domain": "$researcher_user_pool_domain",
            "researcher_user_pool_id": "",
            "researcher_client_id": ""
        },
        "rds": {
            "instance_identifier": "$rds_instance_identifier",
            "secret_arn": ""
        },
        "s3": {
            "logs_bucket_name": "$logs_bucket_name",
            "audio_bucket_name": "$audio_bucket_name",
            "static_bucket_name": "$static_bucket_name"
        },
        "secrets_manager": {
            "secret_name": "$secret_name",
            "tokens_secret_name": "$tokens_secret_name"
        },
        "cloudfront": {
            "origin_access_identity_id": "",
            "waf_id": "$waf_id",
            "distribution_id": ""
        },
        "lambda": {
            "wearable_data_retrieval_function_name": "$wearable_data_retrieval_function_name",
            "wearable_data_retrieval_ecr_repo_name": "$wearable_data_retrieval_ecr_repo_name",
            "wearable_data_retrieval_role_name": "$wearable_data_retrieval_role_name",
            "wearable_data_retrieval_policy_name": "$wearable_data_retrieval_policy_name"
        },
        "certificate_arn": "$certificate_arn",
    }
}
EOF

echo -e "Created project settings file ${BLUE}project-settings$suffix.json${RESET}"

########################################################
# Cognito setup                                        #
########################################################
echo
echo -e "${CYAN}[Cognito Setup]${RESET}"

# Create a participant Cognito user pool
participant_user_pool_response=$(
    aws cognito-idp create-user-pool \
        --pool-name "$project_name-participant-pool" \
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
    # exit 1
fi

participant_user_pool_id=$(echo "$participant_user_pool_response" | jq -r '.UserPool.Id')

# Update project settings with participant user pool ID
sed -i '' "s/\"participant_user_pool_id\": \"\"/\"participant_user_pool_id\": \"$participant_user_pool_id\"/g" project-settings-dev.json

aws cognito-idp create-user-pool-domain \
    --user-pool-id "$participant_user_pool_id" \
    --domain $participant_user_pool_domain

if [ $? -ne 0 ]; then
    echo -e "${RED}Participant Cognito user pool domain creation failed${RESET}"
    # exit 1
fi

participant_client_response=$(
    aws cognito-idp create-user-pool-client \
        --user-pool-id "$participant_user_pool_id" \
        --client-name "$project_name-participant-client" \
        --generate-secret \
        --callback-urls "[\"http://localhost:5000/auth/participant/callback\"]" \
        --logout-urls "[\"http://localhost:3000/login\"]" \
        --supported-identity-providers "[\"COGNITO\"]" \
        --allowed-o-auth-flows "[\"code\"]" \
        --allowed-o-auth-scopes "[\"openid\", \"profile\", \"aws.cognito.signin.user.admin\"]" \
        --allowed-o-auth-flows-user-pool-client
)

if [ $? -ne 0 ]; then
    echo -e "${RED}Participant Cognito user pool client update failed${RESET}"
    # exit 1
fi

participant_client_id=$(echo "$participant_client_response" | jq -r '.UserPoolClient.ClientId')
participant_client_secret=$(echo "$participant_client_response" | jq -r '.UserPoolClient.ClientSecret')

# Update project settings with participant client ID and secret
sed -i '' "s/\"participant_client_id\": \"\"/\"participant_client_id\": \"$participant_client_id\"/g" project-settings-dev.json

echo -e "Created participant user pool ${BLUE}$participant_user_pool_name${RESET} with ID ${BLUE}$participant_user_pool_id${RESET} at ${BLUE}$participant_user_pool_domain${RESET}"

# Create a researcher Cognito user pool
researcher_user_pool_response=$(
    aws cognito-idp create-user-pool \
        --pool-name "$project_name-researcher-pool" \
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
    # exit 1
fi

researcher_user_pool_id=$(echo "$researcher_user_pool_response" | jq -r '.UserPool.Id')

# Update project settings with researcher user pool ID
sed -i '' "s/\"researcher_user_pool_id\": \"\"/\"researcher_user_pool_id\": \"$researcher_user_pool_id\"/g" project-settings-dev.json

aws cognito-idp create-user-pool-domain \
    --user-pool-id "$researcher_user_pool_id" \
    --domain $researcher_user_pool_domain

if [ $? -ne 0 ]; then
    echo -e "${RED}Researcher Cognito user pool domain creation failed${RESET}"
    # exit 1
fi

researcher_client_response=$(
    aws cognito-idp create-user-pool-client \
        --user-pool-id "$researcher_user_pool_id" \
        --client-name "$project_name-researcher-client" \
        --generate-secret \
        --callback-urls "[\"http://localhost:5000/auth/researcher/callback\"]" \
        --logout-urls "[\"http://localhost:3000/coordinator/login\"]" \
        --supported-identity-providers "[\"COGNITO\"]" \
        --allowed-o-auth-flows "[\"code\"]" \
        --allowed-o-auth-scopes "[\"email\", \"phone\", \"openid\", \"profile\", \"aws.cognito.signin.user.admin\"]" \
        --allowed-o-auth-flows-user-pool-client
)

if [ $? -ne 0 ]; then
    echo -e "${RED}Researcher Cognito user pool client creation failed${RESET}"
    # exit 1
fi

researcher_client_id=$(echo "$researcher_client_response" | jq -r '.UserPoolClient.ClientId')
researcher_client_secret=$(echo "$researcher_client_response" | jq -r '.UserPoolClient.ClientSecret')

# Update project settings with researcher client ID and secret
sed -i '' "s/\"researcher_client_id\": \"\"/\"researcher_client_id\": \"$researcher_client_id\"/g" project-settings-dev.json

echo -e "Created researcher user pool ${BLUE}$researcher_user_pool_name${RESET} with ID ${BLUE}$researcher_user_pool_id${RESET} at ${BLUE}$researcher_user_pool_domain${RESET}"

# Create a Cognito user in the researcher user pool
researcher_admin_response=$(
    aws cognito-idp admin-create-user \
        --user-pool-id "$researcher_user_pool_id" \
        --username "$admin_email"
)

if [ $? -ne 0 ]; then
    echo -e "${RED}Researcher Cognito user creation failed${RESET}"
    # exit 1
fi

researcher_admin_id=$(echo "$researcher_admin_response" | jq -r '.User.Username')
echo -e "Created researcher admin user ${BLUE}$researcher_admin_id${RESET}"

########################################################
# S3 setup                                             #
########################################################
echo
echo -e "${CYAN}[S3 Setup]${RESET}"

logs_bucket_response=$(
    aws s3api create-bucket \
        --bucket "$logs_bucket_name" \
        --region $aws_region
)

if [ $? -ne 0 ]; then
    echo "$logs_bucket_response"
    echo -e "${RED}S3 bucket creation failed${RESET}"
    # exit 1
fi

echo -e "Created S3 bucket ${BLUE}$logs_bucket_name${RESET}"

audio_bucket_response=$(
    aws s3api create-bucket \
        --bucket "$audio_bucket_name" \
        --region $aws_region
)

if [ $? -ne 0 ]; then
    echo "$audio_bucket_response"
    echo -e "${RED}S3 bucket creation failed${RESET}"
    # exit 1
fi

echo -e "Created S3 bucket ${BLUE}$audio_bucket_name${RESET}"

static_bucket_response=$(
    aws s3api create-bucket \
        --bucket "$static_bucket_name" \
        --region $aws_region
)

if [ $? -ne 0 ]; then
    echo "$static_bucket_response"
    echo -e "${RED}S3 bucket creation failed${RESET}"
    # exit 1
fi

echo -e "Created S3 bucket ${BLUE}$static_bucket_name${RESET}"

########################################################
# RDS Setup                                            #
########################################################
echo
echo -e "${CYAN}[RDS Setup]${RESET}"

if [ "$BYO_RDS" = true ]; then
    echo -e "Using existing RDS instance ${BLUE}$rds_instance_identifier${RESET}"
else
    # Create the RDS instance
    rds_instance_response=$(
        aws rds create-db-instance \
            --db-instance-class "db.t3.micro" \
            --db-instance-identifier "$rds_instance_identifier" \
            --engine "postgres" \
            --db-name "postgres" \
            --deletion-protection \
            --master-username "postgres" \
            --no-multi-az \
            --storage-encrypted \
            --storage-type "gp2" \
            --allocated-storage 20 \
            --database-insights-mode "standard" \
            --no-enable-performance-insights \
            --manage-master-user-password \
            --publicly-accessible \
            --tags Key=Project,Value=$project_name
    )

    if [ $? -ne 0 ]; then
        echo "$rds_instance_response"
        echo -e "${RED}RDS instance creation failed${RESET}"
        # exit 1
    fi

    rds_secret_arn=$(echo "$rds_instance_response" | jq -r '.DBInstance.MasterUserSecret.SecretArn')
    sed -i '' "s/\"secret_arn\": \"\"/\"secret_arn\": \"$rds_secret_arn\"/g" project-settings$suffix.json

    echo -e "Created RDS instance ${BLUE}$rds_instance_identifier${RESET}"
fi

########################################################
# Cloudfront setup                                     #
########################################################
echo
echo -e "${CYAN}[Cloudfront Setup]${RESET}"

cloudfront_origin_access_identity_response=$(
    aws cloudfront create-cloud-front-origin-access-identity \
        --cloud-front-origin-access-identity-config "{
            \"CallerReference\": \"$project_name\",
            \"Comment\": \"$project_name\"
        }"
)

if [ $? -ne 0 ]; then
    echo "$cloudfront_origin_access_identity_response"
    echo -e "${RED}Cloudfront origin access identity creation failed${RESET}"
    # exit 1
fi

cloudfront_origin_access_identity_id=$(echo "$cloudfront_origin_access_identity_response" | jq -r '.CloudFrontOriginAccessIdentity.Id')
sed -i '' "s/\"origin_access_identity_id\": \"\"/\"origin_access_identity_id\": \"$cloudfront_origin_access_identity_id\"/g" project-settings$suffix.json
echo -e "Created cloudfront origin access identity ${BLUE}$cloudfront_origin_access_identity_id${RESET}"

static_bucket_policy="{
    \"Version\": \"2008-10-17\",
    \"Id\": \"PolicyForCloudFrontPrivateContent\",
    \"Statement\": [
        {
            \"Sid\": \"1\",
            \"Effect\": \"Allow\",
            \"Principal\": {
                \"AWS\": \"arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity $cloudfront_origin_access_identity_id\"
            },
            \"Action\": \"s3:GetObject\",
            \"Resource\": \"arn:aws:s3:::$static_bucket_name/*\"
        }
    ]
}"

static_bucket_put_policy_response=$(
    aws s3api put-bucket-policy \
        --bucket "$static_bucket_name" \
        --policy "$static_bucket_policy"
)

if [ $? -ne 0 ]; then
    echo "$static_bucket_put_policy_response"
    echo -e "${RED}S3 bucket policy update failed${RESET}"
    # exit 1
fi

echo -e "Put OAI policy on static bucket ${BLUE}$static_bucket_name${RESET}"

if [ "$BYO_WAF" = true ]; then
    echo -e "Using existing Web Application Firewall ${BLUE}$waf_id${RESET}"
else
    waf_response=$(
        aws wafv2 create-web-acl \
            --name "$project_name-waf" \
            --description "$project_name WAF" \
            --scope "CLOUDFRONT" \
            --default-action "{
                \"Allow\": {}
            }" \
            --rules "[
                {
                    \"Name\": \"AWS-AWSManagedRulesAmazonIpReputationList\",
                    \"Priority\": 0,
                    \"Statement\": {
                        \"ManagedRuleGroupStatement\": {
                            \"VendorName\": \"AWS\",
                            \"Name\": \"AWSManagedRulesAmazonIpReputationList\"
                        }
                    },
                    \"OverrideAction\": {
                        \"None\": {}
                    },
                    \"VisibilityConfig\": {
                        \"SampledRequestsEnabled\": true,
                        \"CloudWatchMetricsEnabled\": true,
                        \"MetricName\": \"AWS-AWSManagedRulesAmazonIpReputationList\"
                    }
                },
                {
                    \"Name\": \"AWS-AWSManagedRulesCommonRuleSet\",
                    \"Priority\": 1,
                    \"Statement\": {
                        \"ManagedRuleGroupStatement\": {
                            \"VendorName\": \"AWS\",
                            \"Name\": \"AWSManagedRulesCommonRuleSet\"
                        }
                    },
                    \"OverrideAction\": {
                        \"None\": {}
                    },
                    \"VisibilityConfig\": {
                        \"SampledRequestsEnabled\": true,
                        \"CloudWatchMetricsEnabled\": true,
                        \"MetricName\": \"AWS-AWSManagedRulesCommonRuleSet\"
                    }
                },
                {
                    \"Name\": \"AWS-AWSManagedRulesKnownBadInputsRuleSet\",
                    \"Priority\": 2,
                    \"Statement\": {
                        \"ManagedRuleGroupStatement\": {
                            \"VendorName\": \"AWS\",
                            \"Name\": \"AWSManagedRulesKnownBadInputsRuleSet\"
                        }
                    },
                    \"OverrideAction\": {
                        \"None\": {}
                    },
                    \"VisibilityConfig\": {
                        \"SampledRequestsEnabled\": true,
                        \"CloudWatchMetricsEnabled\": true,
                        \"MetricName\": \"AWS-AWSManagedRulesKnownBadInputsRuleSet\"
                    }
                }
            ]" \
            --visibility-config "{
                \"SampledRequestsEnabled\": true,
                \"CloudWatchMetricsEnabled\": true,
                \"MetricName\": \"$project_name-waf\"
            }" \
            --region "us-east-1" \
            --tags Key=Project,Value=$project_name
    )

    if [ $? -ne 0 ]; then
        echo "$waf_response"
        echo -e "${RED}WAF creation failed${RESET}"
        # exit 1
    fi

    waf_id=$(echo "$waf_response" | jq -r '.Summary.ARN')  # TODO: Change to Arn
    sed -i '' "s/\"waf_id\": \"\"/\"waf_id\": \"$waf_id\"/g" project-settings$suffix.json

    echo -e "Created Web Application Firewall ${BLUE}$waf_id${RESET}"
fi

cloudfront_distribution_response=$(
    aws cloudfront create-distribution-with-tags \
        --distribution-config "{
            \"DistributionConfig\": {
                \"Aliases\": {
                    \"Quantity\": 1,
                    \"Items\": [
                        \"$domain_name\"
                    ]
                },
                \"CallerReference\": \"$project_name\",
                \"Comment\": \"$project_name\",
                \"DefaultCacheBehavior\": {
                    \"AllowedMethods\": {
                        \"Quantity\": 2,
                        \"Items\": [
                            \"GET\",
                            \"HEAD\"
                        ],
                        \"CachedMethods\": {
                            \"Quantity\": 2,
                            \"Items\": [
                                \"GET\",
                                \"HEAD\"
                            ]
                        }
                    },
                    \"CachePolicyId\": \"658327ea-f89d-4fab-a63d-7e88639e58f6\",
                    \"TargetOriginId\": \"$static_bucket_name\",
                    \"ViewerProtocolPolicy\": \"redirect-to-https\"
                },
                \"DefaultRootObject\": \"index.html\",
                \"Enabled\": true,
                \"Origins\": {
                    \"Quantity\": 1,
                    \"Items\": [
                        {
                            \"Id\": \"$static_bucket_name\",
                            \"DomainName\": \"$static_bucket_name.s3.$aws_region.amazonaws.com\",
                            \"S3OriginConfig\": {
                                \"OriginAccessIdentity\": \"origin-access-identity/cloudfront/$cloudfront_origin_access_identity_id\"
                            }
                        }
                    ]
                },
                \"ViewerCertificate\": {
                    \"ACMCertificateArn\": \"$certificate_arn\",
                    \"SSLSupportMethod\": \"sni-only\",
                    \"MinimumProtocolVersion\": \"TLSv1.2_2021\"
                },
                \"WebACLId\": \"$waf_id\"
            },
            \"Tags\": {
                \"Items\": [
                    {
                        \"Key\": \"Project\",
                        \"Value\": \"$project_name\"
                    }
                ]
            }
        }" \
        --region $aws_region
)

if [ $? -ne 0 ]; then
    echo "$cloudfront_distribution_response"
    echo -e "${RED}Cloudfront distribution creation failed${RESET}"
    # exit 1
fi

cloudfront_distribution_id=$(echo "$cloudfront_distribution_response" | jq -r '.Distribution.Id')
sed -i '' "s/\"distribution_id\": \"\"/\"distribution_id\": \"$cloudfront_distribution_id\"/g" project-settings$suffix.json

echo -e "Created cloudfront distribution ${BLUE}$cloudfront_distribution_id${RESET}"

########################################################
# Secrets Manager setup                                #
########################################################
echo
echo -e "${CYAN}[Secrets Manager Setup]${RESET}"

# Create an empty development secret on Secrets Manager
secret_response=$(
    aws secretsmanager create-secret \
        --name "$secret_name" \
        --secret-string "{
            \"APP_SYNC_HOST\": \"\",
            \"APPSYNC_ACCESS_KEY\": \"\",
            \"APPSYNC_SECRET_KEY\": \"\",
            \"AWS_AUDIO_FILE_BUCKET\": \"$audio_bucket_name\",
            \"AWS_CLOUDFRONT_DOMAIN_NAME\": \"$frontend_endpoint\",
            \"AWS_DB_INSTANCE_IDENTIFIER\": \"$rds_instance_identifier\",
            \"AWS_DB_SECRET_ARN\": \"$rds_secret_arn\",
            \"AWS_LOG_GROUP_NAME\": \"/aws/lambda/$project_name\",
            \"AWS_LOG_PATTERN\": \"$backend_domain\",
            \"AWS_TABLENAME_USER\": \"\",
            \"AWS_TABLENAME_TAP\": \"\",
            \"AWS_TABLENAME_AUDIO_FILE\": \"\",
            \"AWS_TABLENAME_AUDIO_TAP\": \"\",
            \"COGNITO_PARTICIPANT_CLIENT_ID\": \"$participant_client_id\",
            \"COGNITO_PARTICIPANT_CLIENT_SECRET\": \"$participant_client_secret\",
            \"COGNITO_PARTICIPANT_DOMAIN\": \"$participant_user_pool_domain\",
            \"COGNITO_PARTICIPANT_LOGOUT_URI\": \"$frontend_endpoint/login\",
            \"COGNITO_PARTICIPANT_REDIRECT_URI\": \"$backend_endpoint/auth/participant/callback\",
            \"COGNITO_PARTICIPANT_REGION\": \"$aws_region\",
            \"COGNITO_PARTICIPANT_USER_POOL_ID\": \"$participant_user_pool_id\",
            \"FITBIT_CLIENT_ID\": \"$fitbit_client_id\",
            \"FITBIT_CLIENT_SECRET\": \"$fitbit_client_secret\",
            \"FITBIT_REDIRECT_URI\": \"$backend_endpoint/api/fitbit/callback\",
            \"FLASK_SECRET_KEY\": \"$flask_secret_key\",
            \"LAMBDA_FUNCTION_NAME\": \"$wearable_data_retrieval_function_name\",
            \"TM_FSTRING\": \"$project_name-{api_name}-tokens\",
            \"COGNITO_RESEARCHER_CLIENT_ID\": \"$researcher_client_id\",
            \"COGNITO_RESEARCHER_CLIENT_SECRET\": \"$researcher_client_secret\",
            \"COGNITO_RESEARCHER_DOMAIN\": \"$researcher_user_pool_domain\",
            \"COGNITO_RESEARCHER_LOGOUT_URI\": \"$frontend_endpoint/coordinator/login\"
            \"COGNITO_RESEARCHER_REDIRECT_URI\": \"$backend_endpoint/auth/researcher/callback\",
            \"COGNITO_RESEARCHER_REGION\": \"$aws_region\",
            \"COGNITO_RESEARCHER_USER_POOL_ID\": \"$researcher_user_pool_id\",
        }" \
        --tags Key=Project,Value=$project_name
)

if [ $? -ne 0 ]; then
    echo "$secret_response"
    echo -e "${RED}development secret creation failed${RESET}"
    # exit 1
fi

echo -e "Created development secret ${BLUE}$secret_name${RESET}"

# Create an empty tokens secret on Secrets Manager
tokens_secret_response=$(
    aws secretsmanager create-secret \
        --name "$tokens_secret_name" \
        --tags Key=Project,Value=$project_name
)

if [ $? -ne 0 ]; then
    echo "$tokens_secret_response"
    echo -e "${RED}tokens secret creation failed${RESET}"
    # exit 1
fi

echo -e "Created tokens secret ${BLUE}$tokens_secret_name${RESET}"

########################################################
# Lambda setup                                         #
########################################################
echo
echo -e "${CYAN}[Lambda Setup]${RESET}"

aws ecr get-login-password | docker login --username AWS --password-stdin $aws_account_id.dkr.ecr.us-east-1.amazonaws.com

if [ $? -ne 0 ]; then
    echo -e "${RED}ECR login failed${RESET}"
    # exit 1
fi

echo "Logged in to ECR"

cp -r shared functions/wearable_data_retrieval/shared

docker build \
    --platform linux/amd64 \
    -t $wearable_data_retrieval_ecr_repo_name\:latest \
    functions/wearable_data_retrieval

rm -rf functions/wearable_data_retrieval/shared

if [ $? -ne 0 ]; then
    echo -e "${RED}wearable data retrieval container creation failed${RESET}"
    # exit 1
fi

echo -e "Created wearable data retrieval image ${BLUE}$wearable_data_retrieval_ecr_repo_name\:latest${RESET}"

wearable_data_retrieval_create_repo_response=$(
    aws ecr create-repository \
        --repository-name "$wearable_data_retrieval_image_name" \
        --image-scanning-configuration scanOnPush=true
)

if [ $? -ne 0 ]; then
    echo "$wearable_data_retrieval_create_repo_response"
    echo -e "${RED}wearable data retrieval repository creation failed${RESET}"
    # exit 1
fi

echo -e "Created wearable data retrieval repository ${BLUE}$wearable_data_retrieval_ecr_repo_name${RESET}"

docker push $wearable_data_retrieval_ecr_repo_name\:latest

if [ $? -ne 0 ]; then
    echo -e "${RED}wearable data retrieval container push failed${RESET}"
    # exit 1
fi

echo -e "Pushed wearable data retrieval container to ECR ${BLUE}$wearable_data_retrieval_ecr_repo_name${RESET}"

wearable_data_retrieval_policy="{
    \"Version\": \"2012-10-17\",
    \"Statement\": [
        {
            \"Effect\": \"Allow\",
            \"Action\": [
                \"secretsmanager:ListSecrets\",
                \"secretsmanager:DescribeSecret\",
                \"secretsmanager:GetSecretValue\",
                \"secretsmanager:PutSecretValue\",
                \"secretsmanager:UpdateSecret\"
            ],
            \"Resource\": [
                \"arn:aws:secretsmanager:"$aws_region":"$aws_account_id":secret:"$tokens_secret_name"\",
                \"arn:aws:secretsmanager:"$aws_region":"$aws_account_id":secret:"$secret_name"\"
            ]
        },
        {
            \"Effect\": \"Allow\",
            \"Action\": [
                \"secretsmanager:ListSecrets\"
            ],
            \"Resource\": [
                \"arn:aws:secretsmanager:"$aws_region":"$aws_account_id":secret:*\"
            ]
        },
        {
            \"Effect\": \"Allow\",
            \"Action\": [
                \"s3:PutObject\"
            ],
            \"Resource\": \"arn:aws:s3:::"$logs_bucket_name"\"
        },
        {
            \"Effect\": \"Allow\",
            \"Action\": \"logs:CreateLogGroup\",
            \"Resource\": \"arn:aws:logs:"$aws_region":"$aws_account_id":*\"
        },
        {
            \"Effect\": \"Allow\",
            \"Action\": [
                \"logs:CreateLogStream\",
                \"logs:PutLogEvents\"
            ],
            \"Resource\": [
                \"arn:aws:logs:"$aws_region":"$aws_account_id":log-group:/aws/lambda/"$wearable_data_retrieval_function_name":*\"
            ]
        }
    ]
}"

wearable_data_retrieval_policy_response=$(
    aws iam create-policy \
        --policy-name "$wearable_data_retrieval_policy_name" \
        --policy-document "$wearable_data_retrieval_policy" \
        --tags Key=Project,Value=$project_name
)

if [ $? -ne 0 ]; then
    echo "$wearable_data_retrieval_policy_response"
    echo -e "${RED}wearable data retrieval policy creation failed${RESET}"
    # exit 1
fi

wearable_data_retrieval_policy_arn=$(echo "$wearable_data_retrieval_policy_response" | jq -r '.Policy.Arn')

echo -e "Created wearable data retrieval policy ${BLUE}$wearable_data_retrieval_policy_name${RESET}"

wearable_data_retrieval_role_policy="{
    \"Version\": \"2012-10-17\",
    \"Statement\": [
        {
            \"Effect\": \"Allow\",
            \"Principal\": {
                \"Service\": \"lambda.amazonaws.com\"
            },
            \"Action\": \"sts:AssumeRole\"
        }
    ]
}"

wearable_data_retrieval_role_response=$(
    aws iam create-role \
        --role-name "$wearable_data_retrieval_role_name" \
        --assume-role-policy-document "$wearable_data_retrieval_role_policy" \
        --tags Key=Project,Value=$project_name
)

if [ $? -ne 0 ]; then
    echo "$wearable_data_retrieval_role_response"
    echo -e "${RED}wearable data retrieval role creation failed${RESET}"
    # exit 1
fi

wearable_data_retrieval_attach_ecr_role_response=$(
    aws iam attach-role-policy \
        --role-name "$wearable_data_retrieval_role_name" \
        --policy-arn "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPullOnly"
)

if [ $? -ne 0 ]; then
    echo "$wearable_data_retrieval_attach_ecr_role_response"
    echo -e "${RED}wearable data retrieval attach ecr role failed${RESET}"
    # exit 1
fi

wearable_data_retrieval_attach_execution_role_response=$(
    aws iam attach-role-policy \
        --role-name "$wearable_data_retrieval_role_name" \
        --policy-arn "$wearable_data_retrieval_policy_arn"
)

if [ $? -ne 0 ]; then
    echo "$wearable_data_retrieval_attach_execution_role_response"
    echo -e "${RED}wearable data retrieval attach execution role failed${RESET}"
    # exit 1
fi

wearable_data_retrieval_role_arn=$(
    aws iam get-role \
        --role-name "$wearable_data_retrieval_role_name" \
        --query "Role.Arn" \
        --output text
)

if [ $? -ne 0 ]; then
    echo "$wearable_data_retrieval_role_arn"
    echo -e "${RED}wearable data retrieval role arn retrieval failed${RESET}"
    # exit 1
fi

echo -e "Created wearable data retrieval role ${BLUE}$wearable_data_retrieval_role_name${RESET}"

wearable_data_retrieval_lambda_function_response=$(
    aws lambda create-function \
        --function-name "$wearable_data_retrieval_function_name" \
        --role "$wearable_data_retrieval_role_arn" \
        --code ImageUri="$wearable_data_retrieval_ecr_repo_name":latest \
        --package-type Image \
        --timeout 300 \
        --memory-size 1024 \
        --environment "{
            \"Variables\": {
                \"AWS_CONFIG_SECRET_NAME\": \"$secret_name\",
                \"AWS_KEYS_SECRET_NAME\": \"$tokens_secret_name\",
                \"S3_BUCKET_NAME\": \"$logs_bucket_name\"
            }
        }" \
        --tags Key=Project,Value=$project_name
)

if [ $? -ne 0 ]; then
    echo "$wearable_data_retrieval_lambda_function_response"
    echo -e "${RED}wearable data retrieval lambda function creation failed${RESET}"
    # exit 1
fi

echo -e "Created wearable data retrieval lambda function ${BLUE}$wearable_data_retrieval_function_name${RESET}"

########################################################
# App Setup                                            #
########################################################
echo
echo -e "${CYAN}[App Setup]${RESET}"

# 1. Build docker image
# 2. Create ECR repo
# 3. Push image to ECR
# 4. Create role
# 5. Attach policies to role
# 6. Create function
# 7. Create API Gateway
# 8. Create keep warm role
# 9. Create keep warm event rule
# 10. Create keep warm event target
# 11. Create keep warm rule policy
# 12. Create keep warm role policy
# 13. Create keep warm role policy attachment
# 14. Create keep warm event target policy
# 15. Create keep warm event target policy attachment

########################################################
# Frontend setup                                       #
########################################################
echo
echo -e "${CYAN}[Frontend Setup]${RESET}"

cd frontend

npm install &> /dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}frontend setup failed${RESET}"
    # exit 1
fi

echo -e "Installed frontend dependencies"

npx tailwindcss -i ./src/index.css -o ./src/output.css &> /dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}tailwindcss setup failed${RESET}"
    # exit 1
fi

echo -e "Compiled tailwindcss"

echo
echo -e "${GREEN}[Installation complete]${RESET}"
echo -e "Check your email for a temporary password for the researcher admin user"
echo -e "You can now start the development server with ${BLUE}npm run start${RESET} and ${BLUE}flask run${RESET}"
