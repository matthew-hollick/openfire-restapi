# -*- coding: utf-8 -*-
"""
System module for Openfire REST API.

This module provides functionality to manage system properties in Openfire.
"""

from typing import Dict, Any
from requests import get, post, delete

from ofrestapi.base import Base


__all__ = ["System"]


class System(Base):

    def __init__(self, host: str, secret: str, endpoint: str = "/plugins/restapi/v1/system/properties") -> None:
        """
        Initialize the System API client.
        
        Args:
            host: Scheme://Host/ for API requests
            secret: Shared secret key for API requests
            endpoint: Endpoint for API requests
        """
        super().__init__(host, secret, endpoint)

    def get_props(self) -> Dict[str, Any]:
        """
        Retrieve all system properties.
        
        Returns:
            Dictionary containing all system properties
        """
        return self._submit_request(get, self.endpoint)

    def get_prop(self, key: str) -> Dict[str, Any]:
        """
        Retrieve a specific system property.

        Args:
            key: The name of the system property
            
        Returns:
            Dictionary containing the system property value
        """
        endpoint = "/".join([self.endpoint, key])
        return self._submit_request(get, endpoint)

    def update_prop(self, key: str, value: str) -> bool:
        """
        Create or update a system property.

        Args:
            key: The name of the system property
            value: The value of the system property
            
        Returns:
            True if successful
        """
        payload = {
            "@key": key,
            "@value": value,
        }
        return self._submit_request(post, self.endpoint, json=payload)

    def delete_prop(self, key: str) -> bool:
        """
        Delete a system property.

        Args:
            key: The name of the system property to delete
            
        Returns:
            True if successful
        """
        endpoint = "/".join([self.endpoint, key])
        return self._submit_request(delete, endpoint)

    def get_concurrent_sessions(self) -> Dict[str, Any]:
        """
        Retrieve concurrent sessions information.
        
        Returns:
            Dictionary containing concurrent sessions statistics
        """
        endpoint = "/".join([self.endpoint.rpartition("/")[0], "statistics", "sessions"])
        return self._submit_request(get, endpoint)
