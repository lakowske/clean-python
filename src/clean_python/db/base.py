"""Abstract base repository for database operations."""

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository for CRUD operations.

    This defines the interface that all repositories must implement,
    following the Repository pattern for clean separation between
    business logic and data access.

    Type parameter T represents the entity type (e.g., UserProfile).

    Example:
        >>> class UserProfileRepository(BaseRepository[UserProfile]):
        ...     def create(self, entity: UserProfile) -> UserProfile:
        ...         # Implementation
        ...         pass
    """

    @abstractmethod
    def create(self, entity: T) -> T:
        """Create a new entity in the database.

        Args:
            entity: The entity to create.

        Returns:
            The created entity with database-generated fields populated.

        Raises:
            Exception: If creation fails (e.g., constraint violation).
        """

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Retrieve an entity by its ID.

        Args:
            id: The entity's unique identifier.

        Returns:
            The entity if found, None otherwise.

        Raises:
            Exception: If database query fails.
        """

    @abstractmethod
    def list_all(self, limit: int = 100, offset: int = 0) -> list[T]:
        """List all entities with pagination.

        Args:
            limit: Maximum number of entities to return (default: 100).
            offset: Number of entities to skip (default: 0).

        Returns:
            List of entities (may be empty).

        Raises:
            Exception: If database query fails.
        """

    @abstractmethod
    def update(self, id: int, entity: T) -> Optional[T]:
        """Update an existing entity.

        Args:
            id: The entity's unique identifier.
            entity: The entity with updated values.

        Returns:
            The updated entity if found, None if not found.

        Raises:
            Exception: If update fails (e.g., constraint violation).
        """

    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete an entity by its ID.

        Args:
            id: The entity's unique identifier.

        Returns:
            True if entity was deleted, False if not found.

        Raises:
            Exception: If deletion fails.
        """
