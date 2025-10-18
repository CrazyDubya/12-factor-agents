"""Test helpers for Conductor unit tests."""

from __future__ import annotations

from typing import Callable, Iterable, Optional

from conductor.adapters.base import BaseAdapter, ToolCapability
from conductor.envelopes import ResultEnvelope, TaskEnvelope


def make_capability(
    name: str = "dummy",
    *,
    intents: Iterable[str] = ("dummy",),
    version: str = "0.0.1",
    input_modes: Optional[Iterable[str]] = None,
    output_modes: Optional[Iterable[str]] = None,
    **overrides,
) -> ToolCapability:
    """Create a ToolCapability tailored for tests."""
    capability = ToolCapability(
        name=name,
        version=version,
        intents=list(intents),
        input_modes=list(input_modes or ["cli"]),
        output_modes=list(output_modes or ["stdout"]),
        **overrides,
    )
    return capability


class DummyAdapter(BaseAdapter):
    """Simple adapter implementation for tests."""

    def __init__(
        self,
        capability: ToolCapability,
        *,
        result_factory: Optional[Callable[[TaskEnvelope], ResultEnvelope]] = None,
        fixed_result: Optional[ResultEnvelope] = None,
        latency_ms: float = 1000.0,
        estimated_cost: float = 0.0,
        execute_raises: Optional[Exception] = None,
    ):
        super().__init__(capability)
        self._result_factory = result_factory
        self._fixed_result = fixed_result
        self._latency_ms = latency_ms
        self._estimated_cost = estimated_cost
        self._execute_raises = execute_raises

    async def execute(self, task: TaskEnvelope) -> ResultEnvelope:
        """Return configured result or raise configured exception."""
        is_valid, error = self.validate_task(task)
        if not is_valid:
            raise ValueError(error)

        if self._execute_raises:
            raise self._execute_raises

        if self._result_factory:
            return self._result_factory(task)

        if self._fixed_result is None:
            raise RuntimeError("DummyAdapter requires a result or factory")

        return self._fixed_result

    def estimate_latency(self, task: TaskEnvelope) -> float:
        return self._latency_ms

    def estimate_cost(self, task: TaskEnvelope) -> float:
        return self._estimated_cost
