#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to export Openfire users in a format suitable for Elasticsearch ingestion.
"""

import sys
import os
import json
import click
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

# Add parent directory to path to import ofrestapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ofrestapi import Users


def transform_for_elasticsearch(users: List[Dict[str, Any]], index_name: str) -> List[Dict[str, Any]]:
    """
    Transform user data into Elasticsearch bulk API format.
    
    Args:
        users: List of user dictionaries
        index_name: Name of the Elasticsearch index
        
    Returns:
        List of dictionaries in Elasticsearch bulk API format
    """
    bulk_data = []
    timestamp = datetime.now(timezone.utc).isoformat()
    
    for user in users:
        # Create the action/metadata line
        action = {
            "index": {
                "_index": index_name,
                "_id": user.get("username")
            }
        }
        bulk_data.append(action)
        
        # Transform properties from array to object
        properties = {}
        if "properties" in user and isinstance(user["properties"], list):
            for prop in user["properties"]:
                if "key" in prop and "value" in prop:
                    properties[prop["key"]] = prop["value"]
        
        # Create the document
        document = {
            "username": user.get("username"),
            "name": user.get("name"),
            "email": user.get("email"),
            "properties": properties,
            "@timestamp": timestamp,
            "doc_type": "openfire_user"
        }
        bulk_data.append(document)
    
    return bulk_data


@click.command()
@click.option(
    "--host",
    default="https://localhost:9091",
    help="Openfire server URL (e.g., https://localhost:9091)",
)
@click.option(
    "--token",
    required=True,
    help="API token for authentication",
)
@click.option(
    "--search",
    help="Optional search filter for usernames (acts like wildcard search)",
)
@click.option(
    "--insecure/--secure",
    default=False,
    help="Disable SSL certificate validation (for self-signed certificates)",
)
@click.option(
    "--index",
    default="openfire_users",
    help="Elasticsearch index name",
)
@click.option(
    "--output",
    type=click.Choice(["bulk", "documents"]),
    default="bulk",
    help="Output format: 'bulk' for Elasticsearch Bulk API, 'documents' for individual documents",
)
@click.option(
    "--file",
    help="Output file (if not specified, output to stdout)",
)
def export_users(
    host: str,
    token: str,
    search: Optional[str],
    insecure: bool,
    index: str,
    output: str,
    file: Optional[str],
) -> None:
    """
    Export Openfire users in a format suitable for Elasticsearch ingestion.
    
    This script connects to an Openfire server, retrieves user data, and formats it
    for easy ingestion into Elasticsearch.
    """
    try:
        # Create Users API client
        users_api = Users(host, token)
        
        # Handle SSL verification
        if insecure:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # Monkey patch the requests module
            import requests
            old_request = requests.Session.request
            def new_request(self, method, url, **kwargs):
                kwargs['verify'] = False
                return old_request(self, method, url, **kwargs)
            requests.Session.request = new_request
            
            # Also patch the base requests functions
            old_get = requests.get
            old_post = requests.post
            old_put = requests.put
            old_delete = requests.delete
            
            def new_get(url, **kwargs):
                kwargs['verify'] = False
                return old_get(url, **kwargs)
            
            def new_post(url, **kwargs):
                kwargs['verify'] = False
                return old_post(url, **kwargs)
            
            def new_put(url, **kwargs):
                kwargs['verify'] = False
                return old_put(url, **kwargs)
            
            def new_delete(url, **kwargs):
                kwargs['verify'] = False
                return old_delete(url, **kwargs)
            
            requests.get = new_get
            requests.post = new_post
            requests.put = new_put
            requests.delete = new_delete
            
            click.echo("Warning: SSL certificate validation is disabled", err=True)
        
        # Get users with optional search filter
        result = users_api.get_users(search)
        
        # Process the result based on its structure
        users_list = []
        if isinstance(result, dict) and 'users' in result:
            if isinstance(result['users'], list):
                users_list = result['users']
            elif isinstance(result['users'], dict) and 'user' in result['users']:
                users_list = result['users']['user']
        elif isinstance(result, list):
            users_list = result
        
        if not users_list:
            click.echo("No users found.", err=True)
            return
            
        # Transform data for Elasticsearch
        if output == "bulk":
            es_data = transform_for_elasticsearch(users_list, index)
        else:  # documents
            timestamp = datetime.now(timezone.utc).isoformat()
            es_data = []
            
            for user in users_list:
                # Transform properties from array to object
                properties = {}
                if "properties" in user and isinstance(user["properties"], list):
                    for prop in user["properties"]:
                        if "key" in prop and "value" in prop:
                            properties[prop["key"]] = prop["value"]
                
                # Create the document
                document = {
                    "_index": index,
                    "_id": user.get("username"),
                    "_source": {
                        "username": user.get("username"),
                        "name": user.get("name"),
                        "email": user.get("email"),
                        "properties": properties,
                        "@timestamp": timestamp,
                        "doc_type": "openfire_user"
                    }
                }
                es_data.append(document)
        
        # Output the data
        output_data = json.dumps(es_data, indent=2)
        
        if file:
            with open(file, 'w') as f:
                f.write(output_data)
            click.echo(f"Data exported to {file}", err=True)
        else:
            click.echo(output_data)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    export_users()
