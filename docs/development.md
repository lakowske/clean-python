# Development Workflow

This guide covers the development workflow and tools available in your clean-python project.

## Available Commands

The project includes a Makefile with convenient shortcuts for common development tasks:

```bash
make help         # Show all available commands
make install      # Install development dependencies
make test         # Run tests with coverage
make lint         # Run linting checks
make format       # Format code with ruff
make type-check   # Run type checking with mypy
make docs         # Build documentation
make clean        # Clean build artifacts
make pre-commit   # Run all pre-commit checks
make all          # Run all checks (lint, format, type-check, test)
```

## Development Tools

### Ruff - Code Quality

Ruff is an extremely fast Python linter and formatter that replaces multiple tools:

```bash
# Format code
ruff format .

# Run linting
ruff check .

# Auto-fix issues
ruff check --fix .
```

Configuration is in `pyproject.toml` under `[tool.ruff]`.

### MyPy - Type Checking

MyPy is a static type checker for Python:

```bash
# Run type checking
mypy .

# Check specific files
mypy src/my_project/core.py
```

Configuration is in `pyproject.toml` under `[tool.mypy]`.

### Pytest - Testing

Pytest is configured with coverage reporting:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_core.py

# Run with verbose output
pytest -v
```

Configuration is in `pyproject.toml` under `[tool.pytest.ini_options]`.

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit:

```bash
# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files

# Update hook versions
pre-commit autoupdate
```

The hooks include:

- Trailing whitespace removal
- End-of-file fixing
- YAML validation
- Large file detection
- Ruff linting and formatting
- Type checking with MyPy
- Markdown formatting
- Test coverage validation

## Package Management

### Using UV (Recommended)

UV is a fast Python package manager:

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Add new dependency
uv add requests

# Add development dependency
uv add --dev pytest-mock

# Update dependencies
uv pip install --upgrade-package package-name
```

### Using pip

```bash
# Install dependencies
pip install -e ".[dev]"

# Add new dependency (manually edit pyproject.toml)
pip install -e ".[dev]"
```

## Database Development

> **Note**: This section applies only if you created your project with the `--with-database` flag.

### Installing Database Dependencies

```bash
# Install database dependencies
pip install -e ".[database]"

# Or install all dependencies (dev + database)
pip install -e ".[dev,database]"

# With UV
uv pip install -e ".[dev,database]"
```

### Database Setup

#### SQLite (Default)

No additional setup required. The database file will be created automatically:

```python
from clean_python.db import DatabaseConfig, DatabaseSession

config = DatabaseConfig(db_type="sqlite", database="app.db")
db_session = DatabaseSession(config)
db_session.initialize(create_tables=True)
```

#### PostgreSQL

1. Install PostgreSQL locally or use Docker:

```bash
# Using Docker
docker run --name postgres-dev \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=myapp \
  -p 5432:5432 \
  -d postgres:16
```

2. Configure environment variables in `.env`:

```bash
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=myapp
DB_USERNAME=postgres
DB_PASSWORD=secret
```

3. Load configuration:

```python
from clean_python.db import DatabaseConfig, DatabaseSession

config = DatabaseConfig.from_env()
db_session = DatabaseSession(config)
db_session.initialize(create_tables=True)
```

#### MySQL

1. Install MySQL locally or use Docker:

```bash
# Using Docker
docker run --name mysql-dev \
  -e MYSQL_ROOT_PASSWORD=secret \
  -e MYSQL_DATABASE=myapp \
  -p 3306:3306 \
  -d mysql:8
```

2. Configure environment variables:

```bash
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=myapp
DB_USERNAME=root
DB_PASSWORD=secret
```

### Database Migrations

The project uses Alembic for database migrations:

```bash
# Create a new migration after model changes
alembic revision --autogenerate -m "Add new table"

# Review the generated migration file
# Edit src/my_project/db/migrations/versions/xxx_add_new_table.py if needed

# Apply migrations
alembic upgrade head

# View migration history
alembic history

# Rollback one version
alembic downgrade -1

# View current version
alembic current

# Downgrade to specific version
alembic downgrade <revision_id>
```

### Testing with Database

Use in-memory SQLite for fast tests:

```python
import pytest
from clean_python.db import DatabaseConfig, DatabaseSession

@pytest.fixture
def db_session():
    """Create in-memory database for testing."""
    config = DatabaseConfig(db_type="sqlite", database=":memory:")
    db = DatabaseSession(config)
    db.initialize(create_tables=True)
    yield db
    db.close()

def test_database_operation(db_session):
    """Test database operations."""
    with db_session.get_session() as session:
        # Your test here
        pass
```

### Database Development Workflow

1. **Modify Models**: Update ORM models in `src/my_project/db/models.py`
1. **Create Migration**: Run `alembic revision --autogenerate -m "description"`
1. **Review Migration**: Check the generated file for correctness
1. **Test Migration**: Run `alembic upgrade head` on dev database
1. **Write Tests**: Add tests for new database functionality
1. **Commit**: Commit models and migration files together

### Repository Pattern

The template uses the repository pattern for database operations:

```python
from clean_python.db import UserProfileRepository
from clean_python.core import UserProfile

with db_session.get_session() as session:
    repo = UserProfileRepository(session)

    # CRUD operations
    user = repo.create(UserProfile(name="Jane", email="jane@example.com"))
    found = repo.get_by_id(1)
    users = repo.list_all(limit=10)
    updated = repo.update(1, user)
    deleted = repo.delete(1)
```

To create a new repository:

1. Define your Pydantic model in `src/my_project/core.py`
1. Create ORM model in `src/my_project/db/models.py`
1. Implement repository in `src/my_project/db/repository.py` extending `BaseRepository`
1. Export from `src/my_project/db/__init__.py`

### Database Logging

Enable SQL query logging for debugging:

```python
config = DatabaseConfig(
    db_type="sqlite",
    database="app.db",
    echo=True  # Logs all SQL queries
)
```

Or via environment variable:

```bash
DB_ECHO=true
```

### Connection Pooling

Configure connection pooling for production:

```python
config = DatabaseConfig(
    db_type="postgresql",
    host="localhost",
    database="myapp",
    pool_size=5,        # Number of persistent connections
    max_overflow=10,    # Max additional connections
)
```

### Common Database Tasks

```bash
# Run database example
python examples/database_example.py

# Check database schema
sqlite3 app.db ".schema"  # For SQLite
psql -d myapp -c "\dt"    # For PostgreSQL

# Backup database
# SQLite
cp app.db app.db.backup

# PostgreSQL
pg_dump myapp > backup.sql

# Restore PostgreSQL
psql myapp < backup.sql
```

## Code Examples

The template includes modern Python patterns:

### Pydantic Models

```python
from pydantic import BaseModel, Field, model_validator

class UserProfile(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    age: Optional[int] = Field(None, ge=0, le=120)

    @model_validator(mode='after')
    def validate_model(self) -> 'UserProfile':
        if any(char.isdigit() for char in self.name):
            raise ValueError('Name cannot contain numbers')
        self.name = self.name.strip().title()
        return self
```

### Dataclasses

```python
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Union, Optional

@dataclass
class CalculationResult:
    operand_a: Union[int, float]
    operand_b: Union[int, float]
    operation: str
    result: Union[int, float]
    timestamp: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            'operand_a': self.operand_a,
            'operand_b': self.operand_b,
            'operation': self.operation,
            'result': self.result,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
```

## Testing Patterns

### Testing Pydantic Models

```python
import pytest
from pydantic import ValidationError

def test_user_profile_validation():
    # Test valid data
    profile = UserProfile(name="John Doe", email="john@example.com")
    assert profile.name == "John Doe"

    # Test validation error
    with pytest.raises(ValidationError):
        UserProfile(name="John123", email="john@example.com")
```

### Testing Dataclasses

```python
def test_calculation_result():
    result = CalculationResult(
        operand_a=10,
        operand_b=5,
        operation="subtraction",
        result=5
    )
    assert result.operand_a == 10
    assert result.to_dict()["operation"] == "subtraction"
```

## Documentation

### Building Documentation

```bash
# Build documentation
make docs

# Serve documentation locally
mkdocs serve

# Deploy to GitHub Pages
mkdocs gh-deploy
```

### Writing Documentation

Documentation is written in Markdown and built with MkDocs:

- `docs/index.md` - Main documentation page
- `docs/getting-started.md` - Getting started guide
- `docs/development.md` - Development workflow
- `docs/examples.md` - Code examples
- `docs/api.md` - API reference

## VS Code Integration

The template includes VS Code configuration:

- **Recommended extensions**: Ruff, Python, MyPy
- **Format on save**: Enabled
- **Integrated terminal**: Configured for Python development
- **Debugging**: Pre-configured for Python

## Logging Best Practices

The template includes comprehensive logging:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Use in functions
def process_data(data):
    logger.info(f"Processing data - size: {len(data)}")
    try:
        # Process data
        result = transform(data)
        logger.debug(f"Processing complete - result_size: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"Processing failed - error: {str(e)}", exc_info=True)
        raise
```

## Continuous Integration

The template is ready for CI/CD integration. Consider adding:

- GitHub Actions for automated testing
- Code coverage reporting
- Automated dependency updates
- Security scanning
- Automated releases

## Performance Tips

- Use UV for faster package management
- Enable `--parallel` for pytest on multi-core systems
- Use `ruff --fix` for automatic code fixes
- Configure pre-commit hooks to run only on changed files for speed
