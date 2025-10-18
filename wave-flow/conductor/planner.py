"""
Router and planner for task-to-tool mapping.

Implements:
- Rule-based routing (privacy, modality, env, context)
- Scoring algorithm for tool selection
- Plan generation (single, cascade, vote, DAG)
- Hedging strategies
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set
from enum import Enum
import math

from conductor.envelopes import (
    TaskEnvelope,
    ExecutionPlan,
    PlanNode,
    PrivacyLevel,
)
from conductor.adapters.base import BaseAdapter, ExecutionEnvironment


class PlanStrategy(Enum):
    """Plan execution strategies."""
    SINGLE = "single"  # Single tool execution
    CASCADE = "cascade"  # Try cheap tool first, then fallback to strong
    PARALLEL_VOTE = "vote"  # Run multiple tools, vote on best result
    DAG = "dag"  # Complex multi-step toolchain


@dataclass
class ScoredTool:
    """A tool with its routing score."""
    adapter: BaseAdapter
    score: float
    reasons: List[str]  # Why this score was assigned


class Router:
    """
    Routes tasks to appropriate tools based on rules and scoring.

    Rule-based filtering ensures hard constraints (privacy, environment).
    Scoring ranks remaining candidates.
    """

    def __init__(
        self,
        adapters: List[BaseAdapter],
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize router.

        Args:
            adapters: Available tool adapters
            config: Router configuration (weights, thresholds)
        """
        self.adapters = adapters
        self.config = config or {}

        # Scoring weights (can be configured)
        self.weight_capability = self.config.get("weight_capability", 0.4)
        self.weight_latency = self.config.get("weight_latency", 0.2)
        self.weight_quality = self.config.get("weight_quality", 0.2)
        self.weight_health = self.config.get("weight_health", 0.1)
        self.weight_cost = self.config.get("weight_cost", 0.05)
        self.weight_queue = self.config.get("weight_queue", 0.05)

        # Thresholds
        self.p95_latency_threshold = self.config.get("p95_threshold_ms", 10000)  # 10s
        self.hedge_threshold = self.config.get("hedge_threshold", 0.8)  # Hedge if top score < 0.8

    def route(self, task: TaskEnvelope) -> List[ScoredTool]:
        """
        Route task to appropriate tools.

        Returns list of scored tools, sorted by score (highest first).
        """
        # Step 1: Rule-based filtering
        candidates = self._filter_by_rules(task)

        if not candidates:
            return []

        # Step 2: Score remaining candidates
        scored = []
        for adapter in candidates:
            score, reasons = self._score_adapter(adapter, task)
            scored.append(ScoredTool(adapter=adapter, score=score, reasons=reasons))

        # Sort by score descending
        scored.sort(key=lambda x: x.score, reverse=True)

        return scored

    def _filter_by_rules(self, task: TaskEnvelope) -> List[BaseAdapter]:
        """
        Apply hard constraints to filter adapters.

        Rules:
        1. Privacy level compatibility
        2. Execution environment availability
        3. Intent matching
        4. Context size limits
        """
        candidates = []

        for adapter in self.adapters:
            # Rule 1: Privacy compatibility
            if not adapter.capability.supports_privacy_level(task.constraints.privacy):
                continue

            # Rule 2: Check if can handle intent
            if not adapter.capability.can_handle_intent(task.intent):
                continue

            # Rule 3: Environment compatibility (would need runtime detection)
            # For now, assume all environments available

            # Rule 4: Context size limits
            # Estimate task input size and check against limits
            input_size = self._estimate_input_size(task)
            if adapter.capability.context_limit and input_size > adapter.capability.context_limit:
                continue

            candidates.append(adapter)

        return candidates

    def _score_adapter(self, adapter: BaseAdapter, task: TaskEnvelope) -> tuple[float, List[str]]:
        """
        Score an adapter for a task.

        Scoring formula:
        score = α * cap_fit + β * latency + γ * quality + δ * health - ε * cost - ζ * queue

        Returns: (score, reasons)
        """
        reasons = []
        scores = {}

        # α: Capability fit (how well intents match)
        cap_fit = self._score_capability_fit(adapter, task)
        scores["capability"] = cap_fit * self.weight_capability
        reasons.append(f"capability_fit={cap_fit:.2f}")

        # β: Latency (inverse - lower is better)
        estimated_latency = adapter.estimate_latency(task)
        latency_score = 1.0 / (1.0 + estimated_latency / 1000.0)  # Normalize to 0-1
        scores["latency"] = latency_score * self.weight_latency
        reasons.append(f"latency={estimated_latency:.0f}ms")

        # γ: Quality prior (from historical data or config)
        quality = self._get_quality_prior(adapter)
        scores["quality"] = quality * self.weight_quality
        reasons.append(f"quality={quality:.2f}")

        # δ: Health status
        health = 1.0  # Assume healthy for now, would check adapter._health_status
        scores["health"] = health * self.weight_health
        reasons.append(f"health={health:.2f}")

        # ε: Cost (inverse - lower is better)
        estimated_cost = adapter.estimate_cost(task)
        cost_penalty = min(estimated_cost / 1.0, 1.0)  # Cap at 1.0 for $1+
        scores["cost"] = (1.0 - cost_penalty) * self.weight_cost
        reasons.append(f"cost=${estimated_cost:.4f}")

        # ζ: Queue depth (assume 0 for now)
        queue_depth = 0
        queue_penalty = min(queue_depth / 10.0, 1.0)
        scores["queue"] = (1.0 - queue_penalty) * self.weight_queue
        reasons.append(f"queue={queue_depth}")

        # Total score
        total = sum(scores.values())

        return total, reasons

    def _score_capability_fit(self, adapter: BaseAdapter, task: TaskEnvelope) -> float:
        """
        Score how well adapter's capabilities match task intent.

        Simple string matching for now - could use embeddings.
        """
        intent_lower = task.intent.lower()
        matches = 0
        total = len(adapter.capability.intents)

        for cap_intent in adapter.capability.intents:
            if cap_intent.lower() in intent_lower or intent_lower in cap_intent.lower():
                matches += 1

        if total == 0:
            return 0.0

        # Boost score if at least one match
        return min(matches / total + 0.5, 1.0) if matches > 0 else 0.3

    def _get_quality_prior(self, adapter: BaseAdapter) -> float:
        """
        Get quality prior for adapter from historical data.

        For now, return defaults based on tool type.
        """
        # Would query metrics database for success rates
        defaults = {
            "claude": 0.95,
            "gpt-4": 0.92,
            "gpt-3.5": 0.85,
            "ollama": 0.75,
        }

        name_lower = adapter.get_name().lower()
        for key, quality in defaults.items():
            if key in name_lower:
                return quality

        return 0.8  # Default

    def _estimate_input_size(self, task: TaskEnvelope) -> int:
        """
        Estimate input size in tokens/characters.

        Rough approximation - 4 chars = 1 token.
        """
        total_chars = len(task.intent)
        for value in task.inputs.values():
            total_chars += len(str(value))

        return total_chars // 4  # Token estimate


class Planner:
    """
    Creates execution plans from tasks and routed tools.

    Determines execution strategy (single, cascade, vote, DAG).
    """

    def __init__(self, router: Router, config: Optional[Dict[str, Any]] = None):
        """
        Initialize planner.

        Args:
            router: Router instance for tool selection
            config: Planner configuration
        """
        self.router = router
        self.config = config or {}

        # Strategy thresholds
        self.cascade_threshold = self.config.get("cascade_threshold", 0.7)
        self.vote_threshold = self.config.get("vote_threshold", 0.85)
        self.hedge_on_p95 = self.config.get("hedge_on_p95", True)

    def plan(self, task: TaskEnvelope) -> Optional[ExecutionPlan]:
        """
        Create execution plan for task.

        Returns ExecutionPlan with selected strategy.
        """
        # Route to find suitable tools
        scored_tools = self.router.route(task)

        if not scored_tools:
            return None

        # Determine strategy based on scores and task requirements
        strategy = self._determine_strategy(task, scored_tools)

        # Build plan
        nodes = self._build_plan_nodes(task, scored_tools, strategy)

        return ExecutionPlan(
            id=f"plan_{task.id}",
            nodes=nodes,
            metadata={
                "strategy": strategy.value,
                "tool_count": len(nodes),
                "top_score": scored_tools[0].score if scored_tools else 0.0,
            },
        )

    def _determine_strategy(
        self, task: TaskEnvelope, scored_tools: List[ScoredTool]
    ) -> PlanStrategy:
        """
        Determine execution strategy based on scores and requirements.

        Logic:
        - SINGLE: High confidence in top tool
        - CASCADE: Medium confidence, have fallback
        - PARALLEL_VOTE: Low confidence, need consensus
        - DAG: Complex multi-step task (not implemented yet)
        """
        if not scored_tools:
            return PlanStrategy.SINGLE

        top_score = scored_tools[0].score

        # Check for multi-step intent (contains "then", "after", etc.)
        if any(keyword in task.intent.lower() for keyword in ["then", "after", "next", "→"]):
            # Would parse and build DAG - for now fallback to single
            pass

        # High confidence - use single tool
        if top_score >= self.vote_threshold:
            return PlanStrategy.SINGLE

        # Medium confidence - try cascade if we have alternatives
        if top_score >= self.cascade_threshold and len(scored_tools) >= 2:
            return PlanStrategy.CASCADE

        # Low confidence - use voting if we have multiple tools
        if len(scored_tools) >= 2:
            return PlanStrategy.PARALLEL_VOTE

        # Default to single
        return PlanStrategy.SINGLE

    def _build_plan_nodes(
        self,
        task: TaskEnvelope,
        scored_tools: List[ScoredTool],
        strategy: PlanStrategy,
    ) -> List[PlanNode]:
        """Build plan nodes based on strategy."""
        nodes = []

        if strategy == PlanStrategy.SINGLE:
            # Use top tool
            nodes.append(
                PlanNode(
                    id=f"{task.id}_0",
                    task=task,
                    tool=scored_tools[0].adapter.get_name(),
                    strategy="single",
                    alternatives=[],
                )
            )

        elif strategy == PlanStrategy.CASCADE:
            # Try cheap tool first, then expensive
            for i, scored in enumerate(scored_tools[:2]):
                nodes.append(
                    PlanNode(
                        id=f"{task.id}_{i}",
                        task=task,
                        tool=scored.adapter.get_name(),
                        strategy="cascade",
                        alternatives=[t.adapter.get_name() for t in scored_tools[i+1:i+2]],
                        dependencies=[nodes[-1].id] if i > 0 else [],
                    )
                )

        elif strategy == PlanStrategy.PARALLEL_VOTE:
            # Run top 2-3 tools in parallel
            for i, scored in enumerate(scored_tools[:3]):
                nodes.append(
                    PlanNode(
                        id=f"{task.id}_{i}",
                        task=task,
                        tool=scored.adapter.get_name(),
                        strategy="vote",
                        alternatives=[],
                    )
                )

        else:  # DAG
            # Would parse multi-step intent and build DAG
            # For now, fallback to single
            nodes.append(
                PlanNode(
                    id=f"{task.id}_0",
                    task=task,
                    tool=scored_tools[0].adapter.get_name(),
                    strategy="single",
                    alternatives=[],
                )
            )

        return nodes
