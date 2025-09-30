"""
Core graph structure for needle-preserving temporal retrieval system.
Handles segmentation of million-token contexts into manageable chunks with temporal relationships.
"""

import numpy as np
from typing import List, Dict, Set, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import networkx as nx
from collections import defaultdict
import hashlib

@dataclass
class TextSegment:
    """A segment of text with metadata and provenance."""
    id: str
    text: str
    start_pos: int
    end_pos: int
    timestamp: Optional[datetime] = None
    document_id: Optional[str] = None
    embeddings: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, TextSegment):
            return False
        return self.id == other.id

class ContextGraph:
    """Graph structure representing segmented context with temporal relationships."""

    def __init__(self, segment_size: int = 512, overlap_ratio: float = 0.1):
        self.segment_size = segment_size
        self.overlap_ratio = overlap_ratio
        self.overlap_size = int(segment_size * overlap_ratio)
        self.graph = nx.DiGraph()
        self.segments: Dict[str, TextSegment] = {}
        self.segment_index: List[str] = []
        self.doc_segments: Dict[str, List[str]] = defaultdict(list)

    def add_document(self, text: str, doc_id: str,
                    timestamp: Optional[datetime] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> List[str]:
        """Add a document to the graph and return segment IDs."""
        if metadata is None:
            metadata = {}

        segments = self._create_segments(text, doc_id, timestamp, metadata)
        segment_ids = []

        for segment in segments:
            self.segments[segment.id] = segment
            self.segment_index.append(segment.id)
            self.doc_segments[doc_id].append(segment.id)
            segment_ids.append(segment.id)

        self._build_temporal_edges(doc_id, segment_ids)
        return segment_ids

    def _create_segments(self, text: str, doc_id: str,
                        timestamp: Optional[datetime],
                        metadata: Dict[str, Any]) -> List[TextSegment]:
        """Create overlapping segments from text."""
        words = text.split()
        segments = []

        for i in range(0, len(words), self.segment_size - self.overlap_size):
            start = i
            end = min(i + self.segment_size, len(words))
            segment_text = ' '.join(words[start:end])

            segment_id = self._generate_segment_id(doc_id, start, end)

            segment = TextSegment(
                id=segment_id,
                text=segment_text,
                start_pos=start,
                end_pos=end,
                timestamp=timestamp,
                document_id=doc_id,
                metadata=metadata.copy()
            )
            segments.append(segment)

            if end >= len(words):
                break

        return segments

    def _generate_segment_id(self, doc_id: str, start: int, end: int) -> str:
        """Generate unique segment ID."""
        content = f"{doc_id}_{start}_{end}"
        return hashlib.md5(content.encode()).hexdigest()

    def _build_temporal_edges(self, doc_id: str, segment_ids: List[str]):
        """Build temporal edges between consecutive segments."""
        # First ensure all segments are added as nodes
        for seg_id in segment_ids:
            if seg_id not in self.graph:
                self.graph.add_node(seg_id)

        for i in range(len(segment_ids) - 1):
            source = segment_ids[i]
            target = segment_ids[i + 1]

            # Add sequential edge
            self.graph.add_edge(source, target,
                              edge_type='temporal',
                              weight=1.0,
                              temporal_distance=1)

    def add_semantic_edges(self, threshold: float = 0.5):
        """Add semantic similarity edges between segments."""
        from sklearn.metrics.pairwise import cosine_similarity

        # Calculate pairwise similarities
        for i, seg_id1 in enumerate(self.segment_index):
            for seg_id2 in self.segment_index[i+1:]:
                seg1 = self.segments[seg_id1]
                seg2 = self.segments[seg_id2]

                if seg1.embeddings is not None and seg2.embeddings is not None:
                    similarity = cosine_similarity(
                        seg1.embeddings.reshape(1, -1),
                        seg2.embeddings.reshape(1, -1)
                    )[0][0]

                    if similarity > threshold:
                        # Add bidirectional semantic edge
                        self.graph.add_edge(seg_id1, seg_id2,
                                          edge_type='semantic',
                                          weight=similarity,
                                          temporal_distance=abs(
                                            (datetime.fromisoformat(seg1.timestamp) - datetime.fromisoformat(seg2.timestamp)).total_seconds()
                                          ) if seg1.timestamp and seg2.timestamp else 0)

    def get_segment(self, segment_id: str) -> Optional[TextSegment]:
        """Get segment by ID."""
        return self.segments.get(segment_id)

    def get_neighbors(self, segment_id: str, edge_type: Optional[str] = None) -> Set[str]:
        """Get neighboring segments."""
        if segment_id not in self.graph:
            return set()

        if edge_type:
            return {n for n in self.graph.neighbors(segment_id)
                   if self.graph[segment_id][n]['edge_type'] == edge_type}
        else:
            return set(self.graph.neighbors(segment_id))

    def get_temporal_path(self, start_id: str, end_id: str) -> Optional[List[str]]:
        """Find temporal path between segments."""
        try:
            # Use only temporal edges
            temp_graph = self.graph.edge_subgraph(
                (u, v) for u, v, d in self.graph.edges(data=True)
                if d['edge_type'] == 'temporal'
            )
            return nx.shortest_path(temp_graph, start_id, end_id)
        except nx.NetworkXNoPath:
            return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to serializable dictionary."""
        return {
            'segments': {
                seg_id: {
                    'text': seg.text,
                    'start_pos': seg.start_pos,
                    'end_pos': seg.end_pos,
                    'timestamp': seg.timestamp,
                    'document_id': seg.document_id,
                    'metadata': seg.metadata
                }
                for seg_id, seg in self.segments.items()
            },
            'edges': [
                {
                    'source': u,
                    'target': v,
                    'type': d['edge_type'],
                    'weight': d['weight'],
                    'temporal_distance': d['temporal_distance']
                }
                for u, v, d in self.graph.edges(data=True)
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextGraph':
        """Create graph from dictionary."""
        graph = cls()

        # Rebuild segments
        for seg_id, seg_data in data['segments'].items():
            segment = TextSegment(
                id=seg_id,
                text=seg_data['text'],
                start_pos=seg_data['start_pos'],
                end_pos=seg_data['end_pos'],
                timestamp=datetime.fromisoformat(seg_data['timestamp'])
                if seg_data['timestamp'] else None,
                document_id=seg_data['document_id'],
                metadata=seg_data['metadata']
            )
            graph.segments[seg_id] = segment
            graph.segment_index.append(seg_id)
            if segment.document_id:
                graph.doc_segments[segment.document_id].append(seg_id)

        # Rebuild edges
        for edge_data in data['edges']:
            graph.graph.add_edge(
                edge_data['source'],
                edge_data['target'],
                edge_type=edge_data['type'],
                weight=edge_data['weight'],
                temporal_distance=edge_data['temporal_distance']
            )

        return graph