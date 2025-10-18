"""
Data contracts for the Conductor orchestration system.

Defines TaskEnvelope (inputs), ResultEnvelope (outputs), Artifacts, and Provenance tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import hashlib
import json


class PrivacyLevel(Enum):
    """Privacy constraint levels for task execution."""
    INTERNAL = "internal"  # No code/data leaves local system
    EXTERNAL = "external"  # Can use external APIs/cloud services


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    BUDGET_EXCEEDED = "budget_exceeded"
    DEGRADED = "degraded"  # Completed with reduced quality due to constraints


class ArtifactType(Enum):
    """Types of artifacts produced by tasks."""
    PATCH = "patch"  # Git patch/diff
    CSV = "csv"  # Tabular data
    JSON = "json"  # Structured data
    IMAGE = "image"  # Generated images
    TEXT = "text"  # Plain text
    HTML = "html"  # HTML document
    PDF = "pdf"  # PDF document
    URL = "url"  # External URL reference
    FILE = "file"  # Generic file


@dataclass
class Provenance:
    """Tracks the origin and history of a result."""
    tool: str  # Tool name
    version: str  # Tool version
    args: Dict[str, Any]  # Arguments used
    env: Dict[str, str]  # Environment variables (sanitized)
    started_at: datetime
    completed_at: Optional[datetime] = None
    parent_task_id: Optional[str] = None  # For chained tasks

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "tool": self.tool,
            "version": self.version,
            "args": self.args,
            "env": self.env,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "parent_task_id": self.parent_task_id,
        }


@dataclass
class Artifact:
    """Represents an output artifact from a task."""
    type: ArtifactType
    content: Optional[str] = None  # For small artifacts stored inline
    path: Optional[str] = None  # For artifacts stored on disk
    url: Optional[str] = None  # For remote artifacts
    metadata: Dict[str, Any] = field(default_factory=dict)
    size_bytes: Optional[int] = None
    checksum: Optional[str] = None  # SHA256 checksum
    max_inline_size: int = 1024 * 1024  # 1MB default max for inline content

    def compute_checksum(self) -> str:
        """Compute SHA256 checksum of content."""
        if self.content:
            return hashlib.sha256(self.content.encode()).hexdigest()
        elif self.path:
            import pathlib
            return hashlib.sha256(pathlib.Path(self.path).read_bytes()).hexdigest()
        return ""

    def get_content(self) -> Optional[str]:
        """Get content, loading from path if necessary and within limits."""
        if self.content is not None:
            return self.content
        elif self.path:
            import pathlib
            path = pathlib.Path(self.path)
            if self.size_bytes and self.size_bytes > self.max_inline_size:
                # File is too large to load into memory
                return None
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        # For serialization, only include content if it's reasonably sized
        content_to_serialize = self.content
        if self.path and self.size_bytes and self.size_bytes > self.max_inline_size:
            content_to_serialize = None  # Don't serialize large inline content

        return {
            "type": self.type.value,
            "content": content_to_serialize,
            "path": self.path,
            "url": self.url,
            "metadata": self.metadata,
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
        }


@dataclass
class Diagnostics:
    """Performance and cost diagnostics for a task."""
    latency_ms: float
    tokens_input: Optional[int] = None
    tokens_output: Optional[int] = None
    cost_usd: float = 0.0
    provider: Optional[str] = None
    model: Optional[str] = None
    retries: int = 0
    cache_hit: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "latency_ms": self.latency_ms,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "cost_usd": self.cost_usd,
            "provider": self.provider,
            "model": self.model,
            "retries": self.retries,
            "cache_hit": self.cache_hit,
        }


@dataclass
class TaskConstraints:
    """Constraints and limits for task execution."""
    privacy: PrivacyLevel = PrivacyLevel.EXTERNAL
    deadline_ms: Optional[int] = None  # Deadline in milliseconds
    budget_usd: Optional[float] = None  # Maximum cost in USD
    max_retries: int = 3
    priority: int = 1  # 0=P0 (highest), 1=P1, 2=P2
    require_validation: bool = True
    allow_degraded: bool = True  # Allow quality degradation to meet constraints

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "privacy": self.privacy.value,
            "deadline_ms": self.deadline_ms,
            "budget_usd": self.budget_usd,
            "max_retries": self.max_retries,
            "priority": self.priority,
            "require_validation": self.require_validation,
            "allow_degraded": self.allow_degraded,
        }


@dataclass
class TaskEnvelope:
    """
    Input envelope for a task.

    Defines what needs to be done, the inputs, and constraints.
    """
    id: str  # Unique task ID
    intent: str  # High-level description of what to do
    inputs: Dict[str, Any]  # Input data (repo, files, brief, etc.)
    constraints: TaskConstraints = field(default_factory=TaskConstraints)
    policy: Dict[str, Any] = field(default_factory=dict)  # Additional policy rules
    metadata: Dict[str, Any] = field(default_factory=dict)  # User metadata
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "intent": self.intent,
            "inputs": self.inputs,
            "constraints": self.constraints.to_dict(),
            "policy": self.policy,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    def hash_inputs(self) -> str:
        """Compute hash of inputs for idempotency checking."""
        input_str = json.dumps(self.inputs, sort_keys=True)
        return hashlib.sha256(f"{self.intent}:{input_str}".encode()).hexdigest()


@dataclass
class ResultEnvelope:
    """
    Output envelope for a task result.

    Contains status, artifacts, diagnostics, and provenance.
    """
    task_id: str  # Reference to original task
    status: TaskStatus
    artifacts: List[Artifact] = field(default_factory=list)
    diagnostics: Optional[Diagnostics] = None
    provenance: Optional[Provenance] = None
    error: Optional[str] = None  # Error message if failed
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)  # Result metadata (vote winner, etc.)
    completed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "diagnostics": self.diagnostics.to_dict() if self.diagnostics else None,
            "provenance": self.provenance.to_dict() if self.provenance else None,
            "error": self.error,
            "warnings": self.warnings,
            "metadata": self.metadata,
            "completed_at": self.completed_at.isoformat(),
        }

    def is_success(self) -> bool:
        """Check if task completed successfully."""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.DEGRADED]

    def total_cost(self) -> float:
        """Get total cost in USD."""
        return self.diagnostics.cost_usd if self.diagnostics else 0.0

    def total_latency(self) -> float:
        """Get total latency in milliseconds."""
        return self.diagnostics.latency_ms if self.diagnostics else 0.0


@dataclass
class PlanNode:
    """A node in the execution plan DAG."""
    id: str
    task: TaskEnvelope
    dependencies: List[str] = field(default_factory=list)  # IDs of tasks that must complete first
    tool: Optional[str] = None  # Tool to use (filled by planner)
    strategy: str = "single"  # single, cascade, vote, etc.
    alternatives: List[str] = field(default_factory=list)  # Alternative tools for fallback

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "task": self.task.to_dict(),
            "dependencies": self.dependencies,
            "tool": self.tool,
            "strategy": self.strategy,
            "alternatives": self.alternatives,
        }


@dataclass
class ExecutionPlan:
    """Complete execution plan (DAG) for a workflow."""
    id: str
    nodes: List[PlanNode]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "nodes": [n.to_dict() for n in self.nodes],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    def get_ready_nodes(self, completed: set) -> List[PlanNode]:
        """Get nodes ready to execute (all dependencies completed)."""
        ready = []
        for node in self.nodes:
            if node.id not in completed:
                if all(dep in completed for dep in node.dependencies):
                    ready.append(node)
        return ready
