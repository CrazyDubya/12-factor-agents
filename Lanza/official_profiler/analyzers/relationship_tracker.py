"""
Evidence-based relationship tracking system for elected officials.
Analyzes documented relationships with classification and temporal evolution.
"""
import asyncio
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import re
from collections import defaultdict
import structlog
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from models.database import get_db_session
from models.official import Official, Position, Statement, Vote
from models.relationship import OfficialRelationship, RelationshipType, RelationshipEvidence
from data.staten_island_officials import STATEN_ISLAND_OFFICIALS
from utils.temporal_analyzer import TemporalAnalyzer

logger = structlog.get_logger()


class EvidenceStrength(Enum):
    """Classification of relationship evidence strength."""
    DIRECT_DOCUMENTED = "direct_documented"  # Joint press releases, co-sponsored bills
    STRATEGIC_ALIGNMENT = "strategic_alignment"  # Consistent voting patterns, shared positions
    PARALLEL_ADVOCACY = "parallel_advocacy"  # Similar statements, parallel initiatives
    COINCIDENTAL_SUCCESS = "coincidental_success"  # Both benefit but no coordination evidence
    CONFLICTING_EVIDENCE = "conflicting_evidence"  # Mixed evidence of cooperation/opposition
    INSUFFICIENT_DATA = "insufficient_data"  # Not enough evidence to classify


@dataclass
class RelationshipEvidence:
    """Container for relationship evidence data."""
    evidence_type: str
    description: str
    date: datetime
    source: str
    strength: EvidenceStrength
    officials_involved: List[str]
    issue_area: Optional[str] = None
    outcome_achieved: Optional[str] = None


@dataclass
class RelationshipProfile:
    """Complete relationship profile between officials."""
    official_1: str
    official_2: str
    relationship_type: RelationshipType
    evidence_strength: EvidenceStrength
    evidence_count: int
    first_interaction: datetime
    last_interaction: datetime
    shared_issues: List[str]
    evidence_timeline: List[RelationshipEvidence]
    cooperation_score: float
    stability_score: float


class RelationshipTracker:
    """Tracks and analyzes relationships between elected officials."""

    def __init__(self):
        self.temporal_analyzer = TemporalAnalyzer()
        self.evidence_patterns = self._initialize_evidence_patterns()
        self.relationship_cache = {}

    def _initialize_evidence_patterns(self) -> Dict[str, Dict]:
        """Initialize patterns for identifying relationship evidence."""
        return {
            "direct_cooperation": {
                "keywords": [
                    "joint", "together", "partnership", "collaboration", "co-sponsored",
                    "jointly announced", "worked with", "coordinated", "bipartisan effort"
                ],
                "strength": EvidenceStrength.DIRECT_DOCUMENTED
            },
            "strategic_alignment": {
                "keywords": [
                    "similar position", "aligned", "consistent", "both support",
                    "shared priority", "common goal", "unified approach"
                ],
                "strength": EvidenceStrength.STRATEGIC_ALIGNMENT
            },
            "parallel_advocacy": {
                "keywords": [
                    "also advocates", "separately supports", "independently",
                    "parallel efforts", "similar initiative", "concurrent"
                ],
                "strength": EvidenceStrength.PARALLEL_ADVOCACY
            },
            "succession_support": {
                "keywords": [
                    "endorsed", "supported candidacy", "campaign support",
                    "political transition", "backing", "recommended"
                ],
                "strength": EvidenceStrength.DIRECT_DOCUMENTED
            }
        }

    async def analyze_all_relationships(self) -> Dict[str, List[RelationshipProfile]]:
        """Analyze all relationships between Staten Island officials."""
        relationships = {}
        officials = list(STATEN_ISLAND_OFFICIALS.keys())

        for i, official_1 in enumerate(officials):
            relationships[official_1] = []
            for j, official_2 in enumerate(officials):
                if i != j and j > i:  # Avoid duplicate pairs
                    profile = await self.analyze_relationship_pair(official_1, official_2)
                    if profile:
                        relationships[official_1].append(profile)
                        if official_2 not in relationships:
                            relationships[official_2] = []
                        relationships[official_2].append(profile)

        return relationships

    async def analyze_relationship_pair(self, official_1: str, official_2: str) -> Optional[RelationshipProfile]:
        """Analyze relationship between two specific officials."""
        cache_key = f"{min(official_1, official_2)}_{max(official_1, official_2)}"
        if cache_key in self.relationship_cache:
            return self.relationship_cache[cache_key]

        logger.info("Analyzing relationship pair", official_1=official_1, official_2=official_2)

        # Extract evidence from documented relationships
        evidence_timeline = await self._extract_documented_evidence(official_1, official_2)

        if not evidence_timeline:
            return None

        # Classify relationship
        relationship_type, evidence_strength = self._classify_relationship(evidence_timeline)

        # Calculate metrics
        cooperation_score = self._calculate_cooperation_score(evidence_timeline)
        stability_score = self._calculate_stability_score(evidence_timeline)

        # Extract shared issues
        shared_issues = self._extract_shared_issues(evidence_timeline)

        profile = RelationshipProfile(
            official_1=official_1,
            official_2=official_2,
            relationship_type=relationship_type,
            evidence_strength=evidence_strength,
            evidence_count=len(evidence_timeline),
            first_interaction=min(e.date for e in evidence_timeline),
            last_interaction=max(e.date for e in evidence_timeline),
            shared_issues=shared_issues,
            evidence_timeline=evidence_timeline,
            cooperation_score=cooperation_score,
            stability_score=stability_score
        )

        self.relationship_cache[cache_key] = profile
        return profile

    async def _extract_documented_evidence(self, official_1: str, official_2: str) -> List[RelationshipEvidence]:
        """Extract evidence from documented relationships in Staten Island officials data."""
        evidence = []

        # Get official data
        official_1_data = STATEN_ISLAND_OFFICIALS.get(official_1, {})
        official_2_data = STATEN_ISLAND_OFFICIALS.get(official_2, {})

        # Check relationships in both directions
        relationships_1 = official_1_data.get("relationships", {})
        relationships_2 = official_2_data.get("relationships", {})

        # Extract evidence from official_1's documented relationships with official_2
        if official_2 in relationships_1:
            rel_data = relationships_1[official_2]
            for evidence_item in rel_data.get("evidence", []):
                evidence.append(RelationshipEvidence(
                    evidence_type=evidence_item.get("type", "documented"),
                    description=evidence_item.get("description", ""),
                    date=datetime.strptime(evidence_item.get("date", "2020-01-01"), "%Y-%m-%d"),
                    source=evidence_item.get("source", "documentation"),
                    strength=self._classify_evidence_strength(evidence_item.get("description", "")),
                    officials_involved=[official_1, official_2],
                    issue_area=evidence_item.get("issue_area"),
                    outcome_achieved=evidence_item.get("outcome")
                ))

        # Extract evidence from official_2's documented relationships with official_1
        if official_1 in relationships_2:
            rel_data = relationships_2[official_1]
            for evidence_item in rel_data.get("evidence", []):
                # Avoid duplicates
                existing_descriptions = [e.description for e in evidence]
                if evidence_item.get("description", "") not in existing_descriptions:
                    evidence.append(RelationshipEvidence(
                        evidence_type=evidence_item.get("type", "documented"),
                        description=evidence_item.get("description", ""),
                        date=datetime.strptime(evidence_item.get("date", "2020-01-01"), "%Y-%m-%d"),
                        source=evidence_item.get("source", "documentation"),
                        strength=self._classify_evidence_strength(evidence_item.get("description", "")),
                        officials_involved=[official_2, official_1],
                        issue_area=evidence_item.get("issue_area"),
                        outcome_achieved=evidence_item.get("outcome")
                    ))

        # Sort by date
        evidence.sort(key=lambda x: x.date)
        return evidence

    def _classify_evidence_strength(self, description: str) -> EvidenceStrength:
        """Classify evidence strength based on description content."""
        description_lower = description.lower()

        for pattern_name, pattern_data in self.evidence_patterns.items():
            for keyword in pattern_data["keywords"]:
                if keyword in description_lower:
                    return pattern_data["strength"]

        # Default classification based on specific words
        if any(word in description_lower for word in ["jointly", "together", "partnered", "co-sponsored"]):
            return EvidenceStrength.DIRECT_DOCUMENTED
        elif any(word in description_lower for word in ["similar", "aligned", "consistent", "both"]):
            return EvidenceStrength.STRATEGIC_ALIGNMENT
        elif any(word in description_lower for word in ["parallel", "separately", "also"]):
            return EvidenceStrength.PARALLEL_ADVOCACY
        else:
            return EvidenceStrength.STRATEGIC_ALIGNMENT  # Default for documented relationships

    def _classify_relationship(self, evidence_timeline: List[RelationshipEvidence]) -> Tuple[RelationshipType, EvidenceStrength]:
        """Classify overall relationship type and strength."""
        if not evidence_timeline:
            return RelationshipType.NEUTRAL, EvidenceStrength.INSUFFICIENT_DATA

        # Count evidence by strength
        strength_counts = defaultdict(int)
        for evidence in evidence_timeline:
            strength_counts[evidence.strength] += 1

        # Determine primary relationship type based on evidence
        if strength_counts[EvidenceStrength.DIRECT_DOCUMENTED] >= 2:
            return RelationshipType.COALITION, EvidenceStrength.DIRECT_DOCUMENTED
        elif strength_counts[EvidenceStrength.STRATEGIC_ALIGNMENT] >= 3:
            return RelationshipType.ALLIANCE, EvidenceStrength.STRATEGIC_ALIGNMENT
        elif strength_counts[EvidenceStrength.PARALLEL_ADVOCACY] >= 2:
            return RelationshipType.SUPPORTIVE, EvidenceStrength.PARALLEL_ADVOCACY
        else:
            return RelationshipType.NEUTRAL, EvidenceStrength.STRATEGIC_ALIGNMENT

    def _calculate_cooperation_score(self, evidence_timeline: List[RelationshipEvidence]) -> float:
        """Calculate cooperation score based on evidence strength and frequency."""
        if not evidence_timeline:
            return 0.0

        strength_weights = {
            EvidenceStrength.DIRECT_DOCUMENTED: 1.0,
            EvidenceStrength.STRATEGIC_ALIGNMENT: 0.7,
            EvidenceStrength.PARALLEL_ADVOCACY: 0.5,
            EvidenceStrength.COINCIDENTAL_SUCCESS: 0.3,
            EvidenceStrength.CONFLICTING_EVIDENCE: -0.5,
            EvidenceStrength.INSUFFICIENT_DATA: 0.0
        }

        total_score = sum(strength_weights[evidence.strength] for evidence in evidence_timeline)
        max_possible = len(evidence_timeline) * 1.0
        return min(1.0, max(0.0, total_score / max_possible)) if max_possible > 0 else 0.0

    def _calculate_stability_score(self, evidence_timeline: List[RelationshipEvidence]) -> float:
        """Calculate relationship stability over time."""
        if len(evidence_timeline) < 2:
            return 0.5  # Neutral for single interaction

        # Calculate time span
        time_span = (evidence_timeline[-1].date - evidence_timeline[0].date).days
        if time_span == 0:
            return 0.5

        # Calculate evidence distribution over time
        evidence_per_year = len(evidence_timeline) / (time_span / 365.25)

        # Score based on consistency (more evidence over longer time = more stable)
        if evidence_per_year >= 1.0:  # At least annual interaction
            return min(1.0, 0.5 + (evidence_per_year * 0.1))
        else:
            return max(0.0, 0.5 - (1.0 - evidence_per_year) * 0.3)

    def _extract_shared_issues(self, evidence_timeline: List[RelationshipEvidence]) -> List[str]:
        """Extract shared issues from evidence timeline."""
        issues = set()
        for evidence in evidence_timeline:
            if evidence.issue_area:
                issues.add(evidence.issue_area)

            # Extract issues from description
            description_lower = evidence.description.lower()
            if "infrastructure" in description_lower or "bridge" in description_lower:
                issues.add("Infrastructure")
            if "ferry" in description_lower or "transportation" in description_lower:
                issues.add("Transportation")
            if "flooding" in description_lower or "resiliency" in description_lower:
                issues.add("Climate Resiliency")
            if "healthcare" in description_lower:
                issues.add("Healthcare")
            if "economic" in description_lower or "development" in description_lower:
                issues.add("Economic Development")

        return sorted(list(issues))

    async def track_relationship_evolution(self, official_1: str, official_2: str,
                                         start_year: int = 2000) -> Dict[int, RelationshipProfile]:
        """Track how a relationship has evolved over time."""
        all_evidence = await self._extract_documented_evidence(official_1, official_2)

        yearly_profiles = {}
        for year in range(start_year, datetime.now().year + 1):
            # Filter evidence up to this year
            year_evidence = [
                e for e in all_evidence
                if e.date.year <= year
            ]

            if year_evidence:
                # Create profile for this year's cumulative evidence
                relationship_type, evidence_strength = self._classify_relationship(year_evidence)
                cooperation_score = self._calculate_cooperation_score(year_evidence)
                stability_score = self._calculate_stability_score(year_evidence)
                shared_issues = self._extract_shared_issues(year_evidence)

                yearly_profiles[year] = RelationshipProfile(
                    official_1=official_1,
                    official_2=official_2,
                    relationship_type=relationship_type,
                    evidence_strength=evidence_strength,
                    evidence_count=len(year_evidence),
                    first_interaction=min(e.date for e in year_evidence),
                    last_interaction=max(e.date for e in year_evidence),
                    shared_issues=shared_issues,
                    evidence_timeline=year_evidence,
                    cooperation_score=cooperation_score,
                    stability_score=stability_score
                )

        return yearly_profiles

    async def identify_relationship_clusters(self) -> Dict[str, List[str]]:
        """Identify clusters of officials with strong relationships."""
        all_relationships = await self.analyze_all_relationships()

        clusters = defaultdict(list)
        for official, relationships in all_relationships.items():
            strong_relationships = [
                r for r in relationships
                if r.cooperation_score >= 0.7 and r.evidence_strength in [
                    EvidenceStrength.DIRECT_DOCUMENTED,
                    EvidenceStrength.STRATEGIC_ALIGNMENT
                ]
            ]

            if strong_relationships:
                cluster_key = f"{official}_cluster"
                for rel in strong_relationships:
                    other_official = rel.official_2 if rel.official_1 == official else rel.official_1
                    if other_official not in clusters[cluster_key]:
                        clusters[cluster_key].append(other_official)

        return dict(clusters)

    async def generate_relationship_summary(self) -> Dict[str, Any]:
        """Generate comprehensive relationship analysis summary."""
        all_relationships = await self.analyze_all_relationships()
        clusters = await self.identify_relationship_clusters()

        # Calculate network statistics
        total_relationships = sum(len(rels) for rels in all_relationships.values()) // 2  # Avoid double counting
        strong_relationships = 0
        cooperation_scores = []

        for relationships in all_relationships.values():
            for rel in relationships:
                cooperation_scores.append(rel.cooperation_score)
                if rel.cooperation_score >= 0.7:
                    strong_relationships += 1

        strong_relationships //= 2  # Avoid double counting

        return {
            "network_statistics": {
                "total_officials": len(STATEN_ISLAND_OFFICIALS),
                "total_relationships": total_relationships,
                "strong_relationships": strong_relationships,
                "average_cooperation": sum(cooperation_scores) / len(cooperation_scores) if cooperation_scores else 0,
                "network_density": total_relationships / ((len(STATEN_ISLAND_OFFICIALS) * (len(STATEN_ISLAND_OFFICIALS) - 1)) / 2)
            },
            "relationship_clusters": clusters,
            "detailed_relationships": all_relationships,
            "generated_at": datetime.now().isoformat()
        }