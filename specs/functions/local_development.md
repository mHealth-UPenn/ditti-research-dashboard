# Local Development

Local development is facilitated with `run_image.sh` and `test_image.sh` scripts that mock a live Lambda environment.

## `run_image.sh`

The `run_image.sh` script sets up a complete local test environment with mocked AWS services and database.

### Terminal Output

Terminal output is handled with logging logic common to all bash scripts in the repo.

### Command Line Options

Each run image script includes a help message, logic to parse command line arguments, and a call to `print_info` to display configuration.

```bash
HELP_MESSAGE="
Usage: $0 [options]

Options:
    --no-cache: Build without cache (default: false)
    --port: Port to use (default: 9001)
    --help: Show this help message
"

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cache)
            NOCACHE=1
            shift
            ;;
        --port)
            PORT=$2
            shift
            shift
            ;;
        --help)
            echo "$HELP_MESSAGE"
            exit 0
            shift
            ;;
        -*|--*)
            print_error "Unknown option $1"
            exit 1
            ;;
    esac
done

print_info "Configuration: Port=$PORT, No Cache=$NOCACHE"
```

### Docker Setup

Each run silently cleans up and re-creates and docker resources such as images, networks, databases, etc.:

- Build the function docker image:

    ```bash
    docker build \
        -t {function-name}:test \
        --platform linux/amd64 \
        --secret id=aws,src=$HOME/.aws/credentials \
        --target {dev or prod} \
        -f functions/{function_name}/Dockerfile .
    ```

- Clean up existing resources:

    ```bash
    docker stop ... 2>/dev/null || true
    docker rm -f ... 2>/dev/null || true
    ```

- Create a network:

    ```bash
    docker network create ...
    ```

- Optionally create any databases and wait for them to be ready:

    ```bash
    docker run \
        --name {function}-test-db \
        --network {function}-test-network \
        -e POSTGRES_USER="${DB_USERNAME}" \
        -e POSTGRES_PASSWORD="${DB_PASSWORD}" \
        -e PGPASSWORD="${DB_PASSWORD}" \
        -e POSTGRES_DB=test \
        -d postgres:16

    while ! docker exec {function}-test-db psql -U "${DB_USERNAME}" -d test -c "SELECT 1;" > /dev/null 2>&1; do
        sleep 1
    done
    ```

### Moto Setup

Moto is used to create mock AWS resources that the function container will then interact with.

- Create the `motoserver` container:

    ```bash
    docker run -dp 5005:5000 \
        --name moto-proxy \
        --network {function}-test-network \
        motoserver/moto:latest
    ```

- Configure the environment to use `motoserver`:

    ```bash
    export AWS_ENDPOINT_URL=http://localhost:5005
    export AWS_DEFAULT_REGION=us-east-1
    export AWS_ACCESS_KEY_ID=testing
    export AWS_SECRET_ACCESS_KEY=testing
    ```

- Set up mock AWS resources:

    ```bash
    aws s3api create-bucket --bucket test-bucket
    ```

    **Note:** All AWS resources the function interacts with must be mocked.

- Run the function with a connection to `motoserver`:

    ```bash
    docker run --rm \
        --platform linux/amd64 \
        --name {function}-test \
        --network {function}-network \
        -p "${PORT}:8080" \
        -e AWS_ENDPOINT_URL="http://moto-proxy:5000" \
        -e AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION}" \
        -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
        -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
        -e LOCAL=true \
        -e ... \
        {function}:test
    ```

    **Note:** Other mocked third-party APIs, databases, etc. can be connected to the fucntion with the `--add-host` command line option. For example:
      - `--add-host "${DB_HOST}:${DB_CONTAINER_IP}"`
      - `--add-host "${FITBIT_API_HOST}:${FITBIT_API_CONTAINER_IP}"`

### Cleanup

Stop and remove all containers, networks, resources, etc.:

```bash
docker stop ... 2>/dev/null || true
docker rm -f ... 2>/dev/null || true
docker network rm ... 2>/dev/null || true
```

## `test_image.sh`

The `test_image.sh` script invokes the running Lambda function with test data. For example:

```bash
# Help message
# Parse arguments

# Invoke the function
curl "http://localhost:${PORT}/2015-03-31/functions/function/invocations" -d '{...}'
```
