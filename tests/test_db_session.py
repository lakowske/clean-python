"""Tests for database session management."""

import pytest

from clean_python.db import DatabaseConfig, DatabaseSession
from clean_python.db.models import UserProfileModel


def test_database_session_initialization(sqlite_config):
    """Test DatabaseSession initialization."""
    db_session = DatabaseSession(sqlite_config)

    assert db_session.config == sqlite_config
    assert db_session.engine is None
    assert db_session._session_factory is None


def test_database_session_initialize(sqlite_config):
    """Test DatabaseSession initialize method."""
    db_session = DatabaseSession(sqlite_config)
    db_session.initialize()

    assert db_session.engine is not None
    assert db_session._session_factory is not None

    db_session.close()


def test_database_session_initialize_with_tables(sqlite_config):
    """Test DatabaseSession initialize with table creation."""
    db_session = DatabaseSession(sqlite_config)
    db_session.initialize(create_tables=True)

    # Verify tables were created by checking engine
    assert db_session.engine is not None

    # Test that we can query (even if no data)
    with db_session.get_session() as session:
        count = session.query(UserProfileModel).count()
        assert count == 0

    db_session.close()


def test_database_session_get_session(db_session_manager):
    """Test getting a session from DatabaseSession."""
    with db_session_manager.get_session() as session:
        assert session is not None
        # Session should be usable
        count = session.query(UserProfileModel).count()
        assert count == 0


def test_database_session_get_session_without_init():
    """Test getting session without initialization fails."""
    config = DatabaseConfig(db_type="sqlite", database=":memory:")
    db_session = DatabaseSession(config)

    with pytest.raises(RuntimeError, match="not initialized"):
        with db_session.get_session():
            pass


def test_database_session_commit_on_success(db_session_manager):
    """Test that session commits on success."""
    with db_session_manager.get_session() as session:
        profile = UserProfileModel(name="John Doe", email="john@example.com", age=30, tags=["test"])
        session.add(profile)
        # Should commit automatically

    # Verify data was committed by creating new session
    with db_session_manager.get_session() as session:
        count = session.query(UserProfileModel).count()
        assert count == 1


def test_database_session_rollback_on_error(db_session_manager):
    """Test that session rolls back on error."""
    try:
        with db_session_manager.get_session() as session:
            profile = UserProfileModel(name="John Doe", email="john@example.com", age=30, tags=["test"])
            session.add(profile)
            session.flush()
            raise ValueError("Test error")
    except ValueError:
        pass

    # Verify data was rolled back
    with db_session_manager.get_session() as session:
        count = session.query(UserProfileModel).count()
        assert count == 0


def test_database_session_close(sqlite_config):
    """Test closing DatabaseSession."""
    db_session = DatabaseSession(sqlite_config)
    db_session.initialize()

    assert db_session.engine is not None

    db_session.close()

    assert db_session.engine is None
    assert db_session._session_factory is None


def test_database_session_context_manager(sqlite_config):
    """Test DatabaseSession as context manager."""
    with DatabaseSession(sqlite_config) as db_session:
        assert db_session.engine is not None
        assert db_session._session_factory is not None

    # Should be closed after context
    assert db_session.engine is None


def test_database_session_double_initialization(sqlite_config):
    """Test that double initialization is handled gracefully."""
    db_session = DatabaseSession(sqlite_config)
    db_session.initialize()
    engine1 = db_session.engine

    # Second initialization should be skipped
    db_session.initialize()
    engine2 = db_session.engine

    assert engine1 is engine2

    db_session.close()


def test_database_session_close_without_init():
    """Test that closing without initialization is safe."""
    config = DatabaseConfig(db_type="sqlite", database=":memory:")
    db_session = DatabaseSession(config)

    # Should not raise
    db_session.close()
