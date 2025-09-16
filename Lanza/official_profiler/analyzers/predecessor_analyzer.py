"""
Predecessor analysis system for tracking political continuity and transitions.
Analyzes relationships, policy evolution, and institutional memory across 25 years.
"""
import asyncio
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, Counter
import structlog

from data.predecessor_mapping import (
    STATEN_ISLAND_PREDECESSORS,
    OfficialTenure,
    get_official_timeline,
    get_all_predecessors_summary,
    get_electoral_transitions,
    analyze_continuity_patterns
)
from data.staten_island_officials import STATEN_ISLAND_OFFICIALS

logger = structlog.get_logger()


class TransitionType(Enum):
    """Types of political transitions."""
    ELECTORAL_DEFEAT = "electoral_defeat"
    RETIREMENT = "retirement"
    TERM_LIMITS = "term_limits"
    OFFICE_CHANGE = "office_change"  # Moving to different office
    RESIGNATION = "resignation"
    DEATH = "death"


class ContinuityLevel(Enum):
    """Levels of policy/relationship continuity."""
    HIGH_CONTINUITY = "high_continuity"      # >80% overlap
    MODERATE_CONTINUITY = "moderate_continuity"  # 60-80% overlap
    LOW_CONTINUITY = "low_continuity"        # 40-60% overlap
    DISCONTINUITY = "discontinuity"          # <40% overlap


@dataclass
class TransitionAnalysis:
    """Analysis of a specific political transition."""
    position: str
    transition_year: int
    outgoing_official: str
    incoming_official: str
    transition_type: TransitionType
    party_change: bool
    policy_continuity_score: float
    relationship_continuity_score: float
    institutional_disruption_level: float
    key_changes: List[str]
    continuity_factors: List[str]
    external_influences: List[str]


@dataclass
class SuccessionPattern:
    """Pattern analysis for official succession chains."""
    position: str
    succession_chain: List[str]
    average_tenure_length: float
    party_stability: float
    policy_consistency_score: float
    relationship_network_evolution: Dict[str, float]
    critical_transition_points: List[Tuple[int, str]]


@dataclass
class InstitutionalMemory:
    """Analysis of institutional memory preservation."""
    position: str
    memory_preservation_score: float
    knowledge_transfer_indicators: List[str]
    relationship_preservation: Dict[str, float]
    policy_wisdom_retention: List[str]
    lost_capabilities: List[str]
    enhanced_capabilities: List[str]


class PredecessorAnalyzer:
    """Analyzes predecessor relationships and institutional continuity."""

    def __init__(self):
        self.transition_cache = {}
        self.continuity_patterns = {}
        self.institutional_memory_cache = {}

    async def analyze_all_transitions(self) -> List[TransitionAnalysis]:
        """Analyze all political transitions in the 25-year period."""
        transitions = []
        electoral_transitions = get_electoral_transitions()

        for trans_data in electoral_transitions:
            if trans_data["year"] >= 2000:  # Within our analysis period
                analysis = await self._analyze_single_transition(trans_data)
                transitions.append(analysis)

        return sorted(transitions, key=lambda x: x.transition_year)

    async def _analyze_single_transition(self, transition_data: Dict) -> TransitionAnalysis:
        """Analyze a single political transition."""
        position = transition_data["position"]
        year = transition_data["year"]
        outgoing = transition_data["outgoing_official"]
        incoming = transition_data["incoming_official"]

        # Determine transition type
        transition_type = self._classify_transition_type(transition_data["transition_type"])

        # Calculate policy continuity
        policy_continuity = await self._calculate_policy_continuity(
            position, outgoing, incoming, year
        )

        # Calculate relationship continuity
        relationship_continuity = await self._calculate_relationship_continuity(
            position, outgoing, incoming, year
        )

        # Calculate institutional disruption
        disruption_level = self._calculate_disruption_level(
            transition_data, policy_continuity, relationship_continuity
        )

        # Identify key changes and continuity factors
        key_changes = self._identify_key_changes(transition_data, year)
        continuity_factors = self._identify_continuity_factors(
            position, outgoing, incoming, year
        )

        # Identify external influences
        external_influences = self._identify_external_influences(year)

        return TransitionAnalysis(
            position=position,
            transition_year=year,
            outgoing_official=outgoing,
            incoming_official=incoming,
            transition_type=transition_type,
            party_change=transition_data["party_change"],
            policy_continuity_score=policy_continuity,
            relationship_continuity_score=relationship_continuity,
            institutional_disruption_level=disruption_level,
            key_changes=key_changes,
            continuity_factors=continuity_factors,
            external_influences=external_influences
        )

    def _classify_transition_type(self, transition_reason: str) -> TransitionType:
        """Classify the type of transition."""
        reason_map = {
            "defeated": TransitionType.ELECTORAL_DEFEAT,
            "retired": TransitionType.RETIREMENT,
            "term_limited": TransitionType.TERM_LIMITS,
            "moved_to_other_office": TransitionType.OFFICE_CHANGE,
            "resigned": TransitionType.RESIGNATION,
            "died": TransitionType.DEATH
        }
        return reason_map.get(transition_reason, TransitionType.ELECTORAL_DEFEAT)

    async def _calculate_policy_continuity(self, position: str, outgoing: str,
                                         incoming: str, year: int) -> float:
        """Calculate policy continuity score between officials."""
        # Get achievement themes for both officials
        outgoing_themes = self._extract_policy_themes(position, outgoing)
        incoming_themes = self._extract_policy_themes(position, incoming)

        if not outgoing_themes or not incoming_themes:
            return 0.5  # Neutral score for insufficient data

        # Calculate overlap
        common_themes = set(outgoing_themes) & set(incoming_themes)
        total_themes = set(outgoing_themes) | set(incoming_themes)

        if not total_themes:
            return 0.5

        overlap_score = len(common_themes) / len(total_themes)

        # Adjust for contextual factors
        context_adjustment = self._get_contextual_policy_adjustment(year)

        return min(1.0, max(0.0, overlap_score + context_adjustment))

    def _extract_policy_themes(self, position: str, official_name: str) -> List[str]:
        """Extract policy themes from official's achievements."""
        themes = []

        # Find the official in predecessor data
        for tenure in STATEN_ISLAND_PREDECESSORS.get(position, []):
            if tenure.name == official_name:
                for achievement in tenure.key_achievements:
                    achievement_lower = achievement.lower()

                    # Extract themes
                    if any(word in achievement_lower for word in ["transport", "ferry", "bridge"]):
                        themes.append("transportation")
                    if any(word in achievement_lower for word in ["infrastructure", "development"]):
                        themes.append("infrastructure")
                    if any(word in achievement_lower for word in ["hurricane", "sandy", "recovery"]):
                        themes.append("disaster_recovery")
                    if any(word in achievement_lower for word in ["healthcare", "health"]):
                        themes.append("healthcare")
                    if any(word in achievement_lower for word in ["veterans", "military"]):
                        themes.append("veterans")
                    if any(word in achievement_lower for word in ["economic", "business"]):
                        themes.append("economic_development")
                    if any(word in achievement_lower for word in ["criminal", "justice", "safety"]):
                        themes.append("public_safety")
                    if any(word in achievement_lower for word in ["environment", "climate"]):
                        themes.append("environmental")
                break

        return themes

    def _get_contextual_policy_adjustment(self, year: int) -> float:
        """Get contextual adjustment for policy continuity based on external events."""
        # Major events that typically force policy focus changes
        major_events = {
            2001: -0.2,  # 9/11 - security focus shift
            2008: -0.15, # Financial crisis - economic focus
            2012: -0.1,  # Hurricane Sandy - resilience focus
            2020: -0.15  # COVID-19 - health/economic focus
        }

        # Check for events in transition year +/- 1
        for event_year, adjustment in major_events.items():
            if abs(year - event_year) <= 1:
                return adjustment

        return 0.0

    async def _calculate_relationship_continuity(self, position: str, outgoing: str,
                                               incoming: str, year: int) -> float:
        """Calculate relationship network continuity."""
        # This would analyze whether the incoming official maintained
        # similar relationships/partnerships as the outgoing official

        # For Staten Island context, key relationships would include:
        # - Federal-State coordination
        # - State-Municipal coordination
        # - Cross-party cooperation
        # - Community organization partnerships

        position_type = self._get_position_type(position)

        # Base scores by position type (federal positions have more continuity)
        base_scores = {
            "federal": 0.7,    # Federal positions have institutional continuity
            "state": 0.6,      # State positions have moderate continuity
            "municipal": 0.5   # Municipal positions more variable
        }

        base_score = base_scores.get(position_type, 0.5)

        # Adjust for party changes (typically reduce relationship continuity)
        party_adjustment = -0.2 if self._had_party_change(position, outgoing, incoming) else 0.0

        # Adjust for transition type
        transition_adjustment = self._get_transition_relationship_adjustment(
            self._get_transition_reason(position, incoming)
        )

        return min(1.0, max(0.0, base_score + party_adjustment + transition_adjustment))

    def _get_position_type(self, position: str) -> str:
        """Get the type of position (federal, state, municipal)."""
        if "us_" in position:
            return "federal"
        elif "ny_" in position:
            return "state"
        elif "nyc_" in position or "si_borough" in position:
            return "municipal"
        else:
            return "unknown"

    def _had_party_change(self, position: str, outgoing: str, incoming: str) -> bool:
        """Check if there was a party change in transition."""
        outgoing_party = None
        incoming_party = None

        for tenure in STATEN_ISLAND_PREDECESSORS.get(position, []):
            if tenure.name == outgoing:
                outgoing_party = tenure.party
            elif tenure.name == incoming:
                incoming_party = tenure.party

        return outgoing_party != incoming_party if outgoing_party and incoming_party else False

    def _get_transition_reason(self, position: str, official_name: str) -> str:
        """Get transition reason for an official."""
        for tenure in STATEN_ISLAND_PREDECESSORS.get(position, []):
            if tenure.name == official_name and tenure.predecessor:
                # Find predecessor tenure to get transition reason
                for pred_tenure in STATEN_ISLAND_PREDECESSORS.get(position, []):
                    if pred_tenure.name == tenure.predecessor:
                        return pred_tenure.transition_reason
        return "unknown"

    def _get_transition_relationship_adjustment(self, transition_reason: str) -> float:
        """Get relationship continuity adjustment based on transition type."""
        adjustments = {
            "retired": 0.1,      # Planned transition, better handoff
            "defeated": -0.15,   # Abrupt change, less continuity
            "term_limited": 0.05, # Planned but forced change
            "moved_to_other_office": 0.0,  # Neutral
            "resigned": -0.1     # Unplanned change
        }
        return adjustments.get(transition_reason, 0.0)

    def _calculate_disruption_level(self, transition_data: Dict,
                                  policy_continuity: float,
                                  relationship_continuity: float) -> float:
        """Calculate institutional disruption level (0-1, higher = more disruptive)."""
        base_disruption = 1.0 - ((policy_continuity + relationship_continuity) / 2)

        # Additional disruption factors
        if transition_data["party_change"]:
            base_disruption += 0.1

        if transition_data["transition_type"] in ["defeated", "resigned"]:
            base_disruption += 0.1

        # Major external events increase disruption
        year = transition_data["year"]
        if year in [2001, 2008, 2012, 2020]:
            base_disruption += 0.05

        return min(1.0, base_disruption)

    def _identify_key_changes(self, transition_data: Dict, year: int) -> List[str]:
        """Identify key changes associated with a transition."""
        changes = []

        if transition_data["party_change"]:
            changes.append(f"Party control change: {transition_data['outgoing_party']} → {transition_data['incoming_party']}")

        # Add context-specific changes based on year
        if year == 2001:
            changes.append("Post-9/11 security and recovery focus")
        elif year == 2008:
            changes.append("Financial crisis response priorities")
        elif year == 2012:
            changes.append("Hurricane Sandy recovery emphasis")
        elif year == 2020:
            changes.append("COVID-19 pandemic response focus")

        # Add transition-specific changes
        context = transition_data.get("context", {})
        if context.get("incoming_focus"):
            changes.extend([f"New focus: {focus}" for focus in context["incoming_focus"]])

        return changes

    def _identify_continuity_factors(self, position: str, outgoing: str,
                                   incoming: str, year: int) -> List[str]:
        """Identify factors that preserved continuity."""
        factors = []

        # Policy theme continuity
        outgoing_themes = self._extract_policy_themes(position, outgoing)
        incoming_themes = self._extract_policy_themes(position, incoming)
        common_themes = set(outgoing_themes) & set(incoming_themes)

        for theme in common_themes:
            factors.append(f"Continued {theme} focus")

        # Institutional factors
        position_type = self._get_position_type(position)
        if position_type == "federal":
            factors.append("Federal institutional continuity")
        elif position_type == "state":
            factors.append("State legislative process continuity")

        # Staten Island specific factors
        factors.extend([
            "Staten Island constituency priorities",
            "Infrastructure development needs",
            "Transportation system requirements"
        ])

        return factors

    def _identify_external_influences(self, year: int) -> List[str]:
        """Identify external influences affecting the transition."""
        influences = []

        # National political climate
        if 2001 <= year <= 2008:
            influences.append("Post-9/11 national security focus")
        elif 2009 <= year <= 2016:
            influences.append("Obama administration policies")
        elif 2017 <= year <= 2020:
            influences.append("Trump administration policies")
        elif year >= 2021:
            influences.append("Biden administration policies")

        # Economic cycles
        if year in [2001, 2008, 2020]:
            influences.append("Economic recession/crisis")
        elif 2010 <= year <= 2019:
            influences.append("Economic recovery period")

        # Major events
        event_influences = {
            2001: "9/11 attacks impact",
            2008: "Financial crisis impact",
            2012: "Hurricane Sandy aftermath",
            2020: "COVID-19 pandemic impact"
        }

        if year in event_influences:
            influences.append(event_influences[year])

        return influences

    async def analyze_succession_patterns(self) -> List[SuccessionPattern]:
        """Analyze patterns in official succession chains."""
        patterns = []

        for position, tenures in STATEN_ISLAND_PREDECESSORS.items():
            if len(tenures) < 2:
                continue

            # Calculate metrics
            succession_chain = [t.name for t in tenures]

            # Average tenure length
            tenure_lengths = []
            for tenure in tenures:
                start_year = datetime.strptime(tenure.start_date, "%Y-%m-%d").year
                end_year = datetime.strptime(tenure.end_date, "%Y-%m-%d").year
                tenure_lengths.append(end_year - start_year)

            avg_tenure = sum(tenure_lengths) / len(tenure_lengths)

            # Party stability (what % of time was same party?)
            party_counts = Counter(t.party for t in tenures)
            dominant_party_count = max(party_counts.values())
            party_stability = dominant_party_count / len(tenures)

            # Policy consistency score
            all_themes = []
            for tenure in tenures:
                all_themes.extend(self._extract_policy_themes(position, tenure.name))

            theme_counts = Counter(all_themes)
            if theme_counts:
                # Score based on how consistently themes appear
                consistency_score = sum(count for count in theme_counts.values() if count > 1) / len(all_themes)
            else:
                consistency_score = 0.0

            # Critical transition points (major disruptions)
            critical_points = []
            for i, tenure in enumerate(tenures[1:], 1):
                prev_tenure = tenures[i-1]
                if (prev_tenure.party != tenure.party or
                    prev_tenure.transition_reason in ["defeated", "resigned"]):

                    transition_year = datetime.strptime(tenure.start_date, "%Y-%m-%d").year
                    critical_points.append((transition_year, f"{prev_tenure.name} → {tenure.name}"))

            pattern = SuccessionPattern(
                position=position,
                succession_chain=succession_chain,
                average_tenure_length=avg_tenure,
                party_stability=party_stability,
                policy_consistency_score=consistency_score,
                relationship_network_evolution={},  # Would need more detailed analysis
                critical_transition_points=critical_points
            )

            patterns.append(pattern)

        return patterns

    async def analyze_institutional_memory(self) -> List[InstitutionalMemory]:
        """Analyze institutional memory preservation across transitions."""
        memory_analyses = []

        for position, tenures in STATEN_ISLAND_PREDECESSORS.items():
            if len(tenures) < 2:
                continue

            # Calculate memory preservation score
            total_knowledge_areas = set()
            preserved_knowledge = set()

            for i, tenure in enumerate(tenures):
                current_knowledge = set(self._extract_policy_themes(position, tenure.name))
                total_knowledge_areas.update(current_knowledge)

                if i > 0:  # Has predecessor
                    prev_knowledge = set(self._extract_policy_themes(position, tenures[i-1].name))
                    preserved_knowledge.update(current_knowledge & prev_knowledge)

            memory_score = len(preserved_knowledge) / len(total_knowledge_areas) if total_knowledge_areas else 0.0

            # Identify knowledge transfer indicators
            transfer_indicators = []
            for tenure in tenures:
                if any(word in " ".join(tenure.key_achievements).lower()
                      for word in ["continued", "expanded", "built upon", "enhanced"]):
                    transfer_indicators.append(f"{tenure.name}: Built upon predecessor work")

            # Policy wisdom retention
            wisdom_retained = []
            themes = [theme for tenure in tenures for theme in self._extract_policy_themes(position, tenure.name)]
            persistent_themes = [theme for theme, count in Counter(themes).items() if count >= len(tenures) // 2]
            wisdom_retained.extend([f"Persistent focus on {theme}" for theme in persistent_themes])

            # Enhanced capabilities (new areas developed)
            enhanced_capabilities = []
            if len(tenures) > 1:
                early_themes = set()
                recent_themes = set()

                for tenure in tenures[:len(tenures)//2]:
                    early_themes.update(self._extract_policy_themes(position, tenure.name))

                for tenure in tenures[len(tenures)//2:]:
                    recent_themes.update(self._extract_policy_themes(position, tenure.name))

                new_capabilities = recent_themes - early_themes
                enhanced_capabilities.extend([f"Developed {capability} expertise" for capability in new_capabilities])

            memory_analysis = InstitutionalMemory(
                position=position,
                memory_preservation_score=memory_score,
                knowledge_transfer_indicators=transfer_indicators,
                relationship_preservation={},  # Would need detailed relationship analysis
                policy_wisdom_retention=wisdom_retained,
                lost_capabilities=[],  # Would need more detailed analysis
                enhanced_capabilities=enhanced_capabilities
            )

            memory_analyses.append(memory_analysis)

        return memory_analyses

    async def generate_comprehensive_predecessor_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive analysis of all predecessor patterns."""
        # Run all analyses
        transitions = await self.analyze_all_transitions()
        succession_patterns = await self.analyze_succession_patterns()
        institutional_memory = await self.analyze_institutional_memory()

        # Get summary data
        summary = get_all_predecessors_summary()
        continuity_patterns = analyze_continuity_patterns()

        # Calculate aggregate metrics
        avg_policy_continuity = sum(t.policy_continuity_score for t in transitions) / len(transitions) if transitions else 0
        avg_relationship_continuity = sum(t.relationship_continuity_score for t in transitions) / len(transitions) if transitions else 0
        avg_disruption = sum(t.institutional_disruption_level for t in transitions) / len(transitions) if transitions else 0

        # Identify most stable positions
        stable_positions = sorted(succession_patterns, key=lambda x: x.party_stability, reverse=True)[:3]

        # Identify most disruptive transitions
        disruptive_transitions = sorted(transitions, key=lambda x: x.institutional_disruption_level, reverse=True)[:5]

        return {
            "executive_summary": {
                "total_officials_analyzed": summary["total_officials"],
                "positions_tracked": summary["positions_tracked"],
                "analysis_period": "2000-2025",
                "average_policy_continuity": avg_policy_continuity,
                "average_relationship_continuity": avg_relationship_continuity,
                "average_disruption_level": avg_disruption
            },
            "transition_analysis": {
                "total_transitions": len(transitions),
                "party_changes": len([t for t in transitions if t.party_change]),
                "most_disruptive": [
                    {
                        "position": t.position,
                        "year": t.transition_year,
                        "transition": f"{t.outgoing_official} → {t.incoming_official}",
                        "disruption_level": t.institutional_disruption_level
                    } for t in disruptive_transitions
                ],
                "detailed_transitions": [
                    {
                        "position": t.position,
                        "year": t.transition_year,
                        "officials": f"{t.outgoing_official} → {t.incoming_official}",
                        "party_change": t.party_change,
                        "policy_continuity": t.policy_continuity_score,
                        "relationship_continuity": t.relationship_continuity_score,
                        "key_changes": t.key_changes
                    } for t in transitions
                ]
            },
            "succession_patterns": {
                "most_stable_positions": [
                    {
                        "position": p.position,
                        "party_stability": p.party_stability,
                        "average_tenure": p.average_tenure_length,
                        "policy_consistency": p.policy_consistency_score
                    } for p in stable_positions
                ],
                "detailed_patterns": [
                    {
                        "position": p.position,
                        "succession_chain": p.succession_chain,
                        "average_tenure_years": p.average_tenure_length,
                        "party_stability": p.party_stability,
                        "critical_transitions": p.critical_transition_points
                    } for p in succession_patterns
                ]
            },
            "institutional_memory": {
                "memory_preservation_scores": [
                    {
                        "position": m.position,
                        "memory_score": m.memory_preservation_score,
                        "knowledge_transfer_indicators": len(m.knowledge_transfer_indicators),
                        "wisdom_retained": m.policy_wisdom_retention
                    } for m in institutional_memory
                ],
                "knowledge_continuity": continuity_patterns["policy_continuity"]
            },
            "predecessor_summary": summary,
            "generated_at": datetime.now().isoformat()
        }