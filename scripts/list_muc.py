#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to list all MUC (Multi-User Chat) rooms from an Openfire server using the ofrestapi library.
"""

import sys
import os
import json
import csv
import io
import click
from datetime import datetime, timezone

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
        
        # Convert Unix timestamps to ISO 8601 format
        for room in rooms_list:
            # Convert creationDate if it exists and is a number
            if "creationDate" in room and isinstance(room["creationDate"], (int, float)):
                # Convert milliseconds to seconds and format as ISO 8601
                creation_date = datetime.fromtimestamp(room["creationDate"] / 1000, tz=timezone.utc)
                room["creationDate"] = creation_date.isoformat()
            
            # Convert modificationDate if it exists and is a number
            if "modificationDate" in room and isinstance(room["modificationDate"], (int, float)):
                # Convert milliseconds to seconds and format as ISO 8601
                modification_date = datetime.fromtimestamp(room["modificationDate"] / 1000, tz=timezone.utc)
                room["modificationDate"] = modification_date.isoformat()
        
        # Display results in the requested format
        if output == "json":
            click.echo(json.dumps(rooms_list, indent=2))
        elif output == "csv":
            # Use StringIO and csv.writer for proper CSV formatting
            output_buffer = io.StringIO()
            csv_writer = csv.writer(output_buffer)
            
            if rooms_list:
                # Define headers
                headers = ["roomName", "naturalName", "description", "subject", "occupants", "persistent", "publicRoom"]
                
                # Add user columns if requested
                if show_users:
                    headers.extend(["owners", "admins", "members"])
                    
                # Write headers
                csv_writer.writerow(headers)
                
                # Write each room as a CSV row
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
                    
                    # Format user lists for CSV (using || as delimiter within cells)
                    owners_str = "||".join(owners) if owners else ""
                    admins_str = "||".join(admins) if admins else ""
                    members_str = "||".join(members) if members else ""
                    
                    # Build row values (no need to manually escape commas, quotes, etc.)
                    values = [
                        room.get("roomName", ""),
                        room.get("naturalName", ""),
                        room.get("description", ""),  # No need to replace commas
                        room.get("subject", ""),      # No need to replace commas
                        str(room.get("occupantsCount", 0)),
                        str(room.get("persistent", False)).lower(),
                        str(room.get("publicRoom", False)).lower()
                    ]
                    
                    # Add user columns if requested
                    if show_users:
                        values.extend([owners_str, admins_str, members_str])
                    
                    # Write the row
                    csv_writer.writerow(values)
                
                # Output the CSV data (removing trailing newline)
                click.echo(output_buffer.getvalue().rstrip())
        else:  # table format
            if not rooms_list:
                click.echo("No rooms found.")
                return
                
            # Determine column widths
            room_width = max(8, max((len(room.get("roomName", "")) for room in rooms_list), default=0))
            name_width = max(4, max((len(room.get("naturalName", "")) for room in rooms_list), default=0))
            desc_width = min(30, max(11, max((len(room.get("description", "")[:30]) for room in rooms_list), default=0)))
            
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
                    
                    # Print users by role (affiliations)
                    click.echo(f"  Users with affiliations in room '{room_name}':")
                    
                    if owners or admins or members:
                        if owners:
                            click.echo(f"    Owners: {', '.join(owners)}")
                        if admins:
                            click.echo(f"    Admins: {', '.join(admins)}")
                        if members:
                            click.echo(f"    Members: {', '.join(members)}")
                    else:
                        click.echo("    No affiliated users found")
                    
                    # Get current occupants in the room
                    try:
                        occupants_result = muc_api.get_room_users(room_name, service)
                        
                        # Process occupants based on the response structure
                        occupants_list = []
                        if isinstance(occupants_result, dict):
                            # Handle the 'participants' key which is used in the API response
                            if 'participants' in occupants_result:
                                if isinstance(occupants_result['participants'], list):
                                    occupants_list = occupants_result['participants']
                                # Handle single participant case (explicitly check for dict type)
                                elif isinstance(occupants_result['participants'], dict):
                                    occupants_list = [occupants_result['participants']]
                            # Also try the 'occupants' key for backward compatibility
                            elif 'occupants' in occupants_result:
                                if isinstance(occupants_result['occupants'], list):
                                    occupants_list = occupants_result['occupants']
                                elif isinstance(occupants_result['occupants'], dict) and 'occupant' in occupants_result['occupants']:
                                    occupants_list = occupants_result['occupants']['occupant']
                                    # Handle single occupant case (explicitly check for dict type)
                                    if isinstance(occupants_list, dict):
                                        occupants_list = [occupants_list]
                        
                        # Display current occupants
                        click.echo(f"  Current occupants in room '{room_name}':")
                        if occupants_list:
                            for occupant in occupants_list:
                                jid = occupant.get('jid', 'Unknown')
                                role = occupant.get('role', 'Unknown')
                                affiliation = occupant.get('affiliation', 'Unknown')
                                
                                # Extract nickname from JID if possible
                                nickname = 'Unknown'
                                if '/' in jid:
                                    nickname = jid.split('/')[-1]
                                elif occupant.get('nick'):
                                    nickname = occupant.get('nick')
                                
                                # Format: Nickname (JID) - Role (Affiliation)
                                role_info = f"{role}"
                                if affiliation and affiliation != 'none':
                                    role_info += f" ({affiliation})"
                                    
                                click.echo(f"    {nickname} - {role_info} - {jid}")
                        else:
                            click.echo("    No current occupants")
                    except Exception as e:
                        click.echo(f"    Error retrieving occupants: {e}")
                    
                    click.echo("")
            
            # Print summary
            click.echo(f"Total rooms: {len(rooms_list)}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    list_muc()
