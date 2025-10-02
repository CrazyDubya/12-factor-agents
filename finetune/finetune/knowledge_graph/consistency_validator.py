"""
ConsistencyValidator - Cross-document validation for narrative coherence.

This module provides comprehensive validation of narrative consistency across
all documents in a world, identifying conflicts and suggesting resolutions.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

from .entity_tracker import EntityTracker, Entity, EntityType, EntityMention

logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    WARNING = "warning"

class ValidationType(Enum):
    """Types of validation checks."""
    CHARACTER_CONSISTENCY = "character_consistency"
    LOCATION_CONSISTENCY = "location_consistency"
    TIMELINE_CONSISTENCY = "timeline_consistency"
    WORLD_RULES = "world_rules"
    RELATIONSHIP_CONSISTENCY = "relationship_consistency"
    LOGICAL_COHERENCE = "logical_coherence"

@dataclass
class ValidationResult:
    """Result of a consistency validation check."""
    validation_id: str
    validation_type: ValidationType
    severity: ValidationSeverity
    title: str
    description: str
    affected_entities: List[str]
    affected_documents: List[str]
    evidence: Dict[str, Any]
    suggested_fix: str
    confidence: float
    timestamp: datetime

class ConsistencyValidator:
    """
    Comprehensive validator for narrative consistency across documents.

    This class performs various consistency checks and identifies conflicts
    that could break narrative coherence.
    """

    def __init__(self, entity_tracker: EntityTracker):
        """
        Initialize the consistency validator.

        Args:
            entity_tracker: EntityTracker instance for entity analysis
        """
        self.entity_tracker = entity_tracker
        self.logger = logging.getLogger(__name__)

        # Validation rules and thresholds
        self.validation_config = {
            "character_consistency_threshold": 0.8,
            "location_consistency_threshold": 0.8,
            "timeline_tolerance_days": 1,
            "name_similarity_threshold": 0.9,
            "property_conflict_threshold": 0.7
        }

    def validate_world_consistency(self, world_context: Dict[str, Any],
                                 documents: List[Dict[str, Any]]) -> List[ValidationResult]:
        """
        Perform comprehensive consistency validation for a world.

        Args:
            world_context: World information and rules
            documents: List of all documents to validate

        Returns:
            List of validation results identifying issues
        """
        validation_results = []

        try:
            # Process all documents through entity tracker
            for document in documents:
                self.entity_tracker.process_document(document)

            # Perform different types of validation
            validation_results.extend(self._validate_character_consistency())
            validation_results.extend(self._validate_location_consistency())
            validation_results.extend(self._validate_timeline_consistency(documents))
            validation_results.extend(self._validate_world_rules(world_context, documents))
            validation_results.extend(self._validate_relationship_consistency())
            validation_results.extend(self._validate_logical_coherence(documents))

            # Sort by severity
            validation_results.sort(key=lambda x: self._severity_sort_key(x.severity))

            self.logger.info(f"Completed validation: {len(validation_results)} issues found")

        except Exception as e:
            self.logger.error(f"Error during world consistency validation: {str(e)}")

        return validation_results

    def _validate_character_consistency(self) -> List[ValidationResult]:
        """Validate character consistency across all mentions."""
        results = []

        characters = self.entity_tracker.get_all_entities_of_type(EntityType.CHARACTER)

        for character in characters:
            # Check for property conflicts
            if character.conflicts:
                for conflict in character.conflicts:
                    if conflict["type"] == "property_inconsistency":
                        result = ValidationResult(
                            validation_id=f"char_conflict_{character.entity_id}_{len(results)}",
                            validation_type=ValidationType.CHARACTER_CONSISTENCY,
                            severity=self._map_conflict_severity(conflict.get("severity", "medium")),
                            title=f"Character property conflict: {character.name}",
                            description=f"Conflicting information about {character.name}'s {conflict['property']}: '{conflict['canonical_value']}' vs '{conflict['mentioned_value']}'",
                            affected_entities=[character.entity_id],
                            affected_documents=[conflict["document_id"]],
                            evidence={
                                "property": conflict["property"],
                                "canonical_value": conflict["canonical_value"],
                                "conflicting_value": conflict["mentioned_value"],
                                "character_mentions": len(character.mentions)
                            },
                            suggested_fix=self._suggest_character_fix(character, conflict),
                            confidence=0.8,
                            timestamp=datetime.now()
                        )
                        results.append(result)

            # Check for low consistency scores
            if character.consistency_score < self.validation_config["character_consistency_threshold"]:
                result = ValidationResult(
                    validation_id=f"char_consistency_{character.entity_id}",
                    validation_type=ValidationType.CHARACTER_CONSISTENCY,
                    severity=ValidationSeverity.MAJOR,
                    title=f"Low consistency score: {character.name}",
                    description=f"Character {character.name} has inconsistent portrayal across documents (score: {character.consistency_score:.2f})",
                    affected_entities=[character.entity_id],
                    affected_documents=[mention.document_id for mention in character.mentions],
                    evidence={
                        "consistency_score": character.consistency_score,
                        "mention_count": len(character.mentions),
                        "conflict_count": len(character.conflicts)
                    },
                    suggested_fix="Review character portrayal across documents and establish consistent traits",
                    confidence=0.9,
                    timestamp=datetime.now()
                )
                results.append(result)

            # Check for potential duplicate characters
            similar_characters = self._find_similar_characters(character)
            for similar_char in similar_characters:
                if similar_char.entity_id != character.entity_id:
                    result = ValidationResult(
                        validation_id=f"char_duplicate_{character.entity_id}_{similar_char.entity_id}",
                        validation_type=ValidationType.CHARACTER_CONSISTENCY,
                        severity=ValidationSeverity.MAJOR,
                        title=f"Potential duplicate characters: {character.name} and {similar_char.name}",
                        description=f"Characters '{character.name}' and '{similar_char.name}' may be the same person",
                        affected_entities=[character.entity_id, similar_char.entity_id],
                        affected_documents=list(set([m.document_id for m in character.mentions + similar_char.mentions])),
                        evidence={
                            "similarity_score": self._calculate_character_similarity(character, similar_char),
                            "shared_properties": self._find_shared_properties(character, similar_char)
                        },
                        suggested_fix="Review characters and consider merging if they represent the same person",
                        confidence=0.7,
                        timestamp=datetime.now()
                    )
                    results.append(result)

        return results

    def _validate_location_consistency(self) -> List[ValidationResult]:
        """Validate location consistency across all mentions."""
        results = []

        locations = self.entity_tracker.get_all_entities_of_type(EntityType.LOCATION)

        for location in locations:
            # Check for property conflicts (similar to characters)
            if location.conflicts:
                for conflict in location.conflicts:
                    if conflict["type"] == "property_inconsistency":
                        result = ValidationResult(
                            validation_id=f"loc_conflict_{location.entity_id}_{len(results)}",
                            validation_type=ValidationType.LOCATION_CONSISTENCY,
                            severity=self._map_conflict_severity(conflict.get("severity", "medium")),
                            title=f"Location property conflict: {location.name}",
                            description=f"Conflicting information about {location.name}'s {conflict['property']}",
                            affected_entities=[location.entity_id],
                            affected_documents=[conflict["document_id"]],
                            evidence=conflict,
                            suggested_fix=self._suggest_location_fix(location, conflict),
                            confidence=0.8,
                            timestamp=datetime.now()
                        )
                        results.append(result)

            # Check for geographical inconsistencies
            geo_issues = self._check_geographical_consistency(location)
            for issue in geo_issues:
                result = ValidationResult(
                    validation_id=f"geo_issue_{location.entity_id}_{len(results)}",
                    validation_type=ValidationType.LOCATION_CONSISTENCY,
                    severity=ValidationSeverity.MINOR,
                    title=f"Geographical inconsistency: {location.name}",
                    description=issue["description"],
                    affected_entities=[location.entity_id],
                    affected_documents=issue["documents"],
                    evidence=issue["evidence"],
                    suggested_fix="Review geographical descriptions for consistency",
                    confidence=0.6,
                    timestamp=datetime.now()
                )
                results.append(result)

        return results

    def _validate_timeline_consistency(self, documents: List[Dict[str, Any]]) -> List[ValidationResult]:
        """Validate timeline consistency across documents."""
        results = []

        # Extract temporal references from documents
        temporal_events = self._extract_temporal_events(documents)

        # Check for chronological inconsistencies
        chronology_issues = self._check_chronological_order(temporal_events)

        for issue in chronology_issues:
            result = ValidationResult(
                validation_id=f"timeline_{len(results)}",
                validation_type=ValidationType.TIMELINE_CONSISTENCY,
                severity=ValidationSeverity.MAJOR,
                title="Timeline inconsistency detected",
                description=issue["description"],
                affected_entities=issue["entities"],
                affected_documents=issue["documents"],
                evidence=issue["evidence"],
                suggested_fix="Review and adjust timeline references for chronological consistency",
                confidence=issue["confidence"],
                timestamp=datetime.now()
            )
            results.append(result)

        return results

    def _validate_world_rules(self, world_context: Dict[str, Any],
                            documents: List[Dict[str, Any]]) -> List[ValidationResult]:
        """Validate adherence to established world rules."""
        results = []

        world_rules = world_context.get("world_rules", {})

        if not world_rules:
            return results

        # Check each document for world rule violations
        for document in documents:
            violations = self._check_world_rule_violations(document, world_rules)

            for violation in violations:
                result = ValidationResult(
                    validation_id=f"world_rule_{document['id']}_{len(results)}",
                    validation_type=ValidationType.WORLD_RULES,
                    severity=ValidationSeverity.CRITICAL,
                    title=f"World rule violation in {document['title']}",
                    description=violation["description"],
                    affected_entities=violation.get("entities", []),
                    affected_documents=[document['id']],
                    evidence=violation["evidence"],
                    suggested_fix="Revise content to align with established world rules",
                    confidence=violation["confidence"],
                    timestamp=datetime.now()
                )
                results.append(result)

        return results

    def _validate_relationship_consistency(self) -> List[ValidationResult]:
        """Validate consistency of relationships between entities."""
        results = []

        # Get all character entities
        characters = self.entity_tracker.get_all_entities_of_type(EntityType.CHARACTER)

        # Check for relationship inconsistencies
        for char1 in characters:
            for char2 in characters:
                if char1.entity_id != char2.entity_id:
                    relationship_issues = self._check_relationship_consistency(char1, char2)

                    for issue in relationship_issues:
                        result = ValidationResult(
                            validation_id=f"relationship_{char1.entity_id}_{char2.entity_id}_{len(results)}",
                            validation_type=ValidationType.RELATIONSHIP_CONSISTENCY,
                            severity=ValidationSeverity.MINOR,
                            title=f"Relationship inconsistency: {char1.name} and {char2.name}",
                            description=issue["description"],
                            affected_entities=[char1.entity_id, char2.entity_id],
                            affected_documents=issue["documents"],
                            evidence=issue["evidence"],
                            suggested_fix="Review character interactions and establish consistent relationship dynamics",
                            confidence=0.6,
                            timestamp=datetime.now()
                        )
                        results.append(result)

        return results

    def _validate_logical_coherence(self, documents: List[Dict[str, Any]]) -> List[ValidationResult]:
        """Validate logical coherence across documents."""
        results = []

        # Check for logical contradictions
        for i, doc1 in enumerate(documents):
            for doc2 in documents[i+1:]:
                contradictions = self._find_logical_contradictions(doc1, doc2)

                for contradiction in contradictions:
                    result = ValidationResult(
                        validation_id=f"logic_{doc1['id']}_{doc2['id']}_{len(results)}",
                        validation_type=ValidationType.LOGICAL_COHERENCE,
                        severity=ValidationSeverity.MAJOR,
                        title="Logical contradiction detected",
                        description=contradiction["description"],
                        affected_entities=contradiction.get("entities", []),
                        affected_documents=[doc1['id'], doc2['id']],
                        evidence=contradiction["evidence"],
                        suggested_fix="Review documents and resolve logical contradictions",
                        confidence=contradiction["confidence"],
                        timestamp=datetime.now()
                    )
                    results.append(result)

        return results

    # Helper methods for specific validation checks

    def _find_similar_characters(self, character: Entity) -> List[Entity]:
        """Find characters that might be duplicates of the given character."""
        similar_characters = []
        all_characters = self.entity_tracker.get_all_entities_of_type(EntityType.CHARACTER)

        for other_char in all_characters:
            if other_char.entity_id != character.entity_id:
                similarity = self._calculate_character_similarity(character, other_char)
                if similarity > self.validation_config["name_similarity_threshold"]:
                    similar_characters.append(other_char)

        return similar_characters

    def _calculate_character_similarity(self, char1: Entity, char2: Entity) -> float:
        """Calculate similarity score between two characters."""
        similarity = 0.0

        # Name similarity
        name_sim = self._calculate_string_similarity(char1.name, char2.name)
        similarity += name_sim * 0.4

        # Property similarity
        prop_sim = self._calculate_property_similarity(
            char1.canonical_properties, char2.canonical_properties
        )
        similarity += prop_sim * 0.6

        return similarity

    def _find_shared_properties(self, char1: Entity, char2: Entity) -> Dict[str, Any]:
        """Find properties shared between two characters."""
        shared = {}

        for prop in char1.canonical_properties:
            if prop in char2.canonical_properties:
                if char1.canonical_properties[prop] == char2.canonical_properties[prop]:
                    shared[prop] = char1.canonical_properties[prop]

        return shared

    def _check_geographical_consistency(self, location: Entity) -> List[Dict[str, Any]]:
        """Check for geographical inconsistencies for a location."""
        issues = []

        # This would implement more sophisticated geographical consistency checks
        # For now, return empty list as placeholder
        return issues

    def _extract_temporal_events(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract temporal events and references from documents."""
        events = []

        for document in documents:
            # Simple temporal extraction - would be more sophisticated in practice
            content_lower = document['content'].lower()

            # Look for temporal indicators
            if 'before' in content_lower or 'after' in content_lower:
                events.append({
                    'document_id': document['id'],
                    'content_snippet': document['content'][:200],
                    'temporal_indicators': ['before', 'after']
                })

        return events

    def _check_chronological_order(self, temporal_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for chronological inconsistencies in temporal events."""
        issues = []

        # Placeholder for chronological consistency checking
        # This would analyze temporal relationships and identify contradictions

        return issues

    def _check_world_rule_violations(self, document: Dict[str, Any],
                                   world_rules: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check a document for violations of world rules."""
        violations = []

        # Simple rule checking - would be more sophisticated in practice
        content_lower = document['content'].lower()

        # Check magic system rules
        if 'magic' in world_rules:
            magic_rules = world_rules['magic']
            if isinstance(magic_rules, str) and 'forbidden' in magic_rules.lower():
                if 'magic' in content_lower:
                    violations.append({
                        'description': f"Document mentions magic but world rules indicate magic is forbidden",
                        'evidence': {'rule': magic_rules, 'content_snippet': document['content'][:200]},
                        'confidence': 0.7
                    })

        return violations

    def _check_relationship_consistency(self, char1: Entity, char2: Entity) -> List[Dict[str, Any]]:
        """Check for relationship inconsistencies between two characters."""
        issues = []

        # Analyze mentions of both characters in same documents
        shared_documents = set()

        for mention1 in char1.mentions:
            for mention2 in char2.mentions:
                if mention1.document_id == mention2.document_id:
                    shared_documents.add(mention1.document_id)

        # Placeholder for relationship analysis
        # This would analyze interaction patterns and detect inconsistencies

        return issues

    def _find_logical_contradictions(self, doc1: Dict[str, Any],
                                   doc2: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find logical contradictions between two documents."""
        contradictions = []

        # Simple contradiction detection - would be more sophisticated in practice
        # This would analyze statements that directly contradict each other

        return contradictions

    def _map_conflict_severity(self, severity_str: str) -> ValidationSeverity:
        """Map string severity to ValidationSeverity enum."""
        mapping = {
            'critical': ValidationSeverity.CRITICAL,
            'high': ValidationSeverity.MAJOR,
            'major': ValidationSeverity.MAJOR,
            'medium': ValidationSeverity.MINOR,
            'minor': ValidationSeverity.MINOR,
            'low': ValidationSeverity.WARNING
        }

        return mapping.get(severity_str.lower(), ValidationSeverity.MINOR)

    def _severity_sort_key(self, severity: ValidationSeverity) -> int:
        """Get sort key for severity (higher number = more severe)."""
        severity_order = {
            ValidationSeverity.CRITICAL: 4,
            ValidationSeverity.MAJOR: 3,
            ValidationSeverity.MINOR: 2,
            ValidationSeverity.WARNING: 1
        }

        return severity_order.get(severity, 0)

    def _suggest_character_fix(self, character: Entity, conflict: Dict[str, Any]) -> str:
        """Suggest a fix for a character consistency issue."""
        property_name = conflict.get('property', 'unknown')

        if property_name in ['name', 'title']:
            return f"Standardize {character.name}'s {property_name} across all documents"
        elif property_name in ['age_category', 'role']:
            return f"Review {character.name}'s {property_name} and ensure consistency with character development"
        else:
            return f"Reconcile conflicting information about {character.name}'s {property_name}"

    def _suggest_location_fix(self, location: Entity, conflict: Dict[str, Any]) -> str:
        """Suggest a fix for a location consistency issue."""
        property_name = conflict.get('property', 'unknown')
        return f"Standardize descriptions of {location.name}'s {property_name} across all mentions"

    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings."""
        # Simple similarity based on common words
        words1 = set(str1.lower().split())
        words2 = set(str2.lower().split())

        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _calculate_property_similarity(self, props1: Dict[str, Any], props2: Dict[str, Any]) -> float:
        """Calculate similarity between two property dictionaries."""
        if not props1 and not props2:
            return 1.0
        if not props1 or not props2:
            return 0.0

        common_keys = set(props1.keys()).intersection(set(props2.keys()))
        if not common_keys:
            return 0.0

        matching_values = sum(1 for key in common_keys if props1[key] == props2[key])
        return matching_values / len(common_keys)

    def get_validation_summary(self, validation_results: List[ValidationResult]) -> Dict[str, Any]:
        """Get a summary of validation results."""
        summary = {
            'total_issues': len(validation_results),
            'by_severity': {},
            'by_type': {},
            'affected_documents': set(),
            'affected_entities': set()
        }

        for result in validation_results:
            # Count by severity
            severity_key = result.severity.value
            summary['by_severity'][severity_key] = summary['by_severity'].get(severity_key, 0) + 1

            # Count by type
            type_key = result.validation_type.value
            summary['by_type'][type_key] = summary['by_type'].get(type_key, 0) + 1

            # Collect affected items
            summary['affected_documents'].update(result.affected_documents)
            summary['affected_entities'].update(result.affected_entities)

        # Convert sets to counts
        summary['affected_documents'] = len(summary['affected_documents'])
        summary['affected_entities'] = len(summary['affected_entities'])

        return summary