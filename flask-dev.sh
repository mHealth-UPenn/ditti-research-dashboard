#!/bin/bash
# This script sets up environment variables for the local Flask dev environment
# Usage: source flask-dev.sh

export $(cat secret-aws.env | xargs)
export $(cat flask.env | xargs)
export $(cat cognito.env | xargs)
export $(cat fitbit.env | xargs)

echo "Environment variables set for local development."