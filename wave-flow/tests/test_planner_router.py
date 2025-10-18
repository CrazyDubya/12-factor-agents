from __future__ import annotations

from conductor.envelopes import PrivacyLevel, TaskConstraints, TaskEnvelope
from conductor.planner import Planner, PlanStrategy, Router, ScoredTool
from tests.utils import DummyAdapter, make_capability


def make_task(intent: str = "dummy task", privacy: PrivacyLevel = PrivacyLevel.EXTERNAL) -> TaskEnvelope:
    return TaskEnvelope(id="task-123", intent=intent, inputs={}, constraints=TaskConstraints(privacy=privacy))


def test_router_filters_by_privacy_level() -> None:
    internal_cap = make_capability(
        name="internal",
        intents=["dummy"],
        privacy_compatible=[PrivacyLevel.INTERNAL],
    )
    external_cap = make_capability(
        name="external",
        intents=["dummy"],
        privacy_compatible=[PrivacyLevel.EXTERNAL],
    )
    router = Router([
        DummyAdapter(internal_cap),
        DummyAdapter(external_cap),
    ])

    task = make_task(privacy=PrivacyLevel.EXTERNAL)
    filtered = router._filter_by_rules(task)
    assert len(filtered) == 1
    assert filtered[0].capability.name == "external"


def test_router_filters_by_context_limit_when_input_too_large() -> None:
    tight_cap = make_capability(
        name="tight",
        intents=["long"],
        context_limit=1,
    )
    roomy_cap = make_capability(name="roomy", intents=["long"], context_limit=10_000)
    router = Router([
        DummyAdapter(tight_cap),
        DummyAdapter(roomy_cap),
    ])

    task = make_task(intent="long analysis with many characters" * 10)
    filtered = router._filter_by_rules(task)
    assert len(filtered) == 1
    assert filtered[0].capability.name == "roomy"


def test_router_ranks_tools_by_score_preferring_lower_latency() -> None:
    fast_cap = make_capability(name="fast", intents=["analyze"])
    slow_cap = make_capability(name="slow", intents=["analyze"])
    router = Router([
        DummyAdapter(fast_cap, latency_ms=100.0),
        DummyAdapter(slow_cap, latency_ms=5000.0),
    ])

    task = make_task(intent="analyze data")
    scored = router.route(task)
    assert len(scored) == 2
    assert scored[0].adapter.capability.name == "fast"
    assert scored[0].score >= scored[1].score


class FakeRouter:
    def __init__(self, scored_tools):
        self._scored = scored_tools

    def route(self, task):
        return self._scored


def test_planner_selects_single_strategy_for_high_confidence() -> None:
    cap = make_capability(name="primary", intents=["dummy"])
    scored_tools = [ScoredTool(adapter=DummyAdapter(cap), score=0.9, reasons=["high confidence"])]
    planner = Planner(FakeRouter(scored_tools))

    plan = planner.plan(make_task())
    assert plan is not None
    assert plan.metadata["strategy"] == PlanStrategy.SINGLE.value
    assert len(plan.nodes) == 1
    assert plan.nodes[0].tool == "primary"


def test_planner_builds_cascade_when_scores_medium_with_alternative() -> None:
    primary = DummyAdapter(make_capability(name="cheap", intents=["dummy"]))
    backup = DummyAdapter(make_capability(name="strong", intents=["dummy"]))
    scored = [
        ScoredTool(adapter=primary, score=0.75, reasons=["medium confidence"]),
        ScoredTool(adapter=backup, score=0.6, reasons=["fallback"]),
    ]
    planner = Planner(FakeRouter(scored))

    plan = planner.plan(make_task())
    assert plan is not None
    assert plan.metadata["strategy"] == PlanStrategy.CASCADE.value
    assert len(plan.nodes) == 2
    assert plan.nodes[1].dependencies == [plan.nodes[0].id]


def test_planner_uses_parallel_vote_when_confidence_low() -> None:
    a1 = DummyAdapter(make_capability(name="a1", intents=["dummy"]))
    a2 = DummyAdapter(make_capability(name="a2", intents=["dummy"]))
    scored = [
        ScoredTool(adapter=a1, score=0.5, reasons=["low confidence"]),
        ScoredTool(adapter=a2, score=0.4, reasons=["backup"]),
    ]
    planner = Planner(FakeRouter(scored))

    plan = planner.plan(make_task())
    assert plan is not None
    assert plan.metadata["strategy"] == PlanStrategy.PARALLEL_VOTE.value
    assert {node.tool for node in plan.nodes} == {"a1", "a2"}


def test_planner_returns_none_when_no_tools_available() -> None:
    planner = Planner(FakeRouter([]))
    assert planner.plan(make_task()) is None
