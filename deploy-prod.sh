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

NOTESTS=0
NOBUILD=0
NOCACHE=0
NOROTATOR=0
TAG=latest

# parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-tests)
            NOTESTS=1
            shift
            ;;
        --no-build)
            NOBUILD=1
            shift
            ;;
        --no-cache)
            NOCACHE=1
            shift
            ;;
        --no-rotator)
            NOROTATOR=1
            shift
            ;;
        -t|--tag)
            TAG="$2"
            shift
            shift
            ;;
        -*|--*)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

# export deployment env variables
if [ -f secret-deploy.env ]; then
    export $(cat secret-deploy.env | xargs)
else
    echo "secret-deploy.env not found."
    exit 1
fi

DOCKER_SERVER=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
DOCKER_IMAGE=${DOCKER_SERVER}/${AWS_ECR_REPO_NAME}:${TAG}

# if --no-build was not used
if [ $NOBUILD -eq 0 ]; then

    # --- AWS Parameters and Secrets Lambda Extension ---
    # To improve performance and reduce costs, the application uses the
    # AWS-Parameters-and-Secrets-Extension. This extension retrieves and
    # caches secrets from AWS Secrets Manager. The following steps download
    # the extension, making it available to the Docker build process.
    echo "Downloading AWS Parameters and Secrets Lambda Extension..."

    # A specific, known-working public ARN for the extension is used here
    # to avoid potential permission errors with `list-layer-versions` or
    # `ssm:GetParameter` that can occur when attempting to dynamically find
    # the latest version.
    # NOTE: This version may need to be updated in the future.
    EXTENSION_ARN="arn:aws:lambda:${AWS_REGION}:177933569100:layer:AWS-Parameters-and-Secrets-Lambda-Extension:17"

    # Retrieve the presigned download URL for the layer's content.
    LAYER_DOWNLOAD_URL=$(aws lambda get-layer-version-by-arn \
        --arn "$EXTENSION_ARN" \
        --query 'Content.Location' \
        --output text)

    if [ -z "$LAYER_DOWNLOAD_URL" ]; then
        echo "Failed to get download URL for the layer. Check if the ARN is correct and the region is supported."
        exit 1
    fi

    # Download and unzip the extension
    curl -L "$LAYER_DOWNLOAD_URL" --output extension.zip
    unzip -q extension.zip # This creates an `extensions` directory
    if [ $? -ne 0 ]; then
        echo "Failed to unzip the extension."
        rm -f extension.zip
        rm -rf extensions
        exit 1
    fi

    # login docker
    aws ecr get-login-password | docker login --username AWS --password-stdin ${DOCKER_SERVER}
    if [ $? -ne 0 ]; then
        exit 1
    fi

    # if --no-tests was not used
    if [ $NOTESTS -eq 0 ]; then

        # run tests
        pytest

        if [ $? -ne 0 ]; then
            exit 1
        fi
    else
        echo "Skipping tests..."
    fi

    # include the zappa settings file in the docker image
    zappa save-python-settings-file app
    if [ $NOCACHE -eq 1 ]; then
        docker buildx build --platform linux/amd64 --provenance=false --output=type=docker --no-cache -t ${DOCKER_IMAGE} .
    else
        docker buildx build --platform linux/amd64 --provenance=false --output=type=docker -t ${DOCKER_IMAGE} .
    fi
    rm zappa_settings.py
    # Clean up the downloaded extension files after the build.
    rm -f extension.zip
    rm -rf extensions

    if [ $? -ne 0 ]; then
        exit 1
    fi

    # push the docker image
    docker push ${DOCKER_IMAGE}
    if [ $? -ne 0 ]; then
        exit 1
    fi
fi

# check if the app has been deployed yet
zappa status app &> /dev/null
if [ $? -eq 1 ]; then

    # deploy the app
    zappa deploy app -d ${DOCKER_IMAGE}
else

    # update the app
    zappa update app -d ${DOCKER_IMAGE}
fi

if [ $NOROTATOR -eq 0 ]; then
    APP_URL=$(zappa status app -j | jq -r '."API Gateway URL"')
    if [ -z "$APP_URL" ]; then
        echo "Failed to get App URL for production. Exiting."
        exit 1
    fi
    # Deploy/update the secret rotator Lambda
    ROTATOR_STAGE="fsr-prod"
    ROTATOR_ECR_REPO_NAME="fsr-prod"
    ROTATOR_PROJECT_NAME="fs-rotator"
    ROTATOR_FUNCTION_NAME="${ROTATOR_PROJECT_NAME}-${ROTATOR_STAGE}"
    ROTATOR_ROLE_NAME="${ROTATOR_FUNCTION_NAME}-ZappaLambdaExecutionRole"
    SECRET_NAME="flask-secret-key-prod"
    # Dynamically retrieve the Lambda function name for the production app
    APP_FUNCTION_NAME=$(zappa status app -j | jq -r '."Lambda Name"')
    if [ -z "$APP_FUNCTION_NAME" ]; then
        echo "Failed to get Lambda function name for production. Exiting."
        exit 1
    fi

    ROTATOR_DOCKER_SERVER=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
    ROTATOR_DOCKER_IMAGE=${ROTATOR_DOCKER_SERVER}/${ROTATOR_ECR_REPO_NAME}:${TAG}

    echo "Checking for secret rotator ECR repository..."
    aws ecr describe-repositories --repository-names ${ROTATOR_ECR_REPO_NAME} > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Creating ECR repository ${ROTATOR_ECR_REPO_NAME}..."
        aws ecr create-repository --repository-name ${ROTATOR_ECR_REPO_NAME} > /dev/null
    fi

    echo "Building and pushing the secret rotator image..."
    (cd functions/secret_rotator && docker buildx build --platform linux/amd64 --provenance=false --output=type=docker -t ${ROTATOR_DOCKER_IMAGE} .)
    if [ $? -ne 0 ]; then
        exit 1
    fi
    docker push ${ROTATOR_DOCKER_IMAGE}
    if [ $? -ne 0 ]; then
        exit 1
    fi

    echo "Checking status of ${ROTATOR_STAGE}..."
    zappa status $ROTATOR_STAGE &> /dev/null
    if [ $? -eq 1 ]; then
        echo "Deploying ${ROTATOR_STAGE} for the first time..."
        # deploy the rotator
        zappa deploy $ROTATOR_STAGE -d ${ROTATOR_DOCKER_IMAGE}
    else
        echo "Updating ${ROTATOR_STAGE}..."
        # update the rotator
        zappa update $ROTATOR_STAGE -d ${ROTATOR_DOCKER_IMAGE}
    fi

    echo "Applying IAM policies and environment variables for ${ROTATOR_STAGE}..."
    SECRET_ARN=$(aws secretsmanager describe-secret --secret-id ${SECRET_NAME} --query ARN --output text)
    if [ $? -ne 0 ]; then
        echo "Failed to get ARN for secret ${SECRET_NAME}. Please ensure it exists and rotation is enabled."
        exit 1
    fi
    APP_FUNCTION_ARN="arn:aws:lambda:${AWS_REGION}:${AWS_ACCOUNT_ID}:function:${APP_FUNCTION_NAME}"

    POLICY_JSON=$(cat <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:DescribeSecret",
                "secretsmanager:GetSecretValue",
                "secretsmanager:PutSecretValue",
                "secretsmanager:UpdateSecretVersionStage"
            ],
            "Resource": "${SECRET_ARN}"
        },
        {
            "Effect": "Allow",
            "Action": "secretsmanager:GetRandomPassword",
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "lambda:UpdateFunctionConfiguration",
                "lambda:GetFunctionConfiguration",
                "lambda:GetFunction"
            ],
            "Resource": "${APP_FUNCTION_ARN}"
        }
    ]
}
EOF
)

    aws iam put-role-policy --role-name "${ROTATOR_ROLE_NAME}" --policy-name SecretsManagerRotatorPolicy --policy-document "${POLICY_JSON}"
    aws lambda remove-permission --function-name "${ROTATOR_FUNCTION_NAME}" --statement-id secrets-manager-rotator-invoke-permission > /dev/null 2>&1 || true
    aws lambda add-permission --function-name "${ROTATOR_FUNCTION_NAME}" --statement-id secrets-manager-rotator-invoke-permission --action lambda:InvokeFunction --principal secretsmanager.amazonaws.com --source-arn "${SECRET_ARN}"
    aws lambda update-function-configuration --function-name "${ROTATOR_FUNCTION_NAME}" --environment "Variables={APP_LAMBDA_FUNCTION_NAME=${APP_FUNCTION_NAME},APP_URL=${APP_URL}}"
fi

# echo "Enabling CORS..."

# # save the CORS policy as a JSON string with the CloudFront domain as the only allowed origin
# RESPONSE_PARAMETERS=$(jq -jrc --arg origin "'$AWS_CLOUDFRONT_DOMAIN_NAME'" \
#     '. += { "method.response.header.Access-Control-Allow-Origin": $origin }' <<< "$(cat cors.json)")

# # extract the REST API ID and resource ID from the zappa app status
# ZAPPA_STATUS=$(zappa status app -j)
# if [ $? -ne 0 ]; then
#     exit 1
# fi

# REST_API_ID=$(echo "$ZAPPA_STATUS" | jq -r '."API Gateway URL"' | cut -d"." -f1 | cut -d"/" -f3)
# RESOURCE_ID=$(aws apigateway get-resources --rest-api-id $REST_API_ID | jq -r '.items[] | select(.path == "/") | .id')
# if [ $? -ne 0 ]; then
#     exit 1
# fi

# # check if a method response already exists on the API gateway
# RESPONSES=$(aws apigateway get-method --rest-api-id $REST_API_ID --resource-id $RESOURCE_ID --http-method ANY | jq -rc ".methodResponses")

# # if not, create one
# if [ $RESPONSES = 'null' ]; then
#     aws apigateway put-method-response \
#         --rest-api-id $REST_API_ID \
#         --resource-id $RESOURCE_ID \
#         --http-method ANY \
#         --status-code 200 \
#         --response-parameters "method.response.header.Access-Control-Allow-Credentials=true","method.response.header.Access-Control-Allow-Headers=true","method.response.header.Access-Control-Allow-Methods=true","method.response.header.Access-Control-Allow-Origin=true"
# fi

# # enable CORS on the API gateway's method response
# aws apigateway put-integration-response \
#     --rest-api-id $REST_API_ID \
#     --resource-id $RESOURCE_ID \
#     --http-method ANY \
#     --status-code 200 \
#     --response-parameters $RESPONSE_PARAMETERS
