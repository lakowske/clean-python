"""Database session management."""

import logging
from collections.abc import Generator
from contextlib import contextmanager
from typing import Optional

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from clean_python.db.config import DatabaseConfig
from clean_python.db.models import Base

logger = logging.getLogger(__name__)


class DatabaseSession:
    """Manages database connections and sessions.

    This class handles database engine initialization, connection pooling,
    and provides session management through context managers.

    Attributes:
        config: DatabaseConfig instance with connection parameters.
        engine: SQLAlchemy engine (None until initialized).

    Example:
        >>> config = DatabaseConfig(db_type="sqlite", database="app.db")
        >>> db_session = DatabaseSession(config)
        >>> db_session.initialize()
        >>> with db_session.get_session() as session:
        ...     # Perform database operations
        ...     pass
    """

    def __init__(self, config: DatabaseConfig):
        """Initialize DatabaseSession with configuration.

        Args:
            config: DatabaseConfig instance.
        """
        logger.info(f"Initializing DatabaseSession - db_type: {config.db_type}, database: {config.database}")
        self.config = config
        self.engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None

    def initialize(self, create_tables: bool = False) -> None:
        """Initialize database engine and session factory.

        This method creates the SQLAlchemy engine with connection pooling
        and sets up the session factory. Call this once during application startup.

        Args:
            create_tables: Whether to create all tables defined in Base metadata.
                          Useful for development and testing. For production,
                          use Alembic migrations instead.

        Raises:
            Exception: If engine creation or table creation fails.

        Example:
            >>> db_session = DatabaseSession(config)
            >>> db_session.initialize(create_tables=True)  # For testing
        """
        if self.engine is not None:
            logger.warning("DatabaseSession already initialized - skipping re-initialization")
            return

        try:
            # Get connection URL
            url = self.config.get_connection_url()
            logger.info(
                f"Creating database engine - db_type: {self.config.db_type}, "
                f"database: {self.config.database}, echo: {self.config.echo}"
            )

            # Create engine with configuration
            engine_kwargs = self.config.get_engine_kwargs()
            self.engine = create_engine(url, **engine_kwargs)

            # Test the connection
            with self.engine.connect() as conn:
                logger.debug("Database connection test successful")

            # Create session factory
            self._session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
            logger.info("Database session factory created successfully")

            # Create tables if requested
            if create_tables:
                logger.info("Creating database tables from metadata")
                Base.metadata.create_all(self.engine)
                logger.info("Database tables created successfully")

        except Exception as e:
            logger.error(
                f"Failed to initialize database - db_type: {self.config.db_type}, "
                f"database: {self.config.database}, error: {str(e)}",
                exc_info=True,
            )
            raise

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Context manager for database sessions.

        This provides a session with automatic commit/rollback handling.
        The session is committed if no exceptions occur, otherwise rolled back.

        Yields:
            SQLAlchemy Session instance.

        Raises:
            RuntimeError: If DatabaseSession has not been initialized.
            Exception: Any exception from database operations (after rollback).

        Example:
            >>> with db_session.get_session() as session:
            ...     profile = UserProfileModel(name="John", email="john@example.com")
            ...     session.add(profile)
            ...     # Automatic commit on success, rollback on exception
        """
        if self._session_factory is None:
            error_msg = "DatabaseSession not initialized. Call initialize() first."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        session = self._session_factory()
        logger.debug(f"Database session created - session_id: {id(session)}")

        try:
            yield session
            session.commit()
            logger.debug(f"Database session committed - session_id: {id(session)}")
        except Exception as e:
            session.rollback()
            logger.error(
                f"Database session error, rolled back - session_id: {id(session)}, error: {str(e)}", exc_info=True
            )
            raise
        finally:
            session.close()
            logger.debug(f"Database session closed - session_id: {id(session)}")

    def close(self) -> None:
        """Close the database engine and clean up resources.

        Call this during application shutdown to properly close
        all database connections.

        Example:
            >>> db_session.close()
        """
        if self.engine is not None:
            logger.info(f"Closing database engine - db_type: {self.config.db_type}")
            self.engine.dispose()
            self.engine = None
            self._session_factory = None
            logger.info("Database engine closed successfully")
        else:
            logger.debug("Database engine already closed or not initialized")

    def __enter__(self) -> "DatabaseSession":
        """Enter context manager - initialize database.

        Returns:
            Self for use in with statement.
        """
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager - close database.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_val: Exception value if an exception occurred.
            exc_tb: Exception traceback if an exception occurred.
        """
        self.close()
