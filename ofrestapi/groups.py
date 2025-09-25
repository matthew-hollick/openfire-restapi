# -*- coding: utf-8 -*-
"""
Groups module for Openfire REST API.

This module provides functionality to manage groups in Openfire.
"""

from typing import Dict, Any
from requests import get, put, post, delete

from ofrestapi.base import Base


__all__ = ["Groups"]


class Groups(Base):

    def __init__(self, host: str, secret: str, endpoint: str = "/plugins/restapi/v1/groups") -> None:
        """
        Initialize the Groups API client.
        
        Args:
            host: Scheme://Host/ for API requests
            secret: Shared secret key for API requests
            endpoint: Endpoint for API requests
        """
        super().__init__(host, secret, endpoint)

    def get_groups(self) -> Dict[str, Any]:
        """
        Retrieve all groups.
        
        Returns:
            Dictionary containing group information
        """
        return self._submit_request(get, self.endpoint)

    def get_group(self, groupname: str) -> Dict[str, Any]:
        """
        Retrieve exact group info.

        Args:
            groupname: The exact group name for request
            
        Returns:
            Dictionary containing group information
        """
        endpoint = "/".join([self.endpoint, groupname])
        return self._submit_request(get, endpoint)

    def add_group(self, groupname: str, description: str) -> bool:
        """
        Create a new group.

        Args:
            groupname: Name of the group
            description: Description of the group
            
        Returns:
            True if successful
        """
        payload = {
            "name": groupname,
            "description": description,
        }
        return self._submit_request(post, self.endpoint, json=payload)

    def delete_group(self, groupname: str) -> bool:
        """
        Delete a group.

        Args:
            groupname: The exact group name to delete
            
        Returns:
            True if successful
        """
        endpoint = "/".join([self.endpoint, groupname])
        return self._submit_request(delete, endpoint)

    def update_group(self, groupname: str, description: str) -> bool:
        """
        Update a group.

        Args:
            groupname: Name of the group
            description: Description of the group
            
        Returns:
            True if successful
        """
        endpoint = "/".join([self.endpoint, groupname])
        payload = {
            "name": groupname,
            "description": description,
        }
        return self._submit_request(put, endpoint, json=payload)
