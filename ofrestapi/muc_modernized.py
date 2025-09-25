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
        Create a new chat room.

        Args:
            roomname: The name/id of the room. Can only contain lowercase and alphanumeric characters
            name: Also the name of the room, but can contain non-alphanumeric characters
            description: Description text of the room
            servicename: Optional name of the Group Chat Service. Default: 'conference'
            subject: Optional subject of the room
            password: Optional password that users must provide to enter the room
            maxusers: Optional maximum number of occupants that can be simultaneously in the room. 
                      Default: 0 (unlimited)
            persistent: Optional flag for persistent rooms. Persistent rooms are saved to the database 
                        to make their configurations persistent together with the affiliation of the users. 
                        Otherwise the room will be destroyed if the last occupant leaves. Default: True
            public: Optional flag for public rooms. True if the room is searchable and visible through 
                   service discovery. Default: True
            registration: Optional flag for registration. True if users are allowed to register with 
                         the room. Default: True
            visiblejids: Optional flag for visible JIDs. True if every presence packet will include 
                        the JID of every occupant. Default: True
            changesubject: Optional flag for subject changes. True if participants are allowed to 
                          change the room's subject. Default: False
            anycaninvite: Optional flag for invitations. True if occupants can invite other users 
                         to the room. Affects members-only rooms. Default: False
            changenickname: Optional flag for nickname changes. True if room occupants are allowed 
                          to change their nicknames. Default: True
            logenabled: Optional flag for logging. True if the room's conversation is being logged. 
                       Default: True
            registerednickname: Optional flag for registered nicknames. True if registered users can 
                             only join the room using their registered nickname. Default: False
            membersonly: Optional flag for members-only rooms. True if the room requires an invitation 
                       to enter. Default: False
            moderated: Optional flag for moderated rooms. True if the room is one in which only those 
                     with "voice" may send messages to all occupants. Default: False
            broadcastroles: Optional list of roles whose presence will be broadcasted to other occupants.
                          E.g. ['moderator', 'participant', 'visitor']
            owners: Optional list of room owners. E.g. ['owner@localhost']
            admins: Optional list of room admins. E.g. ['admin@localhost']
            members: Optional list of room members. Contains the bareJID of users with member affiliation.
                   E.g. ['member@localhost']
            outcasts: Optional list of outcast users who are not allowed to join the room.
                    E.g. ['outcast@localhost']
            
        Returns:
            True if successful
        """
        payload = {
            "roomName": roomname,
            "naturalName": name,
            "description": description,
            "subject": subject,
            "password": password,
            "maxUsers": maxusers,
            "persistent": persistent,
            "publicRoom": public,
            "registrationEnabled": registration,
            "canAnyoneDiscoverJID": visiblejids,
            "canOccupantsChangeSubject": changesubject,
            "canOccupantsInvite": anycaninvite,
            "canChangeNickname": changenickname,
            "logEnabled": logenabled,
            "loginRestrictedToNickname": registerednickname,
            "membersOnly": membersonly,
            "moderated": moderated,
            "broadcastPresenceRoles": {"broadcastPresenceRole": broadcastroles},
            "owners": {"owner": owners},
            "admins": {"admin": admins},
            "members": {"member": members},
            "outcasts": {"outcast": outcasts},
        }
        params = {"servicename": servicename}
        return self._submit_request(post, self.endpoint, json=payload, params=params)

    def delete_room(self, roomname: str, servicename: str = "conference") -> bool:
        """
        Delete a chat room.

        Args:
            roomname: Exact room name to delete
            servicename: Optional name of the Group Chat Service. Default: 'conference'
            
        Returns:
            True if successful
        """
        endpoint = "/".join([self.endpoint, roomname])
        params = {"servicename": servicename}
        return self._submit_request(delete, endpoint, params=params)

    def update_room(self, roomname: str, name: Optional[str] = None, description: Optional[str] = None, 
                    servicename: str = "conference", subject: Optional[str] = None, 
                    password: Optional[str] = None, maxusers: int = 0, persistent: bool = True,
                    public: bool = True, registration: bool = True, visiblejids: bool = True, 
                    changesubject: bool = False, anycaninvite: bool = False, changenickname: bool = True, 
                    logenabled: bool = True, registerednickname: bool = False, membersonly: bool = False, 
                    moderated: bool = False, broadcastroles: Optional[List[str]] = None, 
                    owners: Optional[List[str]] = None, admins: Optional[List[str]] = None, 
                    members: Optional[List[str]] = None, outcasts: Optional[List[str]] = None) -> bool:
        """
        Update a chat room.

        Args:
            roomname: The name/id of the room to update
            name: Optional new name of the room
            description: Optional new description text of the room
            servicename: Optional name of the Group Chat Service. Default: 'conference'
            subject: Optional new subject of the room
            password: Optional new password for the room
            maxusers: Optional new maximum number of occupants. Default: 0 (unlimited)
            persistent: Optional flag for persistent rooms. Default: True
            public: Optional flag for public rooms. Default: True
            registration: Optional flag for registration. Default: True
            visiblejids: Optional flag for visible JIDs. Default: True
            changesubject: Optional flag for subject changes. Default: False
            anycaninvite: Optional flag for invitations. Default: False
            changenickname: Optional flag for nickname changes. Default: True
            logenabled: Optional flag for logging. Default: True
            registerednickname: Optional flag for registered nicknames. Default: False
            membersonly: Optional flag for members-only rooms. Default: False
            moderated: Optional flag for moderated rooms. Default: False
            broadcastroles: Optional list of roles whose presence will be broadcasted
            owners: Optional list of room owners
            admins: Optional list of room admins
            members: Optional list of room members
            outcasts: Optional list of outcast users
            
        Returns:
            True if successful
        """
        endpoint = "/".join([self.endpoint, roomname])
        payload = {
            "roomName": roomname,
            "naturalName": name,
            "description": description,
            "subject": subject,
            "password": password,
            "maxUsers": maxusers,
            "persistent": persistent,
            "publicRoom": public,
            "registrationEnabled": registration,
            "canAnyoneDiscoverJID": visiblejids,
            "canOccupantsChangeSubject": changesubject,
            "canOccupantsInvite": anycaninvite,
            "canChangeNickname": changenickname,
            "logEnabled": logenabled,
            "loginRestrictedToNickname": registerednickname,
            "membersOnly": membersonly,
            "moderated": moderated,
            "broadcastPresenceRoles": {"broadcastPresenceRole": broadcastroles},
            "owners": {"owner": owners},
            "admins": {"admin": admins},
            "members": {"member": members},
            "outcasts": {"outcast": outcasts},
        }
        params = {"servicename": servicename}
        return self._submit_request(put, endpoint, json=payload, params=params)

    def grant_user_role(self, roomname: str, username: str, role: str, 
                        servicename: str = "conference") -> bool:
        """
        Grant role to chat room user.

        Args:
            roomname: The exact chat room name
            username: The local username or user JID
            role: Role to grant. One of 'owners', 'admins', 'members', 'outcasts'
            servicename: Optional name of the Group Chat Service. Default: 'conference'
            
        Returns:
            True if successful
        """
        endpoint = "/".join([self.endpoint, roomname, role, username])
        params = {"servicename": servicename}
        return self._submit_request(post, endpoint, params=params)

    def revoke_user_role(self, roomname: str, username: str, role: str, 
                         servicename: str = "conference") -> bool:
        """
        Revoke role from chat room user.

        Args:
            roomname: The exact chat room name
            username: The local username or user JID
            role: Role to revoke. One of 'owners', 'admins', 'members', 'outcasts'
            servicename: Optional name of the Group Chat Service. Default: 'conference'
            
        Returns:
            True if successful
        """
        endpoint = "/".join([self.endpoint, roomname, role, username])
        params = {"servicename": servicename}
        return self._submit_request(delete, endpoint, params=params)
