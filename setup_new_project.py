#!/usr/bin/env python3
"""Setup script for creating a new Python project from this template.

This script will prompt you for project details and automatically update
all configuration files with your project information.

Usage:
    # Interactive mode (prompts for all values)
    python setup_new_project.py

    # Non-interactive mode (all values provided)
    python setup_new_project.py --name my-project --description "My awesome project" \
        --author "John Doe" --email john@example.com --github johndoe

    # Mixed mode (provide some values, prompt for others)
    python setup_new_project.py --name my-project --author "John Doe"
"""

import argparse
import os
import re
import shutil
import subprocess  # nosec B404
import sys
from pathlib import Path
from typing import Any, Dict, List


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Setup a new Python project from the clean-python template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode - prompts for all values
  %(prog)s

  # Full non-interactive mode
  %(prog)s --name my-project --description "My project" \\
      --author "Jane Doe" --email jane@example.com --github janedoe

  # Partial mode - provide some values, prompt for others
  %(prog)s --name my-project --author "Jane Doe"

  # Skip git initialization and cleanup
  %(prog)s --name my-project --no-git --skip-cleanup

  # Create project in specific directory
  %(prog)s --name my-project --output-dir ~/projects/my-project
""",
    )

    parser.add_argument("--name", help="Project name (e.g., my-awesome-project)")
    parser.add_argument("--description", help="Project description (default: 'A clean Python project')")
    parser.add_argument("--author", help="Author name")
    parser.add_argument("--email", help="Author email")
    parser.add_argument("--github", help="GitHub username (optional)")
    parser.add_argument(
        "--output-dir",
        help="Directory to create the new project in (default: ../<project-name>)",
    )
    parser.add_argument("--no-git", action="store_true", help="Skip git repository initialization")
    parser.add_argument(
        "--skip-cleanup",
        action="store_true",
        help="Keep template files (don't remove setup script)",
    )
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")

    return parser.parse_args()


def get_user_input(args: argparse.Namespace) -> Dict[str, Any]:
    """Collect project information from user input or CLI arguments."""
    # Only show header in interactive mode
    if not all([args.name, args.author, args.email]):
        print("🚀 Setting up your new Python project!")
        print("=" * 50)

    # Get basic project info
    if args.name:
        project_name = args.name.strip()
    else:
        project_name = input("Project name (e.g., my-awesome-project): ").strip()
        if not project_name:
            print("❌ Project name is required!")
            sys.exit(1)

    # Convert project name to valid Python module name
    module_name = re.sub(r"[^a-zA-Z0-9_]", "_", project_name.lower())
    module_name = re.sub(r"^[0-9]", "_", module_name)  # Can't start with number

    if args.description:
        description = args.description.strip()
    else:
        description = input("Project description (A clean Python project): ").strip()
        if not description:
            description = "A clean Python project"

    if args.author:
        author_name = args.author.strip()
    else:
        author_name = input("Author name: ").strip()
        if not author_name:
            author_name = "Your Name"

    if args.email:
        author_email = args.email.strip()
    else:
        author_email = input("Author email: ").strip()
        if not author_email:
            author_email = "your.email@example.com"

    if args.github is not None:
        github_username = args.github.strip()
    else:
        github_username = input("GitHub username (optional): ").strip()

    # Generate GitHub URLs if username provided
    if github_username:
        repo_url = f"https://github.com/{github_username}/{project_name}"
        issues_url = f"{repo_url}/issues"
    else:
        repo_url = f"https://github.com/YOUR_USERNAME/{project_name}"
        issues_url = f"{repo_url}/issues"

    return {
        "project_name": project_name,
        "module_name": module_name,
        "description": description,
        "author_name": author_name,
        "author_email": author_email,
        "github_username": github_username,
        "repo_url": repo_url,
        "issues_url": issues_url,
    }


def update_pyproject_toml(config: Dict[str, Any]) -> None:
    """Update pyproject.toml with project information."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text(encoding="utf-8")

    # Update project metadata
    content = re.sub(r'name = "clean-python"', f'name = "{config["project_name"]}"', content)
    content = re.sub(r'description = ".*"', f'description = "{config["description"]}"', content)
    content = re.sub(
        r'authors = \[{name = ".*", email = ".*"}\]',
        f'authors = [{{name = "{config["author_name"]}", email = "{config["author_email"]}"}}]',
        content,
    )

    # Update URLs
    content = re.sub(r'Homepage = ".*"', f'Homepage = "{config["repo_url"]}"', content)
    content = re.sub(r'Repository = ".*"', f'Repository = "{config["repo_url"]}"', content)
    content = re.sub(r'Issues = ".*"', f'Issues = "{config["issues_url"]}"', content)

    pyproject_path.write_text(content, encoding="utf-8")
    print("✅ Updated pyproject.toml")


def update_readme_md(config: Dict[str, Any]) -> None:
    """Update README.md with project information."""
    readme_path = Path("README.md")

    # Create a new README with project-specific content
    readme_content = f"""# {config["project_name"]}

{config["description"]}

## Features

- Modern Python project structure
- Comprehensive testing with pytest and coverage reporting
- Code quality tools (Ruff for linting/formatting, MyPy for type checking)
- Pre-commit hooks for automated quality checks
- GitHub Actions CI/CD pipeline
- VS Code tasks integration

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Git

### Installation

1. Clone the repository:
```bash
git clone {config["repo_url"]}.git
cd {config["project_name"]}
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
```

3. Install the project in development mode:
```bash
pip install -e ".[dev]"
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

## Development

### Running Tests
```bash
# Run tests with coverage
pytest --cov=. --cov-report=term-missing --cov-fail-under=80 --cov-report=html

# Or use VS Code: Ctrl+Shift+P -> "Tasks: Run Task" -> "Run Tests with Coverage"
```

### Code Quality
```bash
# Format code
ruff format .

# Lint code
ruff check .

# Run all pre-commit checks
pre-commit run --all-files
```

### VS Code Integration

This project includes VS Code tasks for common operations:
- `Ctrl+Shift+P` -> "Tasks: Run Task" to see all available tasks
- Install the "Task Explorer" extension for a better task management experience

## Project Structure

```
{config["project_name"]}/
├── src/{config["module_name"]}/     # Main package
├── tests/                          # Test suite
├── .github/workflows/              # GitHub Actions
├── .vscode/                        # VS Code configuration
├── pyproject.toml                  # Project configuration
└── README.md                       # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and run the quality checks
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

{config["author_name"]} - {config["author_email"]}
"""

    readme_path.write_text(readme_content, encoding="utf-8")
    print("✅ Updated README.md")


def rename_module_directory(config: Dict[str, Any]) -> None:
    """Rename the main module directory to match the project."""
    old_module_path = Path("src/clean_python")
    new_module_path = Path(f"src/{config['module_name']}")

    if old_module_path.exists() and old_module_path != new_module_path:
        old_module_path.rename(new_module_path)
        print(f"✅ Renamed module: src/clean_python -> src/{config['module_name']}")
    elif not old_module_path.exists():
        print("⚠️  Module directory src/clean_python not found, skipping rename")


def update_imports_in_files(config: Dict[str, Any]) -> None:
    """Update imports from clean_python to the new module name in all Python files."""
    module_name = config["module_name"]

    # Find all Python files in the project
    python_files: List[Path] = []
    for pattern in ["**/*.py", "tests/**/*.py"]:
        python_files.extend(Path().glob(pattern))

    for file_path in python_files:
        if file_path.is_file():
            try:
                content = file_path.read_text(encoding="utf-8")
                original_content = content

                # Update imports
                content = re.sub(
                    r"from clean_python(\.[\w.]+)? import",
                    rf"from {module_name}\1 import",
                    content,
                )
                content = re.sub(
                    r"import clean_python(\.[\w.]+)?",
                    rf"import {module_name}\1",
                    content,
                )

                # Update __init__.py metadata if this is an __init__.py file
                if file_path.name == "__init__.py":
                    content = re.sub(
                        r'"""Clean Python package with best practices\."""',
                        f'"""{config["description"]}"""',
                        content,
                    )
                    content = re.sub(
                        r'__author__ = "Your Name"',
                        f'__author__ = "{config["author_name"]}"',
                        content,
                    )
                    content = re.sub(
                        r'__email__ = "your\.email@example\.com"',
                        f'__email__ = "{config["author_email"]}"',
                        content,
                    )

                # Write back if changed
                if content != original_content:
                    file_path.write_text(content, encoding="utf-8")
                    print(f"✅ Updated imports in {file_path}")

            except Exception as e:
                print(f"⚠️  Could not update imports in {file_path}: {e}")


def update_github_workflows(config: Dict[str, Any]) -> None:
    """Update GitHub Actions workflow files."""
    _ = config  # Currently unused, but kept for future expansion
    workflow_path = Path(".github/workflows/ci.yml")
    if workflow_path.exists():
        content = workflow_path.read_text(encoding="utf-8")
        # Update any project-specific references if needed
        workflow_path.write_text(content, encoding="utf-8")
        print("✅ Verified GitHub Actions workflow")


def cleanup_template_files() -> None:
    """Remove template-specific files that aren't needed in the new project."""
    files_to_remove = [
        "setup_new_project.py",  # This script itself
    ]

    for file_path in files_to_remove:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            print(f"✅ Removed template file: {file_path}")


def remove_template_git_history() -> None:
    """Remove the template's git history to start fresh."""
    git_dir = Path(".git")
    if git_dir.exists() and git_dir.is_dir():
        try:
            shutil.rmtree(git_dir)
            print("✅ Removed template git history")
        except Exception as e:
            print(f"⚠️  Could not remove .git directory: {e}")


def initialize_new_git_repo() -> None:
    """Initialize a new git repository."""
    try:
        subprocess.run(["git", "init"], check=True)  # nosec B603, B607
        print("✅ Initialized new git repository")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not initialize git repository: {e}")


def create_initial_git_commit(config: Dict[str, Any]) -> None:
    """Create an initial git commit with the new project setup."""
    try:
        subprocess.run(["git", "add", "."], check=True)  # nosec B603, B607
        subprocess.run(  # nosec B603, B607
            [
                "git",
                "commit",
                "-m",
                f"Initial project setup for {config['project_name']}",
            ],
            check=True,
        )
        print("✅ Created initial git commit")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not create git commit: {e}")


def copy_template_files(source_dir: Path, target_dir: Path) -> None:
    """Copy all template files to the target directory."""
    # Files and directories to exclude from copying
    exclude_patterns = {
        ".git",
        "__pycache__",
        ".pytest_cache",
        "*.pyc",
        ".venv",
        "venv",
        "env",
        "htmlcov",
        ".coverage",
        "setup_new_project.py",  # Don't copy this setup script
    }

    def should_exclude(path: Path) -> bool:
        """Check if a path should be excluded."""
        name = path.name
        for pattern in exclude_patterns:
            if pattern.startswith("*") and name.endswith(pattern[1:]) or name == pattern:
                return True
        return False

    # Copy all files and directories
    for item in source_dir.iterdir():
        if should_exclude(item):
            continue

        source_path = item
        target_path = target_dir / item.name

        if item.is_dir():
            shutil.copytree(
                source_path,
                target_path,
                ignore=shutil.ignore_patterns(*exclude_patterns),
            )
        else:
            shutil.copy2(source_path, target_path)

    print(f"✅ Copied template files to {target_dir}")


def main() -> None:
    """Main setup function."""
    # Parse command line arguments
    args = parse_arguments()

    # Get user configuration first to have project name
    config = get_user_input(args)

    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir).resolve()
    else:
        # Default to parent directory with project name
        output_dir = Path.cwd().parent / config["project_name"]

    # Check if output directory already exists
    if output_dir.exists():
        print(f"❌ Directory already exists: {output_dir}")
        print("Please choose a different project name or output directory.")
        sys.exit(1)

    # Show confirmation unless skipped
    if not args.yes:
        print(f"This script will create a new project at: {output_dir}")
        print(f"Based on the clean-python template at: {Path.cwd()}")

        proceed = input("\\nDo you want to continue? (y/N): ").strip().lower()
        if proceed not in ["y", "yes"]:
            print("Setup cancelled.")
            sys.exit(0)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=False)
    print(f"\\n🔧 Creating new project at: {output_dir}")

    # Copy template files
    copy_template_files(Path.cwd(), output_dir)

    # Change to output directory for all operations
    original_dir = Path.cwd()
    os.chdir(output_dir)

    print("\\n🔧 Updating project files...")

    # Update all project files
    update_pyproject_toml(config)
    update_readme_md(config)
    rename_module_directory(config)
    update_imports_in_files(config)
    update_github_workflows(config)

    print("\\n🎉 Project setup complete!")
    print(f"\\nProject: {config['project_name']}")
    print(f"Module:  {config['module_name']}")
    print(f"Author:  {config['author_name']} <{config['author_email']}>")

    # Handle cleanup and git initialization based on arguments
    if args.skip_cleanup:
        print("\\n⚠️  Skipping cleanup (keeping setup script)")
    else:
        if args.yes or not args.skip_cleanup:
            cleanup_template_files()
        else:
            cleanup = input("\\nRemove template files? (Y/n): ").strip().lower()
            if cleanup not in ["n", "no"]:
                cleanup_template_files()

    # Handle git initialization
    if args.no_git:
        print("⚠️  Skipping git initialization")
    else:
        if args.yes:
            remove_template_git_history()
            initialize_new_git_repo()
            create_initial_git_commit(config)
        else:
            git_init = input("\\nInitialize new git repository? (Y/n): ").strip().lower()
            if git_init not in ["n", "no"]:
                remove_template_git_history()
                initialize_new_git_repo()
                create_initial_git_commit(config)

    # Change back to original directory
    os.chdir(original_dir)

    print("\\n✨ Your new Python project is ready!")
    print(f"\\n📁 Project created at: {output_dir}")
    print("\\nNext steps:")
    print(f"1. cd {output_dir}")
    print("2. Create a virtual environment: python -m venv .venv")
    print("3. Activate: source .venv/bin/activate  # Win: .venv\\Scripts\\activate")
    print("4. Install dependencies: pip install -e '.[dev]'")
    if not args.no_git:
        print("5. Install pre-commit hooks: pre-commit install")
        print("6. Start coding! 🚀")
    else:
        print("5. Initialize git: git init")
        print("6. Install pre-commit hooks: pre-commit install")
        print("7. Start coding! 🚀")


if __name__ == "__main__":
    main()
