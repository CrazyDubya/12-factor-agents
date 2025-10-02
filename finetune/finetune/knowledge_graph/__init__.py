"""
Knowledge Graph System for Narrative Consistency

This module provides a comprehensive knowledge graph implementation using Neo4j
to track and maintain consistency across all narrative elements including
characters, locations, events, and relationships.

Key Components:
- GraphManager: Core Neo4j database interaction
- EntityTracker: Character and location consistency tracking
- ConsistencyValidator: Cross-document validation
- TemporalManager: Timeline and causality tracking
"""

from .graph_manager import KnowledgeGraphManager
from .entity_tracker import EntityTracker, EntityType, Entity
from .consistency_validator import ConsistencyValidator, ValidationResult
from .temporal_manager import TemporalManager, TimelineEvent

__all__ = [
    "KnowledgeGraphManager",
    "EntityTracker",
    "EntityType",
    "Entity",
    "ConsistencyValidator",
    "ValidationResult",
    "TemporalManager",
    "TimelineEvent",
]