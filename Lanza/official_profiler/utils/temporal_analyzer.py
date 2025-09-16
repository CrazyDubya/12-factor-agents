"""
Temporal analysis system for tracking position evolution and historical changes.
Enhanced with predecessor data integration for 25-year analysis.
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
from data.predecessor_mapping import STATEN_ISLAND_PREDECESSORS, get_official_timeline
from analyzers.predecessor_analyzer import PredecessorAnalyzer
from analyzers.position_evolution_tracker import PositionEvolutionTracker

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
        self.predecessor_analyzer = PredecessorAnalyzer()
        self.position_tracker = PositionEvolutionTracker()
        self.predecessor_cache = {}

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

    async def analyze_25_year_evolution(self, position: str, issue: str = None) -> Dict[str, Any]:
        """Comprehensive 25-year evolution analysis including all predecessors."""
        timeline = get_official_timeline(position, 2000, 2025)

        if not timeline:
            return {"error": f"No timeline data for position {position}"}

        evolution_analysis = {
            "position": position,
            "analysis_period": "2000-2025",
            "total_officials": len(timeline),
            "official_timeline": [],
            "transition_analysis": [],
            "policy_evolution": {},
            "institutional_continuity": {}
        }

        # Build official timeline with achievements
        for tenure in timeline:
            start_year = datetime.strptime(tenure.start_date, "%Y-%m-%d").year
            end_year = datetime.strptime(tenure.end_date, "%Y-%m-%d").year

            official_data = {
                "name": tenure.name,
                "party": tenure.party,
                "start_year": start_year,
                "end_year": end_year,
                "tenure_length": end_year - start_year,
                "key_achievements": tenure.key_achievements,
                "transition_reason": tenure.transition_reason
            }
            evolution_analysis["official_timeline"].append(official_data)

        # Analyze transitions
        transitions = await self.predecessor_analyzer.analyze_all_transitions()
        position_transitions = [t for t in transitions if t.position == position]

        for transition in position_transitions:
            transition_data = {
                "year": transition.transition_year,
                "outgoing": transition.outgoing_official,
                "incoming": transition.incoming_official,
                "party_change": transition.party_change,
                "transition_type": transition.transition_type.value,
                "policy_continuity": transition.policy_continuity_score,
                "relationship_continuity": transition.relationship_continuity_score,
                "disruption_level": transition.institutional_disruption_level,
                "key_changes": transition.key_changes
            }
            evolution_analysis["transition_analysis"].append(transition_data)

        # Issue-specific analysis if specified
        if issue:
            issue_evolution = await self.position_tracker.track_issue_evolution(issue, position)
            evolution_analysis["policy_evolution"][issue] = {
                "evolution_type": issue_evolution.evolution_type.value,
                "timeline_snapshots": len(issue_evolution.evolution_timeline),
                "driving_factors": issue_evolution.driving_factors,
                "stability_periods": issue_evolution.stability_periods,
                "change_points": issue_evolution.change_points,
                "current_trajectory": issue_evolution.current_trajectory
            }

        # Institutional continuity analysis
        succession_patterns = await self.predecessor_analyzer.analyze_succession_patterns()
        position_pattern = next((p for p in succession_patterns if p.position == position), None)

        if position_pattern:
            evolution_analysis["institutional_continuity"] = {
                "average_tenure_length": position_pattern.average_tenure_length,
                "party_stability": position_pattern.party_stability,
                "policy_consistency": position_pattern.policy_consistency_score,
                "critical_transitions": position_pattern.critical_transition_points
            }

        return evolution_analysis

    async def compare_predecessor_chains(self, positions: List[str],
                                       issue: str = None) -> Dict[str, Any]:
        """Compare evolution patterns across multiple predecessor chains."""
        comparison_analysis = {
            "positions_compared": positions,
            "comparison_period": "2000-2025",
            "individual_analyses": {},
            "comparative_metrics": {},
            "synchronization_analysis": {},
            "divergence_points": []
        }

        # Analyze each position individually
        for position in positions:
            position_analysis = await self.analyze_25_year_evolution(position, issue)
            comparison_analysis["individual_analyses"][position] = position_analysis

        # Comparative metrics
        all_timelines = []
        for position in positions:
            timeline = get_official_timeline(position, 2000, 2025)
            all_timelines.append((position, timeline))

        # Calculate comparative metrics
        tenure_lengths = {}
        party_stability = {}
        transition_frequency = {}

        for position, timeline in all_timelines:
            if timeline:
                # Average tenure length
                tenures = []
                for tenure in timeline:
                    start_year = datetime.strptime(tenure.start_date, "%Y-%m-%d").year
                    end_year = datetime.strptime(tenure.end_date, "%Y-%m-%d").year
                    tenures.append(end_year - start_year)

                tenure_lengths[position] = sum(tenures) / len(tenures) if tenures else 0

                # Party stability (% of time with same party)
                party_counts = {}
                total_years = 0
                for tenure in timeline:
                    start_year = datetime.strptime(tenure.start_date, "%Y-%m-%d").year
                    end_year = datetime.strptime(tenure.end_date, "%Y-%m-%d").year
                    years = end_year - start_year

                    if tenure.party not in party_counts:
                        party_counts[tenure.party] = 0
                    party_counts[tenure.party] += years
                    total_years += years

                max_party_years = max(party_counts.values()) if party_counts else 0
                party_stability[position] = max_party_years / total_years if total_years > 0 else 0

                # Transition frequency
                transition_frequency[position] = len(timeline) / 25  # transitions per year

        comparison_analysis["comparative_metrics"] = {
            "average_tenure_lengths": tenure_lengths,
            "party_stability_scores": party_stability,
            "transition_frequencies": transition_frequency
        }

        # Synchronization analysis (when positions changed simultaneously)
        if issue:
            sync_analysis = await self._analyze_cross_position_synchronization(positions, issue)
            comparison_analysis["synchronization_analysis"] = sync_analysis

        # Identify major divergence points
        divergence_points = await self._identify_divergence_points(positions)
        comparison_analysis["divergence_points"] = divergence_points

        return comparison_analysis

    async def _analyze_cross_position_synchronization(self, positions: List[str],
                                                    issue: str) -> Dict[str, Any]:
        """Analyze synchronization of position changes across multiple offices."""
        sync_analysis = {
            "synchronized_periods": [],
            "divergent_periods": [],
            "coordination_score": 0.0
        }

        # Get issue evolution for each position
        evolutions = {}
        for position in positions:
            evolution = await self.position_tracker.track_issue_evolution(issue, position)
            if evolution.evolution_timeline:
                evolutions[position] = evolution

        if len(evolutions) < 2:
            return sync_analysis

        # Find synchronized change points
        all_change_points = {}
        for position, evolution in evolutions.items():
            change_points = [cp[0] for cp in evolution.change_points]  # Extract years
            all_change_points[position] = change_points

        # Identify synchronized changes (within 2 years)
        sync_tolerance = 2
        synchronized_changes = []

        for pos1, changes1 in all_change_points.items():
            for pos2, changes2 in all_change_points.items():
                if pos1 < pos2:  # Avoid duplicates
                    for year1 in changes1:
                        for year2 in changes2:
                            if abs(year1 - year2) <= sync_tolerance:
                                synchronized_changes.append({
                                    "year_range": f"{min(year1, year2)}-{max(year1, year2)}",
                                    "positions": [pos1, pos2],
                                    "description": f"Synchronized policy change on {issue}"
                                })

        sync_analysis["synchronized_periods"] = synchronized_changes

        # Calculate overall coordination score
        total_changes = sum(len(changes) for changes in all_change_points.values())
        synchronized_count = len(synchronized_changes) * 2  # Each sync affects 2 positions

        sync_analysis["coordination_score"] = (synchronized_count / total_changes
                                             if total_changes > 0 else 0.0)

        return sync_analysis

    async def _identify_divergence_points(self, positions: List[str]) -> List[Dict[str, Any]]:
        """Identify major divergence points between position chains."""
        divergences = []

        # Get all transitions for these positions
        all_transitions = await self.predecessor_analyzer.analyze_all_transitions()
        position_transitions = {pos: [] for pos in positions}

        for transition in all_transitions:
            if transition.position in positions:
                position_transitions[transition.position].append(transition)

        # Look for years where positions diverged (party changes, major policy shifts)
        years_with_changes = set()
        for transitions in position_transitions.values():
            for transition in transitions:
                years_with_changes.add(transition.transition_year)

        for year in sorted(years_with_changes):
            year_changes = {}
            for position in positions:
                position_changes = [t for t in position_transitions[position]
                                  if t.transition_year == year]
                if position_changes:
                    year_changes[position] = position_changes[0]

            if len(year_changes) > 1:
                # Check for divergent patterns
                party_changes = [t.party_change for t in year_changes.values()]
                disruption_levels = [t.institutional_disruption_level for t in year_changes.values()]

                if any(party_changes) or max(disruption_levels) > 0.7:
                    divergence = {
                        "year": year,
                        "positions_affected": list(year_changes.keys()),
                        "divergence_type": "political_realignment" if any(party_changes) else "policy_shift",
                        "average_disruption": sum(disruption_levels) / len(disruption_levels),
                        "details": [
                            f"{pos}: {t.outgoing_official} → {t.incoming_official} ({t.transition_type.value})"
                            for pos, t in year_changes.items()
                        ]
                    }
                    divergences.append(divergence)

        return divergences

    async def generate_comprehensive_temporal_report(self) -> Dict[str, Any]:
        """Generate comprehensive temporal analysis report including all predecessor data."""
        report = {
            "executive_summary": {},
            "25_year_overview": {},
            "position_analyses": {},
            "comparative_analysis": {},
            "issue_evolution": {},
            "institutional_memory": {},
            "generated_at": datetime.now().isoformat()
        }

        # Generate 25-year overview
        summary = await self.predecessor_analyzer.generate_comprehensive_predecessor_analysis()
        report["25_year_overview"] = summary["executive_summary"]

        # Analyze key positions
        key_positions = [
            "us_senate_ny_senior", "us_senate_ny_junior", "us_house_ny11",
            "ny_senate_district_24", "si_borough_president"
        ]

        for position in key_positions:
            position_analysis = await self.analyze_25_year_evolution(position)
            report["position_analyses"][position] = position_analysis

        # Comparative analysis across positions
        comparison = await self.compare_predecessor_chains(key_positions)
        report["comparative_analysis"] = comparison

        # Issue evolution analysis
        key_issues = ["transportation_infrastructure", "healthcare_access", "economic_development"]
        for issue in key_issues:
            issue_report = await self.position_tracker.analyze_cross_position_coordination(issue)
            report["issue_evolution"][issue] = {
                "federal_state_alignment": issue_report.federal_state_alignment,
                "jurisdictional_consistency": issue_report.jurisdictional_consistency,
                "coordination_evidence_count": len(issue_report.coordination_evidence),
                "conflict_evidence_count": len(issue_report.conflict_evidence)
            }

        # Institutional memory analysis
        institutional_analysis = await self.predecessor_analyzer.analyze_institutional_memory()
        report["institutional_memory"] = {
            "positions_analyzed": len(institutional_analysis),
            "average_memory_preservation": (
                sum(m.memory_preservation_score for m in institutional_analysis) /
                len(institutional_analysis) if institutional_analysis else 0
            ),
            "knowledge_transfer_indicators": sum(
                len(m.knowledge_transfer_indicators) for m in institutional_analysis
            )
        }

        # Executive summary
        report["executive_summary"] = {
            "analysis_scope": "Staten Island political representation 2000-2025",
            "total_officials_tracked": summary["executive_summary"]["total_officials_analyzed"],
            "positions_analyzed": len(key_positions),
            "major_transitions": len([t for t in summary["transition_analysis"]["detailed_transitions"]
                                   if t["party_change"]]),
            "average_policy_continuity": summary["executive_summary"]["average_policy_continuity"],
            "institutional_stability": summary["executive_summary"]["average_disruption_level"]
        }

        return report