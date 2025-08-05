# DB Bootstrapper

The DB Bootstrapper Lambda function serves as a CloudFormation custom resource that:

- **Automates Database Setup**: Initializes newly created Aurora PostgreSQL clusters with schema migrations and initial data
- **Ensures Security**: Uses IAM authentication and AWS Secrets Manager for secure database access
- **Supports Data Loading**: Optionally loads bootstrap data from S3 to populate the database
- **Integrates with CloudFormation**: Responds to Create, Update, and Delete events from CloudFormation stacks
- **Provides Comprehensive Logging**: Detailed logging for monitoring and troubleshooting

## Overview

### Key Features

- **Schema Migration Management**: Uses Flask-Migrate to handle database schema changes
- **IAM Database Authentication**: Secure database connections using AWS IAM roles
- **S3 Data Integration**: Loads initial data from S3 buckets for database population
- **VPC Integration**: Runs securely within private subnets with proper network isolation
- **Error Handling**: Robust error handling with detailed CloudFormation responses
- **Local Development Support**: Complete local testing environment with Docker containers

### Architecture

The function follows a modular architecture with clear separation of concerns:

- **Lambda Handler**: Entry point for CloudFormation events
- **Agent Class**: Orchestrates the bootstrapping process
- **Utility Modules**: Specialized components for database, S3, and secrets management
- **Flask Integration**: Leverages Flask for database operations and migrations

### Use Cases

- **Initial Database Setup**: Automatically configure new Aurora PostgreSQL clusters
- **Environment Provisioning**: Set up development, staging, and production databases
- **Data Migration**: Load initial data sets during database creation
- **Infrastructure as Code**: Integrate database initialization into CloudFormation deployments

## Developing Locally

The DB Bootstrapper Lambda function includes a comprehensive local development framework that allows developers to test the function in an environment that closely mirrors production. The framework uses Docker containers to simulate AWS services and provides a complete testing environment.

### Local Development Framework

The local development setup consists of two main scripts:

- **`run_image.sh`**: Sets up the complete local development environment
- **`test_image.sh`**: Sends test requests to the running function

### Environment Configuration

The function requires several environment variables for proper operation:

#### Required Environment Variables

- **`DB_SECRET_ARN`**: ARN of the AWS Secrets Manager secret containing database credentials
- **`DB_USER`**: Database username for master user authentication
- **`DB_HOST`**: Database hostname or endpoint
- **`DB_PORT`**: Database port (typically 5432 for PostgreSQL)
- **`DB_NAME`**: Database name
- **`DB_IAM_USER`**: IAM username for database authentication
- **`DB_BOOTSTRAP_DATA_ARN`**: S3 ARN for bootstrap data file (optional)

#### Local Development Variables

- **`LOCAL_DB`**: Set to "true" to disable IAM authentication for local testing
- **`AWS_ENDPOINT_URL`**: Endpoint URL for AWS services (set to moto proxy for local testing)
- **`AWS_DEFAULT_REGION`**: AWS region (defaults to us-east-1)
- **`AWS_ACCESS_KEY_ID`**: AWS access key (set to "testing" for local testing)
- **`AWS_SECRET_ACCESS_KEY`**: AWS secret key (set to "testing" for local testing)

### `run_image.sh`

The `run_image.sh` script provides a complete local development environment setup:

#### `run_image.sh` Features

- **Docker Image Building**: Builds the Lambda function Docker image with proper dependencies
- **Infrastructure Setup**: Creates Docker network and containers for testing
- **AWS Service Mocking**: Uses moto proxy to mock AWS services (S3, RDS, Secrets Manager)
- **Database Container**: Runs a PostgreSQL container for database testing
- **Environment Configuration**: Sets up all required environment variables
- **Application Deployment**: Runs the function container with proper networking

#### `run_image.sh` Usage

```bash
# Basic usage
./run_image.sh

# Build without cache
./run_image.sh --no-cache

# Specify custom port
./run_image.sh --port 9002

# Include bootstrap data file
./run_image.sh --data-file /path/to/data.json

# Show help
./run_image.sh --help
```

#### What It Does

1. **Builds Docker Image**: Creates the Lambda function container image
2. **Sets Up Network**: Creates a Docker network for container communication
3. **Starts Moto Proxy**: Launches AWS service mocking container
4. **Creates AWS Resources**: Sets up mock S3 buckets, RDS clusters, and secrets
5. **Starts Database**: Launches PostgreSQL container with proper configuration
6. **Configures Environment**: Sets all required environment variables
7. **Runs Application**: Starts the function container with proper networking
8. **Cleanup**: Automatically cleans up containers when stopped

### `test_image.sh`

The `test_image.sh` script sends test requests to the running function:

#### `test_image.sh` Features

- **CloudFormation Event Simulation**: Sends properly formatted CloudFormation events
- **Multiple Request Types**: Supports Create, Update, and Delete operations
- **Configurable Port**: Allows testing on different ports
- **Real Lambda Invocation**: Uses the actual Lambda runtime interface

#### `test_image.sh` Usage

```bash
# Test Create operation (default)
./test_image.sh

# Test Update operation
./test_image.sh --request-type Update

# Test Delete operation
./test_image.sh --request-type Delete

# Test on custom port
./test_image.sh --port 9002 --request-type Create
```

#### Request Types

- **Create**: Initializes database schema and loads bootstrap data
- **Update**: Updates existing database configuration
- **Delete**: Cleans up database resources (typically no-op for safety)

### Local Development Workflow

1. **Start Environment**: Run `./run_image.sh` to set up the complete environment
2. **Test Function**: Use `./test_image.sh` to send test requests
3. **Monitor Logs**: Check container logs for debugging information
4. **Iterate**: Make code changes and rebuild as needed
5. **Cleanup**: Stop the environment with Ctrl+C (automatic cleanup)

## Source Code Structure

### Entry Point

- **`lambda_handler.py`**: AWS Lambda entry point that receives CloudFormation events and delegates to the main agent
- **`db_bootstrapper_agent.py`**: Core agent class that orchestrates all database bootstrapping operations

### Core Components (`src/utils/`)

- **`app_factory.py`**: Creates Flask applications with database configurations
- **`database_manager.py`**: Manages database operations and schema migrations
- **`database_session_manager.py`**: Handles database session lifecycle
- **`database_connection_executer.py`**: Executes database connection operations
- **`db_uri.py`**: Constructs database connection URIs
- **`data_loader.py`**: Loads and processes bootstrap data from S3
- **`data_processor.py`**: Processes and validates data before database insertion
- **`secret_manager.py`**: Retrieves database credentials from AWS Secrets Manager
- **`s3_file_manager.py`**: Manages S3 file operations for bootstrap data
- **`file_reader.py`**: Reads and parses data files
- **`sequence_manager.py`**: Manages database sequences and auto-incrementing IDs
- **`messages.py`**: Contains message templates and logging utilities

### Backend Integration (`src/backend/`)

- **`extensions.py`**: Flask extensions and configurations for database integration

### Flow Overview

1. **Event Reception**: CloudFormation events trigger the Lambda handler
2. **Environment Validation**: Agent validates required environment variables
3. **Secret Retrieval**: Database credentials are fetched from AWS Secrets Manager
4. **App Creation**: Flask applications are created with appropriate database configurations
5. **Data Loading**: Bootstrap data is retrieved from S3 and processed
6. **Database Operations**: Schema migrations and data insertion are performed
7. **Response**: Success/failure responses are sent back to CloudFormation

## Testing

The DB Bootstrapper Lambda function includes a comprehensive test suite designed to ensure reliability and maintainability. The testing framework uses pytest with extensive mocking and integration testing capabilities.

### Test Structure

#### Core Test Files

- **`test_db_bootstrapper_agent.py`**: Comprehensive unit and integration tests for the main agent class
- **`test_lambda_handler.py`**: Tests for the AWS Lambda entry point function
- **`conftest.py`**: Shared pytest fixtures and test configuration

#### Utility Tests (`tests_utils/`)

- **`test_app_factory.py`**: Tests for Flask application factory
- **`test_database_manager.py`**: Database management operations testing
- **`test_database_session_manager.py`**: Session lifecycle management tests
- **`test_database_connection_executer.py`**: Database connection execution tests
- **`test_db_uri.py`**: Database URI construction and validation tests
- **`test_data_loader.py`**: Data loading and processing tests
- **`test_data_processor.py`**: Data validation and processing tests
- **`test_secret_manager.py`**: AWS Secrets Manager integration tests
- **`test_s3_file_manager.py`**: S3 file operations testing
- **`test_file_reader.py`**: File reading and parsing tests
- **`test_sequence_manager.py`**: Database sequence management tests

### Key Fixtures

- **`mock_postgres_container`**: Provides a real PostgreSQL database for integration tests
- **`test_client`**: Flask test client with database configuration
- **`with_mock_tables`**: Creates test database tables
- **`with_mock_data`**: Loads test data into database
- **`with_mock_secret`**: Mocks AWS Secrets Manager responses
- **`with_mock_bucket`**: Mocks S3 bucket operations

### Mocking Strategy

#### PostgreSQL Container (`MockPostgresContainer`)

The `MockPostgresContainer` class provides a real PostgreSQL database for integration testing:

- **Real Database**: Uses actual PostgreSQL Docker container for authentic database operations
- **Automatic Setup**: Handles container lifecycle, connection waiting, and cleanup
- **IAM Role Simulation**: Creates dummy `rds_iam` role for IAM authentication testing
- **Session Scoped**: Container persists across all tests in a session for efficiency

#### AWS Service Mocks (`mock_aws`)

AWS services are mocked using the Moto library for controlled testing:

- **Secrets Manager**: Simulates database credential retrieval
- **S3**: Mocks bootstrap data file operations
- **RDS**: Provides database cluster information
- **IAM**: Simulates authentication and authorization

#### Database Connection Mocks (`MockConnection`, `MockResult`)

Custom database connection mocks provide controlled testing scenarios:

- **Connection State**: Simulates different connection states (user exists/doesn't exist)
- **Query Responses**: Returns predefined responses for specific SQL queries
- **Transaction Control**: Mocks commit and close operations
- **Call Tracking**: Records executed statements for verification

#### Flask Application Mocks (`test_client`)

Flask application mocking provides database integration testing:

- **Real Database URI**: Uses actual PostgreSQL container connection
- **Flask Extensions**: Initializes SQLAlchemy and Flask-Migrate
- **App Context**: Provides proper Flask application context
- **Session Management**: Handles database session lifecycle

#### Mock Data Structure (`mock_data.json`)

Test data is structured to simulate real database scenarios:

```json
{
  "mock_table": [
    {
      "id": 1,
      "name": "Test Table",
      "description": "This is a test table"
    }
  ],
  "alembic_version": [{ "version_num": "123" }]
}
```

#### Database Table Models (`MockTable`, `MockEmptyTable`)

SQLAlchemy models provide structure for test data:

```python
class MockTable(db.Model):
    __tablename__ = MOCK_TABLE_NAME
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=True)
```

## Deployment

The DB Bootstrapper Lambda function is deployed to AWS using CloudFormation templates and Docker container images stored in Amazon ECR. The deployment process involves building the Docker image, pushing it to ECR, and deploying the infrastructure using CloudFormation.

### Prerequisites

Before deploying, ensure you have:

- AWS CLI configured with appropriate permissions
- Docker installed and running
- AWS ECR repository created
- CloudFormation templates available

### Building and Pushing Docker Image

#### 1. Build the Docker Image

```bash
# Build the image for AWS Lambda (x86_64 architecture)
docker build \
  --platform linux/amd64 \
  -t db-bootstrapper:latest \
  -f functions/db_bootstrapper/Dockerfile \
  .

# Tag the image for ECR
docker tag db-bootstrapper:latest \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/db-bootstrapper:latest
```

#### 2. Create an ECR Repository (if one does not exist)

```bash
# Create the ECR repository
aws ecr create-repository \
  --repository-name db-bootstrapper \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=AES256

# Get login token and authenticate Docker
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
```

#### 3. Push the Image to ECR

```bash
# Push the image to ECR
docker push \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/db-bootstrapper:latest
```

### CloudFormation Deployment

The DB Bootstrapper function is deployed as part of the RDS stack using the `cloudformation/rds-template.yml` template.

#### Required Parameters

The deployment requires the following parameters:

- **`BootStrapImageURI`**: ECR URI of the built Docker image
- **`BootStrapDataARN`**: S3 ARN of bootstrap data file (optional)
- **`BootStrapApplicationLogLevel`**: Application log level (INFO, DEBUG, etc.)
- **`BootStrapSystemLogLevel`**: System log level (INFO, DEBUG, etc.)

### Infrastructure Components

#### IAM Role (`cloudformation/iam-template.yml`)

The function uses a dedicated IAM role with the following permissions:

- **Lambda VPC Access**: Allows the function to access VPC resources
- **Secrets Manager Access**: Read access to database credentials
- **RDS IAM Authentication**: Connect to database using IAM authentication
- **S3 Access**: Read access to bootstrap data files (if provided)

#### Lambda Function Configuration

The function is configured with:

- **Architecture**: x86_64
- **Memory**: 128 MB
- **Timeout**: 180 seconds
- **VPC Configuration**: Deployed in private subnets with security groups
- **Environment Variables**: Database connection details and configuration

#### Environment Variables

The function receives the following environment variables from CloudFormation:

- **`DB_HOST`**: Aurora cluster endpoint
- **`DB_PORT`**: Database port (typically 5432)
- **`DB_USER`**: Master database username
- **`DB_NAME`**: Database name
- **`DB_SECRET_ARN`**: ARN of the database credentials secret
- **`DB_IAM_USER`**: IAM username for database authentication
- **`DB_BOOTSTRAP_DATA_ARN`**: S3 ARN for bootstrap data (optional)
