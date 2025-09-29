# MUC Export Documentation

## Overview

The MUC (Multi-User Chat) export functionality allows you to export Openfire chat room data to Filebeat for further processing in Elasticsearch or other systems. The export includes detailed information about chat rooms, their configurations, and occupants.

## Usage

```bash
./scripts/export_muc_for_elasticsearch.py --host http://localhost:9090 --token your_token --url http://filebeat:8080 [options]
```

### Options

- `--host`: Openfire server URL (default: https://localhost:9091)
- `--token`: API token for authentication (required)
- `--service`: MUC service name (default: conference)
- `--type`: Type of rooms to list (public or all) (default: public)
- `--insecure/--secure`: Disable SSL certificate validation (for self-signed certificates)
- `--url`: URL of the Filebeat HTTP endpoint (required for actual sending)
- `--dry-run/--no-dry-run`: Show data that would be sent without actually sending it

### Environment Variables

Common command-line options can be provided via standardized environment variables:
- `--host` can be set with `OPENFIRE_HOST`
- `--token` can be set with `OPENFIRE_TOKEN`
- `--url` can be set with `FILEBEAT_URL`

For backward compatibility, these options also support script-specific environment variables:
- `--host` can also be set with `EXPORT_MUC_HOST`
- `--token` can also be set with `EXPORT_MUC_TOKEN`
- `--url` can also be set with `EXPORT_MUC_URL`

The standardized environment variables (`OPENFIRE_*`, `FILEBEAT_*`) take precedence over the script-specific ones (`EXPORT_MUC_*`) when both are set.

Other script-specific options can be provided via environment variables with the prefix `EXPORT_MUC_` followed by the option name in uppercase. For example:
- `--service` can be set with `EXPORT_MUC_SERVICE`
- `--type` can be set with `EXPORT_MUC_TYPE`
- `--insecure` can be set with `EXPORT_MUC_INSECURE`
- `--dry-run` can be set with `EXPORT_MUC_DRY_RUN`

Boolean flags can be set with environment variables using true/false values.

## Output Format

The script outputs MUC room data in JSON format suitable for Filebeat. The basic structure includes:

```json
{
  "room_name": "lobby",
  "natural_name": "Lobby",
  "description": "Main lobby for general discussions",
  "subject": "Welcome to the lobby",
  "service_name": "conference",
  "creation_date": "2025-08-15T12:30:45+00:00",
  "modification_date": "2025-09-20T08:15:30+00:00",
  "max_users": 30,
  "persistent": true,
  "public_room": true,
  "registration_enabled": true,
  "can_anyone_discover_jid": true,
  "can_occupants_change_subject": false,
  "can_occupants_invite": false,
  "can_change_nickname": true,
  "log_enabled": true,
  "login_restricted_to_nickname": false,
  "members_only": false,
  "moderated": false,
  "broadcast_presence_roles": ["moderator", "participant", "visitor"],
  "allow_pm": "anyone",
  "users": {
    "owners": ["admin@example.com"],
    "admins": [],
    "members": ["user1@example.com", "user2@example.com"],
    "outcasts": []
  },
  "groups": {
    "owner_groups": [],
    "admin_groups": [],
    "member_groups": [],
    "outcast_groups": []
  },
  "occupants": [
    {
      "jid": "user1@example.com/mobile",
      "role": "participant",
      "affiliation": "member",
      "nickname": "mobile"
    }
  ],
  "occupant_count": 1,
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

## Examples

### Dry Run for Public Rooms

```bash
./scripts/export_muc_for_elasticsearch.py --host http://localhost:9090 --token your_token --dry-run
```

### Export All Rooms (Public and Private)

```bash
./scripts/export_muc_for_elasticsearch.py --host http://localhost:9090 --token your_token --url http://filebeat:8080 --type all
```

### Export Rooms from a Different MUC Service

```bash
./scripts/export_muc_for_elasticsearch.py --host http://localhost:9090 --token your_token --url http://filebeat:8080 --service chat
```
