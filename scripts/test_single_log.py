#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for retrieving a single security audit log entry.
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path to import ofrestapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ofrestapi import SecurityAuditLog

def format_timestamp(timestamp_sec):
    """Convert seconds timestamp to human-readable format."""
    dt = datetime.fromtimestamp(timestamp_sec)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def main():
    # Configuration
    host = "http://localhost:9090"
    token = "fred"
    
    # Create SecurityAuditLog API client
    security_api = SecurityAuditLog(host, token)
    security_api.verify_ssl = False
    
    # Get a specific log entry (log ID 22)
    print("Attempting to get a single log entry...")
    
    # Use a very specific time range to try to get just one log
    logs_response = security_api.get_logs(limit=1)
    
    # Extract log entries
    log_entries = security_api.extract_log_entries(logs_response)
    
    print(f"Found {len(log_entries)} log entries")
    
    # Print the log entries
    for log in log_entries:
        timestamp = format_timestamp(log.get('timestamp', 0))
        print(f"[{timestamp}] {log.get('username', 'unknown')}: {log.get('summary', 'No summary')}")
        if log.get('details'):
            print(f"  Details: {log.get('details')}")
        print("-" * 40)
    
    # Print the raw response for debugging
    print("\nRaw response:")
    print(json.dumps(logs_response, indent=2))

if __name__ == "__main__":
    main()
