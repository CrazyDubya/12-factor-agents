"""
TemporalManager - Timeline and causality tracking for narrative consistency.

This module manages temporal relationships, event sequences, and causality
chains to ensure chronological consistency across all narrative documents.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)

class TimelineEventType(Enum):
    """Types of timeline events."""
    BIRTH = "birth"
    DEATH = "death"
    MEETING = "meeting"
    CONFLICT = "conflict"
    DISCOVERY = "discovery"
    TRAVEL = "travel"
    POLITICAL = "political"
    NATURAL = "natural"
    CULTURAL = "cultural"
    PERSONAL = "personal"

class TemporalRelationType(Enum):
    """Types of temporal relationships between events."""
    BEFORE = "before"
    AFTER = "after"
    DURING = "during"
    CAUSES = "causes"
    ENABLES = "enables"
    PREVENTS = "prevents"
    SIMULTANEOUS = "simultaneous"

@dataclass
class TimelineEvent:
    """Represents an event in the narrative timeline."""
    event_id: str
    event_type: TimelineEventType
    title: str
    description: str
    participants: List[str]  # Entity IDs involved
    location: Optional[str]  # Location ID where event occurred
    timestamp: Optional[datetime]  # Absolute timestamp if known
    relative_time: Optional[str]  # Relative time description (e.g., "three days later")
    duration: Optional[timedelta]  # How long the event lasted
    source_document: str  # Document where this event was mentioned
    confidence: float  # Confidence in event details
    consequences: List[str]  # Other events this event leads to
    prerequisites: List[str]  # Events that must happen before this one
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TemporalRelation:
    """Represents a temporal relationship between events."""
    relation_id: str
    relation_type: TemporalRelationType
    source_event: str
    target_event: str
    confidence: float
    evidence: str  # Text evidence for this relationship
    source_document: str

class TemporalManager:
    """
    Manages timeline and causality tracking for narrative consistency.

    This class maintains a comprehensive timeline of all events mentioned
    across documents and validates temporal consistency.
    """

    def __init__(self):
        """Initialize the temporal manager."""
        self.events: Dict[str, TimelineEvent] = {}
        self.relations: Dict[str, TemporalRelation] = {}
        self.timeline_cache: Optional[List[TimelineEvent]] = None
        self.causality_graph: Dict[str, Set[str]] = {}  # event_id -> set of caused events
        self.logger = logging.getLogger(__name__)

    def process_document_for_events(self, document: Dict[str, Any]) -> List[TimelineEvent]:
        """
        Extract timeline events from a document.

        Args:
            document: Document to process for temporal information

        Returns:
            List of timeline events found in the document
        """
        extracted_events = []

        try:
            doc_id = document['id']
            content = document['content']
            doc_type = document['type']

            # Extract events based on document type
            if doc_type == 'chronicle':
                events = self._extract_chronicle_events(document)
            elif doc_type == 'diary':
                events = self._extract_diary_events(document)
            elif doc_type == 'letter':
                events = self._extract_letter_events(document)
            elif doc_type == 'report':
                events = self._extract_report_events(document)
            else:
                events = self._extract_general_events(document)

            # Process and add events
            for event_data in events:
                event = self._create_timeline_event(event_data, doc_id)
                if event:
                    self.events[event.event_id] = event
                    extracted_events.append(event)

            # Extract temporal relations
            relations = self._extract_temporal_relations(document, extracted_events)
            for relation in relations:
                self.relations[relation.relation_id] = relation

            # Invalidate timeline cache
            self.timeline_cache = None

            self.logger.info(f"Extracted {len(extracted_events)} events and {len(relations)} relations from {document['title']}")

        except Exception as e:
            self.logger.error(f"Error processing document for events: {str(e)}")

        return extracted_events

    def _extract_chronicle_events(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract events from a chronicle document."""
        events = []
        content = document['content']

        # Look for historical events and dates
        import re

        # Pattern for historical events
        event_patterns = [
            r'In\s+(\d+),\s+(.+?)(?:\.|$)',  # "In 1234, something happened"
            r'During\s+(.+?),\s+(.+?)(?:\.|$)',  # "During the war, something happened"
            r'(\d+)\s+years?\s+(?:ago|later),\s+(.+?)(?:\.|$)',  # "3 years ago, something happened"
        ]

        for pattern in event_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                time_ref = match.group(1)
                event_desc = match.group(2)

                events.append({
                    'title': event_desc[:50] + "..." if len(event_desc) > 50 else event_desc,
                    'description': event_desc,
                    'time_reference': time_ref,
                    'event_type': TimelineEventType.POLITICAL,  # Default for chronicles
                    'context': match.group(0)
                })

        return events

    def _extract_diary_events(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract events from a diary document."""
        events = []
        content = document['content']

        # Look for personal events and reflections
        import re

        # Pattern for diary events
        event_patterns = [
            r'Today\s+(.+?)(?:\.|$)',  # "Today I did something"
            r'Yesterday\s+(.+?)(?:\.|$)',  # "Yesterday something happened"
            r'I\s+(met|saw|found|discovered)\s+(.+?)(?:\.|$)',  # "I met someone"
        ]

        for pattern in event_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                event_desc = match.group(1) if match.lastindex == 1 else f"{match.group(1)} {match.group(2)}"

                events.append({
                    'title': event_desc[:50] + "..." if len(event_desc) > 50 else event_desc,
                    'description': event_desc,
                    'time_reference': 'recent',
                    'event_type': TimelineEventType.PERSONAL,
                    'context': match.group(0)
                })

        return events

    def _extract_letter_events(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract events from a letter document."""
        events = []
        content = document['content']

        # Look for news and recent events mentioned in letters
        import re

        # Pattern for events mentioned in letters
        event_patterns = [
            r'(?:heard|learned|discovered)\s+that\s+(.+?)(?:\.|$)',  # "I heard that something happened"
            r'(?:news|word)\s+of\s+(.+?)(?:\.|$)',  # "news of something"
            r'(?:recently|lately)\s+(.+?)(?:\.|$)',  # "recently something happened"
        ]

        for pattern in event_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                event_desc = match.group(1)

                events.append({
                    'title': event_desc[:50] + "..." if len(event_desc) > 50 else event_desc,
                    'description': event_desc,
                    'time_reference': 'recent',
                    'event_type': TimelineEventType.CULTURAL,  # Default for news
                    'context': match.group(0)
                })

        return events

    def _extract_report_events(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract events from a report document."""
        events = []
        content = document['content']

        # Look for factual events and observations
        import re

        # Pattern for reported events
        event_patterns = [
            r'(?:observed|witnessed|recorded)\s+(.+?)(?:\.|$)',  # "observed something"
            r'(?:event|incident|occurrence)\s+(?:of|involving)\s+(.+?)(?:\.|$)',  # "event of something"
            r'(?:confirmed|verified)\s+that\s+(.+?)(?:\.|$)',  # "confirmed that something"
        ]

        for pattern in event_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                event_desc = match.group(1)

                events.append({
                    'title': event_desc[:50] + "..." if len(event_desc) > 50 else event_desc,
                    'description': event_desc,
                    'time_reference': 'recent',
                    'event_type': TimelineEventType.NATURAL,  # Default for reports
                    'context': match.group(0)
                })

        return events

    def _extract_general_events(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract events from any document type using general patterns."""
        events = []
        content = document['content']

        # Look for general event indicators
        import re

        # General event patterns
        event_patterns = [
            r'(?:battle|war|conflict)\s+(?:of|at|in)\s+(.+?)(?:\.|$)',  # battles
            r'(?:death|birth|marriage)\s+of\s+(.+?)(?:\.|$)',  # life events
            r'(?:discovery|invention|creation)\s+of\s+(.+?)(?:\.|$)',  # discoveries
            r'(?:journey|travel|voyage)\s+(?:to|from)\s+(.+?)(?:\.|$)',  # travels
        ]

        for pattern in event_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                event_desc = match.group(0)
                subject = match.group(1)

                # Determine event type from pattern
                if 'battle' in event_desc.lower() or 'war' in event_desc.lower():
                    event_type = TimelineEventType.CONFLICT
                elif 'death' in event_desc.lower():
                    event_type = TimelineEventType.DEATH
                elif 'birth' in event_desc.lower():
                    event_type = TimelineEventType.BIRTH
                elif 'discovery' in event_desc.lower():
                    event_type = TimelineEventType.DISCOVERY
                elif 'journey' in event_desc.lower() or 'travel' in event_desc.lower():
                    event_type = TimelineEventType.TRAVEL
                else:
                    event_type = TimelineEventType.CULTURAL

                events.append({
                    'title': f"{event_type.value.title()}: {subject}",
                    'description': event_desc,
                    'time_reference': 'unknown',
                    'event_type': event_type,
                    'context': event_desc
                })

        return events

    def _create_timeline_event(self, event_data: Dict[str, Any], source_doc: str) -> Optional[TimelineEvent]:
        """Create a TimelineEvent object from extracted event data."""

        try:
            event_id = f"event_{source_doc}_{hash(event_data['description']) % 10000}"

            # Parse time reference
            timestamp = self._parse_time_reference(event_data.get('time_reference', 'unknown'))

            # Extract participants (simplified)
            participants = self._extract_participants(event_data['description'])

            event = TimelineEvent(
                event_id=event_id,
                event_type=event_data.get('event_type', TimelineEventType.CULTURAL),
                title=event_data['title'],
                description=event_data['description'],
                participants=participants,
                location=None,  # Would be extracted from context
                timestamp=timestamp,
                relative_time=event_data.get('time_reference'),
                duration=None,
                source_document=source_doc,
                confidence=0.7,  # Default confidence
                consequences=[],
                prerequisites=[]
            )

            return event

        except Exception as e:
            self.logger.error(f"Error creating timeline event: {str(e)}")
            return None

    def _extract_temporal_relations(self, document: Dict[str, Any],
                                  events: List[TimelineEvent]) -> List[TemporalRelation]:
        """Extract temporal relationships between events."""
        relations = []

        content = document['content']

        # Look for temporal connectors
        import re

        temporal_patterns = [
            (r'before\s+(.+?),\s+(.+?)(?:\.|$)', TemporalRelationType.BEFORE),
            (r'after\s+(.+?),\s+(.+?)(?:\.|$)', TemporalRelationType.AFTER),
            (r'during\s+(.+?),\s+(.+?)(?:\.|$)', TemporalRelationType.DURING),
            (r'(.+?)\s+caused\s+(.+?)(?:\.|$)', TemporalRelationType.CAUSES),
            (r'(.+?)\s+led\s+to\s+(.+?)(?:\.|$)', TemporalRelationType.CAUSES),
        ]

        for pattern, relation_type in temporal_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)

            for match in matches:
                first_event_desc = match.group(1)
                second_event_desc = match.group(2)

                # Try to match to extracted events
                source_event = self._find_matching_event(first_event_desc, events)
                target_event = self._find_matching_event(second_event_desc, events)

                if source_event and target_event:
                    relation_id = f"rel_{source_event.event_id}_{target_event.event_id}"

                    relation = TemporalRelation(
                        relation_id=relation_id,
                        relation_type=relation_type,
                        source_event=source_event.event_id,
                        target_event=target_event.event_id,
                        confidence=0.6,
                        evidence=match.group(0),
                        source_document=document['id']
                    )

                    relations.append(relation)

        return relations

    def get_chronological_timeline(self) -> List[TimelineEvent]:
        """Get all events in chronological order."""

        if self.timeline_cache is None:
            # Build timeline
            all_events = list(self.events.values())

            # Sort by timestamp (events without timestamps go to the end)
            def sort_key(event):
                if event.timestamp:
                    return (0, event.timestamp)
                else:
                    return (1, event.event_id)  # Secondary sort for consistency

            all_events.sort(key=sort_key)
            self.timeline_cache = all_events

        return self.timeline_cache

    def validate_temporal_consistency(self) -> List[Dict[str, Any]]:
        """Validate temporal consistency across all events and relations."""
        inconsistencies = []

        # Check for temporal paradoxes
        for relation in self.relations.values():
            if relation.relation_type in [TemporalRelationType.BEFORE, TemporalRelationType.AFTER]:
                paradox = self._check_temporal_paradox(relation)
                if paradox:
                    inconsistencies.append(paradox)

        # Check for causality violations
        causality_violations = self._check_causality_violations()
        inconsistencies.extend(causality_violations)

        # Check for impossible time references
        time_violations = self._check_time_reference_violations()
        inconsistencies.extend(time_violations)

        return inconsistencies

    def _check_temporal_paradox(self, relation: TemporalRelation) -> Optional[Dict[str, Any]]:
        """Check if a temporal relation creates a paradox."""

        source_event = self.events.get(relation.source_event)
        target_event = self.events.get(relation.target_event)

        if not source_event or not target_event:
            return None

        # Check if both events have timestamps
        if source_event.timestamp and target_event.timestamp:
            if relation.relation_type == TemporalRelationType.BEFORE:
                if source_event.timestamp >= target_event.timestamp:
                    return {
                        'type': 'temporal_paradox',
                        'description': f"Event '{source_event.title}' is said to be before '{target_event.title}' but has later timestamp",
                        'relation_id': relation.relation_id,
                        'evidence': relation.evidence,
                        'severity': 'high'
                    }
            elif relation.relation_type == TemporalRelationType.AFTER:
                if source_event.timestamp <= target_event.timestamp:
                    return {
                        'type': 'temporal_paradox',
                        'description': f"Event '{source_event.title}' is said to be after '{target_event.title}' but has earlier timestamp",
                        'relation_id': relation.relation_id,
                        'evidence': relation.evidence,
                        'severity': 'high'
                    }

        return None

    def _check_causality_violations(self) -> List[Dict[str, Any]]:
        """Check for causality violations (effects before causes)."""
        violations = []

        for relation in self.relations.values():
            if relation.relation_type == TemporalRelationType.CAUSES:
                source_event = self.events.get(relation.source_event)
                target_event = self.events.get(relation.target_event)

                if source_event and target_event and source_event.timestamp and target_event.timestamp:
                    if source_event.timestamp > target_event.timestamp:
                        violations.append({
                            'type': 'causality_violation',
                            'description': f"Cause '{source_event.title}' happens after effect '{target_event.title}'",
                            'relation_id': relation.relation_id,
                            'evidence': relation.evidence,
                            'severity': 'critical'
                        })

        return violations

    def _check_time_reference_violations(self) -> List[Dict[str, Any]]:
        """Check for impossible time references."""
        violations = []

        # Check for events that reference future events as past
        # This would be more sophisticated in practice

        return violations

    def _parse_time_reference(self, time_ref: str) -> Optional[datetime]:
        """Parse a time reference into a datetime object."""

        if not time_ref or time_ref == 'unknown':
            return None

        # Simple time parsing - would be more sophisticated in practice
        import re

        # Look for year references
        year_match = re.search(r'\b(\d{4})\b', time_ref)
        if year_match:
            try:
                year = int(year_match.group(1))
                return datetime(year, 1, 1)  # Default to January 1st
            except ValueError:
                pass

        # Relative time references would need more complex parsing
        return None

    def _extract_participants(self, description: str) -> List[str]:
        """Extract participant entity IDs from event description."""
        participants = []

        # Simple name extraction - would use entity recognition in practice
        import re

        names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', description)
        participants.extend(names[:3])  # Limit to first 3 names

        return participants

    def _find_matching_event(self, description: str, events: List[TimelineEvent]) -> Optional[TimelineEvent]:
        """Find an event that matches a description."""

        description_lower = description.lower()

        for event in events:
            if description_lower in event.description.lower() or event.title.lower() in description_lower:
                return event

        return None

    def get_event_chain(self, event_id: str) -> Dict[str, Any]:
        """Get the chain of events leading to and from a specific event."""

        if event_id not in self.events:
            return {}

        event = self.events[event_id]

        # Find events that lead to this event
        predecessors = []
        for relation in self.relations.values():
            if (relation.target_event == event_id and
                relation.relation_type in [TemporalRelationType.CAUSES, TemporalRelationType.ENABLES]):
                predecessor = self.events.get(relation.source_event)
                if predecessor:
                    predecessors.append(predecessor)

        # Find events that follow from this event
        successors = []
        for relation in self.relations.values():
            if (relation.source_event == event_id and
                relation.relation_type in [TemporalRelationType.CAUSES, TemporalRelationType.ENABLES]):
                successor = self.events.get(relation.target_event)
                if successor:
                    successors.append(successor)

        return {
            'event': event,
            'predecessors': predecessors,
            'successors': successors
        }

    def get_timeline_summary(self) -> Dict[str, Any]:
        """Get a summary of the timeline."""

        timeline = self.get_chronological_timeline()

        event_types = {}
        for event in timeline:
            event_type = event.event_type.value
            event_types[event_type] = event_types.get(event_type, 0) + 1

        return {
            'total_events': len(timeline),
            'total_relations': len(self.relations),
            'event_types': event_types,
            'temporal_span': self._calculate_temporal_span(timeline),
            'consistency_issues': len(self.validate_temporal_consistency())
        }

    def _calculate_temporal_span(self, timeline: List[TimelineEvent]) -> Dict[str, Any]:
        """Calculate the temporal span covered by events."""

        timestamped_events = [event for event in timeline if event.timestamp]

        if not timestamped_events:
            return {'span': 'unknown', 'start': None, 'end': None}

        start_time = min(event.timestamp for event in timestamped_events)
        end_time = max(event.timestamp for event in timestamped_events)

        span = end_time - start_time

        return {
            'span': f"{span.days} days",
            'start': start_time.isoformat(),
            'end': end_time.isoformat(),
            'timestamped_events': len(timestamped_events)
        }