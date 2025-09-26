#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to export Openfire users and send them to a Filebeat HTTP endpoint.
"""

import sys
import os
import json
import socket
import requests
import click
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

# Add parent directory to path to import ofrestapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ofrestapi import Users, System


def transform_properties(user: Dict[str, Any]) -> Dict[str, Any]:
    """Transform properties from array to object format."""
    properties = {}
    if "properties" in user and isinstance(user["properties"], list):
        for prop in user["properties"]:
            if "key" in prop and "value" in prop:
                properties[prop["key"]] = prop["value"]
    return properties




def prepare_user_for_filebeat(user: Dict[str, Any], host_info: Dict[str, str]) -> Dict[str, Any]:
    """
    Prepare a user object for sending to Filebeat.
    
    This function transforms the user data into a format suitable for Filebeat,
    adding hostname and server information.
    
    Available fields from Openfire API (not all are included):
    - username: The user's username (string)
    - name: The user's display name (string)
    - email: The user's email address (string)
    - properties: Custom user properties (object)
    - password: User's password (string, not included for security)
    - creationDate: When the user was created (timestamp, not always available)
    - modificationDate: When the user was last modified (timestamp, not always available)
    
    Args:
        user: User dictionary from Openfire API
        host_info: Dictionary with hostname and server information
        
    Returns:
        Dictionary with user data formatted for Filebeat
    """
    # Transform properties from array to object
    properties = transform_properties(user)
    
    # Create the document with additional host information
    result = {
        "username": user.get("username"),
        "name": user.get("name"),
        "email": user.get("email"),
        "properties": properties,
        "@timestamp": datetime.now(timezone.utc).isoformat(),
        "host": {
            "name": host_info.get("hostname"),
        },
        "openfire": {
            "server": host_info.get("server")
        }
    }
    
    # Add xmpp_domain if available
    if host_info.get("xmpp_domain"):
        result["openfire"]["domain"] = host_info.get("xmpp_domain")
        
    return result


def send_to_filebeat(users: List[Dict[str, Any]], url: Optional[str], host_info: Dict[str, str], insecure: bool, dry_run: bool = False) -> Dict[str, Any]:
    """
    Send user data to a Filebeat HTTP endpoint.
    
    Args:
        users: List of user dictionaries
        url: URL of the Filebeat HTTP endpoint
        host_info: Dictionary with hostname and server information
        insecure: Whether to disable SSL certificate validation
        dry_run: If True, only show the data that would be sent without actually sending it
        
    Returns:
        Dictionary with success and failure counts
    """
    results = {"success": 0, "failure": 0, "failed_users": []}
    
    for user in users:
        try:
            # Prepare the user data for Filebeat
            data = prepare_user_for_filebeat(user, host_info)
            
            # In dry run mode, just print the data without sending
            if dry_run:
                click.echo(f"\nDRY RUN: Data that would be sent for user {user.get('username')}:")
                click.echo(json.dumps(data, indent=2))
                results["success"] += 1
                continue
            
            # For actual sending, URL must be provided
            if not url:
                # This should never happen due to earlier checks, but just in case
                click.echo(f"Error: Cannot send user {user.get('username')} - URL is required", err=True)
                results["failure"] += 1
                results["failed_users"].append(user.get("username"))
                continue
                
            # Send the data to Filebeat
            response = requests.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
                verify=not insecure,
                timeout=10  # Add timeout to prevent hanging on network issues
            )
            
            # Check if the request was successful
            if response.status_code >= 200 and response.status_code < 300:
                results["success"] += 1
            else:
                results["failure"] += 1
                results["failed_users"].append(user.get("username"))
                click.echo(f"Failed to send user {user.get('username')}: {response.status_code} {response.text}", err=True)
        except Exception as e:
            results["failure"] += 1
            results["failed_users"].append(user.get("username"))
            click.echo(f"Error sending user {user.get('username')}: {e}", err=True)
    
    return results


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
    "--url",
    help="URL of the Filebeat HTTP endpoint (if specified, data will be sent to this URL)",
)
@click.option(
    "--dry-run/--no-dry-run",
    default=False,
    help="Dry run mode: show data that would be sent without actually sending it",
)
def export_users(
    host: str,
    token: str,
    search: Optional[str],
    insecure: bool,
    url: Optional[str],
    dry_run: bool,
) -> None:
    """
    Export Openfire users and send them to a Filebeat HTTP endpoint.
    
    This script connects to an Openfire server, retrieves user data, and sends it
    to a Filebeat HTTP endpoint for further processing.
    
    All command-line options can also be provided via environment variables with the
    prefix EXPORT_USERS_ followed by the option name in uppercase. For example:
      --host can be set with EXPORT_USERS_HOST
      --token can be set with EXPORT_USERS_TOKEN
      --url can be set with EXPORT_USERS_URL
    
    Boolean flags like --dry-run can be set with EXPORT_USERS_DRY_RUN=true/false.
    """
    try:
        # Handle SSL verification first, before any network clients are created
        if insecure:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Create Users API client
        users_api = Users(host, token)
        
        # Set verify_ssl attribute directly
        users_api.verify_ssl = not insecure
        
        # Get hostname for identification
        hostname = socket.gethostname()
        
        # Get xmpp.domain from system properties if available
        xmpp_domain = None
        try:
            # Create System API client (reusing host and token)
            system_api = System(host, token)
            system_api.verify_ssl = not insecure
            
            # Get all properties in a single request
            props = system_api.get_props()
            
            # Extract xmpp.domain if available
            if "property" in props:
                for prop in props["property"]:
                    if prop.get("key") == "xmpp.domain":
                        xmpp_domain = prop.get("value")
                        break
        except Exception:
            # If we can't get the domain, continue without it
            pass
        
        # Prepare server information
        server_info = {
            "hostname": hostname,
            "server": host,
            "xmpp_domain": xmpp_domain
        }
        
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
            
        # Handle dry run mode first
        if dry_run:
            # For dry run, URL is optional
            if url:
                click.echo(f"DRY RUN: Would send data to Filebeat at {url}", err=True)
            else:
                click.echo("DRY RUN: Would send data to Filebeat", err=True)
        else:
            # For actual sending, URL is required
            if not url:
                click.echo("Error: --url is required for sending data", err=True)
                sys.exit(1)
            click.echo(f"Sending data to Filebeat at {url}", err=True)
            
        results = send_to_filebeat(users_list, url, server_info, insecure, dry_run)
        
        if dry_run:
            click.echo(f"DRY RUN: Would have sent {results['success']} users", err=True)
        else:
            click.echo(f"Sent {results['success']} users successfully, {results['failure']} failed", err=True)
            if results['failure'] > 0:
                click.echo(f"Failed users: {', '.join(results['failed_users'])}", err=True)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    export_users()
