# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may]
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

PORT=9001
DB_PORT=5433
NO_ID=0

HELP_MESSAGE="
Usage: $0 [--port <port>] [--db-port <db-port>] [--no-id] [--help]

Options:
    --port <port>        Port to run the Lambda function on (default: 9001)
    --db-port <db-port>  Port to run the database on (default: 5433)
    --no-id              Do not create a new lambda task entry before invoking.
"

# parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT=$2
            shift
            shift
            ;;
        --db-port)
            DB_PORT=$2
            shift
            shift
            ;;
        --no-id)
            NO_ID=1
            shift
            ;;
        --help)
            echo "$HELP_MESSAGE"
            exit 0
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

if [ $NO_ID -eq 0 ]; then
    export TEST_FLASK_DB="postgresql://test:test@localhost:${DB_PORT}/test"
    export FLASK_CONFIG="Testing"
    OUTPUT=$(flask --app run.py init-lambda-task --status Pending)

    if [ $? -ne 0 ]; then
        echo "Failed to initialize lambda task"
        exit 1
    fi

    FUNCTION_ID=$(echo $OUTPUT | grep ID: | awk -F "ID: " '{ print $2 }')

    echo "Invoking with function ID: ${FUNCTION_ID}"
    curl "http://localhost:${PORT}/2015-03-31/functions/function/invocations" -d '{"function_id": '${FUNCTION_ID}'}'
else
    echo "Invoking without function ID"
    curl "http://localhost:${PORT}/2015-03-31/functions/function/invocations" -d '{}'
fi
