NOTESTS=0
NOBUILD=0
NOCACHE=0
TAG=latest

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

if [ -f secret-deploy.env ]; then
    export $(cat secret-deploy.env | xargs)
else
    echo "secret-deploy.env not found."
    exit 1
fi

DOCKER_SERVER=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
DOCKER_IMAGE=${DOCKER_SERVER}/${AWS_ECR_REPO_NAME}:${TAG}

if [ $NOBUILD -eq 0 ]; then
    aws ecr get-login-password | docker login --username AWS --password-stdin ${DOCKER_SERVER}
    if [ $? -ne 0 ]; then
        exit 1
    fi

    if [ $NOTESTS -eq 0 ]; then
        pytest

        if [ $? -ne 0 ]; then
            exit 1
        fi
    else
        echo "Skipping tests..."
    fi

    zappa save-python-settings-file
    if [ $NOCACHE -eq 1 ]; then
        docker build --no-cache -t ${DOCKER_IMAGE} .
    else
        docker build -t ${DOCKER_IMAGE} .
    fi
    rm zappa_settings.py

    if [ $? -ne 0 ]; then
        exit 1
    fi

    docker push ${DOCKER_IMAGE}
    if [ $? -ne 0 ]; then
        exit 1
    fi
fi

zappa status app &> /dev/null
if [ $? -eq 1 ]; then
    zappa deploy app -d ${DOCKER_IMAGE}
else
    zappa update app -d ${DOCKER_IMAGE}
fi

echo "Enabling CORS..."
RESPONSE_PARAMETERS=$(jq -jrc --arg origin "'$AWS_CLOUDFRONT_DOMAIN_NAME'" \
    '. += { "method.response.header.Access-Control-Allow-Origin": $origin }' <<< "$(cat cors.json)")

ZAPPA_STATUS=$(zappa status app -j)
if [ $? -ne 0 ]; then
    exit 1
fi

REST_API_ID=$(echo "$ZAPPA_STATUS" | jq -r '."API Gateway URL"' | grep -oP "https://+\K\w{10}")
RESOURCE_ID=$(aws apigateway get-resources --rest-api-id $REST_API_ID | jq -r '.items[] | select(.path == "/") | .id')
if [ $? -ne 0 ]; then
    exit 1
fi

aws apigateway put-method-response \
    --rest-api-id $REST_API_ID \
    --resource-id $RESOURCE_ID \
    --http-method ANY \
    --status-code 200 \
    --response-parameters "method.response.header.Access-Control-Allow-Credentials=true","method.response.header.Access-Control-Allow-Headers=true","method.response.header.Access-Control-Allow-Methods=true","method.response.header.Access-Control-Allow-Origin=true"

aws apigateway put-integration-response \
    --rest-api-id $REST_API_ID \
    --resource-id $RESOURCE_ID \
    --http-method ANY \
    --status-code 200 \
    --response-parameters $RESPONSE_PARAMETERS
