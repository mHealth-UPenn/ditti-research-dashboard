#!/bin/bash
# This script sets up environment variables for the deployed Flask staging environment
# Usage: source flask-staging.sh

# Set the local environment to staging
export FLASK_CONFIG=Production
export AWS_SECRET_NAME=secret-aws-portal-staging

# Export AWS secrets
export $(aws secretsmanager get-secret-value --secret-id $AWS_SECRET_NAME --query SecretString --output text | jq -r 'to_entries | map("\(.key)=\(.value|tostring)") | .[]')

# Export staging env file
export $(cat secret-staging.env | xargs)

echo "Environment variables set for staging."