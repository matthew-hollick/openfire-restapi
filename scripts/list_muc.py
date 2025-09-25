#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to list all MUC (Multi-User Chat) rooms from an Openfire server using the ofrestapi library.
"""

import sys
import os
import json
import click

# Add parent directory to path to import ofrestapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ofrestapi import Muc


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
    "--output",
    type=click.Choice(["json", "table", "csv"]),
    default="table",
    help="Output format",
)
@click.option(
    "--show-users/--no-show-users",
    default=False,
    help="Show users in each room",
)
def list_muc(host: str, token: str, service: str, type: str, insecure: bool, output: str, show_users: bool) -> None:
    """
    List all MUC (Multi-User Chat) rooms from the Openfire server.
    
    This script connects to an Openfire server and retrieves a list of all MUC rooms,
    with optional filtering by service name and room type.
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
        
        # Display results in the requested format
        if output == "json":
            click.echo(json.dumps(rooms_list, indent=2))
        elif output == "csv":
            # Print CSV header
            if rooms_list:
                headers = ["roomName", "naturalName", "description", "subject", "occupants", "persistent", "publicRoom"]
                
                # Add user columns if requested
                if show_users:
                    headers.extend(["owners", "admins", "members"])
                    
                click.echo(",".join(headers))
                
                # Print each room as a CSV row
                for room in rooms_list:
                    # Get users from different roles
                    owners = room.get("owners", [])
                    admins = room.get("admins", [])
                    members = room.get("members", [])
                    
                    # Handle different formats
                    if isinstance(owners, dict) and "owner" in owners:
                        owners = owners["owner"]
                    if isinstance(admins, dict) and "admin" in admins:
                        admins = admins["admin"]
                    if isinstance(members, dict) and "member" in members:
                        members = members["member"]
                    
                    # Format user lists for CSV
                    owners_str = "||".join(owners) if owners else ""
                    admins_str = "||".join(admins) if admins else ""
                    members_str = "||".join(members) if members else ""
                    
                    values = [
                        room.get("roomName", ""),
                        room.get("naturalName", ""),
                        room.get("description", "").replace(",", " "),  # Remove commas from description
                        room.get("subject", "").replace(",", " "),      # Remove commas from subject
                        str(room.get("occupantsCount", 0)),
                        str(room.get("persistent", False)).lower(),
                        str(room.get("publicRoom", False)).lower()
                    ]
                    
                    # Add user columns if requested
                    if show_users:
                        values.extend([owners_str, admins_str, members_str])
                        
                    click.echo(",".join(values))
        else:  # table format
            if not rooms_list:
                click.echo("No rooms found.")
                return
                
            # Determine column widths
            room_width = max(8, max(len(room.get("roomName", "")) for room in rooms_list))
            name_width = max(4, max(len(room.get("naturalName", "")) for room in rooms_list))
            desc_width = min(30, max(11, max(len(room.get("description", "")[:30]) for room in rooms_list)))
            
            # Print table header
            click.echo(f"{'ROOM NAME':<{room_width}} | {'NATURAL NAME':<{name_width}} | {'DESCRIPTION':<{desc_width}} | {'OCCUPANTS':<9} | {'PUBLIC':<6} | {'PERSISTENT':<10}")
            click.echo(f"{'-' * room_width} | {'-' * name_width} | {'-' * desc_width} | {'-' * 9} | {'-' * 6} | {'-' * 10}")
            
            # Print each room
            for room in rooms_list:
                room_name = room.get("roomName", "")
                natural_name = room.get("naturalName", "")
                description = room.get("description", "")
                if len(description) > desc_width:
                    description = description[:desc_width-3] + "..."
                occupants = room.get("occupantsCount", 0)
                public = "Yes" if room.get("publicRoom", False) else "No"
                persistent = "Yes" if room.get("persistent", False) else "No"
                
                click.echo(f"{room_name:<{room_width}} | {natural_name:<{name_width}} | {description:<{desc_width}} | {occupants:<9} | {public:<6} | {persistent:<10}")
                
                # Show users if requested
                if show_users:
                    # Get users from different roles
                    owners = room.get("owners", [])
                    admins = room.get("admins", [])
                    members = room.get("members", [])
                    
                    # Handle different formats
                    if isinstance(owners, dict) and "owner" in owners:
                        owners = owners["owner"]
                    if isinstance(admins, dict) and "admin" in admins:
                        admins = admins["admin"]
                    if isinstance(members, dict) and "member" in members:
                        members = members["member"]
                    
                    # Print users by role
                    if owners or admins or members:
                        click.echo(f"  Users in room '{room_name}':")
                        
                        if owners:
                            click.echo(f"    Owners: {', '.join(owners)}")
                        if admins:
                            click.echo(f"    Admins: {', '.join(admins)}")
                        if members:
                            click.echo(f"    Members: {', '.join(members)}")
                        
                        if not (owners or admins or members):
                            click.echo("    No users found")
                        
                        click.echo("")
            
            # Print summary
            click.echo(f"Total rooms: {len(rooms_list)}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    list_muc()
