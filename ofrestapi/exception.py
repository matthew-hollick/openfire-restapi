# -*- coding: utf-8 -*-
"""
Exceptions for the Openfire REST API client.

This module contains all exceptions that can be raised by the Openfire REST API client.
"""

from typing import Optional

__all__ = [
    "OpenfireApiException",
    "IllegalArgumentException",
    "UserNotFoundException",
    "UserAlreadyExistsException",
    "RequestNotAuthorisedException",
    "UserServiceDisabledException",
    "SharedGroupException",
    "InvalidResponseException",
    "PropertyNotFoundException",
    "GroupAlreadyExistsException",
    "GroupNotFoundException",
    "RoomNotFoundException",
    "NotAllowedException",
    "AlreadyExistsException",
]


class OpenfireApiException(Exception):
    """Base exception for all Openfire API exceptions."""
    
    def __init__(self, message: Optional[str] = None):
        """Initialize the exception with an optional message.
        
        Args:
            message: The error message
        """
        self.message = message
        super().__init__(message)


class IllegalArgumentException(OpenfireApiException):
    """Raised when an illegal argument is provided to the API."""
    pass


class UserNotFoundException(OpenfireApiException):
    """Raised when a user is not found."""
    pass


class UserAlreadyExistsException(OpenfireApiException):
    """Raised when attempting to create a user that already exists."""
    pass


class RequestNotAuthorisedException(OpenfireApiException):
    """Raised when a request is not authorized."""
    pass


class UserServiceDisabledException(OpenfireApiException):
    """Raised when the user service is disabled."""
    pass


class SharedGroupException(OpenfireApiException):
    """Raised when there is an issue with shared groups."""
    pass


class InvalidResponseException(OpenfireApiException):
    """Raised when the API returns an invalid response."""
    pass


class PropertyNotFoundException(OpenfireApiException):
    """Raised when a property is not found."""
    pass


class GroupAlreadyExistsException(OpenfireApiException):
    """Raised when attempting to create a group that already exists."""
    pass


class GroupNotFoundException(OpenfireApiException):
    """Raised when a group is not found."""
    pass


class RoomNotFoundException(OpenfireApiException):
    """Raised when a chat room is not found."""
    pass


class NotAllowedException(OpenfireApiException):
    """Raised when an operation is not allowed."""
    pass


class AlreadyExistsException(OpenfireApiException):
    """Raised when an entity already exists."""
    pass
