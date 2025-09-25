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


def transform_for_elasticsearch(rooms: List[Dict[str, Any]], index_name: str) -> List[Dict[str, Any]]:
    """
    Transform MUC room data into Elasticsearch bulk API format.
    
    Args:
        rooms: List of room dictionaries
        index_name: Name of the Elasticsearch index
        
    Returns:
        List of dictionaries in Elasticsearch bulk API format
    """
    bulk_data = []
    timestamp = datetime.now(timezone.utc).isoformat()
    
    for room in rooms:
        # Create the action/metadata line
        action = {
            "index": {
                "_index": index_name,
                "_id": f"{room.get('roomName')}@{room.get('serviceName', 'conference')}"
            }
        }
        bulk_data.append(action)
        
        # Process user roles
        owners = room.get("owners", [])
        admins = room.get("admins", [])
        members = room.get("members", [])
        outcasts = room.get("outcasts", [])
        
        # Handle different formats
        if isinstance(owners, dict) and "owner" in owners:
            owners = owners["owner"]
        if isinstance(admins, dict) and "admin" in admins:
            admins = admins["admin"]
        if isinstance(members, dict) and "member" in members:
            members = members["member"]
        if isinstance(outcasts, dict) and "outcast" in outcasts:
            outcasts = outcasts["outcast"]
            
        # Process group roles
        owner_groups = room.get("ownerGroups", [])
        admin_groups = room.get("adminGroups", [])
        member_groups = room.get("memberGroups", [])
        outcast_groups = room.get("outcastGroups", [])
        
        # Handle different formats
        if isinstance(owner_groups, dict) and "ownerGroup" in owner_groups:
            owner_groups = owner_groups["ownerGroup"]
        if isinstance(admin_groups, dict) and "adminGroup" in admin_groups:
            admin_groups = admin_groups["adminGroup"]
        if isinstance(member_groups, dict) and "memberGroup" in member_groups:
            member_groups = member_groups["memberGroup"]
        if isinstance(outcast_groups, dict) and "outcastGroup" in outcast_groups:
            outcast_groups = outcast_groups["outcastGroup"]
        
        # Create the document
        document = {
            "room_name": room.get("roomName"),
            "natural_name": room.get("naturalName"),
            "description": room.get("description"),
            "subject": room.get("subject"),
            "service_name": room.get("serviceName", "conference"),
            "creation_date": room.get("creationDate"),
            "modification_date": room.get("modificationDate"),
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
            "allow_pm": room.get("allowPM"),
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
            "@timestamp": timestamp,
            "doc_type": "openfire_muc_room"
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
    help="Output format: 'bulk' for Elasticsearch Bulk API, 'documents' for individual documents",
)
@click.option(
    "--file",
    help="Output file (if not specified, output to stdout)",
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
        # Create MUC API client
        muc_api = Muc(host, token)
        
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
            
        # Transform data for Elasticsearch
        if output == "bulk":
            es_data = transform_for_elasticsearch(rooms_list, index)
        else:  # documents
            timestamp = datetime.now(timezone.utc).isoformat()
            es_data = []
            
            for room in rooms_list:
                # Process user roles
                owners = room.get("owners", [])
                admins = room.get("admins", [])
                members = room.get("members", [])
                outcasts = room.get("outcasts", [])
                
                # Handle different formats
                if isinstance(owners, dict) and "owner" in owners:
                    owners = owners["owner"]
                if isinstance(admins, dict) and "admin" in admins:
                    admins = admins["admin"]
                if isinstance(members, dict) and "member" in members:
                    members = members["member"]
                if isinstance(outcasts, dict) and "outcast" in outcasts:
                    outcasts = outcasts["outcast"]
                    
                # Process group roles
                owner_groups = room.get("ownerGroups", [])
                admin_groups = room.get("adminGroups", [])
                member_groups = room.get("memberGroups", [])
                outcast_groups = room.get("outcastGroups", [])
                
                # Handle different formats
                if isinstance(owner_groups, dict) and "ownerGroup" in owner_groups:
                    owner_groups = owner_groups["ownerGroup"]
                if isinstance(admin_groups, dict) and "adminGroup" in admin_groups:
                    admin_groups = admin_groups["adminGroup"]
                if isinstance(member_groups, dict) and "memberGroup" in member_groups:
                    member_groups = member_groups["memberGroup"]
                if isinstance(outcast_groups, dict) and "outcastGroup" in outcast_groups:
                    outcast_groups = outcast_groups["outcastGroup"]
                
                # Create the document
                document = {
                    "_index": index,
                    "_id": f"{room.get('roomName')}@{room.get('serviceName', 'conference')}",
                    "_source": {
                        "room_name": room.get("roomName"),
                        "natural_name": room.get("naturalName"),
                        "description": room.get("description"),
                        "subject": room.get("subject"),
                        "service_name": room.get("serviceName", "conference"),
                        "creation_date": room.get("creationDate"),
                        "modification_date": room.get("modificationDate"),
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
                        "allow_pm": room.get("allowPM"),
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
                        "@timestamp": timestamp,
                        "doc_type": "openfire_muc_room"
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
    export_muc()
