"""
Custom exception classes for the AI Prompt Manager application.
"""

from .base import (
    BaseAppException,
    ServiceException,
    ValidationException,
    DatabaseException,
    AuthenticationException,
    AuthorizationException
)

__all__ = [
    'BaseAppException',
    'ServiceException', 
    'ValidationException',
    'DatabaseException',
    'AuthenticationException',
    'AuthorizationException'
]