"""
Enhanced NPTS System with million-token context support.
Optimized for large-scale document processing with memory management.
"""

import numpy as np
import hashlib
import json
from typing import List, Dict, Set, Tuple, Optional, Any, Iterator
from dataclasses import dataclass, field
from datetime import datetime
import networkx as nx
from collections import defaultdict, deque
import heapq
import psutil
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import time

from context_graph import ContextGraph, TextSegment
from npts_retriever import NPTSRetriever, RetrievalResult
from psma_merger import PSMAMerger, MergedEvidence
from crb_certifier import CRBCertifier, RecallCertificate
from evaluation_framework import EvaluationFramework

@dataclass
class SystemStats:
    """System performance statistics."""
    total_documents: int = 0
    total_segments: int = 0
    total_tokens: int = 0
    memory_usage_mb: float = 0.0
    avg_query_time: float = 0.0
    cache_hit_rate: float = 0.0
    index_build_time: float = 0.0

@dataclass
class ChunkConfig:
    """Configuration for chunked processing."""
    chunk_size: int = 100000  # tokens per chunk
    max_chunks_in_memory: int = 5
    overlap_ratio: float = 0.1
    compression_enabled: bool = True

class QueryCache:
    """LRU cache for query results."""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = {}
        self.access_order = deque()
        self.lock = threading.Lock()

    def get(self, query_hash: str) -> Optional[Dict[str, Any]]:
        with self.lock:
            if query_hash in self.cache:
                # Move to end (most recently used)
                self.access_order.remove(query_hash)
                self.access_order.append(query_hash)
                return self.cache[query_hash]
            return None

    def put(self, query_hash: str, result: Dict[str, Any]):
        with self.lock:
            if query_hash in self.cache:
                self.access_order.remove(query_hash)
            elif len(self.cache) >= self.max_size:
                # Remove least recently used
                oldest = self.access_order.popleft()
                del self.cache[oldest]

            self.cache[query_hash] = result
            self.access_order.append(query_hash)

class MemoryManager:
    """Manages memory usage for large datasets."""

    def __init__(self, max_memory_gb: float = 8.0):
        self.max_memory_bytes = max_memory_gb * 1024**3
        self.chunks_loaded = set()
        self.chunk_access_times = {}
        self.lock = threading.Lock()

    def can_load_chunk(self, chunk_id: str, chunk_size_bytes: int) -> bool:
        """Check if we can load a chunk without exceeding memory limit."""
        with self.lock:
            current_memory = self.get_current_memory_usage()

            if current_memory + chunk_size_bytes <= self.max_memory_bytes:
                return True

            # Try to evict least recently used chunks
            self.evict_chunks(current_memory + chunk_size_bytes - self.max_memory_bytes)
            return current_memory + chunk_size_bytes <= self.max_memory_bytes

    def register_chunk_access(self, chunk_id: str):
        """Register that a chunk was accessed."""
        with self.lock:
            self.chunk_access_times[chunk_id] = time.time()

    def evict_chunks(self, bytes_to_free: int):
        """Evict chunks to free up memory."""
        # Sort by access time (oldest first)
        sorted_chunks = sorted(
            self.chunk_access_times.items(),
            key=lambda x: x[1]
        )

        freed = 0
        for chunk_id, _ in sorted_chunks:
            if freed >= bytes_to_free:
                break

            # Remove chunk from memory (implementation depends on storage)
            self.chunks_loaded.discard(chunk_id)
            del self.chunk_access_times[chunk_id]

            # Estimate chunk size (in practice, track actual sizes)
            freed += 50 * 1024**2  # Assume 50MB per chunk

    def get_current_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss

class EnhancedNeedleRetrievalSystem:
    """Enhanced NPTS system optimized for million-token contexts."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        default_config = self._default_config()
        if config:
            default_config.update(config)
        self.config = default_config

        # Initialize components
        self.context_graphs = {}  # chunk_id -> ContextGraph
        self.retrievers = {}  # chunk_id -> NPTSRetriever
        self.merger = PSMAMerger(
            overlap_threshold=self.config['overlap_threshold'],
            conflict_resolution=self.config['conflict_resolution']
        )
        self.certifier = CRBCertifier(
            target_recall=self.config['target_recall'],
            confidence_level=self.config['confidence_level'],
            budget=self.config['budget']
        )

        # Enhanced components
        self.cache = QueryCache(max_size=self.config.get('cache_size', 1000))
        self.memory_manager = MemoryManager(max_memory_gb=self.config.get('max_memory_gb', 8.0))
        self.chunk_config = ChunkConfig(
            chunk_size=self.config.get('chunk_size', 100000),
            max_chunks_in_memory=self.config.get('max_chunks_in_memory', 5)
        )

        # Statistics
        self.stats = SystemStats()
        self.query_times = deque(maxlen=1000)

        # Threading
        self.executor = ThreadPoolExecutor(max_workers=self.config['max_workers'])

        # System state
        self.initialized = False
        self.document_chunks = {}  # doc_id -> list of chunk_ids
        self.chunk_metadata = {}  # chunk_id -> metadata

    def _default_config(self) -> Dict[str, Any]:
        """Default enhanced system configuration."""
        return {
            'segment_size': 512,
            'overlap_ratio': 0.1,
            'budget': 10000,
            'target_recall': 0.95,
            'confidence_level': 0.90,
            'overlap_threshold': 0.5,
            'conflict_resolution': 'temporal_order',
            'embedding_dim': 768,
            'k_neighbors': 5,
            'output_dir': 'evaluation_results',
            'cache_size': 1000,
            'max_memory_gb': 8.0,
            'chunk_size': 100000,
            'max_chunks_in_memory': 5,
            'max_workers': 4,
            'use_hnsw': True,
            'hnsw_params': {
                'M': 16,
                'ef_construction': 200,
                'ef_search': 100
            }
        }

    def initialize(self, documents: List[Dict[str, Any]]):
        """Initialize system with documents using chunked processing."""
        print(f"Initializing enhanced system with {len(documents)} documents...")

        # Process documents in chunks
        self._process_documents_chunked(documents)

        # Build global index for cross-chunk retrieval
        self._build_global_index()

        self.initialized = True
        print(f"System initialized successfully.")
        print(f"Created {len(self.context_graphs)} chunks from {self.stats.total_documents} documents")
        print(f"Total segments: {self.stats.total_segments:,}")
        print(f"Total tokens: {self.stats.total_tokens:,}")

    def _process_documents_chunked(self, documents: List[Dict[str, Any]]):
        """Process documents in memory-efficient chunks."""
        chunk_id = 0
        current_chunk_tokens = 0
        current_chunk_docs = []

        for doc in documents:
            doc_tokens = len(doc['text'].split())

            # Check if we need to start a new chunk
            if (current_chunk_tokens + doc_tokens > self.chunk_config.chunk_size and
                current_chunk_docs):
                # Process current chunk
                self._process_chunk(current_chunk_docs, f"chunk_{chunk_id}")
                chunk_id += 1
                current_chunk_docs = []
                current_chunk_tokens = 0

            current_chunk_docs.append(doc)
            current_chunk_tokens += doc_tokens

            # Track document chunks
            self.document_chunks[doc['id']] = f"chunk_{chunk_id}"

        # Process final chunk
        if current_chunk_docs:
            self._process_chunk(current_chunk_docs, f"chunk_{chunk_id}")

    def _process_chunk(self, documents: List[Dict[str, Any]], chunk_id: str):
        """Process a single chunk of documents."""
        print(f"Processing {chunk_id} with {len(documents)} documents...")

        start_time = time.time()

        # Create context graph for chunk
        graph = ContextGraph(
            segment_size=self.config['segment_size'],
            overlap_ratio=self.config['overlap_ratio']
        )

        # Process documents
        embeddings = []
        for doc in documents:
            segment_ids = graph.add_document(
                text=doc['text'],
                doc_id=doc['id'],
                timestamp=doc.get('timestamp'),
                metadata=doc.get('metadata', {})
            )

            # Generate embeddings
            if 'embedding' in doc:
                doc_embedding = doc['embedding']
            else:
                doc_embedding = np.random.rand(self.config['embedding_dim'])

            for seg_id in segment_ids:
                segment = graph.get_segment(seg_id)
                if segment:
                    segment.embeddings = doc_embedding + np.random.normal(0, 0.1, doc_embedding.shape)
                    embeddings.append(segment.embeddings)

        # Build semantic edges
        graph.add_semantic_edges(threshold=0.5)

        # Create retriever with HNSW if available
        if self.config['use_hnsw']:
            try:
                from hnswlib import Index
                ann_index = Index(space='l2', dim=self.config['embedding_dim'])
                ann_index.init_index(
                    max_elements=len(embeddings),
                    ef_construction=self.config['hnsw_params']['ef_construction'],
                    M=self.config['hnsw_params']['M']
                )
                ann_index.add_items(np.array(embeddings))
                ann_index.set_ef(self.config['hnsw_params']['ef_search'])
            except ImportError:
                print("HNSW not available, falling back to sklearn")
                ann_index = NearestNeighbors(
                    n_neighbors=self.config['k_neighbors'],
                    algorithm='ball_tree',
                    metric='euclidean'
                )
                ann_index.fit(np.array(embeddings))
        else:
            ann_index = NearestNeighbors(
                n_neighbors=self.config['k_neighbors'],
                algorithm='ball_tree',
                metric='euclidean'
            )
            ann_index.fit(np.array(embeddings))

        # Store chunk components
        self.context_graphs[chunk_id] = graph
        self.retrievers[chunk_id] = NPTSRetriever(
            graph,
            alpha=self.config.get('alpha', 0.7),
            beta=self.config.get('beta', 0.3),
            budget=self.config['budget'],
            k_neighbors=self.config['k_neighbors']
        )
        self.retrievers[chunk_id].ann_index = ann_index
        self.retrievers[chunk_id].segment_embeddings = np.array(embeddings)

        # Store metadata
        self.chunk_metadata[chunk_id] = {
            'document_count': len(documents),
            'segment_count': len(graph.segment_index),
            'total_tokens': sum(len(doc['text'].split()) for doc in documents),
            'build_time': time.time() - start_time
        }

        # Update statistics
        self.stats.total_documents += len(documents)
        self.stats.total_segments += len(graph.segment_index)
        self.stats.total_tokens += sum(len(doc['text'].split()) for doc in documents)
        self.stats.index_build_time += time.time() - start_time

        # Register with memory manager
        self.memory_manager.register_chunk_access(chunk_id)

    def _build_global_index(self):
        """Build global index for cross-chunk retrieval."""
        # Sample segments from each chunk for global similarity
        global_embeddings = []
        global_chunk_ids = []

        for chunk_id, graph in self.context_graphs.items():
            # Sample up to 100 segments per chunk
            sample_size = min(100, len(graph.segment_index))
            sample_indices = np.random.choice(
                len(graph.segment_index),
                sample_size,
                replace=False
            )

            for idx in sample_indices:
                seg_id = graph.segment_index[idx]
                segment = graph.get_segment(seg_id)
                if segment and segment.embeddings is not None:
                    global_embeddings.append(segment.embeddings)
                    global_chunk_ids.append(chunk_id)

        if global_embeddings:
            self.global_ann = NearestNeighbors(
                n_neighbors=min(10, len(global_embeddings)),
                algorithm='ball_tree',
                metric='euclidean'
            )
            self.global_ann.fit(np.array(global_embeddings))
            self.global_chunk_ids = global_chunk_ids

    def query(self, query_text: str, query_embedding: Optional[np.ndarray] = None,
              min_recall: float = 0.95) -> Dict[str, Any]:
        """Query the system with enhanced processing."""
        start_time = time.time()

        # Check cache first
        query_hash = self._hash_query(query_text, query_embedding)
        cached_result = self.cache.get(query_hash)
        if cached_result:
            self.stats.cache_hit_rate = (
                self.stats.cache_hit_rate * 0.9 + 0.1
            )  # Update moving average
            return cached_result

        # Generate query embedding if not provided
        if query_embedding is None:
            query_embedding = np.random.rand(self.config['embedding_dim'])

        # Find relevant chunks using global index
        relevant_chunks = self._find_relevant_chunks(query_embedding)

        # Retrieve from relevant chunks in parallel
        retrieval_results = []
        with ThreadPoolExecutor(max_workers=min(4, len(relevant_chunks))) as executor:
            futures = {
                executor.submit(
                    self._query_chunk,
                    chunk_id,
                    query_text,
                    query_embedding,
                    min_recall
                ): chunk_id
                for chunk_id in relevant_chunks
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result and result.segments:
                        retrieval_results.append(result)
                except Exception as e:
                    print(f"Error querying chunk {futures[future]}: {e}")

        # Merge results from all chunks
        if retrieval_results:
            merged_evidence = self._merge_chunk_results(retrieval_results)
            certificate = self.certifier.certify_recall(
                retrieval_results[0],  # Use first result for certification
                query_complexity=len(relevant_chunks)
            )
            response = self._generate_response(merged_evidence, query_text)
        else:
            # Fallback to sequential search
            merged_evidence = MergedEvidence(
                text="No relevant information found.",
                confidence=0.0,
                provenance=[],
                temporal_span=(None, None),
                metadata={'error': 'no_results'}
            )
            certificate = RecallCertificate(
                lower_bound=0.0,
                upper_bound=0.0,
                confidence=0.0,
                budget_used=0,
                effective_budget=self.config['budget'],
                calibration_score=0.0,
                metadata={'error': 'no_results'}
            )
            response = "No relevant information found."

        # Build result
        result = {
            'query': query_text,
            'response': response,
            'evidence': merged_evidence,
            'certificate': certificate,
            'retrieved_segments': [seg for res in retrieval_results for seg in res.segments],
            'statistics': {
                'chunks_searched': len(relevant_chunks),
                'segments_retrieved': sum(len(res.segments) for res in retrieval_results),
                'query_time': time.time() - start_time,
                'memory_usage_mb': self.memory_manager.get_current_memory_usage() / 1024**2
            }
        }

        # Cache result
        self.cache.put(query_hash, result)

        # Update statistics
        self.query_times.append(time.time() - start_time)
        self.stats.avg_query_time = np.mean(self.query_times)

        return result

    def _find_relevant_chunks(self, query_embedding: np.ndarray) -> List[str]:
        """Find relevant chunks using global index."""
        if not hasattr(self, 'global_ann'):
            # Fallback: search all chunks
            return list(self.context_graphs.keys())

        # Use global index to find similar chunks
        distances, indices = self.global_ann.kneighbors(
            query_embedding.reshape(1, -1)
        )

        # Get unique chunk IDs
        relevant_chunks = set()
        for idx in indices[0]:
            if idx < len(self.global_chunk_ids):
                relevant_chunks.add(self.global_chunk_ids[idx])

        # Also include chunks from document metadata if available
        return list(relevant_chunks) if relevant_chunks else list(self.context_graphs.keys())

    def _query_chunk(self, chunk_id: str, query_text: str,
                     query_embedding: np.ndarray, min_recall: float) -> Optional[RetrievalResult]:
        """Query a specific chunk."""
        if chunk_id not in self.retrievers:
            return None

        # Check memory and load if necessary
        if not self.memory_manager.can_load_chunk(chunk_id, 50 * 1024**2):  # Assume 50MB
            print(f"Memory limit exceeded, skipping chunk {chunk_id}")
            return None

        # Register access
        self.memory_manager.register_chunk_access(chunk_id)

        # Query the chunk
        retriever = self.retrievers[chunk_id]
        return retriever.retrieve(query_text, query_embedding, min_recall)

    def _merge_chunk_results(self, results: List[RetrievalResult]) -> MergedEvidence:
        """Merge results from multiple chunks."""
        if not results:
            return MergedEvidence(
                text="",
                confidence=0.0,
                provenance=[],
                temporal_span=(None, None),
                metadata={'error': 'no_results'}
            )

        if len(results) == 1:
            return self.merger.merge_evidence(
                results[0],
                merge_strategy='temporal_order'
            )

        # Merge multiple results
        all_segments = []
        for result in results:
            all_segments.extend(result.segments)

        # Sort by timestamp if available
        all_segments.sort(key=lambda s: s.timestamp or datetime.min)

        # Combine text
        combined_text = "\n\n".join(seg.text for seg in all_segments)

        # Calculate combined confidence
        avg_confidence = np.mean([r.recall_estimate for r in results])

        # Collect provenance
        all_provenance = []
        for result in results:
            all_provenance.extend(result.provenance)

        # Find temporal span
        timestamps = [s.timestamp for s in all_segments if s.timestamp]
        temporal_span = (
            min(timestamps) if timestamps else None,
            max(timestamps) if timestamps else None
        )

        return MergedEvidence(
            text=combined_text,
            confidence=avg_confidence,
            provenance=list(set(all_provenance)),
            temporal_span=temporal_span,
            metadata={'merged_chunks': len(results)}
        )

    def _generate_response(self, merged_evidence: MergedEvidence, query_text: str) -> str:
        """Generate response based on merged evidence."""
        if not merged_evidence.text.strip():
            return "No relevant information found."

        response = f"Based on the retrieved information:\n\n{merged_evidence.text}"

        if merged_evidence.temporal_span[0] and merged_evidence.temporal_span[1]:
            response += f"\n\nInformation spans from {merged_evidence.temporal_span[0]} to {merged_evidence.temporal_span[1]}."

        response += f"\n\nConfidence: {merged_evidence.confidence:.2f}"
        response += f"\nSources: {len(merged_evidence.provenance)} segments from {len(self.document_chunks)} document chunks"

        return response

    def _hash_query(self, query_text: str, query_embedding: Optional[np.ndarray]) -> str:
        """Generate hash for query caching."""
        content = query_text
        if query_embedding is not None:
            content += str(query_embedding.tobytes())
        return hashlib.md5(content.encode()).hexdigest()

    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        return {
            'system_stats': self.stats.__dict__,
            'chunk_count': len(self.context_graphs),
            'cache_stats': {
                'size': len(self.cache.cache),
                'hit_rate': self.stats.cache_hit_rate
            },
            'memory_stats': {
                'current_usage_mb': self.memory_manager.get_current_memory_usage() / 1024**2,
                'max_usage_gb': self.memory_manager.max_memory_bytes / 1024**3
            },
            'chunk_details': self.chunk_metadata
        }

    def save_system(self, filepath: str):
        """Save system state to file."""
        print(f"Saving system to {filepath}...")

        # Prepare save data
        save_data = {
            'config': self.config,
            'stats': self.stats.__dict__,
            'chunk_metadata': self.chunk_metadata,
            'document_chunks': self.document_chunks,
            'global_chunk_ids': getattr(self, 'global_chunk_ids', [])
        }

        # Save graphs and retrievers separately
        for chunk_id in self.context_graphs:
            chunk_data = {
                'graph': self.context_graphs[chunk_id].to_dict(),
                'retriever_state': {
                    'alpha': self.retrievers[chunk_id].alpha,
                    'beta': self.retrievers[chunk_id].beta,
                    'budget': self.retrievers[chunk_id].budget,
                    'k_neighbors': self.retrievers[chunk_id].k_neighbors
                }
            }

            # Save chunk data
            chunk_path = f"{filepath}_chunk_{chunk_id}.pkl"
            with open(chunk_path, 'wb') as f:
                pickle.dump(chunk_data, f)

        # Save main data
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)

        print(f"System saved successfully.")

    def load_system(self, filepath: str):
        """Load system state from file."""
        print(f"Loading system from {filepath}...")

        # Load main data
        with open(filepath, 'r') as f:
            save_data = json.load(f)

        self.config = save_data['config']
        self.stats = SystemStats(**save_data['stats'])
        self.chunk_metadata = save_data['chunk_metadata']
        self.document_chunks = save_data['document_chunks']

        # Load chunk data
        for chunk_id in self.chunk_metadata:
            chunk_path = f"{filepath}_chunk_{chunk_id}.pkl"
            if os.path.exists(chunk_path):
                with open(chunk_path, 'rb') as f:
                    chunk_data = pickle.load(f)

                # Rebuild graph
                graph = ContextGraph.from_dict(chunk_data['graph'])
                self.context_graphs[chunk_id] = graph

                # Rebuild retriever
                retriever_state = chunk_data['retriever_state']
                retriever = NPTSRetriever(
                    graph,
                    **retriever_state
                )

                # Rebuild ANN index
                if 'embeddings' in chunk_data:
                    embeddings = np.array(chunk_data['embeddings'])
                else:
                    # Extract embeddings from segments
                    embeddings = []
                    for seg_id in graph.segment_index:
                        segment = graph.get_segment(seg_id)
                        if segment and segment.embeddings is not None:
                            embeddings.append(segment.embeddings)

                    if embeddings:
                        embeddings = np.array(embeddings)
                    else:
                        embeddings = np.random.rand(len(graph.segment_index), self.config['embedding_dim'])

                retriever.build_ann_index(embeddings)
                self.retrievers[chunk_id] = retriever

        # Rebuild global index
        self._build_global_index()

        self.initialized = True
        print(f"System loaded successfully.")