"""
Temporal analysis system for tracking position evolution and historical changes.
"""
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import re
from collections import defaultdict
import structlog

from data.staten_island_officials import STATEN_ISLAND_OFFICIALS

logger = structlog.get_logger()


class PositionChangeType(Enum):
    """Types of position changes over time."""
    STRENGTHENED = "strengthened"  # Position became stronger/more committed
    SOFTENED = "softened"  # Position became less strong/more moderate
    REVERSED = "reversed"  # Complete position reversal
    EVOLVED = "evolved"  # Natural evolution based on new information
    CONSISTENT = "consistent"  # No significant change
    CONTEXTUAL = "contextual"  # Changed due to new role/circumstances


@dataclass
class PositionSnapshot:
    """Snapshot of an official's position at a specific time."""
    official: str
    issue: str
    position_summary: str
    date: datetime
    source: str
    context: str
    confidence_level: float
    supporting_evidence: List[str]


@dataclass
class PositionEvolution:
    """Complete evolution of a position over time."""
    official: str
    issue: str
    snapshots: List[PositionSnapshot]
    change_type: PositionChangeType
    evolution_summary: str
    key_turning_points: List[Tuple[datetime, str]]
    stability_score: float


class TemporalAnalyzer:
    """Analyzes temporal evolution of official positions and relationships."""

    def __init__(self):
        self.position_cache = {}
        self.evolution_patterns = self._initialize_evolution_patterns()

    def _initialize_evolution_patterns(self) -> Dict[str, Dict]:
        """Initialize patterns for detecting position evolution."""
        return {
            "strengthening_indicators": [
                "stronger support", "increased commitment", "expanded", "enhanced",
                "more aggressive", "doubled down", "reinforced"
            ],
            "softening_indicators": [
                "reconsidering", "reviewing", "more flexible", "open to",
                "moderate approach", "nuanced", "cautious"
            ],
            "reversal_indicators": [
                "no longer support", "changed position", "now oppose",
                "reversed", "different view", "new stance"
            ],
            "evolution_indicators": [
                "updated position", "learned", "new information", "evolved",
                "refined", "adjusted", "adapted"
            ]
        }

    async def analyze_position_evolution(self, official: str, issue: str,
                                       start_year: int = 2000) -> Optional[PositionEvolution]:
        """Analyze how an official's position on an issue has evolved."""
        snapshots = await self._extract_position_snapshots(official, issue, start_year)

        if len(snapshots) < 2:
            return None

        # Sort by date
        snapshots.sort(key=lambda x: x.date)

        # Analyze change pattern
        change_type = self._classify_change_type(snapshots)
        evolution_summary = self._generate_evolution_summary(snapshots, change_type)
        turning_points = self._identify_turning_points(snapshots)
        stability_score = self._calculate_stability_score(snapshots)

        return PositionEvolution(
            official=official,
            issue=issue,
            snapshots=snapshots,
            change_type=change_type,
            evolution_summary=evolution_summary,
            key_turning_points=turning_points,
            stability_score=stability_score
        )

    async def _extract_position_snapshots(self, official: str, issue: str,
                                        start_year: int) -> List[PositionSnapshot]:
        """Extract position snapshots from documented positions."""
        snapshots = []
        official_data = STATEN_ISLAND_OFFICIALS.get(official, {})

        # Extract from position evolution data
        position_evolution = official_data.get("position_evolution", {})
        issue_data = position_evolution.get(issue, [])

        for position_entry in issue_data:
            snapshot = PositionSnapshot(
                official=official,
                issue=issue,
                position_summary=position_entry.get("position", ""),
                date=datetime.strptime(position_entry.get("date", "2020-01-01"), "%Y-%m-%d"),
                source=position_entry.get("source", "documentation"),
                context=position_entry.get("context", ""),
                confidence_level=position_entry.get("confidence", 0.8),
                supporting_evidence=position_entry.get("evidence", [])
            )

            if snapshot.date.year >= start_year:
                snapshots.append(snapshot)

        # Extract from achievements and focus areas as additional snapshots
        achievements = official_data.get("achievements", [])
        focus_areas = official_data.get("focus_areas", [])

        # Look for issue-related achievements as position indicators
        for achievement in achievements:
            achievement_text = achievement.get("description", "").lower()
            if issue.lower() in achievement_text:
                snapshot = PositionSnapshot(
                    official=official,
                    issue=issue,
                    position_summary=f"Achieved: {achievement.get('description', '')}",
                    date=datetime.strptime(achievement.get("year", "2020") + "-01-01", "%Y-%m-%d"),
                    source="achievements",
                    context="Legislative achievement",
                    confidence_level=0.9,
                    supporting_evidence=[achievement.get("description", "")]
                )
                snapshots.append(snapshot)

        return snapshots

    def _classify_change_type(self, snapshots: List[PositionSnapshot]) -> PositionChangeType:
        """Classify the type of position change over time."""
        if len(snapshots) < 2:
            return PositionChangeType.CONSISTENT

        first_position = snapshots[0].position_summary.lower()
        last_position = snapshots[-1].position_summary.lower()

        # Check for reversal indicators
        for indicator in self.evolution_patterns["reversal_indicators"]:
            if indicator in last_position:
                return PositionChangeType.REVERSED

        # Check for strengthening
        for indicator in self.evolution_patterns["strengthening_indicators"]:
            if indicator in last_position:
                return PositionChangeType.STRENGTHENED

        # Check for softening
        for indicator in self.evolution_patterns["softening_indicators"]:
            if indicator in last_position:
                return PositionChangeType.SOFTENED

        # Check for evolution
        for indicator in self.evolution_patterns["evolution_indicators"]:
            if indicator in last_position:
                return PositionChangeType.EVOLVED

        # Compare sentiment/strength
        if self._has_strengthened_over_time(snapshots):
            return PositionChangeType.STRENGTHENED
        elif self._has_softened_over_time(snapshots):
            return PositionChangeType.SOFTENED
        else:
            return PositionChangeType.CONSISTENT

    def _has_strengthened_over_time(self, snapshots: List[PositionSnapshot]) -> bool:
        """Determine if position has strengthened over time."""
        strengthening_words = ["strong", "committed", "aggressive", "expanded", "increased"]
        early_strength = sum(1 for word in strengthening_words
                           if word in snapshots[0].position_summary.lower())
        late_strength = sum(1 for word in strengthening_words
                          if word in snapshots[-1].position_summary.lower())
        return late_strength > early_strength

    def _has_softened_over_time(self, snapshots: List[PositionSnapshot]) -> bool:
        """Determine if position has softened over time."""
        softening_words = ["moderate", "cautious", "flexible", "review", "consider"]
        early_softness = sum(1 for word in softening_words
                           if word in snapshots[0].position_summary.lower())
        late_softness = sum(1 for word in softening_words
                          if word in snapshots[-1].position_summary.lower())
        return late_softness > early_softness

    def _generate_evolution_summary(self, snapshots: List[PositionSnapshot],
                                  change_type: PositionChangeType) -> str:
        """Generate human-readable evolution summary."""
        if len(snapshots) < 2:
            return "Insufficient data for evolution analysis"

        time_span = (snapshots[-1].date - snapshots[0].date).days // 365
        position_count = len(snapshots)

        summary_templates = {
            PositionChangeType.STRENGTHENED: f"Position strengthened over {time_span} years ({position_count} documented positions)",
            PositionChangeType.SOFTENED: f"Position moderated over {time_span} years ({position_count} documented positions)",
            PositionChangeType.REVERSED: f"Position reversed over {time_span} years ({position_count} documented positions)",
            PositionChangeType.EVOLVED: f"Position evolved over {time_span} years ({position_count} documented positions)",
            PositionChangeType.CONSISTENT: f"Position remained consistent over {time_span} years ({position_count} documented positions)",
            PositionChangeType.CONTEXTUAL: f"Position adapted to context over {time_span} years ({position_count} documented positions)"
        }

        base_summary = summary_templates.get(change_type, f"Position tracked over {time_span} years")

        # Add specific details
        first_year = snapshots[0].date.year
        last_year = snapshots[-1].date.year
        return f"{base_summary}. From {first_year}: '{snapshots[0].position_summary[:100]}...' to {last_year}: '{snapshots[-1].position_summary[:100]}...'"

    def _identify_turning_points(self, snapshots: List[PositionSnapshot]) -> List[Tuple[datetime, str]]:
        """Identify key turning points in position evolution."""
        turning_points = []

        for i in range(1, len(snapshots)):
            prev_snapshot = snapshots[i-1]
            curr_snapshot = snapshots[i]

            # Look for significant changes
            prev_text = prev_snapshot.position_summary.lower()
            curr_text = curr_snapshot.position_summary.lower()

            # Check for reversal language
            if any(indicator in curr_text for indicator in self.evolution_patterns["reversal_indicators"]):
                turning_points.append((curr_snapshot.date, "Position reversal"))

            # Check for major strengthening
            elif any(indicator in curr_text for indicator in self.evolution_patterns["strengthening_indicators"]):
                turning_points.append((curr_snapshot.date, "Position strengthened"))

            # Check for role changes (context-based turning points)
            elif "elected" in curr_snapshot.context.lower() or "appointed" in curr_snapshot.context.lower():
                turning_points.append((curr_snapshot.date, "Role change context"))

            # Check for major policy achievements
            elif "achieved" in curr_text or "passed" in curr_text or "secured" in curr_text:
                turning_points.append((curr_snapshot.date, "Policy achievement"))

        return turning_points

    def _calculate_stability_score(self, snapshots: List[PositionSnapshot]) -> float:
        """Calculate position stability over time."""
        if len(snapshots) < 2:
            return 1.0

        # Calculate consistency of position sentiment
        position_texts = [s.position_summary.lower() for s in snapshots]

        # Simple stability metric: similarity of key terms across positions
        key_terms = set()
        for text in position_texts:
            words = text.split()
            key_terms.update([w for w in words if len(w) > 4])  # Focus on meaningful words

        if not key_terms:
            return 0.5

        # Calculate term consistency across snapshots
        term_appearances = defaultdict(int)
        for text in position_texts:
            for term in key_terms:
                if term in text:
                    term_appearances[term] += 1

        # Score based on how consistently terms appear
        consistency_scores = [count / len(position_texts) for count in term_appearances.values()]
        return sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.5

    async def analyze_temporal_relationship_patterns(self, start_year: int = 2000) -> Dict[str, Any]:
        """Analyze temporal patterns in relationships between officials."""
        temporal_data = defaultdict(lambda: defaultdict(list))

        # Extract relationship evidence by year
        for official, data in STATEN_ISLAND_OFFICIALS.items():
            relationships = data.get("relationships", {})
            for partner, rel_data in relationships.items():
                for evidence in rel_data.get("evidence", []):
                    year = datetime.strptime(evidence.get("date", "2020-01-01"), "%Y-%m-%d").year
                    if year >= start_year:
                        temporal_data[year][f"{official}-{partner}"].append(evidence)

        # Analyze patterns by year
        yearly_analysis = {}
        for year, year_relationships in temporal_data.items():
            yearly_analysis[year] = {
                "total_interactions": sum(len(evidence_list) for evidence_list in year_relationships.values()),
                "unique_partnerships": len(year_relationships),
                "most_active_officials": self._get_most_active_officials(year_relationships),
                "cooperation_types": self._analyze_cooperation_types(year_relationships)
            }

        return {
            "temporal_patterns": yearly_analysis,
            "trend_analysis": self._analyze_cooperation_trends(yearly_analysis),
            "period_summaries": self._generate_period_summaries(yearly_analysis)
        }

    def _get_most_active_officials(self, year_relationships: Dict) -> List[Tuple[str, int]]:
        """Get most active officials in a given year."""
        official_activity = defaultdict(int)
        for partnership, evidence_list in year_relationships.items():
            officials = partnership.split("-")
            for official in officials:
                official_activity[official] += len(evidence_list)

        return sorted(official_activity.items(), key=lambda x: x[1], reverse=True)[:3]

    def _analyze_cooperation_types(self, year_relationships: Dict) -> Dict[str, int]:
        """Analyze types of cooperation in a given year."""
        cooperation_types = defaultdict(int)
        for evidence_list in year_relationships.values():
            for evidence in evidence_list:
                evidence_type = evidence.get("type", "general")
                cooperation_types[evidence_type] += 1
        return dict(cooperation_types)

    def _analyze_cooperation_trends(self, yearly_analysis: Dict) -> Dict[str, Any]:
        """Analyze trends in cooperation over time."""
        years = sorted(yearly_analysis.keys())
        if len(years) < 2:
            return {"trend": "insufficient_data"}

        # Calculate trends
        total_interactions = [yearly_analysis[year]["total_interactions"] for year in years]
        unique_partnerships = [yearly_analysis[year]["unique_partnerships"] for year in years]

        return {
            "interaction_trend": "increasing" if total_interactions[-1] > total_interactions[0] else "decreasing",
            "partnership_trend": "expanding" if unique_partnerships[-1] > unique_partnerships[0] else "contracting",
            "peak_cooperation_year": years[total_interactions.index(max(total_interactions))],
            "trend_strength": self._calculate_trend_strength(total_interactions)
        }

    def _calculate_trend_strength(self, values: List[int]) -> float:
        """Calculate strength of trend in values."""
        if len(values) < 2:
            return 0.0

        # Simple linear trend calculation
        x_values = list(range(len(values)))
        mean_x = sum(x_values) / len(x_values)
        mean_y = sum(values) / len(values)

        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, values))
        denominator = sum((x - mean_x) ** 2 for x in x_values)

        if denominator == 0:
            return 0.0

        slope = numerator / denominator
        return min(1.0, abs(slope) / mean_y) if mean_y > 0 else 0.0

    def _generate_period_summaries(self, yearly_analysis: Dict) -> Dict[str, str]:
        """Generate summaries for different time periods."""
        years = sorted(yearly_analysis.keys())
        if not years:
            return {}

        # Define periods
        periods = {
            "early_2000s": [y for y in years if 2000 <= y <= 2009],
            "2010s": [y for y in years if 2010 <= y <= 2019],
            "2020s": [y for y in years if 2020 <= y <= 2029]
        }

        summaries = {}
        for period_name, period_years in periods.items():
            if not period_years:
                continue

            period_data = [yearly_analysis[year] for year in period_years]
            avg_interactions = sum(d["total_interactions"] for d in period_data) / len(period_data)
            avg_partnerships = sum(d["unique_partnerships"] for d in period_data) / len(period_data)

            summaries[period_name] = (
                f"Average {avg_interactions:.1f} interactions/year, "
                f"{avg_partnerships:.1f} unique partnerships/year across {len(period_years)} years"
            )

        return summaries