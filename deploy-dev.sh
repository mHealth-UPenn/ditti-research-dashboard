if [[ "$1" != "conda" ]]; then
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