from __future__ import annotations

from conductor.envelopes import ArtifactType
from conductor.harvest import Harvester


def test_harvest_extracts_json_artifact() -> None:
    content = """
    {"status": "ok", "count": 2}
    """.strip()

    artifacts = Harvester.harvest(content)
    assert any(artifact.type == ArtifactType.JSON for artifact in artifacts)


def test_harvest_extracts_code_fence_language_metadata() -> None:
    content = """Example:\n```python\nprint('hi')\n```"""
    artifacts = Harvester.harvest(content)
    code_artifacts = [a for a in artifacts if a.metadata.get("language") == "python"]
    assert code_artifacts
    assert code_artifacts[0].type == ArtifactType.TEXT


def test_harvest_extracts_diffs() -> None:
    content = """diff --git a/file.txt b/file.txt\n--- a/file.txt\n+++ b/file.txt\n@@\n-line\n+line updated\n"""
    artifacts = Harvester.harvest(content)
    assert any(a.type == ArtifactType.PATCH for a in artifacts)


def test_extract_key_value_pairs() -> None:
    content = "status: ok\nerrors: none\ninvalid line"
    pairs = Harvester.extract_key_value_pairs(content)
    assert pairs == {"status": "ok", "errors": "none"}
