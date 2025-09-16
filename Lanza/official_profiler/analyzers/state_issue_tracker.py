"""
State-level issue tracking with focus on New York State and Richmond County priorities.
"""
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import structlog
from sqlalchemy.orm import Session
from models.official import Official, Issue, Statement, Vote, PositionEvolution, GeographicLevel
from analyzers.issue_tracker import IssueTracker
from utils.jurisdiction_manager import JurisdictionManager

logger = structlog.get_logger()


class StateIssueTracker(IssueTracker):
    """Enhanced issue tracking for state-level politics and priorities."""

    def __init__(self):
        super().__init__()
        self.jurisdiction_manager = JurisdictionManager()

        # New York State specific issue categories
        self.ny_state_issues = {
            "MTA/Transportation": [
                "mta funding", "subway", "bus service", "congestion pricing",
                "transportation infrastructure", "bridges", "tunnels",
                "ferry service", "staten island expressway"
            ],
            "Housing/Rent": [
                "rent stabilization", "rent control", "housing development",
                "affordable housing", "homeless services", "housing crisis",
                "tenant rights", "landlord regulations"
            ],
            "Taxes/Budget": [
                "property taxes", "income tax", "sales tax", "state budget",
                "municipal aid", "school funding", "pension costs",
                "debt service", "revenue sharing"
            ],
            "Criminal Justice": [
                "bail reform", "criminal justice reform", "police accountability",
                "prison reform", "drug courts", "mental health courts",
                "victim services", "public safety"
            ],
            "Climate/Environment": [
                "climate change", "renewable energy", "offshore wind",
                "environmental justice", "superfund sites", "coastal protection",
                "flood mitigation", "green jobs"
            ],
            "Healthcare": [
                "medicaid", "health insurance", "mental health services",
                "substance abuse", "hospital funding", "nursing homes",
                "prescription drugs", "public health"
            ],
            "Education": [
                "school funding", "university funding", "student debt",
                "teacher training", "school construction", "special education",
                "charter schools", "early childhood education"
            ],
            "Economic Development": [
                "job creation", "small business", "tourism", "port authority",
                "economic incentives", "workforce development", "minimum wage",
                "unemployment benefits"
            ]
        }

        # Richmond County/Staten Island specific priorities
        self.richmond_county_issues = {
            "Transportation": [
                "verrazano bridge tolls", "express bus service", "si ferry",
                "west shore expressway", "goethals bridge", "outerbridge",
                "hylan boulevard", "richmond avenue", "victory boulevard"
            ],
            "Environmental": [
                "fresh kills park", "great kills park", "arthur kill",
                "raritan bay", "flooding", "sewage treatment", "air quality",
                "waste management", "recycling"
            ],
            "Development": [
                "north shore development", "west shore development",
                "stapleton waterfront", "st. george terminal",
                "zoning issues", "historic preservation", "waterfront access"
            ],
            "Healthcare": [
                "richmond university medical center", "hospital services",
                "senior services", "mental health", "addiction services",
                "emergency services"
            ],
            "Education": [
                "cuny college of staten island", "wagner college",
                "public school overcrowding", "school construction",
                "special education services"
            ],
            "Public Safety": [
                "120th precinct", "121st precinct", "122nd precinct",
                "123rd precinct", "fire department", "ems services",
                "traffic safety", "crime prevention"
            ]
        }

    async def analyze_state_legislative_priorities(self, official_id: str,
                                                 db_session: Session,
                                                 session_years: List[int] = None) -> Dict:
        """Analyze state legislative priorities and effectiveness."""
        official = db_session.query(Official).filter_by(id=official_id).first()
        if not official:
            return {"error": "Official not found"}

        if not session_years:
            session_years = [2023, 2022, 2021]  # Default to recent years

        analysis = {
            "official_id": official_id,
            "official_name": official.full_name,
            "jurisdiction_level": official.jurisdiction_level,
            "analysis_period": session_years,
            "state_priorities": {},
            "local_priorities": {},
            "legislative_effectiveness": {},
            "committee_influence": {},
            "coalition_patterns": {},
            "regional_focus": {}
        }

        # Analyze state-level priorities
        analysis["state_priorities"] = await self._analyze_state_priorities(
            official, db_session, session_years
        )

        # Analyze local/regional priorities
        if official.county == "Richmond County" or official.borough == "Staten Island":
            analysis["local_priorities"] = await self._analyze_richmond_priorities(
                official, db_session, session_years
            )

        # Legislative effectiveness analysis
        analysis["legislative_effectiveness"] = await self._analyze_state_legislative_effectiveness(
            official, db_session, session_years
        )

        # Committee influence analysis
        analysis["committee_influence"] = await self._analyze_committee_influence(
            official, db_session
        )

        # Coalition building patterns
        analysis["coalition_patterns"] = await self._analyze_coalition_patterns(
            official, db_session, session_years
        )

        # Regional representation focus
        analysis["regional_focus"] = await self._analyze_regional_representation(
            official, db_session
        )

        return analysis

    async def _analyze_state_priorities(self, official: Official,
                                      db_session: Session,
                                      session_years: List[int]) -> Dict:
        """Analyze engagement with state-level priorities."""
        cutoff_date = datetime.now() - timedelta(days=365 * len(session_years))

        statements = [s for s in official.statements if s.date_made >= cutoff_date]
        votes = [v for v in official.votes if v.vote_date >= cutoff_date]

        state_engagement = defaultdict(int)
        priority_positions = defaultdict(list)

        # Analyze statements for state issue engagement
        for statement in statements:
            statement_text = (statement.content + " " + (statement.summary or "")).lower()

            for category, keywords in self.ny_state_issues.items():
                for keyword in keywords:
                    if keyword in statement_text:
                        state_engagement[category] += 1
                        priority_positions[category].append({
                            "date": statement.date_made,
                            "stance": statement.position_stance,
                            "type": statement.statement_type.value,
                            "summary": statement.summary or statement.content[:200]
                        })

        # Analyze votes for state issue engagement
        for vote in votes:
            vote_text = (vote.bill_title + " " + (vote.bill_summary or "")).lower()

            for category, keywords in self.ny_state_issues.items():
                for keyword in keywords:
                    if keyword in vote_text:
                        state_engagement[category] += 1
                        priority_positions[category].append({
                            "date": vote.vote_date,
                            "stance": "Support" if vote.vote_position in ["Yes", "Aye"] else "Oppose",
                            "type": "vote",
                            "summary": vote.bill_title
                        })

        # Calculate engagement scores
        total_activity = len(statements) + len(votes)
        engagement_scores = {}
        for category, count in state_engagement.items():
            engagement_scores[category] = {
                "raw_count": count,
                "percentage": (count / max(total_activity, 1)) * 100,
                "recent_positions": sorted(priority_positions[category],
                                         key=lambda x: x["date"], reverse=True)[:5]
            }

        return {
            "total_state_engagement": sum(state_engagement.values()),
            "engagement_by_category": engagement_scores,
            "top_priorities": sorted(engagement_scores.items(),
                                   key=lambda x: x[1]["raw_count"], reverse=True)[:5]
        }

    async def _analyze_richmond_priorities(self, official: Official,
                                         db_session: Session,
                                         session_years: List[int]) -> Dict:
        """Analyze engagement with Richmond County/Staten Island specific issues."""
        cutoff_date = datetime.now() - timedelta(days=365 * len(session_years))

        statements = [s for s in official.statements if s.date_made >= cutoff_date]
        votes = [v for v in official.votes if v.vote_date >= cutoff_date]

        richmond_engagement = defaultdict(int)
        local_positions = defaultdict(list)

        # Analyze for Richmond County specific issues
        for statement in statements:
            statement_text = (statement.content + " " + (statement.summary or "")).lower()

            for category, keywords in self.richmond_county_issues.items():
                for keyword in keywords:
                    if keyword in statement_text:
                        richmond_engagement[category] += 1
                        local_positions[category].append({
                            "date": statement.date_made,
                            "stance": statement.position_stance,
                            "type": statement.statement_type.value,
                            "summary": statement.summary or statement.content[:200]
                        })

        # Check for Staten Island specific mentions
        si_mentions = 0
        for statement in statements:
            statement_text = statement.content.lower()
            si_keywords = ["staten island", "richmond county", "borough"]
            if any(keyword in statement_text for keyword in si_keywords):
                si_mentions += 1

        total_activity = len(statements) + len(votes)
        engagement_scores = {}
        for category, count in richmond_engagement.items():
            engagement_scores[category] = {
                "raw_count": count,
                "percentage": (count / max(total_activity, 1)) * 100,
                "recent_positions": sorted(local_positions[category],
                                         key=lambda x: x["date"], reverse=True)[:3]
            }

        return {
            "total_richmond_engagement": sum(richmond_engagement.values()),
            "staten_island_mentions": si_mentions,
            "engagement_by_category": engagement_scores,
            "top_local_priorities": sorted(engagement_scores.items(),
                                         key=lambda x: x[1]["raw_count"], reverse=True)[:3],
            "local_focus_percentage": (sum(richmond_engagement.values()) / max(total_activity, 1)) * 100
        }

    async def _analyze_state_legislative_effectiveness(self, official: Official,
                                                     db_session: Session,
                                                     session_years: List[int]) -> Dict:
        """Analyze effectiveness in state legislature."""
        cutoff_date = datetime.now() - timedelta(days=365 * len(session_years))

        votes = [v for v in official.votes if v.vote_date >= cutoff_date]
        statements = [s for s in official.statements if s.date_made >= cutoff_date]

        effectiveness_metrics = {
            "total_votes": len(votes),
            "key_votes": len([v for v in votes if v.vote_significance == "Key"]),
            "bill_sponsorship": len([v for v in votes if v.vote_type == "Sponsor" and
                                   v.vote_position in ["Yes", "Aye"]]),
            "committee_activity": len([s for s in statements if s.venue and
                                     "committee" in s.venue.lower()]),
            "floor_speeches": len([s for s in statements if s.statement_type.value == "speech"]),
            "press_releases": len([s for s in statements if s.statement_type.value == "press_release"])
        }

        # Calculate effectiveness scores
        activity_score = min((effectiveness_metrics["total_votes"] +
                            effectiveness_metrics["floor_speeches"] +
                            effectiveness_metrics["press_releases"]) / 100, 1.0)

        leadership_score = min((effectiveness_metrics["bill_sponsorship"] +
                              effectiveness_metrics["committee_activity"]) / 20, 1.0)

        overall_effectiveness = (activity_score * 0.6) + (leadership_score * 0.4)

        effectiveness_metrics["scores"] = {
            "activity_score": activity_score,
            "leadership_score": leadership_score,
            "overall_effectiveness": overall_effectiveness
        }

        return effectiveness_metrics

    async def _analyze_committee_influence(self, official: Official,
                                         db_session: Session) -> Dict:
        """Analyze committee assignments and influence."""
        current_position = next((p for p in official.positions if p.is_current), None)

        if not current_position:
            return {"no_current_position": True}

        committee_analysis = {
            "committees": current_position.committees or [],
            "leadership_roles": current_position.leadership_roles or [],
            "committee_relevance": {},
            "influence_score": 0.0
        }

        # Analyze committee relevance to state and local issues
        for committee in (current_position.committees or []):
            relevance_score = self._calculate_committee_relevance(committee)
            committee_analysis["committee_relevance"][committee] = relevance_score

        # Calculate overall influence score
        leadership_bonus = len(committee_analysis["leadership_roles"]) * 0.3
        committee_relevance_avg = (sum(committee_analysis["committee_relevance"].values()) /
                                 max(len(committee_analysis["committee_relevance"]), 1))

        committee_analysis["influence_score"] = min(
            committee_relevance_avg + leadership_bonus, 1.0
        )

        return committee_analysis

    def _calculate_committee_relevance(self, committee_name: str) -> float:
        """Calculate how relevant a committee is to state and local priorities."""
        committee_lower = committee_name.lower()

        # High relevance committees for NY State issues
        high_relevance = [
            "transportation", "housing", "budget", "finance", "appropriations",
            "environmental conservation", "health", "education", "economic development"
        ]

        # Medium relevance committees
        medium_relevance = [
            "local government", "cities", "urban development", "judiciary",
            "labor", "social services", "aging", "mental health"
        ]

        # Special relevance for Richmond County
        richmond_relevance = [
            "transportation", "environmental conservation", "local government",
            "housing", "health", "economic development"
        ]

        score = 0.2  # Base score

        for keyword in high_relevance:
            if keyword in committee_lower:
                score += 0.4
                break

        for keyword in medium_relevance:
            if keyword in committee_lower:
                score += 0.2
                break

        for keyword in richmond_relevance:
            if keyword in committee_lower:
                score += 0.2  # Bonus for local relevance
                break

        return min(score, 1.0)

    async def _analyze_coalition_patterns(self, official: Official,
                                        db_session: Session,
                                        session_years: List[int]) -> Dict:
        """Analyze coalition building patterns in state legislature."""
        cutoff_date = datetime.now() - timedelta(days=365 * len(session_years))

        votes = [v for v in official.votes if v.vote_date >= cutoff_date]

        coalition_analysis = {
            "total_votes": len(votes),
            "party_line_votes": len([v for v in votes if v.party_line_vote]),
            "bipartisan_votes": len([v for v in votes if not v.party_line_vote]),
            "coalition_building_score": 0.0,
            "independence_score": 0.0
        }

        if coalition_analysis["total_votes"] > 0:
            # Coalition building score (higher when participating in bipartisan efforts)
            coalition_analysis["coalition_building_score"] = (
                coalition_analysis["bipartisan_votes"] / coalition_analysis["total_votes"]
            )

            # Independence score (ability to break from party when needed)
            party_breaks = len([v for v in votes if v.party_line_vote and
                              v.vote_position in ["No", "Nay"]])
            coalition_analysis["independence_score"] = (
                party_breaks / max(coalition_analysis["party_line_votes"], 1)
            )

        return coalition_analysis

    async def _analyze_regional_representation(self, official: Official,
                                             db_session: Session) -> Dict:
        """Analyze focus on regional vs. statewide representation."""
        cutoff_date = datetime.now() - timedelta(days=365)

        statements = [s for s in official.statements if s.date_made >= cutoff_date]

        regional_analysis = {
            "total_statements": len(statements),
            "regional_mentions": 0,
            "statewide_mentions": 0,
            "district_specific": 0,
            "regional_focus_score": 0.0
        }

        # Keywords for regional focus
        regional_keywords = [
            "staten island", "richmond county", "borough", "district 23",
            "south shore", "north shore", "west shore", "st. george",
            "tottenville", "great kills", "stapleton"
        ]

        statewide_keywords = [
            "new york state", "statewide", "albany", "capitol", "governor",
            "state budget", "new yorkers"
        ]

        for statement in statements:
            content = statement.content.lower()

            # Count regional mentions
            for keyword in regional_keywords:
                if keyword in content:
                    regional_analysis["regional_mentions"] += 1
                    break  # Count each statement only once

            # Count statewide mentions
            for keyword in statewide_keywords:
                if keyword in content:
                    regional_analysis["statewide_mentions"] += 1
                    break

            # Check for district-specific content
            if statement.geographic_context == "district" or \
               any(keyword in content for keyword in ["my district", "our district"]):
                regional_analysis["district_specific"] += 1

        # Calculate regional focus score
        if regional_analysis["total_statements"] > 0:
            regional_analysis["regional_focus_score"] = (
                (regional_analysis["regional_mentions"] + regional_analysis["district_specific"]) /
                regional_analysis["total_statements"]
            )

        return regional_analysis

    async def track_cross_jurisdictional_issues(self, officials: List[str],
                                              db_session: Session) -> Dict:
        """Track issues that span multiple jurisdiction levels."""
        cross_jurisdictional_analysis = {
            "officials_analyzed": officials,
            "shared_issues": {},
            "coordination_patterns": {},
            "jurisdiction_gaps": {},
            "collaboration_opportunities": {}
        }

        # Analyze each official
        official_issues = {}
        for official_id in officials:
            official = db_session.query(Official).filter_by(id=official_id).first()
            if not official:
                continue

            # Get their recent issue engagement
            analysis = await self.analyze_state_legislative_priorities(
                official_id, db_session
            )

            official_issues[official_id] = {
                "name": official.full_name,
                "jurisdiction": official.jurisdiction_level,
                "issues": analysis
            }

        # Identify shared issues across jurisdictions
        issue_overlap = defaultdict(list)
        for official_id, data in official_issues.items():
            state_priorities = data["issues"].get("state_priorities", {}).get("engagement_by_category", {})
            local_priorities = data["issues"].get("local_priorities", {}).get("engagement_by_category", {})

            all_issues = list(state_priorities.keys()) + list(local_priorities.keys())
            for issue in all_issues:
                issue_overlap[issue].append({
                    "official_id": official_id,
                    "name": data["name"],
                    "jurisdiction": data["jurisdiction"]
                })

        # Identify issues with multi-jurisdictional engagement
        cross_jurisdictional_analysis["shared_issues"] = {
            issue: officials_list for issue, officials_list in issue_overlap.items()
            if len(officials_list) > 1
        }

        return cross_jurisdictional_analysis

    async def generate_state_legislative_report(self, official_id: str,
                                              db_session: Session) -> Dict:
        """Generate comprehensive state legislative report."""
        analysis = await self.analyze_state_legislative_priorities(
            official_id, db_session
        )

        official = db_session.query(Official).filter_by(id=official_id).first()

        report = {
            "executive_summary": self._generate_state_executive_summary(official, analysis),
            "detailed_analysis": analysis,
            "recommendations": self._generate_state_recommendations(analysis),
            "comparison_metrics": self._generate_comparison_metrics(analysis),
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "official_name": official.full_name,
                "jurisdiction": official.jurisdiction_level,
                "analysis_type": "state_legislative_comprehensive"
            }
        }

        return report

    def _generate_state_executive_summary(self, official: Official, analysis: Dict) -> Dict:
        """Generate executive summary for state legislative analysis."""
        state_priorities = analysis.get("state_priorities", {})
        local_priorities = analysis.get("local_priorities", {})
        effectiveness = analysis.get("legislative_effectiveness", {})

        summary = {
            "overall_assessment": "Moderate",  # Default
            "key_strengths": [],
            "areas_for_improvement": [],
            "priority_focus": "Mixed"
        }

        # Assess overall effectiveness
        overall_score = effectiveness.get("scores", {}).get("overall_effectiveness", 0)
        if overall_score > 0.7:
            summary["overall_assessment"] = "Strong"
        elif overall_score > 0.4:
            summary["overall_assessment"] = "Moderate"
        else:
            summary["overall_assessment"] = "Developing"

        # Identify strengths
        if effectiveness.get("bill_sponsorship", 0) > 5:
            summary["key_strengths"].append("Active bill sponsorship")

        if local_priorities.get("local_focus_percentage", 0) > 20:
            summary["key_strengths"].append("Strong local constituency focus")

        coalition_score = analysis.get("coalition_patterns", {}).get("coalition_building_score", 0)
        if coalition_score > 0.3:
            summary["key_strengths"].append("Bipartisan coalition building")

        # Determine priority focus
        state_engagement = state_priorities.get("total_state_engagement", 0)
        local_engagement = local_priorities.get("total_richmond_engagement", 0)

        if local_engagement > state_engagement * 1.5:
            summary["priority_focus"] = "Local"
        elif state_engagement > local_engagement * 1.5:
            summary["priority_focus"] = "Statewide"
        else:
            summary["priority_focus"] = "Balanced"

        return summary

    def _generate_state_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate strategic recommendations based on state analysis."""
        recommendations = []

        effectiveness = analysis.get("legislative_effectiveness", {})
        state_priorities = analysis.get("state_priorities", {})
        local_priorities = analysis.get("local_priorities", {})

        # Effectiveness recommendations
        if effectiveness.get("scores", {}).get("overall_effectiveness", 0) < 0.5:
            recommendations.append({
                "category": "Legislative Effectiveness",
                "priority": "High",
                "recommendation": "Increase bill sponsorship and committee activity",
                "specific_actions": [
                    "Sponsor more legislation in key policy areas",
                    "Increase participation in committee hearings",
                    "Deliver more floor speeches on priority issues"
                ]
            })

        # Local engagement recommendations
        local_focus = local_priorities.get("local_focus_percentage", 0)
        if local_focus < 15:
            recommendations.append({
                "category": "Constituency Services",
                "priority": "High",
                "recommendation": "Strengthen focus on Richmond County/Staten Island issues",
                "specific_actions": [
                    "Increase press releases on local issues",
                    "Hold more town halls and community events",
                    "Address transportation and environmental concerns"
                ]
            })

        # Coalition building recommendations
        coalition_score = analysis.get("coalition_patterns", {}).get("coalition_building_score", 0)
        if coalition_score < 0.3:
            recommendations.append({
                "category": "Coalition Building",
                "priority": "Medium",
                "recommendation": "Expand bipartisan cooperation opportunities",
                "specific_actions": [
                    "Co-sponsor legislation with opposite party members",
                    "Focus on consensus issues like infrastructure",
                    "Participate in bipartisan caucuses"
                ]
            })

        return recommendations

    def _generate_comparison_metrics(self, analysis: Dict) -> Dict:
        """Generate metrics for comparison with other state legislators."""
        return {
            "effectiveness_percentile": "To be calculated with peer comparison",
            "local_focus_ranking": "To be calculated with district comparison",
            "activity_level": analysis.get("legislative_effectiveness", {}).get("scores", {}).get("activity_score", 0),
            "leadership_involvement": analysis.get("legislative_effectiveness", {}).get("scores", {}).get("leadership_score", 0),
            "bipartisan_cooperation": analysis.get("coalition_patterns", {}).get("coalition_building_score", 0)
        }