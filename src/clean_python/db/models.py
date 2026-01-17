"""SQLAlchemy ORM models."""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from clean_python.core import UserProfile

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all ORM models.

    This is the declarative base that all ORM models inherit from.
    It provides common functionality and type annotations for SQLAlchemy.
    """


class UserProfileModel(Base):
    """SQLAlchemy ORM model for UserProfile.

    This model mirrors the Pydantic UserProfile class from core.py,
    providing database persistence with the same validation rules.

    Attributes:
        id: Primary key, auto-incremented integer.
        name: User's full name (1-100 characters, indexed).
        email: User's email address (unique, indexed).
        age: User's age in years (0-120, optional).
        tags: List of user tags stored as JSON.
        created_at: Timestamp when profile was created (UTC).
        updated_at: Timestamp when profile was last updated (UTC).
    """

    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def __init__(self, **kwargs: Any) -> None:
        """Initialize UserProfileModel with default timestamps.

        Args:
            **kwargs: Field values for the model.
        """
        # Set defaults for timestamps if not provided
        now = datetime.now(timezone.utc)
        if "created_at" not in kwargs:
            kwargs["created_at"] = now
        if "updated_at" not in kwargs:
            kwargs["updated_at"] = now
        if "tags" not in kwargs:
            kwargs["tags"] = []
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        """String representation of UserProfileModel.

        Returns:
            String representation with key fields.
        """
        return f"<UserProfileModel(id={self.id}, name='{self.name}', email='{self.email}')>"

    def to_pydantic(self) -> UserProfile:
        """Convert ORM model to Pydantic model.

        This allows seamless conversion from database representation
        to the validated Pydantic model used in business logic.

        Returns:
            UserProfile Pydantic model instance.

        Example:
            >>> db_profile = session.query(UserProfileModel).first()
            >>> pydantic_profile = db_profile.to_pydantic()
            >>> print(pydantic_profile.name)
        """
        logger.debug(
            f"Converting ORM model to Pydantic - id: {self.id}, email: {self.email}, " f"tags_count: {len(self.tags)}"
        )

        try:
            # Note: Pydantic UserProfile doesn't have an id field
            # The created_at is set by Pydantic automatically, so we pass the stored value
            profile = UserProfile(
                name=self.name, email=self.email, age=self.age, tags=self.tags, created_at=self.created_at
            )
            return profile
        except Exception as e:
            logger.error(f"Failed to convert ORM to Pydantic - id: {self.id}, error: {str(e)}", exc_info=True)
            raise

    @classmethod
    def from_pydantic(cls, profile: UserProfile) -> "UserProfileModel":
        """Create ORM model from Pydantic model.

        This allows conversion from the Pydantic model used in business logic
        to the database ORM model for persistence.

        Args:
            profile: Pydantic UserProfile instance.

        Returns:
            UserProfileModel ORM instance (not yet persisted).

        Example:
            >>> pydantic_profile = UserProfile(name="John", email="john@example.com")
            >>> db_profile = UserProfileModel.from_pydantic(pydantic_profile)
            >>> session.add(db_profile)
            >>> session.commit()
        """
        logger.debug(f"Converting Pydantic to ORM model - email: {profile.email}, " f"tags_count: {len(profile.tags)}")

        try:
            return cls(
                name=profile.name,
                email=profile.email,
                age=profile.age,
                tags=profile.tags,
                created_at=profile.created_at,
            )
        except Exception as e:
            logger.error(f"Failed to convert Pydantic to ORM - email: {profile.email}, error: {str(e)}", exc_info=True)
            raise
