"""
Evidence classification system for relationships between elected officials.
Uses ML-based approaches to classify evidence strength and relationship types.
"""
import asyncio
from typing import Dict, List, Optional, Tuple, Set, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import re
import json
from collections import defaultdict, Counter
import structlog

# ML and NLP imports
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

from data.staten_island_officials import STATEN_ISLAND_OFFICIALS
from analyzers.relationship_tracker import EvidenceStrength

logger = structlog.get_logger()


class EvidenceType(Enum):
    """Types of evidence for relationships."""
    LEGISLATIVE_COOPERATION = "legislative_cooperation"
    PUBLIC_STATEMENTS = "public_statements"
    JOINT_INITIATIVES = "joint_initiatives"
    VOTING_PATTERNS = "voting_patterns"
    CAMPAIGN_SUPPORT = "campaign_support"
    MEDIA_APPEARANCES = "media_appearances"
    FUNDING_COORDINATION = "funding_coordination"
    POLICY_ALIGNMENT = "policy_alignment"


class RelationshipDimension(Enum):
    """Dimensions of political relationships."""
    COOPERATION_LEVEL = "cooperation_level"
    IDEOLOGICAL_ALIGNMENT = "ideological_alignment"
    STRATEGIC_COORDINATION = "strategic_coordination"
    PUBLIC_VISIBILITY = "public_visibility"
    TEMPORAL_CONSISTENCY = "temporal_consistency"
    OUTCOME_EFFECTIVENESS = "outcome_effectiveness"


@dataclass
class EvidenceClassification:
    """Classification result for a piece of evidence."""
    evidence_text: str
    evidence_type: EvidenceType
    strength: EvidenceStrength
    confidence: float
    sentiment_score: float
    key_features: List[str]
    relationship_indicators: Dict[str, float]
    temporal_context: Dict[str, Any]


@dataclass
class RelationshipClassification:
    """Complete classification of a relationship."""
    official_1: str
    official_2: str
    evidence_classifications: List[EvidenceClassification]
    overall_strength: EvidenceStrength
    relationship_dimensions: Dict[RelationshipDimension, float]
    confidence_score: float
    classification_summary: str
    supporting_features: List[str]


class EvidenceClassifier:
    """ML-based classifier for relationship evidence."""

    def __init__(self):
        self.vectorizer = None
        self.sentiment_analyzer = None
        self.cooperation_patterns = None
        self.evidence_features = None
        self._initialize_nlp_tools()
        self._initialize_classification_patterns()

    def _initialize_nlp_tools(self):
        """Initialize NLP tools and models."""
        try:
            # Download required NLTK data
            nltk.download('vader_lexicon', quiet=True)
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)

            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 3),
                min_df=2
            )

            logger.info("NLP tools initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize NLP tools", error=str(e))
            self.sentiment_analyzer = None

    def _initialize_classification_patterns(self):
        """Initialize patterns for evidence classification."""
        self.cooperation_patterns = {
            EvidenceType.LEGISLATIVE_COOPERATION: {
                "keywords": [
                    "co-sponsored", "jointly introduced", "bipartisan", "collaborated",
                    "worked together", "joint legislation", "cooperative effort",
                    "cross-party", "united front", "shared bill"
                ],
                "strength_modifiers": {
                    "jointly": 0.9,
                    "together": 0.8,
                    "coordinated": 0.8,
                    "collaborated": 0.9,
                    "co-sponsored": 0.9,
                    "partnered": 0.8
                }
            },
            EvidenceType.PUBLIC_STATEMENTS: {
                "keywords": [
                    "praised", "commended", "supports", "agrees with", "echoes",
                    "backs", "endorses", "stands with", "aligns with",
                    "joint statement", "shared position"
                ],
                "strength_modifiers": {
                    "strongly": 0.9,
                    "fully": 0.8,
                    "completely": 0.9,
                    "wholeheartedly": 0.9,
                    "unequivocally": 0.9
                }
            },
            EvidenceType.JOINT_INITIATIVES: {
                "keywords": [
                    "joint initiative", "collaborative project", "shared effort",
                    "coordinated response", "unified approach", "joint proposal",
                    "cooperative program", "partnership", "alliance"
                ],
                "strength_modifiers": {
                    "landmark": 0.9,
                    "historic": 0.9,
                    "unprecedented": 0.8,
                    "groundbreaking": 0.8,
                    "significant": 0.7
                }
            },
            EvidenceType.VOTING_PATTERNS: {
                "keywords": [
                    "voted together", "similar voting", "consistent votes",
                    "aligned voting", "same position", "parallel votes",
                    "matching record", "synchronized"
                ],
                "strength_modifiers": {
                    "consistently": 0.9,
                    "always": 0.9,
                    "frequently": 0.7,
                    "often": 0.6,
                    "regularly": 0.8
                }
            },
            EvidenceType.CAMPAIGN_SUPPORT: {
                "keywords": [
                    "endorsed", "campaigned for", "supported candidacy",
                    "fundraised for", "backed campaign", "political support",
                    "election support", "endorsement"
                ],
                "strength_modifiers": {
                    "early": 0.8,
                    "strong": 0.8,
                    "enthusiastic": 0.9,
                    "public": 0.7,
                    "vocal": 0.8
                }
            }
        }

        self.evidence_features = {
            "cooperation_indicators": [
                "jointly", "together", "partnership", "collaboration", "coordination",
                "unified", "shared", "common", "mutual", "collective"
            ],
            "strength_indicators": [
                "strong", "solid", "robust", "significant", "substantial",
                "important", "major", "key", "critical", "vital"
            ],
            "temporal_indicators": [
                "ongoing", "continued", "long-term", "sustained", "consistent",
                "regular", "persistent", "enduring", "lasting"
            ],
            "outcome_indicators": [
                "successful", "achieved", "accomplished", "secured", "delivered",
                "resulted", "produced", "generated", "created", "established"
            ]
        }

    async def classify_evidence(self, evidence_text: str, officials: Tuple[str, str],
                              context: Dict[str, Any] = None) -> EvidenceClassification:
        """Classify a single piece of evidence."""
        if not evidence_text:
            return self._create_default_classification(evidence_text, officials)

        # Extract features
        features = self._extract_features(evidence_text)

        # Determine evidence type
        evidence_type = self._classify_evidence_type(evidence_text, features)

        # Calculate strength
        strength, confidence = self._calculate_evidence_strength(evidence_text, evidence_type, features)

        # Sentiment analysis
        sentiment_score = self._analyze_sentiment(evidence_text)

        # Extract relationship indicators
        relationship_indicators = self._extract_relationship_indicators(evidence_text, features)

        # Temporal context analysis
        temporal_context = self._analyze_temporal_context(evidence_text, context)

        return EvidenceClassification(
            evidence_text=evidence_text,
            evidence_type=evidence_type,
            strength=strength,
            confidence=confidence,
            sentiment_score=sentiment_score,
            key_features=features,
            relationship_indicators=relationship_indicators,
            temporal_context=temporal_context
        )

    def _extract_features(self, text: str) -> List[str]:
        """Extract key features from evidence text."""
        text_lower = text.lower()
        features = []

        # Extract cooperation indicators
        for indicator in self.evidence_features["cooperation_indicators"]:
            if indicator in text_lower:
                features.append(f"cooperation:{indicator}")

        # Extract strength indicators
        for indicator in self.evidence_features["strength_indicators"]:
            if indicator in text_lower:
                features.append(f"strength:{indicator}")

        # Extract temporal indicators
        for indicator in self.evidence_features["temporal_indicators"]:
            if indicator in text_lower:
                features.append(f"temporal:{indicator}")

        # Extract outcome indicators
        for indicator in self.evidence_features["outcome_indicators"]:
            if indicator in text_lower:
                features.append(f"outcome:{indicator}")

        # Extract named entities (simplified)
        words = word_tokenize(text_lower)
        significant_words = [w for w in words if len(w) > 3 and w not in stopwords.words('english')]
        features.extend([f"entity:{word}" for word in significant_words[:5]])

        return features

    def _classify_evidence_type(self, text: str, features: List[str]) -> EvidenceType:
        """Classify the type of evidence."""
        text_lower = text.lower()
        type_scores = {}

        for evidence_type, patterns in self.cooperation_patterns.items():
            score = 0
            for keyword in patterns["keywords"]:
                if keyword in text_lower:
                    score += 1

            # Bonus for feature matches
            for feature in features:
                if any(pattern_word in feature for pattern_word in patterns["keywords"]):
                    score += 0.5

            type_scores[evidence_type] = score

        # Return the type with highest score, or default
        if type_scores and max(type_scores.values()) > 0:
            return max(type_scores, key=type_scores.get)
        else:
            return EvidenceType.PUBLIC_STATEMENTS  # Default

    def _calculate_evidence_strength(self, text: str, evidence_type: EvidenceType,
                                   features: List[str]) -> Tuple[EvidenceStrength, float]:
        """Calculate evidence strength and confidence."""
        text_lower = text.lower()
        base_score = 0.5  # Neutral starting point

        # Get patterns for evidence type
        patterns = self.cooperation_patterns.get(evidence_type, {})
        keywords = patterns.get("keywords", [])
        modifiers = patterns.get("strength_modifiers", {})

        # Score based on keyword presence
        keyword_score = sum(1 for keyword in keywords if keyword in text_lower)
        base_score += min(keyword_score * 0.1, 0.3)  # Max 0.3 bonus from keywords

        # Apply strength modifiers
        modifier_bonus = 0
        for modifier, bonus in modifiers.items():
            if modifier in text_lower:
                modifier_bonus = max(modifier_bonus, bonus * 0.2)  # Max modifier bonus

        base_score += modifier_bonus

        # Feature-based scoring
        cooperation_features = len([f for f in features if f.startswith("cooperation:")])
        strength_features = len([f for f in features if f.startswith("strength:")])
        outcome_features = len([f for f in features if f.startswith("outcome:")])

        feature_score = (cooperation_features * 0.1 + strength_features * 0.1 + outcome_features * 0.15)
        base_score += min(feature_score, 0.2)  # Max 0.2 bonus from features

        # Ensure score is within bounds
        final_score = max(0.0, min(1.0, base_score))

        # Convert to EvidenceStrength enum
        if final_score >= 0.8:
            strength = EvidenceStrength.DIRECT_DOCUMENTED
            confidence = 0.9
        elif final_score >= 0.65:
            strength = EvidenceStrength.STRATEGIC_ALIGNMENT
            confidence = 0.8
        elif final_score >= 0.5:
            strength = EvidenceStrength.PARALLEL_ADVOCACY
            confidence = 0.7
        elif final_score >= 0.35:
            strength = EvidenceStrength.COINCIDENTAL_SUCCESS
            confidence = 0.6
        else:
            strength = EvidenceStrength.INSUFFICIENT_DATA
            confidence = 0.5

        return strength, confidence

    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of evidence text."""
        if not self.sentiment_analyzer:
            return 0.0

        try:
            scores = self.sentiment_analyzer.polarity_scores(text)
            # Return compound score (-1 to 1)
            return scores['compound']
        except Exception as e:
            logger.error("Sentiment analysis failed", error=str(e))
            return 0.0

    def _extract_relationship_indicators(self, text: str, features: List[str]) -> Dict[str, float]:
        """Extract relationship dimension indicators."""
        text_lower = text.lower()
        indicators = {}

        # Cooperation level
        cooperation_words = ["cooperation", "collaboration", "partnership", "jointly", "together"]
        cooperation_score = sum(1 for word in cooperation_words if word in text_lower) / len(cooperation_words)
        indicators["cooperation_level"] = min(cooperation_score, 1.0)

        # Strategic coordination
        strategy_words = ["strategic", "coordinated", "planned", "organized", "systematic"]
        strategy_score = sum(1 for word in strategy_words if word in text_lower) / len(strategy_words)
        indicators["strategic_coordination"] = min(strategy_score, 1.0)

        # Public visibility
        public_words = ["public", "announced", "statement", "press", "media", "visible"]
        public_score = sum(1 for word in public_words if word in text_lower) / len(public_words)
        indicators["public_visibility"] = min(public_score, 1.0)

        # Outcome effectiveness
        outcome_words = ["successful", "achieved", "secured", "delivered", "accomplished"]
        outcome_score = sum(1 for word in outcome_words if word in text_lower) / len(outcome_words)
        indicators["outcome_effectiveness"] = min(outcome_score, 1.0)

        return indicators

    def _analyze_temporal_context(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze temporal context of evidence."""
        temporal_context = {
            "recency": 0.5,  # Default medium recency
            "duration": "unknown",
            "frequency": "single"
        }

        if not context:
            return temporal_context

        # Analyze date information
        if "date" in context:
            try:
                evidence_date = datetime.strptime(context["date"], "%Y-%m-%d")
                days_ago = (datetime.now() - evidence_date).days

                # Recency score (more recent = higher score)
                if days_ago <= 30:
                    temporal_context["recency"] = 1.0
                elif days_ago <= 90:
                    temporal_context["recency"] = 0.8
                elif days_ago <= 365:
                    temporal_context["recency"] = 0.6
                elif days_ago <= 1825:  # 5 years
                    temporal_context["recency"] = 0.4
                else:
                    temporal_context["recency"] = 0.2

            except ValueError:
                pass

        # Analyze duration indicators in text
        text_lower = text.lower()
        if any(word in text_lower for word in ["ongoing", "continued", "long-term"]):
            temporal_context["duration"] = "long-term"
        elif any(word in text_lower for word in ["temporary", "short-term", "brief"]):
            temporal_context["duration"] = "short-term"

        # Analyze frequency indicators
        if any(word in text_lower for word in ["repeatedly", "regularly", "consistently"]):
            temporal_context["frequency"] = "repeated"
        elif any(word in text_lower for word in ["occasionally", "sometimes"]):
            temporal_context["frequency"] = "occasional"

        return temporal_context

    def _create_default_classification(self, evidence_text: str, officials: Tuple[str, str]) -> EvidenceClassification:
        """Create default classification for insufficient evidence."""
        return EvidenceClassification(
            evidence_text=evidence_text,
            evidence_type=EvidenceType.PUBLIC_STATEMENTS,
            strength=EvidenceStrength.INSUFFICIENT_DATA,
            confidence=0.1,
            sentiment_score=0.0,
            key_features=[],
            relationship_indicators={},
            temporal_context={}
        )

    async def classify_relationship(self, official_1: str, official_2: str) -> RelationshipClassification:
        """Classify the complete relationship between two officials."""
        # Extract all evidence for this relationship
        evidence_items = self._extract_relationship_evidence(official_1, official_2)

        if not evidence_items:
            return self._create_default_relationship_classification(official_1, official_2)

        # Classify each piece of evidence
        evidence_classifications = []
        for evidence_item in evidence_items:
            classification = await self.classify_evidence(
                evidence_item["description"],
                (official_1, official_2),
                evidence_item.get("context", {})
            )
            evidence_classifications.append(classification)

        # Aggregate classifications
        overall_strength = self._aggregate_evidence_strength(evidence_classifications)
        relationship_dimensions = self._calculate_relationship_dimensions(evidence_classifications)
        confidence_score = self._calculate_overall_confidence(evidence_classifications)
        classification_summary = self._generate_classification_summary(evidence_classifications, overall_strength)
        supporting_features = self._extract_supporting_features(evidence_classifications)

        return RelationshipClassification(
            official_1=official_1,
            official_2=official_2,
            evidence_classifications=evidence_classifications,
            overall_strength=overall_strength,
            relationship_dimensions=relationship_dimensions,
            confidence_score=confidence_score,
            classification_summary=classification_summary,
            supporting_features=supporting_features
        )

    def _extract_relationship_evidence(self, official_1: str, official_2: str) -> List[Dict[str, Any]]:
        """Extract all evidence items for a relationship."""
        evidence_items = []

        # Check both directions
        for primary, secondary in [(official_1, official_2), (official_2, official_1)]:
            official_data = STATEN_ISLAND_OFFICIALS.get(primary, {})
            relationships = official_data.get("relationships", {})

            if secondary in relationships:
                rel_data = relationships[secondary]
                for evidence in rel_data.get("evidence", []):
                    evidence_items.append({
                        "description": evidence.get("description", ""),
                        "context": {
                            "date": evidence.get("date", ""),
                            "source": evidence.get("source", ""),
                            "type": evidence.get("type", ""),
                            "issue_area": evidence.get("issue_area", "")
                        }
                    })

        return evidence_items

    def _aggregate_evidence_strength(self, classifications: List[EvidenceClassification]) -> EvidenceStrength:
        """Aggregate evidence strength from multiple classifications."""
        if not classifications:
            return EvidenceStrength.INSUFFICIENT_DATA

        # Count occurrences of each strength level
        strength_counts = Counter(c.strength for c in classifications)

        # Weight by confidence
        weighted_scores = {}
        for classification in classifications:
            strength = classification.strength
            confidence = classification.confidence

            if strength not in weighted_scores:
                weighted_scores[strength] = 0
            weighted_scores[strength] += confidence

        # Return the strength with highest weighted score
        if weighted_scores:
            return max(weighted_scores, key=weighted_scores.get)
        else:
            return EvidenceStrength.INSUFFICIENT_DATA

    def _calculate_relationship_dimensions(self, classifications: List[EvidenceClassification]) -> Dict[RelationshipDimension, float]:
        """Calculate relationship dimension scores."""
        if not classifications:
            return {}

        dimension_scores = {}

        # Aggregate relationship indicators
        all_indicators = defaultdict(list)
        for classification in classifications:
            for indicator, score in classification.relationship_indicators.items():
                all_indicators[indicator].append(score * classification.confidence)

        # Calculate average scores
        for indicator, scores in all_indicators.items():
            if indicator == "cooperation_level":
                dimension_scores[RelationshipDimension.COOPERATION_LEVEL] = sum(scores) / len(scores)
            elif indicator == "strategic_coordination":
                dimension_scores[RelationshipDimension.STRATEGIC_COORDINATION] = sum(scores) / len(scores)
            elif indicator == "public_visibility":
                dimension_scores[RelationshipDimension.PUBLIC_VISIBILITY] = sum(scores) / len(scores)
            elif indicator == "outcome_effectiveness":
                dimension_scores[RelationshipDimension.OUTCOME_EFFECTIVENESS] = sum(scores) / len(scores)

        # Calculate temporal consistency
        temporal_scores = [c.temporal_context.get("recency", 0.5) for c in classifications if c.temporal_context]
        if temporal_scores:
            dimension_scores[RelationshipDimension.TEMPORAL_CONSISTENCY] = sum(temporal_scores) / len(temporal_scores)

        # Calculate ideological alignment (based on sentiment)
        sentiment_scores = [abs(c.sentiment_score) for c in classifications if c.sentiment_score != 0]
        if sentiment_scores:
            dimension_scores[RelationshipDimension.IDEOLOGICAL_ALIGNMENT] = sum(sentiment_scores) / len(sentiment_scores)

        return dimension_scores

    def _calculate_overall_confidence(self, classifications: List[EvidenceClassification]) -> float:
        """Calculate overall confidence score."""
        if not classifications:
            return 0.0

        # Weight by number of evidence pieces and their individual confidence
        confidence_scores = [c.confidence for c in classifications]
        base_confidence = sum(confidence_scores) / len(confidence_scores)

        # Bonus for multiple pieces of evidence
        evidence_bonus = min(len(classifications) * 0.05, 0.2)  # Max 20% bonus

        return min(1.0, base_confidence + evidence_bonus)

    def _generate_classification_summary(self, classifications: List[EvidenceClassification],
                                       overall_strength: EvidenceStrength) -> str:
        """Generate human-readable classification summary."""
        if not classifications:
            return "Insufficient evidence for classification"

        evidence_count = len(classifications)
        avg_confidence = sum(c.confidence for c in classifications) / evidence_count

        # Count evidence types
        type_counts = Counter(c.evidence_type for c in classifications)
        most_common_type = type_counts.most_common(1)[0][0].value.replace("_", " ") if type_counts else "unknown"

        return (f"{overall_strength.value.replace('_', ' ').title()} relationship based on "
                f"{evidence_count} pieces of evidence (avg confidence: {avg_confidence:.2f}). "
                f"Primary evidence type: {most_common_type}.")

    def _extract_supporting_features(self, classifications: List[EvidenceClassification]) -> List[str]:
        """Extract key supporting features from classifications."""
        all_features = []
        for classification in classifications:
            all_features.extend(classification.key_features)

        # Count feature frequency
        feature_counts = Counter(all_features)

        # Return top features
        return [feature for feature, count in feature_counts.most_common(10)]

    def _create_default_relationship_classification(self, official_1: str, official_2: str) -> RelationshipClassification:
        """Create default classification for insufficient evidence."""
        return RelationshipClassification(
            official_1=official_1,
            official_2=official_2,
            evidence_classifications=[],
            overall_strength=EvidenceStrength.INSUFFICIENT_DATA,
            relationship_dimensions={},
            confidence_score=0.0,
            classification_summary="No evidence available for classification",
            supporting_features=[]
        )

    async def classify_all_relationships(self) -> Dict[str, RelationshipClassification]:
        """Classify all relationships between Staten Island officials."""
        classifications = {}
        officials = list(STATEN_ISLAND_OFFICIALS.keys())

        for i, official_1 in enumerate(officials):
            for j, official_2 in enumerate(officials):
                if i < j:  # Avoid duplicates
                    key = f"{official_1}_{official_2}"
                    classification = await self.classify_relationship(official_1, official_2)

                    # Only include relationships with actual evidence
                    if classification.evidence_classifications:
                        classifications[key] = classification

        return classifications

    def generate_classification_report(self, classifications: Dict[str, RelationshipClassification]) -> Dict[str, Any]:
        """Generate comprehensive classification report."""
        if not classifications:
            return {"message": "No relationship classifications available"}

        # Aggregate statistics
        total_relationships = len(classifications)
        strength_distribution = Counter(c.overall_strength for c in classifications.values())
        avg_confidence = sum(c.confidence_score for c in classifications.values()) / total_relationships

        # Find strongest relationships
        strongest_relationships = sorted(
            classifications.items(),
            key=lambda x: (x[1].overall_strength.value, x[1].confidence_score),
            reverse=True
        )[:5]

        # Analyze evidence types
        all_evidence_types = []
        for classification in classifications.values():
            all_evidence_types.extend([e.evidence_type for e in classification.evidence_classifications])

        evidence_type_distribution = Counter(all_evidence_types)

        return {
            "summary": {
                "total_relationships_classified": total_relationships,
                "average_confidence": avg_confidence,
                "strength_distribution": {k.value: v for k, v in strength_distribution.items()},
                "evidence_type_distribution": {k.value: v for k, v in evidence_type_distribution.items()}
            },
            "strongest_relationships": [
                {
                    "officials": f"{rel[1].official_1} - {rel[1].official_2}",
                    "strength": rel[1].overall_strength.value,
                    "confidence": rel[1].confidence_score,
                    "summary": rel[1].classification_summary
                }
                for rel in strongest_relationships
            ],
            "detailed_classifications": {
                key: {
                    "officials": f"{cls.official_1} - {cls.official_2}",
                    "overall_strength": cls.overall_strength.value,
                    "confidence_score": cls.confidence_score,
                    "evidence_count": len(cls.evidence_classifications),
                    "relationship_dimensions": {k.value: v for k, v in cls.relationship_dimensions.items()},
                    "summary": cls.classification_summary
                }
                for key, cls in classifications.items()
            }
        }