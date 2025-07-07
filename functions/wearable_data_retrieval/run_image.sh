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
NETWORK=""

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
        -*|--*)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

if [ -z "$NETWORK" ]; then
    echo "Network is required using --network"
    exit 1
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

docker run \
    -itp 9000:8080 \
    --env-file functions/wearable_data_retrieval/.env \
    --rm \
    --platform linux/amd64 \
    --network $NETWORK \
    wearable-data-retrieval-dev

