# Code Examples

This page provides examples of the modern Python patterns included in the clean-python template.

## Pydantic Examples

### Basic Model

```python
from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    age: Optional[int] = Field(None, ge=0, le=120)

    class Config:
        # Example configuration
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### Model with Validation

```python
from pydantic import BaseModel, Field, validator
from typing import List

class UserProfile(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    tags: List[str] = Field(default_factory=list)

    @validator('name')
    def validate_name(cls, v):
        if any(char.isdigit() for char in v):
            raise ValueError('Name cannot contain numbers')
        return v.strip().title()

    @validator('tags')
    def validate_tags(cls, v):
        return [tag.strip().lower() for tag in v if tag.strip()]

# Usage
profile = UserProfile(
    name="jane doe",
    email="jane@example.com",
    tags=["  Developer  ", "Python", "  "]
)
print(profile.name)  # "Jane Doe"
print(profile.tags)  # ["developer", "python"]
```

### Nested Models

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: str

class Contact(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None

class Person(BaseModel):
    name: str
    age: int
    address: Address
    contact: Contact
    created_at: datetime = Field(default_factory=datetime.now)

# Usage
person = Person(
    name="John Doe",
    age=30,
    address=Address(
        street="123 Main St",
        city="New York",
        country="USA",
        postal_code="10001"
    ),
    contact=Contact(
        phone="+1-555-0123",
        email="john@example.com"
    )
)
```

## Dataclass Examples

### Basic Dataclass

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Union

@dataclass
class CalculationResult:
    operand_a: Union[int, float]
    operand_b: Union[int, float]
    operation: str
    result: Union[int, float]
    timestamp: datetime = datetime.now()

    def to_dict(self) -> dict:
        return {
            'operand_a': self.operand_a,
            'operand_b': self.operand_b,
            'operation': self.operation,
            'result': self.result,
            'timestamp': self.timestamp.isoformat()
        }

# Usage
result = CalculationResult(
    operand_a=10,
    operand_b=5,
    operation="addition",
    result=15
)
print(result.to_dict())
```

### Dataclass with Validation

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ApplicationConfig:
    debug: bool = False
    log_level: str = "INFO"
    max_users: int = 1000
    timeout: float = 30.0
    features: Optional[List[str]] = None

    def __post_init__(self):
        if self.features is None:
            self.features = ["basic", "logging"]

        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            raise ValueError(f"Invalid log level: {self.log_level}")

        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")

# Usage
config = ApplicationConfig(
    debug=True,
    log_level="DEBUG",
    timeout=60.0
)
```

## Logging Examples

### Basic Logging Setup

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

def process_data(data):
    logger.info(f"Processing data - size: {len(data)}")

    try:
        # Process data
        result = transform_data(data)
        logger.debug(f"Processing complete - result_size: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"Processing failed - error: {str(e)}", exc_info=True)
        raise
```

### Advanced Logging with Context

```python
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@contextmanager
def operation_context(operation_name: str, **kwargs):
    """Context manager for logging operation boundaries."""
    logger.info(f"Starting {operation_name} - {kwargs}")
    try:
        yield
        logger.info(f"Completed {operation_name} successfully")
    except Exception as e:
        logger.error(f"Failed {operation_name} - error: {str(e)}")
        raise

# Usage
def create_user(name: str, email: str):
    with operation_context("user_creation", name=name, email=email):
        # Create user logic
        user = UserProfile(name=name, email=email)
        logger.debug(f"User created - id: {id(user)}")
        return user
```

## Testing Examples

### Testing Pydantic Models

```python
import pytest
from pydantic import ValidationError
from your_module import UserProfile

def test_user_profile_valid():
    """Test UserProfile with valid data."""
    profile = UserProfile(
        name="John Doe",
        email="john@example.com",
        age=30
    )
    assert profile.name == "John Doe"
    assert profile.email == "john@example.com"
    assert profile.age == 30

def test_user_profile_invalid_email():
    """Test UserProfile with invalid email."""
    with pytest.raises(ValidationError) as exc_info:
        UserProfile(name="John Doe", email="invalid-email")

    assert "email" in str(exc_info.value)

def test_user_profile_name_validation():
    """Test UserProfile name validation."""
    with pytest.raises(ValidationError) as exc_info:
        UserProfile(name="John123", email="john@example.com")

    assert "Name cannot contain numbers" in str(exc_info.value)

@pytest.mark.parametrize("name,expected", [
    ("  john doe  ", "John Doe"),
    ("JANE SMITH", "Jane Smith"),
    ("bob", "Bob"),
])
def test_user_profile_name_formatting(name, expected):
    """Test UserProfile name formatting."""
    profile = UserProfile(name=name, email="test@example.com")
    assert profile.name == expected
```

### Testing Dataclasses

```python
import pytest
from datetime import datetime
from your_module import CalculationResult, ApplicationConfig

def test_calculation_result():
    """Test CalculationResult creation."""
    result = CalculationResult(
        operand_a=10,
        operand_b=5,
        operation="subtraction",
        result=5
    )
    assert result.operand_a == 10
    assert result.operand_b == 5
    assert result.operation == "subtraction"
    assert result.result == 5
    assert isinstance(result.timestamp, datetime)

def test_calculation_result_to_dict():
    """Test CalculationResult to_dict method."""
    result = CalculationResult(
        operand_a=10,
        operand_b=5,
        operation="subtraction",
        result=5
    )
    dict_result = result.to_dict()

    assert dict_result["operand_a"] == 10
    assert dict_result["operand_b"] == 5
    assert dict_result["operation"] == "subtraction"
    assert dict_result["result"] == 5
    assert "timestamp" in dict_result

def test_application_config_defaults():
    """Test ApplicationConfig default values."""
    config = ApplicationConfig()
    assert config.debug is False
    assert config.log_level == "INFO"
    assert config.features == ["basic", "logging"]

def test_application_config_validation():
    """Test ApplicationConfig validation."""
    with pytest.raises(ValueError, match="Invalid log level"):
        ApplicationConfig(log_level="INVALID")

    with pytest.raises(ValueError, match="Timeout must be positive"):
        ApplicationConfig(timeout=-1)
```

## Error Handling Examples

### Comprehensive Error Handling

```python
import logging
from pydantic import ValidationError
from typing import Optional

logger = logging.getLogger(__name__)

def safe_create_user(name: str, email: str, age: Optional[int] = None) -> Optional[UserProfile]:
    """Safely create a user profile with comprehensive error handling."""
    try:
        logger.info(f"Creating user profile - name: {name}, email: {email}")

        profile = UserProfile(name=name, email=email, age=age)
        logger.debug(f"User profile created successfully - id: {id(profile)}")
        return profile

    except ValidationError as e:
        logger.warning(f"Validation error creating user - errors: {e.errors()}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error creating user - error: {str(e)}", exc_info=True)
        raise

# Usage
user = safe_create_user("Jane Doe", "jane@example.com", 25)
if user:
    print(f"Created user: {user.name}")
else:
    print("Failed to create user")
```

### Custom Exception Classes

```python
class UserCreationError(Exception):
    """Custom exception for user creation errors."""
    def __init__(self, message: str, user_data: dict):
        super().__init__(message)
        self.user_data = user_data

def create_user_strict(name: str, email: str) -> UserProfile:
    """Create user with strict validation and custom exceptions."""
    try:
        return UserProfile(name=name, email=email)
    except ValidationError as e:
        raise UserCreationError(
            f"Invalid user data: {e}",
            user_data={"name": name, "email": email}
        )

# Usage
try:
    user = create_user_strict("Invalid123", "bad-email")
except UserCreationError as e:
    print(f"Error: {e}")
    print(f"User data: {e.user_data}")
```

## Integration Examples

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class CreateUserRequest(BaseModel):
    name: str
    email: str
    age: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int]

@app.post("/users/", response_model=UserResponse)
async def create_user(request: CreateUserRequest):
    try:
        profile = UserProfile(
            name=request.name,
            email=request.email,
            age=request.age
        )
        # Save to database logic here
        return UserResponse(
            id=1,
            name=profile.name,
            email=profile.email,
            age=profile.age
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Database Examples

> **Note**: The database module is optional. Include it when creating a new project with the `--with-database` flag.

The template includes a complete SQL database integration with SQLAlchemy and Alembic, supporting SQLite, PostgreSQL, and MySQL.

### Database Configuration

```python
from clean_python.db import DatabaseConfig, DatabaseSession

# SQLite (default)
config = DatabaseConfig(
    db_type="sqlite",
    database="app.db",
    echo=False  # Set to True for SQL query logging
)

# PostgreSQL
config = DatabaseConfig(
    db_type="postgresql",
    host="localhost",
    port=5432,
    database="myapp",
    username="postgres",
    password="secret",
    pool_size=5,
    max_overflow=10
)

# MySQL
config = DatabaseConfig(
    db_type="mysql",
    host="localhost",
    port=3306,
    database="myapp",
    username="root",
    password="secret"
)

# Environment variable support (DB_ prefix)
# Set DB_TYPE, DB_HOST, DB_PORT, DB_DATABASE, DB_USERNAME, DB_PASSWORD
config = DatabaseConfig.from_env()
```

### Session Management

```python
from clean_python.db import DatabaseSession

# Initialize database
db_session = DatabaseSession(config)
db_session.initialize(create_tables=True)

# Using context manager (recommended)
with db_session.get_session() as session:
    # Automatic commit on success, rollback on error
    profile = UserProfileModel(name="Jane Doe", email="jane@example.com")
    session.add(profile)
    # Session commits automatically when context exits

# Clean up
db_session.close()

# Or use as context manager for entire lifecycle
with DatabaseSession(config) as db:
    with db.get_session() as session:
        # Use session here
        pass
```

### Repository Pattern

```python
from clean_python.db import UserProfileRepository
from clean_python.core import UserProfile

# Create repository with session
with db_session.get_session() as session:
    repo = UserProfileRepository(session)

    # Create
    profile = UserProfile(name="Jane Doe", email="jane@example.com", age=30)
    created = repo.create(profile)
    print(f"Created user: {created.name}")

    # Read by ID
    user = repo.get_by_id(1)
    if user:
        print(f"Found user: {user.email}")

    # Read by email
    user = repo.get_by_email("jane@example.com")

    # List all (with pagination)
    users = repo.list_all(limit=10, offset=0)

    # Update
    if user:
        user.age = 31
        updated = repo.update(1, user)

    # Delete
    deleted = repo.delete(1)

    # Count
    total = repo.count()
```

### ORM Models

```python
from clean_python.db import UserProfileModel, Base
from clean_python.core import UserProfile

# Convert between Pydantic and ORM models
pydantic_model = UserProfile(name="John Doe", email="john@example.com")
orm_model = UserProfileModel.from_pydantic(pydantic_model)

# Save to database
with db_session.get_session() as session:
    session.add(orm_model)
    session.flush()  # Get ID without committing

    # Convert back to Pydantic
    result = orm_model.to_pydantic()
    print(f"Saved with ID: {orm_model.id}")

# Query directly with ORM
with db_session.get_session() as session:
    users = session.query(UserProfileModel).filter(
        UserProfileModel.age > 25
    ).all()

    for user in users:
        print(f"{user.name}: {user.email}")
```

### Database Migrations with Alembic

```bash
# Create a new migration
alembic revision --autogenerate -m "Add user_preferences table"

# View migration history
alembic history

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View current version
alembic current
```

### Error Handling

```python
from sqlalchemy.exc import IntegrityError
from clean_python.db import UserProfileRepository

def safe_create_user(name: str, email: str):
    """Safely create user with proper error handling."""
    try:
        with db_session.get_session() as session:
            repo = UserProfileRepository(session)
            profile = UserProfile(name=name, email=email)
            return repo.create(profile)
    except ValueError as e:
        # Duplicate email or validation error
        logger.warning(f"User creation failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise

# Usage
user = safe_create_user("Jane Doe", "jane@example.com")
if user:
    print(f"Created: {user.name}")
else:
    print("User with this email already exists")
```

### Testing Database Code

```python
import pytest
from clean_python.db import DatabaseConfig, DatabaseSession, UserProfileRepository
from clean_python.core import UserProfile

@pytest.fixture
def db_session():
    """Create in-memory SQLite database for testing."""
    config = DatabaseConfig(db_type="sqlite", database=":memory:")
    db = DatabaseSession(config)
    db.initialize(create_tables=True)
    yield db
    db.close()

@pytest.fixture
def repository(db_session):
    """Create repository for testing."""
    with db_session.get_session() as session:
        yield UserProfileRepository(session)

def test_create_user(repository):
    """Test user creation."""
    profile = UserProfile(name="Test User", email="test@example.com")
    created = repository.create(profile)

    assert created.name == "Test User"
    assert created.email == "test@example.com"

def test_duplicate_email(repository):
    """Test duplicate email handling."""
    profile1 = UserProfile(name="User One", email="test@example.com")
    profile2 = UserProfile(name="User Two", email="test@example.com")

    repository.create(profile1)

    with pytest.raises(ValueError, match="already exists"):
        repository.create(profile2)
```

### Complete Example

See `examples/database_example.py` for a comprehensive example demonstrating:

- Database configuration for multiple backends
- Session management and context managers
- Repository pattern for CRUD operations
- Error handling and duplicate detection
- Pagination and querying
- PostgreSQL configuration example

These examples demonstrate modern Python patterns that promote code quality, maintainability, and type safety. The template includes all necessary dependencies and configurations to support these patterns out of the box.
