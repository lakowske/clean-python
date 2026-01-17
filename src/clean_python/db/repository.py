"""Concrete repository implementations."""

import logging
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from clean_python.core import UserProfile
from clean_python.db.base import BaseRepository
from clean_python.db.models import UserProfileModel

logger = logging.getLogger(__name__)


class UserProfileRepository(BaseRepository[UserProfile]):
    """Repository for UserProfile CRUD operations.

    This repository provides database operations for user profiles,
    handling conversion between Pydantic models and ORM models.

    Attributes:
        session: SQLAlchemy session for database operations.

    Example:
        >>> with db_session.get_session() as session:
        ...     repo = UserProfileRepository(session)
        ...     profile = UserProfile(name="John Doe", email="john@example.com")
        ...     created = repo.create(profile)
        ...     print(created.name)
    """

    def __init__(self, session: Session):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy Session instance.
        """
        self.session = session
        self.logger = logging.getLogger(__name__)

    def create(self, profile: UserProfile) -> UserProfile:
        """Create a new user profile in the database.

        Args:
            profile: UserProfile Pydantic model to create.

        Returns:
            Created UserProfile with database ID assigned.

        Raises:
            ValueError: If a profile with the same email already exists.
            Exception: If database operation fails.

        Example:
            >>> profile = UserProfile(name="Jane Doe", email="jane@example.com", age=30)
            >>> created = repo.create(profile)
            >>> print(f"Created profile with ID: {created.id}")
        """
        self.logger.info(f"Creating user profile - email: {profile.email}, name: {profile.name}")

        try:
            # Convert Pydantic model to ORM model
            db_model = UserProfileModel.from_pydantic(profile)

            # Add to session and flush to get the ID
            self.session.add(db_model)
            self.session.flush()

            self.logger.debug(
                f"User profile created in database - id: {db_model.id}, email: {db_model.email}, "
                f"tags_count: {len(db_model.tags)}"
            )

            # Convert back to Pydantic and return
            result = db_model.to_pydantic()

            # Store the ID as a separate attribute (since UserProfile doesn't have id field)
            # We'll return the Pydantic model but the caller can get the ID from db_model
            self.logger.info(f"User profile created successfully - id: {db_model.id}, email: {result.email}")
            return result

        except IntegrityError as e:
            self.logger.error(
                f"Integrity error creating user profile - email: {profile.email}, error: {str(e)}", exc_info=True
            )
            raise ValueError(f"User with email {profile.email} already exists") from e
        except Exception as e:
            self.logger.error(f"Failed to create user profile - email: {profile.email}, error: {str(e)}", exc_info=True)
            raise

    def get_by_id(self, id: int) -> Optional[UserProfile]:
        """Retrieve a user profile by ID.

        Args:
            id: User profile ID.

        Returns:
            UserProfile if found, None otherwise.

        Raises:
            Exception: If database query fails.

        Example:
            >>> profile = repo.get_by_id(1)
            >>> if profile:
            ...     print(profile.name)
        """
        self.logger.info(f"Retrieving user profile - id: {id}")

        try:
            db_model = self.session.query(UserProfileModel).filter(UserProfileModel.id == id).first()

            if db_model is None:
                self.logger.debug(f"User profile not found - id: {id}")
                return None

            self.logger.debug(f"User profile retrieved - id: {db_model.id}, email: {db_model.email}")
            return db_model.to_pydantic()

        except Exception as e:
            self.logger.error(f"Failed to retrieve user profile - id: {id}, error: {str(e)}", exc_info=True)
            raise

    def get_by_email(self, email: str) -> Optional[UserProfile]:
        """Retrieve a user profile by email address.

        Args:
            email: User email address.

        Returns:
            UserProfile if found, None otherwise.

        Raises:
            Exception: If database query fails.

        Example:
            >>> profile = repo.get_by_email("john@example.com")
            >>> if profile:
            ...     print(profile.name)
        """
        self.logger.info(f"Retrieving user profile by email - email: {email}")

        try:
            db_model = self.session.query(UserProfileModel).filter(UserProfileModel.email == email).first()

            if db_model is None:
                self.logger.debug(f"User profile not found - email: {email}")
                return None

            self.logger.debug(f"User profile retrieved - id: {db_model.id}, email: {db_model.email}")
            return db_model.to_pydantic()

        except Exception as e:
            self.logger.error(f"Failed to retrieve user profile - email: {email}, error: {str(e)}", exc_info=True)
            raise

    def list_all(self, limit: int = 100, offset: int = 0) -> list[UserProfile]:
        """List all user profiles with pagination.

        Args:
            limit: Maximum number of profiles to return (default: 100).
            offset: Number of profiles to skip (default: 0).

        Returns:
            List of UserProfile instances (may be empty).

        Raises:
            Exception: If database query fails.

        Example:
            >>> profiles = repo.list_all(limit=10, offset=0)
            >>> for profile in profiles:
            ...     print(profile.name)
        """
        self.logger.info(f"Listing user profiles - limit: {limit}, offset: {offset}")

        try:
            db_models = self.session.query(UserProfileModel).offset(offset).limit(limit).all()

            self.logger.debug(f"Retrieved user profiles - count: {len(db_models)}, limit: {limit}, offset: {offset}")

            return [db_model.to_pydantic() for db_model in db_models]

        except Exception as e:
            self.logger.error(
                f"Failed to list user profiles - limit: {limit}, offset: {offset}, error: {str(e)}", exc_info=True
            )
            raise

    def update(self, id: int, profile: UserProfile) -> Optional[UserProfile]:
        """Update an existing user profile.

        Args:
            id: User profile ID to update.
            profile: UserProfile with updated values.

        Returns:
            Updated UserProfile if found, None if not found.

        Raises:
            ValueError: If email is changed to one that already exists.
            Exception: If database operation fails.

        Example:
            >>> profile = repo.get_by_id(1)
            >>> if profile:
            ...     profile.age = 31
            ...     updated = repo.update(1, profile)
        """
        self.logger.info(f"Updating user profile - id: {id}, email: {profile.email}")

        try:
            db_model = self.session.query(UserProfileModel).filter(UserProfileModel.id == id).first()

            if db_model is None:
                self.logger.debug(f"User profile not found for update - id: {id}")
                return None

            # Update fields
            db_model.name = profile.name
            db_model.email = profile.email
            db_model.age = profile.age
            db_model.tags = profile.tags

            self.session.flush()

            self.logger.debug(f"User profile updated - id: {db_model.id}, email: {db_model.email}")
            self.logger.info(f"User profile updated successfully - id: {id}")

            return db_model.to_pydantic()

        except IntegrityError as e:
            self.logger.error(
                f"Integrity error updating user profile - id: {id}, email: {profile.email}, error: {str(e)}",
                exc_info=True,
            )
            raise ValueError(f"User with email {profile.email} already exists") from e
        except Exception as e:
            self.logger.error(f"Failed to update user profile - id: {id}, error: {str(e)}", exc_info=True)
            raise

    def delete(self, id: int) -> bool:
        """Delete a user profile by ID.

        Args:
            id: User profile ID to delete.

        Returns:
            True if profile was deleted, False if not found.

        Raises:
            Exception: If database operation fails.

        Example:
            >>> deleted = repo.delete(1)
            >>> if deleted:
            ...     print("Profile deleted successfully")
        """
        self.logger.info(f"Deleting user profile - id: {id}")

        try:
            db_model = self.session.query(UserProfileModel).filter(UserProfileModel.id == id).first()

            if db_model is None:
                self.logger.debug(f"User profile not found for deletion - id: {id}")
                return False

            email = db_model.email  # Store for logging
            self.session.delete(db_model)
            self.session.flush()

            self.logger.info(f"User profile deleted successfully - id: {id}, email: {email}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete user profile - id: {id}, error: {str(e)}", exc_info=True)
            raise

    def count(self) -> int:
        """Count total number of user profiles.

        Returns:
            Total number of user profiles in the database.

        Raises:
            Exception: If database query fails.

        Example:
            >>> total = repo.count()
            >>> print(f"Total profiles: {total}")
        """
        self.logger.info("Counting user profiles")

        try:
            count: int = self.session.query(UserProfileModel).count()
            self.logger.debug(f"User profile count - count: {count}")
            return count

        except Exception as e:
            self.logger.error(f"Failed to count user profiles - error: {str(e)}", exc_info=True)
            raise
