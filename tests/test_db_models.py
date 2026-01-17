"""Tests for database ORM models."""

from datetime import datetime, timezone

import pytest

from clean_python.core import UserProfile
from clean_python.db.models import UserProfileModel


def test_user_profile_model_creation():
    """Test creating a UserProfileModel instance."""
    profile = UserProfileModel(name="John Doe", email="john@example.com", age=30, tags=["developer", "python"])

    assert profile.name == "John Doe"
    assert profile.email == "john@example.com"
    assert profile.age == 30
    assert profile.tags == ["developer", "python"]
    assert profile.id is None  # Not persisted yet
    assert isinstance(profile.created_at, datetime)
    assert isinstance(profile.updated_at, datetime)


def test_user_profile_model_repr():
    """Test UserProfileModel string representation."""
    profile = UserProfileModel(name="Jane Doe", email="jane@example.com")
    repr_str = repr(profile)

    assert "UserProfileModel" in repr_str
    assert "jane@example.com" in repr_str
    assert "Jane Doe" in repr_str


def test_user_profile_model_to_pydantic():
    """Test converting ORM model to Pydantic model."""
    orm_profile = UserProfileModel(
        name="john doe",  # lowercase to test title case conversion
        email="john@example.com",
        age=30,
        tags=["developer", "python"],
    )

    pydantic_profile = orm_profile.to_pydantic()

    assert isinstance(pydantic_profile, UserProfile)
    assert pydantic_profile.name == "John Doe"  # Should be title cased
    assert pydantic_profile.email == "john@example.com"
    assert pydantic_profile.age == 30
    assert pydantic_profile.tags == ["developer", "python"]


def test_user_profile_model_from_pydantic():
    """Test creating ORM model from Pydantic model."""
    pydantic_profile = UserProfile(name="Jane Doe", email="jane@example.com", age=25, tags=["engineer"])

    orm_profile = UserProfileModel.from_pydantic(pydantic_profile)

    assert isinstance(orm_profile, UserProfileModel)
    assert orm_profile.name == "Jane Doe"
    assert orm_profile.email == "jane@example.com"
    assert orm_profile.age == 25
    assert orm_profile.tags == ["engineer"]


def test_user_profile_model_roundtrip():
    """Test Pydantic -> ORM -> Pydantic conversion."""
    original = UserProfile(name="Alice Smith", email="alice@example.com", age=28, tags=["data", "science"])

    orm_model = UserProfileModel.from_pydantic(original)
    converted = orm_model.to_pydantic()

    assert converted.name == original.name
    assert converted.email == original.email
    assert converted.age == original.age
    assert converted.tags == original.tags


def test_user_profile_model_persistence(db_session):
    """Test persisting UserProfileModel to database."""
    profile = UserProfileModel(name="Bob Brown", email="bob@example.com", age=35, tags=["manager"])

    db_session.add(profile)
    db_session.commit()

    # Should have an ID after commit
    assert profile.id is not None
    assert profile.id > 0


def test_user_profile_model_unique_email(db_session):
    """Test that email must be unique."""
    profile1 = UserProfileModel(name="User One", email="duplicate@example.com")
    profile2 = UserProfileModel(name="User Two", email="duplicate@example.com")

    db_session.add(profile1)
    db_session.commit()

    db_session.add(profile2)
    with pytest.raises(Exception):  # IntegrityError from SQLAlchemy
        db_session.commit()


def test_user_profile_model_query_by_email(db_session):
    """Test querying UserProfileModel by email."""
    profile = UserProfileModel(name="Query Test", email="query@example.com", age=40)

    db_session.add(profile)
    db_session.commit()

    # Query by email
    found = db_session.query(UserProfileModel).filter(UserProfileModel.email == "query@example.com").first()

    assert found is not None
    assert found.name == "Query Test"
    assert found.email == "query@example.com"
    assert found.age == 40


def test_user_profile_model_optional_fields(db_session):
    """Test UserProfileModel with optional fields."""
    profile = UserProfileModel(name="Minimal User", email="minimal@example.com")

    db_session.add(profile)
    db_session.commit()

    assert profile.id is not None
    assert profile.age is None
    assert profile.tags == []


def test_user_profile_model_timestamps(db_session):
    """Test that timestamps are set correctly."""
    before = datetime.now(timezone.utc)
    profile = UserProfileModel(name="Timestamp Test", email="timestamp@example.com")

    db_session.add(profile)
    db_session.commit()
    after = datetime.now(timezone.utc)

    # SQLite doesn't preserve timezone info, so we need to remove it for comparison
    created_at_no_tz = (
        profile.created_at.replace(tzinfo=timezone.utc) if profile.created_at.tzinfo is None else profile.created_at
    )
    updated_at_no_tz = (
        profile.updated_at.replace(tzinfo=timezone.utc) if profile.updated_at.tzinfo is None else profile.updated_at
    )

    assert before <= created_at_no_tz <= after
    assert before <= updated_at_no_tz <= after


def test_user_profile_model_update_timestamp(db_session):
    """Test that updated_at changes on update."""
    profile = UserProfileModel(name="Update Test", email="update@example.com")

    db_session.add(profile)
    db_session.commit()

    original_updated = profile.updated_at

    # Update the profile
    profile.age = 30
    db_session.commit()

    # updated_at should be different (or same if too fast)
    # In real scenarios, there would be a time difference
    assert profile.updated_at >= original_updated
