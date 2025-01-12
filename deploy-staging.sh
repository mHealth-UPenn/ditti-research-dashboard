NOTESTS=0
NOBUILD=0
NOCACHE=0
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
if [ -f secret-staging.env ]; then
    export $(cat secret-staging.env | xargs)
else
    echo "secret-staging.env not found."
    exit 1
fi

DOCKER_SERVER=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
DOCKER_IMAGE=${DOCKER_SERVER}/${AWS_ECR_REPO_NAME}:${TAG}

# if --no-build was not used
if [ $NOBUILD -eq 0 ]; then

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
    zappa save-python-settings-file staging
    if [ $NOCACHE -eq 1 ]; then
        docker build --platform linux/amd64 --no-cache -t ${DOCKER_IMAGE} .
    else
        docker build --platform linux/amd64 -t ${DOCKER_IMAGE} .
    fi
    rm zappa_settings.py

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
zappa status staging &> /dev/null
if [ $? -eq 1 ]; then

    # deploy the app
    zappa deploy staging -d ${DOCKER_IMAGE}
else

    # update the app
    zappa update staging -d ${DOCKER_IMAGE}
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
