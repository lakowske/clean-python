# clean-python

A modern Python project template with pre-commit hooks for linting, formatting, testing and code coverage using Ruff as the all-in-one Python code quality tool.

## 🚀 Features

- **Modern Python Packaging**: Uses `pyproject.toml` for all project configuration
- **Ruff**: Lightning-fast Python linter and formatter (replaces Black, Flake8, isort, and Bandit)
- **Pydantic**: Data validation and settings management with Python type hints
- **Dataclasses**: Simple data structures with built-in validation
- **Pre-commit Hooks**: Automated code quality checks before every commit
- **Testing**: Pytest with coverage reporting (minimum 80% required)
- **Type Checking**: Ty for static type analysis (modern MyPy alternative)
- **Documentation**: MkDocs with Material theme for beautiful documentation
- **UV Support**: Fast Python package manager integration
- **Makefile**: Convenient development commands
- **Security**: Gitleaks for preventing secret commits
- **Dependency Updates**: Dependabot for automated dependency management
- **VS Code Integration**: Pre-configured settings for optimal development experience
- **GitHub Ready**: Includes issue templates and project structure
- **Clean Project Structure**: Organized layout following Python best practices

## 📋 Prerequisites

- Python 3.9 or higher
- Git
- pip (or UV for faster package management)

## 🎯 Quick Start

### Option 1: Interactive Setup (Recommended)

1. Clone this template repository:

```bash
git clone https://github.com/lakowske/clean-python.git
cd clean-python
```

2. Run the setup script:

```bash
python setup_new_project.py
```

3. Follow the prompts to enter:
   - Project name (e.g., `my-awesome-project`)
   - Project description
   - Your name
   - Your email
   - GitHub username (optional)

The script will create your new project in the parent directory and set everything up for you!

### Option 2: Command Line Setup

Provide all information via command line arguments:

```bash
python setup_new_project.py \
    --name my-awesome-project \
    --description "A fantastic Python project" \
    --author "Jane Doe" \
    --email jane.doe@example.com \
    --github janedoe
```

### Option 3: Custom Directory Setup

Create the project in a specific location:

```bash
python setup_new_project.py \
    --name my-project \
    --output-dir ~/projects/my-new-project
```

## 🛠️ Setup Options

| Option           | Description                                            |
| ---------------- | ------------------------------------------------------ |
| `--name`         | Project name (required)                                |
| `--description`  | Project description                                    |
| `--author`       | Your name                                              |
| `--email`        | Your email address                                     |
| `--github`       | Your GitHub username                                   |
| `--output-dir`   | Custom output directory (default: `../<project-name>`) |
| `--no-git`       | Skip git repository initialization                     |
| `--skip-cleanup` | Keep template files (including setup script)           |
| `-y, --yes`      | Skip confirmation prompts                              |

## 📦 What Gets Configured

The setup script automatically:

1. **Creates a new project directory** with your project name
1. **Updates all configuration files** with your project information:
   - `pyproject.toml` - Project metadata and dependencies
   - `README.md` - Customized for your project
   - All source code references
1. **Renames the Python package** to match your project
1. **Initializes a fresh git repository** (unless `--no-git` is used)
1. **Creates an initial commit** with your configured project
1. **Removes template-specific files** (unless `--skip-cleanup` is used)

## 🏗️ Project Structure

After setup, your project will have this structure:

```
my-project/
├── src/
│   └── my_project/          # Your package (renamed from clean_python)
│       ├── __init__.py
│       ├── core.py          # Example module
│       └── actions/         # Example subpackage
├── tests/                   # Test suite
│   ├── conftest.py
│   └── test_*.py
├── .github/                 # GitHub templates
├── .vscode/                 # VS Code settings
├── .pre-commit-config.yaml  # Pre-commit hooks
├── pyproject.toml          # Project configuration
├── .gitignore
└── README.md               # Your project's README
```

## 🧰 Development Workflow

After creating your project:

### 1. Set up your development environment

```bash
cd my-project
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Using Make (recommended)
make install

# Or using UV (fastest)
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

### 2. Install pre-commit hooks

```bash
pre-commit install
```

### 3. Start coding!

Available commands:

```bash
# Using Make (recommended)
make help         # Show all available commands
make test         # Run tests with coverage
make lint         # Run linting
make format       # Format code
make type-check   # Run type checking
make docs         # Build documentation
make all          # Run all checks

# Or run tools directly
ruff check .      # Run linting
ruff format .     # Format code
pytest --cov     # Run tests with coverage
ty .             # Run type checking
mkdocs serve     # Serve documentation locally
pre-commit run --all-files  # Run all checks
```

## ⚙️ Configuration

All tool configurations are centralized in `pyproject.toml`:

- **Ruff**: Linting and formatting rules (120 character line length)
- **Pytest**: Test discovery and coverage settings
- **Ty**: Type checking configuration (modern MyPy alternative)
- **Coverage**: 80% minimum coverage requirement
- **MkDocs**: Documentation configuration
- **Pydantic**: Data validation and serialization

## 🤝 Pre-commit Hooks

The following checks run automatically on commit:

- Trailing whitespace removal
- End-of-file fixing
- YAML validation
- Large file detection
- Ruff linting and formatting
- Ty type checking
- Markdown formatting
- Test coverage validation
- Gitleaks security scanning (prevents secret commits)

## 📝 VS Code Integration

If you use VS Code, the project includes:

- Recommended extensions (Ruff, Python, Ty)
- Configured formatters and linters
- Format-on-save enabled
- Test discovery configured
- Integrated debugging configuration

## 🔄 Updating the Template

To get the latest template improvements:

1. Add the template as a remote:

```bash
git remote add template https://github.com/lakowske/clean-python.git
```

2. Fetch and merge updates:

```bash
git fetch template
git merge template/main --allow-unrelated-histories
```

## 📄 License

This template is released under the MIT License. Your generated projects can use any license you prefer.

## 🙏 Acknowledgments

Built with modern Python development best practices and powered by:

- [Ruff](https://github.com/astral-sh/ruff) - An extremely fast Python linter and formatter
- [Pydantic](https://pydantic.dev/) - Data validation using Python type hints
- [Pytest](https://pytest.org) - The pytest framework
- [Ty](https://github.com/dosisod/ty) - Modern type checker for Python
- [Pre-commit](https://pre-commit.com) - A framework for managing git hooks
- [MkDocs](https://www.mkdocs.org/) - Project documentation with Markdown
- [UV](https://github.com/astral-sh/uv) - An extremely fast Python package installer and resolver
- [Gitleaks](https://github.com/gitleaks/gitleaks) - Detect and prevent secrets in git repos

______________________________________________________________________

Happy coding! 🐍✨
