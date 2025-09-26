#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example script for retrieving security audit logs from Openfire.

This script demonstrates how to use the SecurityAuditLog class to retrieve
security audit logs from an Openfire server.
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Add parent directory to path to import ofrestapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ofrestapi import SecurityAuditLog

def format_timestamp(timestamp_ms):
    """Convert millisecond timestamp to human-readable format."""
    dt = datetime.fromtimestamp(timestamp_ms / 1000)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def main():
    # Configuration
    host = "http://localhost:9090"  # Replace with your Openfire server URL
    token = "your_auth_token"       # Replace with your authentication token
    
    # Create SecurityAuditLog API client
    security_api = SecurityAuditLog(host, token)
    security_api.verify_ssl = False  # Set to True in production
    
    # Example 1: Get recent logs (last 10 entries)
    print("Getting 10 most recent security audit logs...")
    recent_logs = security_api.get_recent_logs(limit=10)
    
    # Extract and print log entries
    log_entries = security_api.extract_log_entries(recent_logs)
    if log_entries:
        print(f"Found {len(log_entries)} recent log entries:")
        for log in log_entries:
            timestamp = format_timestamp(log.get('timestamp', 0))
            print(f"[{timestamp}] {log.get('username', 'unknown')}: {log.get('summary', 'No summary')}")
            if log.get('details'):
                print(f"  Details: {log.get('details')}")
            print("-" * 40)
    else:
        print("No recent log entries found.")
    
    # Example 2: Get logs for a specific user
    username = "admin"  # Replace with the username you want to search for
    print(f"\nGetting security audit logs for user '{username}'...")
    user_logs = security_api.get_logs_by_username(username, limit=5)
    
    # Extract and print log entries
    log_entries = security_api.extract_log_entries(user_logs)
    if log_entries:
        print(f"Found {len(log_entries)} log entries for user '{username}':")
        for log in log_entries:
            timestamp = format_timestamp(log.get('timestamp', 0))
            print(f"[{timestamp}] {log.get('summary', 'No summary')}")
            if log.get('details'):
                print(f"  Details: {log.get('details')}")
            print("-" * 40)
    else:
        print(f"No log entries found for user '{username}'.")
    
    # Example 3: Get logs within a specific timeframe (last 24 hours)
    now_ms = int(datetime.now().timestamp() * 1000)
    yesterday_ms = int((datetime.now() - timedelta(days=1)).timestamp() * 1000)
    
    print(f"\nGetting security audit logs from the last 24 hours...")
    timeframe_logs = security_api.get_logs_in_timeframe(yesterday_ms, now_ms, limit=10)
    
    # Extract and print log entries
    log_entries = security_api.extract_log_entries(timeframe_logs)
    if log_entries:
        print(f"Found {len(log_entries)} log entries in the last 24 hours:")
        for log in log_entries:
            timestamp = format_timestamp(log.get('timestamp', 0))
            print(f"[{timestamp}] {log.get('username', 'unknown')}: {log.get('summary', 'No summary')}")
            if log.get('details'):
                print(f"  Details: {log.get('details')}")
            print("-" * 40)
    else:
        print("No log entries found in the specified timeframe.")

if __name__ == "__main__":
    main()
