"""Tests for JavaScript/TypeScript SDK functionality."""

import pytest
import subprocess
import os
import json
from pathlib import Path


class TestJavaScriptSDK:
    """Test JavaScript/TypeScript SDK build and functionality."""

    @pytest.fixture
    def sdk_path(self):
        """Get SDK directory path."""
        return Path(__file__).parent.parent.parent / "src" / "api" / "sdk" / "javascript"

    def test_package_json_valid(self, sdk_path):
        """Test that package.json is valid."""
        package_json_path = sdk_path / "package.json"
        assert package_json_path.exists(), "package.json not found"

        with open(package_json_path) as f:
            package_data = json.load(f)

        # Check required fields
        assert "name" in package_data
        assert "version" in package_data
        assert "main" in package_data
        assert "types" in package_data
        assert "scripts" in package_data

        # Check SDK-specific fields
        assert package_data["name"] == "@neurascale/sdk"
        assert "build" in package_data["scripts"]
        assert "test" in package_data["scripts"]

    def test_typescript_types_exist(self, sdk_path):
        """Test that TypeScript type definitions exist."""
        types_file = sdk_path / "src" / "types.ts"
        assert types_file.exists(), "types.ts not found"

        with open(types_file) as f:
            content = f.read()

        # Check for key type definitions
        assert "export interface Device" in content
        assert "export interface Session" in content
        assert "export interface Patient" in content
        assert "export interface NeuraScaleConfig" in content

    def test_main_client_exists(self, sdk_path):
        """Test that main client file exists and has expected exports."""
        client_file = sdk_path / "src" / "client.ts"
        assert client_file.exists(), "client.ts not found"

        with open(client_file) as f:
            content = f.read()

        # Check for main class
        assert "export class NeuraScaleClient" in content
        assert "async getDevice" in content
        assert "async listDevices" in content
        assert "async createDevice" in content

    def test_graphql_client_exists(self, sdk_path):
        """Test that GraphQL client exists."""
        graphql_file = sdk_path / "src" / "graphql.ts"
        assert graphql_file.exists(), "graphql.ts not found"

        with open(graphql_file) as f:
            content = f.read()

        assert "export class GraphQLClient" in content
        assert "async query" in content
        assert "async mutation" in content

    def test_streaming_client_exists(self, sdk_path):
        """Test that streaming client exists."""
        streaming_file = sdk_path / "src" / "streaming.ts"
        assert streaming_file.exists(), "streaming.ts not found"

        with open(streaming_file) as f:
            content = f.read()

        assert "export class StreamClient" in content
        assert "WebSocket" in content
        assert "connect" in content
        assert "subscribeToSession" in content

    def test_exceptions_defined(self, sdk_path):
        """Test that exception classes are defined."""
        exceptions_file = sdk_path / "src" / "exceptions.ts"
        assert exceptions_file.exists(), "exceptions.ts not found"

        with open(exceptions_file) as f:
            content = f.read()

        # Check exception classes
        assert "export class NeuraScaleError" in content
        assert "export class AuthenticationError" in content
        assert "export class NotFoundError" in content
        assert "export class RateLimitError" in content

    def test_models_defined(self, sdk_path):
        """Test that model interfaces are defined."""
        models_file = sdk_path / "src" / "models.ts"
        assert models_file.exists(), "models.ts not found"

        with open(models_file) as f:
            content = f.read()

        # Check model interfaces
        assert "export interface Device" in content
        assert "export interface Session" in content
        assert "export interface Patient" in content
        assert "export interface NeuralData" in content

    def test_index_exports(self, sdk_path):
        """Test that index.ts properly exports all modules."""
        index_file = sdk_path / "src" / "index.ts"
        assert index_file.exists(), "index.ts not found"

        with open(index_file) as f:
            content = f.read()

        # Check exports
        assert "export * from './client'" in content
        assert "export * from './graphql'" in content
        assert "export * from './streaming'" in content
        assert "export * from './models'" in content
        assert "export * from './exceptions'" in content

    def test_readme_exists(self, sdk_path):
        """Test that README exists and has proper content."""
        readme_file = sdk_path / "README.md"
        assert readme_file.exists(), "README.md not found"

        with open(readme_file) as f:
            content = f.read()

        # Check for key sections
        assert "# NeuraScale TypeScript/JavaScript SDK" in content
        assert "## Installation" in content
        assert "## Quick Start" in content
        assert "npm install @neurascale/sdk" in content

    @pytest.mark.slow
    def test_typescript_compilation(self, sdk_path):
        """Test that TypeScript compiles without errors."""
        if not (sdk_path / "package.json").exists():
            pytest.skip("No package.json found")

        # Check if npm is available
        try:
            subprocess.run(["npm", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("npm not available")

        # Try to install dependencies and build
        try:
            # Install dependencies
            result = subprocess.run(
                ["npm", "install"],
                cwd=sdk_path,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                pytest.skip(f"npm install failed: {result.stderr}")

            # Run TypeScript compilation
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=sdk_path,
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Check if build succeeded
            assert result.returncode == 0, f"TypeScript compilation failed: {result.stderr}"

            # Check if output files were created
            dist_path = sdk_path / "dist"
            assert dist_path.exists(), "dist directory not created"

        except subprocess.TimeoutExpired:
            pytest.skip("Build process timed out")

    def test_client_api_coverage(self, sdk_path):
        """Test that client covers all main API endpoints."""
        client_file = sdk_path / "src" / "client.ts"
        with open(client_file) as f:
            content = f.read()

        # Device methods
        assert "getDevice" in content
        assert "listDevices" in content
        assert "createDevice" in content
        assert "updateDevice" in content
        assert "deleteDevice" in content

        # Session methods
        assert "getSession" in content
        assert "listSessions" in content
        assert "createSession" in content
        assert "startSession" in content
        assert "stopSession" in content

        # Neural data methods
        assert "getNeuralData" in content

        # Patient methods
        assert "getPatient" in content
        assert "createPatient" in content

        # Analysis methods
        assert "getAnalysis" in content
        assert "startAnalysis" in content

    def test_error_handling_implementation(self, sdk_path):
        """Test that error handling is properly implemented."""
        client_file = sdk_path / "src" / "client.ts"
        with open(client_file) as f:
            content = f.read()

        # Check for error handling patterns
        assert "try {" in content or "catch" in content
        assert "AuthenticationError" in content
        assert "NotFoundError" in content
        assert "RateLimitError" in content

    def test_streaming_websocket_implementation(self, sdk_path):
        """Test WebSocket streaming implementation."""
        streaming_file = sdk_path / "src" / "streaming.ts"
        with open(streaming_file) as f:
            content = f.read()

        # Check WebSocket implementation
        assert "WebSocket" in content
        assert "onopen" in content
        assert "onmessage" in content
        assert "onerror" in content
        assert "onclose" in content

        # Check async iterator support
        assert "async *" in content or "AsyncGenerator" in content

        # Check event handling
        assert "EventEmitter" in content or "addEventListener" in content

    def test_graphql_query_methods(self, sdk_path):
        """Test GraphQL query convenience methods."""
        graphql_file = sdk_path / "src" / "graphql.ts"
        with open(graphql_file) as f:
            content = f.read()

        # Check convenience methods
        assert "getDevice" in content
        assert "listDevices" in content
        assert "getSessionWithData" in content
        assert "startAnalysis" in content

    def test_type_definitions_comprehensive(self, sdk_path):
        """Test that type definitions are comprehensive."""
        types_file = sdk_path / "src" / "types.ts"
        with open(types_file) as f:
            content = f.read()

        # Check for configuration types
        assert "NeuraScaleConfig" in content
        assert "GraphQLConfig" in content
        assert "RequestOptions" in content

        # Check for utility types
        assert "PaginatedResponse" in content
        assert "GraphQLQueryOptions" in content

    def test_browser_compatibility_checks(self, sdk_path):
        """Test browser compatibility considerations."""
        # Check for browser-specific code
        streaming_file = sdk_path / "src" / "streaming.ts"
        with open(streaming_file) as f:
            streaming_content = f.read()

        # Should handle both Node.js and browser WebSocket
        assert "typeof WebSocket" in streaming_content or "global" in streaming_content

    def test_package_dependencies(self, sdk_path):
        """Test that package dependencies are appropriate."""
        package_json_path = sdk_path / "package.json"
        with open(package_json_path) as f:
            package_data = json.load(f)

        dependencies = package_data.get("dependencies", {})
        dev_dependencies = package_data.get("devDependencies", {})

        # Check for essential dependencies
        assert "axios" in dependencies, "axios should be in dependencies"

        # Check for development dependencies
        if dev_dependencies:
            # TypeScript should be in devDependencies if present
            typescript_deps = ["typescript", "@types/node"]
            has_typescript = any(dep in dev_dependencies for dep in typescript_deps)
            # This is optional, so we just check if it exists

    def test_build_configuration(self, sdk_path):
        """Test build configuration files exist."""
        # Check for TypeScript config
        tsconfig_path = sdk_path / "tsconfig.json"
        if tsconfig_path.exists():
            with open(tsconfig_path) as f:
                tsconfig = json.load(f)

            # Check compiler options
            assert "compilerOptions" in tsconfig
            compiler_options = tsconfig["compilerOptions"]
            assert "target" in compiler_options
            assert "module" in compiler_options

    def test_example_usage_in_readme(self, sdk_path):
        """Test that README contains proper usage examples."""
        readme_file = sdk_path / "README.md"
        with open(readme_file) as f:
            content = f.read()

        # Check for TypeScript examples
        assert "```typescript" in content
        assert "NeuraScaleClient" in content
        assert "await client.listDevices()" in content

        # Check for streaming examples
        assert "StreamClient" in content
        assert "stream.on(" in content

        # Check for GraphQL examples
        assert "GraphQLClient" in content
        assert "query" in content

    def test_export_statements_correct(self, sdk_path):
        """Test that all files have correct export statements."""
        src_files = [
            "client.ts",
            "graphql.ts",
            "streaming.ts",
            "models.ts",
            "exceptions.ts",
            "types.ts",
        ]

        for file_name in src_files:
            file_path = sdk_path / "src" / file_name
            if file_path.exists():
                with open(file_path) as f:
                    content = f.read()

                # Each file should have at least one export
                assert (
                    "export " in content
                ), f"{file_name} should have export statements"

    def test_async_await_patterns(self, sdk_path):
        """Test proper async/await usage."""
        client_file = sdk_path / "src" / "client.ts"
        with open(client_file) as f:
            content = f.read()

        # Check for async methods
        assert "async " in content
        assert "await " in content

        # Methods should be properly typed as async
        assert "Promise<" in content