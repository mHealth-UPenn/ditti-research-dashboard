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

NOCACHE=0
PORT=9001
NETWORK=""
IAM_STACK=""
HELP=0

HELP_MESSAGE="
Usage: $0 --network <network> --iam-stack <iam-stack> [options]

Options:
    --network: Network to use
    --iam-stack: Stack name to use
    --no-cache: Build without cache (default: false)
    --port: Port to use (default: 9001)
    --help: Show this help message
"

# parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cache)
            NOCACHE=1
            shift
            ;;
        --network)
            NETWORK=$2
            shift 2
            ;;
        --port)
            PORT=$2
            shift
            shift
            ;;
        --iam-stack)
            IAM_STACK=$2
            shift 2
            ;;
        --help)
            HELP=1
            shift
            ;;
        -*|--*)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

if [ $HELP -eq 1 ] || [ -z "$NETWORK" ] || [ -z "$IAM_STACK" ]; then
    echo "$HELP_MESSAGE"
    exit 0
fi

if [ $NOCACHE -eq 1 ]; then
    docker build \
        -t wearable-data-retrieval-dev \
        --platform linux/amd64 \
        --secret id=aws,src=$HOME/.aws/credentials \
        --target dev \
        --no-cache \
        -f functions/wearable_data_retrieval/Dockerfile .
else
    docker build \
        -t wearable-data-retrieval-dev \
        --platform linux/amd64 \
        --secret id=aws,src=$HOME/.aws/credentials \
        --target dev \
        -f functions/wearable_data_retrieval/Dockerfile .
fi

if [ $? -ne 0 ]; then
    echo "Failed to build the image"
    exit 1
fi

if [ -z "$IAM_STACK" ]; then
    echo "Stack name is required using --iam-stack"
    exit 1
fi

ROLE_ARN=$(aws cloudformation describe-stacks \
    --stack-name $IAM_STACK \
    --query "Stacks[0].Outputs[?OutputKey=='WearableDataRetrievalLambdaRoleArn'].OutputValue" \
    --output text)

if [ $? -ne 0 ]; then
    echo "Failed to get the role ARN"
    exit 1
fi

docker run \
    -itp "${PORT}:8080" \
    --env-file functions/wearable_data_retrieval/.env \
    -e ROLE_ARN=$ROLE_ARN \
    --rm \
    --platform linux/amd64 \
    --network $NETWORK \
    --volume $HOME/.aws/credentials:/root/.aws/credentials \
    wearable-data-retrieval-dev

