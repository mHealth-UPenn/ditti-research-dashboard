#!/bin/bash

# Check if ROLE_ARN is provided
if [ -z "$ROLE_ARN" ]; then
    echo "ROLE_ARN environment variable is not set. Running without role assumption."
    exec /lambda-entrypoint.sh "$@"
    exit 0
fi

# Check if AWS_REGION is provided
if [ -z "$AWS_REGION" ]; then
    echo "AWS_REGION environment variable is not set. Using default region."
    AWS_REGION="us-east-1"
fi

echo "Assuming role: $ROLE_ARN"

# Assume the role and get temporary credentials
CREDENTIALS=$(aws sts assume-role \
    --role-arn "$ROLE_ARN" \
    --role-session-name "LocalLambdaSession" \
    --region "$AWS_REGION" \
    --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
    --output text)

if [ -z "$CREDENTIALS" ]; then
    echo "Failed to assume role. Exiting."
    exit 1
fi

# Extract credentials
ACCESS_KEY=$(echo $CREDENTIALS | awk '{print $1}')
SECRET_KEY=$(echo $CREDENTIALS | awk '{print $2}')
SESSION_TOKEN=$(echo $CREDENTIALS | awk '{print $3}')

# Export credentials as environment variables
export AWS_ACCESS_KEY_ID=$ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=$SECRET_KEY
export AWS_SESSION_TOKEN=$SESSION_TOKEN

echo "Successfully assumed role. Running Lambda function..."

# Execute the Lambda function
exec /lambda-entrypoint.sh "$@"
