"""
Result validators for ensuring output quality.

Validators:
- Git apply --check for patches
- JSON schema validation
- Pytest execution
- Simple rubric graders
"""

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import subprocess

from conductor.envelopes import ResultEnvelope, Artifact, ArtifactType


class Validator:
    """Base validator class."""

    async def validate(self, artifact: Artifact) -> Tuple[bool, Optional[str]]:
        """
        Validate artifact.

        Returns: (is_valid, error_message)
        """
        raise NotImplementedError


class PatchValidator(Validator):
    """Validates patches using git apply --check."""

    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = repo_path

    async def validate(self, artifact: Artifact) -> Tuple[bool, Optional[str]]:
        """Validate that patch can be applied."""
        if artifact.type != ArtifactType.PATCH:
            return False, "Not a patch artifact"

        if not artifact.content:
            return False, "Empty patch content"

        # Write patch to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False) as f:
            f.write(artifact.content)
            patch_file = f.name

        try:
            # Try git apply --check
            cmd = ['git', 'apply', '--check', patch_file]
            if self.repo_path:
                cmd.extend(['-C', self.repo_path])

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return True, None
            else:
                return False, f"Patch validation failed: {stderr.decode()}"

        except Exception as e:
            return False, f"Patch validation error: {str(e)}"
        finally:
            Path(patch_file).unlink(missing_ok=True)


class JSONSchemaValidator(Validator):
    """Validates JSON against a schema."""

    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        try:
            import jsonschema
            self.jsonschema = jsonschema
        except ImportError:
            self.jsonschema = None

    async def validate(self, artifact: Artifact) -> Tuple[bool, Optional[str]]:
        """Validate JSON against schema."""
        if artifact.type != ArtifactType.JSON:
            return False, "Not a JSON artifact"

        if not self.jsonschema:
            return False, "jsonschema package not installed"

        try:
            data = json.loads(artifact.content)
            self.jsonschema.validate(data, self.schema)
            return True, None
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
        except self.jsonschema.ValidationError as e:
            return False, f"Schema validation failed: {str(e)}"


class PytestValidator(Validator):
    """Runs pytest on generated test code."""

    def __init__(self, test_dir: Optional[str] = None):
        self.test_dir = test_dir

    async def validate(self, artifact: Artifact) -> Tuple[bool, Optional[str]]:
        """Run pytest on test file."""
        if not artifact.path and not artifact.content:
            return False, "No test code provided"

        # Write to temp file if content provided
        if artifact.content:
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='_test.py', delete=False
            ) as f:
                f.write(artifact.content)
                test_file = f.name
        else:
            test_file = artifact.path

        try:
            # Run pytest
            process = await asyncio.create_subprocess_exec(
                'pytest',
                test_file,
                '-v',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return True, None
            else:
                return False, f"Tests failed: {stderr.decode()}"

        except Exception as e:
            return False, f"Pytest execution error: {str(e)}"
        finally:
            if artifact.content:
                Path(test_file).unlink(missing_ok=True)


class RubricValidator(Validator):
    """Simple rubric-based validation."""

    def __init__(self, rubric: Dict[str, Any]):
        """
        Args:
            rubric: Dict with validation rules, e.g.:
                {
                    "min_length": 100,
                    "required_keywords": ["function", "return"],
                    "forbidden_keywords": ["TODO", "FIXME"],
                }
        """
        self.rubric = rubric

    async def validate(self, artifact: Artifact) -> Tuple[bool, Optional[str]]:
        """Validate against rubric."""
        content = artifact.content or ""

        # Check minimum length
        if "min_length" in self.rubric:
            if len(content) < self.rubric["min_length"]:
                return False, f"Content too short: {len(content)} < {self.rubric['min_length']}"

        # Check required keywords
        if "required_keywords" in self.rubric:
            for keyword in self.rubric["required_keywords"]:
                if keyword not in content:
                    return False, f"Missing required keyword: {keyword}"

        # Check forbidden keywords
        if "forbidden_keywords" in self.rubric:
            for keyword in self.rubric["forbidden_keywords"]:
                if keyword in content:
                    return False, f"Contains forbidden keyword: {keyword}"

        # Check max length
        if "max_length" in self.rubric:
            if len(content) > self.rubric["max_length"]:
                return False, f"Content too long: {len(content)} > {self.rubric['max_length']}"

        return True, None


class ValidationSuite:
    """Orchestrates multiple validators."""

    def __init__(self):
        self.validators: Dict[str, Validator] = {}

    def add_validator(self, name: str, validator: Validator):
        """Add a validator to the suite."""
        self.validators[name] = validator

    async def validate_result(
        self, result: ResultEnvelope
    ) -> Tuple[bool, Dict[str, Tuple[bool, Optional[str]]]]:
        """
        Validate all artifacts in result.

        Returns: (all_valid, per_artifact_results)
        """
        all_valid = True
        results = {}

        for i, artifact in enumerate(result.artifacts):
            artifact_results = {}

            for name, validator in self.validators.items():
                is_valid, error = await validator.validate(artifact)
                artifact_results[name] = (is_valid, error)

                if not is_valid:
                    all_valid = False

            results[f"artifact_{i}"] = artifact_results

        return all_valid, results
