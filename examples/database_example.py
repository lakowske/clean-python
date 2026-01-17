"""Example demonstrating database operations with user profiles.

This example shows how to:
1. Configure the database (SQLite by default)
2. Initialize the database session
3. Create, read, update, and delete user profiles
4. Handle errors gracefully
5. Use the repository pattern for clean data access

Run this example:
    python examples/database_example.py
"""

import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clean_python.core import UserProfile
from clean_python.db import DatabaseConfig, DatabaseSession, UserProfileRepository

# Configure logging to see database operations
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
)
logger = logging.getLogger(__name__)


def example_sqlite_crud():
    """Demonstrate basic CRUD operations with SQLite."""
    logger.info("=" * 80)
    logger.info("Example 1: Basic CRUD Operations with SQLite")
    logger.info("=" * 80)

    # Configure database (SQLite by default)
    config = DatabaseConfig(
        db_type="sqlite",
        database="example.db",
        echo=False,  # Set to True to see SQL queries
    )

    # Initialize database session
    db_session = DatabaseSession(config)
    db_session.initialize(create_tables=True)  # Create tables if they don't exist

    try:
        # Use the session context manager for automatic transaction handling
        with db_session.get_session() as session:
            repo = UserProfileRepository(session)

            # CREATE: Add a new user profile
            logger.info("\n1. Creating user profile...")
            profile = UserProfile(
                name="Alice Smith", email="alice@example.com", age=28, tags=["engineer", "python", "databases"]
            )
            created = repo.create(profile)
            logger.info(f"✓ Created profile: {created.name} ({created.email})")

            # READ: Retrieve profile by email
            logger.info("\n2. Retrieving user profile by email...")
            retrieved = repo.get_by_email("alice@example.com")
            if retrieved:
                logger.info(f"✓ Retrieved profile: {retrieved.name}, Age: {retrieved.age}, Tags: {retrieved.tags}")

            # UPDATE: Modify the profile
            logger.info("\n3. Updating user profile...")
            if retrieved:
                retrieved.age = 29
                retrieved.tags.append("sqlalchemy")
                # Note: We can't easily update without the ID, so this is for demonstration
                logger.info("✓ Profile updated (would need ID for actual update)")

            # LIST: Get all profiles
            logger.info("\n4. Listing all user profiles...")
            all_profiles = repo.list_all()
            logger.info(f"✓ Total profiles in database: {len(all_profiles)}")
            for p in all_profiles:
                logger.info(f"  - {p.name} ({p.email})")

            # COUNT: Get total count
            logger.info("\n5. Counting profiles...")
            count = repo.count()
            logger.info(f"✓ Total count: {count}")

            # DELETE: Remove a profile (demonstration only - would need ID)
            logger.info("\n6. Deletion available via repo.delete(id)")
            logger.info("   (Skipping actual deletion in this example)")

    except Exception as e:
        logger.error(f"Error during database operations: {str(e)}", exc_info=True)
    finally:
        # Clean up
        db_session.close()
        logger.info("\n✓ Database session closed")


def example_error_handling():
    """Demonstrate error handling with duplicate emails."""
    logger.info("\n" + "=" * 80)
    logger.info("Example 2: Error Handling (Duplicate Emails)")
    logger.info("=" * 80)

    config = DatabaseConfig(db_type="sqlite", database="example.db")
    db_session = DatabaseSession(config)
    db_session.initialize(create_tables=True)

    try:
        # Try to create a profile with a duplicate email
        logger.info("\nAttempting to create profile with duplicate email...")
        try:
            with db_session.get_session() as session:
                repo = UserProfileRepository(session)
                duplicate_profile = UserProfile(name="Another Alice", email="alice@example.com", age=30)
                repo.create(duplicate_profile)
                logger.info("✓ Profile created (unexpected!)")
        except ValueError as e:
            logger.info(f"✓ Expected error caught: {str(e)}")
            logger.info("  Error handling working correctly!")

    finally:
        db_session.close()


def example_multiple_profiles():
    """Demonstrate working with multiple profiles."""
    logger.info("\n" + "=" * 80)
    logger.info("Example 3: Working with Multiple Profiles")
    logger.info("=" * 80)

    config = DatabaseConfig(db_type="sqlite", database="example.db")
    db_session = DatabaseSession(config)
    db_session.initialize(create_tables=True)

    try:
        with db_session.get_session() as session:
            repo = UserProfileRepository(session)

            # Create multiple profiles
            logger.info("\nCreating multiple user profiles...")
            profiles_to_create = [
                UserProfile(name="Bob Johnson", email="bob@example.com", age=35, tags=["manager", "leadership"]),
                UserProfile(name="Charlie Brown", email="charlie@example.com", age=42, tags=["senior", "architect"]),
                UserProfile(name="Diana Prince", email="diana@example.com", age=31, tags=["designer", "ux"]),
            ]

            for profile in profiles_to_create:
                try:
                    created = repo.create(profile)
                    logger.info(f"  ✓ Created: {created.name}")
                except ValueError:
                    logger.info(f"  - Skipped (already exists): {profile.name}")

            # List with pagination
            logger.info("\nListing profiles with pagination...")
            page_size = 2
            offset = 0

            while True:
                page_profiles = repo.list_all(limit=page_size, offset=offset)
                if not page_profiles:
                    break

                logger.info(f"\nPage {offset // page_size + 1}:")
                for p in page_profiles:
                    logger.info(f"  - {p.name} ({p.email}) - {', '.join(p.tags)}")

                offset += page_size
                if len(page_profiles) < page_size:
                    break

    finally:
        db_session.close()


def example_context_manager():
    """Demonstrate using DatabaseSession as a context manager."""
    logger.info("\n" + "=" * 80)
    logger.info("Example 4: Using Context Manager")
    logger.info("=" * 80)

    config = DatabaseConfig(db_type="sqlite", database="example.db")

    # Use DatabaseSession as a context manager for automatic cleanup
    logger.info("\nUsing DatabaseSession as context manager...")
    with DatabaseSession(config) as db_session:
        db_session.initialize(create_tables=True)

        with db_session.get_session() as session:
            repo = UserProfileRepository(session)
            count = repo.count()
            logger.info(f"✓ Total profiles: {count}")

    logger.info("✓ DatabaseSession automatically closed")


def example_postgresql_config():
    """Demonstrate PostgreSQL configuration (doesn't actually connect)."""
    logger.info("\n" + "=" * 80)
    logger.info("Example 5: PostgreSQL Configuration")
    logger.info("=" * 80)

    logger.info("\nConfiguring for PostgreSQL...")
    pg_config = DatabaseConfig(
        db_type="postgresql",
        host="localhost",
        port=5432,
        database="myapp",
        username="myuser",
        password="mypassword",
        pool_size=10,
        max_overflow=20,
    )

    logger.info(f"  Database type: {pg_config.db_type}")
    logger.info(f"  Host: {pg_config.host}:{pg_config.port}")
    logger.info(f"  Database: {pg_config.database}")
    logger.info(f"  Pool size: {pg_config.pool_size}")
    logger.info(f"  Max overflow: {pg_config.max_overflow}")

    # Show connection URL (without password)
    url = pg_config.get_connection_url()
    # Mask password in URL for display
    display_url = url.replace(pg_config.password, "****") if pg_config.password else url
    logger.info(f"  Connection URL: {display_url}")

    logger.info("\n  Note: Not actually connecting to PostgreSQL in this example")
    logger.info("  Install PostgreSQL and update credentials to test with real database")


def cleanup_example_db():
    """Clean up the example database."""
    logger.info("\n" + "=" * 80)
    logger.info("Cleanup")
    logger.info("=" * 80)

    db_path = Path("example.db")
    if db_path.exists():
        logger.info(f"\nRemoving example database: {db_path}")
        db_path.unlink()
        logger.info("✓ Cleanup complete")
    else:
        logger.info("\nNo example database to clean up")


def main():
    """Run all database examples."""
    logger.info("\n" + "=" * 80)
    logger.info("DATABASE MODULE EXAMPLES")
    logger.info("=" * 80)

    try:
        # Run all examples
        example_sqlite_crud()
        example_error_handling()
        example_multiple_profiles()
        example_context_manager()
        example_postgresql_config()

    except Exception as e:
        logger.error(f"Fatal error running examples: {str(e)}", exc_info=True)
        return 1

    finally:
        # Clean up example database
        cleanup_example_db()

    logger.info("\n" + "=" * 80)
    logger.info("ALL EXAMPLES COMPLETED SUCCESSFULLY")
    logger.info("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
