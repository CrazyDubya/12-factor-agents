"""
TF-IDF processing utilities for the V2 Context Selection System.
"""

import math
import time
from collections import Counter
from typing import List, Dict, Any
import numpy as np

from ..core.models import TextSegment


class TFIDFProcessor:
    """Processes TF-IDF scores for text segments.

    Computes Term Frequency-Inverse Document Frequency scores to
    complement semantic similarity scores in the hybrid scoring system.

    Attributes:
        documents_corpus: List of document texts
        word_frequencies: Word frequencies for each document
        document_frequencies: Document frequencies for each word
        total_documents: Total number of documents
        tfidf_ready: Whether TF-IDF computation is complete
    """

    def __init__(self):
        """Initialize TF-IDF processor."""
        self.documents_corpus: List[str] = []
        self.word_frequencies: List[Dict[str, int]] = []
        self.document_frequencies: Dict[str, int] = {}
        self.total_documents: int = 0
        self.tfidf_ready: bool = False

    def precompute(self, segments: List[TextSegment]) -> None:
        """Precompute TF-IDF values for a list of segments.

        Args:
            segments: List of text segments to process
        """
        start_time = time.time()

        # Reset previous computation
        self.documents_corpus = []
        self.word_frequencies = []
        self.document_frequencies = {}
        self.total_documents = 0
        self.tfidf_ready = False

        # Extract document texts
        self.documents_corpus = [seg.text for seg in segments]
        self.total_documents = len(self.documents_corpus)

        if self.total_documents == 0:
            return

        # Compute word frequencies for each document
        for doc in self.documents_corpus:
            words = doc.split()
            self.word_frequencies.append(Counter(words))

            # Update document frequencies
            unique_words = set(words)
            for word in unique_words:
                self.document_frequencies[word] = self.document_frequencies.get(word, 0) + 1

        self.tfidf_ready = True
        compute_time = (time.time() - start_time) * 1000
        print(f"✅ TF-IDF computed ({compute_time:.1f}ms)")

    def compute_score(self, query: str, segment_idx: int) -> float:
        """Compute TF-IDF similarity between query and segment.

        Args:
            query: Query string
            segment_idx: Index of the segment

        Returns:
            TF-IDF similarity score
        """
        if not self.tfidf_ready or segment_idx >= len(self.documents_corpus):
            return 0.0

        # Clean and split query (remove punctuation)
        import re
        query_words = re.findall(r'\b\w+\b', query.lower())
        segment_words = self.word_frequencies[segment_idx]

        if not query_words or not segment_words:
            return 0.0

        # Compute TF-IDF score
        score = 0.0
        for word in query_words:
            if word in segment_words:
                # Term frequency
                tf = segment_words[word] / len(segment_words)

                # Inverse document frequency
                df = self.document_frequencies.get(word, 0)
                if df > 0:
                    idf = math.log(self.total_documents / df)
                    score += tf * idf

        return score

    def compute_scores_batch(self, query: str, segment_indices: List[int]) -> np.ndarray:
        """Compute TF-IDF scores for multiple segments.

        Args:
            query: Query string
            segment_indices: List of segment indices

        Returns:
            Array of TF-IDF scores
        """
        scores = []
        for idx in segment_indices:
            score = self.compute_score(query, idx)
            scores.append(score)

        return np.array(scores)

    def get_top_terms(self, segment_idx: int, top_k: int = 10) -> List[Tuple[str, float]]:
        """Get top TF-IDF terms for a segment.

        Args:
            segment_idx: Index of the segment
            top_k: Number of top terms to return

        Returns:
            List of (term, tfidf_score) tuples
        """
        if not self.tfidf_ready or segment_idx >= len(self.documents_corpus):
            return []

        segment_words = self.word_frequencies[segment_idx]
        term_scores = []

        for word, count in segment_words.items():
            # Term frequency
            tf = count / len(segment_words)

            # Inverse document frequency
            df = self.document_frequencies.get(word, 0)
            if df > 0:
                idf = math.log(self.total_documents / df)
                tfidf_score = tf * idf
                term_scores.append((word, tfidf_score))

        # Sort by TF-IDF score and return top_k
        term_scores.sort(key=lambda x: x[1], reverse=True)
        return term_scores[:top_k]

    def get_vocabulary_size(self) -> int:
        """Get the size of the vocabulary.

        Returns:
            Number of unique terms across all documents
        """
        return len(self.document_frequencies)

    def get_document_frequency(self, term: str) -> int:
        """Get document frequency for a term.

        Args:
            term: Term to look up

        Returns:
            Number of documents containing the term
        """
        return self.document_frequencies.get(term, 0)

    def get_stats(self) -> Dict[str, Any]:
        """Get TF-IDF processor statistics.

        Returns:
            Dictionary with TF-IDF statistics
        """
        if not self.tfidf_ready:
            return {
                'ready': False,
                'total_documents': 0,
                'vocabulary_size': 0
            }

        return {
            'ready': True,
            'total_documents': self.total_documents,
            'vocabulary_size': self.get_vocabulary_size(),
            'avg_document_length': np.mean([len(doc.split()) for doc in self.documents_corpus]),
            'total_word_occurrences': sum(len(freq) for freq in self.word_frequencies)
        }

    def clear(self) -> None:
        """Clear all TF-IDF data."""
        self.documents_corpus.clear()
        self.word_frequencies.clear()
        self.document_frequencies.clear()
        self.total_documents = 0
        self.tfidf_ready = False
        print("✅ TF-IDF processor cleared")