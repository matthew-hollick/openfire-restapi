#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Basic usage example for the Openfire REST API client.
This script demonstrates how to use the client library to interact with an Openfire server.
"""

import os
import sys
import argparse

# Add parent directory to path to import ofrestapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ofrestapi import Users, Groups, System, Sessions, Messages, Muc


def load_credentials(creds_file):
    """Load credentials from a file."""
    creds = {}
    try:
        with open(creds_file, 'r') as f:
            for line in f:
                if ':' in line:
                    key, value = line.split(':', 1)
                    creds[key.strip()] = value.strip()
    except Exception as e:
        print(f"Error loading credentials: {e}")
        sys.exit(1)
    
    return creds


def main():
    parser = argparse.ArgumentParser(description='Openfire REST API client example')
    parser.add_argument('--host', default='https://localhost:9091', 
                        help='Openfire server host (default: https://localhost:9091)')
    parser.add_argument('--creds', default='../credentials.txt',
                        help='Path to credentials file (default: ../credentials.txt)')
    parser.add_argument('--insecure', action='store_true',
                        help='Disable SSL certificate validation')
    
    args = parser.parse_args()
    
    # Load credentials
    creds = load_credentials(args.creds)
    if 'restapi token' not in creds:
        print("Error: 'restapi token' not found in credentials file")
        sys.exit(1)
    
    secret = creds['restapi token']
    host = args.host
    
    print(f"Connecting to Openfire server at {host}")
    
    # If insecure flag is set, disable SSL warnings
    if args.insecure:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        print("Warning: SSL certificate validation is disabled")
        
        # Patch requests to not verify SSL
        import requests
        old_request = requests.Session.request
        def new_request(self, method, url, **kwargs):
            kwargs['verify'] = False
            return old_request(self, method, url, **kwargs)
        requests.Session.request = new_request
    
    # Initialize API clients
    users_api = Users(host, secret)
    groups_api = Groups(host, secret)
    system_api = System(host, secret)
    sessions_api = Sessions(host, secret)
    messages_api = Messages(host, secret)
    muc_api = Muc(host, secret)
    
    # Example 1: Get all users
    print("\n=== Example 1: Get all users ===")
    users = users_api.get_users()
    user_count = len(users.get('users', {}).get('user', []))
    print(f"Found {user_count} users:")
    for user in users.get('users', {}).get('user', [])[:5]:  # Show first 5 users
        print(f"- {user.get('username')}: {user.get('name')}")
    if user_count > 5:
        print(f"... and {user_count - 5} more")
    
    # Example 2: Get all groups
    print("\n=== Example 2: Get all groups ===")
    groups = groups_api.get_groups()
    group_count = len(groups.get('groups', {}).get('group', []))
    print(f"Found {group_count} groups:")
    for group in groups.get('groups', {}).get('group', []):
        print(f"- {group.get('name')}: {group.get('description')}")
    
    # Example 3: Get system properties
    print("\n=== Example 3: Get system properties ===")
    props = system_api.get_props()
    prop_count = len(props.get('properties', {}).get('property', []))
    print(f"Found {prop_count} system properties (showing first 5):")
    for prop in props.get('properties', {}).get('property', [])[:5]:
        print(f"- {prop.get('@key')}: {prop.get('@value')}")
    if prop_count > 5:
        print(f"... and {prop_count - 5} more")
    
    # Example 4: Get active sessions
    print("\n=== Example 4: Get active sessions ===")
    sessions = sessions_api.get_sessions()
    session_count = len(sessions.get('sessions', {}).get('session', []))
    print(f"Found {session_count} active sessions:")
    for session in sessions.get('sessions', {}).get('session', []):
        print(f"- {session.get('username')} from {session.get('hostAddress')}")
    
    # Example 5: Get chat rooms
    print("\n=== Example 5: Get chat rooms ===")
    rooms = muc_api.get_rooms()
    room_count = len(rooms.get('chatRooms', {}).get('chatRoom', []))
    print(f"Found {room_count} chat rooms:")
    for room in rooms.get('chatRooms', {}).get('chatRoom', []):
        print(f"- {room.get('roomName')}: {room.get('naturalName')}")
    
    # Example 6: Send a broadcast message
    print("\n=== Example 6: Send a broadcast message ===")
    message = "This is a test broadcast message from the example script"
    print(f"Sending message: '{message}'")
    try:
        result = messages_api.send_broadcast(message)
        print(f"Message sent successfully: {result}")
    except Exception as e:
        print(f"Failed to send message: {e}")
    
    print("\nExample script completed successfully!")


if __name__ == "__main__":
    main()
