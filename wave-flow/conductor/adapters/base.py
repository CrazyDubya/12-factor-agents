"""
Base adapter interface for tool integrations.

All tool adapters inherit from BaseAdapter and implement execute().
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum

from conductor.envelopes import TaskEnvelope, ResultEnvelope, PrivacyLevel


class ExecutionEnvironment(Enum):
    """Where the tool can execute."""
    LOCAL = "local"  # Local machine
    VPS = "vps"  # Remote VPS/server
    CLOUD = "cloud"  # Cloud API
    GPU = "gpu"  # GPU-enabled machine


@dataclass
class ToolCapability:
    """
    Describes what a tool can do.

    Auto-introspected from tool or loaded from YAML.
    """
    name: str
    version: str
    intents: List[str]  # What intents this tool can handle
    input_modes: List[str]  # stdin, files, args, api
    output_modes: List[str]  # stdout, files, json, stream
    context_limit: Optional[int] = None  # Token/char limit
    token_limit: Optional[int] = None  # Specific token limit for LLMs
    rate_limit_rps: Optional[float] = None  # Requests per second
    rate_limit_burst: Optional[int] = None  # Burst capacity
    environments: List[ExecutionEnvironment] = None  # Where it can run
    cost_per_call: Optional[float] = None  # Approximate cost in USD
    requires_auth: bool = False
    privacy_compatible: List[PrivacyLevel] = None  # Which privacy levels it supports
    health_endpoint: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.environments is None:
            self.environments = [ExecutionEnvironment.LOCAL]
        if self.privacy_compatible is None:
            self.privacy_compatible = [PrivacyLevel.INTERNAL, PrivacyLevel.EXTERNAL]
        if self.metadata is None:
            self.metadata = {}

    def can_handle_intent(self, intent: str) -> bool:
        """Check if this tool can handle the given intent."""
        # Simple substring matching for now, could be more sophisticated
        return any(i.lower() in intent.lower() for i in self.intents)

    def supports_privacy_level(self, level: PrivacyLevel) -> bool:
        """Check if tool supports given privacy level."""
        return level in self.privacy_compatible

    def supports_environment(self, env: ExecutionEnvironment) -> bool:
        """Check if tool can run in given environment."""
        return env in self.environments


class BaseAdapter(ABC):
    """
    Abstract base class for all tool adapters.

    Adapters are black-box wrappers around tools (CLI, API, IDE agents, etc.)
    """

    def __init__(self, capability: ToolCapability, config: Optional[Dict[str, Any]] = None):
        """
        Initialize adapter.

        Args:
            capability: Tool capability description
            config: Optional configuration (API keys, endpoints, etc.)
        """
        self.capability = capability
        self.config = config or {}
        self._health_status = "unknown"
        self._last_health_check = None

    @abstractmethod
    async def execute(self, task: TaskEnvelope) -> ResultEnvelope:
        """
        Execute a task using this tool.

        Args:
            task: Task envelope with inputs and constraints

        Returns:
            Result envelope with outputs and diagnostics
        """
        pass

    async def health_check(self) -> bool:
        """
        Check if tool is healthy and available.

        Returns:
            True if healthy, False otherwise
        """
        # Default implementation - subclasses can override
        return True

    def estimate_cost(self, task: TaskEnvelope) -> float:
        """
        Estimate cost in USD for executing this task.

        Args:
            task: Task to estimate

        Returns:
            Estimated cost in USD
        """
        # Default implementation - subclasses can override
        if self.capability.cost_per_call:
            return self.capability.cost_per_call
        return 0.0

    def estimate_latency(self, task: TaskEnvelope) -> float:
        """
        Estimate latency in milliseconds for executing this task.

        Args:
            task: Task to estimate

        Returns:
            Estimated latency in milliseconds
        """
        # Default implementation - subclasses can override with historical data
        return 1000.0  # 1 second default

    def validate_task(self, task: TaskEnvelope) -> tuple[bool, Optional[str]]:
        """
        Validate that this adapter can handle the given task.

        Args:
            task: Task to validate

        Returns:
            (is_valid, error_message)
        """
        # Check privacy compatibility
        if not self.capability.supports_privacy_level(task.constraints.privacy):
            return False, f"Tool {self.capability.name} not compatible with privacy level {task.constraints.privacy.value}"

        # Check intent match
        if not self.capability.can_handle_intent(task.intent):
            return False, f"Tool {self.capability.name} cannot handle intent: {task.intent}"

        return True, None

    def get_capability(self) -> ToolCapability:
        """Get tool capability description."""
        return self.capability

    def get_name(self) -> str:
        """Get tool name."""
        return self.capability.name

    def get_version(self) -> str:
        """Get tool version."""
        return self.capability.version

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.capability.name}@{self.capability.version})>"
