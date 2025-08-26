# Flask Secret Key Rotator

The Flask Secret Key Rotator Lambda function serves as an AWS Secrets Manager rotation function that:

- **Automates Secret Rotation**: Automatically generates and rotates Flask secret keys on a configurable schedule
- **Ensures Application Security**: Maintains secure Flask applications by regularly updating secret keys
- **Integrates with AWS Secrets Manager**: Follows AWS Secrets Manager's standard 4-step rotation workflow
- **Validates Rotations**: Tests new secrets by calling application health check endpoints
- **Provides Zero-Downtime Updates**: Updates application Lambda functions to use new secrets without service interruption
- **Offers Comprehensive Logging**: Detailed logging for monitoring and troubleshooting rotation events

## Overview

### Key Features

- **Automatic Secret Generation**: Creates cryptographically secure Flask secret keys with configurable character exclusions
- **AWS Secrets Manager Integration**: Full integration with AWS Secrets Manager's rotation framework
- **Application Health Validation**: Tests new secrets by validating application health check endpoints
- **Lambda Function Updates**: Automatically updates application Lambda function configurations
- **VPC Integration**: Runs securely within private subnets with proper network isolation
- **Error Handling**: Robust error handling with detailed logging and rollback capabilities
- **Local Development Support**: Complete local testing environment with comprehensive test suite

### Architecture

The function follows AWS Secrets Manager's standard rotation workflow with clear separation of concerns:

- **Lambda Handler**: Entry point for AWS Secrets Manager rotation events
- **Rotation Step Functions**: Specialized functions for each rotation step (create, set, test, finish)
- **AWS Service Integration**: Direct integration with Secrets Manager, Lambda, and HTTP health checks
- **Environment Management**: Dynamic environment variable updates for application testing

### Use Cases

- **Flask Application Security**: Automatically rotate secret keys for Flask web applications
- **Compliance Requirements**: Meet security compliance requirements for regular secret rotation
- **Production Security**: Maintain secure production environments with automated key management
- **Infrastructure as Code**: Integrate secret rotation into CloudFormation deployments
- **Multi-Environment Support**: Deploy across development, staging, and production environments

## Developing Locally

### Local Development Framework

The secret rotator function is designed to run as an AWS Lambda function triggered by AWS Secrets Manager. For local development, you can:

1. **Run tests locally** - Use pytest to run the comprehensive test suite
2. **Test individual functions** - Import and test specific functions in isolation
3. **Mock AWS services** - Use the provided test fixtures to simulate AWS interactions

### Environment Configuration

The function requires several environment variables for proper operation:

#### Required Environment Variables

- **`APP_LAMBDA_FUNCTION_NAME`** - Name of the application Lambda function to update during rotation
- **`APP_URL`** - Base URL of the application for health check validation
- **`EXCLUDE_CHARACTERS`** - (Optional) Characters to exclude from generated secrets (default: `/@"'\\`)

## Source Code Structure

### Entry Point

The main entry point is `handler.py`, which contains the `lambda_handler` function that AWS Lambda invokes during the secret rotation process. This function orchestrates the entire rotation workflow by calling the appropriate step functions based on the rotation stage.

### Flow Overview

The secret rotation process follows AWS Secrets Manager's standard 4-step rotation workflow:

1. **createSecret** - Generates a new Flask secret key and stores it as `AWSPENDING`
2. **setSecret** - Updates the application Lambda function to use the pending secret for testing
3. **testSecret** - Validates the new secret by calling the application's health check endpoint
4. **finishSecret** - Promotes the pending secret to `AWSCURRENT` and cleans up

### Core Functions

- **`lambda_handler(event, _context)`** - Main entry point that routes to the appropriate rotation step
- **`create_secret(service_client, arn, token)`** - Generates a new Flask secret key with proper character exclusions
- **`set_secret()`** - Triggers Lambda function update to use the pending secret version
- **`test_secret(token)`** - Validates the new secret by checking the application's health endpoint
- **`finish_secret(service_client, arn, token)`** - Finalizes rotation by promoting the secret to current
- **`_wait_for_lambda_ready()`** - Utility function to wait for Lambda function updates to complete

## Testing

Tests can be found in [`test_secret_rotator.py`](../../tests/tests_functions/test_secret_rotator.py). The test suite uses pytest and follows a comprehensive approach to testing the AWS Secrets Manager rotation workflow. Tests are organized to cover each step of the rotation process and various error conditions.

### Key Fixtures

- **`mock_env(monkeypatch)`** - Sets up required environment variables (`APP_LAMBDA_FUNCTION_NAME`, `APP_URL`)
- **`mock_sm_client()`** - Provides a mocked AWS Secrets Manager client with default rotation-enabled metadata
- **`mock_lambda_client()`** - Provides a mocked AWS Lambda client with default function configuration

### Mocking Strategy

- **AWS Services**: Uses `unittest.mock.patch` to mock `boto3.client` calls
- **HTTP Requests**: Mocks `requests.get` for health check endpoint testing
- **Environment Variables**: Uses pytest's `monkeypatch` fixture for environment setup
- **Lambda Updates**: Mocks the `_wait_for_lambda_ready` helper to speed up tests

## Deployment

The Flask Secret Key Rotator Lambda function is deployed to AWS using CloudFormation templates and Docker container images stored in Amazon ECR. The deployment process involves building the Docker image, pushing it to ECR, and deploying the infrastructure using CloudFormation.

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
  -t flask-secret-key-rotator:latest \
  -f functions/secret_rotator/Dockerfile \
  .

# Tag the image for ECR
docker tag flask-secret-key-rotator:latest \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/flask-secret-key-rotator:latest
```

#### 2. Create an ECR Repository (if one does not exist)

```bash
# Create the ECR repository
aws ecr create-repository \
  --repository-name flask-secret-key-rotator \
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
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/flask-secret-key-rotator:latest
```

### CloudFormation Deployment

The Flask Secret Key Rotator function is deployed using the `cloudformation/functions-template.yml` template.

#### Required Parameters

The deployment requires the following parameters:

- **`FlaskSecretKeyRotatorImageURI`**: ECR URI of the built Docker image
- **`FlaskSecretKeyRotatorSecretName`**: Name of the Flask secret key secret in AWS Secrets Manager
- **`FlaskSecretKeyRotatorDays`**: Number of days after which to rotate the Flask secret key (default: 14)
- **`AppFunctionName`**: Name of the Flask application Lambda function
- **`AppInvocationURL`**: URL of the Flask application for health check validation

### Infrastructure Components

#### IAM Role (`cloudformation/iam-template.yml`)

The function uses a dedicated IAM role with the following permissions:

- **Lambda VPC Access**: Allows the function to access VPC resources
- **Secrets Manager Access**: Full access to the Flask secret key secret (describe, get, put, update version stage)
- **Random Password Generation**: Access to generate new secret values
- **Lambda Function Management**: Update and read configuration of the application Lambda function

#### Lambda Function Configuration

The function is configured with:

- **Architecture**: x86_64
- **Memory**: 512 MB
- **Timeout**: 180 seconds
- **VPC Configuration**: Deployed in private subnets with security groups
- **Environment Variables**: Application function name and URL for health checks

#### Environment Variables

The function receives the following environment variables from CloudFormation:

- **`APP_LAMBDA_FUNCTION_NAME`**: Name of the Flask application Lambda function to update
- **`APP_URL`**: Base URL of the Flask application for health check validation

#### Rotation Schedule

The function is automatically triggered by AWS Secrets Manager based on the configured rotation schedule:

- **Automatic Rotation**: Configured via `FlaskSecretKeyRotatorDays` parameter
- **Rotation Lambda Permission**: Allows Secrets Manager to invoke the function
- **Rotation Schedule**: Managed by AWS Secrets Manager's `RotationSchedule` resource
