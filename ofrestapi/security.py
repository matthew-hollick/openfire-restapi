# -*- coding: utf-8 -*-
"""
Security module for Openfire REST API.

This module provides functionality to access security audit logs in Openfire.
"""

from typing import Dict, Any, Optional, List
from requests import get

from ofrestapi.base import Base


__all__ = ["SecurityAuditLog"]


class SecurityAuditLog(Base):

    def __init__(self, host: str, secret: str, endpoint: str = "/plugins/restapi/v1/logs/security") -> None:
        """
        Initialize the SecurityAuditLog API client.
        
        Args:
            host: Scheme://Host/ for API requests
            secret: Shared secret key for API requests
            endpoint: Endpoint for API requests
        """
        super().__init__(host, secret, endpoint)

    def get_logs(self, 
                username: Optional[str] = None, 
                offset: Optional[int] = None, 
                limit: int = 100, 
                start_time: Optional[int] = None, 
                end_time: Optional[int] = None) -> Dict[str, Any]:
        """
        Retrieve entries from the security audit log.
        
        Args:
            username: Optional username to filter events by
            offset: Optional number of log entries to skip
            limit: Number of log entries to retrieve (default: 100)
            start_time: Optional oldest timestamp (in seconds since epoch) of logs to retrieve
            end_time: Optional most recent timestamp (in seconds since epoch) of logs to retrieve
            
        Returns:
            Dictionary containing security audit log entries
        """
        params = {}
        if username:
            params['username'] = username
        if offset is not None:
            params['offset'] = offset
        if limit != 100:  # Only add if different from default
            params['limit'] = limit
        if start_time is not None:
            params['startTime'] = start_time
        if end_time is not None:
            params['endTime'] = end_time
            
        return self._submit_request(get, self.endpoint, params=params)

    def get_logs_by_username(self, username: str, limit: int = 100) -> Dict[str, Any]:
        """
        Retrieve security audit log entries for a specific user.
        
        Args:
            username: Username to filter events by
            limit: Number of log entries to retrieve (default: 100)
            
        Returns:
            Dictionary containing security audit log entries for the specified user
        """
        return self.get_logs(username=username, limit=limit)

    def get_recent_logs(self, limit: int = 20) -> Dict[str, Any]:
        """
        Retrieve the most recent security audit log entries.
        
        Args:
            limit: Number of recent log entries to retrieve (default: 20)
            
        Returns:
            Dictionary containing the most recent security audit log entries
        """
        return self.get_logs(limit=limit)

    def get_logs_in_timeframe(self, start_time: int, end_time: int, limit: int = 100) -> Dict[str, Any]:
        """
        Retrieve security audit log entries within a specific timeframe.
        
        Args:
            start_time: Oldest timestamp (in seconds since epoch) of logs to retrieve
            end_time: Most recent timestamp (in seconds since epoch) of logs to retrieve
            limit: Number of log entries to retrieve (default: 100)
            
        Returns:
            Dictionary containing security audit log entries within the specified timeframe
        """
        return self.get_logs(start_time=start_time, end_time=end_time, limit=limit)

    def extract_log_entries(self, logs_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract individual log entries from the API response.
        
        Args:
            logs_response: The response from get_logs()
            
        Returns:
            List of individual log entry dictionaries
        """
        # Handle the actual response format from the API
        if not logs_response:
            return []
            
        if "logs" in logs_response:
            # The logs might be directly in the 'logs' key as a list
            if isinstance(logs_response["logs"], list):
                return logs_response["logs"]
            # Or it might be nested under logs.log
            elif isinstance(logs_response["logs"], dict) and "log" in logs_response["logs"]:
                # Check if the log is a dict (single entry) and wrap it in a list
                if isinstance(logs_response["logs"]["log"], dict):
                    return [logs_response["logs"]["log"]]
                # Otherwise, return the list as is
                return logs_response["logs"]["log"]
            # Handle empty response
            elif logs_response["logs"] is None or logs_response["logs"] == []:
                return []
        return []
