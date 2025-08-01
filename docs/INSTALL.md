# Installation Guide

🚧 **Under Construction** 🚧

We are working hard at creating a straightforward process for installing and hosting your own version of the Ditti Research Dashboard. A future version will include a step-by-step installation for free, self-hosted options.

Parts of this guide that will completed in future updates are marked with (🚧).

## Prerequisites

- **Ditti API Key (🚧):** A Ditti API key will be required to install the Ditti Research Dashboard.
- **ACM Certificate ARN:** Create an SSL certificate for a valid domain at the [Certificate Manager Dashboard](https://us-east-1.console.aws.amazon.com/acm/home).
- **AWS CloudFront Distribution (🚧):** Create an S3 bucket and CloudFront distribution configured for static website hosting at the [CloudFront Dashboard](https://us-east-1.console.aws.amazon.com/cloudfront/v4/home?region=us-east-1).
- **EC2 Key Pair:** Create and download an EC2 key pair from the [EC2 Dashboard](https://us-east-1.console.aws.amazon.com/ec2/home).

## Installation

### 1. Deploy your VPC

> See [VPC CloudFormation Template](#vpc-cloudformation-template) for more information.

It is highly recommended to run the Ditti Research Dashboard within a VPC. This repo includes a [VPC CloudFormation template](../cloudformation/vpc-template.yaml) to get started.

### 2. Whitelist your IP (optional)

> See [Whitelist Bastion IP Script](#whitelist-bastion-ip-script) for more information.

The provided [VPC CloudFormation template](../cloudformation/vpc-template.yaml) includes an NAT bastion instance and disables SSH access by default. You can use the [whitelist-bastion-ip.sh](../whitelist-bastion-ip.sh) script to enable SSH access from your IP address.

### 3. Deploy your IAM Resources

> See [IAM CloudFormation Template](#iam-cloudformation-template) for more information.

This repo includes an [IAM CloudFormation template](../cloudformation/iam-template.yml) with IAM resources that are required for deploying the RDS database and functions.

### 4. Deploy your Database

> See [RDS CloudFormation Template](#rds-cloudformation-template) for more information.

This repo includes an [RDS CloudFormation template](../cloudformation/rds-template.yaml) that sets up a minimal serverless Aurora for PostgreSQL instance on AWS.

### 5. Set Up Zappa

> See [Zappa Configuration](#zappa-configuration) for more information.

Rename the [zappa_settings.sample.json](../zappa_settings.sample.json) to `zappa_settings.json` and fill the template with your information.

### 6. Deploy the Flask Backend

> See [Staging & Deploy .env Files](#staging--deploy-env-files-) and [Deployment Scripts](#deployment-scripts-) for more information.

Create .env files for your staging or production builds (`secret-staging.env` or `secret-deploy.env`) and use the deploy scripts to set up the Flask backend.

### 7. Deploy Functions

> See [Functions CloudFormation Template](#functions-cloudformation-template) for more information.

A [Functions CloudFormation template](../cloudformation/functions-template.yml) is provided to automate the initial deployment of Lambda functions.

### 6. Deploy the Vite Frontend

> See [Staging & Deploy .env Files](#staging--deploy-env-files-) and [Deployment Scripts](#deployment-scripts-) for more information.

Create a `.staging.env` or `.production.env` file in the `frontend/` directory and use either of the React build scripts to set up the Vite frontend.

## Configuration

### VPC CloudFormation Template

The VPC template creates a secure network infrastructure with public and private subnets, NAT gateway, and security groups.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `App` | `ditti-dashboard` | Application name used for resource tagging |
| `VpcCIDR` | `10.0.0.0/16` | CIDR block for the VPC network |
| `BastionAMI` | Latest Amazon Linux 2023 | AMI ID for the bastion/NAT host |
| `BastionKeyName` | Required | Name of your EC2 key pair for SSH access |

**Outputs:**

| Output | Description |
|--------|-------------|
| `VpcId` | VPC ID |
| `PrivateSubnet1` | Private Subnet 1 |
| `PrivateSubnet2` | Private Subnet 2 |
| `PublicSubnet1` | Public Subnet 1 |
| `PublicSubnet2` | Public Subnet 2 |
| `RDSSecurityGroupId` | RDS Security Group ID |
| `LambdaSecurityGroupId` | Lambda Security Group ID |
| `NatBastionHostPublicIP` | Public IP of the NAT instance and bastion host |
| `NatInstanceSecurityGroupId` | NAT Instance and Bastion Security Group ID |

### IAM CloudFormation Template

The IAM template creates IAM roles for Lambda functions used by the application. These roles provide the necessary permissions for Lambda functions to access AWS services and resources.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `App` | `ditti-dashboard` | Application name |
| `Environment` | Required | Environment name (`staging` or `prod`) |

**Outputs:**

| Output | Description |
|--------|-------------|
| `DBBootStrapLambdaRoleArn` | ARN of the database bootstrap Lambda role |
| `DBBootStrapLambdaRoleName` | Name of the database bootstrap Lambda role |
| `FlaskSecretKeyRotatorLambdaRoleArn` | ARN of the Flask secret key rotator Lambda role |
| `FlaskSecretKeyRotatorLambdaRoleName` | Name of the Flask secret key rotator Lambda role |
| `WearableDataRetrievalLambdaRoleArn` | ARN of the wearable data retrieval Lambda role |
| `WearableDataRetrievalLambdaRoleName` | Name of the wearable data retrieval Lambda role |

### RDS CloudFormation Template

The RDS template creates an Aurora Serverless v2 PostgreSQL cluster with automatic scaling and backup capabilities.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `App` | `ditti-dashboard` | Application name |
| `Environment` | Required | Environment name (`staging` or `prod`) |
| `VpcStackName` | Required | Name of the VPC stack to import resources from |
| `IamStackName` | Required | Name of the IAM stack to import resources from |
| `MasterUsername` | Required | Master username for the DB cluster |
| `IAMUsername` | Required | IAM username for the DB cluster |
| `PostgresVersion` | Required | Version of PostgreSQL to use for the DB cluster |
| `DatabaseName` | Required | Name of the database to create |
| `MinCapacity` | `0` | Minimum ACU (Aurora Capacity Units) |
| `MaxCapacity` | `2` | Maximum ACU (Aurora Capacity Units) |
| `SecondsUntilAutoPause` | `300` | Seconds until the DB cluster will automatically pause |
| `BootStrapImageURI` | Required | URI of the DB bootstrap Lambda function image |
| `BootStrapDataARN` |  | S3 ARN of the DB bootstrap data Lambda function (optional) |
| `BootStrapApplicationLogLevel` | `INFO` | Log level for the DB bootstrap Lambda function (`TRACE`, `DEBUG`, `INFO`, `WARNING`, `ERROR`, `FATAL`) |
| `BootStrapSystemLogLevel` | `INFO` | Log level for the DB bootstrap Lambda function (`DEBUG`, `INFO`, `WARN`) |

**Outputs:**

| Output | Description |
|--------|-------------|
| `DBClusterEndpoint` | Aurora cluster endpoint |
| `DBClusterPort` | Aurora cluster port |
| `DBClusterIamUrl` | Aurora cluster IAM URL |
| `DBSecretARN` | ARN of the database credentials secret |
| `IAMUserARN` | ARN of the IAM user |

### Functions CloudFormation Template

The Functions template creates Lambda functions for wearable data retrieval and Flask secret key rotation, along with their associated IAM policies, triggers, and permissions.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `App` | `ditti-dashboard` | Application name |
| `Environment` | Required | Environment name (`staging` or `prod`) |
| `IAMStackName` | Required | Name of the IAM stack to import resources from |
| `VpcStackName` | Required | Name of the VPC stack to import resources from |
| `RDSStackName` | Required | Name of the RDS stack to import resources from |
| `AppInvocationURL` | Required | API Gateway invocation URL of the Zappa deployment |
| `AppFunctionName` | Required | Name of the Zappa deployment function |
| `FitbitSecretName` | Required | Name of the Fitbit secret (🚧) |
| `FitbitTokensSecretName` | Required | Name of the Fitbit tokens secret (🚧) |
| `WearableDataRetrievalImageURI` | Required | URI of the Wearable Data Retrieval image (🚧) |
| `WearableDataRetrievalLogsBucketName` | Required | Name of the Wearable Data Retrieval logs bucket (🚧) |
| `WearableDataRetrievalLogLevel` | `INFO` | Application log level for the Wearable Data Retrieval Lambda function (`TRACE`, `DEBUG`, `INFO`, `WARNING`, `ERROR`, `FATAL`) |
| `WearableDataRetrievalDailyTriggerSchedule` | `cron(0 0 * * ? *)` | Schedule expression for the Wearable Data Retrieval daily trigger |
| `FlaskSecretKeyRotatorImageURI` | Required | URI of the Flask Secret Key Rotator image (🚧) |
| `FlaskSecretKeyRotatorSecretName` | Required | Name of the Flask secret key secret (🚧) |
| `FlaskSecretKeyRotatorDays` | `14` | Number of days after which to rotate the Flask secret key |

**Outputs:**

| Output | Description |
|--------|-------------|
| `FlaskSecretKeyRotatorLambdaFunctionName` | Name of the Flask secret key rotator Lambda function |
| `FlaskSecretKeyRotatorImageUri` | URI of the Flask secret key rotator image |
| `WearableDataRetrievalLambdaFunctionName` | Name of the wearable data retrieval Lambda function |
| `WearableDataRetrievalImageUri` | URI of the wearable data retrieval image |

### Whitelist Bastion IP Script

The `whitelist-bastion-ip.sh` script manages SSH access to the bastion host by adding/removing IP addresses from NAT bastion the security group.

**Usage:**

```bash
./whitelist-bastion-ip.sh [nat-security-group-id] <action> <ip> [description]
```

| Action | Description | Example |
|--------|-------------|---------|
| `add` | Add an IP address to the whitelist | `./whitelist-bastion-ip.sh sg-1234567890abcdef0 add 203.0.113.1/32 "Office IP"` |
| `remove` | Remove an IP address from the whitelist | `./whitelist-bastion-ip.sh sg-1234567890abcdef0 remove 203.0.113.1/32` |
| `list` | List all whitelisted IP addresses | `./whitelist-bastion-ip.sh sg-1234567890abcdef0 list` |

### Zappa Configuration

The `zappa_settings.json` file configures the Flask application deployment to AWS Lambda via API Gateway.

| Placeholder | Description |
|-------------|-------------|
| `[stage]` | Deployment stage name |
| `[region]` | AWS region |
| `[db-uri]` | Database connection string. This is  output as the `DBClusterIamUrl` from the RDS CloudFormation template. |
| `[secret-name]` | AWS Secrets Manager secret name |
| `[secret-key-secret-name]` | Flask secret key secret name |
| `[log-level]` | Application log level |
| `[project-name]` | Project name for tagging |
| `[certificate-arn]` | Your ACM certificate ARN |
| `[domain]` | Your custom domain name |
| `[subnet-id-*]` | Private subnet ID |
| `[lambda-security-group-id]` | Lambda security group ID. This is output as the `LambdaSecurityGroupId` from the VPC CloudFormation template |
| `[rds-iam-user-arn]` | RDS IAM user ARN. This is output as the `IAMUserARN` from the RDS CloudFormation template |

### Staging & Deploy .env Files (🚧)

#### Backend Environment Variables (`secret-staging.env`)

| Variable | Description |
|----------|-------------|
| `AWS_ACCOUNT_ID` | Your AWS account ID |
| `AWS_REGION` | AWS region for deployment |
| `AWS_ECR_REPO_NAME` | An ECR repository name for the Flask backend's Docker image (🚧) |
| `AWS_BUCKET` | S3 bucket for frontend assets (🚧) |
| `AWS_CLOUDFRONT_DISTRIBUTION_ID` | Your CloudFront distribution ID (🚧) |
| `AWS_CLOUDFRONT_DOMAIN_NAME` | Your CloudFront domain name (🚧) |

#### Frontend Environment Variables (`.staging.env`)

| Variable | Description |
|----------|-------------|
| `VITE_FLASK_SERVER` | Backend API URL |
| `VITE_DEMO` | Demo mode flag |

### Deployment Scripts (🚧)

#### Backend Deployment

The `deploy-prod.sh` and `deploy-staging.sh` scripts provide flexible deployment options for different components of the application:

**Available Commands:**

- `--app`: Deploy or update the Zappa deployment (Flask application)
- `--wearable-data-retrieval`: Update the wearable data retrieval function code
- `--flask-secret-key-rotator`: Update the secret rotator function code
- `--no-cache`: Build Docker images with the `--no-cache` flag (optional)
- `--help`: Show the help message

**App Deployment Process:**

When using `--app`, the script:

- Downloads and includes the AWS Parameters and Secrets Lambda Extension for improved performance
- Builds a Docker image for the Flask application using Zappa settings
- Pushes the image to ECR
- Deploys or updates the Flask application using Zappa

**Function Updates:**

When updating function code (`--wearable-data-retrieval` or `--flask-secret-key-rotator`):

- Retrieves image URIs from CloudFormation stack outputs
- Builds and pushes updated Docker images to ECR
- Updates the Lambda function code using AWS CLI
- Waits for function updates to complete

**Usage Examples:**

```bash
# Deploy only the Flask application
./deploy-prod.sh --app

# Update only the wearable data retrieval function
./deploy-prod.sh --wearable-data-retrieval

# Deploy app and update both functions with no cache
./deploy-prod.sh --app --wearable-data-retrieval --flask-secret-key-rotator --no-cache
```

#### Frontend Deployment

The frontend deployment automatically:

- Builds the React application. The staging script includes source maps for debugging.
- Uploads assets to S3
- Creates a CloudFront invalidation
- Waits for invalidation to complete
