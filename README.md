# clean-python

A modern Python project template with pre-commit hooks for linting, formatting, testing and code coverage using Ruff as the all-in-one Python code quality tool.

## 🚀 Features

- **Modern Python Packaging**: Uses `pyproject.toml` for all project configuration
- **Ruff**: Lightning-fast Python linter and formatter (replaces Black, Flake8, isort, and Bandit)
- **Pre-commit Hooks**: Automated code quality checks before every commit
- **Testing**: Pytest with coverage reporting (minimum 80% required)
- **Type Checking**: MyPy for static type analysis
- **VS Code Integration**: Pre-configured settings for optimal development experience
- **GitHub Ready**: Includes issue templates and project structure
- **Clean Project Structure**: Organized layout following Python best practices

## 📋 Prerequisites

- Python 3.8 or higher
- Git
- pip

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
pip install -e ".[dev]"
```

### 2. Install pre-commit hooks

```bash
pre-commit install
```

### 3. Start coding!

Available commands:

- `ruff check .` - Run linting
- `ruff format .` - Format code
- `pytest` - Run tests
- `pytest --cov` - Run tests with coverage
- `mypy .` - Run type checking
- `pre-commit run --all-files` - Run all checks

## ⚙️ Configuration

All tool configurations are centralized in `pyproject.toml`:

- **Ruff**: Linting and formatting rules (120 character line length)
- **Pytest**: Test discovery and coverage settings
- **MyPy**: Type checking configuration
- **Coverage**: 80% minimum coverage requirement

## 🤝 Pre-commit Hooks

The following checks run automatically on commit:

- Trailing whitespace removal
- End-of-file fixing
- YAML validation
- Large file detection
- Ruff linting and formatting
- MyPy type checking
- Markdown formatting
- Test coverage validation

## 📝 VS Code Integration

If you use VS Code, the project includes:

- Recommended extensions (Ruff, Python, MyPy)
- Configured formatters and linters
- Format-on-save enabled
- Test discovery configured

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
- [Pytest](https://pytest.org) - The pytest framework
- [Pre-commit](https://pre-commit.com) - A framework for managing git hooks

______________________________________________________________________

Happy coding! 🐍✨
