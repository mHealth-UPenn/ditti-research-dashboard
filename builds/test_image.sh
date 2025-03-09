#!/bin/bash
echo "Starting PostgreSQL Docker container..."
docker network create flask-network
docker run \
  -ditp 5432:5432 \
  --name pg \
  --network flask-network \
  --env-file ../postgres.env \
  postgres

# Wait for the database to start, with a timeout of 60 seconds
timeout=60
while ! docker logs pg 2>&1 | grep -q "database system is ready to accept connections"; do
  sleep 1
  timeout=$((timeout - 1))
  if [ $timeout -le 0 ]; then
    echo "Timeout waiting for the database to start."
    docker stop pg
    docker rm pg
    docker network rm flask-network
    exit 1
  fi
done

echo "Starting Flask Docker container..."
docker build -t flask-app ..
docker run \
  -dit \
  --name flask-container \
  --network flask-network \
  --env-file ../flask.env \
  -e FLASK_DB=postgresql://user:pass@pg:5432/postgres \
  -e AWS_DEFAULT_REGION=us-east-1 \
  --entrypoint flask \
  flask-app \
  run

# Wait for the Flask app to start, with a timeout of 60 seconds
timeout=3
while ! docker logs flask-container 2>&1 | grep -q "Debugger PINs"; do
  sleep 1
  timeout=$((timeout - 1))
  if [ $timeout -le 0 ]; then
    echo "Timeout waiting for the Flask app to start."
    echo "Flask logs:"
    docker logs flask-container
    docker stop pg
    docker rm pg
    docker stop flask-container
    docker rm flask-container
    docker network rm flask-network
    exit 1
  fi
done

echo "Running health check..."
response=$(docker exec -t flask-container curl http://localhost:5000/health | jq ".msg")
if [ "$response" != "\"Service is healthy.\"" ]; then
  echo "Health check failed"
  docker stop pg
  docker rm pg
  docker stop flask-container
  docker rm flask-container
  docker network rm flask-network
  exit 1
fi

echo "Health check passed successfully."

# Clean up
docker stop pg
docker rm pg
docker stop flask-container
docker rm flask-container
docker network rm flask-network
