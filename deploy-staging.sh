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

DEPLOY_APP=0
DEPLOY_WEARABLE_DATA_RETRIEVAL=0
DEPLOY_FLASK_SECRET_KEY_ROTATOR=0
NOCACHE=0

HELP_MESSAGE="
Usage: $0 (--app|--wearable-data-retrieval|--flask-secret-key-rotator) [--no-cache] [--help]

Options:
    --app: Deploy the app
    --wearable-data-retrieval: Deploy the wearable data retrieval function
    --flask-secret-key-rotator: Deploy the flask secret key rotator function
    --no-cache: Build without cache (default: false)
    --help: Show this help message
"

# parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --app)
            DEPLOY_APP=1
            shift
            ;;
        --wearable-data-retrieval)
            DEPLOY_WEARABLE_DATA_RETRIEVAL=1
            shift
            ;;
        --flask-secret-key-rotator)
            DEPLOY_FLASK_SECRET_KEY_ROTATOR=1
            shift
            ;;
        --no-cache)
            NOCACHE=1
            shift
            ;;
        --help)
            echo "$HELP_MESSAGE"
            exit 0
            ;;
        -*|--*)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

if [ $DEPLOY_APP -eq 0 ] && [ $DEPLOY_WEARABLE_DATA_RETRIEVAL -eq 0 ] && [ $DEPLOY_FLASK_SECRET_KEY_ROTATOR -eq 0 ]; then
    echo "No deployment target specified. Please specify one or more of --app, --wearable-data-retrieval, or --flask-secret-key-rotator."
    echo "$HELP_MESSAGE"
    exit 1
fi

# export deployment env variables
if [ -f secret-staging.env ]; then
    export $(cat secret-staging.env | xargs)
else
    echo "secret-staging.env not found."
    exit 1
fi

# login docker
DOCKER_SERVER=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
aws ecr get-login-password | docker login --username AWS --password-stdin ${DOCKER_SERVER}
if [ $? -ne 0 ]; then
    exit 1
fi

if [ $DEPLOY_APP -eq 1 ]; then
    DOCKER_IMAGE=${DOCKER_SERVER}/${AWS_ECR_REPO_NAME}:staging

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

    # include the zappa settings file in the docker image
    zappa save-python-settings-file staging
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

    # check if the app has been deployed yet
    zappa status staging &> /dev/null
    if [ $? -eq 1 ]; then

        # deploy the app
        zappa deploy staging -d ${DOCKER_IMAGE}
    else

        # update the app
        zappa update staging -d ${DOCKER_IMAGE}
    fi
fi

if [ $DEPLOY_WEARABLE_DATA_RETRIEVAL -eq 1 ] || [ $DEPLOY_FLASK_SECRET_KEY_ROTATOR -eq 1 ]; then
    STACK_OUTPUTS=$(aws cloudformation describe-stacks --stack-name ${AWS_FUNCTIONS_CLOUDFORMATION_STACK_NAME} | jq ".Stacks[0].Outputs")
fi

if [ $DEPLOY_WEARABLE_DATA_RETRIEVAL -eq 1 ]; then
    echo "Deploying wearable data retrieval..."
    WEARABLE_DATA_RETRIEVAL_LAMBDA_FUNCTION_NAME=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey == "WearableDataRetrievalLambdaFunctionName") | .OutputValue')
    WEARABLE_DATA_RETRIEVAL_IMAGE_URI=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey == "WearableDataRetrievalImageUri") | .OutputValue')

    if [ $NOCACHE -eq 1 ]; then
        docker build \
            -f functions/wearable_data_retrieval/Dockerfile \
            -t ${WEARABLE_DATA_RETRIEVAL_IMAGE_URI} \
            --platform linux/amd64 \
            --secret id=aws,src=$HOME/.aws/credentials \
            --target prod \
            --no-cache .
    else
        docker build \
            -f functions/wearable_data_retrieval/Dockerfile \
            -t ${WEARABLE_DATA_RETRIEVAL_IMAGE_URI} \
            --platform linux/amd64 \
            --secret id=aws,src=$HOME/.aws/credentials \
            --target prod .
    fi

    if [ $? -ne 0 ]; then
        echo "Failed to build the wearable data retrieval function."
        exit 1
    fi

    docker push ${WEARABLE_DATA_RETRIEVAL_IMAGE_URI}

    if [ $? -ne 0 ]; then
        echo "Failed to push the wearable data retrieval function."
        exit 1
    fi

    aws lambda update-function-code \
        --image-uri ${WEARABLE_DATA_RETRIEVAL_IMAGE_URI} \
        --function-name ${WEARABLE_DATA_RETRIEVAL_LAMBDA_FUNCTION_NAME} \
        > /dev/null

    if [ $? -ne 0 ]; then
        echo "Failed to update the wearable data retrieval function."
        exit 1
    fi

    echo "Waiting for the function to update..."
    aws lambda wait function-updated-v2 --function-name ${WEARABLE_DATA_RETRIEVAL_LAMBDA_FUNCTION_NAME}

    echo "Wearable data retrieval function updated."
fi

if [ $DEPLOY_FLASK_SECRET_KEY_ROTATOR -eq 1 ]; then
    echo "Deploying flask secret key rotator..."
    FLASK_SECRET_KEY_ROTATOR_LAMBDA_FUNCTION_NAME=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey == "FlaskSecretKeyRotatorLambdaFunctionName") | .OutputValue')
    FLASK_SECRET_KEY_ROTATOR_IMAGE_URI=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey == "FlaskSecretKeyRotatorImageUri") | .OutputValue')

    if [ $NOCACHE -eq 1 ]; then
        docker build \
            -f functions/secret_rotator/Dockerfile \
            -t ${FLASK_SECRET_KEY_ROTATOR_IMAGE_URI} \
            --platform linux/amd64 \
            --no-cache .
    else
        docker build \
            -f functions/secret_rotator/Dockerfile \
            -t ${FLASK_SECRET_KEY_ROTATOR_IMAGE_URI} \
            --platform linux/amd64 .
    fi

    if [ $? -ne 0 ]; then
        echo "Failed to build the flask secret key rotator function."
        exit 1
    fi

    docker push ${FLASK_SECRET_KEY_ROTATOR_IMAGE_URI}

    if [ $? -ne 0 ]; then
        echo "Failed to push the flask secret key rotator function."
        exit 1
    fi

    aws lambda update-function-code \
        --image-uri ${FLASK_SECRET_KEY_ROTATOR_IMAGE_URI} \
        --function-name ${FLASK_SECRET_KEY_ROTATOR_LAMBDA_FUNCTION_NAME} \
        > /dev/null

    if [ $? -ne 0 ]; then
        echo "Failed to update the flask secret key rotator function."
        exit 1
    fi

    echo "Waiting for the function to update..."
    aws lambda wait function-updated-v2 --function-name ${FLASK_SECRET_KEY_ROTATOR_LAMBDA_FUNCTION_NAME}

    echo "Flask secret key rotator function updated."
fi
