# Wave-Flow Conductor

AI orchestration system with privacy/budget/deadline awareness. Routes tasks to optimal tools via rule-based planning and executes with production-grade reliability.

## Features

### Core Orchestration
- **Smart Routing**: Rule-based tool selection with capability matching
- **Execution Strategies**: Single, cascade (cheap→strong), parallel voting, DAG workflows
- **Privacy Lanes**: Internal (local-only) vs External (cloud-enabled)
- **Budget Awareness**: Track costs, enforce limits, graceful degradation
- **Deadline Enforcement**: Timeout handling with fallback strategies

### Production Reliability
- **Token Bucket Rate Limiting**: Per-provider rate control with burst handling
- **Circuit Breakers**: Automatic failure detection and recovery
- **Exponential Backoff Retries**: Configurable retry strategies
- **Idempotency**: Cache-based deduplication
- **Artifact Provenance**: Full lineage tracking (tool@version, args, env, timing, cost)

### Tool Integration
- **Black-box Adapters**: CLI, HTTP, LLM, GitHub, SSH, VMs, Storage
- **Auto-introspection**: Discover tool capabilities via `--help`, `--version`
- **Hot-reload**: YAML-based capability configs update without restart
- **Health Monitoring**: Background health checks with automatic routing updates

## Quick Start

### Installation

```bash
# Clone repository
git clone <repo-url>
cd wave-flow

# Install with dependencies
pip install -e ".[llm,validation]"

# Set API keys
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-...
```

### Basic Usage

```bash
# Simple code edit
conductor run "edit the calculate function to handle edge cases" \
  --file src/calc.py \
  --privacy internal

# PDF report pipeline with budget
conductor run "extract tables from PDFs and create summary chart" \
  --input reports/*.pdf \
  --steps ocr,table,aggregate,chart,write \
  --budget 0.80

# Issue triage with deadline
conductor run "triage open issues and add labels" \
  --repo myorg/myproject \
  --deadline 300 \
  --budget 0.25
```

### Python API

```python
import asyncio
from conductor.envelopes import TaskEnvelope, TaskConstraints, PrivacyLevel
from conductor.main import create_adapters
from conductor.planner import Router, Planner
from conductor.executor import Executor

async def main():
    # Create task
    task = TaskEnvelope(
        id="task-1",
        intent="explain this code",
        inputs={"code": "def fib(n): ..."},
        constraints=TaskConstraints(
            privacy=PrivacyLevel.INTERNAL,
            budget_usd=0.10,
        ),
    )

    # Setup orchestration
    adapters = create_adapters({"openai_api_key": "sk-..."})
    router = Router(list(adapters.values()))
    planner = Planner(router)
    executor = Executor(adapters)

    # Execute
    plan = planner.plan(task)
    results = await executor.execute_plan(plan)

    # Get output
    for result in results.values():
        print(result.artifacts[0].content)

asyncio.run(main())
```

## Architecture

### Data Contracts

**TaskEnvelope** (inputs):
- `intent`: What to do
- `inputs`: Data (repo, files, brief)
- `constraints`: Privacy, deadline, budget
- `policy`: Additional rules

**ResultEnvelope** (outputs):
- `status`: completed | failed | timeout | budget_exceeded | degraded
- `artifacts`: List of outputs (patch, csv, json, image, text)
- `diagnostics`: Latency, tokens, cost, provider
- `provenance`: Tool@version, args, env, timing

### Routing Algorithm

```
1. Rule-based filtering:
   - Privacy compatibility (internal ⇒ no cloud tools)
   - Intent matching (can tool handle task?)
   - Context size limits (fits in tool window?)
   - Environment availability (local vs cloud vs gpu)

2. Score remaining candidates:
   score = α·cap_fit + β·latency + γ·quality + δ·health − ε·cost − ζ·queue

3. Select strategy:
   - High confidence (>0.85) → SINGLE
   - Medium (>0.70) → CASCADE (cheap then strong)
   - Low → PARALLEL_VOTE (2-3 tools, vote)
   - Multi-step → DAG
```

### Execution Flow

```
Plan → Scheduler → Token Bucket → Circuit Breaker → Adapter → Harvest → Validate → Cache
  ↓                    ↓                ↓              ↓         ↓         ↓        ↓
Budget Check    Rate Limit      Health Check    Execute    Parse    Check    Store
```

## Tool Adapters

### CLI Adapter
```python
from conductor.adapters.cli import CLIAdapter
from conductor.adapters.base import ToolCapability

adapter = CLIAdapter(
    capability=ToolCapability(
        name="python",
        version="3.11",
        intents=["python", "script"],
        ...
    ),
    config={"command": "python", "timeout_default": 300}
)
```

### HTTP Adapter
```python
from conductor.adapters.http import HTTPAdapter

adapter = HTTPAdapter(
    capability=...,
    config={
        "base_url": "https://api.example.com",
        "auth_type": "bearer",
        "auth_token": "...",
    }
)
```

### LLM Adapter
```python
from conductor.adapters.llm import LLMAdapter

# OpenAI
adapter = LLMAdapter(
    capability=...,
    config={
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "...",
    }
)

# Anthropic Claude
adapter = LLMAdapter(
    capability=...,
    config={
        "provider": "anthropic",
        "model": "claude-3-sonnet-20240229",
        "api_key": "...",
    }
)

# Local Ollama
adapter = LLMAdapter(
    capability=...,
    config={
        "provider": "ollama",
        "model": "codellama",
        "api_base": "http://localhost:11434",
    }
)
```

## Capability Configuration

Create YAML files in `caps/` directory:

```yaml
# caps/my-tool.yaml
name: my-tool
version: 1.0.0

intents:
  - code.review
  - test.generate

input_modes:
  - api

output_modes:
  - json
  - text

context_limit: 8192
rate_limit_rps: 5.0
rate_limit_burst: 10

environments:
  - cloud

cost_per_call: 0.01
requires_auth: true

privacy_compatible:
  - external

metadata:
  provider: example
  quality_tier: medium
```

## Wave Terminal Integration

Conductor auto-detects Wave Terminal and enhances UX:

```bash
# Automatic features when Wave detected:
# - Pane management (logs, tests, results)
# - Progress toasts
# - Artifact preview
# - Interactive plan graphs

# Manual integration
export WAVE_ENABLE=1
conductor run "..."
# → Opens panes automatically via wsh

# Web UI as Wave panel
conductor serve
# → Accessible in Wave web widgets
```

## Examples

### F1: Code Edit → Tests → PR

```bash
conductor run "refactor payment processing to use async/await" \
  --repo . \
  --file payments/processor.py \
  --with tests,pr \
  --privacy internal \
  --deadline 900

# What happens:
# 1. Routes to local LLM (privacy=internal)
# 2. Generates code changes
# 3. Runs tests (internal tool)
# 4. Creates PR if tests pass
# 5. Repairs on test failures (cascade to stronger model if needed)
```

### F2: PDF → Tables → Chart → Blog

```bash
conductor run "create data story from quarterly reports" \
  --input reports/Q*.pdf \
  --steps ocr,table,aggregate,chart,write,pr \
  --budget 0.80 \
  --deadline 1800

# What happens:
# 1. OCR PDFs (vision API, $0.10)
# 2. Extract tables (LLM, $0.15)
# 3. Aggregate data (local script, $0)
# 4. Generate chart (local tool, $0)
# 5. Write blog post (LLM, $0.40)
# 6. Create PR (GitHub API, $0)
# Total: ~$0.65, under budget ✓
```

### F3: Issue Triage

```bash
conductor run "triage open issues" \
  --repo myorg/myrepo \
  --limit 30 \
  --with labels,replies \
  --budget 0.25

# What happens:
# 1. Fetch issues via GitHub API
# 2. Batch classify (LLM with rate limiting)
# 3. Add labels via API
# 4. Post triage comments
# 5. Stay under budget by using cheaper model if needed
```

## Configuration

Environment variables:

```bash
# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_TOKEN=ghp_...

# Defaults
CONDUCTOR_CACHE_DIR=.conductor/cache
CONDUCTOR_DEFAULT_BUDGET=1.00
CONDUCTOR_DEFAULT_PRIVACY=external
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev,llm,validation,web]"

# Run full test suite (recommended)
PYTHONPATH=. PYTEST_ADDOPTS='-p no:rerunfailures' pytest

# Run tests with verbose output
PYTHONPATH=. PYTEST_ADDOPTS='-p no:rerunfailures' pytest -v

# Run specific test module
PYTHONPATH=. pytest tests/test_executor.py -v

# Run with coverage reporting
PYTHONPATH=. pytest --cov=conductor --cov-report=html

# Type checking
mypy conductor/

# Format code
black conductor/
```

### Testing Philosophy

The test suite validates:
- **Core orchestration**: Envelopes, router/planner, executor safeguards
- **Async execution paths**: Budget checks, circuit breakers, token buckets
- **DAG execution**: Multi-node plans with dependencies and partial failures
- **Harvest & validation**: JSON extraction, code fences, diff parsing, validators

### Key Executor Behavior

The executor treats **all executed nodes as terminal** (completed), regardless of success or failure. This prevents infinite loops in DAG execution when nodes fail with statuses like `BUDGET_EXCEEDED`, `TIMEOUT`, or `FAILED`.

Downstream nodes can check `result.is_success()` if they need to verify dependency success before executing. This design allows DAGs to continue executing independent branches even when some nodes fail.

Example:
```python
# Node A fails, but Node B (independent) still executes
# Node C (depends on A) also executes, can check A's status if needed
```

## Project Structure

```
wave-flow/
├── conductor/
│   ├── envelopes.py         # Data contracts
│   ├── planner.py           # Router & planner
│   ├── executor.py          # Scheduler & executor
│   ├── harvest.py           # Output parsing
│   ├── validators.py        # Result validation
│   ├── main.py              # CLI entry point
│   └── adapters/
│       ├── base.py          # Adapter interface
│       ├── cli.py           # CLI tools
│       ├── http.py          # REST APIs
│       ├── llm.py           # LLM providers
│       └── ...
├── caps/                    # Tool capability YAMLs
├── flows/                   # Pre-defined workflows
├── tests/                   # Test suite
└── .conductor/              # Runtime data (gitignored)
```

## Testing & Execution Notes

- **Executor termination semantics**: `Executor.execute_plan` treats `FAILED`, `TIMEOUT`, and `BUDGET_EXCEEDED` results as terminal. Dependent nodes are not scheduled once a fatal status is observed, but already-running tasks still complete. See `tests/test_executor.py` for examples covering continuation and early-abort behaviour.
- **CLI adapter integration**: The test suite invokes the runtime interpreter (`sys.executable`) via the CLI adapter to avoid environment-specific command paths. When adding new CLI capabilities, mirror this pattern so tests stay portable.
- **Running tests**: Execute `PYTHONPATH=. PYTEST_ADDOPTS='-p no:rerunfailures' pytest` to run the suite without third-party plugin interference.

## Roadmap

**Week 1** (MVP - Current):
- ✅ Core envelopes & adapters
- ✅ Router & planner with scoring
- ✅ Executor with token buckets, retries, CBs
- ✅ Harvest & validators
- ✅ CLI interface
- ⏳ F1-F3 end-to-end testing

**Week 2**:
- Caps registry with auto-introspection
- Policy engine (privacy lanes, secrets management)
- Observability & metrics dashboard
- Web UI (FastAPI + React)
- Wave integration (wsh + widgets)

**Week 3+**:
- DAG execution for complex workflows
- Additional adapters (SSH, VMs, storage)
- ML-based routing (learn from history)
- Multi-provider ensembles
- Advanced validation (semantic checks)

## License

MIT

## Contributing

Contributions welcome! See CONTRIBUTING.md for guidelines.
