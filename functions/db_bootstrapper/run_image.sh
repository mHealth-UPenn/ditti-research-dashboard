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
DATA_FILE=""

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
        --data-file)
            DATA_FILE=$2
            shift
            shift
            ;;
        -*|--*)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

if [ $NOCACHE -eq 1 ]; then
    docker build \
        --platform linux/amd64 \
        --no-cache \
        -t db-bootstrapper:test \
        -f functions/db_bootstrapper/Dockerfile \
        .
else
    docker build \
        --platform linux/amd64 \
        -t db-bootstrapper:test \
        -f functions/db_bootstrapper/Dockerfile \
        .
fi
if [ $? -ne 0 ]; then
    exit 1
fi

# Create network if it doesn't exist
docker network create db-bootstrapper-network || true

# Remove existing containers
docker stop moto-proxy || true
docker stop db-bootstrapper-test-db || true
docker stop db-bootstrapper-test || true
docker rm -f moto-proxy || true
docker rm -f db-bootstrapper-test-db || true
docker rm -f db-bootstrapper-test || true

# Create a dummy database
docker run \
    --name db-bootstrapper-test-db \
    --network db-bootstrapper-network \
    -e POSTGRES_USER=username \
    -e POSTGRES_PASSWORD=password \
    -e POSTGRES_DB=db \
    -d postgres:16

# Build moto proxy
docker build -t moto-proxy -f moto_proxy/Dockerfile .

# Setup moto proxy
MOTO_LOCATION=$(pip show moto | grep "Location" | cut -d " " -f 2)

docker run -d \
    --name moto-proxy \
    --network db-bootstrapper-network \
    -p 5005:5005 \
    -v "${MOTO_LOCATION}/moto:/moto" \
    moto-proxy

export AWS_CA_BUNDLE="${MOTO_LOCATION}/moto/moto_proxy/ca.crt"
export HTTPS_PROXY=http://localhost:5005
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=testing
export AWS_SECRET_ACCESS_KEY=testing

# Create a dummy secret
aws secretsmanager create-secret \
    --name test-secret \
    --secret-string "{\"username\": \"username\", \"password\": \"password\"}"

DB_BOOTSTRAP_DATA_ARN=""
if [ -n "${DATA_FILE}" ]; then
    # Create a dummy bucket
    aws s3api create-bucket --bucket test-bucket

    # Upload the data to the bucket
    aws s3 cp "${DATA_FILE}" s3://test-bucket/data.json
    DB_BOOTSTRAP_DATA_ARN="s3://test-bucket/data.json"
fi

if [ "$DEBUG" -eq 1 ]; then
    docker run --rm \
        --platform linux/amd64 \
        --name db-bootstrapper-test \
        --network db-bootstrapper-network \
        -p 9000:8080 \
        -e AWS_CA_BUNDLE="/tmp/moto/moto_proxy/ca.crt" \
        -e HTTPS_PROXY=http://moto-proxy:5005 \
        -e AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION}" \
        -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
        -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
        -e DB_SECRET_ARN=test-secret \
        -e DB_HOST=db-bootstrapper-test-db \
        -e DB_PORT=5432 \
        -e DB_USER=username \
        -e DB_NAME=db \
        -e DB_BOOTSTRAP_DATA_ARN="${DB_BOOTSTRAP_DATA_ARN}" \
        -v "${MOTO_LOCATION}/moto:/tmp/moto" \
        db-bootstrapper:test
else
    docker run --rm \
        --platform linux/amd64 \
        --name db-bootstrapper-test \
        --network db-bootstrapper-network \
        -p 9000:8080 \
        -e AWS_CA_BUNDLE="/tmp/moto/moto_proxy/ca.crt" \
        -e HTTPS_PROXY=http://moto-proxy:5005 \
        -e AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION}" \
        -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
        -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
        -e DB_SECRET_ARN=test-secret \
        -e DB_HOST=db-bootstrapper-test-db \
        -e DB_PORT=5432 \
        -e DB_USER=username \
        -e DB_NAME=db \
        -e DB_BOOTSTRAP_DATA_ARN="${DB_BOOTSTRAP_DATA_ARN}" \
        -v "${MOTO_LOCATION}/moto:/tmp/moto" \
        db-bootstrapper:test
fi
