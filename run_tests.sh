#!/bin/bash

# Run tests for the Openfire REST API Python client

# Default values
HOST="https://localhost:9091"
CREDS="credentials.txt"
INSECURE="--insecure"
TESTS="all"

# Display help message
function show_help {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help            Show this help message"
    echo "  --host HOST           Specify Openfire server host (default: $HOST)"
    echo "  --creds FILE          Specify credentials file (default: $CREDS)"
    echo "  --secure              Enable SSL certificate validation (default: disabled)"
    echo "  --tests TESTS         Specify comma-separated list of tests to run (default: all)"
    echo "                        Available tests: users,groups,system,sessions,messages,muc"
    echo ""
    echo "Example:"
    echo "  $0 --host https://openfire.example.com:9091 --tests users,groups"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -h|--help)
            show_help
            exit 0
            ;;
        --host)
            HOST="$2"
            shift
            shift
            ;;
        --creds)
            CREDS="$2"
            shift
            shift
            ;;
        --secure)
            INSECURE=""
            shift
            ;;
        --tests)
            TESTS="$2"
            shift
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if credentials file exists
if [ ! -f "$CREDS" ]; then
    echo "Error: Credentials file '$CREDS' not found"
    echo "Please create a credentials.txt file with the following format:"
    echo "username: admin"
    echo "password: your_password"
    echo "restapi token: your_api_token"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if required packages are installed
echo "Checking required packages..."
python3 -c "import requests, yaml" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    pip install requests pyyaml
fi

# Display test configuration
echo "=== Test Configuration ==="
echo "Openfire server: $HOST"
echo "Credentials file: $CREDS"
echo "SSL validation: $([ -z "$INSECURE" ] && echo "enabled" || echo "disabled")"
echo "Tests to run: $TESTS"
echo ""

# Run the tests
echo "=== Running Basic Connection Test ==="
python3 tests/test_connection.py --host "$HOST" --creds "$CREDS" $INSECURE
CONNECTION_RESULT=$?

echo ""
echo "=== Running API Coverage Analysis ==="
python3 tests/test_api_coverage.py --spec openapi.yaml
COVERAGE_RESULT=$?

echo ""
echo "=== Running Comprehensive Tests ==="
python3 tests/test_local_server.py --host "$HOST" --creds "$CREDS" $INSECURE --tests "$TESTS"
COMPREHENSIVE_RESULT=$?

# Display overall results
echo ""
echo "=== Overall Test Results ==="
echo "Connection Test: $([ $CONNECTION_RESULT -eq 0 ] && echo "PASSED" || echo "FAILED")"
echo "API Coverage Analysis: $([ $COVERAGE_RESULT -eq 0 ] && echo "PASSED" || echo "FAILED")"
echo "Comprehensive Tests: $([ $COMPREHENSIVE_RESULT -eq 0 ] && echo "PASSED" || echo "FAILED")"

# Determine overall status
if [ $CONNECTION_RESULT -eq 0 ] && [ $COMPREHENSIVE_RESULT -eq 0 ]; then
    echo ""
    echo "All critical tests passed successfully!"
    exit 0
else
    echo ""
    echo "Some tests failed. Please check the output for details."
    exit 1
fi
