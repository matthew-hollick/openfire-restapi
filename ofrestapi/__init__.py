# -*- coding: utf-8 -*-

__version__ = '0.1.1'

# Define the public API
__all__ = ['Users', 'Muc', 'System', 'Groups', 'Sessions', 'Messages', 'SecurityAuditLog']

# Use absolute imports for Python 3 compatibility
from ofrestapi.users import Users
from ofrestapi.muc import Muc
from ofrestapi.system import System
from ofrestapi.groups import Groups
from ofrestapi.sessions import Sessions
from ofrestapi.messages import Messages
from ofrestapi.security import SecurityAuditLog
