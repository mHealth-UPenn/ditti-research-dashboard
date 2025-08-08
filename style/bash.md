# Bash Script Style Guide

This document defines the coding standards and best practices for bash scripts in Ditti projects.

## File Structure

### Script Organization

Scripts should follow this structure:

1. Copyright header
2. Color definitions
3. Helper functions
4. Variable declarations
5. Help message
6. Main script logic
7. Cleanup section (if required)

## Color Coding and Logging

### Color Definitions

Define ANSI color codes at the top of the script:

```bash
# Color codes for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
```

### Logging Functions

Implement consistent logging functions:

```bash
# Helper functions for colored output
print_header() {
    echo ""
    echo "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo "${RED}✗ $1${NC}"
}

print_info() {
    echo "${CYAN}ℹ $1${NC}"
}

print_step() {
    echo "→ $1"
}
```

### Progress Tracking Function

Use a standardized function for command execution with progress indication:

```bash
# Function to run commands with progress indication
run_with_progress() {
    local message="$1"
    local command="$2"
    
    print_step "$message"
    if eval "$command" > /dev/null 2>&1; then
        print_success "$message completed"
        return 0
    else
        print_error "$message failed"
        return 1
    fi
}
```

## Variable Naming and Declaration

### Default Values

Declare variables with default values at the top:

```bash
NOCACHE=0
PORT=9001
DB_PORT=5433
DATA_FILE=""
```

### Variable Naming

- Use UPPERCASE for global variables
- Use descriptive names
- Separate words with underscores
- Use lowercase for local variables in functions

### Variable Usage

Always quote variables to prevent word splitting:

```bash
docker run -p "${PORT}:8080" "${IMAGE_NAME}"
```

## Function Definitions

### Function Structure

Functions should be simple and focused:

```bash
function_name() {
    local local_var="$1"
    # Function logic
    return 0
}
```

### Local Variables

Use `local` keyword for function-scoped variables:

```bash
run_with_progress() {
    local message="$1"
    local command="$2"
    # ...
}
```

## Command Line Arguments

### Help Message

Define a comprehensive help message:

```bash
HELP_MESSAGE="
Usage: $0 [options]

Options:
    --no-cache: Build without cache (default: false)
    --port: Port to use (default: 9001)
    --db-port: Port to use for the database (default: 5433)
    --help: Show this help message
"
```

### Argument Parsing

Use a consistent argument parsing pattern:

```bash
# parse arguments
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
            ;;
        -*|--*)
            print_error "Unknown option $1"
            exit 1
            ;;
    esac
done
```

### Configuration Display

Show configuration after parsing arguments:

```bash
print_info "Configuration: Port=$PORT, DB Port=$DB_PORT, No Cache=$NOCACHE"
```

## Error Handling

### Exit Codes

Use appropriate exit codes:

- `0`: Success
- `1`: General error
- `2`: Invalid arguments

### Error Checking

Check command exit status:

```bash
if [ $? -ne 0 ]; then
    print_error "Failed to build the image"
    exit 1
fi
```

### Silent Failures

Use `|| true` for commands that may fail but shouldn't stop execution:

```bash
docker stop container-name 2>/dev/null || true
```

## Docker Commands

### Platform Specification

Always specify platform for Docker builds:

```bash
docker build \
    --platform linux/amd64 \
    -t image-name:tag \
    -f Dockerfile .
```

### Environment Variables

Pass environment variables consistently:

```bash
-e AWS_ENDPOINT_URL="http://moto-proxy:5000" \
-e AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION}" \
-e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
-e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
```

### Network Configuration

Use consistent network naming:

```bash
--network project-name-network
```

## Code Organization

### Section Headers

Use clear section headers with `print_header()`:

```bash
print_header "Building Docker Image"
print_header "Setting Up Infrastructure"
print_header "Database Setup"
print_header "Starting Application"
print_header "Cleanup"
```

### Comment Style

Use descriptive comments:

```bash
# Build Docker image
print_header "Building Docker Image"

# Setup infrastructure
print_header "Setting Up Infrastructure"

# Clean up existing containers silently
print_step "Cleaning up existing containers..."
```

### Logical Grouping

Group related operations together:

```bash
# Configure AWS environment
export AWS_ENDPOINT_URL=http://localhost:5005
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=testing
export AWS_SECRET_ACCESS_KEY=testing
```

## Best Practices

### Resource Cleanup

Include cleanup sections when needed:

```bash
# Clean up
print_header "Cleanup"
print_step "Stopping and removing containers..."
docker stop container-name 2>/dev/null || true
docker rm -f container-name 2>/dev/null || true
docker network rm network-name 2>/dev/null || true
print_success "Cleanup completed"
print_info "Test environment has been cleaned up"
```

### Wait Loops

Use appropriate wait loops for service readiness:

```bash
# Wait for database to be ready
print_step "Waiting for database to be ready..."
while ! docker exec container-name psql -U user -d db -c "SELECT 1;" > /dev/null 2>&1; do
    sleep 1
done
echo ""
print_success "Database is ready"
```

### Output Redirection

Redirect output appropriately:

- `> /dev/null 2>&1` for silent execution
- `2>/dev/null || true` for optional commands

### Command Formatting

Format long commands for readability:

```bash
docker run --rm \
    --platform linux/amd64 \
    --name container-name \
    --network network-name \
    -p "${PORT}:8080" \
    -e ENV_VAR="${VALUE}" \
    image-name
```
