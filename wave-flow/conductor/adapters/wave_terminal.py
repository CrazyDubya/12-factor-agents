"""
Wave Terminal integration adapter.

Provides bidirectional integration with Wave Terminal for:
- Task execution requests from terminal
- Status updates and progress tracking
- Output streaming to terminal
- File system operations
- Security and privacy controls
"""

import asyncio
import sys
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import websockets
import ssl

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


class WaveTerminalAdapter(BaseAdapter):
    """
    Adapter for Wave Terminal integration.
    
    Provides integration with Wave Terminal for task orchestration,
    status updates, and bidirectional communication.
    """
    
    def __init__(
        self,
        capability: ToolCapability,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(capability, config)
        self.ws_url = config.get("ws_url", "ws://localhost:8765") if config else "ws://localhost:8765"
        self.api_token = config.get("api_token") if config else None
        self.connection_timeout = config.get("connection_timeout", 30) if config else 30
        self.terminal_id = config.get("terminal_id", "default") if config else "default"
        self._websocket = None
        self._connected = False
        self._connection_retry_delay = 5  # seconds
        
    async def connect(self) -> bool:
        """Establish connection to Wave Terminal."""
        try:
            # Check if authentication is required
            extra_headers = {}
            if self.api_token:
                extra_headers["Authorization"] = f"Bearer {self.api_token}"
            
            self._websocket = await websockets.connect(
                self.ws_url,
                extra_headers=extra_headers,
                timeout=self.connection_timeout
            )
            
            # Send initial handshake
            handshake_msg = {
                "type": "handshake",
                "terminal_id": self.terminal_id,
                "adapter_version": self.capability.version,
                "capabilities": [intent for intent in self.capability.intents],
                "timestamp": datetime.now().isoformat()
            }
            await self._websocket.send(json.dumps(handshake_msg))
            
            # Wait for handshake response
            response = await asyncio.wait_for(self._websocket.recv(), timeout=10.0)
            response_data = json.loads(response)
            
            if response_data.get("type") == "handshake_ack":
                self._connected = True
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Failed to connect to Wave Terminal: {str(e)}", file=sys.stderr)
            return False
    
    async def disconnect(self):
        """Close connection to Wave Terminal."""
        if self._websocket:
            await self._websocket.close()
            self._connected = False
    
    async def ensure_connection(self) -> bool:
        """Ensure connection to Wave Terminal is active."""
        if self._connected and self._websocket and not self._websocket.closed:
            return True
        
        # Try to reconnect
        success = await self.connect()
        if not success:
            # Retry connection with exponential backoff
            for i in range(3):
                await asyncio.sleep(self._connection_retry_delay * (i + 1))
                success = await self.connect()
                if success:
                    break
        
        return success
    
    async def send_status_update(self, task_id: str, status: str, progress: Optional[float] = None, 
                                message: Optional[str] = None) -> bool:
        """Send status update to Wave Terminal."""
        if not await self.ensure_connection():
            return False
        
        try:
            status_msg = {
                "type": "status_update",
                "task_id": task_id,
                "status": status,
                "progress": progress,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "from_adapter": self.capability.name
            }
            await self._websocket.send(json.dumps(status_msg))
            return True
        except Exception as e:
            print(f"Failed to send status update: {str(e)}", file=sys.stderr)
            self._connected = False
            return False
    
    async def execute(self, task: TaskEnvelope) -> ResultEnvelope:
        """Execute task with Wave Terminal integration."""
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
        
        # Initialize connection if needed
        if not await self.ensure_connection():
            return ResultEnvelope(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error="Unable to connect to Wave Terminal",
            )
        
        # Send task execution request to Wave Terminal
        try:
            task_request = {
                "type": "task_request",
                "task_id": task.id,
                "intent": task.intent,
                "inputs": task.inputs,
                "constraints": task.constraints.to_dict() if hasattr(task.constraints, 'to_dict') else {},
                "timestamp": datetime.now().isoformat()
            }
            
            await self._websocket.send(json.dumps(task_request))
            
            # Send initial status update
            await self.send_status_update(task.id, "started", message="Task started execution")
            
            # Wait for response from Wave Terminal
            response_data = await asyncio.wait_for(
                self._websocket.recv(),
                timeout=task.constraints.deadline_ms / 1000 if task.constraints.deadline_ms else 300.0  # 5 min default
            )
            
            response = json.loads(response_data)
            
            if response.get("type") == "task_result":
                # Process result from Wave Terminal
                status = TaskStatus(response.get("status", "completed"))
                artifacts = []
                
                # Process artifacts from response
                response_artifacts = response.get("artifacts", [])
                for art_data in response_artifacts:
                    artifact = Artifact(
                        type=ArtifactType(art_data["type"]),
                        content=art_data.get("content"),
                        path=art_data.get("path"),
                        metadata=art_data.get("metadata", {}),
                        size_bytes=art_data.get("size_bytes"),
                        checksum=art_data.get("checksum")
                    )
                    artifacts.append(artifact)
                
                # Create result envelope
                result = ResultEnvelope(
                    task_id=task.id,
                    status=status,
                    artifacts=artifacts,
                    diagnostics=Diagnostics(
                        latency_ms=(time.time() - start_time) * 1000,
                        provider=self.capability.name,
                    ),
                    provenance=Provenance(
                        tool=self.capability.name,
                        version=self.capability.version,
                        args={"task_intent": task.intent},
                        env={},
                        started_at=started_at,
                        completed_at=datetime.now(),
                    ),
                    error=response.get("error"),
                    warnings=response.get("warnings", [])
                )
                
                # Send completion status
                await self.send_status_update(
                    task.id, 
                    "completed" if result.is_success() else "failed",
                    progress=100.0,
                    message=f"Task {'completed' if result.is_success() else 'failed'}"
                )
                
                return result
            else:
                # Unexpected response type
                await self.send_status_update(
                    task.id, "failed", message="Unexpected response from Wave Terminal"
                )
                return ResultEnvelope(
                    task_id=task.id,
                    status=TaskStatus.FAILED,
                    error=f"Unexpected response type: {response.get('type')}",
                )
        
        except asyncio.TimeoutError:
            # Send timeout status update
            await self.send_status_update(task.id, "timeout", message="Request timed out")
            latency_ms = (time.time() - start_time) * 1000
            return ResultEnvelope(
                task_id=task.id,
                status=TaskStatus.TIMEOUT,
                error="Wave Terminal request timed out",
                diagnostics=Diagnostics(
                    latency_ms=latency_ms,
                    provider=self.capability.name,
                ),
                provenance=Provenance(
                    tool=self.capability.name,
                    version=self.capability.version,
                    args={"task_intent": task.intent},
                    env={},
                    started_at=started_at,
                    completed_at=datetime.now(),
                ),
            )
        
        except Exception as e:
            # Send error status update
            await self.send_status_update(task.id, "failed", message=f"Execution error: {str(e)}")
            latency_ms = (time.time() - start_time) * 1000
            return ResultEnvelope(
                task_id=task.id,
                status=TaskStatus.FAILED,
                error=f"Wave Terminal execution error: {str(e)}",
                diagnostics=Diagnostics(
                    latency_ms=latency_ms,
                    provider=self.capability.name,
                ),
                provenance=Provenance(
                    tool=self.capability.name,
                    version=self.capability.version,
                    args={"task_intent": task.intent},
                    env={},
                    started_at=started_at,
                    completed_at=datetime.now(),
                ),
            )
    
    async def health_check(self) -> bool:
        """Check if Wave Terminal is accessible."""
        return await self.ensure_connection()
    
    async def send_output_stream(self, task_id: str, output_type: str, content: str) -> bool:
        """Stream output to Wave Terminal."""
        if not await self.ensure_connection():
            return False
        
        try:
            stream_msg = {
                "type": "output_stream",
                "task_id": task_id,
                "output_type": output_type,  # stdout, stderr, progress, etc.
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            await self._websocket.send(json.dumps(stream_msg))
            return True
        except Exception as e:
            print(f"Failed to send output stream: {str(e)}", file=sys.stderr)
            self._connected = False
            return False
    
    def get_terminal_status(self) -> Dict[str, Any]:
        """Get Wave Terminal connection status."""
        return {
            "connected": self._connected,
            "terminal_id": self.terminal_id,
            "last_connection_attempt": getattr(self, '_last_connection_attempt', None),
            "websocket_closed": self._websocket.closed if self._websocket else True,
        }


# Capability definition for Wave Terminal integration
def get_wave_terminal_capability() -> ToolCapability:
    """Get capability definition for Wave Terminal integration."""
    return ToolCapability(
        name="wave-terminal",
        version="1.0.0",
        intents=[
            "terminal-integration", "status-update", "progress-tracking", 
            "output-streaming", "task-execution", "file-operations"
        ],
        input_modes=["websocket"],
        output_modes=["status", "artifacts", "stream"],
        environments=[ExecutionEnvironment.LOCAL],
        privacy_compatible=["internal"],  # Only internal for security
        health_endpoint=None,
        metadata={
            "protocol": "websocket",
            "connection_type": "bidirectional",
            "features": [
                "real-time status updates",
                "progress tracking",
                "output streaming",
                "task orchestration"
            ]
        }
    )