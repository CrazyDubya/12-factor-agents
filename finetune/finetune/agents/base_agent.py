"""
Base Agent class for the multi-agent narrative system.
"""

import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Union
from enum import Enum

import dspy
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class AgentRole(Enum):
    """Enumeration of agent roles in the narrative system."""
    WORLD_BUILDER = "world_builder"
    CHARACTER_DESIGNER = "character_designer"
    PLOT_WEAVER = "plot_weaver"
    DOCUMENT_WRITER = "document_writer"
    CONSISTENCY_CHECKER = "consistency_checker"

@dataclass
class AgentResponse:
    """Response from an agent operation."""
    success: bool
    content: Any
    metadata: Dict[str, Any] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    agent_role: Optional[AgentRole] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class NarrativeContext(BaseModel):
    """Context shared between agents during narrative generation."""
    world_id: str = Field(description="Unique identifier for the world")
    theme: str = Field(description="Overall theme or genre")
    world_rules: Dict[str, Any] = Field(default_factory=dict, description="Physical and social laws")
    characters: List[Dict[str, Any]] = Field(default_factory=list, description="Character definitions")
    locations: List[Dict[str, Any]] = Field(default_factory=list, description="Location definitions")
    events: List[Dict[str, Any]] = Field(default_factory=list, description="Major events in timeline")
    active_plots: List[Dict[str, Any]] = Field(default_factory=list, description="Ongoing narrative threads")
    generated_documents: List[Dict[str, Any]] = Field(default_factory=list, description="Previously generated documents")
    consistency_rules: Dict[str, Any] = Field(default_factory=dict, description="Rules for maintaining consistency")

    class Config:
        arbitrary_types_allowed = True

class BaseAgent(ABC):
    """
    Abstract base class for all narrative agents.

    Each agent specializes in a specific aspect of narrative generation
    and can interact with other agents through a shared context.
    """

    def __init__(self,
                 role: AgentRole,
                 llm: Optional[dspy.LM] = None,
                 max_retries: int = 3,
                 timeout: int = 300):
        """
        Initialize the base agent.

        Args:
            role: The role this agent plays in the system
            llm: Language model to use for generation
            max_retries: Maximum number of retry attempts
            timeout: Timeout for operations in seconds
        """
        self.role = role
        self.llm = llm or dspy.LM('gpt-3.5-turbo')
        self.max_retries = max_retries
        self.timeout = timeout
        self.logger = logging.getLogger(f"{__name__}.{role.value}")

    @abstractmethod
    def execute(self, context: NarrativeContext, **kwargs) -> AgentResponse:
        """
        Execute the agent's primary function.

        Args:
            context: Shared narrative context
            **kwargs: Additional parameters specific to the agent

        Returns:
            AgentResponse with the result of the operation
        """
        pass

    @abstractmethod
    def validate_input(self, context: NarrativeContext, **kwargs) -> bool:
        """
        Validate that the input context and parameters are valid.

        Args:
            context: Shared narrative context
            **kwargs: Additional parameters

        Returns:
            True if input is valid, False otherwise
        """
        pass

    def execute_with_retry(self, context: NarrativeContext, **kwargs) -> AgentResponse:
        """
        Execute the agent with retry logic.

        Args:
            context: Shared narrative context
            **kwargs: Additional parameters

        Returns:
            AgentResponse with the result of the operation
        """
        start_time = time.time()

        # Validate input
        if not self.validate_input(context, **kwargs):
            return AgentResponse(
                success=False,
                content=None,
                error_message="Invalid input parameters",
                execution_time=time.time() - start_time,
                agent_role=self.role
            )

        last_error = None

        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Executing {self.role.value}, attempt {attempt + 1}/{self.max_retries}")

                # Execute with timeout
                result = self.execute(context, **kwargs)

                if result.success:
                    result.execution_time = time.time() - start_time
                    result.agent_role = self.role
                    self.logger.info(f"Successfully completed {self.role.value}")
                    return result
                else:
                    last_error = result.error_message
                    self.logger.warning(f"Attempt {attempt + 1} failed: {last_error}")

            except Exception as e:
                last_error = str(e)
                self.logger.error(f"Exception in attempt {attempt + 1}: {last_error}")

                if attempt < self.max_retries - 1:
                    # Wait before retry (exponential backoff)
                    wait_time = 2 ** attempt
                    self.logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)

        # All attempts failed
        return AgentResponse(
            success=False,
            content=None,
            error_message=f"All {self.max_retries} attempts failed. Last error: {last_error}",
            execution_time=time.time() - start_time,
            agent_role=self.role
        )

    def update_context(self, context: NarrativeContext, updates: Dict[str, Any]) -> None:
        """
        Update the shared narrative context with new information.

        Args:
            context: Context to update
            updates: Dictionary of updates to apply
        """
        for key, value in updates.items():
            if hasattr(context, key):
                if isinstance(getattr(context, key), list):
                    # For list attributes, extend rather than replace
                    if isinstance(value, list):
                        getattr(context, key).extend(value)
                    else:
                        getattr(context, key).append(value)
                elif isinstance(getattr(context, key), dict):
                    # For dict attributes, update rather than replace
                    getattr(context, key).update(value)
                else:
                    # For other attributes, replace
                    setattr(context, key, value)

    def get_context_summary(self, context: NarrativeContext) -> str:
        """
        Get a summary of the current narrative context.

        Args:
            context: Narrative context to summarize

        Returns:
            String summary of the context
        """
        return f"""
World: {context.world_id} ({context.theme})
Characters: {len(context.characters)}
Locations: {len(context.locations)}
Events: {len(context.events)}
Active Plots: {len(context.active_plots)}
Generated Documents: {len(context.generated_documents)}
"""

    def log_operation(self, operation: str, details: Dict[str, Any] = None):
        """
        Log an operation with details.

        Args:
            operation: Description of the operation
            details: Additional details to log
        """
        if details:
            self.logger.info(f"{operation}: {details}")
        else:
            self.logger.info(operation)