"""
LLM adapter for AI model integrations.

Supports:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- Qwen
- Local/Ollama models
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional, List
import json

from conductor.adapters.base import BaseAdapter, ToolCapability
from conductor.envelopes import (
    TaskEnvelope,
    ResultEnvelope,
    TaskStatus,
    Artifact,
    ArtifactType,
    Diagnostics,
    Provenance,
)


class LLMAdapter(BaseAdapter):
    """
    Unified adapter for LLM providers.

    Abstracts provider differences and provides unified interface.
    """

    # Pricing per 1M tokens (rough estimates, should be config-driven)
    PRICING = {
        "gpt-4": {"input": 30.0, "output": 60.0},
        "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
        "claude-3-opus": {"input": 15.0, "output": 75.0},
        "claude-3-sonnet": {"input": 3.0, "output": 15.0},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
        "gemini-pro": {"input": 0.5, "output": 1.5},
        "qwen": {"input": 0.0, "output": 0.0},  # Free tier
        "ollama": {"input": 0.0, "output": 0.0},  # Local
    }

    def __init__(
        self,
        capability: ToolCapability,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(capability, config)
        self.provider = config.get("provider") if config else "openai"
        self.model = config.get("model") if config else "gpt-3.5-turbo"
        self.api_key = config.get("api_key")
        self.api_base = config.get("api_base")
        self.max_tokens = config.get("max_tokens", 4096)
        self.temperature = config.get("temperature", 0.7)

    async def execute(self, task: TaskEnvelope) -> ResultEnvelope:
        """Execute LLM request."""
        start_time = time.time()
        started_at = datetime.now()

        # Validate task
        is_valid, error_msg = self.validate_task(task)
        if not is_valid:
            return ResultEnvelope(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error=error_msg,
            )

        # Extract parameters
        messages = task.inputs.get("messages", [])
        prompt = task.inputs.get("prompt")
        system = task.inputs.get("system")
        model = task.inputs.get("model", self.model)
        max_tokens = task.inputs.get("max_tokens", self.max_tokens)
        temperature = task.inputs.get("temperature", self.temperature)

        # Build messages array if prompt provided
        if prompt and not messages:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

        if not messages:
            return ResultEnvelope(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error="No messages or prompt provided",
            )

        # Route to appropriate provider
        try:
            if self.provider == "openai":
                result = await self._execute_openai(messages, model, max_tokens, temperature, task)
            elif self.provider == "anthropic":
                result = await self._execute_anthropic(messages, model, max_tokens, temperature, task)
            elif self.provider == "google":
                result = await self._execute_google(messages, model, max_tokens, temperature, task)
            elif self.provider in ["ollama", "local"]:
                result = await self._execute_ollama(messages, model, max_tokens, temperature, task)
            else:
                return ResultEnvelope(
                    task_id=task.id,
                    status=TaskStatus.FAILED,
                    error=f"Unknown provider: {self.provider}",
                )

            latency_ms = (time.time() - start_time) * 1000

            # Add diagnostics to result
            if result and result.diagnostics:
                result.diagnostics.latency_ms = latency_ms
                result.diagnostics.provider = self.provider
                result.diagnostics.model = model

            return result

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return ResultEnvelope(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error=f"LLM execution error: {str(e)}",
                diagnostics=Diagnostics(
                    latency_ms=latency_ms,
                    provider=self.provider,
                    model=model,
                ),
                provenance=Provenance(
                    tool=self.capability.name,
                    version=self.capability.version,
                    args={"provider": self.provider, "model": model},
                    env={},
                    started_at=started_at,
                    completed_at=datetime.now(),
                ),
            )

    async def _execute_openai(
        self,
        messages: List[Dict],
        model: str,
        max_tokens: int,
        temperature: float,
        task: TaskEnvelope,
    ) -> ResultEnvelope:
        """Execute OpenAI API request."""
        try:
            import openai
        except ImportError:
            raise ImportError("openai package required. Install with: pip install openai")

        client = openai.AsyncOpenAI(api_key=self.api_key, base_url=self.api_base)

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        content = response.choices[0].message.content
        usage = response.usage

        # Calculate cost
        cost = self._calculate_cost(model, usage.prompt_tokens, usage.completion_tokens)

        return ResultEnvelope(
            task_id=task.id,
            status=TaskStatus.COMPLETED,
            artifacts=[
                Artifact(
                    type=ArtifactType.TEXT,
                    content=content,
                    metadata={
                        "model": model,
                        "finish_reason": response.choices[0].finish_reason,
                    },
                )
            ],
            diagnostics=Diagnostics(
                latency_ms=0,  # Will be set by execute()
                tokens_input=usage.prompt_tokens,
                tokens_output=usage.completion_tokens,
                cost_usd=cost,
                provider=self.provider,
                model=model,
            ),
            provenance=Provenance(
                tool=self.capability.name,
                version=self.capability.version,
                args={"provider": self.provider, "model": model},
                env={},
                started_at=datetime.now(),
                completed_at=datetime.now(),
            ),
        )

    async def _execute_anthropic(
        self,
        messages: List[Dict],
        model: str,
        max_tokens: int,
        temperature: float,
        task: TaskEnvelope,
    ) -> ResultEnvelope:
        """Execute Anthropic API request."""
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package required. Install with: pip install anthropic")

        # Extract system message if present
        system_msg = None
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                user_messages.append(msg)

        client = anthropic.AsyncAnthropic(api_key=self.api_key)

        kwargs = {
            "model": model,
            "messages": user_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_msg:
            kwargs["system"] = system_msg

        response = await client.messages.create(**kwargs)

        content = response.content[0].text if response.content else ""

        # Calculate cost
        cost = self._calculate_cost(model, response.usage.input_tokens, response.usage.output_tokens)

        return ResultEnvelope(
            task_id=task.id,
            status=TaskStatus.COMPLETED,
            artifacts=[
                Artifact(
                    type=ArtifactType.TEXT,
                    content=content,
                    metadata={
                        "model": model,
                        "stop_reason": response.stop_reason,
                    },
                )
            ],
            diagnostics=Diagnostics(
                latency_ms=0,
                tokens_input=response.usage.input_tokens,
                tokens_output=response.usage.output_tokens,
                cost_usd=cost,
                provider=self.provider,
                model=model,
            ),
            provenance=Provenance(
                tool=self.capability.name,
                version=self.capability.version,
                args={"provider": self.provider, "model": model},
                env={},
                started_at=datetime.now(),
                completed_at=datetime.now(),
            ),
        )

    async def _execute_google(
        self,
        messages: List[Dict],
        model: str,
        max_tokens: int,
        temperature: float,
        task: TaskEnvelope,
    ) -> ResultEnvelope:
        """Execute Google Gemini API request."""
        # Placeholder - would need google-generativeai package
        raise NotImplementedError("Google Gemini adapter not yet implemented")

    async def _execute_ollama(
        self,
        messages: List[Dict],
        model: str,
        max_tokens: int,
        temperature: float,
        task: TaskEnvelope,
    ) -> ResultEnvelope:
        """Execute Ollama local API request."""
        try:
            import httpx
        except ImportError:
            raise ImportError("httpx package required. Install with: pip install httpx")

        api_base = self.api_base or "http://localhost:11434"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{api_base}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
                timeout=300.0,
            )
            response.raise_for_status()
            data = response.json()

        content = data.get("message", {}).get("content", "")

        return ResultEnvelope(
            task_id=task.id,
            status=TaskStatus.COMPLETED,
            artifacts=[
                Artifact(
                    type=ArtifactType.TEXT,
                    content=content,
                    metadata={"model": model},
                )
            ],
            diagnostics=Diagnostics(
                latency_ms=0,
                cost_usd=0.0,  # Local execution
                provider="ollama",
                model=model,
            ),
            provenance=Provenance(
                tool=self.capability.name,
                version=self.capability.version,
                args={"provider": "ollama", "model": model},
                env={},
                started_at=datetime.now(),
                completed_at=datetime.now(),
            ),
        )

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on token usage."""
        # Find matching pricing
        pricing = None
        for model_key, prices in self.PRICING.items():
            if model_key in model.lower():
                pricing = prices
                break

        if not pricing:
            return 0.0

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def estimate_cost(self, task: TaskEnvelope) -> float:
        """Estimate cost based on input size."""
        messages = task.inputs.get("messages", [])
        prompt = task.inputs.get("prompt", "")

        # Rough token estimation (4 chars = 1 token)
        total_chars = sum(len(str(m.get("content", ""))) for m in messages) + len(prompt)
        estimated_tokens = total_chars // 4

        # Assume 2:1 output:input ratio
        input_tokens = estimated_tokens
        output_tokens = estimated_tokens * 2

        return self._calculate_cost(self.model, input_tokens, output_tokens)

    async def health_check(self) -> bool:
        """Check if LLM provider is available."""
        try:
            # Simple test request
            if self.provider == "ollama":
                import httpx
                api_base = self.api_base or "http://localhost:11434"
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{api_base}/api/tags", timeout=5.0)
                    return response.status_code == 200
            else:
                # For cloud providers, assume available if API key present
                return self.api_key is not None
        except:
            return False
