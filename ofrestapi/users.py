# -*- coding: utf-8 -*-
"""
Users module for Openfire REST API.

This module provides functionality to manage users in Openfire.
"""

from typing import Dict, List, Optional, Any
from requests import get, put, post, delete

from ofrestapi.base import Base


__all__ = ["Users"]


class Users(Base):
    SUBSCRIPTION_REMOVE = -1
    SUBSCRIPTION_NONE = 0
    SUBSCRIPTION_TO = 1
    SUBSCRIPTION_FROM = 2
    SUBSCRIPTION_BOTH = 3

    def __init__(self, host: str, secret: str, endpoint: str = "/plugins/restapi/v1/users") -> None:
        """
        Initialize the Users API client.
        
        Args:
            host: Scheme://Host/ for API requests
            secret: Shared secret key for API requests
            endpoint: Endpoint for API requests
        """
        super().__init__(host, secret, endpoint)

    def get_user(self, username: str) -> Dict[str, Any]:
        """
        Retrieve exact user info.

        Args:
            username: The exact user name for request
            
        Returns:
            User information as a dictionary
        """
        endpoint = "/".join([self.endpoint, username])
        return self._submit_request(get, endpoint)

    def get_users(self, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve all users or filter by user name.

        Args:
            query: Optional search/filter by user name. Acts like the wildcard search %String%
            
        Returns:
            Dictionary containing user information
        """
        params = {"search": query} if query else None
        return self._submit_request(get, self.endpoint, params=params)

    def add_user(self, username: str, password: str, name: Optional[str] = None, 
               email: Optional[str] = None, props: Optional[Dict[str, str]] = None) -> bool:
        """
        Add a new user.

        Args:
            username: The user name
            password: The password of the user
            name: Optional display name of the user
            email: Optional email address of the user
            props: Optional dictionary with additional user properties
            
        Returns:
            True if successful
        """
        payload = {
            "username": username,
            "password": password,
            "name": name,
            "email": email,
        }
        if props:
            payload["properties"] = {}
            payload["properties"]["property"] = []
            for key, value in props.items():  # Python 3 uses items() instead of iteritems()
                payload["properties"]["property"].append({"@key": key, "@value": value})
        return self._submit_request(post, self.endpoint, json=payload)

    def delete_user(self, username: str) -> bool:
        """
        Delete a user.

        Args:
            username: The user name to delete
            
        Returns:
            True if successful
        """
        endpoint = "/".join([self.endpoint, username])
        return self._submit_request(delete, endpoint)

    def update_user(self, username: str, newusername: Optional[str] = None, password: Optional[str] = None, 
                  name: Optional[str] = None, email: Optional[str] = None, 
                  props: Optional[Dict[str, str]] = None) -> bool:
        """
        Update user information.

        Args:
            username: The user name
            newusername: Optional new user name
            password: Optional new password
            name: Optional new display name
            email: Optional new email address
            props: Optional dictionary with additional user properties
            
        Returns:
            True if successful
        """
        endpoint = "/".join([self.endpoint, username])
        payload = {
            "username": newusername if newusername else username,
            "password": password,
            "name": name,
            "email": email,
        }
        if props:
            payload["properties"] = {}
            payload["properties"]["property"] = []
            for key, value in props.items():  # Python 3 uses items() instead of iteritems()
                payload["properties"]["property"].append({"@key": key, "@value": value})
        return self._submit_request(put, endpoint, json=payload)

    def get_user_groups(self, username: str) -> Dict[str, Any]:
        """
        Retrieve all groups a user belongs to.

        Args:
            username: The user name
            
        Returns:
            Dictionary containing group information
        """
        endpoint = "/".join([self.endpoint, username, "groups"])
        return self._submit_request(get, endpoint)

    def add_user_groups(self, username: str, groups: List[str]) -> bool:
        """
        Add user to one or more groups.

        Args:
            username: The user name
            groups: List of group names to add the user to (e.g. ['Admins', 'Friends'])
            
        Returns:
            True if successful
        """
        endpoint = "/".join([self.endpoint, username, "groups"])
        payload = {
            "groupname": groups,
        }
        return self._submit_request(post, endpoint, json=payload)

    def delete_user_groups(self, username: str, groups: List[str]) -> bool:
        """
        Remove user from one or more groups.

        Args:
            username: The user name
            groups: List of group names to remove the user from (e.g. ['Admins', 'Friends'])
            
        Returns:
            True if successful
        """
        endpoint = "/".join([self.endpoint, username, "groups"])
        payload = {
            "groupname": groups,
        }
        return self._submit_request(delete, endpoint, json=payload)

    def lock_user(self, username: str) -> bool:
        """
        Lock out a user from the system.

        Args:
            username: The user name to lock
            
        Returns:
            True if successful
        """
        endpoint = "/".join([self.endpoint.rpartition("/")[0], "lockouts", username])
        return self._submit_request(post, endpoint)

    def unlock_user(self, username: str) -> bool:
        """
        Unlock a previously locked user.

        Args:
            username: The user name to unlock
            
        Returns:
            True if successful
        """
        endpoint = "/".join([self.endpoint.rpartition("/")[0], "lockouts", username])
        return self._submit_request(delete, endpoint)

    def get_user_roster(self, username: str) -> Dict[str, Any]:
        """
        Retrieve a user's roster (buddy list).

        Args:
            username: The user name
            
        Returns:
            Dictionary containing roster information
        """
        endpoint = "/".join([self.endpoint, username, "roster"])
        return self._submit_request(get, endpoint)

    def add_user_roster_item(self, username: str, jid: str, name: Optional[str] = None, 
                          subscription: Optional[int] = None, groups: Optional[List[str]] = None) -> bool:
        """
        Add a user roster entry (buddy).

        Args:
            username: The user name
            jid: The JID of the roster item to be added (e.g. foo@example.org)
            name: Optional nickname for the user when used in this roster
            subscription: Optional subscription type. One of SUBSCRIPTION_REMOVE,
                         SUBSCRIPTION_NONE, SUBSCRIPTION_TO, SUBSCRIPTION_FROM, SUBSCRIPTION_BOTH
            groups: Optional list of groups to organize roster entries under (e.g. ['Admins', 'Friends'])
            
        Returns:
            True if successful
        """
        endpoint = "/".join([self.endpoint, username, "roster"])
        payload = {
            "jid": jid,
            "nickname": name,
            "subscriptionType": subscription,
            "groups": {"group": groups},
        }
        return self._submit_request(post, endpoint, json=payload)

    def delete_user_roster_item(self, username: str, jid: str) -> bool:
        """
        Delete a user roster entry (buddy).

        Args:
            username: The user name
            jid: The JID of the roster item to be deleted (e.g. foo@example.org)
            
        Returns:
            True if successful
        """
        endpoint = "/".join([self.endpoint, username, "roster", jid])
        return self._submit_request(delete, endpoint)

    def update_user_roster_item(self, username: str, jid: str, name: Optional[str] = None, 
                             subscription: Optional[int] = None, groups: Optional[List[str]] = None) -> bool:
        """
        Update a user roster entry (buddy).

        Args:
            username: The user name
            jid: The JID of the roster item to be updated (e.g. foo@example.org)
            name: Optional nickname for the user when used in this roster
            subscription: Optional subscription type. One of SUBSCRIPTION_REMOVE,
                         SUBSCRIPTION_NONE, SUBSCRIPTION_TO, SUBSCRIPTION_FROM, SUBSCRIPTION_BOTH
            groups: Optional list of groups to organize roster entries under (e.g. ['Admins', 'Friends'])
            
        Returns:
            True if successful
        """
        endpoint = "/".join([self.endpoint, username, "roster", jid])
        payload = {
            "jid": jid,
            "nickname": name,
            "subscriptionType": subscription,
            "groups": {"group": groups},
        }
        return self._submit_request(put, endpoint, json=payload)
