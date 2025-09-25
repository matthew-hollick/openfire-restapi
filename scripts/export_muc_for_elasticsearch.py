#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to export Openfire MUC (Multi-User Chat) rooms in a format suitable for Elasticsearch ingestion.
"""

import sys
import os
import json
import click
from datetime import datetime, timezone
from typing import Dict, Any, List

# Add parent directory to path to import ofrestapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ofrestapi import Muc


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
            # Handle single participant case
            elif not isinstance(occupants_data['participants'], list) and occupants_data['participants']:
                occupants_list = [occupants_data['participants']]
        # Also try the 'occupants' key for backward compatibility
        elif 'occupants' in occupants_data:
            if isinstance(occupants_data['occupants'], list):
                occupants_list = occupants_data['occupants']
            elif isinstance(occupants_data['occupants'], dict) and 'occupant' in occupants_data['occupants']:
                occupants_list = occupants_data['occupants']['occupant']
                # Handle single occupant case
                if not isinstance(occupants_list, list):
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


def _create_document_source(room: Dict[str, Any], timestamp: str, muc_api=None, service: str = "conference") -> Dict[str, Any]:
    """
    Transform a room dictionary into an Elasticsearch document source.
    
    Args:
        room: Room dictionary
        timestamp: ISO-formatted timestamp string
        muc_api: Optional MUC API client for fetching additional data
        service: Optional MUC service name
        
    Returns:
        Dictionary containing the document source
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
    
    # Create the document source
    return {
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
        "@timestamp": timestamp,
        "doc_type": "openfire_muc_room"
    }


def transform_for_elasticsearch(rooms: List[Dict[str, Any]], index: str, muc_api=None, service: str = "conference") -> List[Dict[str, Any]]:
    """
    Transform a list of rooms into Elasticsearch bulk API format.
    
    Args:
        rooms: List of room dictionaries
        index: Elasticsearch index name
        muc_api: Optional MUC API client for fetching additional data
        service: Optional MUC service name
        
    Returns:
        List of dictionaries in Elasticsearch bulk API format
    """
    bulk_data = []
    timestamp = datetime.now(timezone.utc).isoformat()
    
    for room in rooms:
        # Create the action/metadata line
        action = {
            "index": {
                "_index": index,
                "_id": f"{room.get('roomName')}@{room.get('serviceName', 'conference')}"
            }
        }
        bulk_data.append(action)
        
        # Create the document using the helper function
        document = _create_document_source(room, timestamp, muc_api, service)
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
    "--service",
    default="conference",
    help="MUC service name (default: conference)",
)
@click.option(
    "--type",
    type=click.Choice(["public", "all"]),
    default="public",
    help="Type of rooms to list (public or all)",
)
@click.option(
    "--insecure/--secure",
    default=False,
    help="Disable SSL certificate validation (for self-signed certificates)",
)
@click.option(
    "--index",
    default="openfire_muc_rooms",
    help="Elasticsearch index name",
)
@click.option(
    "--output",
    type=click.Choice(["bulk", "documents"]),
    default="bulk",
    help="Output format (bulk for Elasticsearch bulk API, documents for individual documents)",
)
@click.option(
    "--file",
    help="Output file path (optional, defaults to stdout)",
)
def export_muc(
    host: str,
    token: str,
    service: str,
    type: str,
    insecure: bool,
    index: str,
    output: str,
    file: str,
) -> None:
    """
    Export Openfire MUC (Multi-User Chat) rooms in a format suitable for Elasticsearch ingestion.
    
    This script connects to an Openfire server, retrieves MUC room data, and formats it
    for easy ingestion into Elasticsearch.
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
                
        # Get occupant counts for each room
        for room in rooms_list:
            room_name = room.get("roomName", "")
            try:
                occupants_result = muc_api.get_room_users(room_name, service)
                occupant_count = 0
                
                if isinstance(occupants_result, dict) and 'participants' in occupants_result:
                    if isinstance(occupants_result['participants'], list):
                        occupant_count = len(occupants_result['participants'])
                    elif occupants_result['participants']:  # Single occupant
                        occupant_count = 1
                        
                room["occupantsCount"] = occupant_count
            except Exception:
                # If there's an error, leave the default occupantsCount (usually 0)
                pass
        
        # Format the output based on the requested format
        if output == "bulk":
            es_data = transform_for_elasticsearch(rooms_list, index, muc_api, service)
        else:  # documents
            timestamp = datetime.now(timezone.utc).isoformat()
            es_data = []
            
            for room in rooms_list:
                document = {
                    "_index": index,
                    "_id": f"{room.get('roomName')}@{room.get('serviceName', 'conference')}",
                    "_source": _create_document_source(room, timestamp, muc_api, service)
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
    export_muc()
