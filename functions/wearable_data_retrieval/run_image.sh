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

print_header "Wearable Data Retrieval Test Environment Setup"

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
            print_error "Unknown option $1"
            exit 1
            ;;
    esac
done

print_info "Configuration: Port=$PORT, DB Port=$DB_PORT, No Cache=$NOCACHE"

# Build Docker image
print_header "Building Docker Image"
if [ $NOCACHE -eq 1 ]; then
    print_step "Building image without cache..."
    docker build \
        -t wearable-data-retrieval:test \
        --platform linux/amd64 \
        --secret id=aws,src=$HOME/.aws/credentials \
        --target prod \
        --no-cache \
        -f functions/wearable_data_retrieval/Dockerfile .
else
    print_step "Building image with cache..."
    docker build \
        -t wearable-data-retrieval:test \
        --platform linux/amd64 \
        --secret id=aws,src=$HOME/.aws/credentials \
        --target prod \
        -f functions/wearable_data_retrieval/Dockerfile .
fi

if [ $? -ne 0 ]; then
    print_error "Failed to build the image"
    exit 1
fi
print_success "Docker image built successfully"

# Setup infrastructure
print_header "Setting Up Infrastructure"

# Create network if it doesn't exist
run_with_progress "Creating Docker network" "docker network create wearable-data-retrieval-network 2>/dev/null || true"

# Clean up existing containers silently
print_step "Cleaning up existing containers..."
docker stop moto-proxy wearable-data-retrieval-test-db wearable-data-retrieval-test 2>/dev/null || true
docker rm -f moto-proxy wearable-data-retrieval-test-db wearable-data-retrieval-test 2>/dev/null || true
print_success "Cleanup completed"

# Set up moto proxy
print_step "Starting Moto proxy (AWS mock service)..."
docker run -dp 5005:5000 \
    --name moto-proxy \
    --network wearable-data-retrieval-network \
    motoserver/moto:latest
print_success "Moto proxy started"

# Configure AWS environment
export AWS_ENDPOINT_URL=http://localhost:5005
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=testing
export AWS_SECRET_ACCESS_KEY=testing

# Create AWS resources
print_step "Creating AWS test resources..."
aws s3api create-bucket --bucket test-bucket
print_success "S3 bucket created"

# Database setup
print_header "Database Setup"

# Create a dummy postgres container
print_step "Starting PostgreSQL container..."
docker run \
    --name wearable-data-retrieval-test-db \
    --network wearable-data-retrieval-network \
    -p "${DB_PORT}:5432" \
    -e POSTGRES_USER=test \
    -e POSTGRES_PASSWORD=test \
    -e PGPASSWORD=test \
    -e POSTGRES_DB=test \
    -d postgres:16
print_success "PostgreSQL container started"

# Wait for database to be ready
print_step "Waiting for database to be ready..."
while ! docker exec wearable-data-retrieval-test-db psql -U test -d test -c "SELECT 1;" > /dev/null 2>&1; do
    sleep 1
done
echo ""
print_success "Database is ready"

# Bootstrap the database
print_step "Bootstrapping database..."
export TEST_FLASK_DB="postgresql://test:test@localhost:${DB_PORT}/test"
export FLASK_CONFIG="Testing"
flask --app run.py db upgrade
flask --app run.py init-integration-testing-db
print_success "Database bootstrapped"

# Start the main application
print_header "Starting Application"
print_info "Application will be available at http://localhost:${PORT}"
print_info "Press Ctrl+C to stop the application and cleanup"

docker run --rm \
    --name wearable-data-retrieval-test \
    --platform linux/amd64 \
    --network wearable-data-retrieval-network \
    -itp "${PORT}:8080" \
    -e S3_BUCKET_NAME=test-bucket \
    -e DB_URI=postgresql://test:test@wearable-data-retrieval-test-db:5432/test \
    -e LOG_LEVEL=DEBUG \
    -e LOCAL=true \
    -e AWS_ENDPOINT_URL=http://moto-proxy:5000 \
    -e AWS_DEFAULT_REGION=us-east-1 \
    -e AWS_ACCESS_KEY_ID=testing \
    -e AWS_SECRET_ACCESS_KEY=testing \
    wearable-data-retrieval:test

# Clean up
print_header "Cleanup"
print_step "Stopping and removing containers..."
docker stop moto-proxy wearable-data-retrieval-test-db 2>/dev/null || true
docker rm moto-proxy wearable-data-retrieval-test-db 2>/dev/null || true
docker network rm wearable-data-retrieval-network 2>/dev/null || true
print_success "Cleanup completed"
print_info "Test environment has been cleaned up"
