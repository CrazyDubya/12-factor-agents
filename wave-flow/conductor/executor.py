"""
Scheduler and executor for running execution plans.

Features:
- Token bucket rate limiting
- Exponential backoff retries
- Circuit breakers
- Deadline enforcement
- Budget tracking
- Priority queues
- Idempotency
"""

import asyncio
import time
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import json

from conductor.envelopes import (
    TaskEnvelope,
    ResultEnvelope,
    ExecutionPlan,
    PlanNode,
    TaskStatus,
)
from conductor.adapters.base import BaseAdapter


@dataclass
class TokenBucket:
    """Token bucket for rate limiting."""
    capacity: int  # Maximum tokens
    rate: float  # Tokens per second refill rate
    tokens: float = field(init=False)  # Current tokens
    last_refill: float = field(init=False)  # Last refill timestamp

    def __post_init__(self):
        self.tokens = float(self.capacity)
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens. Returns True if successful."""
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_refill = now

    async def wait_for_tokens(self, tokens: int = 1):
        """Wait until tokens are available."""
        while not self.consume(tokens):
            await asyncio.sleep(0.1)


@dataclass
class CircuitBreaker:
    """Circuit breaker for adapter health management."""
    failure_threshold: int = 5  # Failures before opening
    timeout_seconds: int = 60  # How long to stay open
    failures: int = 0
    last_failure_time: Optional[float] = None
    is_open: bool = False

    def record_success(self):
        """Record successful execution."""
        self.failures = 0
        self.is_open = False

    def record_failure(self):
        """Record failed execution."""
        self.failures += 1
        self.last_failure_time = time.time()

        if self.failures >= self.failure_threshold:
            self.is_open = True

    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if not self.is_open:
            return True

        # Check if timeout has passed
        if self.last_failure_time:
            elapsed = time.time() - self.last_failure_time
            if elapsed >= self.timeout_seconds:
                # Try half-open state
                self.is_open = False
                self.failures = 0
                return True

        return False


class Executor:
    """
    Executes plans with production-grade reliability features.
    """

    def __init__(
        self,
        adapters: Dict[str, BaseAdapter],
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize executor.

        Args:
            adapters: Map of adapter names to adapter instances
            config: Executor configuration
        """
        self.adapters = adapters
        self.config = config or {}

        # Rate limiters per adapter
        self.token_buckets: Dict[str, TokenBucket] = {}
        self._init_token_buckets()

        # Circuit breakers per adapter
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        for name in adapters.keys():
            self.circuit_breakers[name] = CircuitBreaker()

        # Idempotency cache
        self.cache_dir = Path(self.config.get("cache_dir", ".conductor/cache"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for frequently accessed results (LRU with size limit)
        self._memory_cache: Dict[str, ResultEnvelope] = {}
        self._cache_access_order: List[str] = []  # Track access order for LRU
        self._max_memory_cache_size = int(self.config.get("max_memory_cache_size", 100))  # Max items in memory cache
        self._max_cache_file_size = int(self.config.get("max_cache_file_size", 10 * 1024 * 1024))  # 10MB max per file
        self._max_total_cache_size = int(self.config.get("max_total_cache_size", 100 * 1024 * 1024))  # 100MB total cache

        # Budget tracking
        self.budget_spent = 0.0
        self.budget_limit = None

        # Execution state
        self.running_tasks: Dict[str, asyncio.Task] = {}

    def _init_token_buckets(self):
        """Initialize token buckets from adapter capabilities."""
        for name, adapter in self.adapters.items():
            cap = adapter.capability
            if cap.rate_limit_rps:
                capacity = cap.rate_limit_burst or int(cap.rate_limit_rps * 10)
                self.token_buckets[name] = TokenBucket(
                    capacity=capacity,
                    rate=cap.rate_limit_rps,
                )

    async def execute_plan(self, plan: ExecutionPlan) -> Dict[str, ResultEnvelope]:
        """
        Execute entire plan, respecting dependencies.

        Returns map of node_id -> result.
        """
        # Set budget if specified in any task
        if plan.nodes:
            first_task = plan.nodes[0].task
            if first_task.constraints.budget_usd:
                self.budget_limit = first_task.constraints.budget_usd

        # Check for special execution strategies
        strategy = plan.metadata.get("strategy")

        if strategy == "cascade":
            return await self._execute_cascade_plan(plan)
        elif strategy == "vote":
            return await self._execute_vote_plan(plan)
        else:
            # Standard DAG execution
            return await self._execute_dag_plan(plan)

    async def _execute_dag_plan(self, plan: ExecutionPlan) -> Dict[str, ResultEnvelope]:
        """
        Execute plan as DAG, respecting dependencies.

        This is the standard execution path for SINGLE and DAG strategies.
        """
        results: Dict[str, ResultEnvelope] = {}
        completed: set = set()

        # Track plan-level termination state
        aborted_status: Optional[TaskStatus] = None

        while len(completed) < len(plan.nodes):
            # Get nodes ready to execute
            ready = plan.get_ready_nodes(completed)

            if not ready:
                # Check if we're stuck
                if len(completed) < len(plan.nodes):
                    # Some nodes have unresolved dependencies (failure upstream)
                    break
                else:
                    break

            # Execute ready nodes in parallel using asyncio tasks
            node_tasks = {}
            for node in ready:
                node_task = asyncio.create_task(self._execute_node(node))
                node_id = node.id
                node_tasks[node_id] = node_task
                # Track running task
                self.running_tasks[node_id] = node_task

            # Wait for all running nodes to complete
            for node_id, task in node_tasks.items():
                try:
                    result = await task
                    results[node_id] = result

                    status = result.status
                    if result.is_success():
                        completed.add(node_id)
                        continue

                    # Mark failure-like states as completed to avoid deadlock,
                    # but signal to stop scheduling further tasks.
                    if status in {
                        TaskStatus.FAILED,
                        TaskStatus.TIMEOUT,
                        TaskStatus.BUDGET_EXCEEDED,
                    }:
                        completed.add(node_id)
                        aborted_status = status
                    else:
                        completed.add(node_id)
                finally:
                    # Clean up the running task tracking
                    self.running_tasks.pop(node_id, None)

            if aborted_status:
                # Cancel any remaining running tasks to prevent resource leaks
                for node_id, task in self.running_tasks.items():
                    if not task.done():
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass  # Expected when cancelling tasks
                
                # Clear the running_tasks dict
                self.running_tasks.clear()
                break

        return results

    async def _execute_cascade_plan(self, plan: ExecutionPlan) -> Dict[str, ResultEnvelope]:
        """
        Execute cascade plan: try cheap tool first, fallback to strong if needed.

        Cascade strategy:
        1. Execute first (cheap) node
        2. If successful, skip remaining nodes and return
        3. If failed, execute second (strong) node
        4. Return best available result

        Preserves abort semantics for terminal failures.
        """
        results: Dict[str, ResultEnvelope] = {}

        if not plan.nodes:
            return results

        # Execute first node (cheap/fast option)
        first_node = plan.nodes[0]
        first_result = await self._execute_node(first_node)
        results[first_node.id] = first_result

        # If first node succeeded, we're done (skip fallback)
        if first_result.is_success():
            return results

        # First node failed - try fallback if available
        if len(plan.nodes) > 1:
            second_node = plan.nodes[1]
            second_result = await self._execute_node(second_node)
            results[second_node.id] = second_result

            # If second node succeeded, prefer its result
            if second_result.is_success():
                return results

        # Both failed - return both results (terminal abort)
        return results

    async def _execute_vote_plan(self, plan: ExecutionPlan) -> Dict[str, ResultEnvelope]:
        """
        Execute vote plan: run multiple tools in parallel and select best result.

        Vote strategy:
        1. Execute all nodes in parallel
        2. Select best result using _select_vote_result()
        3. Return all results with vote winner marked in metadata
        """
        results: Dict[str, ResultEnvelope] = {}

        if not plan.nodes:
            return results

        # Execute all vote nodes in parallel using asyncio tasks
        node_tasks = {}
        for node in plan.nodes:
            node_task = asyncio.create_task(self._execute_node(node))
            node_id = node.id
            node_tasks[node_id] = node_task
            # Track running task
            self.running_tasks[node_id] = node_task

        # Gather all results
        for node_id, task in node_tasks.items():
            try:
                result = await task
                results[node_id] = result
            finally:
                # Clean up the running task tracking
                self.running_tasks.pop(node_id, None)

        # Select best result
        winner_id = self._select_vote_result(results)

        # Mark winner in metadata
        if winner_id and winner_id in results:
            if not results[winner_id].metadata:
                results[winner_id].metadata = {}
            results[winner_id].metadata["vote_winner"] = True

        return results

    def _select_vote_result(self, results: Dict[str, ResultEnvelope]) -> Optional[str]:
        """
        Select best result from vote execution.

        Selection criteria (in priority order):
        1. Prefer successful results over failures
        2. Among successes, prefer fastest (lowest latency)
        3. If all failed, return first failure

        Returns: node_id of winning result, or None if no results
        """
        if not results:
            return None

        successful = [
            (node_id, result)
            for node_id, result in results.items()
            if result.is_success()
        ]

        # If we have successes, pick fastest
        if successful:
            winner = min(
                successful,
                key=lambda x: x[1].diagnostics.latency_ms if x[1].diagnostics else float('inf')
            )
            return winner[0]

        # All failed - return first failure
        return list(results.keys())[0]

    async def _execute_node(self, node: PlanNode) -> ResultEnvelope:
        """
        Execute a single plan node with retries and circuit breaker.
        """
        task = node.task
        adapter_name = node.tool

        # Check idempotency cache
        cache_key = task.hash_inputs()
        cached_result = self._check_cache(cache_key)
        if cached_result:
            cached_result.diagnostics.cache_hit = True
            return cached_result

        # Get adapter
        adapter = self.adapters.get(adapter_name)
        if not adapter:
            return ResultEnvelope(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error=f"Adapter '{adapter_name}' not found",
            )

        # Check circuit breaker
        if not self.circuit_breakers[adapter_name].can_execute():
            # Try alternative if available
            if node.alternatives:
                alt_name = node.alternatives[0]
                alt_adapter = self.adapters.get(alt_name)
                if alt_adapter and self.circuit_breakers[alt_name].can_execute():
                    adapter = alt_adapter
                    adapter_name = alt_name
                else:
                    return ResultEnvelope(
                        task_id=task.id,
                        status=TaskStatus.FAILED,
                        error=f"Circuit breaker open for {adapter_name} and no healthy alternatives",
                    )
            else:
                return ResultEnvelope(
                    task_id=task.id,
                    status=TaskStatus.FAILED,
                    error=f"Circuit breaker open for {adapter_name}",
                )

        # Execute with retries
        max_retries = task.constraints.max_retries
        for attempt in range(max_retries + 1):
            task_future = None
            try:
                # Check budget before execution
                if not self._check_budget(adapter, task):
                    return ResultEnvelope(
                        task_id=task.id,
                        status=TaskStatus.BUDGET_EXCEEDED,
                        error=f"Budget limit reached: ${self.budget_spent:.2f} / ${self.budget_limit:.2f}",
                    )

                # Wait for rate limit token
                if adapter_name in self.token_buckets:
                    await self.token_buckets[adapter_name].wait_for_tokens()

                # Execute with deadline - create a task and track it
                task_future = adapter.execute(task)
                
                deadline = task.constraints.deadline_ms
                if deadline:
                    result = await asyncio.wait_for(
                        task_future,
                        timeout=deadline / 1000.0,
                    )
                else:
                    result = await task_future

                # Track budget
                if result.diagnostics:
                    self.budget_spent += result.diagnostics.cost_usd
                    result.diagnostics.retries = attempt

                # Record success
                self.circuit_breakers[adapter_name].record_success()

                # Cache successful result
                if result.is_success():
                    self._cache_result(cache_key, result)

                return result

            except asyncio.TimeoutError:
                # Deadline exceeded
                # Cancel the running task if possible
                if task_future and hasattr(task_future, 'cancel'):
                    task_future.cancel()
                
                return ResultEnvelope(
                    task_id=task.id,
                    status=TaskStatus.TIMEOUT,
                    error=f"Deadline exceeded: {deadline}ms",
                )

            except Exception as e:
                # Record failure
                self.circuit_breakers[adapter_name].record_failure()

                # Check if should retry
                if attempt < max_retries:
                    # Exponential backoff
                    backoff = min(2 ** attempt, 60)  # Cap at 60s
                    await asyncio.sleep(backoff)
                    continue
                else:
                    # Final failure
                    return ResultEnvelope(
                        task_id=task.id,
                        status=TaskStatus.FAILED,
                        error=f"Execution failed after {max_retries} retries: {str(e)}",
                    )

        # Should not reach here
        return ResultEnvelope(
            task_id=task.id,
            status=TaskStatus.FAILED,
            error="Unknown execution error",
        )

    def _check_budget(self, adapter: BaseAdapter, task: TaskEnvelope) -> bool:
        """Check if budget allows execution."""
        if not self.budget_limit:
            return True

        estimated_cost = adapter.estimate_cost(task)
        return (self.budget_spent + estimated_cost) <= self.budget_limit

    def _check_cache(self, cache_key: str) -> Optional[ResultEnvelope]:
        """Check idempotency cache for existing result with proper deserialization."""
        # Check memory cache first
        if cache_key in self._memory_cache:
            # Move to end of access order (mark as recently used)
            if cache_key in self._cache_access_order:
                self._cache_access_order.remove(cache_key)
            self._cache_access_order.append(cache_key)
            return self._memory_cache[cache_key]
        
        # Check disk cache
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                # Check file size before reading to prevent memory issues
                file_size = cache_file.stat().st_size
                if file_size > self._max_cache_file_size:
                    print(f"Cache file too large, skipping: {cache_key}")
                    return None
                
                data = json.loads(cache_file.read_text())
                
                # Properly reconstruct ResultEnvelope from dict
                result = ResultEnvelope(
                    task_id=data["task_id"],
                    status=TaskStatus(data["status"]),
                    diagnostics=Diagnostics(
                        latency_ms=data["diagnostics"]["latency_ms"],
                        tokens_input=data["diagnostics"].get("tokens_input"),
                        tokens_output=data["diagnostics"].get("tokens_output"),
                        cost_usd=data["diagnostics"].get("cost_usd", 0.0),
                        provider=data["diagnostics"].get("provider"),
                        model=data["diagnostics"].get("model"),
                        retries=data["diagnostics"].get("retries", 0),
                        cache_hit=data["diagnostics"].get("cache_hit", False),
                    ) if data["diagnostics"] else None,
                    provenance=Provenance(
                        tool=data["provenance"]["tool"],
                        version=data["provenance"]["version"],
                        args=data["provenance"]["args"],
                        env=data["provenance"]["env"],
                        started_at=datetime.fromisoformat(data["provenance"]["started_at"]),
                        completed_at=datetime.fromisoformat(data["provenance"]["completed_at"]),
                    ) if data["provenance"] else None,
                    error=data["error"],
                    warnings=data["warnings"],
                    completed_at=datetime.fromisoformat(data["completed_at"]),
                )
                
                # Create artifacts from data
                result.artifacts = []
                for artifact_data in data["artifacts"]:
                    artifact = Artifact(
                        type=ArtifactType(artifact_data["type"]),
                        content=artifact_data["content"],
                        path=artifact_data["path"],
                        url=artifact_data["url"],
                        metadata=artifact_data["metadata"],
                        size_bytes=artifact_data["size_bytes"],
                        checksum=artifact_data["checksum"],
                    )
                    result.artifacts.append(artifact)
                
                # Add to memory cache with LRU management
                self._add_to_memory_cache(cache_key, result)
                
                return result
            except Exception as e:
                print(f"Error loading cache for {cache_key}: {e}")
                # Clean up corrupted cache file
                try:
                    cache_file.unlink(missing_ok=True)
                except:
                    pass
                pass
        return None

    def _cache_result(self, cache_key: str, result: ResultEnvelope):
        """Cache result for idempotency with size management."""
        # Add to memory cache first
        self._add_to_memory_cache(cache_key, result)
        
        # Write to disk cache
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            cache_dict = result.to_dict()
            cache_content = json.dumps(cache_dict, indent=2)
            
            # Check if content is too large before writing
            if len(cache_content.encode('utf-8')) > self._max_cache_file_size:
                print(f"Result too large to cache, skipping disk cache: {cache_key}")
                return
            
            cache_file.write_text(cache_content)
            
            # Check and enforce total cache size limits
            self._enforce_cache_size_limits()
            
        except Exception as e:
            print(f"Error writing cache for {cache_key}: {e}")
            # Remove from memory cache if disk write fails
            self._memory_cache.pop(cache_key, None)
            if cache_key in self._cache_access_order:
                self._cache_access_order.remove(cache_key)

    def _add_to_memory_cache(self, cache_key: str, result: ResultEnvelope):
        """Add result to memory cache with LRU eviction."""
        # If key already exists, update it
        if cache_key in self._memory_cache:
            self._memory_cache[cache_key] = result
            # Move to end of access order
            if cache_key in self._cache_access_order:
                self._cache_access_order.remove(cache_key)
            self._cache_access_order.append(cache_key)
            return
        
        # If cache is at max size, remove least recently used item
        if len(self._memory_cache) >= self._max_memory_cache_size:
            if self._cache_access_order:
                lru_key = self._cache_access_order.pop(0)
                self._memory_cache.pop(lru_key, None)
        
        # Add new item
        self._memory_cache[cache_key] = result
        self._cache_access_order.append(cache_key)

    def _enforce_cache_size_limits(self):
        """Enforce total cache size limits by removing old files."""
        try:
            # Get all cache files and their sizes
            cache_files = list(self.cache_dir.glob("*.json"))
            file_sizes = [(f, f.stat().st_size) for f in cache_files if f.is_file()]
            total_size = sum(size for _, size in file_sizes)
            
            if total_size > self._max_total_cache_size:
                # Sort by modification time (oldest first)
                file_sizes.sort(key=lambda x: x[0].stat().st_mtime)
                
                # Remove oldest files until under the limit
                removed_size = 0
                for file_path, size in file_sizes:
                    if total_size - removed_size <= self._max_total_cache_size:
                        break
                    file_path.unlink(missing_ok=True)
                    removed_size += size
                    # Also remove from memory cache if present
                    cache_key = file_path.stem
                    self._memory_cache.pop(cache_key, None)
                    if cache_key in self._cache_access_order:
                        self._cache_access_order.remove(cache_key)
                        
        except Exception as e:
            print(f"Error enforcing cache size limits: {e}")

    def clear_cache(self):
        """Clear both memory and disk cache."""
        # Clear memory cache
        self._memory_cache.clear()
        self._cache_access_order.clear()
        
        # Clear disk cache
        import shutil
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except:
                pass

    def get_budget_status(self) -> Dict[str, Any]:
        """Get current budget status."""
        return {
            "spent": self.budget_spent,
            "limit": self.budget_limit,
            "remaining": (self.budget_limit - self.budget_spent) if self.budget_limit else None,
            "percent_used": (self.budget_spent / self.budget_limit * 100) if self.budget_limit else 0,
        }

    def reset_budget(self):
        """Reset budget tracking."""
        self.budget_spent = 0.0
        self.budget_limit = None
