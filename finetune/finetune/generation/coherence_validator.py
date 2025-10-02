"""
Real-time Coherence Validation

Validates narrative coherence of generated text using multiple metrics
including semantic consistency, temporal logic, and character consistency.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer

try:
    from textstat import flesch_reading_ease, automated_readability_index
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False


class CoherenceValidator:
    """
    Real-time coherence validation for generated narrative text.

    Features:
    - Semantic coherence analysis
    - Temporal consistency checking
    - Character consistency validation
    - Readability assessment
    - Cross-document coherence validation
    """

    def __init__(
        self,
        use_semantic_model: bool = True,
        coherence_threshold: float = 0.6,
        cache_embeddings: bool = True,
    ):
        self.coherence_threshold = coherence_threshold
        self.cache_embeddings = cache_embeddings
        self.use_semantic_model = use_semantic_model

        # Initialize semantic model
        self.semantic_model = None
        if use_semantic_model:
            try:
                self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
                logging.info("Semantic coherence model loaded")
            except Exception as e:
                logging.warning(f"Failed to load semantic model: {e}")
                self.semantic_model = None

        # Caches
        self.embedding_cache = {} if cache_embeddings else None
        self.validation_cache = {}

    def validate_text(
        self,
        text: str,
        context: Optional[Dict] = None,
        previous_texts: Optional[List[str]] = None,
    ) -> float:
        """
        Validate overall coherence of a text.

        Args:
            text: Text to validate
            context: Optional context for consistency checking
            previous_texts: Previous texts for cross-document coherence

        Returns:
            Coherence score between 0 and 1
        """

        if not text.strip():
            return 0.0

        # Check cache
        cache_key = hash(text + str(context) if context else text)
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]

        scores = []

        # 1. Semantic coherence
        semantic_score = self._validate_semantic_coherence(text)
        scores.append(("semantic", semantic_score, 0.3))

        # 2. Structural coherence
        structural_score = self._validate_structural_coherence(text)
        scores.append(("structural", structural_score, 0.2))

        # 3. Temporal consistency
        temporal_score = self._validate_temporal_consistency(text)
        scores.append(("temporal", temporal_score, 0.2))

        # 4. Character consistency
        character_score = self._validate_character_consistency(text, context)
        scores.append(("character", character_score, 0.15))

        # 5. Readability
        readability_score = self._validate_readability(text)
        scores.append(("readability", readability_score, 0.15))

        # 6. Cross-document coherence (if applicable)
        if previous_texts:
            cross_doc_score = self._validate_cross_document_coherence(text, previous_texts)
            scores.append(("cross_document", cross_doc_score, 0.2))
            # Reweight other scores
            total_weight = sum(weight for _, _, weight in scores[:-1])
            scores = [(name, score, weight * 0.8 / total_weight) for name, score, weight in scores[:-1]] + [scores[-1]]

        # Calculate weighted average
        total_score = sum(score * weight for _, score, weight in scores)
        total_weight = sum(weight for _, _, weight in scores)
        final_score = total_score / total_weight if total_weight > 0 else 0.0

        # Cache result
        self.validation_cache[cache_key] = final_score

        logging.debug(f"Coherence validation: {final_score:.3f} - {dict((name, f'{score:.2f}') for name, score, _ in scores)}")

        return final_score

    def validate_coherence_between_texts(self, text1: str, text2: str) -> float:
        """Validate coherence between two related texts."""

        if not text1.strip() or not text2.strip():
            return 0.0

        # Semantic similarity
        semantic_similarity = self._calculate_semantic_similarity(text1, text2)

        # Character consistency
        char_consistency = self._validate_character_consistency_between_texts(text1, text2)

        # Temporal consistency
        temporal_consistency = self._validate_temporal_flow_between_texts(text1, text2)

        # Weighted combination
        coherence_score = (
            semantic_similarity * 0.4 +
            char_consistency * 0.3 +
            temporal_consistency * 0.3
        )

        return coherence_score

    def _validate_semantic_coherence(self, text: str) -> float:
        """Validate semantic coherence within the text."""

        if not self.semantic_model:
            return 0.7  # Default score without semantic model

        sentences = self._split_into_sentences(text)
        if len(sentences) < 2:
            return 1.0  # Single sentence is coherent

        try:
            # Get embeddings
            embeddings = []
            for sentence in sentences:
                if sentence.strip():
                    if self.embedding_cache and sentence in self.embedding_cache:
                        embedding = self.embedding_cache[sentence]
                    else:
                        embedding = self.semantic_model.encode([sentence])[0]
                        if self.embedding_cache:
                            self.embedding_cache[sentence] = embedding
                    embeddings.append(embedding)

            if len(embeddings) < 2:
                return 1.0

            # Calculate pairwise similarities
            similarities = []
            for i in range(len(embeddings) - 1):
                similarity = np.dot(embeddings[i], embeddings[i + 1]) / (
                    np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i + 1])
                )
                similarities.append(similarity)

            # Average similarity (higher is more coherent)
            avg_similarity = np.mean(similarities)

            # Convert to 0-1 scale (cosine similarity ranges from -1 to 1)
            normalized_score = (avg_similarity + 1) / 2

            return max(0.0, min(1.0, normalized_score))

        except Exception as e:
            logging.warning(f"Semantic coherence validation failed: {e}")
            return 0.7

    def _validate_structural_coherence(self, text: str) -> float:
        """Validate structural coherence (flow, transitions, organization)."""

        if not text.strip():
            return 0.0

        score_components = []

        # 1. Paragraph structure
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if len(paragraphs) > 1:
            # Good paragraph structure
            avg_paragraph_length = np.mean([len(p.split()) for p in paragraphs])
            if 20 <= avg_paragraph_length <= 150:  # Reasonable paragraph length
                score_components.append(0.8)
            else:
                score_components.append(0.5)
        else:
            score_components.append(0.6)  # Single paragraph is okay

        # 2. Sentence length variation
        sentences = self._split_into_sentences(text)
        if len(sentences) > 1:
            sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
            if sentence_lengths:
                length_std = np.std(sentence_lengths)
                length_mean = np.mean(sentence_lengths)
                if length_mean > 0:
                    coefficient_of_variation = length_std / length_mean
                    # Good variation in sentence length (not too uniform, not too chaotic)
                    if 0.2 <= coefficient_of_variation <= 0.8:
                        score_components.append(0.8)
                    else:
                        score_components.append(0.6)
                else:
                    score_components.append(0.5)
            else:
                score_components.append(0.5)
        else:
            score_components.append(0.7)

        # 3. Transition indicators
        transition_words = [
            "however", "therefore", "moreover", "furthermore", "nevertheless",
            "consequently", "meanwhile", "subsequently", "additionally", "thus",
            "hence", "accordingly", "specifically", "particularly", "indeed",
            "then", "next", "after", "before", "while", "during", "finally"
        ]

        words = text.lower().split()
        transition_count = sum(1 for word in words if word in transition_words)

        if len(words) > 0:
            transition_density = transition_count / len(words)
            # Optimal transition density is around 1-3%
            if 0.01 <= transition_density <= 0.03:
                score_components.append(0.9)
            elif 0.005 <= transition_density <= 0.05:
                score_components.append(0.7)
            else:
                score_components.append(0.5)
        else:
            score_components.append(0.5)

        return np.mean(score_components) if score_components else 0.5

    def _validate_temporal_consistency(self, text: str) -> float:
        """Validate temporal consistency and logical flow."""

        # Time expression patterns
        time_patterns = [
            (r'\b(yesterday|today|tomorrow)\b', 'relative_days'),
            (r'\b(morning|afternoon|evening|night|dawn|dusk)\b', 'day_parts'),
            (r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', 'weekdays'),
            (r'\b(spring|summer|autumn|fall|winter)\b', 'seasons'),
            (r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b', 'months'),
            (r'\b\d{1,2}:\d{2}\b', 'clock_times'),
            (r'\b(before|after|during|while|when|then|next|later|earlier|previously|subsequently)\b', 'sequence_words'),
        ]

        time_expressions = {}
        for pattern, category in time_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                time_expressions[category] = matches

        # No time expressions - neutral score
        if not time_expressions:
            return 0.8

        score_components = []

        # 1. Check for conflicting time references
        if 'relative_days' in time_expressions:
            # Check for consistency (shouldn't have "yesterday" and "tomorrow" in rapid succession)
            relative_days = time_expressions['relative_days']
            if len(set(relative_days)) > 2:  # Too many different relative time references
                score_components.append(0.4)
            else:
                score_components.append(0.8)

        # 2. Sequence word usage
        if 'sequence_words' in time_expressions:
            sequence_count = len(time_expressions['sequence_words'])
            word_count = len(text.split())
            if word_count > 0:
                sequence_density = sequence_count / word_count
                if 0.01 <= sequence_density <= 0.05:  # Good sequence indicator density
                    score_components.append(0.9)
                else:
                    score_components.append(0.7)

        # 3. Time consistency within categories
        for category, expressions in time_expressions.items():
            if category in ['day_parts', 'seasons', 'months']:
                if len(set(expressions)) <= 2:  # Not too many different references
                    score_components.append(0.8)
                else:
                    score_components.append(0.6)

        return np.mean(score_components) if score_components else 0.8

    def _validate_character_consistency(self, text: str, context: Optional[Dict] = None) -> float:
        """Validate character name consistency and character behavior."""

        # Extract potential character names
        characters = self._extract_character_names(text)

        if not characters:
            return 0.8  # No characters to validate

        score_components = []

        # 1. Name consistency (no variations of same character)
        name_variations = self._detect_name_variations(characters)
        if name_variations:
            score_components.append(0.6)  # Penalty for inconsistent naming
        else:
            score_components.append(1.0)

        # 2. Context consistency (if context provided)
        if context and "characters" in context:
            known_characters = set(context["characters"])
            text_characters = set(characters)

            # Check for new characters vs established ones
            overlap = len(known_characters.intersection(text_characters))
            if overlap > 0:
                consistency_ratio = overlap / len(text_characters) if text_characters else 0
                score_components.append(min(1.0, consistency_ratio + 0.3))  # Bonus for using established characters
            else:
                score_components.append(0.7)  # Neutral for new characters

        # 3. Character mention balance
        character_mentions = {}
        for char in characters:
            character_mentions[char] = len(re.findall(r'\b' + re.escape(char) + r'\b', text, re.IGNORECASE))

        if character_mentions:
            mention_counts = list(character_mentions.values())
            if len(mention_counts) > 1:
                # Check if character mentions are reasonably balanced
                mention_std = np.std(mention_counts)
                mention_mean = np.mean(mention_counts)
                if mention_mean > 0:
                    balance_score = max(0.3, 1.0 - (mention_std / mention_mean))
                    score_components.append(balance_score)
                else:
                    score_components.append(0.5)
            else:
                score_components.append(0.8)  # Single character is fine

        return np.mean(score_components) if score_components else 0.8

    def _validate_readability(self, text: str) -> float:
        """Validate text readability and quality."""

        if not text.strip():
            return 0.0

        score_components = []

        # 1. Basic text statistics
        words = text.split()
        sentences = self._split_into_sentences(text)

        if len(words) > 0 and len(sentences) > 0:
            avg_words_per_sentence = len(words) / len(sentences)
            # Optimal range: 10-20 words per sentence
            if 10 <= avg_words_per_sentence <= 20:
                score_components.append(0.9)
            elif 5 <= avg_words_per_sentence <= 30:
                score_components.append(0.7)
            else:
                score_components.append(0.5)

        # 2. Word length diversity
        if words:
            word_lengths = [len(word.strip('.,!?;:"()[]{}')) for word in words]
            if word_lengths:
                avg_word_length = np.mean(word_lengths)
                word_length_std = np.std(word_lengths)

                # Good average word length (4-6 characters) with some variation
                if 4 <= avg_word_length <= 6 and word_length_std >= 1:
                    score_components.append(0.8)
                else:
                    score_components.append(0.6)
            else:
                score_components.append(0.5)

        # 3. Formal readability metrics (if available)
        if TEXTSTAT_AVAILABLE:
            try:
                flesch_score = flesch_reading_ease(text)
                # Convert Flesch score to 0-1 scale
                # Flesch scores: 90-100 (very easy), 60-70 (standard), 30-50 (difficult)
                if 50 <= flesch_score <= 80:  # Good range for narrative
                    readability_score = 0.9
                elif 30 <= flesch_score <= 90:
                    readability_score = 0.7
                else:
                    readability_score = 0.5

                score_components.append(readability_score)

            except Exception:
                # Fallback if readability calculation fails
                score_components.append(0.7)

        # 4. Repetition check
        word_freq = {}
        for word in words:
            clean_word = word.lower().strip('.,!?;:"()[]{}')
            if len(clean_word) > 3:  # Only check longer words
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1

        if word_freq:
            max_freq = max(word_freq.values())
            total_words = len([w for w in words if len(w.strip('.,!?;:"()[]{}')) > 3])

            if total_words > 0:
                max_freq_ratio = max_freq / total_words
                # Penalize excessive repetition
                if max_freq_ratio > 0.1:  # More than 10% of content is one word
                    score_components.append(0.3)
                elif max_freq_ratio > 0.05:
                    score_components.append(0.6)
                else:
                    score_components.append(0.9)
            else:
                score_components.append(0.7)

        return np.mean(score_components) if score_components else 0.7

    def _validate_cross_document_coherence(self, current_text: str, previous_texts: List[str]) -> float:
        """Validate coherence with previous documents."""

        if not previous_texts:
            return 1.0

        # Calculate semantic similarity with most recent documents
        similarities = []
        for prev_text in previous_texts[-3:]:  # Check last 3 documents
            similarity = self._calculate_semantic_similarity(current_text, prev_text)
            similarities.append(similarity)

        if similarities:
            avg_similarity = np.mean(similarities)
            # Good cross-document coherence should have moderate similarity (not too high, not too low)
            if 0.3 <= avg_similarity <= 0.7:
                return 0.9
            elif 0.2 <= avg_similarity <= 0.8:
                return 0.7
            else:
                return 0.5

        return 0.8

    # Helper methods

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _extract_character_names(self, text: str) -> List[str]:
        """Extract potential character names from text."""
        # Look for capitalized words that could be names
        name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        potential_names = re.findall(name_pattern, text)

        # Filter out common non-name words
        common_words = {
            "The", "This", "That", "And", "But", "When", "Where", "Who", "What", "How",
            "Mr", "Mrs", "Ms", "Dr", "Sir", "Lady", "Lord", "King", "Queen", "Prince", "Princess",
            "Captain", "General", "Major", "Colonel", "Today", "Tomorrow", "Yesterday",
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
            "January", "February", "March", "April", "May", "June", "July", "August",
            "September", "October", "November", "December", "Spring", "Summer", "Autumn", "Winter"
        }

        character_names = []
        for name in potential_names:
            if name not in common_words and len(name) > 2:
                character_names.append(name)

        # Remove duplicates while preserving order
        seen = set()
        unique_names = []
        for name in character_names:
            if name not in seen:
                seen.add(name)
                unique_names.append(name)

        return unique_names

    def _detect_name_variations(self, names: List[str]) -> List[Tuple[str, str]]:
        """Detect potential variations of the same character name."""
        variations = []

        for i, name1 in enumerate(names):
            for j, name2 in enumerate(names[i+1:], i+1):
                # Check if names might be variations
                if self._could_be_same_character(name1, name2):
                    variations.append((name1, name2))

        return variations

    def _could_be_same_character(self, name1: str, name2: str) -> bool:
        """Check if two names could refer to the same character."""
        # Simple heuristics
        name1_parts = name1.split()
        name2_parts = name2.split()

        # Check for partial matches (e.g., "John Smith" vs "John")
        if len(name1_parts) != len(name2_parts):
            shorter = name1_parts if len(name1_parts) < len(name2_parts) else name2_parts
            longer = name2_parts if len(name1_parts) < len(name2_parts) else name1_parts

            # If all parts of shorter name are in longer name
            if all(part in longer for part in shorter):
                return True

        # Check for similar spelling (simple edit distance)
        if abs(len(name1) - len(name2)) <= 2:
            # Very simple similarity check
            similar_chars = sum(1 for c1, c2 in zip(name1.lower(), name2.lower()) if c1 == c2)
            similarity_ratio = similar_chars / max(len(name1), len(name2))
            if similarity_ratio > 0.8:
                return True

        return False

    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        if not self.semantic_model:
            return 0.5  # Default neutral similarity

        try:
            embeddings = self.semantic_model.encode([text1, text2])
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            # Convert from [-1, 1] to [0, 1]
            return (similarity + 1) / 2

        except Exception as e:
            logging.warning(f"Semantic similarity calculation failed: {e}")
            return 0.5

    def _validate_character_consistency_between_texts(self, text1: str, text2: str) -> float:
        """Validate character consistency between two texts."""
        chars1 = set(self._extract_character_names(text1))
        chars2 = set(self._extract_character_names(text2))

        if not chars1 and not chars2:
            return 1.0  # No characters in either text

        if not chars1 or not chars2:
            return 0.7  # One text has characters, other doesn't

        # Calculate overlap
        overlap = len(chars1.intersection(chars2))
        total_unique = len(chars1.union(chars2))

        if total_unique == 0:
            return 1.0

        consistency_ratio = overlap / total_unique
        return min(1.0, consistency_ratio + 0.3)  # Bonus for some character overlap

    def _validate_temporal_flow_between_texts(self, text1: str, text2: str) -> float:
        """Validate temporal flow between two texts."""
        # This is a simplified version - could be enhanced with more sophisticated temporal analysis

        # Look for sequence indicators in second text that reference first
        sequence_indicators = [
            "then", "next", "after", "later", "subsequently", "following", "meanwhile", "afterwards"
        ]

        text2_lower = text2.lower()
        sequence_count = sum(1 for indicator in sequence_indicators if indicator in text2_lower)

        # Basic scoring based on presence of sequence indicators
        if sequence_count > 0:
            return min(1.0, 0.7 + (sequence_count * 0.1))
        else:
            return 0.6  # Neutral score if no explicit temporal connections