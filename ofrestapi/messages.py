# -*- coding: utf-8 -*-
"""
Messages module for Openfire REST API.

This module provides functionality to manage messages in Openfire.
"""

from typing import Dict, Any
from requests import get, post

from ofrestapi.base import Base


__all__ = ["Messages"]


class Messages(Base):

    def __init__(self, host: str, secret: str, endpoint: str = "/plugins/restapi/v1/messages/users") -> None:
        """
        Initialize the Messages API client.
        
        Args:
            host: Scheme://Host/ for API requests
            secret: Shared secret key for API requests
            endpoint: Endpoint for API requests
        """
        super().__init__(host, secret, endpoint)

    def send_broadcast(self, message: str) -> bool:
        """
        Send a broadcast/server message to all online users.

        Args:
            message: Message text to be sent
            
        Returns:
            True if successful
        """
        payload = {
            "body": message,
        }
        return self._submit_request(post, self.endpoint, json=payload)

    def get_unread_messages(self, jid: str) -> Dict[str, Any]:
        """
        Retrieve unread messages count for a user.

        Args:
            jid: The JID to get message count from
            
        Returns:
            Dictionary containing unread message information
        """
        endpoint = "/plugins/restapi/v1/archive/messages/unread/" + jid
        return self._submit_request(get, endpoint)
