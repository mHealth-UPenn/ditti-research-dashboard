# Wearable Data Retrieval

The Wearable Data Retrieval function is an AWS Lambda service designed to automatically fetch and synchronize sleep data from wearable devices (primarily Fitbit) for research study participants. It provides a robust, scalable solution for collecting longitudinal sleep data from study subjects while maintaining data integrity and tracking synchronization status.

## Overview

### Key Features

- **Automated Data Synchronization**: Automatically retrieves sleep data from Fitbit API for eligible study participants
- **Intelligent Subject Filtering**: Identifies subjects requiring data synchronization based on consent status, enrollment dates, and last sync timestamps
- **Comprehensive Sleep Data Processing**: Handles sleep logs, sleep levels, and sleep summaries with detailed metrics
- **Robust Error Handling**: Implements comprehensive error handling with detailed logging and status tracking
- **Database Transaction Management**: Ensures data consistency through proper transaction handling and rollback mechanisms
- **IAM Database Authentication**: Supports both traditional and IAM-based database authentication for enhanced security
- **Execution Tracking**: Maintains detailed execution logs and status tracking in the database
- **S3 Log Archiving**: Automatically uploads execution logs to S3 for monitoring and debugging
- **Local Development Support**: Includes comprehensive local development environment with mock services

### Architecture

The function follows a layered architecture pattern with clear separation of concerns:

- **Lambda Handler Layer**: Entry point that orchestrates the entire data retrieval workflow
- **Configuration Layer**: Manages environment variables and AWS secrets for secure credential handling
- **Database Layer**: Provides connection management, transaction handling, and data persistence
- **Service Layer**: Implements business logic for study subject management and data processing
- **API Integration Layer**: Handles OAuth authentication and data retrieval from Fitbit API
- **Logging Layer**: Provides comprehensive logging and monitoring capabilities

### Use Cases

- **Research Study Data Collection**: Automatically collect sleep data from participants in longitudinal research studies
- **Data Synchronization**: Keep research databases synchronized with the latest wearable device data
- **Compliance Monitoring**: Track participant consent status and ensure data collection compliance
- **Sleep Research**: Support sleep science research by providing comprehensive sleep metrics and patterns
- **Health Monitoring**: Enable continuous health monitoring through wearable device integration
- **Clinical Trials**: Support clinical trials requiring sleep data collection and analysis

## Developing Locally

### Local Development Framework

The local development setup consists of two main scripts:

- **`run_image.sh`**: Sets up the complete local development environment
- **`test_image.sh`**: Sends test requests to the running function

### Environment Configuration

The function requires several environment variables for proper operation:

#### Required Environment Variables

The following environment variables are always required for the function to operate:

- **`DB_URI`**: Database connection string for PostgreSQL database
  - Format: `postgresql://username@hostname:port/database`
  - Used for connecting to the research database to manage study subjects and sleep data

- **`S3_BUCKET_NAME`**: Name of the S3 bucket for storing log files
  - Used to upload function execution logs for monitoring and debugging
  - Must be accessible by the Lambda function's IAM role

#### Non-Local Environment Variables

The following variables are required when running in non-local environments (AWS Lambda):

- **`FITBIT_TOKENS_SECRET_NAME`**: Name of the AWS Secrets Manager secret containing Fitbit OAuth tokens
  - Contains user-specific OAuth tokens for accessing Fitbit API data
  - Format: Dictionary mapping `ditti_id` to OAuth token dictionaries

- **`FITBIT_SECRET_NAME`**: Name of the AWS Secrets Manager secret containing Fitbit API credentials
  - Contains Fitbit API client ID and client secret
  - Used for OAuth authentication with Fitbit API

#### Optional Environment Variables

- **`DB_USE_IAM`**: Enable IAM database authentication (default: `"false"`)
  - Set to `"true"` to use AWS IAM authentication instead of password authentication
  - Requires proper IAM roles and policies for RDS access

- **`LOG_LEVEL`**: Logging level for the function (default: `"INFO"`)
  - Options: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`
  - Controls verbosity of function logging

#### Local Development Variables

- **`LOCAL`**: Enable local development mode (default: `"false"`)
  - Set to `"true"` to run in local development mode
  - When enabled, skips AWS Secrets Manager calls and uses mock Fitbit data
  - Allows development without AWS credentials or secrets

#### AWS Configuration Variables

- **`AWS_ENDPOINT_URL`**: AWS service endpoint URL (default: AWS default endpoints)
  - Set to `http://localhost:5005` for local development with moto proxy
  - Used to redirect AWS API calls to mock services during testing

- **`AWS_DEFAULT_REGION`**: AWS region for service calls (default: `us-east-1`)
  - Specifies the AWS region for API calls and resource creation

- **`AWS_ACCESS_KEY_ID`**: AWS access key for authentication
  - Set to `"testing"` for local development with mock services
  - Required for AWS API calls and service authentication

- **`AWS_SECRET_ACCESS_KEY`**: AWS secret key for authentication
  - Set to `"testing"` for local development with mock services
  - Required for AWS API calls and service authentication

#### Database Configuration Variables

- **`POSTGRES_USER`**: PostgreSQL database username (default: `test`)
  - Used for local development database setup

- **`POSTGRES_PASSWORD`**: PostgreSQL database password (default: `test`)
  - Used for local development database setup

- **`PGPASSWORD`**: PostgreSQL password environment variable (default: `test`)
  - Used by psql commands for database authentication

- **`POSTGRES_DB`**: PostgreSQL database name (default: `test`)
  - Used for local development database setup

#### Flask Configuration Variables

- **`TEST_FLASK_DB`**: Flask test database connection string
  - Format: `postgresql://username:password@hostname:port/database`
  - Used for database bootstrapping and testing operations

- **`FLASK_CONFIG`**: Flask configuration environment (default: `Testing`)
  - Sets the Flask application configuration for testing environment

### `run_image.sh`

The `run_image.sh` script provides a complete local development environment setup:

#### `run_image.sh` Features

- **Docker Image Building**: Builds the Lambda function Docker image with proper dependencies
- **Infrastructure Setup**: Creates Docker network and containers for testing
- **AWS Service Mocking**: Uses moto proxy to mock AWS services (S3, IAM, Secrets Manager)
- **Database Container**: Runs a PostgreSQL container for database testing
- **Environment Configuration**: Sets up all required environment variables for local development
- **Application Deployment**: Runs the function container with proper networking
- **Database Bootstrapping**: Initializes database schema and test data
- **Colored Output**: Provides clear, color-coded progress indicators

#### `run_image.sh` Usage

```bash
# Basic usage
./run_image.sh

# Build without cache
./run_image.sh --no-cache

# Specify custom port
./run_image.sh --port 9002

# Specify custom database port
./run_image.sh --db-port 5434

# Show help
./run_image.sh --help
```

#### What It Does

1. **Builds Docker Image**: Creates the Lambda function container image with proper platform targeting
2. **Sets Up Network**: Creates a Docker network for container communication
3. **Starts Moto Proxy**: Launches AWS service mocking container on port 5005
4. **Creates AWS Resources**: Sets up mock S3 buckets and IAM roles
5. **Starts Database**: Launches PostgreSQL container with test configuration
6. **Bootstraps Database**: Runs Flask migrations and initializes test data
7. **Configures Environment**: Sets all required environment variables for local development
8. **Runs Application**: Starts the function container with Lambda runtime interface
9. **Cleanup**: Automatically cleans up containers when stopped with Ctrl+C

### `test_image.sh`

The `test_image.sh` script sends test requests to the running function:

#### `test_image.sh` Features

- **Lambda Task Management**: Creates database entries for tracking function execution
- **Function Invocation**: Sends properly formatted Lambda invocation events
- **Configurable Ports**: Allows testing on different application and database ports
- **Real Lambda Runtime**: Uses the actual Lambda runtime interface for testing
- **Optional Function ID**: Can test with or without pre-created function IDs

#### `test_image.sh` Usage

```bash
# Test with auto-generated function ID (default)
./test_image.sh

# Test without creating function ID
./test_image.sh --no-id

# Test on custom port
./test_image.sh --port 9002

# Test with custom database port
./test_image.sh --db-port 5434

# Show help
./test_image.sh --help
```

#### Request Types

- **With Function ID**: Creates a new lambda task entry and invokes the function with the task ID
- **Without Function ID**: Invokes the function without a pre-created task entry (function creates its own)

### Local Development Workflow

1. **Start Environment**: Run `./run_image.sh` to set up the complete environment
2. **Test Function**: Use `./test_image.sh` to send test requests
3. **Monitor Logs**: Check container logs for debugging information
4. **Iterate**: Make code changes and rebuild as needed
5. **Cleanup**: Stop the environment with Ctrl+C (automatic cleanup)

## Source Code Structure

### Entry Point

- **`lambda_function.py`**: AWS Lambda entry point that processes wearable data retrieval requests and orchestrates the entire data retrieval workflow
- **`config.py`**: Configuration management module that loads environment variables and AWS secrets

### Core Components

#### Database Layer (`lambda_function.py`)

- **`DB`**: Database connection manager that handles IAM authentication and connection pooling
  - **`__init__(db_uri, use_iam=False, iam_sslmode="require")`**: Initializes SQLAlchemy engine with optional IAM authentication
  - **`create_auth_token(hostname, port, username)`**: Generates IAM authentication tokens for RDS connections
  - **`provide_token()`**: Event listener that injects IAM tokens into connection parameters
  - Supports both traditional password authentication and AWS IAM database authentication

- **`DBService`**: Base service class providing database connection context management
  - **`connect()`**: Context manager that provides transactional database connections
  - Ensures proper connection lifecycle management with automatic commit/rollback
  - Handles connection cleanup and error recovery
  - All database operations must be performed within the `connect()` context

- **`LambdaTaskService`**: Manages Lambda function execution tracking in the database
  - **`get_entry(entry_id)`**: Retrieves and loads a specific Lambda task entry by ID
  - **`create_entry()`**: Creates a new Lambda task entry with "InProgress" status
  - **`update_status(status, **kwargs)`**: Updates task status and optional metadata fields
  - Manages the `lambda_task` table with fields for tracking execution status, billing, timestamps, and error codes
  - Supports task statuses: "Pending", "InProgress", "Success", "Failed", "CompletedWithErrors"

- **`StudySubjectService`**: Handles study subject data retrieval and updates
  - **`get_entries()`**: Fetches study subjects requiring API synchronization with complex join logic
  - **`iter_entries()`**: Provides iterator for processing study subjects one at a time
  - **`insert_data(data)`**: Inserts sleep log, level, and summary data for the current study subject
  - **`update_last_sync_date()`**: Updates synchronization timestamp for API tracking
  - Manages multiple related tables: `study_subject`, `join_study_subject_api`, `join_study_subject_study`, `sleep_log`, `sleep_level`, `sleep_summary`
  - Implements sophisticated query logic to identify subjects needing data synchronization based on consent, expiration dates, and last sync timestamps

#### Data Models (`lambda_function.py`)

- **`LambdaTaskEntry`**: Data class representing Lambda function execution records
- **`StudySubjectEntry`**: Data class representing study subject information and enrollment details

#### Configuration Management (`config.py`)

- **`load_config()`**: Loads and validates environment configuration and AWS secrets
- **`Config`**: Typed configuration structure for database, Fitbit, and S3 settings
- **`FitbitConfig`**: Fitbit API configuration structure
- **`DBConfig`**: Database connection configuration structure
- **`S3Config`**: S3 bucket configuration structure

#### Utility Functions (`lambda_function.py`)

- **`build_url()`**: Constructs Fitbit API URLs for data retrieval
- **`handler()`**: Main Lambda handler function that orchestrates the entire workflow

### Flow Overview

1. **Event Reception**: Lambda function receives execution events with optional function_id
2. **Configuration Loading**: Environment variables and AWS secrets are loaded and validated
3. **Database Initialization**: Database connection is established with IAM authentication if enabled
4. **Task Tracking**: Lambda task entry is created or retrieved for execution tracking
5. **Study Subject Processing**: Study subjects are retrieved and processed for data synchronization
6. **API Data Retrieval**: Fitbit API data is fetched for each eligible study subject
7. **Data Storage**: Retrieved data is processed and stored in the database
8. **Status Updates**: Task status is updated throughout the process with error handling
9. **Logging**: Comprehensive logging is maintained for monitoring and debugging

## Deployment

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
  -t wearable-data-retrieval:latest \
  -f functions/wearable_data_retrieval/Dockerfile \
  .

# Tag the image for ECR
docker tag wearable-data-retrieval:latest \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/wearable-data-retrieval:latest
```

#### 2. Create an ECR Repository (if one does not exist)

```bash
# Create the ECR repository
aws ecr create-repository \
  --repository-name wearable-data-retrieval \
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
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/wearable-data-retrieval:latest
```

### CloudFormation Deployment

The Wearable Data Retrieval function is deployed using CloudFormation templates that create the necessary infrastructure components.

#### Required Parameters

The deployment requires the following parameters:

- **`WearableDataRetrievalImageURI`**: ECR URI of the built Docker image
- **`WearableDataRetrievalLogLevel`**: Application log level (INFO, DEBUG, etc.)
- **`WearableDataRetrievalS3Bucket`**: S3 bucket name for log file storage
- **`WearableDataRetrievalDBURI`**: Database connection URI
- **`WearableDataRetrievalDBUseIAM`**: Whether to use IAM database authentication
- **`WearableDataRetrievalFitbitTokensSecretName`**: AWS Secrets Manager secret name for Fitbit OAuth tokens
- **`WearableDataRetrievalFitbitSecretName`**: AWS Secrets Manager secret name for Fitbit API credentials

### Infrastructure Components

#### IAM Role (`cloudformation/iam-template.yml`)

The function uses a dedicated IAM role with the following permissions:

- **Lambda VPC Access**: Allows the function to access VPC resources
- **Secrets Manager Access**: Read access to Fitbit API credentials and OAuth tokens
- **RDS IAM Authentication**: Connect to database using IAM authentication (if enabled)
- **S3 Access**: Write access to S3 bucket for log file uploads
- **CloudWatch Logs**: Write access for function logging

#### Lambda Function Configuration

The function is configured with:

- **Architecture**: x86_64
- **Memory**: 512 MB (increased for API processing and data handling)
- **Timeout**: 900 seconds (15 minutes for API data retrieval)
- **VPC Configuration**: Deployed in private subnets with security groups
- **Environment Variables**: Database connection, S3 configuration, and Fitbit API settings

#### Environment Variables

The function receives the following environment variables from CloudFormation:

- **`DB_URI`**: Database connection string
- **`DB_USE_IAM`**: IAM database authentication flag
- **`S3_BUCKET_NAME`**: S3 bucket for log file storage
- **`FITBIT_TOKENS_SECRET_NAME`**: AWS Secrets Manager secret name for OAuth tokens
- **`FITBIT_SECRET_NAME`**: AWS Secrets Manager secret name for API credentials
- **`LOG_LEVEL`**: Application logging level
