# -*- coding: utf-8 -*-
"""
Sessions module for Openfire REST API.

This module provides functionality to manage user sessions in Openfire.
"""

from typing import Dict, Any
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
