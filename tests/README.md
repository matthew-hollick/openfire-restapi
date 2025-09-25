# Openfire REST API Tests

This directory contains test scripts for the Openfire REST API Python client.

## Test Scripts

1. **test_connection.py** - Basic connectivity test to verify the client can connect to an Openfire server
2. **test_api_coverage.py** - Analyzes API coverage against the OpenAPI specification
3. **test_local_server.py** - Comprehensive test suite that performs actual API operations against a running Openfire server

## Running the Tests

### Prerequisites

- Python 3.6 or higher
- A running Openfire server with the REST API plugin enabled
- API credentials (admin username, password, and REST API token)

### Setup

1. Make sure you have the required Python packages:

```bash
pip install requests pyyaml
```

2. Create a `credentials.txt` file in the project root with the following format:

```
username: admin
password: your_password
restapi token: your_api_token
```

### Basic Connection Test

This test verifies that the client can connect to the Openfire server and perform basic API calls:

```bash
python tests/test_connection.py --host https://localhost:9091 --creds credentials.txt --insecure
```

Options:
- `--host`: The Openfire server URL (default: https://localhost:9091)
- `--creds`: Path to credentials file (default: credentials.txt)
- `--insecure`: Disable SSL certificate validation for self-signed certificates

### API Coverage Analysis

This test analyzes how well the Python client covers the endpoints defined in the OpenAPI specification:

```bash
python tests/test_api_coverage.py --spec openapi.yaml
```

Options:
- `--spec`: Path to the OpenAPI specification file (default: openapi.yaml)

### Comprehensive Tests

This test suite performs actual API operations against a running Openfire server:

```bash
python tests/test_local_server.py --host https://localhost:9091 --creds credentials.txt --insecure
```

Options:
- `--host`: The Openfire server URL (default: https://localhost:9091)
- `--creds`: Path to credentials file (default: credentials.txt)
- `--insecure`: Disable SSL certificate validation for self-signed certificates
- `--tests`: Comma-separated list of tests to run (default: all)
  - Available tests: users,groups,system,sessions,messages,muc

Example to run only user and group tests:

```bash
python tests/test_local_server.py --tests users,groups --insecure
```

## Notes

- The tests are designed to clean up after themselves (e.g., deleting test users, groups, and rooms that were created during testing)
- When using a self-signed certificate, always use the `--insecure` flag
- Some tests may be skipped if they require specific conditions (e.g., active user sessions)
- The tests create resources with random names to avoid conflicts with existing resources
