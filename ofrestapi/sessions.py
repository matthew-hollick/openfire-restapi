# -*- coding: utf-8 -*-
"""
Sessions module for Openfire REST API.

This module provides functionality to manage user sessions in Openfire.
"""

from typing import Dict, Any, List
from requests import get, delete

from ofrestapi.base import Base


__all__ = ["Sessions"]


class Sessions(Base):

    def __init__(self, host: str, secret: str, endpoint: str = "/plugins/restapi/v1/sessions") -> None:
        """
        Initialize the Sessions API client.
        
        Args:
            host: Scheme://Host/ for API requests
            secret: Shared secret key for API requests
            endpoint: Endpoint for API requests
        """
        super().__init__(host, secret, endpoint)

    def get_sessions(self) -> Dict[str, Any]:
        """
        Retrieve sessions of all users.
        
        Returns:
            Dictionary containing session information for all users
        """
        return self._submit_request(get, self.endpoint)

    def get_user_sessions(self, username: str) -> Dict[str, Any]:
        """
        Retrieve sessions of a specific user.

        Args:
            username: The user name
            
        Returns:
            Dictionary containing session information for the specified user
        """
        endpoint = "/".join([self.endpoint, username])
        return self._submit_request(get, endpoint)

    def close_user_sessions(self, username: str) -> bool:
        """
        Close all sessions of a specific user.

        Args:
            username: The user name
            
        Returns:
            True if successful
        """
        endpoint = "/".join([self.endpoint, username])
        return self._submit_request(delete, endpoint)
        
    def is_user_online(self, username: str) -> bool:
        """
        Check if a user is currently online (has active sessions).
        
        Args:
            username: The user name to check
            
        Returns:
            True if the user has active sessions, False otherwise
        """
        try:
            sessions = self.get_user_sessions(username)
            if "sessions" in sessions and sessions["sessions"]:
                return True
            return False
        except Exception:
            # If there's an error (e.g., user not found), assume user is offline
            return False
            
    def get_user_session_details(self, username: str) -> List[Dict[str, Any]]:
        """
        Get detailed information about a user's active sessions.
        
        Args:
            username: The user name to check
            
        Returns:
            List of dictionaries containing session details
        """
        try:
            sessions = self.get_user_sessions(username)
            
            # Check if we have sessions data
            if not sessions or "sessions" not in sessions:
                return []
                
            # Handle the case where sessions is a list directly
            if isinstance(sessions["sessions"], list):
                return sessions["sessions"]
                
            # Handle the case where sessions contains a 'session' key
            if isinstance(sessions["sessions"], dict) and "session" in sessions["sessions"]:
                session_data = sessions["sessions"]["session"]
                if isinstance(session_data, dict):
                    return [session_data]
                elif isinstance(session_data, list):
                    return session_data
                    
            return []
        except Exception as e:
            print(f"Error getting session details: {e}")
            return []
