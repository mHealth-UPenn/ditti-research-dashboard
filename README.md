# Ditti Research Dashboard

The **Ditti Research Dashboard** was created to provide a single, centralized platform for managing and visualizing data collected from the **Penn Ditti Mobile App**. With this dashboard, research coordinators and clinicians can efficiently enroll new subjects and monitor adherence to behavioral sleep interventions.

**🏥 Dashboard for Research and Clinical Data Management:**

The Ditti Research Dashboard allows researchers and clinicians to manage and visualize **anonymized study data** from the Penn Ditti app, supporting the monitoring of behavioral sleep intervention adherence.

**🔑 Comprehensive Role and Permission Control:**

The **Admin Dashboard** provides **granular role-based access controls**, enabling coordinators to manage **study-specific** and **app-wide permissions**.

**☁️ Scalable & HIPAA-compliant Cloud Infrastructure:**

Built on **AWS** with **TypeScript, React.js, and Python**, the dashboard integrates user data from **DynamoDB** and is expanding to include a **Fitbit Dashboard** for visualizing participant sleep data.

## Key Features

- 📊 **Visualizations** of user interactions with the **Penn Ditti Mobile App**
- 📝 **Interfaces** for managing study-related data and enrolling study subjects
- 🎙️ **Tools** for labeling and uploading **audio files** for the Penn Ditti Mobile App
- 🔧 **Administrative controls** for managing app-level and study-level permissions
- ☁️ **Serverless architecture** to optimize cost-efficiency
- 🔗 **Integrations** with third-party wearable device APIs
- 🖼️ **Side-by-side visualizations** of wearable and Penn Ditti data

## Tech Stack & Infrastructure

**Backend:**

- Python
- Flask Web Framework
- Zappa
- PostgreSQL

**Frontend:**

- TypeScript
- React.js
- Tailwind CSS
- Visx

**AWS Services:**

- Lambda
- Cognito
- AppSync
- DynamoDB
- S3
- CloudFront
- Secrets Manager
- Relational Database Service (RDS)

🚀 *The Ditti Research Dashboard is evolving to support deeper insights into behavioral sleep interventions and participant engagement.*

## Running Locally

### Prerequisites

- Docker
- Python
- WSL, Linux, or MacOS

### Setup

Clone the repository:

```bash
git clone https://github.com/yourusername/aws-portal.git
cd aws-portal
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Run the deploy script:

```bash
./deploy-dev.sh init no-aws
```

Run the development server:

```bash
flask run
```

In a new terminal window, run the frontend:

```bash
cd aws_portal/frontend
npm install
npm run start
```

## Running Tests

To run the test suite, use the following command:

```bash
pytest
```

## Backend Deployment Scripts

The repository includes several deployment scripts to facilitate the deployment process for different environments.

### Development Deployment

The `deploy-dev.sh` script sets up the development environment. It handles the creation of a Python virtual environment, installs required Python packages, exports environment variables, and optionally initializes the application.

```bash
./deploy-dev.sh [conda] [init] [no-aws]
```

- `conda`: Skip Python virtual environment setup if using Conda.
- `init`: Run initialization commands for the application.
- `no-aws`: Skip fetching secrets from AWS Secrets Manager.

### Staging Deployment

The `deploy-staging.sh` script is used for deploying to the staging environment. It supports options to skip tests, skip building the Docker image, and use the Docker cache.

```bash
./deploy-staging.sh [--no-tests] [--no-build] [--no-cache] [-t|--tag <tag>]
```

- `--no-tests`: Skip running tests.
- `--no-build`: Skip building the Docker image.
- `--no-cache`: Build the Docker image without using the cache.
- `-t|--tag <tag>`: Specify the Docker image tag (default is `latest`).

### Production Deployment

The `deploy-prod.sh` script is used for deploying to the production environment. It supports the same options as the staging deployment script.

```bash
./deploy-prod.sh [--no-tests] [--no-build] [--no-cache] [-t|--tag <tag>]
```

- `--no-tests`: Skip running tests.
- `--no-build`: Skip building the Docker image.
- `--no-cache`: Build the Docker image without using the cache.
- `-t|--tag <tag>`: Specify the Docker image tag (default is `latest`).

These scripts ensure a smooth and consistent deployment process across different environments.

**Note:** In production and staging environments, `run.py` retrieves secrets from AWS Secrets Manager and sets them as environment variables before creating the Flask app instance.

**Note:** In production, Zappa automatically wraps the app object in production-ready WSGI middleware.

## Frontend Deployment Scripts

### Production Build

The `react-build-prod.sh` script is used for building and deploying the React frontend to the production environment. It exports deployment environment variables, builds the React app, uploads the built app to the specified AWS S3 bucket, and creates a CloudFront invalidation to update the app's frontend.

```bash
./react-build-prod.sh
```

### Staging Build

The `react-build-staging.sh` script is used for building and deploying the React frontend to the staging environment. It follows the same steps as the production build script.

```bash
./react-build-staging.sh
```

## Environment Configuration

Refer to the following `.env.template` files for configuring environment variables:

### .env.aws.template

For configuring AWS services when running locally.

| Variable Name               | Description                              |
|-----------------------------|------------------------------------------|
| APP_SYNC_HOST               | AppSync host URL.                         |
| APPSYNC_ACCESS_KEY          | AppSync access key.                       |
| APPSYNC_SECRET_KEY          | AppSync secret key.                       |
| AWS_TABLENAME_USER          | DynamoDB table name for users.            |
| AWS_TABLENAME_TAP           | DynamoDB table name for taps.             |
| AWS_TABLENAME_AUDIO_FILE    | DynamoDB table name for audio files.      |
| AWS_TABLENAME_AUDIO_TAP     | DynamoDB table name for audio taps.       |
| AWS_AUDIO_FILE_BUCKET       | S3 bucket for audio files.                |
| COGNITO_PARTICIPANT_CLIENT_ID | Cognito participant client ID.          |
| COGNITO_PARTICIPANT_CLIENT_SECRET | Cognito participant client secret.  |
| COGNITO_PARTICIPANT_DOMAIN  | Cognito participant domain.               |
| COGNITO_PARTICIPANT_REGION  | Cognito participant region.               |
| COGNITO_PARTICIPANT_USER_POOL_ID | Cognito participant user pool ID.    |
| TM_FSTRING                  | Token manager configuration string. This expects to be a format string that takes one argument `api_name`. For example, `{api_name}-tokens-dev`.      |

### .env.deploy.template

For use when deploying to staging or production environments. To use, make two copies of this file: `.env.prod` and `.env.staging`.

| Variable Name                   | Description                              |
|---------------------------------|------------------------------------------|
| AWS_REGION                      | AWS region.                               |
| AWS_ACCOUNT_ID                  | The AWS account ID of the account that owns all AWS resources.                           |
| AWS_BUCKET                      | The S3 bucket to use for static web hosting.                                |
| AWS_CLOUDFRONT_DISTRIBUTION_ID  | CloudFront distribution ID.               |
| AWS_CLOUDFRONT_DOMAIN_NAME      | CloudFront domain name.                   |
| AWS_ECR_REPO_NAME               | ECR repository name.                      |

### .env.local

For configuring the local Flask app.

| Variable Name                   | Description                              |
|---------------------------------|------------------------------------------|
| FLASK_CONFIG                    | Flask configuration (Default, Staging, Production, or Testing),                      |
| FLASK_DEBUG                     | Flask debug mode.                         |
| FLASK_LOG_LEVEL                 | Flask log level.                          |
| FLASK_SECRET_KEY                | Flask secret key.                         |
| FLASK_PEPPER                    | Flask pepper.                             |
| FLASK_ADMIN_EMAIL               | Admin email. This will be used for logging in to the application when running locally.                             |
| FLASK_ADMIN_PASSWORD            | Admin password. This will be used for logging in to the application when running locally.                           |
| FLASK_DB                        | Flask database URI. This must match the credentials in `.env.postgres`.                       |
| FLASK_APP                       | Flask app entry point.                    |
| LOCAL_LAMBDA_ENDPOINT           | Local Lambda endpoint. This will be used for invoking data processing tasks.                    |

### .env.postgres

For configuring the local postgres container.

| Variable Name                   | Description                              |
|---------------------------------|------------------------------------------|
| POSTGRES_USER                   | PostgreSQL user.                          |
| POSTGRES_PASSWORD               | PostgreSQL password.                      |
| POSTGRES_PORT                   | PostgreSQL port.                          |
| POSTGRES_DB                     | PostgreSQL database name.                 |

## Repo Structure

Following are the main directories in the repository:

| Directory  | Description                                      |
|------------|--------------------------------------------------|
| `backend`  | The Flask app.                                   |
| `frontend` | The frontend React app.                          |
| `functions`| Lambda functions, including the data processing task. |
| `migrations`| Database migrations with `Flask-Migrate`.       |
| `shared`   | Modules shared between backend and functions.    |
| `tests`    | Testing scripts.                                 |

## Zappa Serverless Deployment

The Ditti Research Dashboard uses Zappa for serverless deployment to AWS Lambda. Below are the deployment scripts and their usage for different environments.

### Zappa Settings

The `zappa_settings.json` file contains the configuration for different environments such as `app` (production) and `staging`. Key settings include:

- `app_function`: The entry point for the Flask app.
- `aws_region`: The AWS region for deployment.
- `environment_variables`: Environment variables for the app.
- `events`: Scheduled events for Lambda functions.
- `log_level`: Logging level.
- `project_name`: The name of the project.
- `runtime`: The Python runtime version.
- `tags`: Tags for AWS resources.
- `certificate_arn`: ARN for the SSL certificate.
- `domain`: The domain name for the app.

### RDS Stopper Script

The `rds_stopper.py` script is designed to manage the state of an RDS instance based on recent activity. It checks for HTTP requests in the last two hours and stops the RDS instance if no requests are found.

#### Key Functions

- **Logging Setup:** Configures logging to capture information and errors.
- **Stop Function:**
  - Retrieves HTTP request logs from AWS CloudWatch.
  - Checks for requests in the last two hours.
  - If no requests are found, it checks the status of the RDS instance.
  - Stops the RDS instance if it is running.

#### Environment Variables

The script relies on the following environment variables:

- `AWS_LOG_GROUP_NAME`: The name of the CloudWatch log group.
- `AWS_LOG_PATTERN`: The filter pattern for log events.
- `AWS_DB_INSTANCE_IDENTIFIER`: The identifier of the RDS instance.

#### Usage

To use the script, ensure the required environment variables are set and execute the script. The script is scheduled to run every hour using Zappa's event configuration.

## Wearable Data Retrieval

The `functions/wearable_data_retrieval` directory contains a Lambda function designed to pull Fitbit sleep data from the Fitbit API for participants who have consented to participate in a research study. This function is part of the Ditti Research Dashboard and can be run locally using the provided bash scripts.

### Key Files

- **Dockerfile**: Defines the Docker image for the Lambda function.
- **lambda_function.py**: Contains the main logic for retrieving and processing Fitbit sleep data.
- **run_image.sh**: Builds and runs the Docker image locally.
- **test_image.sh**: Tests the running Docker image by invoking the Lambda function.

### Running Wearable Data Retrieval Locally

To run the wearable data retrieval function locally, follow these steps:

Build and Run the Docker Image:

```bash
./run_image.sh [--no-cache] [--debug] [--staging]
```

- `--no-cache`: Build the Docker image without using the cache.
- `--debug`: Enable debug mode.
- `--staging`: Run in staging mode.

Test the Running Docker Image:

```bash
./test_image.sh
```

This will invoke the Lambda function locally and simulate the retrieval of Fitbit sleep data.

### Wearable Data Retrieval Environment Variables

Ensure the following environment variables are set in your `.env` file:

- `AWS_REGION`: The AWS region.
- `FITBIT_CLIENT_ID`: Fitbit API client ID.
- `FITBIT_CLIENT_SECRET`: Fitbit API client secret.
- `DATABASE_URI`: URI for connecting to the database.

These scripts and configurations facilitate the development and testing of the wearable data retrieval function in a local environment before deploying it to AWS Lambda.
