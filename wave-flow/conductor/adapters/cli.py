"""
CLI adapter for executing command-line tools.

Spawns subprocess, handles stdin/files, harvests stdout/stderr.
"""

import asyncio
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import re

from conductor.adapters.base import BaseAdapter, ToolCapability
from conductor.envelopes import (
    TaskEnvelope,
    ResultEnvelope,
    TaskStatus,
    Artifact,
    ArtifactType,
    Diagnostics,
    Provenance,
)


class CLIAdapter(BaseAdapter):
    """
    Adapter for generic CLI tools.

    Supports:
    - Command execution with args
    - Stdin input
    - File-based input/output
    - Timeout handling
    - Sandboxed temp directories
    """

    def __init__(
        self,
        capability: ToolCapability,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(capability, config)
        self.command = config.get("command") if config else None
        self.allowed_commands = config.get("allowed_commands", []) if config else []
        self.timeout_default = config.get("timeout_default", 300)  # 5 min default

    async def execute(self, task: TaskEnvelope) -> ResultEnvelope:
        """Execute CLI tool with task inputs."""
        start_time = time.time()
        started_at = datetime.now()

        # Validate task
        is_valid, error_msg = self.validate_task(task)
        if not is_valid:
            return ResultEnvelope(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error=error_msg,
            )

        # Extract command and args from task inputs
        command = task.inputs.get("command", self.command)
        args = task.inputs.get("args", [])
        stdin_data = task.inputs.get("stdin")
        input_files = task.inputs.get("input_files", {})
        env = task.inputs.get("env", {})
        
        # Validate and sanitize command and args to prevent injection
        if command:
            # Basic command validation - only allow alphanumeric chars, hyphens, underscores, and periods
            if not re.match(r'^[a-zA-Z0-9_\-\.]+
            return ResultEnvelope(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error="No command specified",
            )

        # Security check
        if self.allowed_commands and command not in self.allowed_commands:
            return ResultEnvelope(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error=f"Command '{command}' not in allowed list",
            )

        # Create sandboxed temp directory
        with tempfile.TemporaryDirectory(prefix="conductor_") as tmpdir:
            tmppath = Path(tmpdir)

            # Write input files
            for filename, content in input_files.items():
                filepath = tmppath / filename
                filepath.parent.mkdir(parents=True, exist_ok=True)
                filepath.write_text(content)

            # Prepare environment
            full_env = {**subprocess.os.environ.copy(), **env}
            full_env["CONDUCTOR_TMPDIR"] = str(tmppath)

            # Determine timeout
            timeout = task.constraints.deadline_ms / 1000 if task.constraints.deadline_ms else self.timeout_default

            try:
                # Build full command
                full_command = [command] + args

                # Execute subprocess
                process = await asyncio.create_subprocess_exec(
                    *full_command,
                    stdin=subprocess.PIPE if stdin_data else None,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(tmppath),
                    env=full_env,
                )

                # Wait for completion with timeout
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(
                            input=stdin_data.encode() if stdin_data else None
                        ),
                        timeout=timeout,
                    )
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                    latency_ms = (time.time() - start_time) * 1000
                    return ResultEnvelope(
                        task_id=task.id,
                        status=TaskStatus.TIMEOUT,
                        error=f"Command timed out after {timeout}s",
                        diagnostics=Diagnostics(latency_ms=latency_ms),
                        provenance=Provenance(
                            tool=self.capability.name,
                            version=self.capability.version,
                            args={"command": command, "args": args},
                            env={k: v for k, v in env.items() if "SECRET" not in k.upper()},
                            started_at=started_at,
                            completed_at=datetime.now(),
                        ),
                    )

                latency_ms = (time.time() - start_time) * 1000

                # Check return code
                if process.returncode != 0:
                    return ResultEnvelope(
                        task_id=task.id,
                        status=TaskStatus.FAILED,
                        error=f"Command exited with code {process.returncode}: {stderr.decode()}",
                        diagnostics=Diagnostics(latency_ms=latency_ms),
                        provenance=Provenance(
                            tool=self.capability.name,
                            version=self.capability.version,
                            args={"command": command, "args": args},
                            env={k: v for k, v in env.items() if "SECRET" not in k.upper()},
                            started_at=started_at,
                            completed_at=datetime.now(),
                        ),
                    )

                # Harvest output
                artifacts = []

                # Stdout as primary artifact
                if stdout:
                    artifacts.append(
                        Artifact(
                            type=ArtifactType.TEXT,
                            content=stdout.decode(),
                            metadata={"source": "stdout"},
                        )
                    )

                # Stderr as warning if present
                warnings = []
                if stderr:
                    warnings.append(f"stderr: {stderr.decode()}")

                # Harvest output files
                output_patterns = task.inputs.get("output_patterns", [])
                for pattern in output_patterns:
                    for filepath in tmppath.glob(pattern):
                        if filepath.is_file():
                            content = filepath.read_text()
                            artifact_type = self._detect_artifact_type(filepath.suffix)
                            artifacts.append(
                                Artifact(
                                    type=artifact_type,
                                    content=content if len(content) < 100000 else None,
                                    path=str(filepath) if len(content) >= 100000 else None,
                                    metadata={"filename": filepath.name},
                                    size_bytes=len(content),
                                )
                            )

                return ResultEnvelope(
                    task_id=task.id,
                    status=TaskStatus.COMPLETED,
                    artifacts=artifacts,
                    warnings=warnings,
                    diagnostics=Diagnostics(
                        latency_ms=latency_ms,
                        provider="local",
                    ),
                    provenance=Provenance(
                        tool=self.capability.name,
                        version=self.capability.version,
                        args={"command": command, "args": args},
                        env={k: v for k, v in env.items() if "SECRET" not in k.upper()},
                        started_at=started_at,
                        completed_at=datetime.now(),
                    ),
                )

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                return ResultEnvelope(
                    task_id=task.id,
                    status=TaskStatus.FAILED,
                    error=f"Execution error: {str(e)}",
                    diagnostics=Diagnostics(latency_ms=latency_ms),
                    provenance=Provenance(
                        tool=self.capability.name,
                        version=self.capability.version,
                        args={"command": command, "args": args},
                        env={k: v for k, v in env.items() if "SECRET" not in k.upper()},
                        started_at=started_at,
                        completed_at=datetime.now(),
                    ),
                )

    async def health_check(self) -> bool:
        """Check if command is available."""
        if not self.command:
            return False

        try:
            # Try to get version or help
            process = await asyncio.create_subprocess_exec(
                self.command,
                "--version",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            await asyncio.wait_for(process.communicate(), timeout=5.0)
            return process.returncode == 0
        except:
            return False

    def _detect_artifact_type(self, suffix: str) -> ArtifactType:
        """Detect artifact type from file extension."""
        type_map = {
            ".patch": ArtifactType.PATCH,
            ".diff": ArtifactType.PATCH,
, Path(command).name):
                return ResultEnvelope(
                    task_id=task.id,
                    status=TaskStatus.FAILED,
                    error=f"Invalid command format: {command}",
                )
        
        # Validate arguments to prevent injection
        sanitized_args = []
        for arg in args:
            # Convert to string and validate
            arg_str = str(arg)
, Path(command).name):
                return ResultEnvelope(
                    task_id=task.id,
                    status=TaskStatus.FAILED,
                    error=f"Invalid command format: {command}",
                )
        
        # Validate arguments to prevent injection
        sanitized_args = []
