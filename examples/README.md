# Openfire REST API Client Examples

This directory contains example scripts demonstrating how to use the Openfire REST API Python client.

## Example Scripts

1. **basic_usage.py** - Simple examples of basic API operations
2. **advanced_usage.py** - More complex examples including error handling, user/group management, and MUC operations

## Running the Examples

### Prerequisites

- Python 3.6 or higher
- A running Openfire server with the REST API plugin enabled
- API credentials (admin username, password, and REST API token)

### Setup

1. Make sure you have the required Python packages:

```bash
pip install requests
```

2. Create a `credentials.txt` file in the project root with the following format:

```
username: admin
password: your_password
restapi token: your_api_token
```

### Basic Usage Example

This script demonstrates simple API operations:

```bash
cd examples
./basic_usage.py --host https://localhost:9091 --creds ../credentials.txt --insecure
```

Options:
- `--host`: The Openfire server URL (default: https://localhost:9091)
- `--creds`: Path to credentials file (default: ../credentials.txt)
- `--insecure`: Disable SSL certificate validation for self-signed certificates

### Advanced Usage Example

This script demonstrates more complex operations including error handling:

```bash
cd examples
./advanced_usage.py --host https://localhost:9091 --creds ../credentials.txt --insecure --example all
```

Options:
- `--host`: The Openfire server URL (default: https://localhost:9091)
- `--creds`: Path to credentials file (default: ../credentials.txt)
- `--insecure`: Disable SSL certificate validation for self-signed certificates
- `--example`: Which example to run (choices: all, error, user, group, muc)

## Example Descriptions

### Basic Usage Examples

1. **Get all users** - Retrieves and displays all users in the system
2. **Get all groups** - Retrieves and displays all groups in the system
3. **Get system properties** - Retrieves and displays system properties
4. **Get active sessions** - Retrieves and displays active user sessions
5. **Get chat rooms** - Retrieves and displays all chat rooms
6. **Send a broadcast message** - Sends a broadcast message to all online users

### Advanced Usage Examples

1. **Error Handling** - Demonstrates proper error handling with the API
2. **User Management** - Shows how to create, read, update, and delete users with properties
3. **Group Management** - Shows how to create groups and manage group membership
4. **MUC Management** - Shows how to create and manage chat rooms and user roles

## Notes

- The examples are designed to clean up after themselves (e.g., deleting test users, groups, and rooms that were created during execution)
- When using a self-signed certificate, always use the `--insecure` flag
- The examples create resources with random names to avoid conflicts with existing resources
