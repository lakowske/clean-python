"""Database configuration module."""

import logging
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)

DatabaseType = Literal["sqlite", "postgresql", "mysql"]


class DatabaseConfig(BaseModel):
    """Database configuration with environment variable support.

    This configuration supports multiple database backends (SQLite, PostgreSQL, MySQL)
    and can be configured via environment variables with DB_ prefix.

    Attributes:
        db_type: Type of database (sqlite, postgresql, mysql).
        host: Database server host (not required for SQLite).
        port: Database server port (defaults based on db_type).
        database: Database name or path for SQLite.
        username: Database username (not required for SQLite).
        password: Database password (not required for SQLite).
        echo: Whether to log SQL queries (useful for debugging).
        pool_size: Number of connections to maintain in the pool.
        max_overflow: Maximum number of connections that can be created beyond pool_size.

    Example:
        >>> config = DatabaseConfig(db_type="sqlite", database="app.db")
        >>> url = config.get_connection_url()
        >>> print(url)
        sqlite:///app.db
    """

    db_type: DatabaseType = Field(default="sqlite", description="Database type")
    host: Optional[str] = Field(default=None, description="Database host")
    port: Optional[int] = Field(default=None, description="Database port")
    database: str = Field(default="app.db", description="Database name or path")
    username: Optional[str] = Field(default=None, description="Database username")
    password: Optional[str] = Field(default=None, description="Database password")
    echo: bool = Field(default=False, description="Log SQL queries")
    pool_size: int = Field(default=5, ge=1, description="Connection pool size")
    max_overflow: int = Field(default=10, ge=0, description="Max overflow connections")

    model_config = {"env_prefix": "DB_"}

    @model_validator(mode="after")  # type: ignore[misc]
    def set_default_port(self) -> "DatabaseConfig":
        """Set default port based on database type if not provided.

        Returns:
            Self with port set to default if needed.
        """
        if self.port is None:
            if self.db_type == "postgresql":
                self.port = 5432
            elif self.db_type == "mysql":
                self.port = 3306
        return self

    def get_connection_url(self) -> str:
        """Generate SQLAlchemy connection URL.

        Returns:
            SQLAlchemy database URL string.

        Raises:
            ValueError: If required connection parameters are missing.

        Example:
            >>> config = DatabaseConfig(db_type="sqlite", database="test.db")
            >>> config.get_connection_url()
            'sqlite:///test.db'
        """
        logger.debug(
            f"Generating connection URL - db_type: {self.db_type}, "
            f"database: {self.database}, host: {self.host}, port: {self.port}"
        )

        if self.db_type == "sqlite":
            url = f"sqlite:///{self.database}"
            logger.debug(f"Generated SQLite URL - url: {url}")
            return url

        # For PostgreSQL and MySQL, we need host, username, and password
        if not self.host:
            error_msg = f"{self.db_type} requires a host"
            logger.error(f"Missing required parameter - db_type: {self.db_type}, error: {error_msg}")
            raise ValueError(error_msg)

        if not self.username:
            error_msg = f"{self.db_type} requires a username"
            logger.error(f"Missing required parameter - db_type: {self.db_type}, error: {error_msg}")
            raise ValueError(error_msg)

        # Build connection URL
        if self.db_type == "postgresql":
            driver = "postgresql+psycopg2"
        elif self.db_type == "mysql":
            driver = "mysql+pymysql"
        else:
            error_msg = f"Unsupported database type: {self.db_type}"
            logger.error(f"Invalid database type - db_type: {self.db_type}")
            raise ValueError(error_msg)

        # Build URL with credentials
        if self.password:
            url = f"{driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            url = f"{driver}://{self.username}@{self.host}:{self.port}/{self.database}"

        # Don't log the full URL as it may contain password
        logger.debug(
            f"Generated database URL - driver: {driver}, host: {self.host}, "
            f"port: {self.port}, database: {self.database}, username: {self.username}"
        )

        return url

    def get_engine_kwargs(self) -> dict[str, Any]:
        """Get keyword arguments for SQLAlchemy create_engine.

        Returns:
            Dictionary of engine configuration parameters.

        Example:
            >>> config = DatabaseConfig(pool_size=10, max_overflow=20)
            >>> kwargs = config.get_engine_kwargs()
            >>> kwargs["pool_size"]
            10
        """
        kwargs: dict[str, Any] = {"echo": self.echo}

        # Connection pooling is only for non-SQLite databases
        if self.db_type != "sqlite":
            kwargs["pool_size"] = self.pool_size
            kwargs["max_overflow"] = self.max_overflow
            kwargs["pool_pre_ping"] = True  # Verify connections before using

        logger.debug(f"Generated engine kwargs - kwargs: {kwargs}")
        return kwargs
