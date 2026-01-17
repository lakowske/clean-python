"""Database module for SQL data store operations.

This module provides a configurable SQL data store with support for
SQLite, PostgreSQL, and MySQL databases. It includes:

- DatabaseConfig: Configuration with environment variable support
- DatabaseSession: Session management and connection pooling
- Base: Declarative base for ORM models
- UserProfileModel: SQLAlchemy ORM model for user profiles
- BaseRepository: Abstract repository interface
- UserProfileRepository: Repository for user profile CRUD operations

Example:
    >>> from clean_python.db import DatabaseConfig, DatabaseSession, UserProfileRepository
    >>> from clean_python.core import UserProfile
    >>>
    >>> # Configure database
    >>> config = DatabaseConfig(db_type="sqlite", database="app.db")
    >>> db_session = DatabaseSession(config)
    >>> db_session.initialize(create_tables=True)
    >>>
    >>> # Use repository for CRUD operations
    >>> with db_session.get_session() as session:
    ...     repo = UserProfileRepository(session)
    ...     profile = UserProfile(name="John Doe", email="john@example.com")
    ...     created = repo.create(profile)
"""

from clean_python.db.base import BaseRepository
from clean_python.db.config import DatabaseConfig, DatabaseType
from clean_python.db.models import Base, UserProfileModel
from clean_python.db.repository import UserProfileRepository
from clean_python.db.session import DatabaseSession

__all__ = [
    "DatabaseConfig",
    "DatabaseType",
    "DatabaseSession",
    "Base",
    "UserProfileModel",
    "BaseRepository",
    "UserProfileRepository",
]
