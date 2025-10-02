"""
QualityController - Validation and filtering of generated content.

This module provides comprehensive quality assessment for synthetic documents,
ensuring only high-quality, coherent content makes it into training datasets.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import json

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

@dataclass
class QualityMetrics:
    """Quality metrics for a document."""
    coherence_score: float
    consistency_score: float
    readability_score: float
    diversity_score: float
    contradiction_rate: float
    entity_consistency: float
    grammar_score: float
    overall_score: float

class QualityDimension(Enum):
    """Dimensions of quality assessment."""
    COHERENCE = "coherence"
    CONSISTENCY = "consistency"
    READABILITY = "readability"
    DIVERSITY = "diversity"
    GRAMMAR = "grammar"
    ENTITY_TRACKING = "entity_tracking"

class QualityController:
    """
    Comprehensive quality controller for synthetic documents.

    This class evaluates generated documents across multiple quality dimensions
    and provides filtering and improvement suggestions.
    """

    def __init__(self, use_neural_metrics: bool = True):
        """
        Initialize the quality controller.

        Args:
            use_neural_metrics: Whether to use neural models for quality assessment
        """
        self.use_neural_metrics = use_neural_metrics
        self.logger = logging.getLogger(__name__)

        # Initialize neural models if requested
        self.sentence_model = None
        if use_neural_metrics:
            try:
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.logger.info("Loaded sentence transformer for quality assessment")
            except Exception as e:
                self.logger.warning(f"Failed to load sentence transformer: {str(e)}")
                self.use_neural_metrics = False

        # Quality assessment thresholds
        self.thresholds = {
            'min_coherence': 0.6,
            'min_consistency': 0.7,
            'min_readability': 0.5,
            'max_contradiction_rate': 0.15,
            'min_entity_consistency': 0.8,
            'min_grammar_score': 0.7
        }

        # Common words for readability assessment
        self.common_words = self._load_common_words()

        # Contradiction patterns
        self.contradiction_patterns = [
            (r'always', r'never'),
            (r'everyone', r'no one'),
            (r'everywhere', r'nowhere'),
            (r'everything', r'nothing'),
            (r'before', r'after'),
            (r'first', r'last'),
            (r'beginning', r'end')
        ]

    def evaluate_document(self, document: Dict[str, Any]) -> QualityMetrics:
        """
        Evaluate a document across all quality dimensions.

        Args:
            document: Document to evaluate

        Returns:
            QualityMetrics object with scores for all dimensions
        """
        try:
            content = document['content']

            # Calculate individual quality scores
            coherence_score = self._assess_coherence(content)
            consistency_score = self._assess_consistency(document)
            readability_score = self._assess_readability(content)
            diversity_score = self._assess_diversity(content)
            contradiction_rate = self._detect_contradictions(content)
            entity_consistency = self._assess_entity_consistency(document)
            grammar_score = self._assess_grammar(content)

            # Calculate overall score (weighted average)
            overall_score = self._calculate_overall_score(
                coherence_score, consistency_score, readability_score,
                diversity_score, contradiction_rate, entity_consistency, grammar_score
            )

            metrics = QualityMetrics(
                coherence_score=coherence_score,
                consistency_score=consistency_score,
                readability_score=readability_score,
                diversity_score=diversity_score,
                contradiction_rate=contradiction_rate,
                entity_consistency=entity_consistency,
                grammar_score=grammar_score,
                overall_score=overall_score
            )

            return metrics

        except Exception as e:
            self.logger.error(f"Error evaluating document {document.get('id', 'unknown')}: {str(e)}")

            # Return default metrics on error
            return QualityMetrics(
                coherence_score=0.5,
                consistency_score=0.5,
                readability_score=0.5,
                diversity_score=0.5,
                contradiction_rate=0.0,
                entity_consistency=0.5,
                grammar_score=0.5,
                overall_score=0.5
            )

    def _assess_coherence(self, content: str) -> float:
        """Assess the coherence of document content."""

        if not content:
            return 0.0

        # Split content into sentences
        sentences = self._split_into_sentences(content)

        if len(sentences) < 2:
            return 1.0  # Single sentence is trivially coherent

        coherence_score = 0.0

        if self.use_neural_metrics and self.sentence_model:
            # Use sentence transformer for semantic coherence
            try:
                embeddings = self.sentence_model.encode(sentences)

                # Calculate average cosine similarity between consecutive sentences
                similarities = []
                for i in range(len(embeddings) - 1):
                    similarity = np.dot(embeddings[i], embeddings[i + 1]) / (
                        np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i + 1])
                    )
                    similarities.append(similarity)

                coherence_score = np.mean(similarities) if similarities else 0.5

            except Exception as e:
                self.logger.warning(f"Neural coherence assessment failed: {str(e)}")
                coherence_score = self._assess_coherence_heuristic(sentences)
        else:
            # Use heuristic-based coherence assessment
            coherence_score = self._assess_coherence_heuristic(sentences)

        return max(0.0, min(1.0, coherence_score))

    def _assess_coherence_heuristic(self, sentences: List[str]) -> float:
        """Heuristic-based coherence assessment."""

        coherence_factors = []

        # Factor 1: Lexical overlap between consecutive sentences
        lexical_overlaps = []
        for i in range(len(sentences) - 1):
            words1 = set(sentences[i].lower().split())
            words2 = set(sentences[i + 1].lower().split())

            if words1 and words2:
                overlap = len(words1.intersection(words2)) / len(words1.union(words2))
                lexical_overlaps.append(overlap)

        if lexical_overlaps:
            coherence_factors.append(np.mean(lexical_overlaps))

        # Factor 2: Pronoun reference consistency
        pronoun_score = self._assess_pronoun_coherence(sentences)
        coherence_factors.append(pronoun_score)

        # Factor 3: Topic consistency
        topic_score = self._assess_topic_consistency(sentences)
        coherence_factors.append(topic_score)

        return np.mean(coherence_factors) if coherence_factors else 0.5

    def _assess_consistency(self, document: Dict[str, Any]) -> float:
        """Assess internal consistency of the document."""

        content = document['content']
        consistency_factors = []

        # Factor 1: Character name consistency
        character_consistency = self._check_character_name_consistency(content)
        consistency_factors.append(character_consistency)

        # Factor 2: Location name consistency
        location_consistency = self._check_location_name_consistency(content)
        consistency_factors.append(location_consistency)

        # Factor 3: Temporal consistency
        temporal_consistency = self._check_temporal_consistency(content)
        consistency_factors.append(temporal_consistency)

        # Factor 4: Factual consistency (within document)
        factual_consistency = self._check_factual_consistency(content)
        consistency_factors.append(factual_consistency)

        return np.mean(consistency_factors) if consistency_factors else 0.8

    def _assess_readability(self, content: str) -> float:
        """Assess the readability of the content."""

        if not content:
            return 0.0

        readability_factors = []

        # Factor 1: Average sentence length
        sentences = self._split_into_sentences(content)
        if sentences:
            avg_sentence_length = np.mean([len(s.split()) for s in sentences])
            # Optimal sentence length is around 15-20 words
            length_score = 1.0 - min(abs(avg_sentence_length - 17.5) / 17.5, 1.0)
            readability_factors.append(length_score)

        # Factor 2: Vocabulary complexity
        words = content.lower().split()
        if words:
            common_word_ratio = sum(1 for word in words if word in self.common_words) / len(words)
            readability_factors.append(common_word_ratio)

        # Factor 3: Sentence structure variety
        structure_variety = self._assess_sentence_structure_variety(sentences)
        readability_factors.append(structure_variety)

        return np.mean(readability_factors) if readability_factors else 0.5

    def _assess_diversity(self, content: str) -> float:
        """Assess the lexical and structural diversity of content."""

        words = content.lower().split()

        if len(words) < 10:
            return 0.5  # Too short to assess diversity

        diversity_factors = []

        # Factor 1: Lexical diversity (Type-Token Ratio)
        unique_words = set(words)
        ttr = len(unique_words) / len(words)
        diversity_factors.append(ttr)

        # Factor 2: Sentence length diversity
        sentences = self._split_into_sentences(content)
        if len(sentences) > 1:
            sentence_lengths = [len(s.split()) for s in sentences]
            length_std = np.std(sentence_lengths) / (np.mean(sentence_lengths) + 1)
            diversity_factors.append(min(length_std, 1.0))

        # Factor 3: Part-of-speech diversity (simplified)
        pos_diversity = self._assess_pos_diversity(words)
        diversity_factors.append(pos_diversity)

        return np.mean(diversity_factors) if diversity_factors else 0.5

    def _detect_contradictions(self, content: str) -> float:
        """Detect contradictions within the content."""

        content_lower = content.lower()
        contradictions_found = 0
        total_patterns_checked = 0

        for pattern1, pattern2 in self.contradiction_patterns:
            total_patterns_checked += 1

            # Check if both contradictory patterns appear
            if re.search(pattern1, content_lower) and re.search(pattern2, content_lower):
                # Check if they're in close proximity (potential contradiction)
                pattern1_matches = [(m.start(), m.end()) for m in re.finditer(pattern1, content_lower)]
                pattern2_matches = [(m.start(), m.end()) for m in re.finditer(pattern2, content_lower)]

                for p1_start, p1_end in pattern1_matches:
                    for p2_start, p2_end in pattern2_matches:
                        # If patterns are within 200 characters, consider it a potential contradiction
                        if abs(p1_start - p2_start) < 200:
                            contradictions_found += 1
                            break

        # Additional contradiction detection
        contradictions_found += self._detect_semantic_contradictions(content)

        # Calculate contradiction rate
        sentences = self._split_into_sentences(content)
        sentence_pairs = len(sentences) * (len(sentences) - 1) / 2 if len(sentences) > 1 else 1

        contradiction_rate = contradictions_found / max(sentence_pairs, 1)

        return min(contradiction_rate, 1.0)

    def _assess_entity_consistency(self, document: Dict[str, Any]) -> float:
        """Assess consistency of entity references within the document."""

        content = document['content']

        # Extract potential entity mentions
        entities = self._extract_entity_mentions(content)

        if not entities:
            return 1.0  # No entities to be inconsistent

        consistency_scores = []

        # Check each entity for consistent references
        for entity_name, mentions in entities.items():
            if len(mentions) > 1:
                # Check for consistent spelling and context
                spelling_consistency = self._check_entity_spelling_consistency(mentions)
                context_consistency = self._check_entity_context_consistency(entity_name, content)

                entity_score = (spelling_consistency + context_consistency) / 2
                consistency_scores.append(entity_score)

        return np.mean(consistency_scores) if consistency_scores else 1.0

    def _assess_grammar(self, content: str) -> float:
        """Assess grammatical correctness of the content."""

        # This is a simplified grammar assessment
        # In production, you might use a library like language_tool_python

        grammar_factors = []

        # Factor 1: Sentence completeness
        sentences = self._split_into_sentences(content)
        complete_sentences = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence[0].isupper() and sentence[-1] in '.!?':
                complete_sentences += 1

        if sentences:
            completeness_score = complete_sentences / len(sentences)
            grammar_factors.append(completeness_score)

        # Factor 2: Capitalization consistency
        capitalization_score = self._assess_capitalization(content)
        grammar_factors.append(capitalization_score)

        # Factor 3: Punctuation consistency
        punctuation_score = self._assess_punctuation(content)
        grammar_factors.append(punctuation_score)

        return np.mean(grammar_factors) if grammar_factors else 0.7

    def _calculate_overall_score(self, coherence: float, consistency: float, readability: float,
                               diversity: float, contradiction_rate: float, entity_consistency: float,
                               grammar: float) -> float:
        """Calculate weighted overall quality score."""

        # Weights for different quality dimensions
        weights = {
            'coherence': 0.25,
            'consistency': 0.20,
            'readability': 0.15,
            'diversity': 0.10,
            'contradiction_penalty': 0.15,
            'entity_consistency': 0.10,
            'grammar': 0.05
        }

        # Calculate weighted score
        score = (
            coherence * weights['coherence'] +
            consistency * weights['consistency'] +
            readability * weights['readability'] +
            diversity * weights['diversity'] +
            entity_consistency * weights['entity_consistency'] +
            grammar * weights['grammar']
        )

        # Apply contradiction penalty
        contradiction_penalty = contradiction_rate * weights['contradiction_penalty']
        score -= contradiction_penalty

        return max(0.0, min(1.0, score))

    # Helper methods

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting - could use more sophisticated methods
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _load_common_words(self) -> Set[str]:
        """Load a set of common English words."""
        # Simplified common words list
        common_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'she', 'or', 'an', 'will',
            'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out',
            'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can',
            'like', 'time', 'no', 'just', 'him', 'know', 'take', 'people', 'into',
            'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than',
            'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
            'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well',
            'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day',
            'most', 'us', 'is', 'water', 'long', 'find', 'here', 'thing', 'great',
            'right', 'move', 'try', 'man', 'hand', 'old', 'life', 'same', 'tell',
            'boy', 'follow', 'came', 'want', 'show', 'each', 'good', 'play', 'small',
            'end', 'put', 'home', 'read', 'hand', 'port', 'large', 'spell', 'add',
            'even', 'land', 'here', 'must', 'big', 'high', 'such', 'follow', 'act',
            'why', 'ask', 'men', 'change', 'went', 'light', 'kind', 'off', 'need',
            'house', 'picture', 'try', 'us', 'again', 'animal', 'point', 'mother',
            'world', 'near', 'build', 'self', 'earth', 'father'
        }

        return common_words

    def _assess_pronoun_coherence(self, sentences: List[str]) -> float:
        """Assess pronoun reference coherence."""

        pronouns = ['he', 'she', 'it', 'they', 'him', 'her', 'them', 'his', 'hers', 'its', 'their']
        coherence_scores = []

        for i, sentence in enumerate(sentences):
            sentence_words = sentence.lower().split()
            sentence_pronouns = [word for word in sentence_words if word in pronouns]

            if sentence_pronouns and i > 0:
                # Check if there are potential referents in previous sentences
                prev_sentence = sentences[i - 1].lower()
                has_referent = any(word[0].isupper() for word in sentences[i - 1].split())

                if has_referent:
                    coherence_scores.append(1.0)
                else:
                    coherence_scores.append(0.5)

        return np.mean(coherence_scores) if coherence_scores else 1.0

    def _assess_topic_consistency(self, sentences: List[str]) -> float:
        """Assess topic consistency across sentences."""

        if len(sentences) < 2:
            return 1.0

        # Simple topic consistency based on noun overlap
        all_nouns = []
        for sentence in sentences:
            # Simple noun extraction (words that are capitalized or end with common noun suffixes)
            words = sentence.split()
            nouns = [word for word in words if word[0].isupper() or
                    any(word.lower().endswith(suffix) for suffix in ['tion', 'ness', 'ment', 'ing'])]
            all_nouns.extend(nouns)

        if not all_nouns:
            return 0.5

        # Calculate how many sentences share common topics
        topic_consistency = 0.0
        for i in range(len(sentences) - 1):
            sentence1_nouns = set(word for word in sentences[i].split() if word in all_nouns)
            sentence2_nouns = set(word for word in sentences[i + 1].split() if word in all_nouns)

            if sentence1_nouns and sentence2_nouns:
                overlap = len(sentence1_nouns.intersection(sentence2_nouns))
                union = len(sentence1_nouns.union(sentence2_nouns))
                topic_consistency += overlap / union if union > 0 else 0

        return topic_consistency / (len(sentences) - 1) if len(sentences) > 1 else 1.0

    def _check_character_name_consistency(self, content: str) -> float:
        """Check for consistent character name usage."""

        # Extract potential character names (capitalized words)
        names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)

        if not names:
            return 1.0

        # Group similar names
        name_groups = {}
        for name in names:
            base_name = name.split()[0]  # First name
            if base_name not in name_groups:
                name_groups[base_name] = []
            name_groups[base_name].append(name)

        # Check consistency within groups
        consistency_scores = []
        for base_name, variations in name_groups.items():
            if len(variations) > 1:
                unique_variations = set(variations)
                consistency = 1.0 - (len(unique_variations) - 1) / len(variations)
                consistency_scores.append(consistency)

        return np.mean(consistency_scores) if consistency_scores else 1.0

    def _check_location_name_consistency(self, content: str) -> float:
        """Check for consistent location name usage."""

        # Look for location patterns
        location_patterns = [
            r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\bat\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\bto\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]

        locations = []
        for pattern in location_patterns:
            matches = re.findall(pattern, content)
            locations.extend(matches)

        if not locations:
            return 1.0

        # Check for consistent spelling
        location_counts = {}
        for location in locations:
            location_counts[location] = location_counts.get(location, 0) + 1

        # If all locations are mentioned consistently, score is high
        total_mentions = len(locations)
        unique_locations = len(location_counts)

        # Prefer fewer unique spellings for the same locations
        consistency = 1.0 - (unique_locations - 1) / max(total_mentions, 1)

        return max(0.0, min(1.0, consistency))

    def _check_temporal_consistency(self, content: str) -> float:
        """Check for temporal consistency."""

        # Look for temporal references
        temporal_patterns = [
            r'\b(yesterday|today|tomorrow)\b',
            r'\b(before|after|during)\b',
            r'\b(first|second|third|last|next)\b',
            r'\b(morning|afternoon|evening|night)\b'
        ]

        temporal_refs = []
        for pattern in temporal_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            temporal_refs.extend(matches)

        if len(temporal_refs) < 2:
            return 1.0  # Not enough temporal references to check

        # Simple temporal consistency check
        # This would be more sophisticated in a production system
        return 0.8  # Default temporal consistency score

    def _check_factual_consistency(self, content: str) -> float:
        """Check for factual consistency within the document."""

        # This is a simplified factual consistency check
        # In production, this would use more sophisticated NLI models

        sentences = self._split_into_sentences(content)

        if len(sentences) < 2:
            return 1.0

        # Look for potential factual statements
        factual_indicators = ['is', 'was', 'are', 'were', 'has', 'have', 'had']
        factual_sentences = []

        for sentence in sentences:
            if any(indicator in sentence.lower().split() for indicator in factual_indicators):
                factual_sentences.append(sentence)

        # Simple consistency check - no obvious contradictions
        if len(factual_sentences) > 1:
            # Check for direct contradictions (very simplified)
            contradiction_found = False
            for i in range(len(factual_sentences)):
                for j in range(i + 1, len(factual_sentences)):
                    if self._sentences_contradict(factual_sentences[i], factual_sentences[j]):
                        contradiction_found = True
                        break
                if contradiction_found:
                    break

            return 0.5 if contradiction_found else 0.9

        return 0.9

    def _assess_sentence_structure_variety(self, sentences: List[str]) -> float:
        """Assess variety in sentence structures."""

        if not sentences:
            return 0.0

        # Categorize sentences by structure
        structures = {'simple': 0, 'compound': 0, 'complex': 0}

        for sentence in sentences:
            if ',' in sentence or ';' in sentence or ' and ' in sentence or ' but ' in sentence:
                if 'because' in sentence.lower() or 'that' in sentence.lower() or 'which' in sentence.lower():
                    structures['complex'] += 1
                else:
                    structures['compound'] += 1
            else:
                structures['simple'] += 1

        # Calculate variety (entropy-based)
        total = sum(structures.values())
        if total == 0:
            return 0.0

        probabilities = [count / total for count in structures.values()]
        entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
        max_entropy = np.log2(len(structures))

        return entropy / max_entropy if max_entropy > 0 else 0.0

    def _assess_pos_diversity(self, words: List[str]) -> float:
        """Assess part-of-speech diversity (simplified)."""

        # Simple POS tagging based on common patterns
        pos_counts = {'noun': 0, 'verb': 0, 'adj': 0, 'adv': 0, 'other': 0}

        for word in words:
            if word.endswith('ly'):
                pos_counts['adv'] += 1
            elif word.endswith('ed') or word.endswith('ing'):
                pos_counts['verb'] += 1
            elif word.endswith('ful') or word.endswith('less') or word.endswith('ish'):
                pos_counts['adj'] += 1
            elif len(word) > 3 and word[0].isupper():
                pos_counts['noun'] += 1
            else:
                pos_counts['other'] += 1

        # Calculate diversity
        total = sum(pos_counts.values())
        if total == 0:
            return 0.0

        probabilities = [count / total for count in pos_counts.values()]
        entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
        max_entropy = np.log2(len(pos_counts))

        return entropy / max_entropy if max_entropy > 0 else 0.0

    def _detect_semantic_contradictions(self, content: str) -> int:
        """Detect semantic contradictions in content."""

        # Simple semantic contradiction detection
        contradictions = 0

        # Look for obvious contradictions
        if 'always' in content.lower() and 'never' in content.lower():
            contradictions += 1
        if 'all' in content.lower() and 'none' in content.lower():
            contradictions += 1
        if 'every' in content.lower() and 'no ' in content.lower():
            contradictions += 1

        return contradictions

    def _extract_entity_mentions(self, content: str) -> Dict[str, List[str]]:
        """Extract entity mentions from content."""

        # Extract potential entity names (capitalized words/phrases)
        entities = {}

        # Find capitalized words that could be names
        names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)

        for name in names:
            if name not in entities:
                entities[name] = []
            entities[name].append(name)

        return entities

    def _check_entity_spelling_consistency(self, mentions: List[str]) -> float:
        """Check spelling consistency for entity mentions."""

        if len(mentions) <= 1:
            return 1.0

        # Check if all mentions are exactly the same
        unique_spellings = set(mentions)
        consistency = 1.0 - (len(unique_spellings) - 1) / len(mentions)

        return max(0.0, consistency)

    def _check_entity_context_consistency(self, entity_name: str, content: str) -> float:
        """Check context consistency for an entity."""

        # Find all sentences mentioning this entity
        sentences = self._split_into_sentences(content)
        entity_sentences = [s for s in sentences if entity_name in s]

        if len(entity_sentences) <= 1:
            return 1.0

        # Simple context consistency check
        # In production, this would use more sophisticated methods
        return 0.8  # Default context consistency score

    def _assess_capitalization(self, content: str) -> float:
        """Assess capitalization consistency."""

        sentences = self._split_into_sentences(content)

        if not sentences:
            return 0.0

        properly_capitalized = 0
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence[0].isupper():
                properly_capitalized += 1

        return properly_capitalized / len(sentences)

    def _assess_punctuation(self, content: str) -> float:
        """Assess punctuation consistency."""

        sentences = self._split_into_sentences(content)

        if not sentences:
            return 0.0

        properly_punctuated = 0
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence[-1] in '.!?':
                properly_punctuated += 1

        return properly_punctuated / len(sentences)

    def _sentences_contradict(self, sentence1: str, sentence2: str) -> bool:
        """Check if two sentences contradict each other (simplified)."""

        # Very simple contradiction detection
        s1_lower = sentence1.lower()
        s2_lower = sentence2.lower()

        # Look for negation patterns
        if ('not' in s1_lower and 'not' not in s2_lower) or ('not' in s2_lower and 'not' not in s1_lower):
            # Check if they're talking about similar things
            s1_words = set(s1_lower.split())
            s2_words = set(s2_lower.split())

            overlap = len(s1_words.intersection(s2_words))
            if overlap > 2:  # Some shared context
                return True

        return False

    def batch_evaluate_documents(self, documents: List[Dict[str, Any]]) -> List[QualityMetrics]:
        """Evaluate multiple documents in batch."""

        results = []

        for doc in documents:
            metrics = self.evaluate_document(doc)
            results.append(metrics)

        return results

    def filter_by_quality(self, documents: List[Dict[str, Any]],
                         min_overall_score: float = 0.7) -> List[Dict[str, Any]]:
        """Filter documents by minimum quality score."""

        filtered_docs = []

        for doc in documents:
            metrics = self.evaluate_document(doc)
            if metrics.overall_score >= min_overall_score:
                # Add quality metrics to document metadata
                if 'metadata' not in doc:
                    doc['metadata'] = {}
                doc['metadata']['quality_metrics'] = {
                    'overall_score': metrics.overall_score,
                    'coherence_score': metrics.coherence_score,
                    'consistency_score': metrics.consistency_score,
                    'readability_score': metrics.readability_score
                }
                filtered_docs.append(doc)

        self.logger.info(f"Filtered {len(documents)} documents to {len(filtered_docs)} high-quality documents")

        return filtered_docs

    def get_quality_report(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a comprehensive quality report for a document collection."""

        if not documents:
            return {'error': 'No documents provided'}

        all_metrics = self.batch_evaluate_documents(documents)

        # Calculate aggregate statistics
        coherence_scores = [m.coherence_score for m in all_metrics]
        consistency_scores = [m.consistency_score for m in all_metrics]
        overall_scores = [m.overall_score for m in all_metrics]

        report = {
            'total_documents': len(documents),
            'average_scores': {
                'coherence': np.mean(coherence_scores),
                'consistency': np.mean(consistency_scores),
                'overall': np.mean(overall_scores)
            },
            'score_distribution': {
                'excellent': len([s for s in overall_scores if s >= 0.9]),
                'good': len([s for s in overall_scores if 0.8 <= s < 0.9]),
                'acceptable': len([s for s in overall_scores if 0.7 <= s < 0.8]),
                'poor': len([s for s in overall_scores if s < 0.7])
            },
            'quality_metrics': {
                'coherence': {
                    'mean': np.mean(coherence_scores),
                    'std': np.std(coherence_scores),
                    'min': np.min(coherence_scores),
                    'max': np.max(coherence_scores)
                },
                'consistency': {
                    'mean': np.mean(consistency_scores),
                    'std': np.std(consistency_scores),
                    'min': np.min(consistency_scores),
                    'max': np.max(consistency_scores)
                }
            }
        }

        return report