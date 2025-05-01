#!/bin/bash

project_name=$1

# Check if the current version of python is 3.13 and is a virtual environment
if [[ $(python --version) != "Python 3.13"* || -z "$VIRTUAL_ENV" ]]; then
    echo "Current version of python is not 3.13 or not a virtual environment. Please activate a 3.13 virtual environment first."
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is required but not installed. Please install AWS CLI first."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is required but not installed. Please install Docker first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is required but not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "npm is required but not installed. Please install npm first."
    exit 1
fi

# Run the Python installation script
python -c "from install.installer import Installer; Installer('dev').uninstall()"
