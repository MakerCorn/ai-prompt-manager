"""
Base classes and shared functionality for the AI Prompt Manager application.
"""

from .database_manager import BaseDatabaseManager, DatabaseManager
from .service_base import BaseService, ServiceResult
from .repository_base import BaseRepository

__all__ = [
    'BaseDatabaseManager',
    'DatabaseManager',
    'BaseService',
    'ServiceResult', 
    'BaseRepository'
]