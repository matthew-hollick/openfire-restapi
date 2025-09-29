# Security Logs Export Documentation

## Overview

The security logs export functionality allows you to export Openfire security audit logs to Filebeat for further processing in Elasticsearch or other systems. The export includes detailed information about security events in the Openfire server.

## Usage

```bash
./scripts/export_security_logs_for_elasticsearch.py --host http://localhost:9090 --token your_token --url http://filebeat:8080 [options]
```

### Options

- `--host`: Openfire server URL (default: https://localhost:9091)
- `--token`: API token for authentication (required)
- `--username`: Optional username to filter logs
- `--limit`: Maximum number of logs to retrieve (default: 100)
- `--start-time`: Start timestamp in seconds since epoch
- `--end-time`: End timestamp in seconds since epoch
- `--since`: Relative time to fetch logs from (e.g., '1h' for 1 hour, '30m' for 30 minutes, '2d' for 2 days, '1w' for 1 week)
- `--insecure/--secure`: Disable SSL certificate validation (for self-signed certificates)
- `--url`: URL of the Filebeat HTTP endpoint (required for actual sending)
- `--dry-run/--no-dry-run`: Show data that would be sent without actually sending it

### Environment Variables

Common command-line options can be provided via standardized environment variables:
- `--host` can be set with `OPENFIRE_HOST`
- `--token` can be set with `OPENFIRE_TOKEN`
- `--url` can be set with `FILEBEAT_URL`

Script-specific options can be provided via environment variables with the prefix `EXPORT_SECURITY_LOGS_` followed by the option name in uppercase. For example:
- `--start-time` can be set with `EXPORT_SECURITY_LOGS_START_TIME`
- `--end-time` can be set with `EXPORT_SECURITY_LOGS_END_TIME`
- `--since` can be set with `EXPORT_SECURITY_LOGS_SINCE`

Boolean flags can be set with environment variables using true/false values.

## Output Format

The script outputs security log data in JSON format suitable for Filebeat. The basic structure includes:

```json
{
  "log_id": 22,
  "username": "admin",
  "summary": "Successful admin console login attempt",
  "details": "The user logged in successfully to the admin console from address 127.0.0.1.",
  "node": "192.168.5.15",
  "timestamp_ms": 1758900075,
  "@timestamp": "2025-09-26T15:21:15+00:00",
  "host": {
    "name": "hostname"
  },
  "openfire": {
    "server": "http://openfire:9090",
    "domain": "xmpp.example.com"
  }
}
```

## Examples

### Dry Run with Relative Time Filter

```bash
./scripts/export_security_logs_for_elasticsearch.py --host http://localhost:9090 --token your_token --since 1d --dry-run
```

### Export Logs for a Specific User

```bash
./scripts/export_security_logs_for_elasticsearch.py --host http://localhost:9090 --token your_token --url http://filebeat:8080 --username admin --limit 50
```

### Export Logs Within a Specific Timeframe

```bash
./scripts/export_security_logs_for_elasticsearch.py --host http://localhost:9090 --token your_token --url http://filebeat:8080 --start-time 1758814000 --end-time 1758900100
```
