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

set -Eeuo pipefail

# Color codes for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Helper functions for colored output
print_header() {
    echo ""
    echo "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo "${RED}✗ $1${NC}"
}

print_info() {
    echo "${CYAN}ℹ $1${NC}"
}

print_step() {
    echo "→ $1"
}

# Function to run commands with progress indication
run_with_progress() {
    local message="$1"
    local command="$2"
    
    print_step "$message"
    if eval "$command" > /dev/null 2>&1; then
        print_success "$message completed"
        return 0
    else
        print_error "$message failed"
        return 1
    fi
}

require_cmd() { command -v "$1" >/dev/null 2>&1 || { print_error "Missing dependency: $1"; exit 1; }; }
require_cmd docker
require_cmd aws
require_cmd jq

# Flag to prevent double cleanup
CLEANUP_RUN=false

# Flag for cleanup on successful run
DOCKER_REACHED=false

cleanup() {
    if [ "$CLEANUP_RUN" = true ]; then
        return
    fi
    CLEANUP_RUN=true

    print_header "Cleanup"
    print_step "Stopping and removing containers..."
    docker stop moto-proxy db-bootstrapper-test-db 2>/dev/null || true
    docker rm -f moto-proxy db-bootstrapper-test-db 2>/dev/null || true
    docker network rm db-bootstrapper-network 2>/dev/null || true
    print_success "Cleanup completed"
    print_info "Test environment has been cleaned up"
}

cleanup_on_interrupt() {
    cleanup
    if [ "$DOCKER_REACHED" = true ]; then
        exit 0
    fi
}

# Set up traps for different scenarios
trap cleanup_on_interrupt INT TERM
trap cleanup EXIT

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

print_header "Database Bootstrapper Test Environment Setup"

# parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cache)
            NOCACHE=1
            shift
            ;;
        --data-file)
            [ -f "$2" ] || { print_error "Data file not found: $2"; exit 1; }
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
            print_error "Unknown option $1"
            exit 1
            ;;
    esac
done

print_info "Configuration: Port=$PORT, No Cache=$NOCACHE, Data File=$DATA_FILE"

# Build Docker image
print_header "Building Docker Image"
if [ $NOCACHE -eq 1 ]; then
    print_step "Building image without cache..."
    docker build \
        --platform linux/amd64 \
        --no-cache \
        -t db-bootstrapper:test \
        -f functions/db_bootstrapper/Dockerfile \
        .
else
    print_step "Building image with cache..."
    docker build \
        --platform linux/amd64 \
        -t db-bootstrapper:test \
        -f functions/db_bootstrapper/Dockerfile \
        .
fi

print_success "Docker image built successfully"

# Setup infrastructure
print_header "Setting Up Infrastructure"

# Create network if it doesn't exist
run_with_progress "Creating Docker network" "docker network create db-bootstrapper-network 2>/dev/null || true"

# Clean up existing containers silently
print_step "Cleaning up existing containers..."
docker stop moto-proxy db-bootstrapper-test-db db-bootstrapper-test 2>/dev/null || true
docker rm -f moto-proxy db-bootstrapper-test-db db-bootstrapper-test 2>/dev/null || true
print_success "Cleanup completed"

# Set up moto proxy
print_step "Starting Moto proxy (AWS mock service)..."
docker run -dp 5005:5000 \
    --name moto-proxy \
    --network db-bootstrapper-network \
    motoserver/moto:latest

print_step "Waiting for Moto to be ready..."
MOTO_READY=false
for i in {1..50}; do
  if aws s3api list-buckets >/dev/null 2>&1; then
    print_success "Moto is ready"
    MOTO_READY=true
    break
  fi
  sleep 0.2
done

if [ "$MOTO_READY" = false ]; then
    print_error "Moto failed to start"
    exit 1
fi

# Configure AWS environment
export AWS_ENDPOINT_URL=http://localhost:5005
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=testing
export AWS_SECRET_ACCESS_KEY=testing

# AWS Resources Setup
print_header "AWS Resources Setup"

# Upload dummy data to S3 if provided
DB_BOOTSTRAP_DATA_ARN=""
if [ -n "${DATA_FILE}" ]; then
    print_step "Setting up S3 data file..."
    # Create a dummy bucket
    aws s3api create-bucket --bucket test-bucket
    print_success "S3 bucket created"

    # Upload the data to the bucket
    aws s3 cp "${DATA_FILE}" s3://test-bucket/data.json
    DB_BOOTSTRAP_DATA_ARN="arn:aws:s3:::test-bucket/data.json"
    print_success "Data file uploaded to S3"
else
    print_info "No data file provided, skipping S3 setup"
fi

# Create Aurora PostgreSQL cluster and instance
print_step "Creating Aurora PostgreSQL cluster..."
aws rds create-db-cluster \
    --db-cluster-identifier test-aurora-cluster \
    --engine aurora-postgresql \
    --engine-version 16.6 \
    --database-name test \
    --master-username admin \
    --manage-master-user-password \
    --port 5432 \
    --enable-iam-database-authentication > /dev/null 2>&1
print_success "Aurora cluster created"

print_step "Creating Aurora PostgreSQL instance..."
aws rds create-db-instance \
    --db-instance-identifier test-aurora-instance \
    --db-cluster-identifier test-aurora-cluster \
    --engine aurora-postgresql \
    --db-instance-class db.serverless > /dev/null 2>&1
print_success "Aurora instance created"

# Get DB hostname
print_step "Retrieving database connection details..."
DB_HOST=$(aws rds describe-db-instances \
    --db-instance-identifier test-aurora-instance \
    --query "DBInstances[0].Endpoint.Address" \
    --output text 2>/dev/null)

# Get secret ARN
DB_SECRET_ARN=$(aws rds describe-db-clusters \
    --db-cluster-identifier test-aurora-cluster \
    --query "DBClusters[0].MasterUserSecret.SecretArn" \
    --output text 2>/dev/null)

# Get master username and password
SECRET_VALUE=$(aws secretsmanager get-secret-value \
    --secret-id "${DB_SECRET_ARN}" \
    --query "SecretString" \
    --output text 2>/dev/null)
DB_USERNAME=$(echo "${SECRET_VALUE}" | jq -r '.username')
DB_PASSWORD=$(echo "${SECRET_VALUE}" | jq -r '.password')
print_success "Database credentials retrieved"

# Database setup
print_header "Database Setup"

# Create a dummy database
print_step "Starting PostgreSQL container..."
docker run \
    --name db-bootstrapper-test-db \
    --network db-bootstrapper-network \
    -e POSTGRES_USER="${DB_USERNAME}" \
    -e POSTGRES_PASSWORD="${DB_PASSWORD}" \
    -e PGPASSWORD="${DB_PASSWORD}" \
    -e POSTGRES_DB=test \
    -d postgres:16
print_success "PostgreSQL container started"

# Wait for database to be ready
print_step "Waiting for database to be ready..."
DB_READY=false
for i in {1..50}; do
    if docker exec db-bootstrapper-test-db psql -U "${DB_USERNAME}" -d test -c "SELECT 1;" > /dev/null 2>&1; then
        print_success "Database is ready"
        DB_READY=true
        break
    fi
    sleep 0.2
done

if [ "$DB_READY" = false ]; then
    print_error "Database failed to start"
    exit 1
fi
echo ""

# Create dummy rds_iam role in database
print_step "Setting up IAM database authentication..."
docker exec db-bootstrapper-test-db psql -U "${DB_USERNAME}" -d test -c "CREATE ROLE rds_iam;"
print_success "IAM role created in database"

# Get the Postgres container's IP for host mapping
print_step "Configuring network mapping..."
DB_CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' db-bootstrapper-test-db)
print_success "Network mapping configured"

# Start the main application
print_header "Starting Application"
print_info "Application will be available at http://localhost:${PORT}"
print_info "Press Ctrl+C to stop the application and cleanup"

DOCKER_REACHED=true
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
