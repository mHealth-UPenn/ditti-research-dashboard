#!/bin/bash
echo "Running tests with pytest..."
docker run -ditp 5432:5432 --name pg --env-file ../postgres.env postgres

# Wait for the database to start, with a timeout of 60 seconds
timeout=60
while ! docker logs pg 2>&1 | grep -q "database system is ready to accept connections"; do
  sleep 1
  timeout=$((timeout - 1))
  if [ $timeout -le 0 ]; then
    echo "Timeout waiting for the database to start."
    docker stop pgDebugger PIN
    exit 1
  fi
done

# Run the tests
export $(cat ../flask.env | xargs)
pytest ../tests/
if [ $? -ne 0 ]; then
  echo "Tests failed."
  docker stop pg
  docker rm pg
  exit 1
else
  echo "Tests passed successfully."
fi

docker stop pg
docker rm pg
