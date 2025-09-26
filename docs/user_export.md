# User Export Documentation

## Overview

The user export functionality allows you to export Openfire user data to Filebeat for further processing in Elasticsearch or other systems. The export includes user profile information and can optionally include room membership and login status information.

## Usage

```bash
./scripts/export_users_for_elasticsearch.py --host http://localhost:9090 --token your_token --url http://filebeat:8080 [options]
```

### Options

- `--host`: Openfire server URL (default: https://localhost:9091)
- `--token`: API token for authentication (required)
- `--search`: Optional search filter for usernames (acts like wildcard search)
- `--insecure/--secure`: Disable SSL certificate validation (for self-signed certificates)
- `--url`: URL of the Filebeat HTTP endpoint (required for actual sending)
- `--dry-run/--no-dry-run`: Show data that would be sent without actually sending it
- `--include-rooms/--no-include-rooms`: Include room membership information for each user
- `--include-sessions/--no-include-sessions`: Include session/login status information for each user
- `--verbose`: Show verbose debug output

### Environment Variables

All command-line options can also be provided via environment variables with the prefix `EXPORT_USERS_` followed by the option name in uppercase. For example:
- `--host` can be set with `EXPORT_USERS_HOST`
- `--token` can be set with `EXPORT_USERS_TOKEN`
- `--url` can be set with `EXPORT_USERS_URL`

Boolean flags like `--dry-run` can be set with `EXPORT_USERS_DRY_RUN=true/false`.

## Output Format

The script outputs user data in JSON format suitable for Filebeat. The basic structure includes:

```json
{
  "username": "user1",
  "name": "User One",
  "email": "user1@example.com",
  "properties": {
    "property1": "value1",
    "property2": "value2"
  },
  "@timestamp": "2025-09-26T19:00:50.697051+00:00",
  "host": {
    "name": "hostname"
  },
  "openfire": {
    "server": "http://openfire:9090",
    "domain": "xmpp.example.com"
  }
}
```

### Room Membership Information

When `--include-rooms` is specified, the output includes room membership information:

```json
{
  "room_memberships": {
    "current_rooms": [
      {
        "room_name": "lobby",
        "natural_name": "Lobby",
        "subject": "Welcome",
        "occupant_nickname": "user1",
        "occupant_role": "participant",
        "service_name": "conference"
      }
    ],
    "affiliated_rooms": {
      "owner": [
        {
          "room_name": "room1",
          "natural_name": "Room 1",
          "subject": "Topic",
          "service_name": "conference"
        }
      ],
      "admin": [],
      "member": [],
      "outcast": []
    }
  }
}
```

### Login Status Information

When `--include-sessions` is specified, the output includes login status information:

```json
{
  "login_status": {
    "is_online": true,
    "sessions": [
      {
        "resource": "mobile",
        "status": "Available",
        "priority": 5,
        "client_type": "Conversations",
        "ip_address": "192.168.1.5",
        "connected_since": "2025-09-26T10:15:30+00:00"
      }
    ]
  }
}
```

## Examples

### Dry Run with Room and Session Information

```bash
./scripts/export_users_for_elasticsearch.py --host http://localhost:9090 --token your_token --include-rooms --include-sessions --dry-run
```

### Export All Users to Filebeat

```bash
./scripts/export_users_for_elasticsearch.py --host http://localhost:9090 --token your_token --url http://filebeat:8080
```

### Export Specific Users with Room and Session Information

```bash
./scripts/export_users_for_elasticsearch.py --host http://localhost:9090 --token your_token --url http://filebeat:8080 --search "admin*" --include-rooms --include-sessions
```
