"""
Multi-level issue coordination analyzer for tracking issue advocacy across jurisdictions.
Identifies how Staten Island officials coordinate on issues across federal, state, and municipal levels.
"""
import asyncio
from typing import Dict, List, Optional, Tuple, Set, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
import structlog

from data.staten_island_officials import STATEN_ISLAND_OFFICIALS
from utils.temporal_analyzer import TemporalAnalyzer
from analyzers.relationship_tracker import RelationshipTracker

logger = structlog.get_logger()


class CoordinationLevel(Enum):
    """Levels of multi-jurisdictional coordination."""
    FEDERAL_STATE = "federal_state"
    STATE_MUNICIPAL = "state_municipal"
    FEDERAL_MUNICIPAL = "federal_municipal"
    CROSS_JURISDICTION = "cross_jurisdiction"  # All three levels
    INTRA_FEDERAL = "intra_federal"  # Senate-House coordination
    INTRA_STATE = "intra_state"  # Senate-Assembly coordination
    INTRA_MUNICIPAL = "intra_municipal"  # Council-Borough President coordination


class IssueStage(Enum):
    """Stages of issue development and resolution."""
    IDENTIFICATION = "identification"  # Issue identified/raised
    ADVOCACY = "advocacy"  # Active advocacy/lobbying
    LEGISLATION = "legislation"  # Bills/resolutions introduced
    IMPLEMENTATION = "implementation"  # Funding/programs secured
    EVALUATION = "evaluation"  # Results assessment


@dataclass
class IssueAdvocacy:
    """Single official's advocacy on a specific issue."""
    official: str
    issue: str
    jurisdiction_level: str
    position_type: str
    advocacy_actions: List[str]
    stage: IssueStage
    date_range: Tuple[datetime, datetime]
    outcomes_achieved: List[str]
    coordination_evidence: List[str]


@dataclass
class CoordinatedIssue:
    """Multi-level coordination on a specific issue."""
    issue_name: str
    issue_description: str
    coordination_level: CoordinationLevel
    participating_officials: List[str]
    advocacy_timeline: List[IssueAdvocacy]
    coordination_evidence: List[str]
    outcomes_achieved: List[str]
    success_metrics: Dict[str, float]
    coordination_effectiveness: float


class IssueCoordinator:
    """Analyzes multi-level issue coordination among Staten Island officials."""

    def __init__(self):
        self.temporal_analyzer = TemporalAnalyzer()
        self.relationship_tracker = RelationshipTracker()
        self.issue_cache = {}
        self.coordination_patterns = self._initialize_coordination_patterns()

    def _initialize_coordination_patterns(self) -> Dict[str, Dict]:
        """Initialize patterns for identifying issue coordination."""
        return {
            "infrastructure_issues": {
                "keywords": ["bridge", "tunnel", "road", "transportation", "infrastructure"],
                "typical_coordination": [CoordinationLevel.FEDERAL_STATE, CoordinationLevel.CROSS_JURISDICTION],
                "funding_sources": ["federal", "state", "municipal"],
                "key_outcomes": ["funding secured", "project approved", "construction began"]
            },
            "transportation_issues": {
                "keywords": ["ferry", "bus", "transit", "mta", "transportation"],
                "typical_coordination": [CoordinationLevel.STATE_MUNICIPAL, CoordinationLevel.FEDERAL_STATE],
                "funding_sources": ["state", "federal"],
                "key_outcomes": ["service improved", "funding increased", "routes expanded"]
            },
            "climate_resilience": {
                "keywords": ["flooding", "resilience", "climate", "storm", "coastal protection"],
                "typical_coordination": [CoordinationLevel.CROSS_JURISDICTION],
                "funding_sources": ["federal", "state"],
                "key_outcomes": ["infrastructure built", "funding secured", "protection implemented"]
            },
            "healthcare_issues": {
                "keywords": ["hospital", "healthcare", "medical", "health services"],
                "typical_coordination": [CoordinationLevel.FEDERAL_STATE, CoordinationLevel.STATE_MUNICIPAL],
                "funding_sources": ["federal", "state"],
                "key_outcomes": ["funding secured", "services expanded", "facility built"]
            },
            "economic_development": {
                "keywords": ["economic", "development", "business", "jobs", "investment"],
                "typical_coordination": [CoordinationLevel.STATE_MUNICIPAL, CoordinationLevel.CROSS_JURISDICTION],
                "funding_sources": ["state", "municipal", "federal"],
                "key_outcomes": ["investment secured", "jobs created", "development approved"]
            }
        }

    async def analyze_all_coordinated_issues(self) -> Dict[str, CoordinatedIssue]:
        """Analyze all coordinated issues among Staten Island officials."""
        coordinated_issues = {}

        # Extract all issues from official data
        all_issues = self._extract_all_issues()

        for issue_name, issue_data in all_issues.items():
            coordinated_issue = await self._analyze_issue_coordination(issue_name, issue_data)
            if coordinated_issue and coordinated_issue.coordination_effectiveness > 0.3:
                coordinated_issues[issue_name] = coordinated_issue

        return coordinated_issues

    def _extract_all_issues(self) -> Dict[str, Dict]:
        """Extract all issues mentioned across officials."""
        all_issues = defaultdict(lambda: {
            "mentions": [],
            "advocacies": [],
            "achievements": []
        })

        for official, data in STATEN_ISLAND_OFFICIALS.items():
            # Extract from focus areas
            focus_areas = data.get("focus_areas", [])
            for area in focus_areas:
                all_issues[area]["mentions"].append({
                    "official": official,
                    "type": "focus_area",
                    "jurisdiction": data.get("position_type", "")
                })

            # Extract from achievements
            achievements = data.get("achievements", [])
            for achievement in achievements:
                description = achievement.get("description", "")
                year = achievement.get("year", "2020")

                # Categorize achievement by issue type
                for issue_type, patterns in self.coordination_patterns.items():
                    if any(keyword in description.lower() for keyword in patterns["keywords"]):
                        all_issues[issue_type]["achievements"].append({
                            "official": official,
                            "description": description,
                            "year": year,
                            "jurisdiction": data.get("position_type", "")
                        })

            # Extract from position evolution
            position_evolution = data.get("position_evolution", {})
            for issue, positions in position_evolution.items():
                all_issues[issue]["advocacies"].extend([{
                    "official": official,
                    "position": pos.get("position", ""),
                    "date": pos.get("date", "2020-01-01"),
                    "jurisdiction": data.get("position_type", "")
                } for pos in positions])

            # Extract from relationships (joint initiatives)
            relationships = data.get("relationships", {})
            for partner, rel_data in relationships.items():
                for evidence in rel_data.get("evidence", []):
                    description = evidence.get("description", "")
                    for issue_type, patterns in self.coordination_patterns.items():
                        if any(keyword in description.lower() for keyword in patterns["keywords"]):
                            all_issues[issue_type]["advocacies"].append({
                                "official": official,
                                "partner": partner,
                                "description": description,
                                "date": evidence.get("date", "2020-01-01"),
                                "type": "joint_initiative"
                            })

        return dict(all_issues)

    async def _analyze_issue_coordination(self, issue_name: str, issue_data: Dict) -> Optional[CoordinatedIssue]:
        """Analyze coordination for a specific issue."""
        # Identify participating officials
        participating_officials = set()
        for data_type, items in issue_data.items():
            for item in items:
                participating_officials.add(item.get("official", ""))

        participating_officials = list(participating_officials)

        if len(participating_officials) < 2:
            return None  # No coordination if only one official

        # Build advocacy timeline
        advocacy_timeline = await self._build_advocacy_timeline(issue_name, issue_data)

        # Determine coordination level
        coordination_level = self._determine_coordination_level(participating_officials)

        # Extract coordination evidence
        coordination_evidence = self._extract_coordination_evidence(issue_data)

        # Calculate effectiveness
        coordination_effectiveness = self._calculate_coordination_effectiveness(
            advocacy_timeline, coordination_evidence, participating_officials
        )

        # Extract outcomes
        outcomes_achieved = self._extract_outcomes(issue_data)

        # Calculate success metrics
        success_metrics = self._calculate_success_metrics(advocacy_timeline, outcomes_achieved)

        return CoordinatedIssue(
            issue_name=issue_name,
            issue_description=self._generate_issue_description(issue_name, issue_data),
            coordination_level=coordination_level,
            participating_officials=participating_officials,
            advocacy_timeline=advocacy_timeline,
            coordination_evidence=coordination_evidence,
            outcomes_achieved=outcomes_achieved,
            success_metrics=success_metrics,
            coordination_effectiveness=coordination_effectiveness
        )

    async def _build_advocacy_timeline(self, issue_name: str, issue_data: Dict) -> List[IssueAdvocacy]:
        """Build chronological timeline of advocacy actions."""
        timeline = []

        # Process advocacies
        for advocacy in issue_data.get("advocacies", []):
            if "date" in advocacy:
                date = datetime.strptime(advocacy.get("date", "2020-01-01"), "%Y-%m-%d")
                timeline.append(IssueAdvocacy(
                    official=advocacy.get("official", ""),
                    issue=issue_name,
                    jurisdiction_level=self._get_jurisdiction_level(advocacy.get("jurisdiction", "")),
                    position_type=advocacy.get("jurisdiction", ""),
                    advocacy_actions=[advocacy.get("description", advocacy.get("position", ""))],
                    stage=IssueStage.ADVOCACY,
                    date_range=(date, date),
                    outcomes_achieved=[],
                    coordination_evidence=[]
                ))

        # Process achievements as implementation stage
        for achievement in issue_data.get("achievements", []):
            year = int(achievement.get("year", "2020"))
            date = datetime(year, 1, 1)
            timeline.append(IssueAdvocacy(
                official=achievement.get("official", ""),
                issue=issue_name,
                jurisdiction_level=self._get_jurisdiction_level(achievement.get("jurisdiction", "")),
                position_type=achievement.get("jurisdiction", ""),
                advocacy_actions=[achievement.get("description", "")],
                stage=IssueStage.IMPLEMENTATION,
                date_range=(date, date),
                outcomes_achieved=[achievement.get("description", "")],
                coordination_evidence=[]
            ))

        # Sort by date
        timeline.sort(key=lambda x: x.date_range[0])
        return timeline

    def _get_jurisdiction_level(self, position_type: str) -> str:
        """Map position type to jurisdiction level."""
        position_type_lower = position_type.lower()
        if "senator" in position_type_lower and "state" not in position_type_lower:
            return "federal"
        elif "representative" in position_type_lower or "congress" in position_type_lower:
            return "federal"
        elif "state" in position_type_lower or "assembly" in position_type_lower:
            return "state"
        elif "council" in position_type_lower or "borough" in position_type_lower or "mayor" in position_type_lower:
            return "municipal"
        else:
            return "unknown"

    def _determine_coordination_level(self, participating_officials: List[str]) -> CoordinationLevel:
        """Determine the level of coordination based on participating officials."""
        jurisdictions = set()
        for official in participating_officials:
            official_data = STATEN_ISLAND_OFFICIALS.get(official, {})
            position_type = official_data.get("position_type", "")
            jurisdictions.add(self._get_jurisdiction_level(position_type))

        jurisdictions.discard("unknown")

        if len(jurisdictions) >= 3:
            return CoordinationLevel.CROSS_JURISDICTION
        elif "federal" in jurisdictions and "state" in jurisdictions:
            return CoordinationLevel.FEDERAL_STATE
        elif "state" in jurisdictions and "municipal" in jurisdictions:
            return CoordinationLevel.STATE_MUNICIPAL
        elif "federal" in jurisdictions and "municipal" in jurisdictions:
            return CoordinationLevel.FEDERAL_MUNICIPAL
        elif "federal" in jurisdictions:
            return CoordinationLevel.INTRA_FEDERAL
        elif "state" in jurisdictions:
            return CoordinationLevel.INTRA_STATE
        elif "municipal" in jurisdictions:
            return CoordinationLevel.INTRA_MUNICIPAL
        else:
            return CoordinationLevel.CROSS_JURISDICTION

    def _extract_coordination_evidence(self, issue_data: Dict) -> List[str]:
        """Extract evidence of coordination from issue data."""
        evidence = []

        for advocacy in issue_data.get("advocacies", []):
            if advocacy.get("type") == "joint_initiative":
                evidence.append(f"Joint initiative between {advocacy.get('official')} and {advocacy.get('partner')}: {advocacy.get('description')}")
            elif "partner" in advocacy:
                evidence.append(f"Coordinated advocacy by {advocacy.get('official')} with {advocacy.get('partner')}")

        # Look for coordination keywords in descriptions
        coordination_keywords = ["jointly", "together", "coordinated", "partnership", "collaboration"]
        for achievement in issue_data.get("achievements", []):
            description = achievement.get("description", "")
            if any(keyword in description.lower() for keyword in coordination_keywords):
                evidence.append(f"Coordinated achievement by {achievement.get('official')}: {description}")

        return evidence

    def _calculate_coordination_effectiveness(self, advocacy_timeline: List[IssueAdvocacy],
                                           coordination_evidence: List[str],
                                           participating_officials: List[str]) -> float:
        """Calculate overall coordination effectiveness."""
        if not advocacy_timeline:
            return 0.0

        # Base score from number of participants
        participation_score = min(1.0, len(participating_officials) / 5.0)

        # Evidence strength score
        evidence_score = min(1.0, len(coordination_evidence) / 3.0)

        # Timeline consistency score
        timeline_score = self._calculate_timeline_consistency(advocacy_timeline)

        # Outcome achievement score
        outcome_score = len([a for a in advocacy_timeline if a.outcomes_achieved]) / len(advocacy_timeline)

        # Weighted average
        return (participation_score * 0.25 + evidence_score * 0.35 +
                timeline_score * 0.20 + outcome_score * 0.20)

    def _calculate_timeline_consistency(self, advocacy_timeline: List[IssueAdvocacy]) -> float:
        """Calculate consistency of advocacy timeline."""
        if len(advocacy_timeline) < 2:
            return 0.5

        # Check for temporal clustering (coordination tends to happen close in time)
        dates = [a.date_range[0] for a in advocacy_timeline]
        dates.sort()

        # Calculate average time between advocacy actions
        time_gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
        avg_gap = sum(time_gaps) / len(time_gaps) if time_gaps else 0

        # Score based on consistency (closer together = more coordinated)
        if avg_gap <= 30:  # Within a month
            return 1.0
        elif avg_gap <= 90:  # Within a quarter
            return 0.8
        elif avg_gap <= 365:  # Within a year
            return 0.6
        else:
            return 0.3

    def _extract_outcomes(self, issue_data: Dict) -> List[str]:
        """Extract achieved outcomes from issue data."""
        outcomes = []
        for achievement in issue_data.get("achievements", []):
            outcomes.append(achievement.get("description", ""))
        return outcomes

    def _calculate_success_metrics(self, advocacy_timeline: List[IssueAdvocacy],
                                 outcomes_achieved: List[str]) -> Dict[str, float]:
        """Calculate various success metrics."""
        if not advocacy_timeline:
            return {}

        return {
            "advocacy_to_outcome_ratio": len(outcomes_achieved) / len(advocacy_timeline) if advocacy_timeline else 0,
            "multi_stage_progression": len(set(a.stage for a in advocacy_timeline)) / len(IssueStage),
            "jurisdiction_coverage": len(set(a.jurisdiction_level for a in advocacy_timeline)) / 3.0,  # federal, state, municipal
            "temporal_span_years": (max(a.date_range[0] for a in advocacy_timeline) -
                                  min(a.date_range[0] for a in advocacy_timeline)).days / 365.25
        }

    def _generate_issue_description(self, issue_name: str, issue_data: Dict) -> str:
        """Generate human-readable issue description."""
        participating_count = len(set(item.get("official", "") for items in issue_data.values() for item in items))
        achievement_count = len(issue_data.get("achievements", []))
        advocacy_count = len(issue_data.get("advocacies", []))

        return (f"{issue_name} coordination involving {participating_count} officials, "
                f"{advocacy_count} advocacy actions, {achievement_count} achievements")

    async def analyze_coordination_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in multi-level coordination."""
        coordinated_issues = await self.analyze_all_coordinated_issues()

        # Analyze by coordination level
        coordination_by_level = defaultdict(list)
        for issue in coordinated_issues.values():
            coordination_by_level[issue.coordination_level.value].append(issue)

        # Analyze most effective coordination patterns
        effectiveness_by_level = {}
        for level, issues in coordination_by_level.items():
            if issues:
                effectiveness_by_level[level] = sum(i.coordination_effectiveness for i in issues) / len(issues)

        # Analyze by issue type
        effectiveness_by_issue_type = {}
        for issue_name, issue in coordinated_issues.items():
            issue_type = self._classify_issue_type(issue_name)
            if issue_type not in effectiveness_by_issue_type:
                effectiveness_by_issue_type[issue_type] = []
            effectiveness_by_issue_type[issue_type].append(issue.coordination_effectiveness)

        for issue_type, effectiveness_scores in effectiveness_by_issue_type.items():
            effectiveness_by_issue_type[issue_type] = sum(effectiveness_scores) / len(effectiveness_scores)

        # Identify coordination champions
        official_coordination_scores = defaultdict(list)
        for issue in coordinated_issues.values():
            for official in issue.participating_officials:
                official_coordination_scores[official].append(issue.coordination_effectiveness)

        coordination_champions = {}
        for official, scores in official_coordination_scores.items():
            coordination_champions[official] = {
                "average_effectiveness": sum(scores) / len(scores),
                "coordination_count": len(scores),
                "total_coordination_score": sum(scores)
            }

        return {
            "coordination_summary": {
                "total_coordinated_issues": len(coordinated_issues),
                "average_effectiveness": sum(i.coordination_effectiveness for i in coordinated_issues.values()) / len(coordinated_issues) if coordinated_issues else 0,
                "most_effective_coordination_level": max(effectiveness_by_level.items(), key=lambda x: x[1]) if effectiveness_by_level else None
            },
            "effectiveness_by_level": effectiveness_by_level,
            "effectiveness_by_issue_type": effectiveness_by_issue_type,
            "coordination_champions": dict(sorted(coordination_champions.items(),
                                                key=lambda x: x[1]["total_coordination_score"], reverse=True)),
            "detailed_issues": {name: {
                "coordination_level": issue.coordination_level.value,
                "effectiveness": issue.coordination_effectiveness,
                "participating_officials": issue.participating_officials,
                "outcomes_count": len(issue.outcomes_achieved)
            } for name, issue in coordinated_issues.items()}
        }

    def _classify_issue_type(self, issue_name: str) -> str:
        """Classify issue by type based on keywords."""
        issue_name_lower = issue_name.lower()
        for issue_type, patterns in self.coordination_patterns.items():
            if any(keyword in issue_name_lower for keyword in patterns["keywords"]):
                return issue_type
        return "other"

    async def generate_coordination_report(self) -> Dict[str, Any]:
        """Generate comprehensive coordination analysis report."""
        coordinated_issues = await self.analyze_all_coordinated_issues()
        coordination_patterns = await self.analyze_coordination_patterns()

        # Generate recommendations
        recommendations = self._generate_coordination_recommendations(coordination_patterns)

        return {
            "executive_summary": self._generate_executive_summary(coordination_patterns),
            "coordination_patterns": coordination_patterns,
            "detailed_issues": coordinated_issues,
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }

    def _generate_executive_summary(self, coordination_patterns: Dict) -> Dict[str, str]:
        """Generate executive summary of coordination analysis."""
        summary_data = coordination_patterns["coordination_summary"]
        champions = coordination_patterns["coordination_champions"]

        top_coordinator = max(champions.items(), key=lambda x: x[1]["total_coordination_score"]) if champions else None

        return {
            "overview": f"Analysis of {summary_data['total_coordinated_issues']} coordinated issues among Staten Island officials",
            "effectiveness": f"Average coordination effectiveness: {summary_data['average_effectiveness']:.2f}",
            "top_coordinator": f"Most active coordinator: {top_coordinator[0]} with {top_coordinator[1]['coordination_count']} coordinated issues" if top_coordinator else "No clear top coordinator identified",
            "best_coordination_level": f"Most effective coordination level: {summary_data['most_effective_coordination_level'][0]}" if summary_data.get('most_effective_coordination_level') else "No standout coordination level"
        }

    def _generate_coordination_recommendations(self, coordination_patterns: Dict) -> List[str]:
        """Generate recommendations for improving coordination."""
        recommendations = []

        effectiveness_by_level = coordination_patterns["effectiveness_by_level"]
        if effectiveness_by_level:
            best_level = max(effectiveness_by_level.items(), key=lambda x: x[1])
            recommendations.append(f"Focus on {best_level[0]} coordination - shows highest effectiveness ({best_level[1]:.2f})")

        effectiveness_by_issue = coordination_patterns["effectiveness_by_issue_type"]
        if effectiveness_by_issue:
            best_issue_type = max(effectiveness_by_issue.items(), key=lambda x: x[1])
            recommendations.append(f"Leverage successful {best_issue_type[0]} coordination model for other issues")

        champions = coordination_patterns["coordination_champions"]
        if champions:
            top_champions = sorted(champions.items(), key=lambda x: x[1]["total_coordination_score"], reverse=True)[:3]
            recommendations.append(f"Expand coordination network around proven coordinators: {', '.join([c[0] for c in top_champions])}")

        return recommendations