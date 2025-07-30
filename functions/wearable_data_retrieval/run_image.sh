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
DB_PORT=5433

HELP_MESSAGE="
Usage: $0 [options]

Options:
    --no-cache: Build without cache (default: false)
    --port: Port to use (default: 9001)
    --db-port: Port to use for the database (default: 5433)
    --help: Show this help message
"

# parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cache)
            NOCACHE=1
            shift
            ;;
        --port)
            PORT=$2
            shift
            shift
            ;;
        --db-port)
            DB_PORT=$2
            shift
            shift
            ;;
        --help)
            echo "$HELP_MESSAGE"
            exit 0
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
        -t wearable-data-retrieval:test \
        --platform linux/amd64 \
        --secret id=aws,src=$HOME/.aws/credentials \
        --target prod \
        --no-cache \
        -f functions/wearable_data_retrieval/Dockerfile .
else
    docker build \
        -t wearable-data-retrieval:test \
        --platform linux/amd64 \
        --secret id=aws,src=$HOME/.aws/credentials \
        --target prod \
        -f functions/wearable_data_retrieval/Dockerfile .
fi

if [ $? -ne 0 ]; then
    echo "Failed to build the image"
    exit 1
fi

# Create network if it doesn't exist
docker network create wearable-data-retrieval-network || true

# Remove existing containers
docker stop moto-proxy || true
docker stop wearable-data-retrieval-test-db || true
docker stop wearable-data-retrieval-test || true
docker rm -f moto-proxy || true
docker rm -f wearable-data-retrieval-test-db || true
docker rm -f wearable-data-retrieval-test || true

# Set up moto proxy
docker run -dp 5005:5000 \
    --name moto-proxy \
    --network wearable-data-retrieval-network \
    motoserver/moto:latest

export AWS_ENDPOINT_URL=http://localhost:5005
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=testing
export AWS_SECRET_ACCESS_KEY=testing

# Create a dummy bucket
aws s3api create-bucket --bucket test-bucket

# Create a mock lambda execution role
ROLE_ARN=$(aws iam create-role  \
    --role-name test-lambda-role \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }' \
    --query 'Role.Arn' \
    --output text)

# Create a dummy postgres container
docker run \
    --name wearable-data-retrieval-test-db \
    --network wearable-data-retrieval-network \
    -p "${DB_PORT}:5432" \
    -e POSTGRES_USER=test \
    -e POSTGRES_PASSWORD=test \
    -e PGPASSWORD=test \
    -e POSTGRES_DB=test \
    -d postgres:16

# Wait for database to be ready
while ! docker exec wearable-data-retrieval-test-db psql -U test -d test -c "SELECT 1;" > /dev/null 2>&1; do
    echo "Waiting for database to be ready..."
    sleep 1
done
echo "Database is ready"

# Bootstrap the database
export TEST_FLASK_DB="postgresql://test:test@localhost:${DB_PORT}/test"
export FLASK_CONFIG="Testing"
flask --app run.py db upgrade
flask --app run.py init-integration-testing-db

docker run --rm \
    --name wearable-data-retrieval-test \
    --platform linux/amd64 \
    --network wearable-data-retrieval-network \
    -itp "${PORT}:8080" \
    -e S3_BUCKET_NAME=test-bucket \
    -e DB_URI=postgresql://test:test@wearable-data-retrieval-test-db:5432/test \
    -e LOG_LEVEL=DEBUG \
    -e LOCAL=true \
    -e AWSROLE_ARN=$ROLE_ARN \
    -e AWS_ENDPOINT_URL=http://moto-proxy:5000 \
    -e AWS_DEFAULT_REGION=us-east-1 \
    -e AWS_ACCESS_KEY_ID=testing \
    -e AWS_SECRET_ACCESS_KEY=testing \
    wearable-data-retrieval:test

# Clean up
# rm -rf /tmp/.aws
docker stop moto-proxy || true
docker rm moto-proxy || true
docker stop wearable-data-retrieval-test-db || true
docker rm wearable-data-retrieval-test-db || true
docker network rm wearable-data-retrieval-network || true
