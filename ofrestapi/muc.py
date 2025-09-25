# -*- coding: utf-8 -*-
"""
MUC (Multi-User Chat) module for Openfire REST API.

This module provides functionality to manage chat rooms in Openfire.
"""

from typing import Dict, List, Optional, Any
from requests import get, put, post, delete

from ofrestapi.base import Base


__all__ = ["Muc"]


class Muc(Base):

    def __init__(self, host: str, secret: str, endpoint: str = "/plugins/restapi/v1/chatrooms") -> None:
        """
        Initialize the MUC API client.
        
        Args:
            host: Scheme://Host/ for API requests
            secret: Shared secret key for API requests
            endpoint: Endpoint for API requests
        """
        super().__init__(host, secret, endpoint)

    def get_room(self, roomname: str, servicename: str = "conference") -> Dict[str, Any]:
        """
        Retrieve exact chat room info.

        Args:
            roomname: The exact chat room name for request
            servicename: Optional name of the Group Chat Service. Default: 'conference'
            
        Returns:
            Dictionary containing chat room information
        """
        endpoint = "/".join([self.endpoint, roomname])
        params = {"servicename": servicename}
        return self._submit_request(get, endpoint, params=params)

    def get_rooms(self, servicename: str = "conference", typeof: str = "public", 
               query: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve all chat rooms or filter by chat room name.

        Args:
            servicename: Optional name of the Group Chat Service. Default: 'conference'
            typeof: Optional search only specified type of rooms. Values: 'all', 'public'. Default: 'public'
            query: Optional search/filter by room name. Acts like the wildcard search %String%
            
        Returns:
            Dictionary containing chat rooms information
        """
        params = {
            "servicename": servicename,
            "type": typeof,
            "search": query,
        }
        return self._submit_request(get, self.endpoint, params=params)

    def get_room_users(self, roomname: str, servicename: str = "conference") -> Dict[str, Any]:
        """
        Retrieve chat room participants.

        Args:
            roomname: The exact chat room name for request
            servicename: Optional name of the Group Chat Service. Default: 'conference'
            
        Returns:
            Dictionary containing participant information
        """
        endpoint = "/".join([self.endpoint, roomname, "participants"])
        params = {"servicename": servicename}
        return self._submit_request(get, endpoint, params=params)

    def add_room(self, roomname: str, name: str, description: str, servicename: str = "conference",
                 subject: Optional[str] = None, password: Optional[str] = None, maxusers: int = 0, 
                 persistent: bool = True, public: bool = True, registration: bool = True, 
                 visiblejids: bool = True, changesubject: bool = False, anycaninvite: bool = False, 
                 changenickname: bool = True, logenabled: bool = True, registerednickname: bool = False, 
                 membersonly: bool = False, moderated: bool = False,
                 broadcastroles: Optional[List[str]] = None, owners: Optional[List[str]] = None, 
                 admins: Optional[List[str]] = None, members: Optional[List[str]] = None, 
                 outcasts: Optional[List[str]] = None) -> bool:
        """
        Create a chat room

        :param roomname: The name/id of the room. Can only contains lowercase and alphanumeric characters
        :param name: Also the name of the room, but can contains non alphanumeric characters
        :param description: Description text of the room
        :param servicename: (optional) The name of the Group Chat Service. Default: `conference`
        :param subject: (optional) Subject of the room
        :param password: (optional) The password that the user must provide to enter the room
        :param maxusers: (optional) The maximum number of occupants that can be simultaneously in the room. Default: 0 (unlimited)
        :param persistent: (optional) Persistent rooms are saved to the database to make their configurations persistent together with the affiliation of the users. Otherwise the room will be destroyed if the last occupant leave the room. Default: True
        :param public: (optional) True if the room is searchable and visible through service discovery. Default: True
        :param registration: (optional) True if users are allowed to register with the room. Default: True
        :param visiblejids: (optional) True if every presence packet will include the JID of every occupant. Default: True
        :param changesubject: (optional) True if participants are allowed to change the room’s subject. Default: True
        :param anycaninvite: (optional) True if occupants can invite other users to the room. Affects on members only rooms. Default: False
        :param changenickname: (optional) True if room occupants are allowed to change their nicknames. Default: True
        :param logenabled: (optional) True if the room’s conversation is being logged. Default: True
        :param registerednickname: (optional) True if registered users can only join the room using their registered nickname. Default: False
        :param membersonly: (optional) True if the room requires an invitation to enter. Default: False
        :param moderated: (optional) True if the room in which only those with “voice” may send messages to all occupants. Default: False
        :param broadcastroles: (optional) The list of roles of which presence will be broadcasted to the rest of the occupants.
        :type broadcastroles: List of strings. E.g. any from [ 'moderator', 'participant', 'visitor' ]
        :param owners: (optional) A collection with the current list of owners
        :type owners: List of strings. E.g. ['owner@localhost',]
        :param admins: (optional) A collection with the current list of admins
        :type admins: List of strings. E.g. ['admin@localhost',]
        :param members: (optional) A collection with the current list of room members. The collection contains the bareJID of the users with member affiliation. If the room is not members-only then the list will contain the users that registered with the room and therefore they may have reserved a nickname
        :type members: List of strings. E.g. ['member@localhost',]
        :param outcasts: (optional) A collection with the current list of outcast users. An outcast user is not allowed to join the room again
        :type outcasts: List of strings. E.g. ['outcast@localhost',]
        """
        payload = {
            'roomName': roomname,
            'naturalName': name,
            'description': description,
            'subject': subject,
            'password': password,
            'maxUsers': maxusers,
            'persistent': persistent,
            'publicRoom': public,
            'registrationEnabled': registration,
            'canAnyoneDiscoverJID': visiblejids,
            'canOccupantsChangeSubject': changesubject,
            'canOccupantsInvite': anycaninvite,
            'canChangeNickname': changenickname,
            'logEnabled': logenabled,
            'loginRestrictedToNickname': registerednickname,
            'membersOnly': membersonly,
            'moderated': moderated,
            'broadcastPresenceRoles': {'broadcastPresenceRole': broadcastroles},
            'owners': {'owner': owners},
            'admins': {'admin': admins},
            'members': {'member': members},
            'outcasts': {'outcast': outcasts},
        }
        params = {'servicename': servicename}
        return self._submit_request(post, self.endpoint, json=payload, params=params)

    def delete_room(self, roomname, servicename='conference'):
        """
        Delete a chat room

        :param roomname: Exact room name
        :param servicename: (optional) The name of the Group Chat Service. Default: `conference`
        """
        endpoint = '/'.join([self.endpoint, roomname])
        params = {'servicename': servicename}
        return self._submit_request(delete, endpoint, params=params)

    def update_room(self, roomname, name=None, description=None, servicename='conference',
                    subject=None, password=None, maxusers=0, persistent=True,
                    public=True, registration=True, visiblejids=True, changesubject=False,
                    anycaninvite=False, changenickname=True, logenabled=True,
                    registerednickname=False, membersonly=False, moderated=False,
                    broadcastroles=None, owners=None, admins=None, members=None, outcasts=None):
        """
        Update a chat room

        :param roomname: The name/id of the room. Can only contains lowercase and alphanumeric characters
        :param name: (optional) Also the name of the room, but can contains non alphanumeric characters
        :param description: (optional) Description text of the room
        :param servicename: (optional) The name of the Group Chat Service. Default: `conference`
        :param subject: (optional) Subject of the room
        :param password: (optional) The password that the user must provide to enter the room
        :param maxusers: (optional) The maximum number of occupants that can be simultaneously in the room. Default: 0 (unlimited)
        :param persistent: (optional) Persistent rooms are saved to the database to make their configurations persistent together with the affiliation of the users. Otherwise the room will be destroyed if the last occupant leave the room. Default: True
        :param public: (optional) True if the room is searchable and visible through service discovery. Default: True
        :param registration: (optional) True if users are allowed to register with the room. Default: True
        :param visiblejids: (optional) True if every presence packet will include the JID of every occupant. Default: True
        :param changesubject: (optional) True if participants are allowed to change the room’s subject. Default: True
        :param anycaninvite: (optional) True if occupants can invite other users to the room. Affects on members only rooms. Default: False
        :param changenickname: (optional) True if room occupants are allowed to change their nicknames. Default: True
        :param logenabled: (optional) True if the room’s conversation is being logged. Default: True
        :param registerednickname: (optional) True if registered users can only join the room using their registered nickname. Default: False
        :param membersonly: (optional) True if the room requires an invitation to enter. Default: False
        :param moderated: (optional) True if the room in which only those with “voice” may send messages to all occupants. Default: False
        :param broadcastroles: (optional) The list of roles of which presence will be broadcasted to the rest of the occupants.
        :type broadcastroles: List of strings. E.g. any from [ 'moderator', 'participant', 'visitor' ]
        :param owners: (optional) A collection with the current list of owners
        :type owners: List of strings. E.g. ['owner@localhost',]
        :param admins: (optional) A collection with the current list of admins
        :type admins: List of strings. E.g. ['admin@localhost',]
        :param members: (optional) A collection with the current list of room members. The collection contains the bareJID of the users with member affiliation. If the room is not members-only then the list will contain the users that registered with the room and therefore they may have reserved a nickname
        :type members: List of strings. E.g. ['member@localhost',]
        :param outcasts: (optional) A collection with the current list of outcast users. An outcast user is not allowed to join the room again
        :type outcasts: List of strings. E.g. ['outcast@localhost',]
        """
        endpoint = '/'.join([self.endpoint, roomname])
        payload = {
            'roomName': roomname,
            'naturalName': name,
            'description': description,
            'subject': subject,
            'password': password,
            'maxUsers': maxusers,
            'persistent': persistent,
            'publicRoom': public,
            'registrationEnabled': registration,
            'canAnyoneDiscoverJID': visiblejids,
            'canOccupantsChangeSubject': changesubject,
            'canOccupantsInvite': anycaninvite,
            'canChangeNickname': changenickname,
            'logEnabled': logenabled,
            'loginRestrictedToNickname': registerednickname,
            'membersOnly': membersonly,
            'moderated': moderated,
            'broadcastPresenceRoles': {'broadcastPresenceRole': broadcastroles},
            'owners': {'owner': owners},
            'admins': {'admin': admins},
            'members': {'member': members},
            'outcasts': {'outcast': outcasts},
        }
        params = {'servicename': servicename}
        return self._submit_request(put, endpoint, json=payload, params=params)

    def grant_user_role(self, roomname, username, role, servicename='conference'):
        """
        Grant role to chat room user

        :param roomname: The exact chat room name for request
        :param username: The local username or the user JID
        :param role: Any from `owners`,`admins`,`members`,`outcasts`
        :param servicename: (optional) The name of the Group Chat Service. Default: `conference`
        """
        endpoint = '/'.join([self.endpoint, roomname, role, username])
        params = {'servicename': servicename}
        return self._submit_request(post, endpoint, params=params)

    def revoke_user_role(self, roomname, username, role, servicename='conference'):
        """
        Revoke role from chat room user

        :param roomname: The exact chat room name for request
        :param username: The local username or the user JID
        :param role: Any from `owners`,`admins`,`members`,`outcasts`
        :param servicename: (optional) The name of the Group Chat Service. Default: `conference`
        """
        endpoint = '/'.join([self.endpoint, roomname, role, username])
        params = {'servicename': servicename}
        return self._submit_request(delete, endpoint, params=params)
