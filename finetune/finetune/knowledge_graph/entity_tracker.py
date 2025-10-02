"""
EntityTracker - Character and location consistency tracking.

This module provides sophisticated tracking of entities (characters, locations,
objects) across documents to maintain narrative consistency and detect conflicts.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from collections import defaultdict

logger = logging.getLogger(__name__)

class EntityType(Enum):
    """Types of entities tracked in the narrative."""
    CHARACTER = "character"
    LOCATION = "location"
    OBJECT = "object"
    ORGANIZATION = "organization"
    EVENT = "event"
    CONCEPT = "concept"

@dataclass
class EntityMention:
    """Represents a mention of an entity in a document."""
    document_id: str
    document_type: str
    mention_text: str
    context: str  # Surrounding text for context
    position: int  # Character position in document
    confidence: float  # Confidence that this is the correct entity
    properties: Dict[str, Any]  # Properties mentioned about the entity

@dataclass
class Entity:
    """Represents a tracked entity in the narrative."""
    entity_id: str
    entity_type: EntityType
    name: str
    aliases: Set[str]
    canonical_properties: Dict[str, Any]
    mentions: List[EntityMention]
    first_appearance: str  # Document ID where first mentioned
    last_appearance: str   # Document ID where last mentioned
    consistency_score: float
    conflicts: List[Dict[str, Any]]

class EntityTracker:
    """
    Tracks entities across documents for consistency validation.

    This class maintains a comprehensive database of all entities mentioned
    across documents and validates that their properties remain consistent.
    """

    def __init__(self):
        """Initialize the entity tracker."""
        self.entities: Dict[str, Entity] = {}
        self.entity_name_index: Dict[str, Set[str]] = defaultdict(set)  # name -> entity_ids
        self.document_entities: Dict[str, Set[str]] = defaultdict(set)  # doc_id -> entity_ids
        self.logger = logging.getLogger(__name__)

    def process_document(self, document: Dict[str, Any]) -> List[EntityMention]:
        """
        Process a document to extract and track entity mentions.

        Args:
            document: Document data to process

        Returns:
            List of entity mentions found in the document
        """
        mentions = []

        try:
            doc_id = document['id']
            doc_type = document['type']
            content = document['content']

            # Extract entity mentions from content
            character_mentions = self._extract_character_mentions(content, doc_id, doc_type)
            location_mentions = self._extract_location_mentions(content, doc_id, doc_type)
            object_mentions = self._extract_object_mentions(content, doc_id, doc_type)

            all_mentions = character_mentions + location_mentions + object_mentions

            # Process each mention
            for mention in all_mentions:
                entity = self._process_mention(mention)
                if entity:
                    mentions.append(mention)
                    self.document_entities[doc_id].add(entity.entity_id)

            self.logger.info(f"Processed {len(mentions)} entity mentions in document {document['title']}")

        except Exception as e:
            self.logger.error(f"Error processing document {document.get('id', 'unknown')}: {str(e)}")

        return mentions

    def _extract_character_mentions(self, content: str, doc_id: str, doc_type: str) -> List[EntityMention]:
        """Extract character mentions from document content."""
        mentions = []

        # Simple name extraction - in practice would use NER or more sophisticated methods
        import re

        # Look for capitalized names (simplified approach)
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        matches = re.finditer(name_pattern, content)

        for match in matches:
            name = match.group(1)

            # Filter out common non-name words
            if self._is_likely_name(name):
                # Get context around the mention
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end]

                # Extract properties from context
                properties = self._extract_character_properties(name, context)

                mention = EntityMention(
                    document_id=doc_id,
                    document_type=doc_type,
                    mention_text=name,
                    context=context,
                    position=match.start(),
                    confidence=self._calculate_name_confidence(name, context),
                    properties=properties
                )

                mentions.append(mention)

        return mentions

    def _extract_location_mentions(self, content: str, doc_id: str, doc_type: str) -> List[EntityMention]:
        """Extract location mentions from document content."""
        mentions = []

        # Look for location patterns like "in [Place]", "at [Place]", etc.
        import re

        location_patterns = [
            r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\bat\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\bfrom\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\bto\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\bthe\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]

        for pattern in location_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)

            for match in matches:
                location = match.group(1)

                if self._is_likely_location(location):
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end]

                    properties = self._extract_location_properties(location, context)

                    mention = EntityMention(
                        document_id=doc_id,
                        document_type=doc_type,
                        mention_text=location,
                        context=context,
                        position=match.start(),
                        confidence=self._calculate_location_confidence(location, context),
                        properties=properties
                    )

                    mentions.append(mention)

        return mentions

    def _extract_object_mentions(self, content: str, doc_id: str, doc_type: str) -> List[EntityMention]:
        """Extract object mentions from document content."""
        mentions = []

        # Look for significant objects mentioned in documents
        import re

        # Common object patterns
        object_patterns = [
            r'\bthe\s+(sword|crown|ring|amulet|book|scroll|map|key|gem|artifact|weapon|armor)\b',
            r'\ba\s+(legendary|magical|ancient|sacred|cursed)\s+([a-z]+)',
        ]

        for pattern in object_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)

            for match in matches:
                obj_name = match.group().strip()

                if len(obj_name) > 3:  # Filter very short matches
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end]

                    properties = self._extract_object_properties(obj_name, context)

                    mention = EntityMention(
                        document_id=doc_id,
                        document_type=doc_type,
                        mention_text=obj_name,
                        context=context,
                        position=match.start(),
                        confidence=self._calculate_object_confidence(obj_name, context),
                        properties=properties
                    )

                    mentions.append(mention)

        return mentions

    def _process_mention(self, mention: EntityMention) -> Optional[Entity]:
        """Process a mention and update or create the corresponding entity."""

        # Determine entity type based on mention characteristics
        entity_type = self._determine_entity_type(mention)

        # Try to find existing entity
        entity_id = self._find_or_create_entity(mention, entity_type)

        if entity_id:
            entity = self.entities[entity_id]

            # Add this mention to the entity
            entity.mentions.append(mention)
            entity.last_appearance = mention.document_id

            # Update canonical properties
            self._update_canonical_properties(entity, mention)

            # Check for consistency conflicts
            conflicts = self._check_mention_consistency(entity, mention)
            entity.conflicts.extend(conflicts)

            # Update consistency score
            entity.consistency_score = self._calculate_consistency_score(entity)

            return entity

        return None

    def _find_or_create_entity(self, mention: EntityMention, entity_type: EntityType) -> Optional[str]:
        """Find an existing entity for this mention or create a new one."""

        mention_text = mention.mention_text.lower()

        # Look for exact name match
        if mention_text in self.entity_name_index:
            possible_entities = self.entity_name_index[mention_text]

            # Find best matching entity
            best_entity_id = None
            best_score = 0.0

            for entity_id in possible_entities:
                entity = self.entities[entity_id]
                if entity.entity_type == entity_type:
                    similarity = self._calculate_entity_similarity(entity, mention)
                    if similarity > best_score and similarity > 0.7:  # Threshold for match
                        best_score = similarity
                        best_entity_id = entity_id

            if best_entity_id:
                return best_entity_id

        # Look for alias matches
        for entity_id, entity in self.entities.items():
            if entity.entity_type == entity_type:
                for alias in entity.aliases:
                    if alias.lower() == mention_text:
                        return entity_id

        # Create new entity
        entity_id = self._generate_entity_id(mention, entity_type)
        entity = Entity(
            entity_id=entity_id,
            entity_type=entity_type,
            name=mention.mention_text,
            aliases=set(),
            canonical_properties={},
            mentions=[],
            first_appearance=mention.document_id,
            last_appearance=mention.document_id,
            consistency_score=1.0,
            conflicts=[]
        )

        self.entities[entity_id] = entity
        self.entity_name_index[mention_text].add(entity_id)

        self.logger.info(f"Created new {entity_type.value} entity: {mention.mention_text}")

        return entity_id

    def _determine_entity_type(self, mention: EntityMention) -> EntityType:
        """Determine the type of entity based on mention characteristics."""

        mention_lower = mention.mention_text.lower()
        context_lower = mention.context.lower()

        # Character indicators
        character_indicators = ['said', 'spoke', 'thought', 'felt', 'walked', 'ran', 'looked']
        if any(indicator in context_lower for indicator in character_indicators):
            return EntityType.CHARACTER

        # Location indicators
        location_indicators = ['in', 'at', 'from', 'to', 'place', 'city', 'town', 'castle', 'forest']
        if any(indicator in context_lower for indicator in location_indicators):
            return EntityType.LOCATION

        # Object indicators
        object_indicators = ['held', 'carried', 'used', 'wore', 'found', 'lost', 'sword', 'ring', 'book']
        if any(indicator in context_lower for indicator in object_indicators):
            return EntityType.OBJECT

        # Default to character if capitalized like a name
        if mention.mention_text[0].isupper():
            return EntityType.CHARACTER

        return EntityType.CONCEPT

    def _update_canonical_properties(self, entity: Entity, mention: EntityMention):
        """Update the canonical properties of an entity based on a new mention."""

        for prop_name, prop_value in mention.properties.items():
            if prop_name not in entity.canonical_properties:
                # New property - add it
                entity.canonical_properties[prop_name] = prop_value
            else:
                # Existing property - check for conflicts
                existing_value = entity.canonical_properties[prop_name]
                if existing_value != prop_value:
                    # Property conflict detected
                    conflict = {
                        "type": "property_conflict",
                        "property": prop_name,
                        "existing_value": existing_value,
                        "new_value": prop_value,
                        "document_id": mention.document_id,
                        "confidence": mention.confidence
                    }

                    # Decide which value to keep based on confidence
                    if mention.confidence > 0.8:
                        entity.canonical_properties[prop_name] = prop_value

    def _check_mention_consistency(self, entity: Entity, mention: EntityMention) -> List[Dict[str, Any]]:
        """Check if a mention is consistent with the entity's established properties."""

        conflicts = []

        # Check property consistency
        for prop_name, prop_value in mention.properties.items():
            if prop_name in entity.canonical_properties:
                canonical_value = entity.canonical_properties[prop_name]

                # Check for direct conflicts
                if canonical_value != prop_value:
                    conflicts.append({
                        "type": "property_inconsistency",
                        "property": prop_name,
                        "canonical_value": canonical_value,
                        "mentioned_value": prop_value,
                        "document_id": mention.document_id,
                        "severity": "high" if prop_name in ["name", "type", "role"] else "medium"
                    })

        # Check temporal consistency (if applicable)
        # This would check if events/states are logically consistent across mentions

        return conflicts

    def _calculate_consistency_score(self, entity: Entity) -> float:
        """Calculate a consistency score for an entity based on its mentions and conflicts."""

        if not entity.mentions:
            return 1.0

        # Base score
        score = 1.0

        # Penalize for conflicts
        conflict_penalty = 0.0
        for conflict in entity.conflicts:
            severity = conflict.get("severity", "medium")
            if severity == "high":
                conflict_penalty += 0.3
            elif severity == "medium":
                conflict_penalty += 0.1
            else:
                conflict_penalty += 0.05

        score -= min(conflict_penalty, 0.8)  # Cap penalty at 0.8

        # Reward for consistent mentions
        if len(entity.mentions) > 1:
            consistency_bonus = 0.1 * min(len(entity.mentions) - 1, 5) / 5
            score += consistency_bonus

        return max(0.0, min(1.0, score))

    def get_entity_inconsistencies(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get all inconsistencies for a specific entity."""

        if entity_id not in self.entities:
            return []

        entity = self.entities[entity_id]
        return entity.conflicts

    def get_document_entities(self, document_id: str) -> List[Entity]:
        """Get all entities mentioned in a specific document."""

        if document_id not in self.document_entities:
            return []

        entity_ids = self.document_entities[document_id]
        return [self.entities[entity_id] for entity_id in entity_ids if entity_id in self.entities]

    def find_entity_by_name(self, name: str, entity_type: EntityType = None) -> List[Entity]:
        """Find entities by name, optionally filtered by type."""

        name_lower = name.lower()
        entities = []

        if name_lower in self.entity_name_index:
            for entity_id in self.entity_name_index[name_lower]:
                entity = self.entities[entity_id]
                if entity_type is None or entity.entity_type == entity_type:
                    entities.append(entity)

        return entities

    def get_all_entities_of_type(self, entity_type: EntityType) -> List[Entity]:
        """Get all entities of a specific type."""

        return [entity for entity in self.entities.values() if entity.entity_type == entity_type]

    def merge_entities(self, entity_id1: str, entity_id2: str) -> bool:
        """Merge two entities that have been determined to be the same."""

        if entity_id1 not in self.entities or entity_id2 not in self.entities:
            return False

        entity1 = self.entities[entity_id1]
        entity2 = self.entities[entity_id2]

        # Merge mentions
        entity1.mentions.extend(entity2.mentions)

        # Merge aliases
        entity1.aliases.update(entity2.aliases)
        entity1.aliases.add(entity2.name)

        # Merge properties (prefer entity1's canonical properties)
        for prop_name, prop_value in entity2.canonical_properties.items():
            if prop_name not in entity1.canonical_properties:
                entity1.canonical_properties[prop_name] = prop_value

        # Update appearances
        if entity2.first_appearance < entity1.first_appearance:
            entity1.first_appearance = entity2.first_appearance

        if entity2.last_appearance > entity1.last_appearance:
            entity1.last_appearance = entity2.last_appearance

        # Merge conflicts
        entity1.conflicts.extend(entity2.conflicts)

        # Update index
        for name in [entity2.name.lower()] + [alias.lower() for alias in entity2.aliases]:
            if name in self.entity_name_index:
                self.entity_name_index[name].discard(entity_id2)
                self.entity_name_index[name].add(entity_id1)

        # Update document entities
        for doc_id, entity_ids in self.document_entities.items():
            if entity_id2 in entity_ids:
                entity_ids.discard(entity_id2)
                entity_ids.add(entity_id1)

        # Remove merged entity
        del self.entities[entity_id2]

        # Recalculate consistency score
        entity1.consistency_score = self._calculate_consistency_score(entity1)

        self.logger.info(f"Merged entities: {entity1.name} and {entity2.name}")

        return True

    # Helper methods for entity extraction and analysis

    def _is_likely_name(self, text: str) -> bool:
        """Check if text is likely a character name."""
        common_words = {'The', 'This', 'That', 'These', 'Those', 'When', 'Where', 'What', 'Why', 'How', 'And', 'But', 'Or', 'With', 'For', 'From'}
        return text not in common_words and len(text) > 2

    def _is_likely_location(self, text: str) -> bool:
        """Check if text is likely a location name."""
        return len(text) > 2 and not text.lower() in ['the', 'and', 'but', 'for', 'with']

    def _extract_character_properties(self, name: str, context: str) -> Dict[str, Any]:
        """Extract character properties from context."""
        properties = {}

        context_lower = context.lower()

        # Simple property extraction
        if 'king' in context_lower or 'queen' in context_lower:
            properties['title'] = 'royalty'
        elif 'lord' in context_lower or 'lady' in context_lower:
            properties['title'] = 'nobility'
        elif 'captain' in context_lower:
            properties['title'] = 'military'

        # Age indicators
        if 'young' in context_lower or 'child' in context_lower:
            properties['age_category'] = 'young'
        elif 'old' in context_lower or 'elder' in context_lower:
            properties['age_category'] = 'old'

        return properties

    def _extract_location_properties(self, location: str, context: str) -> Dict[str, Any]:
        """Extract location properties from context."""
        properties = {}

        context_lower = context.lower()

        # Location type
        if 'city' in context_lower or 'town' in context_lower:
            properties['type'] = 'settlement'
        elif 'castle' in context_lower or 'fortress' in context_lower:
            properties['type'] = 'structure'
        elif 'forest' in context_lower or 'woods' in context_lower:
            properties['type'] = 'wilderness'

        return properties

    def _extract_object_properties(self, obj_name: str, context: str) -> Dict[str, Any]:
        """Extract object properties from context."""
        properties = {}

        context_lower = context.lower()

        # Object type and properties
        if 'magical' in context_lower or 'enchanted' in context_lower:
            properties['magical'] = True
        if 'ancient' in context_lower or 'old' in context_lower:
            properties['age'] = 'ancient'
        if 'valuable' in context_lower or 'precious' in context_lower:
            properties['value'] = 'high'

        return properties

    def _calculate_name_confidence(self, name: str, context: str) -> float:
        """Calculate confidence that a text is a character name."""
        confidence = 0.5  # Base confidence

        # Capitalization helps
        if name[0].isupper():
            confidence += 0.2

        # Context clues
        context_lower = context.lower()
        if any(word in context_lower for word in ['said', 'spoke', 'thought']):
            confidence += 0.2

        return min(1.0, confidence)

    def _calculate_location_confidence(self, location: str, context: str) -> float:
        """Calculate confidence that a text is a location."""
        confidence = 0.5

        context_lower = context.lower()
        if any(prep in context_lower for prep in ['in', 'at', 'from', 'to']):
            confidence += 0.3

        return min(1.0, confidence)

    def _calculate_object_confidence(self, obj_name: str, context: str) -> float:
        """Calculate confidence that a text is an object."""
        confidence = 0.6

        context_lower = context.lower()
        if any(verb in context_lower for verb in ['held', 'carried', 'used']):
            confidence += 0.2

        return min(1.0, confidence)

    def _calculate_entity_similarity(self, entity: Entity, mention: EntityMention) -> float:
        """Calculate similarity between an entity and a mention."""
        similarity = 0.0

        # Name similarity
        if entity.name.lower() == mention.mention_text.lower():
            similarity += 0.5

        # Property similarity
        common_props = set(entity.canonical_properties.keys()) & set(mention.properties.keys())
        if common_props:
            matching_props = sum(1 for prop in common_props
                               if entity.canonical_properties[prop] == mention.properties[prop])
            similarity += 0.3 * (matching_props / len(common_props))

        return similarity

    def _generate_entity_id(self, mention: EntityMention, entity_type: EntityType) -> str:
        """Generate a unique ID for a new entity."""
        base_name = mention.mention_text.lower().replace(' ', '_')
        return f"{entity_type.value}_{base_name}_{len(self.entities)}"