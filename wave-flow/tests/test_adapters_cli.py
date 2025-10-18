from __future__ import annotations

import sys

import pytest

from conductor.adapters.cli import CLIAdapter
from conductor.envelopes import TaskConstraints, TaskEnvelope, TaskStatus
from tests.utils import make_capability


@pytest.mark.asyncio
async def test_cli_adapter_executes_python_command() -> None:
    capability = make_capability(name="python", intents=["run"])
    python_cmd = sys.executable
    adapter = CLIAdapter(
        capability,
        config={"command": python_cmd, "allowed_commands": [python_cmd]},
    )

    task = TaskEnvelope(
        id="cli-1",
        intent="run",
        inputs={"args": ["-c", "print('hello from cli')"]},
        constraints=TaskConstraints(),
    )

    result = await adapter.execute(task)

    assert result.status == TaskStatus.COMPLETED
    assert result.artifacts
    stdout = result.artifacts[0].content or ""
    assert "hello from cli" in stdout


@pytest.mark.asyncio
async def test_cli_adapter_rejects_disallowed_command() -> None:
    capability = make_capability(name="python", intents=["run"])
    python_cmd = sys.executable
    adapter = CLIAdapter(
        capability,
        config={"command": python_cmd, "allowed_commands": [python_cmd]},
    )

    task = TaskEnvelope(
        id="cli-2",
        intent="run",
        inputs={"command": "bash", "args": ["-c", "echo hi"]},
        constraints=TaskConstraints(),
    )

    result = await adapter.execute(task)
    assert result.status == TaskStatus.FAILED
    assert "not in allowed list" in (result.error or "")
