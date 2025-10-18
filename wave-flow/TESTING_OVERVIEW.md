# Testing Overview

## Current Scope
- **Unit coverage** spans core orchestration primitives: envelopes, router/planner selection logic, executor safeguards (including terminal failure handling), output harvesting, and validators (JSON schema, rubric, pytest).
- **Async execution paths** validated through dummy adapters exercising budget checks, circuit breaker fallback, token bucket behavior, and plan-abort semantics when fatal results surface.
- **Adapter smoke tests** now include a CLI integration that executes the runtime's Python interpreter, capturing stdout artifacts and ensuring capability/constraint plumbing works end to end.
- **Harvest and validation workflows** verified across JSON extraction, code fences, diff parsing, and rubric enforcement to ensure artifact handling remains resilient.
- **CASCADE strategy coverage** (✅ **COMPLETE**): 5 comprehensive tests covering primary success (skip fallback), primary fails → fallback succeeds, both fail, budget exceeded triggers fallback, and circuit breaker triggers fallback.
- **VOTE strategy coverage** (✅ **COMPLETE**): 4 comprehensive tests covering all succeed (pick fastest), partial failures (pick from successes), all fail (return failures), and success preferred over speed.

## Test Execution
Run the full suite locally with:

```bash
PYTHONPATH=. PYTEST_ADDOPTS='-p no:rerunfailures' pytest
```

The command disables problematic third-party plugins in constrained environments while preserving asyncio strict mode.

**Current Status**: 44 tests passing (20 executor tests including 9 CASCADE/VOTE tests)

## Recommendations
1. ~~**Cascade/vote plan coverage**~~: ✅ **COMPLETED** - Comprehensive CASCADE and VOTE execution tests added with abort semantics validation.
2. **HTTP/LLM adapter doubles**: Introduce mocked async clients (e.g., `httpx.MockTransport`) so HTTP/LLM adapters gain similar integration protection without hitting real endpoints.
3. **Validator ergonomics**: Introduce fixture-driven validation suites that combine rubric, schema, and pytest validators to detect configuration drift early.
4. **Coverage reporting**: Wire `pytest --cov` into CI when available to keep visibility on orchestration-critical modules and guide future test additions.

## Next Steps
- Document the executor failure-handling behaviour and CLI adapter exercise in `README.md` so contributors understand expectations before extending orchestration paths.
- Build on the CLI integration harness to cover HTTP/LLM adapters once mocking scaffolds land, keeping adapter contracts tight as new providers appear.
