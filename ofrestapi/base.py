# -*- coding: utf-8 -*-
from typing import Any, Dict, Callable, Union, List
from requests import Response

from ofrestapi.exception import (IllegalArgumentException, UserNotFoundException, UserAlreadyExistsException,
                       RequestNotAuthorisedException, UserServiceDisabledException,
                       SharedGroupException, InvalidResponseException, PropertyNotFoundException,
                       GroupAlreadyExistsException, GroupNotFoundException, RoomNotFoundException,
                       NotAllowedException, AlreadyExistsException)


EXCEPTIONS_MAP = {
    'IllegalArgumentException': IllegalArgumentException,
    'UserNotFoundException': UserNotFoundException,
    'UserAlreadyExistsException': UserAlreadyExistsException,
    'RequestNotAuthorised': RequestNotAuthorisedException,
    'UserServiceDisabled': UserServiceDisabledException,
    'SharedGroupException': SharedGroupException,
    'PropertyNotFoundException': PropertyNotFoundException,
    'GroupAlreadyExistsException': GroupAlreadyExistsException,
    'GroupNotFoundException': GroupNotFoundException,
    'RoomNotFoundException': RoomNotFoundException,
    'NotAllowedException': NotAllowedException,
    'AlreadyExistsException': AlreadyExistsException,
}


# Define the public API
__all__ = ['Base']


class Base:

    def __init__(self, host: str, secret: str, endpoint: str, verify_ssl: bool = True) -> None:
        """
        Initialize the Base API client.
        
        Args:
            host: Scheme://Host/ for API requests
            secret: Shared secret key for API requests
            endpoint: Endpoint for API requests
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        self.headers: Dict[str, str] = {
            "Authorization": secret,
            "Accept": "application/json"
        }
        self.host = host
        self.endpoint = endpoint
        self.verify_ssl = verify_ssl

    def _submit_request(self, func: Callable, endpoint: str, **kwargs: Any) -> Union[Dict[str, Any], List[Dict[str, Any]], bool]:
        """
        Wrapper for sending a request to the API.

        Args:
            func: The requests function to use (get, post, put, delete)
            endpoint: Plugin endpoint for request
            **kwargs: Additional arguments that the request function takes

        Returns:
            JSON object (dict or list) or True if successful but no JSON response

        Raises:
            Various exceptions based on the API response
        """
        # Add verify parameter if not already present
        if 'verify' not in kwargs:
            kwargs['verify'] = self.verify_ssl
            
        r: Response = func(
            headers=self.headers,
            url=self.host + endpoint,
            **kwargs
        )
        if r.status_code in (200, 201):
            try:
                return r.json()
            except ValueError:
                # No JSON response but request was successful
                return True
        else:
            try:
                response_json = r.json()
                exception = response_json.get("exception")
                message = response_json.get("message", "Unknown error")
            except ValueError:
                raise InvalidResponseException(f"Invalid response with status code: {r.status_code}")
            
            if exception in EXCEPTIONS_MAP:
                raise EXCEPTIONS_MAP[exception](message)
            else:
                raise InvalidResponseException(f"Unknown exception: {exception}")

