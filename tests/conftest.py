"""Test configuration and fixtures for pytest."""

import glob
import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_databases():
    """Clean up any database files created during test runs."""
    # Get the test directory path
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(test_dir)

    # Patterns for database files that might be created
    db_patterns = [
        os.path.join(project_root, "*.db"),
        os.path.join(project_root, "src", "*.db"),
        os.path.join(test_dir, "*.db"),
        "youth_data.db",
        "test*.db",
        "*.sqlite",
        "*.sqlite3",
    ]

    def cleanup_files():
        """Remove any database files."""
        removed_files = []
        for pattern in db_patterns:
            files = glob.glob(pattern)
            for file_path in files:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        removed_files.append(file_path)
                except OSError as e:
                    # Log but don't fail if we can't remove a file
                    print(f"Warning: Could not remove {file_path}: {e}")

        if removed_files:
            print(f"Cleaned up database files: {removed_files}")

    # Clean up before tests
    cleanup_files()

    # Run tests
    yield

    # Clean up after tests
    cleanup_files()


@pytest.fixture(autouse=True)
def clean_environment():
    """Clean environment variables that might affect tests."""
    # Store original values
    original_env = {}
    env_vars_to_clean = ["POPULATEDUMMY", "POSTGRESCONNECTIONSTRING"]

    for var in env_vars_to_clean:
        original_env[var] = os.environ.get(var)

    yield

    # Restore original environment
    for var, value in original_env.items():
        if value is None:
            os.environ.pop(var, None)
        else:
            os.environ[var] = value
