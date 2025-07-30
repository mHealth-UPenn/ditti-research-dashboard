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
DATA_FILE=""

HELP_MESSAGE="
Usage: $0 [options]

Options:
    --no-cache: Build without cache (default: false)
    --data-file: Path to the data file to upload to S3 (default: "")
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
        --data-file)
            DATA_FILE=$2
            shift
            shift
            ;;
        --port)
            PORT=$2
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

# Set up moto proxy
docker run -dp 5005:5000 \
    --name moto-proxy \
    --network db-bootstrapper-network \
    motoserver/moto:latest

export AWS_ENDPOINT_URL=http://localhost:5005
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=testing
export AWS_SECRET_ACCESS_KEY=testing

# Upload dummy data to S3 if provided
DB_BOOTSTRAP_DATA_ARN=""
if [ -n "${DATA_FILE}" ]; then
    # Create a dummy bucket
    aws s3api create-bucket --bucket test-bucket

    # Upload the data to the bucket
    aws s3 cp "${DATA_FILE}" s3://test-bucket/data.json
    DB_BOOTSTRAP_DATA_ARN="arn:aws:s3:::test-bucket/data.json"
fi

# Create a dummy Aurora PostgreSQL cluster and instance
aws rds create-db-cluster \
    --db-cluster-identifier test-aurora-cluster \
    --engine aurora-postgresql \
    --engine-version 16.6 \
    --database-name test \
    --master-username admin \
    --manage-master-user-password \
    --port 5432 \
    --enable-iam-database-authentication > /dev/null

aws rds create-db-instance \
    --db-instance-identifier test-aurora-instance \
    --db-cluster-identifier test-aurora-cluster \
    --engine aurora-postgresql \
    --db-instance-class db.serverless > /dev/null

# Get DB hostname
DB_HOST=$(aws rds describe-db-instances \
    --db-instance-identifier test-aurora-instance \
    --query "DBInstances[0].Endpoint.Address" \
    --output text)

# Get secret ARN
DB_SECRET_ARN=$(aws rds describe-db-clusters \
    --db-cluster-identifier test-aurora-cluster \
    --query "DBClusters[0].MasterUserSecret.SecretArn" \
    --output text)

# Get master username and password
SECRET_VALUE=$(aws secretsmanager get-secret-value \
    --secret-id "${DB_SECRET_ARN}" \
    --query "SecretString" \
    --output text)
DB_USERNAME=$(echo "${SECRET_VALUE}" | jq -r '.username')
DB_PASSWORD=$(echo "${SECRET_VALUE}" | jq -r '.password')

# Create a dummy database
docker run \
    --name db-bootstrapper-test-db \
    --network db-bootstrapper-network \
    -e POSTGRES_USER="${DB_USERNAME}" \
    -e POSTGRES_PASSWORD="${DB_PASSWORD}" \
    -e PGPASSWORD="${DB_PASSWORD}" \
    -e POSTGRES_DB=test \
    -d postgres:16

# Wait for database to be ready
while ! docker exec db-bootstrapper-test-db psql -U "${DB_USERNAME}" -d test -c "SELECT 1;" > /dev/null 2>&1; do
    echo "Waiting for database to be ready..."
    sleep 1
done
echo "Database is ready"

# Create dummy rds_iam role in database
docker exec db-bootstrapper-test-db psql -U "${DB_USERNAME}" -d test -c "CREATE ROLE rds_iam;"

# Get the Postgres container's IP for host mapping
DB_CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' db-bootstrapper-test-db)

docker run --rm \
    --platform linux/amd64 \
    --name db-bootstrapper-test \
    --network db-bootstrapper-network \
    --add-host "${DB_HOST}:${DB_CONTAINER_IP}" \
    -p "${PORT}:8080" \
    -e AWS_ENDPOINT_URL="http://moto-proxy:5000" \
    -e AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION}" \
    -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
    -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
    -e DB_SECRET_ARN="${DB_SECRET_ARN}" \
    -e DB_HOST="${DB_HOST}" \
    -e DB_PORT="5432" \
    -e DB_USER="${DB_USERNAME}" \
    -e DB_NAME=test \
    -e DB_BOOTSTRAP_DATA_ARN="${DB_BOOTSTRAP_DATA_ARN}" \
    -e DB_IAM_USER=iam_user \
    -e LOCAL_DB=true \
    db-bootstrapper:test

# Clean up moto proxy
docker stop moto-proxy || true
docker stop db-bootstrapper-test-db || true
docker rm -f moto-proxy || true
docker rm -f db-bootstrapper-test-db || true
docker network rm db-bootstrapper-network || true
