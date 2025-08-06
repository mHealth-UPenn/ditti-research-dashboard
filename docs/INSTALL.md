# Installation Guide

🚧 **Under Construction** 🚧

We are working hard at creating a straightforward process for installing and hosting your own version of the Ditti Research Dashboard. A future version will include a step-by-step installation for free, self-hosted options.

## Prerequisites

- **Ditti API Key (under construction):** A Ditti API key will be required to install the Ditti Research Dashboard.
- **ACM Certificate ARN:** Create an SSL certificate for a valid domain at the [Certificate Manager Dashboard](https://us-east-1.console.aws.amazon.com/acm/home).
- **AWS CloudFront Distribution:** Create an S3 bucket and CloudFront distribution configured for static website hosting at the [CloudFront Dashboard](https://us-east-1.console.aws.amazon.com/cloudfront/v4/home?region=us-east-1).
- **EC2 Key Pair:** Create and download an EC2 key pair from the [EC2 Dashboard](https://us-east-1.console.aws.amazon.com/ec2/home).

## Installation

### 1. Deploy your VPC

> See [VPC CloudFormation Template](#vpc-cloudformation-template) for more information.

It is highly recommended to run the Ditti Research Dashboard within a VPC. This repo includes a [VPC CloudFormation template](../cloudformation/vpc-template.yaml) to get started.

### 2. Whitelist your IP (optional)

> See [Whitelist Bastion IP Script](#whitelist-bastion-ip-script) for more information.

The provided [VPC CloudFormation template](../cloudformation/vpc-template.yaml) includes an NAT bastion instance and disables SSH access by default. You can use the [whitelist-bastion-ip.sh](../whitelist-bastion-ip.sh) script to enable SSH access from your IP address.

### 3. Deploy your Database

> See [RDS CloudFormation Template](#rds-cloudformation-template) for more information.

This repo includes an [RDS CloudFormation template](../cloudformation/rds-template.yaml) that sets up a minimal serverless Aurora for PostgreSQL instance on AWS.

### 4. Set Up Zappa

> See [Zappa Configuration](#zappa-configuration) for more information.

Rename the [zappa_settings.sample.json](../zappa_settings.sample.json) to `zappa_settings.json` and fill the template with your information.

### 5. Deploy the Flask Backend

> See [Staging & Deploy .env Files](#staging--deploy-env-files) and [Deployment Scripts](#deployment-scripts) for more information.

Create .env files for your staging or production builds (`secret-staging.env` or `secret-deploy.env`) and use the deploy scripts to set up the Flask backend.

### 6. Deploy the Vite Frontend

> See [Staging & Deploy .env Files](#staging--deploy-env-files) and [Deployment Scripts](#deployment-scripts) for more information.

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

### RDS CloudFormation Template

The RDS template creates an Aurora Serverless v2 PostgreSQL cluster with automatic scaling and backup capabilities.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `App` | `ditti-dashboard` | Application name |
| `Environment` | Required | Environment name (`staging` or `prod`) |
| `StackIdentifier` | Required | Unique identifier (e.g., `jdoe`) |
| `VpcStackName` | Required | Name of the VPC stack |
| `MasterUsername` | Required | Database master username |
| `IAMUsername` | Required | IAM database username |
| `PostgresVersion` | Required | PostgreSQL version (e.g., `16.6`) |
| `DatabaseName` | Required | Database name |
| `MinCapacity` | `0` | Minimum ACU (Aurora Capacity Units) |
| `MaxCapacity` | `2` | Maximum ACU |
| `SecondsUntilAutoPause` | `300` | Auto-pause delay in seconds |

**Outputs:**

| Output | Description |
|--------|-------------|
| `DBClusterEndpoint` | Aurora cluster endpoint |
| `DBClusterPort` | Aurora cluster port |
| `DBClusterIamUrl` | Aurora cluster IAM URL |
| `DBSecretARN` | ARN of the database credentials secret |
| `IAMUserARN` | ARN of the IAM user |

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

### Staging & Deploy .env Files

#### Backend Environment Variables (`secret-staging.env`)

| Variable | Description |
|----------|-------------|
| `AWS_ACCOUNT_ID` | Your AWS account ID |
| `AWS_REGION` | AWS region for deployment |
| `AWS_ECR_REPO_NAME` | An ECR repository name for the Flask backend's Docker image |
| `AWS_BUCKET` | S3 bucket for frontend assets |
| `AWS_CLOUDFRONT_DISTRIBUTION_ID` | Your CloudFront distribution ID |
| `AWS_CLOUDFRONT_DOMAIN_NAME` | Your CloudFront domain name |

#### Frontend Environment Variables (`.staging.env`)

| Variable | Description |
|----------|-------------|
| `VITE_FLASK_SERVER` | Backend API URL |
| `VITE_DEMO` | Demo mode flag |

### Deployment Scripts

#### Backend Deployment

The backend deployment automatically:

- Downloads and includes the AWS Parameters and Secrets Lambda Extension for improved performance
- Runs pytest tests (unless `--no-tests` is specified)
- Builds a Docker image for the Flask application using Zappa settings
- Pushes the image to ECR
- Deploys or updates the Flask application using Zappa
- Optionally deploys a secret rotator Lambda function that automatically rotates Flask secret keys
- Configures IAM policies and permissions for the secret rotator

| Option | Description |
|--------|-------------|
| `--no-tests` | Skip running tests before deployment |
| `--no-build` | Skip Docker build (use existing image) |
| `--no-cache` | Build Docker image without cache |
| `--no-rotator` | Skip secret rotator deployment |
| `-t, --tag` | Specify Docker image tag |

#### Frontend Deployment

The frontend deployment automatically:

- Builds the React application. The staging script includes source maps for debugging.
- Uploads assets to S3
- Creates a CloudFront invalidation
- Waits for invalidation to complete
