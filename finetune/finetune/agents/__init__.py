"""
Multi-Agent Narrative System

This module contains specialized agents for different aspects of narrative generation:
- WorldBuilder: Creates consistent world rules and settings
- CharacterDesigner: Develops personas with consistent traits
- PlotWeaver: Manages narrative threads and causality
- DocumentWriter: Generates specific document types
- ConsistencyChecker: Validates cross-document coherence
"""

from .base_agent import BaseAgent, AgentResponse
from .world_builder import WorldBuilderAgent
from .character_designer import CharacterDesignerAgent
from .plot_weaver import PlotWeaverAgent
from .document_writer import DocumentWriterAgent
from .consistency_checker import ConsistencyCheckerAgent
from .agent_coordinator import AgentCoordinator

__all__ = [
    "BaseAgent",
    "AgentResponse",
    "WorldBuilderAgent",
    "CharacterDesignerAgent",
    "PlotWeaverAgent",
    "DocumentWriterAgent",
    "ConsistencyCheckerAgent",
    "AgentCoordinator",
]