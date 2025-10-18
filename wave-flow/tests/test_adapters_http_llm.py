from __future__ import annotations

import sys
import types

import httpx
import pytest

from conductor.adapters.http import HTTPAdapter
from conductor.adapters.llm import LLMAdapter
from conductor.envelopes import TaskConstraints, TaskEnvelope, TaskStatus
from tests.utils import make_capability


@pytest.mark.asyncio
async def test_http_adapter_uses_mock_transport(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            captured["client_kwargs"] = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def request(self, method, url, headers=None, params=None, data=None, json=None):
            captured["request"] = {
                "method": method,
                "url": url,
                "headers": headers,
                "params": params,
                "json": json,
            }
            return httpx.Response(
                status_code=200,
                request=httpx.Request(method, url),
                headers={"content-type": "application/json"},
                json={"status": "ok"},
            )

    import conductor.adapters.http as http_module

    monkeypatch.setattr(http_module, "httpx", types.SimpleNamespace(AsyncClient=FakeAsyncClient))

    capability = make_capability(
        name="http",
        intents=["fetch"],
        input_modes=["http"],
        output_modes=["json"],
    )
    adapter = HTTPAdapter(
        capability,
        config={"base_url": "https://example.com/api", "timeout": 5},
    )

    task = TaskEnvelope(
        id="http-task",
        intent="fetch",
        inputs={"method": "GET", "url": "https://example.com/api/resource", "params": {"q": "wave"}},
        constraints=TaskConstraints(),
    )

    result = await adapter.execute(task)

    assert result.status == TaskStatus.COMPLETED
    assert result.artifacts
    artifact = result.artifacts[0]
    assert artifact.type.value == "json"
    assert "status" in (artifact.content or "")
    assert captured["request"]["params"] == {"q": "wave"}


@pytest.mark.asyncio
async def test_llm_adapter_uses_fake_openai(monkeypatch) -> None:
    class FakeChatCompletions:
        async def create(self, *, model, messages, max_tokens, temperature):
            return types.SimpleNamespace(
                choices=[
                    types.SimpleNamespace(
                        message=types.SimpleNamespace(content="mocked response"),
                        finish_reason="stop",
                    )
                ],
                usage=types.SimpleNamespace(prompt_tokens=10, completion_tokens=20),
            )

    class FakeClient:
        def __init__(self, *_, **__):
            self.chat = types.SimpleNamespace(completions=FakeChatCompletions())

    fake_openai = types.SimpleNamespace(AsyncOpenAI=lambda *args, **kwargs: FakeClient())
    monkeypatch.setitem(sys.modules, "openai", fake_openai)

    capability = make_capability(
        name="gpt-3.5-turbo",
        intents=["analyze"],
        input_modes=["api"],
        output_modes=["text"],
        token_limit=4096,
    )
    adapter = LLMAdapter(
        capability,
        config={"provider": "openai", "model": "gpt-3.5-turbo", "api_key": "sk-test"},
    )

    task = TaskEnvelope(
        id="llm-task",
        intent="analyze",
        inputs={
            "messages": [
                {"role": "user", "content": "Say hello"},
            ]
        },
        constraints=TaskConstraints(),
    )

    result = await adapter.execute(task)

    assert result.status == TaskStatus.COMPLETED
    assert result.artifacts
    assert result.artifacts[0].content == "mocked response"
    assert result.diagnostics is not None
    assert result.diagnostics.tokens_input == 10
    assert result.diagnostics.tokens_output == 20
