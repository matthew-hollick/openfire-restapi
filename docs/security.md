# Security Audit Logs

This module provides functionality to access security audit logs in Openfire.

## SecurityAuditLog Class

### Constructor

```python
SecurityAuditLog(host, secret, endpoint="/plugins/restapi/v1/logs/security")
```

- `host`: Scheme://Host/ for API requests
- `secret`: Shared secret key for API requests
- `endpoint`: Endpoint for API requests (default: "/plugins/restapi/v1/logs/security")

### Methods

#### get_logs

```python
get_logs(username=None, offset=None, limit=100, start_time=None, end_time=None)
```

Retrieve entries from the security audit log.

- `username`: Optional username to filter events by
- `offset`: Optional number of log entries to skip
- `limit`: Number of log entries to retrieve (default: 100)
- `start_time`: Optional oldest timestamp (in seconds since epoch) of logs to retrieve
- `end_time`: Optional most recent timestamp (in seconds since epoch) of logs to retrieve

Returns a dictionary containing security audit log entries.

#### get_logs_by_username

```python
get_logs_by_username(username, limit=100)
```

Retrieve security audit log entries for a specific user.

- `username`: Username to filter events by
- `limit`: Number of log entries to retrieve (default: 100)

Returns a dictionary containing security audit log entries for the specified user.

#### get_recent_logs

```python
get_recent_logs(limit=20)
```

Retrieve the most recent security audit log entries.

- `limit`: Number of recent log entries to retrieve (default: 20)

Returns a dictionary containing the most recent security audit log entries.

#### get_logs_in_timeframe

```python
get_logs_in_timeframe(start_time, end_time, limit=100)
```

Retrieve security audit log entries within a specific timeframe.

- `start_time`: Oldest timestamp (in milliseconds since epoch) of logs to retrieve
- `end_time`: Most recent timestamp (in milliseconds since epoch) of logs to retrieve
- `limit`: Number of log entries to retrieve (default: 100)

Returns a dictionary containing security audit log entries within the specified timeframe.

#### extract_log_entries

```python
extract_log_entries(logs_response)
```

Extract individual log entries from the API response.

- `logs_response`: The response from get_logs()

Returns a list of individual log entry dictionaries.

## Example Usage

```python
from ofrestapi import SecurityAuditLog

# Create SecurityAuditLog API client
security_api = SecurityAuditLog("http://localhost:9090", "your_auth_token")
security_api.verify_ssl = False  # Set to True in production

# Get recent logs
recent_logs = security_api.get_recent_logs(limit=10)

# Extract log entries
log_entries = security_api.extract_log_entries(recent_logs)
for log in log_entries:
    print(f"{log.get('timestamp')}: {log.get('username')} - {log.get('summary')}")

# Get logs for a specific user
user_logs = security_api.get_logs_by_username("admin", limit=5)
```

## Log Entry Structure

Each log entry contains the following fields:

- `logId`: Unique identifier for the log entry
- `username`: Username associated with the log entry
- `timestamp`: Timestamp of the log entry (in seconds since epoch)
- `summary`: Summary of the log entry
- `node`: Node where the log entry was generated
- `details`: Additional details about the log entry

## API Response Format

The API response from the `/plugins/restapi/v1/logs/security` endpoint has the following structure:

```json
{
  "logs": [
    {
      "logId": 22,
      "username": "admin",
      "timestamp": 1758900075,
      "summary": "Successful admin console login attempt",
      "node": "192.168.5.15",
      "details": "The user logged in successfully to the admin console from address 127.0.0.1. "
    },
    {
      "logId": 21,
      "username": "admin",
      "timestamp": 1758814896,
      "summary": "created new MUC room alpha",
      "node": "192.168.5.15",
      "details": "subject = alpha topic\nroomdesc = alpha description\nroomname = alpha\nmaxusers = 30"
    }
  ]
}
```

Note that all timestamps are in seconds since epoch.
