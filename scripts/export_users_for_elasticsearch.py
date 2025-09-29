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

from ofrestapi import Users, System, Sessions, Muc


def transform_properties(user: Dict[str, Any]) -> Dict[str, Any]:
    """Transform properties from array to object format."""
    properties = {}
    if "properties" in user and isinstance(user["properties"], list):
        for prop in user["properties"]:
            if "key" in prop and "value" in prop:
                properties[prop["key"]] = prop["value"]
    return properties




def prepare_user_for_filebeat(user: Dict[str, Any], host_info: Dict[str, str], 
                         session_info: Optional[Dict[str, Any]] = None, 
                         room_info: Optional[Dict[str, Any]] = None,
                         verbose: bool = False) -> Dict[str, Any]:
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
    
    # Add session information if available
    if session_info is not None:
        if verbose:
            click.echo(f"Debug: Adding session info for {user.get('username')}: {session_info}")
            
        result["login_status"] = {
            "is_online": session_info.get("is_online", False)
        }
        
        # Add detailed session information if available
        if "sessions" in session_info and session_info["sessions"]:
            result["login_status"]["sessions"] = []
            for session in session_info["sessions"]:
                session_data = {
                    "resource": session.get("resource"),
                    "status": session.get("presenceStatus"),
                    "priority": session.get("priority"),
                    "client_type": session.get("clientType"),
                    "ip_address": session.get("hostAddress")
                }
                
                # Add connection time if available
                if "creationDate" in session:
                    try:
                        # Convert timestamp to ISO format
                        timestamp = int(session.get("creationDate", 0))
                        if timestamp > 0:
                            dt = datetime.fromtimestamp(timestamp / 1000, timezone.utc)
                            session_data["connected_since"] = dt.isoformat()
                    except (ValueError, TypeError):
                        pass
                        
                result["login_status"]["sessions"].append(session_data)
    
    # Add room information if available
    if room_info is not None:
        if verbose:
            click.echo(f"Debug: Adding room info for {user.get('username')}: {room_info}")
            
        result["room_memberships"] = {
            "current_rooms": room_info.get("occupied_rooms", []),
            "affiliated_rooms": room_info.get("affiliated_rooms", {})
        }
    
    # Add xmpp_domain if available
    if host_info.get("xmpp_domain"):
        result["openfire"]["domain"] = host_info.get("xmpp_domain")
        
    return result


def send_to_filebeat(users: List[Dict[str, Any]], url: Optional[str], host_info: Dict[str, str], insecure: bool, dry_run: bool = False, verbose: bool = False) -> Dict[str, Any]:
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
            # User data is already prepared, just use it directly
            data = user
            
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
    envvar="OPENFIRE_HOST",
)
@click.option(
    "--token",
    required=True,
    help="API token for authentication",
    envvar="OPENFIRE_TOKEN",
)
@click.option(
    "--search",
    help="Optional search filter for usernames (acts like wildcard search)",
    envvar="EXPORT_USERS_SEARCH",
)
@click.option(
    "--insecure/--secure",
    default=False,
    help="Disable SSL certificate validation (for self-signed certificates)",
    envvar="EXPORT_USERS_INSECURE",
)
@click.option(
    "--url",
    help="URL of the Filebeat HTTP endpoint (if specified, data will be sent to this URL)",
    envvar="FILEBEAT_URL",
)
@click.option(
    "--dry-run/--no-dry-run",
    default=False,
    help="Dry run mode: show data that would be sent without actually sending it",
    envvar="EXPORT_USERS_DRY_RUN",
)
@click.option(
    "--include-rooms/--no-include-rooms",
    default=False,
    help="Include room membership information for each user",
    envvar="EXPORT_USERS_INCLUDE_ROOMS",
)
@click.option(
    "--include-sessions/--no-include-sessions",
    default=False,
    help="Include session/login status information for each user",
    envvar="EXPORT_USERS_INCLUDE_SESSIONS",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Show verbose debug output",
    envvar="EXPORT_USERS_VERBOSE",
)
def export_users(
    host: str,
    token: str,
    search: Optional[str],
    insecure: bool,
    url: Optional[str],
    dry_run: bool,
    include_rooms: bool,
    include_sessions: bool,
    verbose: bool,
) -> None:
    """
    Export Openfire users and send them to a Filebeat HTTP endpoint.
    
    This script connects to an Openfire server, retrieves user data, and sends it
    to a Filebeat HTTP endpoint for further processing.
    
    Common command-line options can be provided via standardized environment variables:
      --host can be set with OPENFIRE_HOST
      --token can be set with OPENFIRE_TOKEN
      --url can be set with FILEBEAT_URL
    
    Script-specific options can be provided via environment variables with the
    prefix EXPORT_USERS_ followed by the option name in uppercase. For example:
      --search can be set with EXPORT_USERS_SEARCH
      --insecure can be set with EXPORT_USERS_INSECURE
      --dry-run can be set with EXPORT_USERS_DRY_RUN
      --include-rooms can be set with EXPORT_USERS_INCLUDE_ROOMS
      --include-sessions can be set with EXPORT_USERS_INCLUDE_SESSIONS
      --verbose can be set with EXPORT_USERS_VERBOSE
    
    Boolean flags can be set with environment variables using true/false values.
    """
    try:
        # Handle SSL verification first, before any network clients are created
        if insecure:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Create API clients
        users_api = Users(host, token)
        users_api.verify_ssl = not insecure
        
        # Create additional API clients if needed
        sessions_api = None
        muc_api = None
        
        if include_sessions:
            sessions_api = Sessions(host, token)
            sessions_api.verify_ssl = not insecure
            
        if include_rooms:
            muc_api = Muc(host, token)
            muc_api.verify_ssl = not insecure
        
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
            
        # Process each user to gather additional information
        processed_users = []
        for user in users_list:
            username = user.get("username")
            
            # Get session information if requested
            session_info = None
            if include_sessions and sessions_api and username:
                try:
                    is_online = sessions_api.is_user_online(username)
                    session_details = sessions_api.get_user_session_details(username) if is_online else []
                    session_info = {
                        "is_online": is_online,
                        "sessions": session_details
                    }
                    if verbose:
                        click.echo(f"Debug: Session info for {username}: online={is_online}, sessions={len(session_details)}")
                except Exception as e:
                    click.echo(f"Warning: Could not get session info for {username}: {e}", err=True)
            
            # Get room information if requested
            room_info = None
            if include_rooms and muc_api and username:
                try:
                    # Call get_user_rooms with the correct parameters
                    room_info = muc_api.get_user_rooms(username, servicename="conference")
                    if verbose:
                        occupied = len(room_info.get("occupied_rooms", []))
                        affiliated = sum(len(rooms) for rooms in room_info.get("affiliated_rooms", {}).values())
                        click.echo(f"Debug: Room info for {username}: occupied={occupied}, affiliated={affiliated}")
                except Exception as e:
                    click.echo(f"Warning: Could not get room info for {username}: {e}", err=True)
            
            # Prepare the user data with additional information
            processed_user = prepare_user_for_filebeat(
                user, 
                server_info, 
                session_info=session_info, 
                room_info=room_info,
                verbose=verbose
            )
            processed_users.append(processed_user)
            
        results = send_to_filebeat(processed_users, url, server_info, insecure, dry_run, verbose=verbose)
        
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
