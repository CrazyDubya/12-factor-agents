"""
Pointer-Safe Merge Algebra (PSMA) implementation.
Handles evidence merging with provenance preservation.
"""

import numpy as np
from typing import List, Dict, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass
from collections import defaultdict
import re
from difflib import SequenceMatcher
from datetime import datetime

from context_graph import TextSegment
from npts_retriever import RetrievalResult

@dataclass
class MergedEvidence:
    """Merged evidence with provenance tracking."""
    text: str
    provenance: List[str]  # Source segment IDs
    confidence: float
    temporal_span: Tuple[Optional[str], Optional[str]]  # Start and end timestamps
    metadata: Dict[str, Any]

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class PSMAMerger:
    """Pointer-Safe Merge Algebra for evidence combination."""

    def __init__(self, overlap_threshold: float = 0.8,
                 conflict_resolution: str = 'confidence'):
        self.overlap_threshold = overlap_threshold
        self.conflict_resolution = conflict_resolution
        self.merge_operations = {
            'union': self._merge_union,
            'intersection': self._merge_intersection,
            'concatenation': self._merge_concatenation,
            'temporal_order': self._merge_temporal_order
        }

    def merge_evidence(self, retrieval_result: RetrievalResult,
                      merge_strategy: str = 'temporal_order') -> MergedEvidence:
        """
        Merge retrieved evidence using PSMA operations.

        Args:
            retrieval_result: Result from NPTS retrieval
            merge_strategy: Strategy for merging ('union', 'intersection',
                          'concatenation', 'temporal_order')

        Returns:
            MergedEvidence with preserved provenance
        """
        if merge_strategy not in self.merge_operations:
            raise ValueError(f"Unknown merge strategy: {merge_strategy}")

        merge_func = self.merge_operations[merge_strategy]
        return merge_func(retrieval_result.segments, retrieval_result.provenance)

    def _merge_union(self, segments: List[TextSegment],
                    provenance: Dict[str, List[str]]) -> MergedEvidence:
        """Merge segments using union operation."""
        # Combine all unique text spans
        seen_spans = set()
        merged_spans = []
        all_provenance = []

        for segment in segments:
            # Check for overlaps
            is_overlap = False
            segment_words = segment.text.split()

            for i, (span_text, _) in enumerate(merged_spans):
                span_words = span_text.split()
                if self._calculate_overlap(segment_words, span_words) > self.overlap_threshold:
                    is_overlap = True
                    # Merge with existing span
                    merged_text = self._merge_text_spans(span_text, segment.text)
                    merged_spans[i] = (merged_text, merged_spans[i][1] + [segment.id])
                    break

            if not is_overlap:
                merged_spans.append((segment.text, [segment.id]))

            all_provenance.append(segment.id)

        # Combine merged spans
        final_text = ' '.join(span for span, _ in merged_spans)
        all_provenance = list(set(all_provenance))

        return MergedEvidence(
            text=final_text,
            provenance=all_provenance,
            confidence=self._calculate_merged_confidence(segments),
            temporal_span=self._get_temporal_span(segments),
            metadata={'merge_strategy': 'union', 'num_segments': len(segments)}
        )

    def _merge_intersection(self, segments: List[TextSegment],
                          provenance: Dict[str, List[str]]) -> MergedEvidence:
        """Merge segments using intersection operation."""
        if len(segments) < 2:
            return self._merge_union(segments, provenance)

        # Find common information across segments
        base_text = segments[0].text
        common_text = base_text

        for segment in segments[1:]:
            common_text = self._find_common_substring(common_text, segment.text)

        if not common_text:
            # Fallback to union if no intersection
            return self._merge_union(segments, provenance)

        return MergedEvidence(
            text=common_text,
            provenance=[seg.id for seg in segments],
            confidence=min(self._calculate_segment_confidence(seg) for seg in segments),
            temporal_span=self._get_temporal_span(segments),
            metadata={'merge_strategy': 'intersection', 'num_segments': len(segments)}
        )

    def _merge_concatenation(self, segments: List[TextSegment],
                           provenance: Dict[str, List[str]]) -> MergedEvidence:
        """Merge segments using concatenation with smart transitions."""
        if len(segments) == 1:
            return self._merge_union(segments, provenance)

        # Sort segments temporally if possible
        sorted_segments = self._sort_segments_temporally(segments)

        merged_parts = []
        current_provenance = []

        for i, segment in enumerate(sorted_segments):
            if i > 0:
                # Add transition if needed
                prev_seg = sorted_segments[i-1]
                transition = self._generate_transition(prev_seg, segment)
                if transition:
                    merged_parts.append(transition)

            merged_parts.append(segment.text)
            current_provenance.append(segment.id)

        final_text = ' '.join(merged_parts)

        return MergedEvidence(
            text=final_text,
            provenance=current_provenance,
            confidence=self._calculate_merged_confidence(segments),
            temporal_span=self._get_temporal_span(segments),
            metadata={'merge_strategy': 'concatenation', 'num_segments': len(segments)}
        )

    def _merge_temporal_order(self, segments: List[TextSegment],
                            provenance: Dict[str, List[str]]) -> MergedEvidence:
        """Merge segments preserving temporal order."""
        # Group segments by time proximity
        temporal_groups = self._group_by_temporal_proximity(segments)

        merged_parts = []
        current_provenance = []

        # Process groups in chronological order
        for group in sorted(temporal_groups, key=lambda g: self._get_group_time(g)):
            if len(group) == 1:
                merged_parts.append(group[0].text)
                current_provenance.append(group[0].id)
            else:
                # Merge segments within the same time period
                group_merged = self._merge_within_temporal_group(group)
                merged_parts.append(group_merged.text)
                current_provenance.extend(group_merged.provenance)

        final_text = ' '.join(merged_parts)

        return MergedEvidence(
            text=final_text,
            provenance=list(set(current_provenance)),
            confidence=self._calculate_merged_confidence(segments),
            temporal_span=self._get_temporal_span(segments),
            metadata={'merge_strategy': 'temporal_order', 'num_segments': len(segments)}
        )

    def _calculate_overlap(self, text1: List[str], text2: List[str]) -> float:
        """Calculate overlap ratio between two text spans."""
        set1 = set(text1)
        set2 = set(text2)
        intersection = set1.intersection(set2)
        union = set1.union(set2)

        return len(intersection) / len(union) if union else 0

    def _merge_text_spans(self, span1: str, span2: str) -> str:
        """Merge two overlapping text spans."""
        # Simple concatenation with duplicate removal
        words1 = span1.split()
        words2 = span2.split()

        # Find overlap
        matcher = SequenceMatcher(None, words1, words2)
        match = matcher.find_longest_match(0, len(words1), 0, len(words2))

        if match.size > 0:
            # Merge at overlap point
            merged = words1[:match.a] + words1[match.a:] + words2[match.b + match.size:]
            return ' '.join(merged)
        else:
            # No overlap, just concatenate
            return f"{span1} {span2}"

    def _find_common_substring(self, text1: str, text2: str) -> str:
        """Find longest common substring between two texts."""
        matcher = SequenceMatcher(None, text1, text2)
        match = matcher.find_longest_match(0, len(text1), 0, len(text2))

        if match.size > 0:
            return text1[match.a:match.a + match.size]
        else:
            return ""

    def _sort_segments_temporally(self, segments: List[TextSegment]) -> List[TextSegment]:
        """Sort segments by timestamp."""
        def sort_key(seg):
            if seg.timestamp:
                return seg.timestamp
            return datetime.min

        return sorted(segments, key=sort_key)

    def _generate_transition(self, seg1: TextSegment, seg2: TextSegment) -> Optional[str]:
        """Generate transition text between segments."""
        if not seg1.timestamp or not seg2.timestamp:
            return None

        time_diff = abs((datetime.fromisoformat(seg2.timestamp) - datetime.fromisoformat(seg1.timestamp)).total_seconds())

        if time_diff < 3600:  # Less than 1 hour
            return "Subsequently,"
        elif time_diff < 86400:  # Less than 1 day
            return "Later that day,"
        elif time_diff < 604800:  # Less than 1 week
            return "In the following days,"
        else:
            return "Sometime later,"

    def _group_by_temporal_proximity(self, segments: List[TextSegment],
                                   time_window: int = 3600) -> List[List[TextSegment]]:
        """Group segments by temporal proximity."""
        groups = []

        for segment in segments:
            if not segment.timestamp:
                # Segments without timestamps go in their own group
                groups.append([segment])
                continue

            added = False
            for group in groups:
                # Check if segment belongs to this group
                for group_seg in group:
                    if group_seg.timestamp:
                        time_diff = abs((datetime.fromisoformat(segment.timestamp) - datetime.fromisoformat(group_seg.timestamp)).total_seconds())
                        if time_diff <= time_window:
                            group.append(segment)
                            added = True
                            break
                if added:
                    break

            if not added:
                groups.append([segment])

        return groups

    def _merge_within_temporal_group(self, segments: List[TextSegment]) -> MergedEvidence:
        """Merge segments within the same temporal group."""
        # Use union for segments in the same time period
        return self._merge_union(segments, {})

    def _get_group_time(self, group: List[TextSegment]) -> datetime:
        """Get representative time for a temporal group."""
        times = [seg.timestamp for seg in group if seg.timestamp]
        if times:
            return min(times)
        return datetime.min

    def _calculate_merged_confidence(self, segments: List[TextSegment]) -> float:
        """Calculate confidence score for merged evidence."""
        if not segments:
            return 0.0

        confidences = [self._calculate_segment_confidence(seg) for seg in segments]

        if self.conflict_resolution == 'confidence':
            # Weight by confidence scores
            weights = np.array(confidences)
            weights = weights / weights.sum()
            return float(np.average(confidences, weights=weights))
        else:
            # Simple average
            return float(np.mean(confidences))

    def _calculate_segment_confidence(self, segment: TextSegment) -> float:
        """Calculate confidence score for a single segment."""
        # Base confidence from segment metadata if available
        if 'confidence' in segment.metadata:
            return segment.metadata['confidence']

        # Default confidence based on segment length
        word_count = len(segment.text.split())
        return min(1.0, word_count / 100)  # Normalize by typical segment length

    def _get_temporal_span(self, segments: List[TextSegment]) -> Tuple[Optional[str], Optional[str]]:
        """Get temporal span of merged evidence."""
        timestamps = [seg.timestamp for seg in segments if seg.timestamp]

        if not timestamps:
            return (None, None)

        start_time = min(timestamps)
        end_time = max(timestamps)

        return (start_time if start_time else None,
                end_time if end_time else None)

    def resolve_conflicts(self, evidence_list: List[MergedEvidence]) -> MergedEvidence:
        """Resolve conflicts between multiple evidence pieces."""
        if len(evidence_list) == 1:
            return evidence_list[0]

        # Strategy 1: Select evidence with highest confidence
        best_evidence = max(evidence_list, key=lambda e: e.confidence)

        # Strategy 2: If similar confidence, prefer more sources
        high_conf_evidence = [e for e in evidence_list
                            if abs(e.confidence - best_evidence.confidence) < 0.1]

        if len(high_conf_evidence) > 1:
            best_evidence = max(high_conf_evidence, key=lambda e: len(e.provenance))

        return best_evidence

    def create_pointer_map(self, merged_evidence: MergedEvidence,
                         original_segments: List[TextSegment]) -> Dict[str, List[Tuple[int, int]]]:
        """
        Create mapping from merged text to original segment positions.

        Args:
            merged_evidence: The merged evidence
            original_segments: List of original segments

        Returns:
            Dictionary mapping segment IDs to character ranges in merged text
        """
        pointer_map = defaultdict(list)
        merged_text = merged_evidence.text
        current_pos = 0

        for seg_id in merged_evidence.provenance:
            # Find segment in original list
            segment = next((s for s in original_segments if s.id == seg_id), None)
            if not segment:
                continue

            # Find segment text in merged text
            seg_text = segment.text
            start_pos = merged_text.find(seg_text, current_pos)

            if start_pos != -1:
                end_pos = start_pos + len(seg_text)
                pointer_map[seg_id].append((start_pos, end_pos))
                current_pos = end_pos

        return dict(pointer_map)