# Openfire REST API Client

A Python client for Openfire's REST API Plugin, modernized for Python 3.

## Requirements

* Python 3.6 or higher
* python-setuptools
* python-requests
* pyyaml (for tests)

## Installation

### Using pip

```bash
pip install openfire-restapi
```

### Using uv (with mise)

```bash
mise install
uv pip install .
```

### From source

```bash
git clone https://github.com/matthew-hollick/openfire-restapi.git
cd openfire-restapi
python setup.py install
```

### Using a virtual environment

```bash
python -m venv env
source env/bin/activate
pip install requests pyyaml
git clone https://github.com/matthew-hollick/openfire-restapi.git
cd openfire-restapi
pip install .
```

## Documentation

* [User related](docs/users.md)
* [Groups related](docs/groups.md)
* [Chat room related](docs/muc.md)
* [Session related](docs/sessions.md)
* [Messages related](docs/messages.md)
* [System related](docs/system.md)

## Testing

This package includes comprehensive test scripts to verify functionality against a running Openfire server.

### Prerequisites

- A running Openfire server with the REST API plugin enabled
- API credentials (admin username, password, and REST API token)

### Setting up credentials

Create a `credentials.txt` file in the project root with the following format:

```
username: admin
password: your_password
restapi token: your_api_token
```

### Running tests

Use the provided script to run all tests:

```bash
./run_tests.sh --host https://localhost:9091 --insecure
```

Options:
- `--host HOST`: Specify Openfire server host (default: https://localhost:9091)
- `--creds FILE`: Specify credentials file (default: credentials.txt)
- `--secure`: Enable SSL certificate validation (default: disabled)
- `--tests TESTS`: Specify comma-separated list of tests to run (default: all)

For more detailed information about the test suite, see the [tests README](tests/README.md).

## SSL Certificate Validation

When connecting to an Openfire server with a self-signed certificate, you should disable SSL certificate validation in your code:

```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Then in your requests:
import requests
requests.get(url, verify=False)
```

In production environments with valid certificates, always enable certificate validation.
