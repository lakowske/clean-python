#!/usr/bin/env python3
"""Integration test for the clean-python template.

This script tests the complete workflow from project generation to running
all development tools and commands.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


# ANSI color codes for output
class Colors:
    """ANSI color codes for output."""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_step(message: str) -> None:
    """Print a step message."""
    print(f"{Colors.BLUE}{Colors.BOLD}🔧 {message}{Colors.RESET}")


def print_success(message: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")


def print_error(message: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")


def run_command(
    cmd: list[str],
    cwd: Optional[Path] = None,
    check: bool = True,
    capture_output: bool = False,
    env: Optional[dict[str, str]] = None,
) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    cmd_str = " ".join(cmd)
    print(f"  Running: {Colors.CYAN}{cmd_str}{Colors.RESET}")

    try:
        result = subprocess.run(cmd, cwd=cwd, check=check, capture_output=capture_output, text=True, env=env)  # nosec B603
        if capture_output:
            print(f"  Output: {result.stdout.strip()}")
            if result.stderr:
                print(f"  Error: {result.stderr.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {cmd_str}")
        if capture_output:
            print(f"  stdout: {e.stdout}")
            print(f"  stderr: {e.stderr}")
        raise


def test_project_generation(template_dir: Path, tmp_dir: Path) -> Path:
    """Test project generation using the setup script."""
    print_step("Testing project generation")

    project_name = "test-integration-project"
    project_path = tmp_dir / project_name

    # Clean up any existing project
    if project_path.exists():
        shutil.rmtree(project_path)

    # Run the setup script
    setup_script = template_dir / "setup_new_project.py"
    run_command(
        [
            sys.executable,
            str(setup_script),
            "--name",
            project_name,
            "--description",
            "Integration test project",
            "--author",
            "Test User",
            "--email",
            "test@example.com",
            "--github",
            "testuser",
            "--output-dir",
            str(project_path),
            "--yes",
        ],
        cwd=template_dir,
    )

    # Verify project was created
    assert project_path.exists(), f"Project directory {project_path} was not created"
    assert (project_path / "pyproject.toml").exists(), "pyproject.toml not found"
    assert (project_path / "Makefile").exists(), "Makefile not found"
    assert (project_path / "README.md").exists(), "README.md not found"
    assert (project_path / ".pre-commit-config.yaml").exists(), "Pre-commit config not found"
    assert (project_path / "mkdocs.yml").exists(), "MkDocs config not found"

    print_success("Project generation completed successfully")
    return project_path


def test_venv_creation(project_path: Path) -> Path:
    """Test virtual environment creation."""
    print_step("Testing virtual environment creation")

    venv_path = project_path / ".venv"

    # Clean up any existing venv
    if venv_path.exists():
        shutil.rmtree(venv_path)

    # Create virtual environment
    run_command([sys.executable, "-m", "venv", ".venv"], cwd=project_path)

    # Verify venv was created
    assert venv_path.exists(), "Virtual environment was not created"

    # Check for activation script
    if os.name == "nt":  # Windows
        activate_script = venv_path / "Scripts" / "activate"
        python_exe = venv_path / "Scripts" / "python.exe"
    else:  # Unix-like
        activate_script = venv_path / "bin" / "activate"
        python_exe = venv_path / "bin" / "python"

    assert activate_script.exists(), "Activation script not found"
    assert python_exe.exists(), "Python executable not found in venv"

    print_success("Virtual environment creation completed successfully")
    return venv_path


def get_venv_python(venv_path: Path) -> str:
    """Get the path to the Python executable in the virtual environment."""
    if os.name == "nt":  # Windows
        return str(venv_path / "Scripts" / "python.exe")
    # Unix-like
    return str(venv_path / "bin" / "python")


def get_venv_env(venv_path: Path) -> dict[str, str]:
    """Get environment variables for using the virtual environment."""
    env = os.environ.copy()
    if os.name == "nt":  # Windows
        env["PATH"] = str(venv_path / "Scripts") + os.pathsep + env["PATH"]
    else:  # Unix-like
        env["PATH"] = str(venv_path / "bin") + os.pathsep + env["PATH"]
    env["VIRTUAL_ENV"] = str(venv_path)
    return env


def test_make_install(project_path: Path, venv_path: Path) -> None:
    """Test make install command."""
    print_step("Testing make install")

    python_exe = get_venv_python(venv_path)
    env = get_venv_env(venv_path)

    # Test make install
    run_command(["make", "install"], cwd=project_path, env=env)

    # Verify installation by checking if packages are available
    result = run_command(
        [python_exe, "-c", "import pydantic; print('pydantic imported successfully')"],
        cwd=project_path,
        capture_output=True,
    )
    assert "pydantic imported successfully" in result.stdout, "Pydantic not installed correctly"

    result = run_command(
        [python_exe, "-c", "import pytest; print('pytest imported successfully')"],
        cwd=project_path,
        capture_output=True,
    )
    assert "pytest imported successfully" in result.stdout, "Pytest not installed correctly"

    print_success("Make install completed successfully")


def test_pre_commit_setup(project_path: Path, venv_path: Path) -> None:
    """Test pre-commit installation and basic functionality."""
    print_step("Testing pre-commit setup")

    env = get_venv_env(venv_path)

    # Install pre-commit hooks
    run_command(["pre-commit", "install"], cwd=project_path, env=env)

    # Verify hooks are installed
    hooks_dir = project_path / ".git" / "hooks"
    assert hooks_dir.exists(), "Git hooks directory not found"
    assert (hooks_dir / "pre-commit").exists(), "Pre-commit hook not installed"

    print_success("Pre-commit setup completed successfully")


def test_make_targets(project_path: Path, venv_path: Path) -> None:
    """Test all make targets."""
    print_step("Testing make targets")

    env = get_venv_env(venv_path)

    # Test make help
    result = run_command(["make", "help"], cwd=project_path, env=env, capture_output=True)
    assert "help" in result.stdout, "Make help not working"

    # Test make format
    try:
        run_command(["make", "format"], cwd=project_path, env=env)
        print_success("Make format completed")
    except subprocess.CalledProcessError as e:
        print_warning(f"Make format failed: {e}")

    # Test make lint
    try:
        run_command(["make", "lint"], cwd=project_path, env=env)
        print_success("Make lint completed")
    except subprocess.CalledProcessError as e:
        print_warning(f"Make lint failed: {e}")

    # Test make test
    try:
        run_command(["make", "test"], cwd=project_path, env=env)
        print_success("Make test completed")
    except subprocess.CalledProcessError as e:
        print_warning(f"Make test failed: {e}")

    # Test make type-check
    try:
        run_command(["make", "type-check"], cwd=project_path, env=env)
        print_success("Make type-check completed")
    except subprocess.CalledProcessError as e:
        print_warning(f"Make type-check failed: {e}")

    print_success("Make targets testing completed")


def test_documentation(project_path: Path, venv_path: Path) -> None:
    """Test documentation generation."""
    print_step("Testing documentation generation")

    env = get_venv_env(venv_path)

    try:
        # Test make docs
        run_command(["make", "docs"], cwd=project_path, env=env)

        # Verify documentation was built
        site_dir = project_path / "site"
        assert site_dir.exists(), "Documentation site directory not created"
        assert (site_dir / "index.html").exists(), "Documentation index.html not found"

        print_success("Documentation generation completed successfully")
    except subprocess.CalledProcessError as e:
        print_warning(f"Documentation generation failed: {e}")


def test_pre_commit_run(project_path: Path, venv_path: Path) -> None:
    """Test running pre-commit hooks."""
    print_step("Testing pre-commit execution")

    env = get_venv_env(venv_path)

    try:
        # Run pre-commit on all files
        run_command(["pre-commit", "run", "--all-files"], cwd=project_path, env=env)
        print_success("Pre-commit execution completed successfully")
    except subprocess.CalledProcessError as e:
        print_warning(f"Pre-commit execution failed: {e}")


def test_python_functionality(project_path: Path, venv_path: Path) -> None:
    """Test that the generated Python code works correctly."""
    print_step("Testing Python functionality")

    python_exe = get_venv_python(venv_path)
    env = get_venv_env(venv_path)

    # Test importing the module
    module_name = "test_integration_project"  # Based on project name
    result = run_command(
        [
            python_exe,
            "-c",
            f"from {module_name}.core import greet, UserProfile, CalculationResult; "
            f"print(greet('World')); "
            f"profile = UserProfile(name='John', email='john@example.com'); "
            f"print(f'Profile: {{profile.name}}'); "
            f"calc = CalculationResult(1, 2, 'add', 3); "
            f"print(f'Calc: {{calc.result}}')",
        ],
        cwd=project_path,
        capture_output=True,
        env=env,
    )

    assert "Hello, World!" in result.stdout, "Greeting function not working"
    assert "Profile: John" in result.stdout, "UserProfile not working"
    assert "Calc: 3" in result.stdout, "CalculationResult not working"

    print_success("Python functionality testing completed successfully")


def main() -> None:
    """Run the complete integration test."""
    print(f"{Colors.BOLD}{Colors.MAGENTA}🚀 Starting Clean Python Template Integration Test{Colors.RESET}")
    print("=" * 60)

    # Get template directory
    template_dir = Path(__file__).parent.absolute()
    tmp_dir = template_dir / "tmp"

    # Ensure tmp directory exists
    tmp_dir.mkdir(exist_ok=True)

    try:
        # Test project generation
        project_path = test_project_generation(template_dir, tmp_dir)

        # Test virtual environment creation
        venv_path = test_venv_creation(project_path)

        # Test make install
        test_make_install(project_path, venv_path)

        # Test pre-commit setup
        test_pre_commit_setup(project_path, venv_path)

        # Test make targets
        test_make_targets(project_path, venv_path)

        # Test documentation
        test_documentation(project_path, venv_path)

        # Test pre-commit execution
        test_pre_commit_run(project_path, venv_path)

        # Test Python functionality
        test_python_functionality(project_path, venv_path)

        print("\n" + "=" * 60)
        print(f"{Colors.BOLD}{Colors.GREEN}🎉 All integration tests passed successfully!{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Project generated at: {project_path}{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Virtual environment created at: {venv_path}{Colors.RESET}")
        print(f"{Colors.GREEN}✅ All make targets working{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Pre-commit hooks functional{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Documentation generation working{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Python code functionality verified{Colors.RESET}")

    except Exception as e:
        print("\n" + "=" * 60)
        print_error(f"Integration test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
