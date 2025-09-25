#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for testing the client against a local Openfire server.
This script performs actual API operations against a running Openfire server.
"""

import os
import sys
import uuid
import argparse
import requests
from typing import Dict

# Add parent directory to path to import ofrestapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ofrestapi import Users, Groups, System, Sessions, Messages, Muc


def load_credentials(creds_file: str) -> Dict[str, str]:
    """
    Load credentials from a file.
    
    Args:
        creds_file: Path to credentials file
        
    Returns:
        Dictionary with credentials
    """
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


class TestResult:
    """Class to track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
    
    def add_pass(self):
        self.passed += 1
        print("✅ PASS")
    
    def add_fail(self, error: str):
        self.failed += 1
        print(f"❌ FAIL: {error}")
    
    def add_skip(self, reason: str):
        self.skipped += 1
        print(f"⏭️ SKIP: {reason}")
    
    def summary(self):
        total = self.passed + self.failed + self.skipped
        print("\n=== Test Summary ===")
        print(f"Passed: {self.passed}/{total}")
        print(f"Failed: {self.failed}/{total}")
        print(f"Skipped: {self.skipped}/{total}")
        
        if self.failed == 0:
            print("All executed tests passed successfully!")
            return True
        else:
            print("Some tests failed.")
            return False


def test_users_api(host: str, secret: str, result: TestResult) -> None:
    """
    Test the Users API with actual operations.
    
    Args:
        host: Openfire server host
        secret: API secret key
        result: TestResult object to track results
    """
    print("\n=== Testing Users API ===")
    users_api = Users(host, secret)
    
    # Test 1: Get all users
    print("\nTest: Get all users")
    try:
        users = users_api.get_users()
        
        # Handle different response formats
        if isinstance(users, dict):
            # Handle dictionary response
            if 'users' in users:
                if isinstance(users['users'], list):
                    # Format: {"users": [{user1}, {user2}, ...]}
                    users_count = len(users['users'])
                elif isinstance(users['users'], dict) and 'user' in users['users']:
                    # Format: {"users": {"user": [{user1}, {user2}, ...]}}
                    users_count = len(users['users']['user'])
                else:
                    users_count = 0
            else:
                users_count = 0
        elif isinstance(users, list):
            # Handle list response
            users_count = len(users)
        else:
            users_count = 0
            
        print(f"Retrieved {users_count} users")
        result.add_pass()
    except Exception as e:
        result.add_fail(str(e))
    
    # Test 2: Create a new user
    test_username = f"testuser_{uuid.uuid4().hex[:8]}"
    print(f"\nTest: Create user '{test_username}'")
    try:
        success = users_api.add_user(
            username=test_username,
            password="TestPassword123",
            name="Test User",
            email=f"{test_username}@example.com",
            props={"testprop": "testvalue"}
        )
        if success:
            result.add_pass()
        else:
            result.add_fail("Failed to create user")
    except Exception as e:
        result.add_fail(str(e))
    
    # Test 3: Get specific user (using existing admin user)
    existing_username = "admin"
    print(f"\nTest: Get user '{existing_username}'")
    try:
        user = users_api.get_user(existing_username)
        if user and user.get('username') == existing_username:
            result.add_pass()
        else:
            result.add_fail("User data doesn't match")
    except Exception as e:
        result.add_fail(str(e))
    
    # Test 4: Update user
    print(f"\nTest: Update user '{test_username}'")
    try:
        success = users_api.update_user(
            username=test_username,
            name="Updated Test User",
            email=f"updated_{test_username}@example.com"
        )
        if success:
            result.add_pass()
        else:
            result.add_fail("Failed to update user")
    except Exception as e:
        result.add_fail(str(e))
    
    # Test 5: Delete user
    print(f"\nTest: Delete user '{test_username}'")
    try:
        success = users_api.delete_user(test_username)
        if success:
            result.add_pass()
        else:
            result.add_fail("Failed to delete user")
    except Exception as e:
        result.add_fail(str(e))


def test_groups_api(host: str, secret: str, result: TestResult) -> None:
    """
    Test the Groups API with actual operations.
    
    Args:
        host: Openfire server host
        secret: API secret key
        result: TestResult object to track results
    """
    print("\n=== Testing Groups API ===")
    groups_api = Groups(host, secret)
    
    # Test 1: Get all groups
    print("\nTest: Get all groups")
    try:
        groups = groups_api.get_groups()
        
        # Handle different response formats
        if isinstance(groups, dict):
            # Handle dictionary response
            if 'groups' in groups:
                if isinstance(groups['groups'], list):
                    # Format: {"groups": [{group1}, {group2}, ...]}
                    groups_count = len(groups['groups'])
                elif isinstance(groups['groups'], dict) and 'group' in groups['groups']:
                    # Format: {"groups": {"group": [{group1}, {group2}, ...]}}
                    groups_count = len(groups['groups']['group'])
                else:
                    groups_count = 0
            else:
                groups_count = 0
        elif isinstance(groups, list):
            # Handle list response
            groups_count = len(groups)
        else:
            groups_count = 0
            
        print(f"Retrieved {groups_count} groups")
        result.add_pass()
    except Exception as e:
        result.add_fail(str(e))
    
    # Test 2: Create a new group
    test_groupname = f"testgroup_{uuid.uuid4().hex[:8]}"
    print(f"\nTest: Create group '{test_groupname}'")
    try:
        success = groups_api.add_group(
            groupname=test_groupname,
            description="Test Group Description"
        )
        if success:
            result.add_pass()
        else:
            result.add_fail("Failed to create group")
    except Exception as e:
        result.add_fail(str(e))
    
    # Test 3: Get specific group (using existing group)
    existing_groupname = "this is a test group"
    print(f"\nTest: Get group '{existing_groupname}'")
    try:
        group = groups_api.get_group(existing_groupname)
        if group and group.get('name') == existing_groupname:
            result.add_pass()
        else:
            result.add_fail("Group data doesn't match")
    except Exception as e:
        result.add_fail(str(e))
    
    # Test 4: Update group
    print(f"\nTest: Update group '{test_groupname}'")
    try:
        success = groups_api.update_group(
            groupname=test_groupname,
            description="Updated Test Group Description"
        )
        if success:
            result.add_pass()
        else:
            result.add_fail("Failed to update group")
    except Exception as e:
        result.add_fail(str(e))
    
    # Test 5: Delete group
    print(f"\nTest: Delete group '{test_groupname}'")
    try:
        success = groups_api.delete_group(test_groupname)
        if success:
            result.add_pass()
        else:
            result.add_fail("Failed to delete group")
    except Exception as e:
        result.add_fail(str(e))


def test_muc_api(host: str, secret: str, result: TestResult) -> None:
    """
    Test the MUC API with actual operations.
    
    Args:
        host: Openfire server host
        secret: API secret key
        result: TestResult object to track results
    """
    print("\n=== Testing MUC API ===")
    muc_api = Muc(host, secret)
    
    # Test 1: Get all rooms
    print("\nTest: Get all rooms")
    try:
        rooms = muc_api.get_rooms()
        
        # Handle different response formats
        if isinstance(rooms, dict):
            if 'chatRooms' in rooms:
                if isinstance(rooms['chatRooms'], dict) and 'chatRoom' in rooms['chatRooms']:
                    room_count = len(rooms['chatRooms']['chatRoom'])
                elif isinstance(rooms['chatRooms'], list):
                    room_count = len(rooms['chatRooms'])
                else:
                    room_count = 0
            else:
                room_count = 0
        elif isinstance(rooms, list):
            room_count = len(rooms)
        else:
            room_count = 0
            
        print(f"Retrieved {room_count} rooms")
        result.add_pass()
    except Exception as e:
        result.add_fail(str(e))
    
    # Test 2: Create a new room
    test_roomname = f"testroom_{uuid.uuid4().hex[:8]}"
    print(f"\nTest: Create room '{test_roomname}'")
    try:
        success = muc_api.add_room(
            roomname=test_roomname,
            name=f"Test Room {test_roomname}",
            description="Test Room Description",
            persistent=True,
            public=True
        )
        if success:
            result.add_pass()
        else:
            result.add_fail("Failed to create room")
    except Exception as e:
        result.add_fail(str(e))
    
    # Test 3: Get specific room (using existing room)
    existing_roomname = "thisroom"
    print(f"\nTest: Get room '{existing_roomname}'")
    try:
        room = muc_api.get_room(existing_roomname)
        if room and room.get('roomName') == existing_roomname:
            result.add_pass()
        else:
            result.add_fail("Room data doesn't match")
    except Exception as e:
        result.add_fail(str(e))
    
    # Test 4: Update room
    print(f"\nTest: Update room '{test_roomname}'")
    try:
        success = muc_api.update_room(
            roomname=test_roomname,
            description="Updated Test Room Description",
            maxusers=25
        )
        if success:
            result.add_pass()
        else:
            result.add_fail("Failed to update room")
    except Exception as e:
        result.add_fail(str(e))
    
    # Test 5: Delete room
    print(f"\nTest: Delete room '{test_roomname}'")
    try:
        success = muc_api.delete_room(test_roomname)
        if success:
            result.add_pass()
        else:
            result.add_fail("Failed to delete room")
    except Exception as e:
        result.add_fail(str(e))


def test_system_api(host: str, secret: str, result: TestResult) -> None:
    """
    Test the System API with actual operations.
    
    Args:
        host: Openfire server host
        secret: API secret key
        result: TestResult object to track results
    """
    print("\n=== Testing System API ===")
    system_api = System(host, secret)
    
    # Test 1: Get all system properties
    print("\nTest: Get all system properties")
    try:
        props = system_api.get_props()
        prop_count = len(props.get('properties', {}).get('property', []))
        print(f"Retrieved {prop_count} system properties")
        result.add_pass()
    except Exception as e:
        result.add_fail(str(e))
    
    # Test 2: Create/update a system property
    test_prop_key = f"test.property.{uuid.uuid4().hex[:8]}"
    test_prop_value = f"test_value_{uuid.uuid4().hex[:8]}"
    print(f"\nTest: Create/update system property '{test_prop_key}'")
    try:
        success = system_api.update_prop(test_prop_key, test_prop_value)
        if success:
            result.add_pass()
        else:
            result.add_fail("Failed to create/update system property")
    except Exception as e:
        result.add_fail(str(e))
    
    # Test 3: Get specific system property (using existing property)
    existing_prop_key = "xmpp.domain"
    print(f"\nTest: Get system property '{existing_prop_key}'")
    try:
        prop = system_api.get_prop(existing_prop_key)
        if prop and prop.get('@key') == existing_prop_key:
            result.add_pass()
        else:
            result.add_fail("Property data doesn't match")
    except Exception as e:
        result.add_fail(str(e))
    
    # Test 4: Delete system property
    print(f"\nTest: Delete system property '{test_prop_key}'")
    try:
        success = system_api.delete_prop(test_prop_key)
        if success:
            result.add_pass()
        else:
            result.add_fail("Failed to delete system property")
    except Exception as e:
        result.add_fail(str(e))
    
    # Test 5: Get concurrent sessions
    print("\nTest: Get concurrent sessions")
    try:
        system_api.get_concurrent_sessions()
        print("Retrieved concurrent sessions information")
        result.add_pass()
    except Exception as e:
        result.add_fail(str(e))


def test_sessions_api(host: str, secret: str, result: TestResult) -> None:
    """
    Test the Sessions API with actual operations.
    
    Args:
        host: Openfire server host
        secret: API secret key
        result: TestResult object to track results
    """
    print("\n=== Testing Sessions API ===")
    sessions_api = Sessions(host, secret)
    
    # Test 1: Get all sessions
    print("\nTest: Get all sessions")
    try:
        sessions = sessions_api.get_sessions()
        
        # Handle different response formats
        if isinstance(sessions, dict):
            if 'sessions' in sessions:
                if isinstance(sessions['sessions'], dict) and 'session' in sessions['sessions']:
                    session_count = len(sessions['sessions']['session'])
                elif isinstance(sessions['sessions'], list):
                    session_count = len(sessions['sessions'])
                else:
                    session_count = 0
            else:
                session_count = 0
        elif isinstance(sessions, list):
            session_count = len(sessions)
        else:
            session_count = 0
            
        print(f"Retrieved {session_count} sessions")
        result.add_pass()
    except Exception as e:
        result.add_fail(str(e))
    
    # For the remaining tests, we need an active user session
    print("\nTest: Get user sessions")
    result.add_skip("Requires an active user session")
    
    print("\nTest: Close user sessions")
    result.add_skip("Requires an active user session")


def test_messages_api(host: str, secret: str, result: TestResult) -> None:
    """
    Test the Messages API with actual operations.
    
    Args:
        host: Openfire server host
        secret: API secret key
        result: TestResult object to track results
    """
    print("\n=== Testing Messages API ===")
    messages_api = Messages(host, secret)
    
    # Test 1: Send broadcast message
    print("\nTest: Send broadcast message")
    try:
        success = messages_api.send_broadcast(f"Test broadcast message from API test {uuid.uuid4().hex[:8]}")
        if success:
            result.add_pass()
        else:
            result.add_fail("Failed to send broadcast message")
    except Exception as e:
        result.add_fail(str(e))
    
    # Test 2: Get unread messages
    # This requires a valid JID with unread messages, so we'll skip it
    print("\nTest: Get unread messages")
    result.add_skip("Requires a valid JID with unread messages")


def main():
    parser = argparse.ArgumentParser(description='Test Openfire REST API against local server')
    parser.add_argument('--host', default='https://localhost:9091', 
                        help='Openfire server host (default: https://localhost:9091)')
    parser.add_argument('--creds', default='credentials.txt',
                        help='Path to credentials file (default: credentials.txt)')
    parser.add_argument('--insecure', action='store_true',
                        help='Disable SSL certificate validation')
    parser.add_argument('--tests', default='all',
                        help='Comma-separated list of tests to run (users,groups,system,sessions,messages,muc)')
    
    args = parser.parse_args()
    
    # Load credentials
    creds = load_credentials(args.creds)
    if 'restapi token' not in creds:
        print("Error: 'restapi token' not found in credentials file")
        sys.exit(1)
    
    secret = creds['restapi token']
    host = args.host
    
    print(f"Testing connection to Openfire server at {host}")
    print(f"Using API token: {secret}")
    
    # If insecure flag is set, disable SSL warnings
    if args.insecure:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        print("Warning: SSL certificate validation is disabled")
        
        # Patch requests to not verify SSL
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
    
    # Parse tests to run
    tests_to_run = args.tests.split(',') if args.tests != 'all' else ['users', 'groups', 'system', 'sessions', 'messages', 'muc']
    
    # Create test result tracker
    result = TestResult()
    
    # Run tests
    if 'users' in tests_to_run:
        test_users_api(host, secret, result)
    
    if 'groups' in tests_to_run:
        test_groups_api(host, secret, result)
    
    if 'system' in tests_to_run:
        test_system_api(host, secret, result)
    
    if 'sessions' in tests_to_run:
        test_sessions_api(host, secret, result)
    
    if 'messages' in tests_to_run:
        test_messages_api(host, secret, result)
    
    if 'muc' in tests_to_run:
        test_muc_api(host, secret, result)
    
    # Print summary
    success = result.summary()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
