#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for handling a single security audit log entry returned as a dict.
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path to import ofrestapi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ofrestapi import SecurityAuditLog

def main():
    # Create a mock response with a single log entry as a dict
    mock_response = {
        "logs": {
            "log": {
                "logId": 22,
                "username": "admin",
                "timestamp": 1758900075,
                "summary": "Successful admin console login attempt",
                "node": "192.168.5.15",
                "details": "The user logged in successfully to the admin console from address 127.0.0.1."
            }
        }
    }
    
    # Create SecurityAuditLog API client
    security_api = SecurityAuditLog("http://localhost:9090", "fred")
    
    # Test the extract_log_entries method with our mock response
    log_entries = security_api.extract_log_entries(mock_response)
    
    # Print results
    print(f"Type of log_entries: {type(log_entries)}")
    print(f"Length of log_entries: {len(log_entries)}")
    
    if log_entries:
        print("\nLog entries extracted:")
        for i, entry in enumerate(log_entries):
            print(f"\nEntry {i+1}:")
            print(f"  logId: {entry.get('logId')}")
            print(f"  username: {entry.get('username')}")
            print(f"  timestamp: {entry.get('timestamp')}")
            print(f"  summary: {entry.get('summary')}")
    else:
        print("No log entries extracted!")

if __name__ == "__main__":
    main()
