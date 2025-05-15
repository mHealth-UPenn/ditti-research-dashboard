# Dev Setup Guide

## Prerequisites

- [**Python 3.13**](https://docs.python.org/3/whatsnew/3.13.html): We recommend using Python 3.13 for development.
- [**AWS CLI**](https://aws.amazon.com/cli/): Installing and [configuring](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html#getting-started-quickstart-new-command): the AWS CLI before getting started.
- [**Docker**](https://www.docker.com/): Services are run locally using Docker for development.
- [**Node.js v22**](https://nodejs.org/en/blog/release/v22.11.0): Our frontend is built using Node.js v22.
- **Unix runtime environment**: Our development environment must be run in a Unix environment with either Linux, MacOS, or [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/install).
- **Dev Fitbit Credentials** (optional): If you plan to contribute changes to our integration with Fitbit, you must register your own application on [dev.fitbit.com](https://dev.fitbit.com/).

## Install Framework

This repo contains an install framework that automates the deployment of development environments. The `install-dev.sh` script runs this framework.

Running the install framework outputs a `project-config.json` with details about your stack. The stack can be uninstalled using `uninstall-dev.sh`.

## Development Stack

**Frontend**:

- The frontend can be found in `frontend/` and is managed with npm.

**Flask API**:

- The Flask API can be found in `backend/` and is run using `./deploy-dev.sh`

**Docker**:

- A PostgreSQL Docker container.
- A wearable data retrieval container that can be found in `functions/wearable_data_retrieval`.

**AWS** (deployed using CloudFormation):

- Cognito user pool, client, and domain for researcher log in.
- Cognito user pool, client, and domain for participant log in.
- SecretsManager secret for storing development credentials.
- SecretsManager secret for storing participant Fitbit API keys.
- S3 bucket for uploading audio files.
- S3 bucket for uploading wearable data retrieval function logs.

## Setup

1. Create a Python3.13 virtual environment and install project requirements.

   ```bash
   python3.13 -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   ```

2. Run the install framework.

   ```bash
   ./install-dev.sh
   ```

   You will be prompted to configure the AWS CLI. Ensure you have sufficient permissions to deploy the stack.

   Enter a recognizable name for your project.

   Enter your Fitbit OAuth 2.0 Client ID and Client Secret. If you do not have these, leave them blank.

   Enter an email that you will use to log in with as an admin.

3. Run the frontend.

   ```bash
   cd frontend
   npm run start
   ```

   **Note:** If you are contributing changes to the frontend, enable hot reloading of Tailwind CSS:

   ```bash
   npm run tailwind:watch
   ```

4. Run the backend.

   ```bash
   ./deploy-dev.sh
   ```

   This script starts the Docker containers and runs the Flask API.

5. Retrieve your temporary password from your email and log in to [localhost:3000/coordinator/login](http://localhost:3000/coordinator/login).
