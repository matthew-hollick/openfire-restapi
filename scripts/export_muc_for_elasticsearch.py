#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to export Openfire MUC (Multi-User Chat) rooms and send them to a Filebeat HTTP endpoint.
"""

import sys
import os
import json
import socket
import requests
import click
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Add parent directory to path to import ofrestapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ofrestapi import Muc, System


def _normalize_role_data(role_data: Any, key_name: str) -> List:
    """
    Normalize role data to ensure it's always a list.
    
    Args:
        role_data: The role data to normalize (dict, list, or None)
        key_name: The key name to extract from dict if role_data is a dict
        
    Returns:
        A list of role values
    """
    if isinstance(role_data, dict) and key_name in role_data:
        return role_data[key_name]
    elif isinstance(role_data, list):
        return role_data
    else:
        return []


def _convert_timestamp(timestamp_value: Any) -> str:
    """
    Convert a Unix timestamp (milliseconds) to ISO 8601 format.
    
    Args:
        timestamp_value: Unix timestamp in milliseconds or any other value
        
    Returns:
        ISO 8601 formatted timestamp if input is a number, otherwise the original value
    """
    if isinstance(timestamp_value, (int, float)):
        return datetime.fromtimestamp(timestamp_value / 1000, tz=timezone.utc).isoformat()
    return timestamp_value


def _process_occupants(occupants_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process occupants data from the API response.
    
    Args:
        occupants_data: The API response containing occupants/participants data
        
    Returns:
        A list of normalized occupant dictionaries
    """
    occupants_list = []
    
    if isinstance(occupants_data, dict):
        # Handle the 'participants' key which is used in the API response
        if 'participants' in occupants_data:
            if isinstance(occupants_data['participants'], list):
                occupants_list = occupants_data['participants']
            # Handle single participant case (explicitly check for dict type)
            elif isinstance(occupants_data['participants'], dict):
                occupants_list = [occupants_data['participants']]
        # Also try the 'occupants' key for backward compatibility
        elif 'occupants' in occupants_data:
            if isinstance(occupants_data['occupants'], list):
                occupants_list = occupants_data['occupants']
            elif isinstance(occupants_data['occupants'], dict) and 'occupant' in occupants_data['occupants']:
                occupants_list = occupants_data['occupants']['occupant']
                # Handle single occupant case (explicitly check for dict type)
                if isinstance(occupants_list, dict):
                    occupants_list = [occupants_list]
    
    # Normalize each occupant entry
    normalized_occupants = []
    for occupant in occupants_list:
        normalized = {
            "jid": occupant.get('jid', ''),
            "role": occupant.get('role', ''),
            "affiliation": occupant.get('affiliation', ''),
        }
        
        # Extract nickname from JID if possible
        if '/' in normalized["jid"]:
            normalized["nickname"] = normalized["jid"].split('/')[-1]
        elif occupant.get('nick'):
            normalized["nickname"] = occupant.get('nick')
        else:
            normalized["nickname"] = "Unknown"
            
        normalized_occupants.append(normalized)
    
    return normalized_occupants


def prepare_room_for_filebeat(room: Dict[str, Any], host_info: Dict[str, str], muc_api=None, service: str = "conference") -> Dict[str, Any]:
    """
    Prepare a room object for sending to Filebeat.
    
    This function transforms the room data into a format suitable for Filebeat,
    adding hostname and server information.
    
    Available fields from Openfire API (not all may be included):
    - roomName: The name of the room (string)
    - naturalName: The display name of the room (string)
    - description: Room description (string)
    - subject: Room subject/topic (string)
    - creationDate: When the room was created (timestamp)
    - modificationDate: When the room was last modified (timestamp)
    - maxUsers: Maximum number of users allowed (integer)
    - persistent: Whether the room persists after all users leave (boolean)
    - publicRoom: Whether the room is publicly listed (boolean)
    - and many more configuration settings
    
    Args:
        room: Room dictionary from Openfire API
        host_info: Dictionary with hostname and server information
        muc_api: Optional MUC API client for fetching additional data
        service: Optional MUC service name
        
    Returns:
        Dictionary with room data formatted for Filebeat
    """
    # Process user roles with the helper function
    owners = _normalize_role_data(room.get("owners", []), "owner")
    admins = _normalize_role_data(room.get("admins", []), "admin")
    members = _normalize_role_data(room.get("members", []), "member")
    outcasts = _normalize_role_data(room.get("outcasts", []), "outcast")
    
    # Process group roles with the helper function
    owner_groups = _normalize_role_data(room.get("ownerGroups", []), "ownerGroup")
    admin_groups = _normalize_role_data(room.get("adminGroups", []), "adminGroup")
    member_groups = _normalize_role_data(room.get("memberGroups", []), "memberGroup")
    outcast_groups = _normalize_role_data(room.get("outcastGroups", []), "outcastGroup")
    
    # Get current occupants if API client is provided
    occupants = []
    if muc_api and room.get("roomName"):
        try:
            occupants_result = muc_api.get_room_users(room.get("roomName"), service)
            occupants = _process_occupants(occupants_result)
        except Exception:
            # If there's an error, leave occupants as an empty list
            pass
    
    # Create the document with additional host information
    result = {
        "room_name": room.get("roomName"),
        "natural_name": room.get("naturalName"),
        "description": room.get("description"),
        "subject": room.get("subject"),
        "service_name": room.get("serviceName", "conference"),
        "creation_date": _convert_timestamp(room.get("creationDate")),
        "modification_date": _convert_timestamp(room.get("modificationDate")),
        "max_users": room.get("maxUsers"),
        "persistent": room.get("persistent"),
        "public_room": room.get("publicRoom"),
        "registration_enabled": room.get("registrationEnabled"),
        "can_anyone_discover_jid": room.get("canAnyoneDiscoverJID"),
        "can_occupants_change_subject": room.get("canOccupantsChangeSubject"),
        "can_occupants_invite": room.get("canOccupantsInvite"),
        "can_change_nickname": room.get("canChangeNickname"),
        "log_enabled": room.get("logEnabled"),
        "login_restricted_to_nickname": room.get("loginRestrictedToNickname"),
        "members_only": room.get("membersOnly"),
        "moderated": room.get("moderated"),
        "broadcast_presence_roles": room.get("broadcastPresenceRoles", []),
        "allow_pm": room.get("allowPM", "anyone"),
        "users": {
            "owners": owners,
            "admins": admins,
            "members": members,
            "outcasts": outcasts
        },
        "groups": {
            "owner_groups": owner_groups,
            "admin_groups": admin_groups,
            "member_groups": member_groups,
            "outcast_groups": outcast_groups
        },
        "occupants": occupants,
        "occupant_count": len(occupants),
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


def send_to_filebeat(rooms: List[Dict[str, Any]], url: Optional[str], host_info: Dict[str, str], muc_api=None, service: str = "conference", insecure: bool = False, dry_run: bool = False) -> Dict[str, Any]:
    """
    Send room data to a Filebeat HTTP endpoint.
    
    Args:
        rooms: List of room dictionaries
        url: URL of the Filebeat HTTP endpoint
        host_info: Dictionary with hostname and server information
        muc_api: Optional MUC API client for fetching additional data
        service: Optional MUC service name
        insecure: Whether to disable SSL certificate validation
        dry_run: If True, only show the data that would be sent without actually sending it
        
    Returns:
        Dictionary with success and failure counts
    """
    results = {"success": 0, "failure": 0, "failed_rooms": []}
    
    for room in rooms:
        try:
            # Prepare the room data for Filebeat
            data = prepare_room_for_filebeat(room, host_info, muc_api, service)
            
            # In dry run mode, just print the data without sending
            if dry_run:
                click.echo(f"\nDRY RUN: Data that would be sent for room {room.get('roomName')}:")
                click.echo(json.dumps(data, indent=2))
                results["success"] += 1
                continue
            
            # For actual sending, URL must be provided
            if not url:
                # This should never happen due to earlier checks, but just in case
                click.echo(f"Error: Cannot send room {room.get('roomName')} - URL is required", err=True)
                results["failure"] += 1
                results["failed_rooms"].append(room.get("roomName"))
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
                results["failed_rooms"].append(room.get("roomName"))
                click.echo(f"Failed to send room {room.get('roomName')}: {response.status_code} {response.text}", err=True)
        except Exception as e:
            results["failure"] += 1
            results["failed_rooms"].append(room.get("roomName"))
            click.echo(f"Error sending room {room.get('roomName')}: {e}", err=True)
    
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
    "--service",
    default="conference",
    help="MUC service name (default: conference)",
    envvar="EXPORT_MUC_SERVICE",
)
@click.option(
    "--type",
    type=click.Choice(["public", "all"]),
    default="public",
    help="Type of rooms to list (public or all)",
    envvar="EXPORT_MUC_TYPE",
)
@click.option(
    "--insecure/--secure",
    default=False,
    help="Disable SSL certificate validation (for self-signed certificates)",
    envvar="EXPORT_MUC_INSECURE",
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
    envvar="EXPORT_MUC_DRY_RUN",
)
def export_muc(
    host: str,
    token: str,
    service: str,
    type: str,
    insecure: bool,
    url: Optional[str],
    dry_run: bool,
) -> None:
    """
    Export Openfire MUC (Multi-User Chat) rooms and send them to a Filebeat HTTP endpoint.
    
    This script connects to an Openfire server, retrieves MUC room data, and sends it
    to a Filebeat HTTP endpoint for further processing.
    
    Common command-line options can be provided via standardized environment variables:
      --host can be set with OPENFIRE_HOST
      --token can be set with OPENFIRE_TOKEN
      --url can be set with FILEBEAT_URL
    
    Script-specific options can be provided via environment variables with the
    prefix EXPORT_MUC_ followed by the option name in uppercase. For example:
      --service can be set with EXPORT_MUC_SERVICE
      --type can be set with EXPORT_MUC_TYPE
      --insecure can be set with EXPORT_MUC_INSECURE
      --dry-run can be set with EXPORT_MUC_DRY_RUN
    
    Boolean flags can be set with environment variables using true/false values.
    """
    try:
        # Handle SSL verification first, before any network clients are created
        if insecure:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            click.echo("Warning: SSL certificate validation is disabled", err=True)
        
        # Create MUC API client
        muc_api = Muc(host, token)
        
        # Set verify_ssl attribute directly
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
        
        # Get rooms with optional filtering
        result = muc_api.get_rooms(servicename=service, typeof=type)
        
        # Process the result based on its structure
        rooms_list = []
        if isinstance(result, dict) and 'chatRooms' in result:
            if isinstance(result['chatRooms'], list):
                rooms_list = result['chatRooms']
            elif isinstance(result['chatRooms'], dict) and 'chatRoom' in result['chatRooms']:
                rooms_list = result['chatRooms']['chatRoom']
        elif isinstance(result, list):
            rooms_list = result
        
        if not rooms_list:
            click.echo("No rooms found.", err=True)
            return
        
        # Add service name to each room for proper identification
        for room in rooms_list:
            if 'serviceName' not in room:
                room['serviceName'] = service
                
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
            
        results = send_to_filebeat(rooms_list, url, server_info, muc_api, service, insecure, dry_run)
        
        if dry_run:
            click.echo(f"DRY RUN: Would have sent {results['success']} rooms", err=True)
        else:
            click.echo(f"Sent {results['success']} rooms successfully, {results['failure']} failed", err=True)
            if results['failure'] > 0:
                click.echo(f"Failed rooms: {', '.join(results['failed_rooms'])}", err=True)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    export_muc()
