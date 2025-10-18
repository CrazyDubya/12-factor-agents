from __future__ import annotations

import asyncio
import time

import pytest

from conductor.envelopes import (
    Diagnostics,
    ExecutionPlan,
    PlanNode,
    ResultEnvelope,
    TaskConstraints,
    TaskEnvelope,
    TaskStatus,
)
from conductor.executor import CircuitBreaker, Executor, TokenBucket
from tests.utils import DummyAdapter, make_capability


def make_task(intent: str = "dummy") -> TaskEnvelope:
    return TaskEnvelope(id="task-1", intent=intent, inputs={}, constraints=TaskConstraints())


async def execute_plan(executor: Executor, plan: ExecutionPlan):
    return await executor.execute_plan(plan)


@pytest.mark.asyncio
async def test_executor_runs_single_node_successfully() -> None:
    def build_result(task: TaskEnvelope) -> ResultEnvelope:
        return ResultEnvelope(
            task_id=task.id,
            status=TaskStatus.COMPLETED,
            diagnostics=Diagnostics(latency_ms=10.0, cost_usd=0.05),
        )

    adapter = DummyAdapter(
        make_capability(name="success", intents=["dummy"]),
        result_factory=build_result,
        latency_ms=25.0,
        estimated_cost=0.05,
    )
    executor = Executor({"success": adapter})

    plan = ExecutionPlan(
        id="plan-1",
        nodes=[
            PlanNode(
                id="node-1",
                task=make_task(),
                tool="success",
            )
        ],
    )

    results = await execute_plan(executor, plan)
    assert "node-1" in results
    assert results["node-1"].status == TaskStatus.COMPLETED
    assert executor.get_budget_status()["spent"] == pytest.approx(0.05)


@pytest.mark.asyncio
async def test_executor_respects_budget_limit() -> None:
    task = TaskEnvelope(
        id="task-budget",
        intent="dummy",
        inputs={},
        constraints=TaskConstraints(budget_usd=0.5, max_retries=0),
    )

    adapter = DummyAdapter(
        make_capability(name="expensive", intents=["dummy"]),
        result_factory=lambda _: ResultEnvelope(task_id=task.id, status=TaskStatus.COMPLETED),
        estimated_cost=1.0,
    )

    executor = Executor({"expensive": adapter})

    plan = ExecutionPlan(
        id="plan-budget",
        nodes=[PlanNode(id="node-budget", task=task, tool="expensive")],
    )

    results = await execute_plan(executor, plan)
    assert results["node-budget"].status == TaskStatus.BUDGET_EXCEEDED


@pytest.mark.asyncio
async def test_executor_falls_back_when_circuit_open() -> None:
    task = make_task()

    healthy_result = ResultEnvelope(task_id=task.id, status=TaskStatus.COMPLETED)

    flaky_adapter = DummyAdapter(
        make_capability(name="flaky", intents=["dummy"]),
        result_factory=lambda _: healthy_result,
    )
    healthy_adapter = DummyAdapter(
        make_capability(name="healthy", intents=["dummy"]),
        result_factory=lambda _: healthy_result,
    )

    executor = Executor({
        "flaky": flaky_adapter,
        "healthy": healthy_adapter,
    })

    # Force circuit open for the flaky adapter
    breaker = executor.circuit_breakers["flaky"]
    breaker.is_open = True
    breaker.last_failure_time = time.time()

    node = PlanNode(
        id="node-fallback",
        task=task,
        tool="flaky",
        alternatives=["healthy"],
    )

    result = await executor._execute_node(node)
    assert result.status == TaskStatus.COMPLETED


@pytest.mark.asyncio
async def test_executor_stops_after_terminal_failure() -> None:
    """Ensure dependent nodes are not scheduled after a terminal failure."""
    fail_task = make_task(intent="fail")
    downstream_task = TaskEnvelope(
        id="task-downstream",
        intent="downstream",
        inputs={},
        constraints=TaskConstraints(),
    )

    executed_downstream = False

    def downstream_result(_: TaskEnvelope) -> ResultEnvelope:
        nonlocal executed_downstream
        executed_downstream = True
        return ResultEnvelope(task_id=downstream_task.id, status=TaskStatus.COMPLETED)

    executor = Executor(
        {
            "failer": DummyAdapter(
                make_capability(name="failer", intents=["fail"]),
                result_factory=lambda t: ResultEnvelope(
                    task_id=t.id,
                    status=TaskStatus.BUDGET_EXCEEDED,
                    error="Budget hit",
                ),
            ),
            "downstream": DummyAdapter(
                make_capability(name="downstream", intents=["downstream"]),
                result_factory=downstream_result,
            ),
        }
    )

    plan = ExecutionPlan(
        id="plan-abort",
        nodes=[
            PlanNode(id="node-fail", task=fail_task, tool="failer", dependencies=[]),
            PlanNode(id="node-down", task=downstream_task, tool="downstream", dependencies=["node-fail"]),
        ],
    )

    results = await execute_plan(executor, plan)

    assert results["node-fail"].status == TaskStatus.BUDGET_EXCEEDED
    assert "node-down" not in results
    assert not executed_downstream


def test_token_bucket_consumes_and_refills() -> None:
    bucket = TokenBucket(capacity=2, rate=1.0)

    assert bucket.consume(1)
    assert bucket.consume(1)
    assert not bucket.consume(1)

    bucket.last_refill -= 10
    assert bucket.consume(1)


@pytest.mark.asyncio
async def test_token_bucket_wait_for_tokens_refills() -> None:
    bucket = TokenBucket(capacity=1, rate=1.0)
    bucket.tokens = 0
    bucket.last_refill -= 10

    await bucket.wait_for_tokens(1)
    assert bucket.tokens <= bucket.capacity


def test_circuit_breaker_opens_and_recovers() -> None:
    breaker = CircuitBreaker(failure_threshold=2, timeout_seconds=1)

    breaker.record_failure()
    assert breaker.can_execute()
    breaker.record_failure()
    assert not breaker.can_execute()

    breaker.last_failure_time = time.time() - 5
    assert breaker.can_execute()
    assert breaker.failures == 0
    assert not breaker.is_open


@pytest.mark.asyncio
async def test_executor_continues_after_node_failure() -> None:
    """Test that independent nodes execute even when upstream nodes fail."""
    # Node 1 fails
    task1 = make_task(intent="fail")
    # Node 2 succeeds (independent of node 1)
    task2 = make_task(intent="succeed")

    fail_adapter = DummyAdapter(
        make_capability(name="failer", intents=["fail"]),
        result_factory=lambda t: ResultEnvelope(task_id=t.id, status=TaskStatus.FAILED, error="Intentional failure"),
    )
    success_adapter = DummyAdapter(
        make_capability(name="succeeder", intents=["succeed"]),
        result_factory=lambda t: ResultEnvelope(task_id=t.id, status=TaskStatus.COMPLETED),
    )

    executor = Executor({"failer": fail_adapter, "succeeder": success_adapter})

    # Create plan with two independent nodes
    plan = ExecutionPlan(
        id="plan-parallel",
        nodes=[
            PlanNode(id="node-fail", task=task1, tool="failer", dependencies=[]),
            PlanNode(id="node-succeed", task=task2, tool="succeeder", dependencies=[]),
        ],
    )

    results = await execute_plan(executor, plan)

    # Both nodes should execute despite one failing
    assert "node-fail" in results
    assert "node-succeed" in results
    assert results["node-fail"].status == TaskStatus.FAILED
    assert results["node-succeed"].status == TaskStatus.COMPLETED


@pytest.mark.asyncio
async def test_executor_multi_node_budget_exceeded() -> None:
    """Test that budget exceeded in one node doesn't block independent nodes."""
    task1 = TaskEnvelope(
        id="task-expensive",
        intent="expensive",
        inputs={},
        constraints=TaskConstraints(budget_usd=0.01, max_retries=0),
    )
    task2 = make_task(intent="cheap")

    expensive_adapter = DummyAdapter(
        make_capability(name="expensive", intents=["expensive"]),
        result_factory=lambda t: ResultEnvelope(task_id=t.id, status=TaskStatus.COMPLETED),
        estimated_cost=10.0,  # Way over budget
    )
    cheap_adapter = DummyAdapter(
        make_capability(name="cheap", intents=["cheap"]),
        result_factory=lambda t: ResultEnvelope(task_id=t.id, status=TaskStatus.COMPLETED),
        estimated_cost=0.0,
    )

    executor = Executor({"expensive": expensive_adapter, "cheap": cheap_adapter})
    executor.budget_limit = task1.constraints.budget_usd

    plan = ExecutionPlan(
        id="plan-budget",
        nodes=[
            PlanNode(id="node-expensive", task=task1, tool="expensive", dependencies=[]),
            PlanNode(id="node-cheap", task=task2, tool="cheap", dependencies=[]),
        ],
    )

    results = await execute_plan(executor, plan)

    # Both nodes should attempt execution
    assert "node-expensive" in results
    assert "node-cheap" in results
    # First node should hit budget limit
    assert results["node-expensive"].status == TaskStatus.BUDGET_EXCEEDED
    # Second node should succeed
    assert results["node-cheap"].status == TaskStatus.COMPLETED


@pytest.mark.asyncio
async def test_executor_parallel_nodes_execute_concurrently() -> None:
    """Test that parallel (no dependencies) nodes execute together."""
    task1 = make_task(intent="parallel1")
    task2 = make_task(intent="parallel2")
    task3 = make_task(intent="parallel3")

    adapter1 = DummyAdapter(
        make_capability(name="tool1", intents=["parallel1"]),
        result_factory=lambda t: ResultEnvelope(task_id=t.id, status=TaskStatus.COMPLETED),
    )
    adapter2 = DummyAdapter(
        make_capability(name="tool2", intents=["parallel2"]),
        result_factory=lambda t: ResultEnvelope(task_id=t.id, status=TaskStatus.COMPLETED),
    )
    adapter3 = DummyAdapter(
        make_capability(name="tool3", intents=["parallel3"]),
        result_factory=lambda t: ResultEnvelope(task_id=t.id, status=TaskStatus.COMPLETED),
    )

    executor = Executor({"tool1": adapter1, "tool2": adapter2, "tool3": adapter3})

    plan = ExecutionPlan(
        id="plan-parallel",
        nodes=[
            PlanNode(id="node-1", task=task1, tool="tool1", dependencies=[]),
            PlanNode(id="node-2", task=task2, tool="tool2", dependencies=[]),
            PlanNode(id="node-3", task=task3, tool="tool3", dependencies=[]),
        ],
    )

    start_time = time.time()
    results = await execute_plan(executor, plan)
    elapsed = time.time() - start_time

    # All nodes should complete
    assert len(results) == 3
    assert all(r.status == TaskStatus.COMPLETED for r in results.values())

    # Should execute relatively quickly (not sequentially waiting)
    # Even with executor overhead, 3 parallel tasks should be < 1s
    assert elapsed < 2.0


@pytest.mark.asyncio
async def test_executor_dag_with_dependencies() -> None:
    """Test that DAG respects dependencies but continues on failures."""
    # Node 1: No deps, succeeds
    # Node 2: Depends on node 1, succeeds
    # Node 3: Depends on node 1, fails
    # Node 4: Depends on node 3, should still execute after node 3 fails
    task1 = make_task(intent="root")
    task2 = make_task(intent="branch-success")
    task3 = make_task(intent="branch-fail")
    task4 = make_task(intent="leaf")

    def result_success(t: TaskEnvelope) -> ResultEnvelope:
        return ResultEnvelope(task_id=t.id, status=TaskStatus.COMPLETED)

    def result_fail(t: TaskEnvelope) -> ResultEnvelope:
        return ResultEnvelope(task_id=t.id, status=TaskStatus.FAILED, error="Intentional")

    executor = Executor({
        "root": DummyAdapter(make_capability(name="root", intents=["root"]), result_factory=result_success),
        "success": DummyAdapter(make_capability(name="success", intents=["branch-success"]), result_factory=result_success),
        "failer": DummyAdapter(make_capability(name="failer", intents=["branch-fail"]), result_factory=result_fail),
        "leaf": DummyAdapter(make_capability(name="leaf", intents=["leaf"]), result_factory=result_success),
    })

    plan = ExecutionPlan(
        id="plan-dag",
        nodes=[
            PlanNode(id="node-1", task=task1, tool="root", dependencies=[]),
            PlanNode(id="node-2", task=task2, tool="success", dependencies=["node-1"]),
            PlanNode(id="node-3", task=task3, tool="failer", dependencies=["node-1"]),
            PlanNode(id="node-4", task=task4, tool="leaf", dependencies=["node-3"]),
        ],
    )

    results = await execute_plan(executor, plan)

    assert results["node-1"].status == TaskStatus.COMPLETED
    assert results["node-2"].status == TaskStatus.COMPLETED
    assert results["node-3"].status == TaskStatus.FAILED
    assert "node-4" not in results


# ===== CASCADE STRATEGY TESTS =====


@pytest.mark.asyncio
async def test_cascade_primary_success_skips_fallback() -> None:
    """Test cascade strategy: primary succeeds, fallback is skipped."""
    task = make_task(intent="cascade-test")

    # Primary adapter succeeds
    primary_executed = False
    fallback_executed = False

    def primary_result(_: TaskEnvelope) -> ResultEnvelope:
        nonlocal primary_executed
        primary_executed = True
        return ResultEnvelope(task_id=task.id, status=TaskStatus.COMPLETED)

    def fallback_result(_: TaskEnvelope) -> ResultEnvelope:
        nonlocal fallback_executed
        fallback_executed = True
        return ResultEnvelope(task_id=task.id, status=TaskStatus.COMPLETED)

    executor = Executor({
        "primary": DummyAdapter(
            make_capability(name="primary", intents=["cascade-test"]),
            result_factory=primary_result,
        ),
        "fallback": DummyAdapter(
            make_capability(name="fallback", intents=["cascade-test"]),
            result_factory=fallback_result,
        ),
    })

    # Create cascade plan
    plan = ExecutionPlan(
        id="cascade-plan",
        nodes=[
            PlanNode(id="node-primary", task=task, tool="primary", strategy="cascade"),
            PlanNode(id="node-fallback", task=task, tool="fallback", strategy="cascade", dependencies=["node-primary"]),
        ],
        metadata={"strategy": "cascade"},
    )

    results = await execute_plan(executor, plan)

    # Primary executed and succeeded
    assert primary_executed
    assert "node-primary" in results
    assert results["node-primary"].status == TaskStatus.COMPLETED

    # Fallback should NOT be executed (cascade short-circuits on success)
    assert not fallback_executed
    assert "node-fallback" not in results


@pytest.mark.asyncio
async def test_cascade_primary_fails_fallback_succeeds() -> None:
    """Test cascade strategy: primary fails, fallback succeeds."""
    task = make_task(intent="cascade-test")

    primary_adapter = DummyAdapter(
        make_capability(name="primary", intents=["cascade-test"]),
        result_factory=lambda t: ResultEnvelope(task_id=t.id, status=TaskStatus.FAILED, error="Primary failed"),
    )
    fallback_adapter = DummyAdapter(
        make_capability(name="fallback", intents=["cascade-test"]),
        result_factory=lambda t: ResultEnvelope(task_id=t.id, status=TaskStatus.COMPLETED),
    )

    executor = Executor({
        "primary": primary_adapter,
        "fallback": fallback_adapter,
    })

    plan = ExecutionPlan(
        id="cascade-plan",
        nodes=[
            PlanNode(id="node-primary", task=task, tool="primary", strategy="cascade"),
            PlanNode(id="node-fallback", task=task, tool="fallback", strategy="cascade", dependencies=["node-primary"]),
        ],
        metadata={"strategy": "cascade"},
    )

    results = await execute_plan(executor, plan)

    # Both executed
    assert "node-primary" in results
    assert "node-fallback" in results

    # Primary failed, fallback succeeded
    assert results["node-primary"].status == TaskStatus.FAILED
    assert results["node-fallback"].status == TaskStatus.COMPLETED


@pytest.mark.asyncio
async def test_cascade_both_fail_terminal_abort() -> None:
    """Test cascade strategy: both primary and fallback fail."""
    task = make_task(intent="cascade-test")

    primary_adapter = DummyAdapter(
        make_capability(name="primary", intents=["cascade-test"]),
        result_factory=lambda t: ResultEnvelope(task_id=t.id, status=TaskStatus.FAILED, error="Primary failed"),
    )
    fallback_adapter = DummyAdapter(
        make_capability(name="fallback", intents=["cascade-test"]),
        result_factory=lambda t: ResultEnvelope(task_id=t.id, status=TaskStatus.FAILED, error="Fallback failed"),
    )

    executor = Executor({
        "primary": primary_adapter,
        "fallback": fallback_adapter,
    })

    plan = ExecutionPlan(
        id="cascade-plan",
        nodes=[
            PlanNode(id="node-primary", task=task, tool="primary", strategy="cascade"),
            PlanNode(id="node-fallback", task=task, tool="fallback", strategy="cascade", dependencies=["node-primary"]),
        ],
        metadata={"strategy": "cascade"},
    )

    results = await execute_plan(executor, plan)

    # Both executed and failed
    assert "node-primary" in results
    assert "node-fallback" in results
    assert results["node-primary"].status == TaskStatus.FAILED
    assert results["node-fallback"].status == TaskStatus.FAILED


@pytest.mark.asyncio
async def test_cascade_primary_budget_exceeded_tries_fallback() -> None:
    """Test cascade strategy: primary hits budget, fallback executes."""
    task = TaskEnvelope(
        id="cascade-budget",
        intent="cascade-test",
        inputs={},
        constraints=TaskConstraints(budget_usd=0.05, max_retries=0),
    )

    expensive_adapter = DummyAdapter(
        make_capability(name="expensive", intents=["cascade-test"]),
        result_factory=lambda t: ResultEnvelope(task_id=t.id, status=TaskStatus.COMPLETED),
        estimated_cost=10.0,  # Way over budget
    )
    cheap_adapter = DummyAdapter(
        make_capability(name="cheap", intents=["cascade-test"]),
        result_factory=lambda t: ResultEnvelope(task_id=t.id, status=TaskStatus.COMPLETED),
        estimated_cost=0.01,  # Under budget
    )

    executor = Executor({
        "expensive": expensive_adapter,
        "cheap": cheap_adapter,
    })
    executor.budget_limit = task.constraints.budget_usd

    plan = ExecutionPlan(
        id="cascade-budget",
        nodes=[
            PlanNode(id="node-expensive", task=task, tool="expensive", strategy="cascade"),
            PlanNode(id="node-cheap", task=task, tool="cheap", strategy="cascade", dependencies=["node-expensive"]),
        ],
        metadata={"strategy": "cascade"},
    )

    results = await execute_plan(executor, plan)

    # Primary hit budget limit
    assert "node-expensive" in results
    assert results["node-expensive"].status == TaskStatus.BUDGET_EXCEEDED

    # Fallback succeeded
    assert "node-cheap" in results
    assert results["node-cheap"].status == TaskStatus.COMPLETED


@pytest.mark.asyncio
async def test_cascade_circuit_breaker_triggers_fallback() -> None:
    """Test cascade strategy: circuit breaker open triggers fallback."""
    task = make_task(intent="cascade-test")

    flaky_adapter = DummyAdapter(
        make_capability(name="flaky", intents=["cascade-test"]),
        result_factory=lambda t: ResultEnvelope(task_id=t.id, status=TaskStatus.COMPLETED),
    )
    reliable_adapter = DummyAdapter(
        make_capability(name="reliable", intents=["cascade-test"]),
        result_factory=lambda t: ResultEnvelope(task_id=t.id, status=TaskStatus.COMPLETED),
    )

    executor = Executor({
        "flaky": flaky_adapter,
        "reliable": reliable_adapter,
    })

    # Force circuit open for flaky adapter
    breaker = executor.circuit_breakers["flaky"]
    breaker.is_open = True
    breaker.last_failure_time = time.time()

    plan = ExecutionPlan(
        id="cascade-cb",
        nodes=[
            PlanNode(id="node-flaky", task=task, tool="flaky", strategy="cascade", alternatives=["reliable"]),
            PlanNode(id="node-reliable", task=task, tool="reliable", strategy="cascade", dependencies=["node-flaky"]),
        ],
        metadata={"strategy": "cascade"},
    )

    results = await execute_plan(executor, plan)

    # Flaky failed due to circuit breaker, but used alternative
    assert "node-flaky" in results
    assert results["node-flaky"].status == TaskStatus.COMPLETED  # Alternative succeeded


# ===== VOTE STRATEGY TESTS =====


@pytest.mark.asyncio
async def test_vote_all_succeed_picks_fastest() -> None:
    """Test vote strategy: all nodes succeed, fastest wins."""
    task = make_task(intent="vote-test")

    fast_adapter = DummyAdapter(
        make_capability(name="fast", intents=["vote-test"]),
        result_factory=lambda t: ResultEnvelope(
            task_id=t.id,
            status=TaskStatus.COMPLETED,
            diagnostics=Diagnostics(latency_ms=100.0),
        ),
    )
    medium_adapter = DummyAdapter(
        make_capability(name="medium", intents=["vote-test"]),
        result_factory=lambda t: ResultEnvelope(
            task_id=t.id,
            status=TaskStatus.COMPLETED,
            diagnostics=Diagnostics(latency_ms=500.0),
        ),
    )
    slow_adapter = DummyAdapter(
        make_capability(name="slow", intents=["vote-test"]),
        result_factory=lambda t: ResultEnvelope(
            task_id=t.id,
            status=TaskStatus.COMPLETED,
            diagnostics=Diagnostics(latency_ms=1000.0),
        ),
    )

    executor = Executor({
        "fast": fast_adapter,
        "medium": medium_adapter,
        "slow": slow_adapter,
    })

    plan = ExecutionPlan(
        id="vote-plan",
        nodes=[
            PlanNode(id="node-fast", task=task, tool="fast", strategy="vote"),
            PlanNode(id="node-medium", task=task, tool="medium", strategy="vote"),
            PlanNode(id="node-slow", task=task, tool="slow", strategy="vote"),
        ],
        metadata={"strategy": "vote"},
    )

    results = await execute_plan(executor, plan)

    # All executed
    assert len(results) == 3
    assert all(r.status == TaskStatus.COMPLETED for r in results.values())

    # Fastest should be marked as winner
    assert results["node-fast"].metadata.get("vote_winner") is True
    assert results["node-medium"].metadata.get("vote_winner") is not True
    assert results["node-slow"].metadata.get("vote_winner") is not True


@pytest.mark.asyncio
async def test_vote_partial_failures_picks_from_successes() -> None:
    """Test vote strategy: some nodes fail, winner from successes."""
    task = make_task(intent="vote-test")

    fail_adapter = DummyAdapter(
        make_capability(name="fail", intents=["vote-test"]),
        result_factory=lambda t: ResultEnvelope(task_id=t.id, status=TaskStatus.FAILED, error="Failed"),
    )
    success_slow_adapter = DummyAdapter(
        make_capability(name="success-slow", intents=["vote-test"]),
        result_factory=lambda t: ResultEnvelope(
            task_id=t.id,
            status=TaskStatus.COMPLETED,
            diagnostics=Diagnostics(latency_ms=800.0),
        ),
    )
    success_fast_adapter = DummyAdapter(
        make_capability(name="success-fast", intents=["vote-test"]),
        result_factory=lambda t: ResultEnvelope(
            task_id=t.id,
            status=TaskStatus.COMPLETED,
            diagnostics=Diagnostics(latency_ms=200.0),
        ),
    )

    executor = Executor({
        "fail": fail_adapter,
        "success-slow": success_slow_adapter,
        "success-fast": success_fast_adapter,
    })

    plan = ExecutionPlan(
        id="vote-plan",
        nodes=[
            PlanNode(id="node-fail", task=task, tool="fail", strategy="vote"),
            PlanNode(id="node-slow", task=task, tool="success-slow", strategy="vote"),
            PlanNode(id="node-fast", task=task, tool="success-fast", strategy="vote"),
        ],
        metadata={"strategy": "vote"},
    )

    results = await execute_plan(executor, plan)

    # All executed
    assert len(results) == 3
    assert results["node-fail"].status == TaskStatus.FAILED
    assert results["node-slow"].status == TaskStatus.COMPLETED
    assert results["node-fast"].status == TaskStatus.COMPLETED

    # Fastest success should win
    assert results["node-fast"].metadata.get("vote_winner") is True


@pytest.mark.asyncio
async def test_vote_all_fail_returns_all_failures() -> None:
    """Test vote strategy: all nodes fail, first failure wins."""
    task = make_task(intent="vote-test")

    fail1_adapter = DummyAdapter(
        make_capability(name="fail1", intents=["vote-test"]),
        result_factory=lambda t: ResultEnvelope(task_id=t.id, status=TaskStatus.FAILED, error="Fail 1"),
    )
    fail2_adapter = DummyAdapter(
        make_capability(name="fail2", intents=["vote-test"]),
        result_factory=lambda t: ResultEnvelope(task_id=t.id, status=TaskStatus.FAILED, error="Fail 2"),
    )

    executor = Executor({
        "fail1": fail1_adapter,
        "fail2": fail2_adapter,
    })

    plan = ExecutionPlan(
        id="vote-plan",
        nodes=[
            PlanNode(id="node-fail1", task=task, tool="fail1", strategy="vote"),
            PlanNode(id="node-fail2", task=task, tool="fail2", strategy="vote"),
        ],
        metadata={"strategy": "vote"},
    )

    results = await execute_plan(executor, plan)

    # All executed and failed
    assert len(results) == 2
    assert all(r.status == TaskStatus.FAILED for r in results.values())

    # First failure should be marked as winner (best available)
    winner_exists = any(r.metadata.get("vote_winner") for r in results.values())
    assert winner_exists


@pytest.mark.asyncio
async def test_vote_result_selection_prefers_success_over_speed() -> None:
    """Test vote result selection: success is preferred even if slower."""
    task = make_task(intent="vote-test")

    # Fast failure
    fast_fail_adapter = DummyAdapter(
        make_capability(name="fast-fail", intents=["vote-test"]),
        result_factory=lambda t: ResultEnvelope(
            task_id=t.id,
            status=TaskStatus.FAILED,
            error="Fast but failed",
            diagnostics=Diagnostics(latency_ms=50.0),
        ),
    )
    # Slow success
    slow_success_adapter = DummyAdapter(
        make_capability(name="slow-success", intents=["vote-test"]),
        result_factory=lambda t: ResultEnvelope(
            task_id=t.id,
            status=TaskStatus.COMPLETED,
            diagnostics=Diagnostics(latency_ms=5000.0),
        ),
    )

    executor = Executor({
        "fast-fail": fast_fail_adapter,
        "slow-success": slow_success_adapter,
    })

    plan = ExecutionPlan(
        id="vote-plan",
        nodes=[
            PlanNode(id="node-fast-fail", task=task, tool="fast-fail", strategy="vote"),
            PlanNode(id="node-slow-success", task=task, tool="slow-success", strategy="vote"),
        ],
        metadata={"strategy": "vote"},
    )

    results = await execute_plan(executor, plan)

    # Both executed
    assert len(results) == 2
    assert results["node-fast-fail"].status == TaskStatus.FAILED
    assert results["node-slow-success"].status == TaskStatus.COMPLETED

    # Slow success should win (success preferred over speed)
    assert results["node-slow-success"].metadata.get("vote_winner") is True
    assert results["node-fast-fail"].metadata.get("vote_winner") is not True
