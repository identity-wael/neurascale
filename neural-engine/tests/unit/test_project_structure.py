"""Test the Neural Engine project structure."""

import pytest
from pathlib import Path


class TestProjectStructure:
    """Verify the Neural Engine project structure is correct."""

    @pytest.fixture
    def project_root(self):
        """Get the neural-engine project root."""
        # Go up from tests/unit to neural-engine
        return Path(__file__).parent.parent.parent

    def test_required_directories_exist(self, project_root):
        """Test that all required directories exist."""
        required_dirs = [
            "src",
            "tests",
            "tests/unit",
            "tests/integration",
            "tests/performance",
            "functions",
            "docker",
            "configs",
            "scripts",
            "docs",
        ]

        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            assert dir_path.exists(), f"Required directory {dir_name} does not exist"
            assert dir_path.is_dir(), f"{dir_name} is not a directory"

    def test_required_files_exist(self, project_root):
        """Test that all required files exist."""
        required_files = [
            "README.md",
            "requirements.txt",
            "requirements-dev.txt",
            "setup.py",
            ".flake8",
            "pytest.ini",
        ]

        for file_name in required_files:
            file_path = project_root / file_name
            assert file_path.exists(), f"Required file {file_name} does not exist"
            assert file_path.is_file(), f"{file_name} is not a file"

    def test_src_structure(self, project_root):
        """Test the src directory structure."""
        src_modules = [
            "src/neural_engine",
            "src/neural_engine/__init__.py",
            "src/processors",
            "src/processors/__init__.py",
            "src/api",
            "src/api/__init__.py",
            "src/utils",
            "src/utils/__init__.py",
        ]

        for module_path in src_modules:
            path = project_root / module_path
            assert path.exists(), f"Module {module_path} does not exist"

    def test_docker_files(self, project_root):
        """Test Docker configuration files."""
        docker_files = [
            "docker/Dockerfile.processor",
            "docker/Dockerfile.api",
            "docker/docker-compose.yml",
            "docker/docker-compose.dev.yml",
        ]

        for docker_file in docker_files:
            path = project_root / docker_file
            assert path.exists(), f"Docker file {docker_file} does not exist"

    def test_gcp_configuration(self, project_root):
        """Test Google Cloud configuration files."""
        gcp_files = [
            "cloudbuild.yaml",
            "app.yaml",
        ]

        for gcp_file in gcp_files:
            path = project_root / gcp_file
            assert path.exists(), f"GCP configuration file {gcp_file} does not exist"
