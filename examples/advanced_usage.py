#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Advanced usage example for the Openfire REST API client.
This script demonstrates error handling, SSL certificate handling, and more complex operations.
"""

import os
import sys
import uuid
import argparse
import requests
from pprint import pprint

# Add parent directory to path to import ofrestapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ofrestapi import Users, Groups, Muc
from ofrestapi.exception import (
    OpenfireApiException, UserNotFoundException, UserAlreadyExistsException
)


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


def setup_ssl_handling(insecure=False):
    """Configure SSL certificate handling."""
    if insecure:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        print("Warning: SSL certificate validation is disabled")
        
        # Create a session with SSL verification disabled
        session = requests.Session()
        session.verify = False
        
        # Monkey patch the requests module to use our session
        old_request = requests.Session.request
        def new_request(self, method, url, **kwargs):
            kwargs['verify'] = False
            return old_request(self, method, url, **kwargs)
        requests.Session.request = new_request
    else:
        print("SSL certificate validation is enabled")


def example_error_handling(host, secret):
    """Demonstrate error handling with the API."""
    print("\n=== Example: Error Handling ===")
    users_api = Users(host, secret)
    
    # Try to get a non-existent user
    non_existent_user = f"nonexistent_{uuid.uuid4().hex[:8]}"
    print(f"Attempting to get non-existent user: {non_existent_user}")
    try:
        user = users_api.get_user(non_existent_user)
        print("User found (unexpected):", user)
    except UserNotFoundException as e:
        print(f"Expected error caught: {e.__class__.__name__}: {e}")
    except OpenfireApiException as e:
        print(f"Openfire API error: {e.__class__.__name__}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e.__class__.__name__}: {e}")
    
    # Try to create a user and then create it again (should fail)
    test_user = f"testuser_{uuid.uuid4().hex[:8]}"
    print(f"\nAttempting to create user: {test_user}")
    try:
        users_api.add_user(
            username=test_user,
            password="TestPassword123",
            name="Test User",
            email=f"{test_user}@example.com"
        )
        print(f"User {test_user} created successfully")
        
        print("Attempting to create the same user again (should fail)")
        users_api.add_user(
            username=test_user,
            password="TestPassword123",
            name="Test User",
            email=f"{test_user}@example.com"
        )
        print("User created again (unexpected)")
    except UserAlreadyExistsException as e:
        print(f"Expected error caught: {e.__class__.__name__}: {e}")
    except OpenfireApiException as e:
        print(f"Openfire API error: {e.__class__.__name__}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e.__class__.__name__}: {e}")
    finally:
        # Clean up - delete the test user
        try:
            users_api.delete_user(test_user)
            print(f"Cleanup: User {test_user} deleted")
        except Exception as e:
            print(f"Cleanup error: {e}")


def example_user_management(host, secret):
    """Demonstrate user management operations."""
    print("\n=== Example: User Management ===")
    users_api = Users(host, secret)
    
    # Create a test user with properties
    test_user = f"testuser_{uuid.uuid4().hex[:8]}"
    print(f"Creating user: {test_user}")
    
    try:
        # Create user with custom properties
        users_api.add_user(
            username=test_user,
            password="TestPassword123",
            name="Test User",
            email=f"{test_user}@example.com",
            props={
                "title": "Software Engineer",
                "department": "Engineering",
                "location": "Remote"
            }
        )
        print(f"User {test_user} created successfully")
        
        # Get the user details
        user = users_api.get_user(test_user)
        print("User details:")
        pprint(user)
        
        # Update the user
        print(f"\nUpdating user: {test_user}")
        users_api.update_user(
            username=test_user,
            name="Updated Test User",
            email=f"updated_{test_user}@example.com",
            props={
                "title": "Senior Software Engineer",
                "department": "Engineering",
                "location": "Remote",
                "start_date": "2025-09-25"
            }
        )
        print(f"User {test_user} updated successfully")
        
        # Get the updated user details
        user = users_api.get_user(test_user)
        print("Updated user details:")
        pprint(user)
    finally:
        # Clean up - delete the test user
        try:
            users_api.delete_user(test_user)
            print(f"Cleanup: User {test_user} deleted")
        except Exception as e:
            print(f"Cleanup error: {e}")


def example_group_management(host, secret):
    """Demonstrate group management operations."""
    print("\n=== Example: Group Management ===")
    groups_api = Groups(host, secret)
    users_api = Users(host, secret)
    
    # Create test users and groups
    test_group = f"testgroup_{uuid.uuid4().hex[:8]}"
    test_users = [f"testuser_{uuid.uuid4().hex[:8]}" for _ in range(3)]
    
    try:
        # Create test users
        for i, username in enumerate(test_users):
            users_api.add_user(
                username=username,
                password="TestPassword123",
                name=f"Test User {i+1}",
                email=f"{username}@example.com"
            )
            print(f"Created test user: {username}")
        
        # Create a group
        print(f"\nCreating group: {test_group}")
        groups_api.add_group(
            groupname=test_group,
            description="Test Group for API Example"
        )
        print(f"Group {test_group} created successfully")
        
        # Add users to the group
        print(f"Adding users to group: {test_group}")
        for username in test_users:
            users_api.add_user_groups(username, [test_group])
            print(f"Added user {username} to group {test_group}")
        
        # Get group details
        group = groups_api.get_group(test_group)
        print("\nGroup details:")
        pprint(group)
        
        # Get users in group
        for username in test_users:
            user_groups = users_api.get_user_groups(username)
            print(f"Groups for user {username}:")
            pprint(user_groups)
        
        # Update the group
        print(f"\nUpdating group: {test_group}")
        groups_api.update_group(
            groupname=test_group,
            description="Updated Test Group Description"
        )
        print(f"Group {test_group} updated successfully")
        
        # Get updated group details
        group = groups_api.get_group(test_group)
        print("Updated group details:")
        pprint(group)
        
        # Remove a user from the group
        print(f"\nRemoving user {test_users[0]} from group {test_group}")
        users_api.delete_user_groups(test_users[0], [test_group])
        print(f"User {test_users[0]} removed from group {test_group}")
        
        # Verify removal
        user_groups = users_api.get_user_groups(test_users[0])
        print(f"Groups for user {test_users[0]} after removal:")
        pprint(user_groups)
    finally:
        # Clean up - delete the test group and users
        try:
            groups_api.delete_group(test_group)
            print(f"Cleanup: Group {test_group} deleted")
        except Exception as e:
            print(f"Cleanup error (group): {e}")
        
        for username in test_users:
            try:
                users_api.delete_user(username)
                print(f"Cleanup: User {username} deleted")
            except Exception as e:
                print(f"Cleanup error (user {username}): {e}")


def example_muc_management(host, secret):
    """Demonstrate MUC (chat room) management operations."""
    print("\n=== Example: MUC Management ===")
    muc_api = Muc(host, secret)
    users_api = Users(host, secret)
    
    # Create test room and users
    test_room = f"testroom_{uuid.uuid4().hex[:8]}"
    test_users = [f"testuser_{uuid.uuid4().hex[:8]}" for _ in range(2)]
    
    try:
        # Create test users
        for i, username in enumerate(test_users):
            users_api.add_user(
                username=username,
                password="TestPassword123",
                name=f"Test User {i+1}",
                email=f"{username}@example.com"
            )
            print(f"Created test user: {username}")
        
        # Create a chat room
        print(f"\nCreating chat room: {test_room}")
        muc_api.add_room(
            roomname=test_room,
            name=f"Test Room {test_room}",
            description="Test Room for API Example",
            persistent=True,
            public=True,
            maxusers=25,
            owners=[test_users[0]]
        )
        print(f"Chat room {test_room} created successfully")
        
        # Get room details
        room = muc_api.get_room(test_room)
        print("\nRoom details:")
        pprint(room)
        
        # Update the room
        print(f"\nUpdating room: {test_room}")
        muc_api.update_room(
            roomname=test_room,
            description="Updated Test Room Description",
            maxusers=50,
            admins=[test_users[1]]
        )
        print(f"Room {test_room} updated successfully")
        
        # Get updated room details
        room = muc_api.get_room(test_room)
        print("Updated room details:")
        pprint(room)
        
        # Grant and revoke user roles
        print(f"\nGranting 'members' role to user {test_users[1]}")
        muc_api.grant_user_role(test_room, test_users[1], "members")
        print("Role granted successfully")
        
        print(f"Revoking 'members' role from user {test_users[1]}")
        muc_api.revoke_user_role(test_room, test_users[1], "members")
        print("Role revoked successfully")
    finally:
        # Clean up - delete the test room and users
        try:
            muc_api.delete_room(test_room)
            print(f"Cleanup: Room {test_room} deleted")
        except Exception as e:
            print(f"Cleanup error (room): {e}")
        
        for username in test_users:
            try:
                users_api.delete_user(username)
                print(f"Cleanup: User {username} deleted")
            except Exception as e:
                print(f"Cleanup error (user {username}): {e}")


def main():
    parser = argparse.ArgumentParser(description='Openfire REST API advanced examples')
    parser.add_argument('--host', default='https://localhost:9091', 
                        help='Openfire server host (default: https://localhost:9091)')
    parser.add_argument('--creds', default='../credentials.txt',
                        help='Path to credentials file (default: ../credentials.txt)')
    parser.add_argument('--insecure', action='store_true',
                        help='Disable SSL certificate validation')
    parser.add_argument('--example', choices=['all', 'error', 'user', 'group', 'muc'],
                        default='all', help='Which example to run (default: all)')
    
    args = parser.parse_args()
    
    # Load credentials
    creds = load_credentials(args.creds)
    if 'restapi token' not in creds:
        print("Error: 'restapi token' not found in credentials file")
        sys.exit(1)
    
    secret = creds['restapi token']
    host = args.host
    
    print(f"Connecting to Openfire server at {host}")
    
    # Configure SSL handling
    setup_ssl_handling(args.insecure)
    
    # Run the selected examples
    if args.example in ['all', 'error']:
        example_error_handling(host, secret)
    
    if args.example in ['all', 'user']:
        example_user_management(host, secret)
    
    if args.example in ['all', 'group']:
        example_group_management(host, secret)
    
    if args.example in ['all', 'muc']:
        example_muc_management(host, secret)
    
    print("\nAll examples completed!")


if __name__ == "__main__":
    main()
