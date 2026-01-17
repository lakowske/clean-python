"""Tests for database repository operations."""

import pytest

from clean_python.core import UserProfile
from clean_python.db.models import UserProfileModel


def test_repository_create(user_repository, db_session):
    """Test creating a user profile through repository."""
    profile = UserProfile(name="Jane Doe", email="jane@example.com", age=30, tags=["developer", "python"])

    created_profile = user_repository.create(profile)

    assert created_profile.email == "jane@example.com"
    assert created_profile.name == "Jane Doe"
    assert created_profile.age == 30
    assert created_profile.tags == ["developer", "python"]

    # Verify in database
    db_profile = db_session.query(UserProfileModel).filter_by(email="jane@example.com").first()
    assert db_profile is not None
    assert db_profile.name == "Jane Doe"


def test_repository_create_duplicate_email(user_repository):
    """Test that creating duplicate email fails."""
    profile1 = UserProfile(name="User One", email="duplicate@example.com")
    profile2 = UserProfile(name="User Two", email="duplicate@example.com")

    user_repository.create(profile1)

    with pytest.raises(ValueError, match="already exists"):
        user_repository.create(profile2)


def test_repository_get_by_id(user_repository, db_session):
    """Test retrieving a user profile by ID."""
    # Create profile directly in database
    db_profile = UserProfileModel(name="John Doe", email="john@example.com", age=25)
    db_session.add(db_profile)
    db_session.commit()

    # Retrieve through repository
    retrieved = user_repository.get_by_id(db_profile.id)

    assert retrieved is not None
    assert retrieved.name == "John Doe"
    assert retrieved.email == "john@example.com"
    assert retrieved.age == 25


def test_repository_get_by_id_not_found(user_repository):
    """Test retrieving non-existent profile returns None."""
    retrieved = user_repository.get_by_id(99999)

    assert retrieved is None


def test_repository_get_by_email(user_repository, db_session):
    """Test retrieving a user profile by email."""
    db_profile = UserProfileModel(name="Alice Smith", email="alice@example.com", age=28)
    db_session.add(db_profile)
    db_session.commit()

    retrieved = user_repository.get_by_email("alice@example.com")

    assert retrieved is not None
    assert retrieved.name == "Alice Smith"
    assert retrieved.email == "alice@example.com"


def test_repository_get_by_email_not_found(user_repository):
    """Test retrieving by non-existent email returns None."""
    retrieved = user_repository.get_by_email("nonexistent@example.com")

    assert retrieved is None


def test_repository_list_all_empty(user_repository):
    """Test listing profiles when database is empty."""
    profiles = user_repository.list_all()

    assert profiles == []


def test_repository_list_all(user_repository, db_session):
    """Test listing all user profiles."""
    # Create multiple profiles
    names = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
    for i, name in enumerate(names):
        db_profile = UserProfileModel(name=name, email=f"user{i}@example.com", age=20 + i)
        db_session.add(db_profile)
    db_session.commit()

    profiles = user_repository.list_all()

    assert len(profiles) == 5
    assert all(isinstance(p, UserProfile) for p in profiles)


def test_repository_list_all_with_limit(user_repository, db_session):
    """Test listing profiles with limit."""
    # Create multiple profiles
    names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry", "Iris", "Jack"]
    for i, name in enumerate(names):
        db_profile = UserProfileModel(name=name, email=f"user{i}@example.com")
        db_session.add(db_profile)
    db_session.commit()

    profiles = user_repository.list_all(limit=5)

    assert len(profiles) == 5


def test_repository_list_all_with_offset(user_repository, db_session):
    """Test listing profiles with offset."""
    # Create profiles with predictable ordering
    names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry", "Iris", "Jack"]
    for i, name in enumerate(names):
        db_profile = UserProfileModel(name=name, email=f"user{i}@example.com")
        db_session.add(db_profile)
    db_session.commit()

    # Skip first 5 profiles
    profiles = user_repository.list_all(limit=5, offset=5)

    assert len(profiles) == 5


def test_repository_update(user_repository, db_session):
    """Test updating a user profile."""
    # Create initial profile
    db_profile = UserProfileModel(name="Bob Brown", email="bob@example.com", age=30)
    db_session.add(db_profile)
    db_session.commit()
    profile_id = db_profile.id

    # Update through repository
    updated_profile = UserProfile(name="Robert Brown", email="bob@example.com", age=31, tags=["updated"])
    result = user_repository.update(profile_id, updated_profile)

    assert result is not None
    assert result.name == "Robert Brown"
    assert result.age == 31
    assert result.tags == ["updated"]

    # Verify in database
    db_profile = db_session.query(UserProfileModel).filter_by(id=profile_id).first()
    assert db_profile.name == "Robert Brown"
    assert db_profile.age == 31


def test_repository_update_not_found(user_repository):
    """Test updating non-existent profile returns None."""
    profile = UserProfile(name="Ghost User", email="ghost@example.com")
    result = user_repository.update(99999, profile)

    assert result is None


def test_repository_update_duplicate_email(user_repository, db_session):
    """Test updating to duplicate email fails."""
    # Create two profiles
    db_profile1 = UserProfileModel(name="User One", email="user1@example.com")
    db_profile2 = UserProfileModel(name="User Two", email="user2@example.com")
    db_session.add(db_profile1)
    db_session.add(db_profile2)
    db_session.commit()

    # Try to update profile2 to have same email as profile1
    updated_profile = UserProfile(name="User Two", email="user1@example.com")

    with pytest.raises(ValueError, match="already exists"):
        user_repository.update(db_profile2.id, updated_profile)


def test_repository_delete(user_repository, db_session):
    """Test deleting a user profile."""
    db_profile = UserProfileModel(name="Delete Me", email="delete@example.com")
    db_session.add(db_profile)
    db_session.commit()
    profile_id = db_profile.id

    result = user_repository.delete(profile_id)

    assert result is True

    # Verify deleted from database
    db_profile = db_session.query(UserProfileModel).filter_by(id=profile_id).first()
    assert db_profile is None


def test_repository_delete_not_found(user_repository):
    """Test deleting non-existent profile returns False."""
    result = user_repository.delete(99999)

    assert result is False


def test_repository_count_empty(user_repository):
    """Test counting profiles when database is empty."""
    count = user_repository.count()

    assert count == 0


def test_repository_count(user_repository, db_session):
    """Test counting user profiles."""
    # Create multiple profiles
    names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace"]
    for i, name in enumerate(names):
        db_profile = UserProfileModel(name=name, email=f"user{i}@example.com")
        db_session.add(db_profile)
    db_session.commit()

    count = user_repository.count()

    assert count == 7


def test_repository_full_workflow(user_repository):
    """Test complete CRUD workflow."""
    # Create
    profile = UserProfile(name="Workflow Test", email="workflow@example.com", age=25, tags=["test"])
    created = user_repository.create(profile)
    assert created.name == "Workflow Test"

    # Get by email
    retrieved = user_repository.get_by_email("workflow@example.com")
    assert retrieved is not None
    assert retrieved.name == "Workflow Test"

    # List
    all_profiles = user_repository.list_all()
    assert len(all_profiles) >= 1

    # Count
    count = user_repository.count()
    assert count >= 1

    # Note: We can't easily test update/delete here since we don't have the ID
    # Those are tested in separate test cases
