"""
Needle-Preserving Temporal Retrieval (NPTS) implementation.
Uses prize-collecting Steiner Tree approach with temporal regularization.
"""

import numpy as np
from typing import List, Dict, Set, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import networkx as nx
from collections import defaultdict
import heapq
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity

from context_graph import ContextGraph, TextSegment

@dataclass
class RetrievalResult:
    """Result of NPTS retrieval with provenance tracking."""
    segments: List[TextSegment]
    scores: List[float]
    provenance: Dict[str, List[str]]  # Maps answer parts to source segments
    total_cost: float
    temporal_coherence: float
    recall_estimate: float

class NPTSRetriever:
    """Needle-Preserving Temporal Retrieval system."""

    def __init__(self, context_graph: ContextGraph,
                 alpha: float = 0.7,  # Temporal regularization weight
                 beta: float = 0.3,   # Semantic similarity weight
                 budget: int = 10000, # Maximum tokens to retrieve
                 k_neighbors: int = 5):
        self.graph = context_graph
        self.alpha = alpha
        self.beta = beta
        self.budget = budget
        self.k_neighbors = k_neighbors
        self.ann_index = None
        self.segment_embeddings = None

    def build_ann_index(self, embeddings: np.ndarray):
        """Build approximate nearest neighbor index for fast retrieval."""
        self.segment_embeddings = embeddings
        self.ann_index = NearestNeighbors(
            n_neighbors=self.k_neighbors,
            algorithm='ball_tree',
            metric='euclidean'
        )
        self.ann_index.fit(embeddings)

    def retrieve(self, query: str, query_embedding: np.ndarray,
                 min_recall: float = 0.95) -> RetrievalResult:
        """
        Retrieve relevant segments using NPTS algorithm.

        Args:
            query: Query text
            query_embedding: Query vector embedding
            min_recall: Minimum recall threshold

        Returns:
            RetrievalResult with selected segments and metadata
        """
        # Step 1: Identify needle segments using similarity search
        needle_candidates = self._find_needle_candidates(query_embedding)

        # Step 2: Solve prize-collecting Steiner Tree problem
        steiner_tree = self._solve_prize_collecting_steiner(needle_candidates)

        # Step 3: Apply temporal regularization
        regularized_tree = self._apply_temporal_regularization(steiner_tree)

        # Step 4: Budget-aware selection
        selected_segments = self._select_within_budget(regularized_tree)

        # Step 5: Estimate recall and build provenance
        recall_estimate = self._estimate_recall(selected_segments, needle_candidates)
        provenance = self._build_provenance(selected_segments, query)

        total_tokens = sum(len(seg.text.split()) for seg in selected_segments)

        return RetrievalResult(
            segments=selected_segments,
            scores=[self._calculate_segment_score(seg, query_embedding)
                   for seg in selected_segments],
            provenance=provenance,
            total_cost=total_tokens,
            temporal_coherence=self._calculate_temporal_coherence(selected_segments),
            recall_estimate=recall_estimate
        )

    def _find_needle_candidates(self, query_embedding: np.ndarray,
                               top_k: int = 50) -> List[Tuple[str, float]]:
        """Find top-k similar segments using ANN search."""
        if self.ann_index is None:
            raise ValueError("ANN index not built. Call build_ann_index() first.")

        distances, indices = self.ann_index.kneighbors(
            query_embedding.reshape(1, -1)
        )

        candidates = []
        for idx, dist in zip(indices[0], distances[0]):
            segment_id = self.graph.segment_index[idx]
            # Use a proper similarity transformation
            score = 1 / (1 + dist)  # Convert distance to similarity score
            candidates.append((segment_id, score))

        return sorted(candidates, key=lambda x: x[1], reverse=True)[:top_k]

    def _solve_prize_collecting_steiner(self, needle_candidates: List[Tuple[str, float]]) -> nx.Graph:
        """
        Solve prize-collecting Steiner Tree problem.

        Args:
            needle_candidates: List of (segment_id, prize) pairs

        Returns:
            Steiner tree subgraph
        """
        if not needle_candidates:
            return nx.Graph()

        # Filter candidates that exist in the graph
        valid_candidates = [(seg_id, prize) for seg_id, prize in needle_candidates
                          if seg_id in self.graph.graph]

        if not valid_candidates:
            return nx.Graph()

        # Scale prizes to emphasize top candidates
        max_prize = max(prize for _, prize in valid_candidates)
        scaled_candidates = [(seg_id, prize / max_prize * 10) for seg_id, prize in valid_candidates]

        # Create terminals set with scaled prizes
        terminals = {seg_id: prize for seg_id, prize in scaled_candidates}

        # Initialize with minimum spanning tree over terminals
        steiner_tree = nx.Graph()

        # Add terminals as nodes
        for seg_id in terminals:
            steiner_tree.add_node(seg_id, prize=terminals[seg_id])

        # Find paths between terminals, prioritizing high-prize pairs
        for i, (term1, prize1) in enumerate(scaled_candidates):
            for term2, prize2 in scaled_candidates[i+1:]:
                # Only connect if combined prize is significant
                if prize1 + prize2 > 1.0:
                    path = self._find_optimal_path(term1, term2)
                    if path:
                        # Add path edges to Steiner tree
                        for j in range(len(path) - 1):
                            edge_data = self.graph.graph[path[j]][path[j+1]]
                            steiner_tree.add_edge(
                                path[j], path[j+1],
                                weight=edge_data['weight'],
                                temporal_distance=edge_data['temporal_distance'],
                                edge_type=edge_data['edge_type']
                            )
                            # Add non-terminal nodes
                            if path[j] not in terminals:
                                steiner_tree.add_node(path[j])
                            if path[j+1] not in terminals:
                                steiner_tree.add_node(path[j+1])

        return steiner_tree

    def _find_optimal_path(self, source: str, target: str) -> Optional[List[str]]:
        """Find optimal path considering both semantic and temporal factors."""
        try:
            # Combined cost: semantic similarity and temporal distance
            def edge_weight(u, v, d):
                semantic_cost = 1 - d['weight']  # Convert similarity to cost
                temporal_cost = d['temporal_distance'] / 86400  # Normalize to days
                return self.alpha * temporal_cost + self.beta * semantic_cost

            path = nx.shortest_path(
                self.graph.graph,
                source=source,
                target=target,
                weight=edge_weight
            )
            return path
        except nx.NetworkXNoPath:
            return None

    def _apply_temporal_regularization(self, tree: nx.Graph) -> nx.Graph:
        """Apply temporal regularization to favor coherent timelines."""
        if len(tree.nodes) < 2:
            return tree

        # Calculate temporal variation penalty
        segments = [self.graph.segments[node_id] for node_id in tree.nodes
                   if node_id in self.graph.segments]

        # Sort segments by timestamp
        valid_segments = [s for s in segments if s.timestamp is not None]
        if len(valid_segments) < 2:
            return tree

        sorted_segments = sorted(valid_segments, key=lambda x: x.timestamp)

        # Penalize large temporal jumps
        total_temporal_variation = 0
        for i in range(len(sorted_segments) - 1):
            time_diff = abs((datetime.fromisoformat(sorted_segments[i+1].timestamp) -
                           datetime.fromisoformat(sorted_segments[i].timestamp)).total_seconds())
            total_temporal_variation += time_diff

        # Remove edges that cause excessive temporal variation
        edges_to_remove = []
        for u, v, d in tree.edges(data=True):
            if d['edge_type'] == 'semantic':
                seg_u = self.graph.segments[u]
                seg_v = self.graph.segments[v]
                if seg_u.timestamp and seg_v.timestamp:
                    time_diff = abs((datetime.fromisoformat(seg_v.timestamp) - datetime.fromisoformat(seg_u.timestamp)).total_seconds())
                    if time_diff > total_temporal_variation / len(tree.edges) * 2:
                        edges_to_remove.append((u, v))

        for u, v in edges_to_remove:
            tree.remove_edge(u, v)

        return tree

    def _select_within_budget(self, tree: nx.Graph) -> List[TextSegment]:
        """Select segments within token budget, prioritizing high-value nodes."""
        if not tree.nodes:
            return []

        # Calculate node scores
        node_scores = {}
        for node in tree.nodes:
            if node in self.graph.segments:
                segment = self.graph.segments[node]
                # Score based on degree and any terminal prizes
                score = tree.degree[node]
                if 'prize' in tree.nodes[node]:
                    score += tree.nodes[node]['prize'] * 10
                node_scores[node] = score

        # Sort nodes by score
        sorted_nodes = sorted(node_scores.items(), key=lambda x: x[1], reverse=True)

        # Greedily select nodes within budget
        selected = []
        current_cost = 0

        for node_id, _ in sorted_nodes:
            segment = self.graph.segments[node_id]
            segment_cost = len(segment.text.split())

            if current_cost + segment_cost <= self.budget:
                selected.append(segment)
                current_cost += segment_cost

        return selected

    def _calculate_segment_score(self, segment: TextSegment,
                               query_embedding: np.ndarray) -> float:
        """Calculate relevance score for a segment."""
        if segment.embeddings is None:
            return 0.0

        similarity = cosine_similarity(
            query_embedding.reshape(1, -1),
            segment.embeddings.reshape(1, -1)
        )[0][0]

        return float(similarity)

    def _estimate_recall(self, selected_segments: List[TextSegment],
                        needle_candidates: List[Tuple[str, float]]) -> float:
        """
        Estimate recall based on coverage of needle candidates.

        Args:
            selected_segments: List of selected segments
            needle_candidates: List of candidate needles with scores

        Returns:
            Estimated recall value
        """
        selected_ids = {seg.id for seg in selected_segments}
        needle_ids = {seg_id for seg_id, _ in needle_candidates}

        if not needle_ids:
            return 1.0

        coverage = len(selected_ids.intersection(needle_ids)) / len(needle_ids)

        # Adjust for budget constraints
        budget_factor = min(1.0, self.budget / 50000)  # Normalize by typical budget

        return min(1.0, coverage * budget_factor)

    def _build_provenance(self, selected_segments: List[TextSegment],
                         query: str) -> Dict[str, List[str]]:
        """Build provenance mapping for retrieved segments."""
        provenance = {}

        # Simple keyword-based provenance
        query_terms = set(query.lower().split())

        for segment in selected_segments:
            segment_terms = set(segment.text.lower().split())
            common_terms = query_terms.intersection(segment_terms)

            for term in common_terms:
                if term not in provenance:
                    provenance[term] = []
                provenance[term].append(segment.id)

        return provenance

    def _calculate_temporal_coherence(self, segments: List[TextSegment]) -> float:
        """Calculate temporal coherence score for selected segments."""
        if len(segments) < 2:
            return 1.0

        # Filter segments with timestamps
        timed_segments = [s for s in segments if s.timestamp is not None]
        if len(timed_segments) < 2:
            return 0.5  # Partial credit

        # Sort by timestamp
        sorted_segments = sorted(timed_segments, key=lambda x: x.timestamp)

        # Calculate temporal smoothness
        time_diffs = []
        for i in range(len(sorted_segments) - 1):
            diff = abs((datetime.fromisoformat(sorted_segments[i+1].timestamp) -
                       datetime.fromisoformat(sorted_segments[i].timestamp)).total_seconds())
            time_diffs.append(diff)

        # Lower variation = higher coherence
        mean_diff = np.mean(time_diffs)
        std_diff = np.std(time_diffs)

        if mean_diff == 0:
            return 1.0

        coherence = 1.0 / (1.0 + std_diff / mean_diff)
        return float(coherence)