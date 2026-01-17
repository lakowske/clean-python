"""Tests for database configuration."""

import pytest

from clean_python.db import DatabaseConfig


def test_sqlite_config_default():
    """Test SQLite configuration with defaults."""
    config = DatabaseConfig()

    assert config.db_type == "sqlite"
    assert config.database == "app.db"
    assert config.echo is False
    assert config.pool_size == 5
    assert config.max_overflow == 10


def test_sqlite_config_custom():
    """Test SQLite configuration with custom values."""
    config = DatabaseConfig(db_type="sqlite", database="test.db", echo=True, pool_size=10)

    assert config.db_type == "sqlite"
    assert config.database == "test.db"
    assert config.echo is True
    assert config.pool_size == 10


def test_sqlite_config_in_memory():
    """Test SQLite in-memory database configuration."""
    config = DatabaseConfig(db_type="sqlite", database=":memory:")

    assert config.db_type == "sqlite"
    assert config.database == ":memory:"


def test_sqlite_connection_url():
    """Test SQLite connection URL generation."""
    config = DatabaseConfig(db_type="sqlite", database="test.db")
    url = config.get_connection_url()

    assert url == "sqlite:///test.db"


def test_sqlite_in_memory_connection_url():
    """Test SQLite in-memory connection URL generation."""
    config = DatabaseConfig(db_type="sqlite", database=":memory:")
    url = config.get_connection_url()

    assert url == "sqlite:///:memory:"


def test_postgresql_config():
    """Test PostgreSQL configuration."""
    config = DatabaseConfig(
        db_type="postgresql", host="localhost", database="testdb", username="testuser", password="testpass"
    )

    assert config.db_type == "postgresql"
    assert config.host == "localhost"
    assert config.port == 5432  # Default port
    assert config.database == "testdb"
    assert config.username == "testuser"
    assert config.password == "testpass"


def test_postgresql_config_custom_port():
    """Test PostgreSQL configuration with custom port."""
    config = DatabaseConfig(
        db_type="postgresql", host="localhost", port=5433, database="testdb", username="testuser", password="testpass"
    )

    assert config.port == 5433


def test_postgresql_connection_url():
    """Test PostgreSQL connection URL generation."""
    config = DatabaseConfig(
        db_type="postgresql", host="localhost", database="testdb", username="testuser", password="testpass"
    )
    url = config.get_connection_url()

    assert url == "postgresql+psycopg2://testuser:testpass@localhost:5432/testdb"


def test_postgresql_connection_url_without_password():
    """Test PostgreSQL connection URL without password."""
    config = DatabaseConfig(db_type="postgresql", host="localhost", database="testdb", username="testuser")
    url = config.get_connection_url()

    assert url == "postgresql+psycopg2://testuser@localhost:5432/testdb"


def test_postgresql_missing_host():
    """Test PostgreSQL configuration fails without host."""
    config = DatabaseConfig(db_type="postgresql", database="testdb", username="testuser")

    with pytest.raises(ValueError, match="requires a host"):
        config.get_connection_url()


def test_postgresql_missing_username():
    """Test PostgreSQL configuration fails without username."""
    config = DatabaseConfig(db_type="postgresql", host="localhost", database="testdb")

    with pytest.raises(ValueError, match="requires a username"):
        config.get_connection_url()


def test_mysql_config():
    """Test MySQL configuration."""
    config = DatabaseConfig(
        db_type="mysql", host="localhost", database="testdb", username="testuser", password="testpass"
    )

    assert config.db_type == "mysql"
    assert config.host == "localhost"
    assert config.port == 3306  # Default port
    assert config.database == "testdb"


def test_mysql_connection_url():
    """Test MySQL connection URL generation."""
    config = DatabaseConfig(
        db_type="mysql", host="localhost", database="testdb", username="testuser", password="testpass"
    )
    url = config.get_connection_url()

    assert url == "mysql+pymysql://testuser:testpass@localhost:3306/testdb"


def test_engine_kwargs_sqlite():
    """Test engine kwargs for SQLite."""
    config = DatabaseConfig(db_type="sqlite", database="test.db", echo=True)
    kwargs = config.get_engine_kwargs()

    assert kwargs["echo"] is True
    assert "pool_size" not in kwargs  # No pooling for SQLite
    assert "max_overflow" not in kwargs


def test_engine_kwargs_postgresql():
    """Test engine kwargs for PostgreSQL."""
    config = DatabaseConfig(
        db_type="postgresql",
        host="localhost",
        database="testdb",
        username="testuser",
        echo=True,
        pool_size=10,
        max_overflow=20,
    )
    kwargs = config.get_engine_kwargs()

    assert kwargs["echo"] is True
    assert kwargs["pool_size"] == 10
    assert kwargs["max_overflow"] == 20
    assert kwargs["pool_pre_ping"] is True


def test_config_validation_pool_size():
    """Test configuration validation for pool size."""
    with pytest.raises(ValueError):
        DatabaseConfig(pool_size=0)  # Must be >= 1


def test_config_validation_max_overflow():
    """Test configuration validation for max overflow."""
    with pytest.raises(ValueError):
        DatabaseConfig(max_overflow=-1)  # Must be >= 0
