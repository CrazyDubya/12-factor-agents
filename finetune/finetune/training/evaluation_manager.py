"""
Evaluation Manager for Narrative Coherence Assessment

Implements comprehensive evaluation metrics for narrative generation models,
including coherence, consistency, creativity, and quality assessment.
"""

import json
import logging
import math
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from textstat import flesch_reading_ease, flesch_kincaid_grade
from transformers import AutoTokenizer, pipeline

from ..config import TrainingConfig


@dataclass
class EvaluationMetrics:
    """Container for comprehensive evaluation metrics."""

    # Core metrics
    perplexity: float = 0.0
    loss: float = 0.0

    # Coherence metrics
    semantic_coherence: float = 0.0
    narrative_flow: float = 0.0
    temporal_consistency: float = 0.0
    character_consistency: float = 0.0

    # Quality metrics
    grammar_score: float = 0.0
    readability_score: float = 0.0
    creativity_score: float = 0.0
    diversity_score: float = 0.0

    # Content metrics
    entity_consistency: float = 0.0
    factual_consistency: float = 0.0
    emotional_consistency: float = 0.0

    # Technical metrics
    repetition_penalty: float = 0.0
    length_consistency: float = 0.0
    vocabulary_richness: float = 0.0

    # Overall scores
    overall_coherence: float = 0.0
    overall_quality: float = 0.0
    overall_score: float = 0.0

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary."""
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }

    def __str__(self) -> str:
        """String representation of metrics."""
        return f"Overall: {self.overall_score:.3f} | Coherence: {self.overall_coherence:.3f} | Quality: {self.overall_quality:.3f}"


class EvaluationManager:
    """
    Comprehensive evaluation manager for narrative generation models.

    Features:
    - Multi-dimensional coherence assessment
    - Cross-document consistency validation
    - Creative writing quality metrics
    - Automated and human-interpretable scoring
    """

    def __init__(
        self,
        use_gpu: bool = True,
        cache_embeddings: bool = True,
    ):
        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.cache_embeddings = cache_embeddings
        self.device = "cuda" if self.use_gpu else "cpu"

        # Initialize models
        self._setup_evaluation_models()

        # Caches
        self.embedding_cache = {} if cache_embeddings else None
        self.sentiment_cache = {}

    def _setup_evaluation_models(self):
        """Initialize evaluation models and pipelines."""
        try:
            # Sentence transformer for semantic similarity
            self.sentence_model = SentenceTransformer(
                'all-MiniLM-L6-v2',
                device=self.device
            )

            # Sentiment analysis pipeline
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if self.use_gpu else -1,
                return_all_scores=True,
            )

            # Grammar checker (lightweight)
            self.grammar_checker = pipeline(
                "text-classification",
                model="textattack/roberta-base-CoLA",
                device=0 if self.use_gpu else -1,
            )

            logging.info("Evaluation models loaded successfully")

        except Exception as e:
            logging.warning(f"Some evaluation models failed to load: {e}")
            # Fallback to basic evaluation
            self.sentence_model = None
            self.sentiment_analyzer = None
            self.grammar_checker = None

    def evaluate_narrative_quality(
        self,
        model,
        tokenizer: AutoTokenizer,
        eval_data: List[Dict],
        config: TrainingConfig,
        max_samples: int = 100,
    ) -> Dict:
        """
        Comprehensive narrative quality evaluation.

        Args:
            model: The model to evaluate
            tokenizer: Model tokenizer
            eval_data: Evaluation dataset
            config: Training configuration
            max_samples: Maximum samples to evaluate

        Returns:
            Dictionary of evaluation metrics
        """

        logging.info("Starting comprehensive narrative evaluation")
        start_time = time.time()

        # Sample evaluation data
        eval_samples = eval_data[:max_samples] if len(eval_data) > max_samples else eval_data

        # Generate model outputs
        generated_texts = self._generate_evaluation_outputs(
            model, tokenizer, eval_samples, config
        )

        # Evaluate different aspects
        coherence_metrics = self._evaluate_coherence(generated_texts, eval_samples)
        quality_metrics = self._evaluate_quality(generated_texts)
        consistency_metrics = self._evaluate_consistency(generated_texts, eval_samples)
        creativity_metrics = self._evaluate_creativity(generated_texts)

        # Compute overall metrics
        overall_metrics = self._compute_overall_metrics(
            coherence_metrics,
            quality_metrics,
            consistency_metrics,
            creativity_metrics,
        )

        # Create final evaluation result
        evaluation_result = {
            **coherence_metrics,
            **quality_metrics,
            **consistency_metrics,
            **creativity_metrics,
            **overall_metrics,
            "evaluation_time": time.time() - start_time,
            "num_samples": len(eval_samples),
            "model_info": {
                "name": getattr(model, 'name_or_path', 'unknown'),
                "device": str(model.device) if hasattr(model, 'device') else 'unknown',
            }
        }

        logging.info(f"Evaluation completed in {evaluation_result['evaluation_time']:.2f}s")
        return evaluation_result

    def _generate_evaluation_outputs(
        self,
        model,
        tokenizer: AutoTokenizer,
        eval_samples: List[Dict],
        config: TrainingConfig,
    ) -> List[str]:
        """Generate model outputs for evaluation."""

        model.eval()
        generated_texts = []

        with torch.no_grad():
            for sample in eval_samples:
                # Extract prompt (assuming 'input' or 'prompt' field)
                prompt = sample.get('input', sample.get('prompt', sample.get('text', '')))
                if not prompt:
                    continue

                # Tokenize
                inputs = tokenizer(
                    prompt,
                    return_tensors="pt",
                    truncation=True,
                    max_length=config.max_sequence_length // 2,
                ).to(model.device)

                # Generate
                try:
                    outputs = model.generate(
                        **inputs,
                        max_new_tokens=min(512, config.max_sequence_length // 4),
                        temperature=0.8,
                        top_p=0.9,
                        do_sample=True,
                        pad_token_id=tokenizer.eos_token_id,
                    )

                    # Decode only new tokens
                    generated_text = tokenizer.decode(
                        outputs[0][inputs["input_ids"].shape[1]:],
                        skip_special_tokens=True,
                    )

                    generated_texts.append(generated_text.strip())

                except Exception as e:
                    logging.warning(f"Generation failed for sample: {e}")
                    generated_texts.append("")

        return generated_texts

    def _evaluate_coherence(
        self,
        generated_texts: List[str],
        eval_samples: List[Dict],
    ) -> Dict:
        """Evaluate narrative coherence metrics."""

        coherence_scores = []
        narrative_flow_scores = []
        temporal_scores = []

        for text in generated_texts:
            if not text.strip():
                coherence_scores.append(0.0)
                narrative_flow_scores.append(0.0)
                temporal_scores.append(0.0)
                continue

            # Semantic coherence via sentence similarity
            coherence = self._compute_semantic_coherence(text)
            coherence_scores.append(coherence)

            # Narrative flow via transition smoothness
            flow = self._compute_narrative_flow(text)
            narrative_flow_scores.append(flow)

            # Temporal consistency via timeline markers
            temporal = self._compute_temporal_consistency(text)
            temporal_scores.append(temporal)

        return {
            "semantic_coherence": np.mean(coherence_scores) if coherence_scores else 0.0,
            "narrative_flow": np.mean(narrative_flow_scores) if narrative_flow_scores else 0.0,
            "temporal_consistency": np.mean(temporal_scores) if temporal_scores else 0.0,
        }

    def _evaluate_quality(self, generated_texts: List[str]) -> Dict:
        """Evaluate text quality metrics."""

        grammar_scores = []
        readability_scores = []
        vocab_richness_scores = []
        repetition_scores = []

        for text in generated_texts:
            if not text.strip():
                grammar_scores.append(0.0)
                readability_scores.append(0.0)
                vocab_richness_scores.append(0.0)
                repetition_scores.append(0.0)
                continue

            # Grammar score
            grammar = self._compute_grammar_score(text)
            grammar_scores.append(grammar)

            # Readability
            try:
                readability = flesch_reading_ease(text) / 100.0  # Normalize to 0-1
                readability = max(0.0, min(1.0, readability))  # Clamp
            except:
                readability = 0.5  # Neutral score on error

            readability_scores.append(readability)

            # Vocabulary richness
            vocab_richness = self._compute_vocabulary_richness(text)
            vocab_richness_scores.append(vocab_richness)

            # Repetition penalty
            repetition = self._compute_repetition_penalty(text)
            repetition_scores.append(repetition)

        return {
            "grammar_score": np.mean(grammar_scores) if grammar_scores else 0.0,
            "readability_score": np.mean(readability_scores) if readability_scores else 0.0,
            "vocabulary_richness": np.mean(vocab_richness_scores) if vocab_richness_scores else 0.0,
            "repetition_penalty": np.mean(repetition_scores) if repetition_scores else 0.0,
        }

    def _evaluate_consistency(
        self,
        generated_texts: List[str],
        eval_samples: List[Dict],
    ) -> Dict:
        """Evaluate cross-document consistency."""

        entity_consistency_scores = []
        character_consistency_scores = []
        factual_consistency_scores = []

        # Extract entities and characters from generated texts
        all_entities = []
        all_characters = []

        for text in generated_texts:
            entities = self._extract_entities(text)
            characters = self._extract_characters(text)

            all_entities.append(entities)
            all_characters.append(characters)

        # Compute consistency across documents
        entity_consistency = self._compute_entity_consistency(all_entities)
        character_consistency = self._compute_character_consistency(all_characters)

        # Factual consistency (simplified)
        factual_consistency = self._compute_factual_consistency(generated_texts, eval_samples)

        return {
            "entity_consistency": entity_consistency,
            "character_consistency": character_consistency,
            "factual_consistency": factual_consistency,
        }

    def _evaluate_creativity(self, generated_texts: List[str]) -> Dict:
        """Evaluate creativity and diversity metrics."""

        creativity_scores = []
        diversity_scores = []

        # Overall diversity across all texts
        all_text = " ".join(generated_texts)
        overall_diversity = self._compute_text_diversity(all_text)

        for text in generated_texts:
            if not text.strip():
                creativity_scores.append(0.0)
                continue

            # Creativity via novelty and unexpectedness
            creativity = self._compute_creativity_score(text)
            creativity_scores.append(creativity)

        # Individual text diversity
        for text in generated_texts:
            diversity = self._compute_text_diversity(text)
            diversity_scores.append(diversity)

        return {
            "creativity_score": np.mean(creativity_scores) if creativity_scores else 0.0,
            "diversity_score": np.mean(diversity_scores) if diversity_scores else 0.0,
            "overall_diversity": overall_diversity,
        }

    def _compute_overall_metrics(
        self,
        coherence_metrics: Dict,
        quality_metrics: Dict,
        consistency_metrics: Dict,
        creativity_metrics: Dict,
    ) -> Dict:
        """Compute weighted overall metrics."""

        # Coherence composite
        overall_coherence = (
            coherence_metrics.get("semantic_coherence", 0.0) * 0.4 +
            coherence_metrics.get("narrative_flow", 0.0) * 0.3 +
            coherence_metrics.get("temporal_consistency", 0.0) * 0.3
        )

        # Quality composite
        overall_quality = (
            quality_metrics.get("grammar_score", 0.0) * 0.3 +
            quality_metrics.get("readability_score", 0.0) * 0.2 +
            quality_metrics.get("vocabulary_richness", 0.0) * 0.25 +
            (1.0 - quality_metrics.get("repetition_penalty", 0.0)) * 0.25  # Invert penalty
        )

        # Consistency composite
        overall_consistency = (
            consistency_metrics.get("entity_consistency", 0.0) * 0.4 +
            consistency_metrics.get("character_consistency", 0.0) * 0.4 +
            consistency_metrics.get("factual_consistency", 0.0) * 0.2
        )

        # Creativity composite
        overall_creativity = (
            creativity_metrics.get("creativity_score", 0.0) * 0.6 +
            creativity_metrics.get("diversity_score", 0.0) * 0.4
        )

        # Final overall score
        overall_score = (
            overall_coherence * 0.35 +
            overall_quality * 0.25 +
            overall_consistency * 0.25 +
            overall_creativity * 0.15
        )

        return {
            "overall_coherence": overall_coherence,
            "overall_quality": overall_quality,
            "overall_consistency": overall_consistency,
            "overall_creativity": overall_creativity,
            "overall_score": overall_score,
        }

    # Helper methods for specific metric computations

    def _compute_semantic_coherence(self, text: str) -> float:
        """Compute semantic coherence via sentence embeddings."""
        if not self.sentence_model or not text.strip():
            return 0.0

        sentences = self._split_sentences(text)
        if len(sentences) < 2:
            return 1.0  # Single sentence is coherent

        try:
            # Get sentence embeddings
            embeddings = self.sentence_model.encode(sentences)

            # Compute pairwise similarities
            similarities = []
            for i in range(len(embeddings) - 1):
                sim = cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
                similarities.append(sim)

            return np.mean(similarities)

        except Exception as e:
            logging.warning(f"Semantic coherence computation failed: {e}")
            return 0.5

    def _compute_narrative_flow(self, text: str) -> float:
        """Compute narrative flow via transition indicators."""
        if not text.strip():
            return 0.0

        # Transition words and phrases
        transitions = [
            "then", "next", "after", "before", "meanwhile", "suddenly",
            "however", "therefore", "consequently", "furthermore",
            "in addition", "on the other hand", "as a result",
        ]

        words = text.lower().split()
        transition_count = sum(1 for word in words if word in transitions)

        # Score based on transition density
        if len(words) == 0:
            return 0.0

        transition_density = transition_count / len(words)
        # Normalize (good flow is around 2-5% transitions)
        optimal_density = 0.03
        score = 1.0 - abs(transition_density - optimal_density) / optimal_density
        return max(0.0, min(1.0, score))

    def _compute_temporal_consistency(self, text: str) -> float:
        """Compute temporal consistency via time markers."""
        if not text.strip():
            return 0.0

        # Time indicators
        time_patterns = [
            r'\b(yesterday|today|tomorrow)\b',
            r'\b(morning|afternoon|evening|night)\b',
            r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
            r'\b\d{1,2}:\d{2}\b',  # Times
            r'\b\d{4}\b',  # Years
        ]

        time_references = []
        for pattern in time_patterns:
            matches = re.findall(pattern, text.lower())
            time_references.extend(matches)

        # Simple heuristic: consistent if reasonable number of time references
        if len(time_references) == 0:
            return 0.8  # Neutral - no temporal confusion

        # Too many time references might indicate confusion
        words = len(text.split())
        time_density = len(time_references) / words if words > 0 else 0

        if time_density > 0.1:  # More than 10% time words
            return 0.3  # Likely temporal confusion
        elif time_density > 0.05:
            return 0.6  # Moderate temporal density
        else:
            return 0.9  # Good temporal consistency

    def _compute_grammar_score(self, text: str) -> float:
        """Compute grammar score."""
        if not self.grammar_checker or not text.strip():
            return 0.5  # Neutral score

        try:
            # Split into sentences for better evaluation
            sentences = self._split_sentences(text)
            scores = []

            for sentence in sentences[:5]:  # Limit to first 5 sentences
                if len(sentence.strip()) < 5:
                    continue

                result = self.grammar_checker(sentence)
                if result and len(result) > 0:
                    # Assuming binary classification (ACCEPTABLE/UNACCEPTABLE)
                    score = result[0].get('score', 0.5)
                    if result[0].get('label') == 'UNACCEPTABLE':
                        score = 1.0 - score
                    scores.append(score)

            return np.mean(scores) if scores else 0.5

        except Exception as e:
            logging.warning(f"Grammar scoring failed: {e}")
            return 0.5

    def _compute_vocabulary_richness(self, text: str) -> float:
        """Compute vocabulary richness (TTR - Type-Token Ratio)."""
        if not text.strip():
            return 0.0

        words = re.findall(r'\b\w+\b', text.lower())
        if len(words) == 0:
            return 0.0

        unique_words = set(words)
        ttr = len(unique_words) / len(words)

        # Adjust for text length (longer texts naturally have lower TTR)
        if len(words) > 100:
            ttr = ttr * 1.2  # Boost for longer texts
        elif len(words) < 20:
            ttr = ttr * 0.8  # Penalize very short texts

        return min(1.0, ttr)

    def _compute_repetition_penalty(self, text: str) -> float:
        """Compute repetition penalty."""
        if not text.strip():
            return 0.0

        words = re.findall(r'\b\w+\b', text.lower())
        if len(words) == 0:
            return 0.0

        # Check for repeated phrases
        phrases = []
        for i in range(len(words) - 2):
            phrase = " ".join(words[i:i+3])
            phrases.append(phrase)

        phrase_counts = Counter(phrases)
        repeated_phrases = sum(1 for count in phrase_counts.values() if count > 1)

        # Penalty based on repetition
        if len(phrases) == 0:
            return 0.0

        repetition_ratio = repeated_phrases / len(phrases)
        return min(1.0, repetition_ratio * 2)  # Scale penalty

    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities (simplified version)."""
        # Simple pattern-based entity extraction
        entities = []

        # Capitalized words (potential proper nouns)
        entity_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        matches = re.findall(entity_pattern, text)
        entities.extend(matches)

        return list(set(entities))  # Remove duplicates

    def _extract_characters(self, text: str) -> List[str]:
        """Extract character names (simplified version)."""
        # Look for potential character names
        character_patterns = [
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # First Last
            r'\b(?:Mr\.|Mrs\.|Ms\.|Dr\.)\s+[A-Z][a-z]+\b',  # Title Name
        ]

        characters = []
        for pattern in character_patterns:
            matches = re.findall(pattern, text)
            characters.extend(matches)

        return list(set(characters))

    def _compute_entity_consistency(self, all_entities: List[List[str]]) -> float:
        """Compute consistency of entity usage across documents."""
        if not all_entities:
            return 1.0

        # Flatten all entities
        all_entity_names = [entity for entities in all_entities for entity in entities]
        if not all_entity_names:
            return 1.0

        # Count entity usage
        entity_counts = Counter(all_entity_names)
        total_entities = len(all_entity_names)
        unique_entities = len(entity_counts)

        # Consistency is higher when entities are reused appropriately
        if unique_entities == 0:
            return 1.0

        reuse_ratio = (total_entities - unique_entities) / total_entities
        return min(1.0, reuse_ratio * 2)  # Scale to 0-1

    def _compute_character_consistency(self, all_characters: List[List[str]]) -> float:
        """Compute character consistency across documents."""
        return self._compute_entity_consistency(all_characters)  # Similar logic

    def _compute_factual_consistency(
        self,
        generated_texts: List[str],
        eval_samples: List[Dict],
    ) -> float:
        """Compute factual consistency (simplified version)."""
        # For now, return a neutral score
        # In a full implementation, this would check facts against a knowledge base
        return 0.7

    def _compute_creativity_score(self, text: str) -> float:
        """Compute creativity score based on linguistic features."""
        if not text.strip():
            return 0.0

        # Simple creativity indicators
        creativity_indicators = [
            r'\b(imagine|dream|fantasy|magic|wonder)\b',
            r'\b(suddenly|unexpectedly|amazingly|incredibly)\b',
            r'\b(unique|unusual|extraordinary|remarkable)\b',
        ]

        words = text.lower().split()
        if len(words) == 0:
            return 0.0

        creative_word_count = 0
        for pattern in creativity_indicators:
            matches = re.findall(pattern, text.lower())
            creative_word_count += len(matches)

        # Metaphor detection (simplified)
        metaphor_patterns = [
            r'\bis like\b', r'\bas.*as\b', r'\bmetaphor\b', r'\bsymbol\b'
        ]

        metaphor_count = 0
        for pattern in metaphor_patterns:
            matches = re.findall(pattern, text.lower())
            metaphor_count += len(matches)

        # Combine indicators
        creativity_density = (creative_word_count + metaphor_count * 2) / len(words)
        return min(1.0, creativity_density * 10)  # Scale appropriately

    def _compute_text_diversity(self, text: str) -> float:
        """Compute text diversity via lexical and syntactic variety."""
        if not text.strip():
            return 0.0

        words = re.findall(r'\b\w+\b', text.lower())
        if len(words) == 0:
            return 0.0

        # Lexical diversity (TTR)
        unique_words = set(words)
        lexical_diversity = len(unique_words) / len(words)

        # Sentence length diversity
        sentences = self._split_sentences(text)
        if len(sentences) < 2:
            syntactic_diversity = 0.5
        else:
            sentence_lengths = [len(s.split()) for s in sentences]
            syntactic_diversity = np.std(sentence_lengths) / np.mean(sentence_lengths) if np.mean(sentence_lengths) > 0 else 0

        # Combine measures
        diversity = (lexical_diversity * 0.7 + min(1.0, syntactic_diversity) * 0.3)
        return min(1.0, diversity)

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]


def create_evaluation_metrics(**kwargs) -> EvaluationMetrics:
    """Factory function to create evaluation metrics."""
    return EvaluationMetrics(**kwargs)