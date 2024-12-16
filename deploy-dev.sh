# Initialize flags
CONDA_FLAG=false
INIT_FLAG=false
NO_AWS=false

# Check for "conda" and "init" parameters
for arg in "$@"
do
    if [[ "$arg" == "conda" ]]; then
        CONDA_FLAG=true
    elif [[ "$arg" == "init" ]]; then
        INIT_FLAG=true
    elif [[ "$arg" == "no-aws" ]]; then
        NO_AWS=true
    fi
done

# Handle Python virtual environment setup if "conda" is not provided
if [[ "$CONDA_FLAG" == false ]]; then
    # if no python virtual environment, create one
    if [ ! -f env/bin/activate ]; then
        echo "Initializing Python virtual environment..."
        python3 -m venv env
    fi

    # enter the python virtual environment
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        echo "Entering Python virtual environment..."
        source env/bin/activate
    fi
else
    echo "Skipping Python virtual environment setup."
fi

# install missing python packages
arr1=$(pip3 freeze)
arr2=$(cat requirements.txt)
arr3=(`echo ${arr1[@]} ${arr2[@]} | tr ' ' '\n' | sort | uniq -u`)
arr4=(`echo ${arr2[@]} ${arr3[@]} | tr ' ' '\n' | sort | uniq -d`)

if [[ ! -z ${arr4[@]} ]]; then
    echo "Installing required Python packages..."
    pip3 install ${arr4[@]}
else
    echo "Correct Python packages are installed."
fi

# if aws credentials are available, export them
if [ -f secret-aws.env ]; then
    echo "secret-aws.env found. Exporting credentials..."
    export $(cat secret-aws.env | xargs)
else
    echo "secret-aws.env not found. Credentials not exported."
fi

# export development env variables
export $(cat flask.env | xargs)

# export development cognito and fitbit env variables
export $(cat cognito.env | xargs)
export $(cat fitbit.env | xargs)

if [[ "$NO_AWS" == false ]]; then
    # Secret name
    SECRET_NAME="aws-portal-secret-dev"

    # Retrieve secret value using AWS CLI
    echo "Fetching secret: $SECRET_NAME"
    SECRET_JSON=$(aws secretsmanager get-secret-value --secret-id "$SECRET_NAME" --query 'SecretString' --output text)

    if [[ -z "$SECRET_JSON" ]]; then
    echo "Failed to retrieve secret or secret is empty."
    else
        # Parse the JSON and export key-value pairs as environment variables
        echo "Exporting key-value pairs as environment variables..."
        echo "$SECRET_JSON" | jq -r 'to_entries | .[] | "export \(.key)=\(.value)"' | while read -r ENV_VAR; do
        eval "$ENV_VAR"
        done
    fi
fi

echo "Environment variables exported successfully."

# Run initialization commands if "init" parameter is provided
if [[ "$INIT_FLAG" == true ]]; then
    echo "Initializing application..."
    docker run -ditp 5432:5432 --name aws-pg --env-file postgres.env postgres
    flask db upgrade
    flask init-integration-testing-db
fi
