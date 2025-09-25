# Openfire REST API Scripts

This directory contains utility scripts that use the `ofrestapi` library to interact with an Openfire server.

## Requirements

- Python 3.6+
- Click library: `pip install click`

## Available Scripts

### list_users.py

Lists all users from an Openfire server.

#### Usage

```bash
./list_users.py --host https://openfire-server:9091 --token your-api-token [OPTIONS]
```

#### Options

- `--host`: Openfire server URL (default: https://localhost:9091)
- `--token`: API token for authentication (required)
- `--search`: Optional search filter for usernames (acts like wildcard search)
- `--insecure/--secure`: Disable/enable SSL certificate validation (default: --secure)
- `--output`: Output format: json, table, or csv (default: table)
- `--help`: Show help message

#### Examples

List all users in table format:
```bash
./list_users.py --host https://openfire-server:9091 --token your-api-token
```

List users with names containing "admin" in JSON format:
```bash
./list_users.py --host https://openfire-server:9091 --token your-api-token --search admin --output json
```

List all users with insecure SSL (for self-signed certificates):
```bash
./list_users.py --host https://openfire-server:9091 --token your-api-token --insecure
```

Export users to CSV:
```bash
./list_users.py --host https://openfire-server:9091 --token your-api-token --output csv > users.csv
```

### export_users_for_elasticsearch.py

Exports Openfire users in a format suitable for Elasticsearch ingestion.

#### Usage

```bash
./export_users_for_elasticsearch.py --host https://openfire-server:9091 --token your-api-token [OPTIONS]
```

#### Options

- `--host`: Openfire server URL (default: https://localhost:9091)
- `--token`: API token for authentication (required)
- `--search`: Optional search filter for usernames (acts like wildcard search)
- `--insecure/--secure`: Disable/enable SSL certificate validation (default: --secure)
- `--index`: Elasticsearch index name (default: openfire_users)
- `--output`: Output format: bulk or documents (default: bulk)
- `--file`: Output file (if not specified, output to stdout)
- `--help`: Show help message

#### Examples

Export all users in Elasticsearch bulk API format:
```bash
./export_users_for_elasticsearch.py --host https://openfire-server:9091 --token your-api-token > users_bulk.json
```

Export users to a file in individual document format:
```bash
./export_users_for_elasticsearch.py --host https://openfire-server:9091 --token your-api-token --output documents --file users_documents.json
```

Export specific users with insecure SSL:
```bash
./export_users_for_elasticsearch.py --host https://openfire-server:9091 --token your-api-token --search admin --insecure
```

### list_muc.py

Lists all MUC (Multi-User Chat) rooms from an Openfire server.

#### Usage

```bash
./list_muc.py --host https://openfire-server:9091 --token your-api-token [OPTIONS]
```

#### Options

- `--host`: Openfire server URL (default: https://localhost:9091)
- `--token`: API token for authentication (required)
- `--service`: MUC service name (default: conference)
- `--type`: Type of rooms to list: public or all (default: public)
- `--insecure/--secure`: Disable/enable SSL certificate validation (default: --secure)
- `--output`: Output format: json, table, or csv (default: table)
- `--show-users/--no-show-users`: Show users in each room (default: --no-show-users)
- `--help`: Show help message

#### Examples

List all public rooms in table format:
```bash
./list_muc.py --host https://openfire-server:9091 --token your-api-token
```

List all rooms (including private) in JSON format:
```bash
./list_muc.py --host https://openfire-server:9091 --token your-api-token --type all --output json
```

List rooms from a specific service with insecure SSL:
```bash
./list_muc.py --host https://openfire-server:9091 --token your-api-token --service chatrooms --insecure
```

Export rooms to CSV:
```bash
./list_muc.py --host https://openfire-server:9091 --token your-api-token --output csv > rooms.csv
```

List rooms with their users:
```bash
./list_muc.py --host https://openfire-server:9091 --token your-api-token --show-users
```

### export_muc_for_elasticsearch.py

Exports Openfire MUC (Multi-User Chat) rooms in a format suitable for Elasticsearch ingestion.

#### Usage

```bash
./export_muc_for_elasticsearch.py --host https://openfire-server:9091 --token your-api-token [OPTIONS]
```

#### Options

- `--host`: Openfire server URL (default: https://localhost:9091)
- `--token`: API token for authentication (required)
- `--service`: MUC service name (default: conference)
- `--type`: Type of rooms to list: public or all (default: public)
- `--insecure/--secure`: Disable/enable SSL certificate validation (default: --secure)
- `--index`: Elasticsearch index name (default: openfire_muc_rooms)
- `--output`: Output format: bulk or documents (default: bulk)
- `--file`: Output file (if not specified, output to stdout)
- `--help`: Show help message

#### Examples

Export all public rooms in Elasticsearch bulk API format:
```bash
./export_muc_for_elasticsearch.py --host https://openfire-server:9091 --token your-api-token > muc_rooms_bulk.json
```

Export rooms to a file in individual document format:
```bash
./export_muc_for_elasticsearch.py --host https://openfire-server:9091 --token your-api-token --output documents --file muc_rooms_documents.json
```

Export rooms from a specific service with insecure SSL:
```bash
./export_muc_for_elasticsearch.py --host https://openfire-server:9091 --token your-api-token --service chatrooms --insecure
```
