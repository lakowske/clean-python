"""Configuration for pytest."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from clean_python.db import Base, DatabaseConfig, DatabaseSession, UserProfileRepository


@pytest.fixture
def sqlite_config():
    """In-memory SQLite configuration for testing.

    Returns:
        DatabaseConfig instance configured for in-memory SQLite.
    """
    return DatabaseConfig(db_type="sqlite", database=":memory:", echo=False)


@pytest.fixture
def db_engine(sqlite_config):
    """Create test database engine.

    Args:
        sqlite_config: DatabaseConfig fixture.

    Yields:
        SQLAlchemy Engine instance with tables created.
    """
    engine = create_engine(sqlite_config.get_connection_url())
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Create test database session.

    Args:
        db_engine: SQLAlchemy Engine fixture.

    Yields:
        SQLAlchemy Session instance.
    """
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def user_repository(db_session):
    """Create UserProfileRepository for testing.

    Args:
        db_session: SQLAlchemy Session fixture.

    Returns:
        UserProfileRepository instance.
    """
    return UserProfileRepository(db_session)


@pytest.fixture
def db_session_manager(sqlite_config):
    """Create DatabaseSession manager for testing.

    Args:
        sqlite_config: DatabaseConfig fixture.

    Yields:
        DatabaseSession instance initialized with tables.
    """
    db_session_mgr = DatabaseSession(sqlite_config)
    db_session_mgr.initialize(create_tables=True)
    yield db_session_mgr
    db_session_mgr.close()
