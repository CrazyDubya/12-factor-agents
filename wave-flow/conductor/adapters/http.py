"""
HTTP adapter for REST API integrations.

Supports:
- GET/POST/PUT/DELETE/PATCH requests
- Authentication (Bearer, API Key, Basic)
- Custom headers
- JSON/form-data payloads
- Response harvesting
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional
import json
import re
from urllib.parse import urlparse

try:
    import httpx
except ImportError:
    httpx = None

from conductor.adapters.base import BaseAdapter, ToolCapability, ExecutionEnvironment
from conductor.envelopes import (
    TaskEnvelope,
    ResultEnvelope,
    TaskStatus,
    Artifact,
    ArtifactType,
    Diagnostics,
    Provenance,
)


class HTTPAdapter(BaseAdapter):
    """
    Adapter for HTTP/REST APIs.

    Supports multiple authentication methods and content types.
    """

    def __init__(
        self,
        capability: ToolCapability,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(capability, config)
        self.base_url = config.get("base_url") if config else None
        self.auth_type = config.get("auth_type", "none")  # bearer, api_key, basic, none
        self.auth_token = config.get("auth_token")
        self.api_key_header = config.get("api_key_header", "X-API-Key")
        self.timeout = config.get("timeout", 30)
        self.verify_ssl = config.get("verify_ssl", True)

        if httpx is None:
            raise ImportError("httpx is required for HTTP adapter. Install with: pip install httpx")

    async def execute(self, task: TaskEnvelope) -> ResultEnvelope:
        """Execute HTTP request."""
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

        # Extract request parameters
        method = task.inputs.get("method", "GET").upper()
        url = task.inputs.get("url", self.base_url)
        headers = task.inputs.get("headers", {})
        params = task.inputs.get("params", {})
        data = task.inputs.get("data")
        json_data = task.inputs.get("json")
        
        # SECURITY: Validate HTTP method
        allowed_methods = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
        if method not in allowed_methods:
            return ResultEnvelope(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error=f"Invalid HTTP method: {method}",
            )
        
        # SECURITY: Validate URL
        if not url:
            return ResultEnvelope(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error="No URL specified",
            )
        
        # Parse and validate URL structure
        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme or parsed_url.scheme not in ["http", "https"]:
                return ResultEnvelope(
                    task_id=task.id,
                    status=TaskStatus.FAILED,
                    error=f"Invalid URL scheme: {parsed_url.scheme}. Only http and https allowed.",
                )
            
            # Prevent requests to internal addresses if not allowed
            if not self.capability.supports_environment(ExecutionEnvironment.LOCAL):
                # Check for potentially dangerous internal addresses
                if parsed_url.hostname in ["localhost", "127.0.0.1", "::1"] or \
                   parsed_url.hostname.startswith("10.") or \
                   parsed_url.hostname.startswith("172.") or \
                   parsed_url.hostname.startswith("192.168."):
                    return ResultEnvelope(
                        task_id=task.id,
                        status=TaskStatus.FAILED,
                        error=f"Access to internal address not allowed: {parsed_url.hostname}",
                    )
        except Exception as e:
            return ResultEnvelope(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error=f"Invalid URL format: {str(e)}",
            )
        
        # SECURITY: Validate headers to prevent dangerous header injection
        validated_headers = {}
        forbidden_headers = {
            "host", "content-length", "content-type", "connection", 
            "upgrade", "transfer-encoding", "http2-settings"
        }
        
        for header_name, header_value in headers.items():
            # Validate header name
            if not re.match(r'^[a-zA-Z0-9_-]+

        if not url:
            return ResultEnvelope(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error="No URL specified",
            )

        # Add authentication
        if self.auth_type == "bearer" and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        elif self.auth_type == "api_key" and self.auth_token:
            headers[self.api_key_header] = self.auth_token

        # Determine timeout
        timeout = task.constraints.deadline_ms / 1000 if task.constraints.deadline_ms else self.timeout

        try:
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=timeout) as client:
                # Make request
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    data=data,
                    json=json_data,
                )

                latency_ms = (time.time() - start_time) * 1000

                # Check response status
                if response.status_code >= 400:
                    return ResultEnvelope(
                        task_id=task.id,
                        status=TaskStatus.FAILED,
                        error=f"HTTP {response.status_code}: {response.text}",
                        diagnostics=Diagnostics(
                            latency_ms=latency_ms,
                            provider=self.capability.name,
                        ),
                        provenance=Provenance(
                            tool=self.capability.name,
                            version=self.capability.version,
                            args={"method": method, "url": url},
                            env={},
                            started_at=started_at,
                            completed_at=datetime.now(),
                        ),
                    )

                # Parse response
                artifacts = []
                content_type = response.headers.get("content-type", "")
                response_size = len(response.content)
                
                # Check for response size to prevent memory issues
                max_response_size = 100 * 1024 * 1024  # 100MB limit
                if response_size > max_response_size:
                    return ResultEnvelope(
                        task_id=task.id,
                        status=TaskStatus.FAILED,
                        error=f"Response too large: {response_size} bytes > {max_response_size} bytes limit",
                        diagnostics=Diagnostics(
                            latency_ms=latency_ms,
                            provider=self.capability.name,
                        ),
                        provenance=Provenance(
                            tool=self.capability.name,
                            version=self.capability.version,
                            args={"method": method, "url": url},
                            env={},
                            started_at=started_at,
                            completed_at=datetime.now(),
                        ),
                    )

                # Handle response based on content type
                if "application/json" in content_type:
                    artifacts.append(
                        Artifact(
                            type=ArtifactType.JSON,
                            content=response.text,
                            metadata={
                                "status_code": response.status_code,
                                "content_type": content_type,
                                "response_size": response_size,
                            },
                        )
                    )
                elif "text/html" in content_type:
                    artifacts.append(
                        Artifact(
                            type=ArtifactType.HTML,
                            content=response.text,
                            metadata={
                                "status_code": response.status_code,
                                "content_type": content_type,
                                "response_size": response_size,
                            },
                        )
                    )
                else:
                    artifacts.append(
                        Artifact(
                            type=ArtifactType.TEXT,
                            content=response.text,
                            metadata={
                                "status_code": response.status_code,
                                "content_type": content_type,
                                "response_size": response_size,
                            },
                        )
                    )

                # Calculate cost if configured
                cost = self.estimate_cost(task)

                return ResultEnvelope(
                    task_id=task.id,
                    status=TaskStatus.COMPLETED,
                    artifacts=artifacts,
                    diagnostics=Diagnostics(
                        latency_ms=latency_ms,
                        cost_usd=cost,
                        provider=self.capability.name,
                    ),
                    provenance=Provenance(
                        tool=self.capability.name,
                        version=self.capability.version,
                        args={"method": method, "url": url},
                        env={},
                        started_at=started_at,
                        completed_at=datetime.now(),
                    ),
                )

        except httpx.TimeoutException:
            latency_ms = (time.time() - start_time) * 1000
            return ResultEnvelope(
                task_id=task.id,
                status=TaskStatus.TIMEOUT,
                error=f"Request timed out after {timeout}s",
                diagnostics=Diagnostics(latency_ms=latency_ms),
                provenance=Provenance(
                    tool=self.capability.name,
                    version=self.capability.version,
                    args={"method": method, "url": url},
                    env={},
                    started_at=started_at,
                    completed_at=datetime.now(),
                ),
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return ResultEnvelope(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error=f"Request error: {str(e)}",
                diagnostics=Diagnostics(latency_ms=latency_ms),
                provenance=Provenance(
                    tool=self.capability.name,
                    version=self.capability.version,
                    args={"method": method, "url": url},
                    env={},
                    started_at=started_at,
                    completed_at=datetime.now(),
                ),
            )

    async def health_check(self) -> bool:
        """Check if API endpoint is reachable."""
        if not self.base_url and not self.capability.health_endpoint:
            return True  # Can't check without URL

        url = self.capability.health_endpoint or self.base_url

        try:
            async with httpx.AsyncClient(verify=self.verify_ssl, timeout=5.0) as client:
                response = await client.get(url)
