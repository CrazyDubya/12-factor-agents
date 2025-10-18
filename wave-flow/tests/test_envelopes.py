from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from conductor.envelopes import (
    Artifact,
    ArtifactType,
    Diagnostics,
    ResultEnvelope,
    TaskEnvelope,
    TaskStatus,
)


def test_artifact_compute_checksum_for_inline_content() -> None:
    artifact = Artifact(type=ArtifactType.TEXT, content="hello world")
    expected = hashlib.sha256(b"hello world").hexdigest()
    assert artifact.compute_checksum() == expected


def test_artifact_compute_checksum_for_file_path(tmp_path: Path) -> None:
    file_path = tmp_path / "data.txt"
    file_path.write_text("wave-flow")
    artifact = Artifact(type=ArtifactType.FILE, path=str(file_path))
    expected = hashlib.sha256(b"wave-flow").hexdigest()
    assert artifact.compute_checksum() == expected


def test_task_envelope_hash_inputs_is_deterministic() -> None:
    inputs = {"repo": "demo", "depth": 3}
    task1 = TaskEnvelope(id="task-1", intent="analyze repo", inputs=inputs)
    task2 = TaskEnvelope(id="task-1", intent="analyze repo", inputs=json.loads(json.dumps(inputs)))
    assert task1.hash_inputs() == task2.hash_inputs()


def test_result_envelope_helpers() -> None:
    diagnostics = Diagnostics(latency_ms=120.0, cost_usd=1.5)
    result = ResultEnvelope(
        task_id="task-1",
        status=TaskStatus.COMPLETED,
        diagnostics=diagnostics,
    )

    assert result.is_success()
    assert result.total_cost() == 1.5
    assert result.total_latency() == 120.0

    degraded = ResultEnvelope(task_id="task-1", status=TaskStatus.DEGRADED)
    assert degraded.is_success()

    failed = ResultEnvelope(task_id="task-1", status=TaskStatus.FAILED)
    assert not failed.is_success()
