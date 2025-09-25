#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for verifying connection to Openfire server.
This script tests basic connectivity and authentication with the Openfire server.
"""

import os
import sys
import argparse
from typing import Dict

# Add parent directory to path to import ofrestapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ofrestapi import Users, Groups, System, Sessions, Muc


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


def test_users_api(host: str, secret: str) -> bool:
    """
    Test the Users API.
    
    Args:
        host: Openfire server host
        secret: API secret key
        verify_ssl: Whether to verify SSL certificates
        
    Returns:
        True if successful
    """
    print("\n=== Testing Users API ===")
    try:
        users_api = Users(host, secret)
        result = users_api.get_users()
        
        # Handle different response formats
        if isinstance(result, dict):
            # Handle dictionary response
            if 'users' in result:
                if isinstance(result['users'], list):
                    # Format: {"users": [{user1}, {user2}, ...]}
                    users_count = len(result['users'])
                elif isinstance(result['users'], dict) and 'user' in result['users']:
                    # Format: {"users": {"user": [{user1}, {user2}, ...]}}
                    users_count = len(result['users']['user'])
                else:
                    users_count = 0
            else:
                users_count = 0
        elif isinstance(result, list):
            # Handle list response
            users_count = len(result)
        else:
            users_count = 0
            
        print(f"Successfully retrieved {users_count} users")
        return True
    except Exception as e:
        print(f"Error testing Users API: {e}")
        return False


def test_groups_api(host: str, secret: str) -> bool:
    """
    Test the Groups API.
    
    Args:
        host: Openfire server host
        secret: API secret key
        verify_ssl: Whether to verify SSL certificates
        
    Returns:
        True if successful
    """
    print("\n=== Testing Groups API ===")
    try:
        groups_api = Groups(host, secret)
        result = groups_api.get_groups()
        
        # Handle different response formats
        if isinstance(result, dict):
            # Handle dictionary response
            if 'groups' in result:
                if isinstance(result['groups'], list):
                    # Format: {"groups": [{group1}, {group2}, ...]}
                    groups_count = len(result['groups'])
                elif isinstance(result['groups'], dict) and 'group' in result['groups']:
                    # Format: {"groups": {"group": [{group1}, {group2}, ...]}}
                    groups_count = len(result['groups']['group'])
                else:
                    groups_count = 0
            else:
                groups_count = 0
        elif isinstance(result, list):
            # Handle list response
            groups_count = len(result)
        else:
            groups_count = 0
            
        print(f"Successfully retrieved {groups_count} groups")
        return True
    except Exception as e:
        print(f"Error testing Groups API: {e}")
        return False


def test_system_api(host: str, secret: str) -> bool:
    """
    Test the System API.
    
    Args:
        host: Openfire server host
        secret: API secret key
        verify_ssl: Whether to verify SSL certificates
        
    Returns:
        True if successful
    """
    print("\n=== Testing System API ===")
    try:
        system_api = System(host, secret)
        result = system_api.get_props()
        
        # Handle different response formats for properties
        if isinstance(result, dict):
            if 'properties' in result:
                if isinstance(result['properties'], dict) and 'property' in result['properties']:
                    prop_count = len(result['properties']['property'])
                elif isinstance(result['properties'], list):
                    prop_count = len(result['properties'])
                else:
                    prop_count = 0
            else:
                prop_count = 0
        elif isinstance(result, list):
            prop_count = len(result)
        else:
            prop_count = 0
            
        print(f"Successfully retrieved {prop_count} system properties")
        
        # Test concurrent sessions
        sessions = system_api.get_concurrent_sessions()
        print(f"Current sessions: {sessions}")
        return True
    except Exception as e:
        print(f"Error testing System API: {e}")
        return False


def test_sessions_api(host: str, secret: str) -> bool:
    """
    Test the Sessions API.
    
    Args:
        host: Openfire server host
        secret: API secret key
        verify_ssl: Whether to verify SSL certificates
        
    Returns:
        True if successful
    """
    print("\n=== Testing Sessions API ===")
    try:
        sessions_api = Sessions(host, secret)
        result = sessions_api.get_sessions()
        
        # Handle different response formats
        if isinstance(result, dict):
            if 'sessions' in result:
                if isinstance(result['sessions'], dict) and 'session' in result['sessions']:
                    session_count = len(result['sessions']['session'])
                elif isinstance(result['sessions'], list):
                    session_count = len(result['sessions'])
                else:
                    session_count = 0
            else:
                session_count = 0
        elif isinstance(result, list):
            session_count = len(result)
        else:
            session_count = 0
            
        print(f"Successfully retrieved {session_count} active sessions")
        return True
    except Exception as e:
        print(f"Error testing Sessions API: {e}")
        return False


def test_muc_api(host: str, secret: str) -> bool:
    """
    Test the MUC API.
    
    Args:
        host: Openfire server host
        secret: API secret key
        verify_ssl: Whether to verify SSL certificates
        
    Returns:
        True if successful
    """
    print("\n=== Testing MUC API ===")
    try:
        muc_api = Muc(host, secret)
        result = muc_api.get_rooms()
        
        # Handle different response formats
        if isinstance(result, dict):
            if 'chatRooms' in result:
                if isinstance(result['chatRooms'], dict) and 'chatRoom' in result['chatRooms']:
                    room_count = len(result['chatRooms']['chatRoom'])
                elif isinstance(result['chatRooms'], list):
                    room_count = len(result['chatRooms'])
                else:
                    room_count = 0
            else:
                room_count = 0
        elif isinstance(result, list):
            room_count = len(result)
        else:
            room_count = 0
            
        print(f"Successfully retrieved {room_count} chat rooms")
        return True
    except Exception as e:
        print(f"Error testing MUC API: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Test Openfire REST API connection')
    parser.add_argument('--host', default='https://localhost:9091', 
                        help='Openfire server host (default: https://localhost:9091)')
    parser.add_argument('--creds', default='credentials.txt',
                        help='Path to credentials file (default: credentials.txt)')
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
    
    print(f"Testing connection to Openfire server at {host}")
    print(f"Using API token: {secret}")
    
    # If insecure flag is set, disable SSL warnings and certificate verification
    if args.insecure:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        print("Warning: SSL certificate validation is disabled")
        
        # Monkey patch the requests module to disable SSL verification
        import requests
        old_request = requests.Session.request
        def new_request(self, method, url, **kwargs):
            kwargs['verify'] = False
            return old_request(self, method, url, **kwargs)
        requests.Session.request = new_request
    
    # Run tests
    success_count = 0
    total_tests = 5
    
    if test_users_api(host, secret):
        success_count += 1
    
    if test_groups_api(host, secret):
        success_count += 1
    
    if test_system_api(host, secret):
        success_count += 1
    
    if test_sessions_api(host, secret):
        success_count += 1
    
    if test_muc_api(host, secret):
        success_count += 1
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Passed: {success_count}/{total_tests} tests")
    
    if success_count == total_tests:
        print("All tests passed successfully!")
        return 0
    else:
        print("Some tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
