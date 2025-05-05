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
DEBUG=0
STAGING=0

# parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cache)
            NOCACHE=1
            shift
            ;;
        --debug)
            DEBUG=1
            shift
            ;;
        --staging)
            STAGING=1
            shift
            ;;
        -*|--*)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

cp -r ../../shared shared
if [ $NOCACHE -eq 1 ]; then
    docker build --platform linux/amd64 --no-cache -t wearable-data-retrieval:test .
else
    docker build --platform linux/amd64 -t wearable-data-retrieval:test .
fi
if [ $? -ne 0 ]; then
    rm -rf shared
    exit 1
fi
rm -rf shared

if [ "$STAGING" -eq 1 ]; then
    docker run --rm \
        --platform linux/amd64 \
        --name wearable-data-retrieval-test \
        --network aws-network \
        -p 9000:8080 \
        --env-file .env \
        -e DEBUG=true \
        -e STAGING=true \
        wearable-data-retrieval:test
elif [ "$DEBUG" -eq 1 ]; then
    docker run --rm \
        --platform linux/amd64 \
        --name wearable-data-retrieval-test \
        --network aws-network \
        -p 9000:8080 \
        --env-file .env \
        -e TESTING=true \
        -e DEBUG=true \
        wearable-data-retrieval:test
else
    docker run --rm \
        --platform linux/amd64 \
        --name wearable-data-retrieval-test \
        --network aws-network \
        -p 9000:8080 \
        --env-file .env \
        -e TESTING=true \
        wearable-data-retrieval:test
fi
