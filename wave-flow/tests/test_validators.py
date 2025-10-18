from __future__ import annotations

import json
import types

import pytest

from conductor.envelopes import Artifact, ArtifactType, ResultEnvelope, TaskStatus
from conductor.validators import JSONSchemaValidator, PytestValidator, RubricValidator, ValidationSuite


@pytest.mark.asyncio
async def test_jsonschema_validator_accepts_valid_payload() -> None:
    schema = {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}
    validator = JSONSchemaValidator(schema)

    if validator.jsonschema is None:
        validator.jsonschema = types.SimpleNamespace(validate=lambda data, schema: None)

    artifact = Artifact(type=ArtifactType.JSON, content=json.dumps({"name": "wave"}))
    is_valid, error = await validator.validate(artifact)
    assert is_valid
    assert error is None


@pytest.mark.asyncio
async def test_jsonschema_validator_reports_invalid_json() -> None:
    validator = JSONSchemaValidator({"type": "object"})
    if validator.jsonschema is None:
        def raise_error(_data, _schema):
            raise ValueError("boom")

        validator.jsonschema = types.SimpleNamespace(validate=raise_error)

    artifact = Artifact(type=ArtifactType.JSON, content="not json")
    is_valid, error = await validator.validate(artifact)
    assert not is_valid
    assert error is not None


@pytest.mark.asyncio
async def test_rubric_validator_enforces_rules() -> None:
    validator = RubricValidator({"required_keywords": ["pass"], "forbidden_keywords": ["fail"]})

    passing_artifact = Artifact(type=ArtifactType.TEXT, content="please pass this test")
    is_valid, error = await validator.validate(passing_artifact)
    assert is_valid
    assert error is None

    failing_artifact = Artifact(type=ArtifactType.TEXT, content="please pass but fail anyway")
    is_valid, error = await validator.validate(failing_artifact)
    assert not is_valid
    assert "forbidden" in error.lower()


@pytest.mark.asyncio
async def test_pytest_validator_requires_content_or_path() -> None:
    validator = PytestValidator()
    artifact = Artifact(type=ArtifactType.TEXT, content=None, path=None)
    is_valid, error = await validator.validate(artifact)
    assert not is_valid
    assert "no test code" in error.lower()


@pytest.mark.asyncio
async def test_validation_suite_aggregates_results() -> None:
    suite = ValidationSuite()
    suite.add_validator("rubric", RubricValidator({"required_keywords": ["ready"]}))

    artifact = Artifact(type=ArtifactType.TEXT, content="system ready")
    envelope = ResultEnvelope(task_id="task", status=TaskStatus.COMPLETED, artifacts=[artifact])

    all_valid, results = await suite.validate_result(envelope)
    assert all_valid
    assert "artifact_0" in results
    assert results["artifact_0"]["rubric"][0]
