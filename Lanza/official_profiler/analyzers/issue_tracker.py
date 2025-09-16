"""
Issue tracking and position evolution analysis system.
"""
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import structlog
from sqlalchemy.orm import Session
from models.official import Official, Issue, Statement, Vote, PositionEvolution, GeographicLevel

logger = structlog.get_logger()


class IssueTracker:
    """Comprehensive issue tracking and position analysis."""

    def __init__(self):
        self.issue_categories = {
            "Healthcare": [
                "medicare", "medicaid", "health insurance", "prescription drugs",
                "mental health", "healthcare costs", "hospital", "medical"
            ],
            "Economy": [
                "jobs", "employment", "wages", "inflation", "recession",
                "economic growth", "unemployment", "workforce"
            ],
            "Education": [
                "schools", "teachers", "student loans", "college", "university",
                "k-12", "education funding", "school choice"
            ],
            "Environment": [
                "climate change", "clean energy", "renewable", "pollution",
                "carbon emissions", "environmental protection", "green jobs"
            ],
            "Defense": [
                "military", "defense spending", "veterans", "national security",
                "armed forces", "pentagon", "military budget"
            ],
            "Immigration": [
                "border security", "immigration reform", "refugees",
                "asylum", "deportation", "citizenship", "visa"
            ],
            "Infrastructure": [
                "roads", "bridges", "broadband", "water systems", "transportation",
                "infrastructure investment", "public works"
            ],
            "Social Issues": [
                "abortion", "gun rights", "civil rights", "lgbtq",
                "voting rights", "criminal justice", "police reform"
            ],
            "Foreign Policy": [
                "nato", "china", "russia", "middle east", "trade deals",
                "international relations", "diplomacy", "sanctions"
            ],
            "Technology": [
                "artificial intelligence", "social media", "privacy",
                "cybersecurity", "big tech", "data protection"
            ]
        }

        self.geographic_hierarchy = {
            GeographicLevel.NATIONAL: ["federal", "national", "congress", "senate", "house"],
            GeographicLevel.REGIONAL: ["region", "multi-state", "regional"],
            GeographicLevel.STATE: ["state", "statewide", "commonwealth"],
            GeographicLevel.COUNTY: ["county", "parish", "borough"],
            GeographicLevel.CITY: ["city", "municipal", "town", "village"],
            GeographicLevel.DISTRICT: ["district", "congressional", "legislative"]
        }

    async def track_position_evolution(self, official_id: str,
                                     issue_id: str, db_session: Session,
                                     timeframe_days: int = 1095) -> Dict:
        """Track how an official's position on an issue has evolved over time."""
        cutoff_date = datetime.now() - timedelta(days=timeframe_days)

        # Get all statements and votes related to this issue
        statements = db_session.query(Statement).filter(
            Statement.official_id == official_id,
            Statement.issue_id == issue_id,
            Statement.date_made >= cutoff_date
        ).order_by(Statement.date_made.asc()).all()

        votes = db_session.query(Vote).filter(
            Vote.official_id == official_id,
            Vote.vote_date >= cutoff_date
        ).all()

        # Filter votes by issue relevance
        issue = db_session.query(Issue).filter_by(id=issue_id).first()
        relevant_votes = self._filter_votes_by_issue(votes, issue)

        evolution_data = {
            "official_id": official_id,
            "issue_id": issue_id,
            "issue_name": issue.name if issue else "Unknown",
            "analysis_period": f"{timeframe_days} days",
            "timeline": [],
            "position_changes": [],
            "consistency_score": 0.0,
            "trend_analysis": {},
            "key_moments": []
        }

        # Create timeline of positions
        timeline_events = []

        # Add statements to timeline
        for statement in statements:
            if statement.position_stance:
                timeline_events.append({
                    "date": statement.date_made,
                    "type": "statement",
                    "stance": statement.position_stance,
                    "content": statement.summary or statement.content[:200],
                    "source": statement.statement_type.value,
                    "confidence": statement.confidence_score or 0.5
                })

        # Add votes to timeline
        for vote in relevant_votes:
            stance = self._vote_to_stance(vote, issue)
            if stance:
                timeline_events.append({
                    "date": vote.vote_date,
                    "type": "vote",
                    "stance": stance,
                    "content": vote.bill_title,
                    "source": f"{vote.chamber} vote",
                    "confidence": 0.8  # Votes are generally clear indicators
                })

        # Sort timeline by date
        timeline_events.sort(key=lambda x: x["date"])
        evolution_data["timeline"] = timeline_events

        # Analyze position changes
        if len(timeline_events) >= 2:
            changes = self._identify_position_changes(timeline_events)
            evolution_data["position_changes"] = changes

            # Calculate consistency score
            evolution_data["consistency_score"] = self._calculate_consistency_score(timeline_events)

            # Trend analysis
            evolution_data["trend_analysis"] = self._analyze_position_trends(timeline_events)

            # Identify key moments
            evolution_data["key_moments"] = self._identify_key_moments(timeline_events, changes)

        return evolution_data

    async def analyze_geographic_issue_relevance(self, official: Official,
                                               db_session: Session) -> Dict:
        """Analyze issues by geographic relevance levels."""
        analysis = {
            "official_id": official.id,
            "official_name": official.full_name,
            "geographic_context": {
                "state": official.state,
                "district": official.district,
                "county": official.county,
                "city": official.city
            },
            "issue_breakdown": {},
            "geographic_focus": {},
            "recommendations": []
        }

        # Get all statements from the official
        statements = db_session.query(Statement).filter(
            Statement.official_id == official.id,
            Statement.date_made >= datetime.now() - timedelta(days=365)
        ).all()

        # Categorize issues by geographic level
        issue_geographic_breakdown = defaultdict(lambda: defaultdict(int))

        for statement in statements:
            if statement.issue:
                issue_name = statement.issue.name
                geographic_level = self._determine_geographic_level(statement, official)

                issue_geographic_breakdown[issue_name][geographic_level.value] += 1

        # Analyze focus patterns
        geographic_totals = defaultdict(int)
        for issue, levels in issue_geographic_breakdown.items():
            for level, count in levels.items():
                geographic_totals[level] += count

        total_statements = sum(geographic_totals.values())
        if total_statements > 0:
            for level, count in geographic_totals.items():
                analysis["geographic_focus"][level] = {
                    "count": count,
                    "percentage": (count / total_statements) * 100
                }

        analysis["issue_breakdown"] = dict(issue_geographic_breakdown)

        # Generate recommendations
        analysis["recommendations"] = self._generate_geographic_recommendations(
            analysis["geographic_focus"], official
        )

        return analysis

    async def identify_emerging_issues(self, official_id: str,
                                     db_session: Session,
                                     lookback_days: int = 90) -> List[Dict]:
        """Identify emerging issues the official is engaging with."""
        recent_cutoff = datetime.now() - timedelta(days=lookback_days)
        older_cutoff = datetime.now() - timedelta(days=lookback_days * 2)

        # Get recent vs older statements
        recent_statements = db_session.query(Statement).filter(
            Statement.official_id == official_id,
            Statement.date_made >= recent_cutoff
        ).all()

        older_statements = db_session.query(Statement).filter(
            Statement.official_id == official_id,
            Statement.date_made >= older_cutoff,
            Statement.date_made < recent_cutoff
        ).all()

        # Extract topics/issues from statements
        recent_topics = self._extract_topics_from_statements(recent_statements)
        older_topics = self._extract_topics_from_statements(older_statements)

        # Identify emerging patterns
        emerging_issues = []

        for topic, recent_count in recent_topics.items():
            older_count = older_topics.get(topic, 0)

            # Calculate emergence score
            if older_count == 0 and recent_count >= 2:
                # Completely new topic
                emergence_score = 1.0
                change_type = "new"
            elif older_count > 0:
                # Increased attention
                growth_rate = (recent_count - older_count) / older_count
                if growth_rate > 0.5:  # 50% increase
                    emergence_score = min(growth_rate, 2.0) / 2.0
                    change_type = "increasing"
                else:
                    continue
            else:
                continue

            emerging_issues.append({
                "topic": topic,
                "recent_mentions": recent_count,
                "previous_mentions": older_count,
                "emergence_score": emergence_score,
                "change_type": change_type,
                "growth_rate": (recent_count - older_count) / max(older_count, 1)
            })

        # Sort by emergence score
        emerging_issues.sort(key=lambda x: x["emergence_score"], reverse=True)

        return emerging_issues[:10]  # Top 10 emerging issues

    async def analyze_issue_consistency(self, official_id: str,
                                      db_session: Session) -> Dict:
        """Analyze consistency of positions across all issues."""
        # Get all position evolutions
        evolutions = db_session.query(PositionEvolution).filter(
            PositionEvolution.official_id == official_id
        ).all()

        consistency_analysis = {
            "official_id": official_id,
            "overall_consistency_score": 0.0,
            "issue_consistency": {},
            "flip_flops": [],
            "stable_positions": [],
            "inconsistent_areas": []
        }

        issue_consistency_scores = {}
        all_changes = []

        # Group by issue
        issue_groups = defaultdict(list)
        for evolution in evolutions:
            issue_groups[evolution.issue_id].append(evolution)

        for issue_id, issue_evolutions in issue_groups.items():
            issue_evolutions.sort(key=lambda x: x.position_date)

            # Calculate consistency for this issue
            issue_score, changes = self._calculate_issue_consistency(issue_evolutions)
            issue_consistency_scores[issue_id] = issue_score
            all_changes.extend(changes)

            # Get issue name
            issue = db_session.query(Issue).filter_by(id=issue_id).first()
            issue_name = issue.name if issue else f"Issue {issue_id}"

            consistency_analysis["issue_consistency"][issue_name] = {
                "consistency_score": issue_score,
                "position_changes": len(changes),
                "major_changes": len([c for c in changes if c.get("significance") == "Major"])
            }

            # Categorize issues
            if issue_score > 0.8:
                consistency_analysis["stable_positions"].append({
                    "issue": issue_name,
                    "score": issue_score
                })
            elif issue_score < 0.4:
                consistency_analysis["inconsistent_areas"].append({
                    "issue": issue_name,
                    "score": issue_score
                })

            # Identify flip-flops (multiple major changes)
            major_changes = [c for c in changes if c.get("significance") == "Major"]
            if len(major_changes) >= 2:
                consistency_analysis["flip_flops"].append({
                    "issue": issue_name,
                    "changes": len(major_changes),
                    "timeline": [c["date"] for c in major_changes]
                })

        # Calculate overall consistency
        if issue_consistency_scores:
            consistency_analysis["overall_consistency_score"] = \
                sum(issue_consistency_scores.values()) / len(issue_consistency_scores)

        return consistency_analysis

    def _filter_votes_by_issue(self, votes: List[Vote], issue: Issue) -> List[Vote]:
        """Filter votes that are relevant to a specific issue."""
        if not issue:
            return []

        relevant_votes = []
        issue_keywords = self.issue_categories.get(issue.category, [])
        issue_keywords.extend([issue.name.lower()])

        for vote in votes:
            bill_text = (vote.bill_title + " " + (vote.bill_summary or "")).lower()

            # Check if any issue keywords appear in the bill
            if any(keyword in bill_text for keyword in issue_keywords):
                relevant_votes.append(vote)

        return relevant_votes

    def _vote_to_stance(self, vote: Vote, issue: Issue) -> Optional[str]:
        """Convert vote position to issue stance."""
        if not issue:
            return None

        # This is simplified - in reality would need complex mapping
        # of bill content to position stance
        if vote.vote_position in ["Yes", "Aye"]:
            return "Support"
        elif vote.vote_position in ["No", "Nay"]:
            return "Oppose"
        else:
            return "Neutral"

    def _identify_position_changes(self, timeline_events: List[Dict]) -> List[Dict]:
        """Identify significant position changes in timeline."""
        changes = []

        for i in range(1, len(timeline_events)):
            current_event = timeline_events[i]
            previous_event = timeline_events[i - 1]

            if current_event["stance"] != previous_event["stance"]:
                # Determine significance of change
                significance = "Minor"
                if (previous_event["stance"] == "Support" and current_event["stance"] == "Oppose") or \
                   (previous_event["stance"] == "Oppose" and current_event["stance"] == "Support"):
                    significance = "Major"

                changes.append({
                    "date": current_event["date"],
                    "from_stance": previous_event["stance"],
                    "to_stance": current_event["stance"],
                    "significance": significance,
                    "context": current_event["content"],
                    "days_since_last": (current_event["date"] - previous_event["date"]).days
                })

        return changes

    def _calculate_consistency_score(self, timeline_events: List[Dict]) -> float:
        """Calculate consistency score from timeline events."""
        if len(timeline_events) < 2:
            return 1.0  # No changes = perfect consistency

        stance_counts = Counter(event["stance"] for event in timeline_events)
        most_common_stance_count = stance_counts.most_common(1)[0][1]

        # Consistency is the proportion of the most frequent stance
        return most_common_stance_count / len(timeline_events)

    def _analyze_position_trends(self, timeline_events: List[Dict]) -> Dict:
        """Analyze trends in position evolution."""
        if len(timeline_events) < 3:
            return {"trend": "insufficient_data"}

        # Look at overall trajectory
        first_stance = timeline_events[0]["stance"]
        last_stance = timeline_events[-1]["stance"]

        # Count stance transitions
        stance_sequence = [event["stance"] for event in timeline_events]

        trends = {
            "initial_position": first_stance,
            "current_position": last_stance,
            "trajectory": self._determine_trajectory(first_stance, last_stance),
            "volatility": self._calculate_volatility(stance_sequence),
            "recent_trend": self._analyze_recent_trend(stance_sequence[-5:])  # Last 5 positions
        }

        return trends

    def _identify_key_moments(self, timeline_events: List[Dict],
                            changes: List[Dict]) -> List[Dict]:
        """Identify key moments in position evolution."""
        key_moments = []

        # Major position changes are always key moments
        for change in changes:
            if change["significance"] == "Major":
                key_moments.append({
                    "date": change["date"],
                    "type": "major_position_change",
                    "description": f"Changed from {change['from_stance']} to {change['to_stance']}",
                    "context": change["context"]
                })

        # High-profile statements (could be determined by source or content)
        for event in timeline_events:
            if event["type"] == "statement" and event["source"] in ["press_release", "interview"]:
                if event["confidence"] > 0.8:
                    key_moments.append({
                        "date": event["date"],
                        "type": "high_profile_statement",
                        "description": f"Strong {event['stance']} statement",
                        "context": event["content"]
                    })

        # Sort by date
        key_moments.sort(key=lambda x: x["date"])

        return key_moments

    def _determine_geographic_level(self, statement: Statement,
                                  official: Official) -> GeographicLevel:
        """Determine the geographic level of relevance for a statement."""
        if statement.geographic_context:
            context = statement.geographic_context.lower()

            if context in ["national", "federal", "country"]:
                return GeographicLevel.NATIONAL
            elif context in ["regional", "multi-state"]:
                return GeographicLevel.REGIONAL
            elif context in ["state", "statewide"]:
                return GeographicLevel.STATE
            elif context in ["county", "parish"]:
                return GeographicLevel.COUNTY
            elif context in ["city", "local", "municipal"]:
                return GeographicLevel.CITY
            elif context in ["district", "congressional"]:
                return GeographicLevel.DISTRICT

        # Default to national for congressional statements
        if official.positions and any(p.position_type.value in ["senator", "representative"]
                                    for p in official.positions if p.is_current):
            return GeographicLevel.NATIONAL

        return GeographicLevel.STATE

    def _extract_topics_from_statements(self, statements: List[Statement]) -> Dict[str, int]:
        """Extract topics/issues from statements."""
        topic_counts = Counter()

        for statement in statements:
            # Use existing issue classification
            if statement.issue:
                topic_counts[statement.issue.name] += 1

            # Also extract from key phrases
            if statement.key_phrases:
                for phrase_data in statement.key_phrases:
                    if isinstance(phrase_data, dict):
                        phrase = phrase_data.get("phrase", "")
                        if len(phrase.split()) <= 3:  # Short phrases only
                            topic_counts[phrase] += 1

        return dict(topic_counts)

    def _calculate_issue_consistency(self, evolutions: List[PositionEvolution]) -> Tuple[float, List[Dict]]:
        """Calculate consistency score for a single issue."""
        if len(evolutions) < 2:
            return 1.0, []

        changes = []
        stances = []

        for evolution in evolutions:
            stances.append(evolution.stance)

            if evolution.is_change:
                changes.append({
                    "date": evolution.position_date,
                    "from_stance": evolution.previous_stance,
                    "to_stance": evolution.stance,
                    "significance": evolution.change_significance or "Minor"
                })

        # Consistency is inverse of volatility
        stance_counter = Counter(stances)
        most_common_count = stance_counter.most_common(1)[0][1]
        consistency = most_common_count / len(stances)

        return consistency, changes

    def _determine_trajectory(self, first_stance: str, last_stance: str) -> str:
        """Determine overall trajectory of position changes."""
        if first_stance == last_stance:
            return "stable"
        elif (first_stance == "Support" and last_stance == "Oppose") or \
             (first_stance == "Oppose" and last_stance == "Support"):
            return "reversal"
        elif first_stance == "Neutral":
            return "clarification"
        elif last_stance == "Neutral":
            return "moderation"
        else:
            return "evolution"

    def _calculate_volatility(self, stance_sequence: List[str]) -> float:
        """Calculate volatility of position changes."""
        if len(stance_sequence) < 2:
            return 0.0

        changes = sum(1 for i in range(1, len(stance_sequence))
                     if stance_sequence[i] != stance_sequence[i-1])

        return changes / (len(stance_sequence) - 1)

    def _analyze_recent_trend(self, recent_stances: List[str]) -> str:
        """Analyze recent trend in positions."""
        if len(recent_stances) < 2:
            return "insufficient_data"

        if len(set(recent_stances)) == 1:
            return "stable"

        # Look at direction of change
        if len(recent_stances) >= 3:
            if recent_stances[-3:] == sorted(recent_stances[-3:]):
                return "strengthening"
            elif recent_stances[-3:] == sorted(recent_stances[-3:], reverse=True):
                return "weakening"

        return "mixed"

    def _generate_geographic_recommendations(self, geographic_focus: Dict,
                                           official: Official) -> List[Dict]:
        """Generate recommendations based on geographic analysis."""
        recommendations = []

        total_statements = sum(focus["count"] for focus in geographic_focus.values())
        if total_statements == 0:
            return recommendations

        # Check for imbalances
        national_pct = geographic_focus.get("national", {}).get("percentage", 0)
        local_pct = (geographic_focus.get("state", {}).get("percentage", 0) +
                    geographic_focus.get("district", {}).get("percentage", 0) +
                    geographic_focus.get("county", {}).get("percentage", 0) +
                    geographic_focus.get("city", {}).get("percentage", 0))

        if national_pct > 80:
            recommendations.append({
                "priority": "Medium",
                "category": "Local Engagement",
                "recommendation": "Increase focus on state and district issues",
                "rationale": f"{national_pct:.1f}% focus on national issues may disconnect from local constituents"
            })

        if local_pct < 20:
            recommendations.append({
                "priority": "High",
                "category": "Constituent Services",
                "recommendation": "Emphasize local and district-specific initiatives",
                "rationale": f"Only {local_pct:.1f}% focus on local issues"
            })

        # Richmond-specific recommendations
        if official.county == "Richmond City" or official.city == "Richmond":
            richmond_focus = geographic_focus.get("city", {}).get("percentage", 0)
            if richmond_focus < 15:
                recommendations.append({
                    "priority": "High",
                    "category": "Richmond Engagement",
                    "recommendation": "Increase visibility on Richmond city issues",
                    "rationale": f"Only {richmond_focus:.1f}% focus on city-level issues"
                })

        return recommendations