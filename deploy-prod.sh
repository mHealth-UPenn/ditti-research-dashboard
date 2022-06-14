NOTESTS=0
NOCACHE=0
TAG=latest

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-tests)
            NOTESTS=1
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

if [ -f secret-aws.env ]; then
    export $(cat secret-aws.env | xargs)
else
    echo "secret-aws.env not found."
    exit 1
fi

DOCKER_SERVER=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
DOCKER_IMAGE=${DOCKER_SERVER}/${AWS_ECR_IMAGE_NAME}:${TAG}

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
    docker build -t --no-cache ${DOCKER_IMAGE} .
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

if [ $(zappa status app -j) == *"Error: No Lambda aws-portal-app detected"* ]
then
    zappa deploy app -d ${DOCKER_IMAGE}
else
    zappa update app -d ${DOCKER_IMAGE}
fi
