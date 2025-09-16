"""
Position evolution tracker for mapping policy changes through predecessor chains.
Analyzes how positions on key issues evolved across different officials over 25 years.
"""
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, Counter
import structlog

from data.predecessor_mapping import STATEN_ISLAND_PREDECESSORS, OfficialTenure
from data.staten_island_officials import STATEN_ISLAND_OFFICIALS
from analyzers.predecessor_analyzer import PredecessorAnalyzer

logger = structlog.get_logger()


class PositionEvolutionType(Enum):
    """Types of position evolution patterns."""
    GRADUAL_SHIFT = "gradual_shift"
    SUDDEN_CHANGE = "sudden_change"
    CYCLICAL_RETURN = "cyclical_return"
    PROGRESSIVE_DEVELOPMENT = "progressive_development"
    REACTIVE_ADAPTATION = "reactive_adaptation"
    CONSISTENT_ADVOCACY = "consistent_advocacy"


class IssueStance(Enum):
    """Stance on policy issues."""
    STRONG_SUPPORT = "strong_support"
    MODERATE_SUPPORT = "moderate_support"
    NEUTRAL = "neutral"
    MODERATE_OPPOSITION = "moderate_opposition"
    STRONG_OPPOSITION = "strong_opposition"
    NO_POSITION = "no_position"


@dataclass
class PositionSnapshot:
    """Snapshot of an official's position on a specific issue."""
    official: str
    position_title: str
    issue: str
    stance: IssueStance
    year: int
    evidence: List[str]
    context: str
    external_factors: List[str]
    confidence: float  # 0-1 confidence in position assessment


@dataclass
class IssueEvolution:
    """Evolution of positions on a specific issue across time."""
    issue: str
    position_title: str
    evolution_timeline: List[PositionSnapshot]
    evolution_type: PositionEvolutionType
    driving_factors: List[str]
    stability_periods: List[Tuple[int, int, str]]  # (start_year, end_year, description)
    change_points: List[Tuple[int, str, str]]  # (year, reason, description)
    current_trajectory: str
    predictive_indicators: List[str]


@dataclass
class CrossPositionAnalysis:
    """Analysis of how different positions approach the same issue."""
    issue: str
    position_approaches: Dict[str, List[PositionSnapshot]]
    coordination_evidence: List[str]
    conflict_evidence: List[str]
    federal_state_alignment: float  # -1 to 1
    jurisdictional_consistency: float  # 0 to 1
    temporal_synchronization: float  # 0 to 1


class PositionEvolutionTracker:
    """Tracks evolution of policy positions through predecessor chains."""

    def __init__(self):
        self.predecessor_analyzer = PredecessorAnalyzer()
        self.evolution_cache = {}
        self.issue_mapping = self._initialize_issue_mapping()

    def _initialize_issue_mapping(self) -> Dict[str, Dict]:
        """Initialize mapping of issues and their detection patterns."""
        return {
            "transportation_infrastructure": {
                "keywords": [
                    "transportation", "ferry", "bridge", "tunnel", "road", "highway",
                    "verrazzano", "staten island ferry", "bus", "rail", "transit"
                ],
                "key_developments": {
                    2001: "Post-9/11 security considerations",
                    2008: "Economic stimulus infrastructure focus",
                    2012: "Hurricane Sandy damage and resilience",
                    2019: "Congestion pricing debates",
                    2021: "Infrastructure Investment and Jobs Act"
                }
            },
            "healthcare_access": {
                "keywords": [
                    "healthcare", "hospital", "medical", "health insurance", "medicaid",
                    "richmond university medical center", "staten island university hospital"
                ],
                "key_developments": {
                    2010: "Affordable Care Act implementation",
                    2012: "Hurricane Sandy healthcare system damage",
                    2020: "COVID-19 pandemic response",
                    2021: "Mental health crisis recognition"
                }
            },
            "economic_development": {
                "keywords": [
                    "economic development", "business", "jobs", "investment", "development",
                    "small business", "tourism", "port", "manufacturing"
                ],
                "key_developments": {
                    2001: "Post-9/11 economic recovery",
                    2008: "Financial crisis response",
                    2012: "Hurricane Sandy economic impact",
                    2020: "COVID-19 economic disruption"
                }
            },
            "environmental_climate": {
                "keywords": [
                    "environment", "climate", "flooding", "coastal protection", "resilience",
                    "clean energy", "pollution", "green infrastructure"
                ],
                "key_developments": {
                    2007: "Climate change awareness rise",
                    2012: "Hurricane Sandy climate wake-up call",
                    2015: "Paris Climate Agreement",
                    2021: "Green New Deal discussions"
                }
            },
            "public_safety": {
                "keywords": [
                    "public safety", "police", "fire", "emergency", "crime", "law enforcement",
                    "homeland security", "911", "first responders"
                ],
                "key_developments": {
                    2001: "Post-9/11 security transformation",
                    2008: "Community policing emphasis",
                    2020: "Police reform discussions",
                    2021: "Public safety reimagining"
                }
            },
            "veterans_affairs": {
                "keywords": [
                    "veterans", "military", "va", "veteran affairs", "armed forces",
                    "military families", "veteran benefits"
                ],
                "key_developments": {
                    2001: "Post-9/11 veteran care expansion",
                    2007: "Iraq/Afghanistan veteran issues",
                    2014: "VA scandal and reform",
                    2021: "Veteran suicide prevention focus"
                }
            },
            "housing_development": {
                "keywords": [
                    "housing", "development", "affordable housing", "zoning", "real estate",
                    "homeownership", "rental", "public housing"
                ],
                "key_developments": {
                    2008: "Housing crisis and foreclosures",
                    2012: "Hurricane Sandy housing damage",
                    2020: "COVID-19 housing insecurity",
                    2021: "Housing affordability crisis"
                }
            }
        }

    async def track_issue_evolution(self, issue: str, position: str) -> IssueEvolution:
        """Track evolution of a specific issue across officials in a position."""
        if issue not in self.issue_mapping:
            raise ValueError(f"Issue '{issue}' not in tracking system")

        # Get all officials who held this position
        timeline = []
        if position in STATEN_ISLAND_PREDECESSORS:
            for tenure in STATEN_ISLAND_PREDECESSORS[position]:
                # Extract position snapshots for this official and issue
                snapshots = await self._extract_position_snapshots(
                    tenure, issue, position
                )
                timeline.extend(snapshots)

        # Sort by year
        timeline.sort(key=lambda x: x.year)

        if not timeline:
            return self._create_empty_evolution(issue, position)

        # Analyze evolution pattern
        evolution_type = self._classify_evolution_pattern(timeline)
        driving_factors = self._identify_driving_factors(timeline, issue)
        stability_periods = self._identify_stability_periods(timeline)
        change_points = self._identify_change_points(timeline, issue)
        current_trajectory = self._analyze_current_trajectory(timeline)
        predictive_indicators = self._extract_predictive_indicators(timeline, issue)

        return IssueEvolution(
            issue=issue,
            position_title=position,
            evolution_timeline=timeline,
            evolution_type=evolution_type,
            driving_factors=driving_factors,
            stability_periods=stability_periods,
            change_points=change_points,
            current_trajectory=current_trajectory,
            predictive_indicators=predictive_indicators
        )

    async def _extract_position_snapshots(self, tenure: OfficialTenure,
                                        issue: str, position: str) -> List[PositionSnapshot]:
        """Extract position snapshots for an official on a specific issue."""
        snapshots = []
        issue_config = self.issue_mapping[issue]

        # Analyze achievements for issue-related positions
        for achievement in tenure.key_achievements:
            achievement_lower = achievement.lower()

            # Check if achievement relates to this issue
            relevance_score = 0
            for keyword in issue_config["keywords"]:
                if keyword in achievement_lower:
                    relevance_score += 1

            if relevance_score > 0:
                # Determine stance from achievement language
                stance = self._extract_stance_from_text(achievement)

                # Determine year (approximate from tenure period)
                start_year = datetime.strptime(tenure.start_date, "%Y-%m-%d").year
                end_year = datetime.strptime(tenure.end_date, "%Y-%m-%d").year

                # Create snapshot for mid-point of tenure
                snapshot_year = start_year + (end_year - start_year) // 2

                # Get external factors for this year
                external_factors = self._get_external_factors(snapshot_year, issue)

                snapshot = PositionSnapshot(
                    official=tenure.name,
                    position_title=position,
                    issue=issue,
                    stance=stance,
                    year=snapshot_year,
                    evidence=[achievement],
                    context=f"During {tenure.party} tenure ({start_year}-{end_year})",
                    external_factors=external_factors,
                    confidence=min(1.0, relevance_score * 0.3)  # Scale by relevance
                )
                snapshots.append(snapshot)

        return snapshots

    def _extract_stance_from_text(self, text: str) -> IssueStance:
        """Extract policy stance from achievement text."""
        text_lower = text.lower()

        # Strong support indicators
        strong_support = [
            "secured", "delivered", "passed", "established", "created", "expanded",
            "championed", "led", "pioneered", "achieved"
        ]

        # Moderate support indicators
        moderate_support = [
            "supported", "advocated", "promoted", "endorsed", "backed",
            "worked for", "pushed for"
        ]

        # Opposition indicators
        opposition = [
            "opposed", "blocked", "prevented", "stopped", "defeated",
            "rejected", "voted against"
        ]

        # Check for strong support
        if any(indicator in text_lower for indicator in strong_support):
            return IssueStance.STRONG_SUPPORT

        # Check for moderate support
        elif any(indicator in text_lower for indicator in moderate_support):
            return IssueStance.MODERATE_SUPPORT

        # Check for opposition
        elif any(indicator in text_lower for indicator in opposition):
            return IssueStance.MODERATE_OPPOSITION

        # Default to moderate support for positive achievements
        else:
            return IssueStance.MODERATE_SUPPORT

    def _get_external_factors(self, year: int, issue: str) -> List[str]:
        """Get external factors that might influence position on issue in given year."""
        factors = []

        # General external factors
        if 2001 <= year <= 2002:
            factors.append("Post-9/11 national security focus")
        elif 2008 <= year <= 2010:
            factors.append("Economic recession and recovery")
        elif 2012 <= year <= 2014:
            factors.append("Hurricane Sandy aftermath")
        elif 2020 <= year <= 2022:
            factors.append("COVID-19 pandemic impact")

        # Issue-specific factors
        issue_config = self.issue_mapping.get(issue, {})
        key_developments = issue_config.get("key_developments", {})

        for dev_year, development in key_developments.items():
            if abs(year - dev_year) <= 1:  # Within 1 year
                factors.append(development)

        return factors

    def _classify_evolution_pattern(self, timeline: List[PositionSnapshot]) -> PositionEvolutionType:
        """Classify the type of evolution pattern."""
        if len(timeline) < 2:
            return PositionEvolutionType.CONSISTENT_ADVOCACY

        # Convert stances to numeric for analysis
        stance_values = {
            IssueStance.STRONG_OPPOSITION: -2,
            IssueStance.MODERATE_OPPOSITION: -1,
            IssueStance.NEUTRAL: 0,
            IssueStance.MODERATE_SUPPORT: 1,
            IssueStance.STRONG_SUPPORT: 2,
            IssueStance.NO_POSITION: 0
        }

        values = [stance_values[snapshot.stance] for snapshot in timeline]

        # Calculate change over time
        total_change = abs(values[-1] - values[0])
        variance = sum((v - sum(values)/len(values))**2 for v in values) / len(values)

        # Classify pattern
        if total_change <= 0.5:
            return PositionEvolutionType.CONSISTENT_ADVOCACY
        elif variance > 1.5:
            return PositionEvolutionType.CYCLICAL_RETURN
        elif total_change >= 2:
            return PositionEvolutionType.SUDDEN_CHANGE
        elif self._has_progressive_development(timeline):
            return PositionEvolutionType.PROGRESSIVE_DEVELOPMENT
        elif self._has_reactive_adaptation(timeline):
            return PositionEvolutionType.REACTIVE_ADAPTATION
        else:
            return PositionEvolutionType.GRADUAL_SHIFT

    def _has_progressive_development(self, timeline: List[PositionSnapshot]) -> bool:
        """Check if timeline shows progressive development pattern."""
        # Progressive development: increasing sophistication/specificity over time
        evidence_complexity = []
        for snapshot in timeline:
            # Measure complexity by evidence detail and specificity
            avg_evidence_length = sum(len(e) for e in snapshot.evidence) / len(snapshot.evidence)
            evidence_complexity.append(avg_evidence_length)

        # Check if evidence becomes more detailed over time
        return len(evidence_complexity) > 1 and evidence_complexity[-1] > evidence_complexity[0] * 1.2

    def _has_reactive_adaptation(self, timeline: List[PositionSnapshot]) -> bool:
        """Check if timeline shows reactive adaptation pattern."""
        # Reactive adaptation: position changes correlate with external factors
        adaptations = 0
        for i in range(1, len(timeline)):
            prev_snapshot = timeline[i-1]
            curr_snapshot = timeline[i]

            # Check if stance changed and there were external factors
            if (prev_snapshot.stance != curr_snapshot.stance and
                len(curr_snapshot.external_factors) > 0):
                adaptations += 1

        return adaptations >= len(timeline) // 2

    def _identify_driving_factors(self, timeline: List[PositionSnapshot], issue: str) -> List[str]:
        """Identify key factors driving position evolution."""
        factors = []

        # External event influences
        all_external_factors = set()
        for snapshot in timeline:
            all_external_factors.update(snapshot.external_factors)

        factors.extend(list(all_external_factors))

        # Party influence
        party_changes = []
        for i in range(1, len(timeline)):
            if timeline[i-1].context != timeline[i].context:  # Different party context
                party_changes.append(f"Party change: {timeline[i].year}")

        factors.extend(party_changes)

        # Issue-specific developments
        issue_config = self.issue_mapping.get(issue, {})
        for year, development in issue_config.get("key_developments", {}).items():
            timeline_years = [s.year for s in timeline]
            if min(timeline_years) <= year <= max(timeline_years):
                factors.append(f"Key development: {development} ({year})")

        return factors

    def _identify_stability_periods(self, timeline: List[PositionSnapshot]) -> List[Tuple[int, int, str]]:
        """Identify periods of stable positions."""
        if len(timeline) < 2:
            return []

        stability_periods = []
        current_start = timeline[0].year
        current_stance = timeline[0].stance

        for i in range(1, len(timeline)):
            if timeline[i].stance != current_stance:
                # End of stability period
                if timeline[i-1].year > current_start:
                    stability_periods.append((
                        current_start,
                        timeline[i-1].year,
                        f"Stable {current_stance.value} stance"
                    ))

                # Start new period
                current_start = timeline[i].year
                current_stance = timeline[i].stance

        # Add final period if it's stable
        if timeline[-1].year > current_start:
            stability_periods.append((
                current_start,
                timeline[-1].year,
                f"Stable {current_stance.value} stance"
            ))

        return stability_periods

    def _identify_change_points(self, timeline: List[PositionSnapshot], issue: str) -> List[Tuple[int, str, str]]:
        """Identify significant change points in position evolution."""
        change_points = []

        for i in range(1, len(timeline)):
            prev_snapshot = timeline[i-1]
            curr_snapshot = timeline[i]

            if prev_snapshot.stance != curr_snapshot.stance:
                # Identify reason for change
                reason = "Unknown"
                if curr_snapshot.external_factors:
                    reason = curr_snapshot.external_factors[0]  # Primary external factor
                elif prev_snapshot.context != curr_snapshot.context:
                    reason = "Leadership change"

                description = f"{prev_snapshot.stance.value} → {curr_snapshot.stance.value}"

                change_points.append((curr_snapshot.year, reason, description))

        return change_points

    def _analyze_current_trajectory(self, timeline: List[PositionSnapshot]) -> str:
        """Analyze current trajectory of position evolution."""
        if len(timeline) < 2:
            return "Insufficient data for trajectory analysis"

        recent_snapshots = timeline[-3:] if len(timeline) >= 3 else timeline

        # Analyze recent trend
        stance_values = {
            IssueStance.STRONG_OPPOSITION: -2,
            IssueStance.MODERATE_OPPOSITION: -1,
            IssueStance.NEUTRAL: 0,
            IssueStance.MODERATE_SUPPORT: 1,
            IssueStance.STRONG_SUPPORT: 2,
            IssueStance.NO_POSITION: 0
        }

        recent_values = [stance_values[s.stance] for s in recent_snapshots]

        if len(recent_values) < 2:
            return "Stable position"

        change = recent_values[-1] - recent_values[0]

        if change > 0.5:
            return "Strengthening support"
        elif change < -0.5:
            return "Weakening support"
        elif abs(change) <= 0.5:
            return "Stable position"
        else:
            return "Mixed signals"

    def _extract_predictive_indicators(self, timeline: List[PositionSnapshot], issue: str) -> List[str]:
        """Extract indicators that might predict future position changes."""
        indicators = []

        if not timeline:
            return indicators

        # Recent external factors
        recent_snapshot = timeline[-1]
        if recent_snapshot.external_factors:
            indicators.extend([
                f"Current influence: {factor}" for factor in recent_snapshot.external_factors
            ])

        # Confidence trends
        if len(timeline) >= 2:
            recent_confidence = timeline[-1].confidence
            prev_confidence = timeline[-2].confidence

            if recent_confidence < prev_confidence * 0.8:
                indicators.append("Decreasing position confidence")
            elif recent_confidence > prev_confidence * 1.2:
                indicators.append("Increasing position confidence")

        # Issue-specific upcoming developments
        issue_config = self.issue_mapping.get(issue, {})
        current_year = datetime.now().year

        for year, development in issue_config.get("key_developments", {}).items():
            if current_year <= year <= current_year + 3:
                indicators.append(f"Upcoming: {development} ({year})")

        return indicators

    def _create_empty_evolution(self, issue: str, position: str) -> IssueEvolution:
        """Create empty evolution for positions with no data."""
        return IssueEvolution(
            issue=issue,
            position_title=position,
            evolution_timeline=[],
            evolution_type=PositionEvolutionType.CONSISTENT_ADVOCACY,
            driving_factors=["Insufficient data"],
            stability_periods=[],
            change_points=[],
            current_trajectory="No data available",
            predictive_indicators=[]
        )

    async def analyze_cross_position_coordination(self, issue: str) -> CrossPositionAnalysis:
        """Analyze how different positions coordinate on the same issue."""
        position_approaches = {}

        # Get position snapshots for all tracked positions
        for position in STATEN_ISLAND_PREDECESSORS.keys():
            evolution = await self.track_issue_evolution(issue, position)
            if evolution.evolution_timeline:
                position_approaches[position] = evolution.evolution_timeline

        if not position_approaches:
            return self._create_empty_cross_analysis(issue)

        # Analyze coordination and conflicts
        coordination_evidence = self._find_coordination_evidence(position_approaches)
        conflict_evidence = self._find_conflict_evidence(position_approaches)

        # Calculate alignment scores
        federal_state_alignment = self._calculate_federal_state_alignment(position_approaches)
        jurisdictional_consistency = self._calculate_jurisdictional_consistency(position_approaches)
        temporal_synchronization = self._calculate_temporal_synchronization(position_approaches)

        return CrossPositionAnalysis(
            issue=issue,
            position_approaches=position_approaches,
            coordination_evidence=coordination_evidence,
            conflict_evidence=conflict_evidence,
            federal_state_alignment=federal_state_alignment,
            jurisdictional_consistency=jurisdictional_consistency,
            temporal_synchronization=temporal_synchronization
        )

    def _find_coordination_evidence(self, position_approaches: Dict[str, List[PositionSnapshot]]) -> List[str]:
        """Find evidence of coordination between positions."""
        evidence = []

        # Look for synchronized timing of similar positions
        years_by_stance = defaultdict(list)
        for position, snapshots in position_approaches.items():
            for snapshot in snapshots:
                years_by_stance[snapshot.stance].append((snapshot.year, position))

        # Find years where multiple positions took similar stances
        for stance, year_position_pairs in years_by_stance.items():
            year_groups = defaultdict(list)
            for year, position in year_position_pairs:
                year_groups[year].append(position)

            for year, positions in year_groups.items():
                if len(positions) > 1:
                    evidence.append(f"{year}: {', '.join(positions)} all took {stance.value} stance")

        return evidence

    def _find_conflict_evidence(self, position_approaches: Dict[str, List[PositionSnapshot]]) -> List[str]:
        """Find evidence of conflicts between positions."""
        evidence = []

        # Group snapshots by year
        snapshots_by_year = defaultdict(list)
        for position, snapshots in position_approaches.items():
            for snapshot in snapshots:
                snapshots_by_year[snapshot.year].append((position, snapshot))

        # Look for opposing stances in same year
        for year, position_snapshots in snapshots_by_year.items():
            if len(position_snapshots) > 1:
                stances = [(pos, snap.stance) for pos, snap in position_snapshots]

                # Check for opposition
                support_positions = [pos for pos, stance in stances
                                   if stance in [IssueStance.STRONG_SUPPORT, IssueStance.MODERATE_SUPPORT]]
                oppose_positions = [pos for pos, stance in stances
                                  if stance in [IssueStance.STRONG_OPPOSITION, IssueStance.MODERATE_OPPOSITION]]

                if support_positions and oppose_positions:
                    evidence.append(f"{year}: {', '.join(support_positions)} supported while {', '.join(oppose_positions)} opposed")

        return evidence

    def _calculate_federal_state_alignment(self, position_approaches: Dict[str, List[PositionSnapshot]]) -> float:
        """Calculate alignment between federal and state positions."""
        federal_positions = [pos for pos in position_approaches.keys() if "us_" in pos]
        state_positions = [pos for pos in position_approaches.keys() if "ny_" in pos]

        if not federal_positions or not state_positions:
            return 0.0  # No alignment possible

        # Compare stances across years
        alignment_scores = []

        for year in range(2000, 2026):
            federal_stances = []
            state_stances = []

            for pos in federal_positions:
                for snapshot in position_approaches.get(pos, []):
                    if snapshot.year == year:
                        federal_stances.append(snapshot.stance)

            for pos in state_positions:
                for snapshot in position_approaches.get(pos, []):
                    if snapshot.year == year:
                        state_stances.append(snapshot.stance)

            if federal_stances and state_stances:
                # Calculate similarity
                stance_values = {
                    IssueStance.STRONG_OPPOSITION: -2,
                    IssueStance.MODERATE_OPPOSITION: -1,
                    IssueStance.NEUTRAL: 0,
                    IssueStance.MODERATE_SUPPORT: 1,
                    IssueStance.STRONG_SUPPORT: 2,
                    IssueStance.NO_POSITION: 0
                }

                fed_avg = sum(stance_values[s] for s in federal_stances) / len(federal_stances)
                state_avg = sum(stance_values[s] for s in state_stances) / len(state_stances)

                # Calculate alignment (-1 to 1, where 1 is perfect alignment)
                max_diff = 4  # Maximum difference between extreme positions
                alignment = 1 - abs(fed_avg - state_avg) / max_diff
                alignment_scores.append(alignment)

        return sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0.0

    def _calculate_jurisdictional_consistency(self, position_approaches: Dict[str, List[PositionSnapshot]]) -> float:
        """Calculate consistency of positions across jurisdictions."""
        if len(position_approaches) < 2:
            return 1.0  # Perfect consistency with single position

        all_stances = []
        for snapshots in position_approaches.values():
            for snapshot in snapshots:
                all_stances.append(snapshot.stance)

        if not all_stances:
            return 0.0

        # Calculate variance in stances
        stance_values = {
            IssueStance.STRONG_OPPOSITION: -2,
            IssueStance.MODERATE_OPPOSITION: -1,
            IssueStance.NEUTRAL: 0,
            IssueStance.MODERATE_SUPPORT: 1,
            IssueStance.STRONG_SUPPORT: 2,
            IssueStance.NO_POSITION: 0
        }

        values = [stance_values[stance] for stance in all_stances]
        mean_value = sum(values) / len(values)
        variance = sum((v - mean_value)**2 for v in values) / len(values)

        # Convert variance to consistency score (0-1)
        max_variance = 4  # Maximum possible variance
        consistency = 1 - (variance / max_variance)

        return max(0.0, min(1.0, consistency))

    def _calculate_temporal_synchronization(self, position_approaches: Dict[str, List[PositionSnapshot]]) -> float:
        """Calculate temporal synchronization of position changes."""
        if len(position_approaches) < 2:
            return 1.0

        # Get all change years for each position
        change_years_by_position = {}
        for position, snapshots in position_approaches.items():
            change_years = []
            for i in range(1, len(snapshots)):
                if snapshots[i].stance != snapshots[i-1].stance:
                    change_years.append(snapshots[i].year)
            change_years_by_position[position] = change_years

        # Calculate synchronization
        all_change_years = set()
        for years in change_years_by_position.values():
            all_change_years.update(years)

        if not all_change_years:
            return 1.0  # No changes to synchronize

        synchronized_changes = 0
        total_changes = sum(len(years) for years in change_years_by_position.values())

        for year in all_change_years:
            positions_changing = sum(1 for years in change_years_by_position.values() if year in years)
            if positions_changing > 1:
                synchronized_changes += positions_changing

        return synchronized_changes / total_changes if total_changes > 0 else 0.0

    def _create_empty_cross_analysis(self, issue: str) -> CrossPositionAnalysis:
        """Create empty cross-position analysis."""
        return CrossPositionAnalysis(
            issue=issue,
            position_approaches={},
            coordination_evidence=[],
            conflict_evidence=[],
            federal_state_alignment=0.0,
            jurisdictional_consistency=0.0,
            temporal_synchronization=0.0
        )

    async def generate_comprehensive_evolution_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive analysis of position evolution across all issues and positions."""
        analysis_results = {}

        # Analyze each issue across all positions
        for issue in self.issue_mapping.keys():
            issue_analysis = {
                "position_evolutions": {},
                "cross_position_analysis": None,
                "key_insights": []
            }

            # Track evolution for each position
            for position in STATEN_ISLAND_PREDECESSORS.keys():
                evolution = await self.track_issue_evolution(issue, position)
                if evolution.evolution_timeline:
                    issue_analysis["position_evolutions"][position] = {
                        "evolution_type": evolution.evolution_type.value,
                        "timeline_length": len(evolution.evolution_timeline),
                        "driving_factors": evolution.driving_factors,
                        "change_points": len(evolution.change_points),
                        "current_trajectory": evolution.current_trajectory
                    }

            # Cross-position analysis
            cross_analysis = await self.analyze_cross_position_coordination(issue)
            issue_analysis["cross_position_analysis"] = {
                "federal_state_alignment": cross_analysis.federal_state_alignment,
                "jurisdictional_consistency": cross_analysis.jurisdictional_consistency,
                "temporal_synchronization": cross_analysis.temporal_synchronization,
                "coordination_evidence_count": len(cross_analysis.coordination_evidence),
                "conflict_evidence_count": len(cross_analysis.conflict_evidence)
            }

            # Generate key insights
            issue_analysis["key_insights"] = self._generate_issue_insights(
                issue, issue_analysis["position_evolutions"], cross_analysis
            )

            analysis_results[issue] = issue_analysis

        # Generate overall summary
        summary = self._generate_overall_summary(analysis_results)

        return {
            "executive_summary": summary,
            "issue_analyses": analysis_results,
            "generated_at": datetime.now().isoformat()
        }

    def _generate_issue_insights(self, issue: str, position_evolutions: Dict,
                               cross_analysis: CrossPositionAnalysis) -> List[str]:
        """Generate key insights for a specific issue."""
        insights = []

        # Evolution pattern insights
        evolution_types = [evo["evolution_type"] for evo in position_evolutions.values()]
        if evolution_types:
            most_common_evolution = Counter(evolution_types).most_common(1)[0][0]
            insights.append(f"Most common evolution pattern: {most_common_evolution}")

        # Coordination insights
        if cross_analysis.federal_state_alignment > 0.7:
            insights.append("Strong federal-state alignment on this issue")
        elif cross_analysis.federal_state_alignment < 0.3:
            insights.append("Significant federal-state divergence on this issue")

        # Consistency insights
        if cross_analysis.jurisdictional_consistency > 0.8:
            insights.append("High jurisdictional consistency across positions")
        elif cross_analysis.jurisdictional_consistency < 0.4:
            insights.append("Significant variation in approaches across jurisdictions")

        # Temporal insights
        if cross_analysis.temporal_synchronization > 0.6:
            insights.append("Position changes tend to be synchronized across officials")

        return insights

    def _generate_overall_summary(self, analysis_results: Dict) -> Dict[str, Any]:
        """Generate overall summary of position evolution analysis."""
        total_evolutions = sum(
            len(issue_data["position_evolutions"])
            for issue_data in analysis_results.values()
        )

        # Calculate average metrics
        alignment_scores = [
            issue_data["cross_position_analysis"]["federal_state_alignment"]
            for issue_data in analysis_results.values()
        ]
        avg_alignment = sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0

        consistency_scores = [
            issue_data["cross_position_analysis"]["jurisdictional_consistency"]
            for issue_data in analysis_results.values()
        ]
        avg_consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0

        # Find most and least coordinated issues
        coordination_by_issue = {
            issue: data["cross_position_analysis"]["federal_state_alignment"]
            for issue, data in analysis_results.items()
        }

        most_coordinated = max(coordination_by_issue.items(), key=lambda x: x[1]) if coordination_by_issue else None
        least_coordinated = min(coordination_by_issue.items(), key=lambda x: x[1]) if coordination_by_issue else None

        return {
            "total_issues_analyzed": len(analysis_results),
            "total_position_evolutions": total_evolutions,
            "average_federal_state_alignment": avg_alignment,
            "average_jurisdictional_consistency": avg_consistency,
            "most_coordinated_issue": most_coordinated[0] if most_coordinated else None,
            "least_coordinated_issue": least_coordinated[0] if least_coordinated else None,
            "analysis_period": "2000-2025"
        }