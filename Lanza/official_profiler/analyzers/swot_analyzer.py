"""
SWOT Analysis module for comprehensive political assessment of elected officials.
"""
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict, Counter
import structlog
from sqlalchemy.orm import Session
from models.official import Official, Vote, Statement, FinancialDisclosure, Position

logger = structlog.get_logger()


class SWOTAnalyzer:
    """Comprehensive SWOT analysis for elected officials."""

    def __init__(self):
        self.analysis_weights = {
            "legislative_effectiveness": 0.25,
            "constituency_support": 0.20,
            "fundraising_ability": 0.15,
            "media_coverage": 0.15,
            "party_alignment": 0.10,
            "coalition_building": 0.15
        }

    async def generate_comprehensive_swot(self, official_id: str,
                                        db_session: Session) -> Dict:
        """Generate complete SWOT analysis for an official."""
        official = db_session.query(Official).filter_by(id=official_id).first()
        if not official:
            return {"error": "Official not found"}

        swot_analysis = {
            "official_id": official_id,
            "official_name": official.full_name,
            "analysis_date": datetime.now().isoformat(),
            "analysis_context": self._determine_analysis_context(official),
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": [],
            "overall_assessment": {},
            "detailed_metrics": {}
        }

        # Gather comprehensive data
        data_package = await self._gather_analysis_data(official, db_session)

        # Analyze each SWOT component
        swot_analysis["strengths"] = await self._analyze_strengths(official, data_package)
        swot_analysis["weaknesses"] = await self._analyze_weaknesses(official, data_package)
        swot_analysis["opportunities"] = await self._analyze_opportunities(official, data_package)
        swot_analysis["threats"] = await self._analyze_threats(official, data_package)

        # Generate overall assessment
        swot_analysis["overall_assessment"] = self._calculate_overall_assessment(swot_analysis)
        swot_analysis["detailed_metrics"] = self._calculate_detailed_metrics(data_package)

        # Strategic recommendations
        swot_analysis["strategic_recommendations"] = self._generate_strategic_recommendations(swot_analysis)

        return swot_analysis

    async def _gather_analysis_data(self, official: Official,
                                  db_session: Session) -> Dict:
        """Gather comprehensive data for SWOT analysis."""
        cutoff_date = datetime.now() - timedelta(days=730)  # 2 years of data

        data = {
            "official": official,
            "recent_votes": [],
            "recent_statements": [],
            "financial_data": [],
            "positions": [],
            "legislative_metrics": {},
            "constituency_metrics": {},
            "media_metrics": {},
            "party_metrics": {}
        }

        # Recent votes
        data["recent_votes"] = db_session.query(Vote).filter(
            Vote.official_id == official.id,
            Vote.vote_date >= cutoff_date
        ).all()

        # Recent statements
        data["recent_statements"] = db_session.query(Statement).filter(
            Statement.official_id == official.id,
            Statement.date_made >= cutoff_date
        ).all()

        # Financial disclosures
        data["financial_data"] = db_session.query(FinancialDisclosure).filter(
            FinancialDisclosure.official_id == official.id
        ).order_by(FinancialDisclosure.report_year.desc()).limit(3).all()

        # Positions
        data["positions"] = db_session.query(Position).filter(
            Position.official_id == official.id
        ).all()

        # Calculate derived metrics
        data["legislative_metrics"] = self._calculate_legislative_metrics(data["recent_votes"])
        data["constituency_metrics"] = self._calculate_constituency_metrics(data["recent_statements"])
        data["media_metrics"] = self._calculate_media_metrics(data["recent_statements"])
        data["party_metrics"] = self._calculate_party_metrics(data["recent_votes"], official.party)

        return data

    async def _analyze_strengths(self, official: Official, data: Dict) -> List[Dict]:
        """Analyze strengths of the official."""
        strengths = []

        # Legislative Effectiveness
        legislative_score = data["legislative_metrics"].get("effectiveness_score", 0)
        if legislative_score > 0.7:
            strengths.append({
                "category": "Legislative Effectiveness",
                "description": "Strong track record of passing legislation and securing key votes",
                "evidence": f"Legislative effectiveness score: {legislative_score:.2f}",
                "impact": "High",
                "quantification": legislative_score
            })

        # Bill Sponsorship Success
        bills_passed = data["legislative_metrics"].get("bills_passed", 0)
        if bills_passed > 5:
            strengths.append({
                "category": "Legislative Productivity",
                "description": "High success rate in bill sponsorship and passage",
                "evidence": f"Successfully passed {bills_passed} bills in recent period",
                "impact": "High",
                "quantification": bills_passed
            })

        # Committee Leadership
        current_position = next((p for p in data["positions"] if p.is_current), None)
        if current_position and current_position.leadership_roles:
            leadership_roles = current_position.leadership_roles
            if leadership_roles:
                strengths.append({
                    "category": "Leadership Position",
                    "description": "Holds influential committee leadership positions",
                    "evidence": f"Leadership roles: {', '.join(leadership_roles)}",
                    "impact": "High",
                    "quantification": len(leadership_roles)
                })

        # Fundraising Ability
        financial_strength = self._assess_financial_strength(data["financial_data"])
        if financial_strength > 0.7:
            strengths.append({
                "category": "Fundraising Capability",
                "description": "Strong fundraising track record and financial resources",
                "evidence": f"Financial strength score: {financial_strength:.2f}",
                "impact": "Medium",
                "quantification": financial_strength
            })

        # Constituency Engagement
        engagement_score = data["constituency_metrics"].get("engagement_score", 0)
        if engagement_score > 0.6:
            strengths.append({
                "category": "Constituency Relations",
                "description": "Active engagement with constituents through various channels",
                "evidence": f"Constituency engagement score: {engagement_score:.2f}",
                "impact": "Medium",
                "quantification": engagement_score
            })

        # Party Alignment (when beneficial)
        party_alignment = data["party_metrics"].get("alignment_score", 0.5)
        if 0.8 <= party_alignment <= 0.95:  # Strong but not blind party loyalty
            strengths.append({
                "category": "Party Unity",
                "description": "Strong alignment with party positions while maintaining independence",
                "evidence": f"Party alignment score: {party_alignment:.2f}",
                "impact": "Medium",
                "quantification": party_alignment
            })

        # Coalition Building
        coalition_score = self._calculate_coalition_building_score(data["recent_votes"])
        if coalition_score > 0.6:
            strengths.append({
                "category": "Coalition Building",
                "description": "Effective at building bipartisan coalitions",
                "evidence": f"Coalition building score: {coalition_score:.2f}",
                "impact": "High",
                "quantification": coalition_score
            })

        # Media Presence
        media_effectiveness = data["media_metrics"].get("effectiveness_score", 0)
        if media_effectiveness > 0.6:
            strengths.append({
                "category": "Media Relations",
                "description": "Effective media communication and public messaging",
                "evidence": f"Media effectiveness score: {media_effectiveness:.2f}",
                "impact": "Medium",
                "quantification": media_effectiveness
            })

        # Seniority and Experience
        years_in_office = self._calculate_years_in_office(data["positions"])
        if years_in_office > 10:
            strengths.append({
                "category": "Experience and Seniority",
                "description": "Extensive legislative experience and institutional knowledge",
                "evidence": f"Years in office: {years_in_office}",
                "impact": "Medium",
                "quantification": years_in_office
            })

        return sorted(strengths, key=lambda x: x["quantification"], reverse=True)

    async def _analyze_weaknesses(self, official: Official, data: Dict) -> List[Dict]:
        """Analyze weaknesses of the official."""
        weaknesses = []

        # Poor Legislative Effectiveness
        legislative_score = data["legislative_metrics"].get("effectiveness_score", 0)
        if legislative_score < 0.3:
            weaknesses.append({
                "category": "Legislative Effectiveness",
                "description": "Low success rate in passing legislation",
                "evidence": f"Legislative effectiveness score: {legislative_score:.2f}",
                "severity": "High",
                "quantification": 1 - legislative_score
            })

        # Controversial Votes
        controversial_votes = data["legislative_metrics"].get("controversial_votes", [])
        if len(controversial_votes) > 3:
            weaknesses.append({
                "category": "Controversial Positions",
                "description": "Multiple controversial votes that could alienate voters",
                "evidence": f"{len(controversial_votes)} controversial votes identified",
                "severity": "Medium",
                "quantification": len(controversial_votes)
            })

        # Poor Fundraising
        financial_strength = self._assess_financial_strength(data["financial_data"])
        if financial_strength < 0.3:
            weaknesses.append({
                "category": "Fundraising Challenges",
                "description": "Weak fundraising performance compared to peers",
                "evidence": f"Financial strength score: {financial_strength:.2f}",
                "severity": "High",
                "quantification": 1 - financial_strength
            })

        # Low Constituency Engagement
        engagement_score = data["constituency_metrics"].get("engagement_score", 0)
        if engagement_score < 0.3:
            weaknesses.append({
                "category": "Constituency Disconnect",
                "description": "Limited engagement with constituents",
                "evidence": f"Engagement score: {engagement_score:.2f}",
                "severity": "High",
                "quantification": 1 - engagement_score
            })

        # Extreme Party Alignment
        party_alignment = data["party_metrics"].get("alignment_score", 0.5)
        if party_alignment > 0.95:
            weaknesses.append({
                "category": "Rigid Party Line",
                "description": "Excessive party loyalty may appear as lack of independence",
                "evidence": f"Party alignment score: {party_alignment:.2f}",
                "severity": "Medium",
                "quantification": party_alignment - 0.8
            })

        # Poor Coalition Building
        coalition_score = self._calculate_coalition_building_score(data["recent_votes"])
        if coalition_score < 0.3:
            weaknesses.append({
                "category": "Limited Bipartisanship",
                "description": "Difficulty building coalitions across party lines",
                "evidence": f"Coalition building score: {coalition_score:.2f}",
                "severity": "Medium",
                "quantification": 1 - coalition_score
            })

        # Negative Media Coverage
        media_sentiment = data["media_metrics"].get("avg_sentiment", 0)
        if media_sentiment < -0.3:
            weaknesses.append({
                "category": "Negative Media Coverage",
                "description": "Consistently negative media portrayal",
                "evidence": f"Average media sentiment: {media_sentiment:.2f}",
                "severity": "Medium",
                "quantification": abs(media_sentiment)
            })

        # Age/Health Concerns
        if official.date_of_birth:
            age = (datetime.now() - official.date_of_birth).days / 365.25
            if age > 75:
                weaknesses.append({
                    "category": "Age Concerns",
                    "description": "Advanced age may raise electability questions",
                    "evidence": f"Age: {age:.0f} years",
                    "severity": "Medium",
                    "quantification": (age - 65) / 10
                })

        # Limited Committee Influence
        current_position = next((p for p in data["positions"] if p.is_current), None)
        if current_position and not current_position.leadership_roles:
            if not current_position.committees or len(current_position.committees) < 2:
                weaknesses.append({
                    "category": "Limited Committee Presence",
                    "description": "Minimal committee assignments or leadership roles",
                    "evidence": f"Committee assignments: {len(current_position.committees or [])}",
                    "severity": "Low",
                    "quantification": 2 - len(current_position.committees or [])
                })

        return sorted(weaknesses, key=lambda x: x["quantification"], reverse=True)

    async def _analyze_opportunities(self, official: Official, data: Dict) -> List[Dict]:
        """Analyze opportunities for the official."""
        opportunities = []

        # Emerging Issues Alignment
        trending_topics = self._identify_trending_issues(data["recent_statements"])
        if trending_topics:
            opportunities.append({
                "category": "Issue Leadership",
                "description": "Position as leader on emerging policy issues",
                "details": f"Active on trending topics: {', '.join(trending_topics[:3])}",
                "potential": "High",
                "timeframe": "6-12 months"
            })

        # Committee Leadership Opportunities
        current_position = next((p for p in data["positions"] if p.is_current), None)
        if current_position and not current_position.leadership_roles:
            opportunities.append({
                "category": "Committee Leadership",
                "description": "Potential for committee chair or ranking member positions",
                "details": "Senior member eligible for leadership roles",
                "potential": "Medium",
                "timeframe": "1-2 years"
            })

        # Coalition Building Opportunities
        coalition_score = self._calculate_coalition_building_score(data["recent_votes"])
        if 0.4 < coalition_score < 0.7:
            opportunities.append({
                "category": "Bipartisan Leadership",
                "description": "Build reputation as bipartisan dealmaker",
                "details": "Moderate coalition building score suggests potential",
                "potential": "High",
                "timeframe": "Immediate"
            })

        # Media Profile Enhancement
        media_coverage = data["media_metrics"].get("coverage_volume", 0)
        if media_coverage < 50:  # Low media presence
            opportunities.append({
                "category": "Media Profile",
                "description": "Increase visibility through strategic media engagement",
                "details": "Currently low media profile allows for growth",
                "potential": "Medium",
                "timeframe": "3-6 months"
            })

        # Fundraising Growth
        financial_strength = self._assess_financial_strength(data["financial_data"])
        if 0.3 < financial_strength < 0.7:
            opportunities.append({
                "category": "Fundraising Expansion",
                "description": "Expand donor base and fundraising capabilities",
                "details": "Moderate financial position with growth potential",
                "potential": "Medium",
                "timeframe": "6-12 months"
            })

        # District Demographics
        district_opportunities = self._analyze_district_demographics(official)
        if district_opportunities:
            opportunities.extend(district_opportunities)

        # Electoral Cycle Timing
        electoral_opportunities = self._analyze_electoral_timing(official)
        if electoral_opportunities:
            opportunities.extend(electoral_opportunities)

        return opportunities

    async def _analyze_threats(self, official: Official, data: Dict) -> List[Dict]:
        """Analyze threats facing the official."""
        threats = []

        # Primary Challenge Risk
        primary_risk = self._assess_primary_challenge_risk(official, data)
        if primary_risk > 0.6:
            threats.append({
                "category": "Primary Challenge",
                "description": "High risk of facing serious primary challenger",
                "likelihood": "High" if primary_risk > 0.8 else "Medium",
                "impact": "High",
                "timeframe": "Next election cycle",
                "risk_score": primary_risk
            })

        # General Election Vulnerability
        general_risk = self._assess_general_election_risk(official, data)
        if general_risk > 0.5:
            threats.append({
                "category": "General Election Risk",
                "description": "Vulnerable in general election",
                "likelihood": "High" if general_risk > 0.7 else "Medium",
                "impact": "High",
                "timeframe": "Next election cycle",
                "risk_score": general_risk
            })

        # Scandal Risk
        scandal_indicators = self._assess_scandal_risk(data)
        if scandal_indicators > 0.4:
            threats.append({
                "category": "Scandal Vulnerability",
                "description": "Potential exposure to ethical or personal scandals",
                "likelihood": "Medium",
                "impact": "High",
                "timeframe": "Ongoing",
                "risk_score": scandal_indicators
            })

        # Party Disfavor
        party_alignment = data["party_metrics"].get("alignment_score", 0.5)
        if party_alignment < 0.3 or party_alignment > 0.95:
            threat_type = "Party Isolation" if party_alignment < 0.3 else "Base Backlash"
            threats.append({
                "category": threat_type,
                "description": "Risk of losing party or base support",
                "likelihood": "Medium",
                "impact": "Medium",
                "timeframe": "6-12 months",
                "risk_score": abs(0.6 - party_alignment)
            })

        # Demographic Changes
        demographic_threats = self._analyze_demographic_shifts(official)
        if demographic_threats:
            threats.extend(demographic_threats)

        # National Political Environment
        national_threats = self._analyze_national_environment(official)
        if national_threats:
            threats.extend(national_threats)

        # Health/Age Concerns
        if official.date_of_birth:
            age = (datetime.now() - official.date_of_birth).days / 365.25
            if age > 70:
                threats.append({
                    "category": "Age/Health Questions",
                    "description": "Voter concerns about age and fitness for office",
                    "likelihood": "Medium",
                    "impact": "Medium",
                    "timeframe": "Ongoing",
                    "risk_score": (age - 65) / 20
                })

        return sorted(threats, key=lambda x: x["risk_score"], reverse=True)

    def _calculate_legislative_metrics(self, votes: List[Vote]) -> Dict:
        """Calculate legislative effectiveness metrics."""
        if not votes:
            return {"effectiveness_score": 0, "bills_passed": 0, "controversial_votes": []}

        total_votes = len(votes)
        key_votes = [v for v in votes if v.vote_significance == "Key"]
        important_votes = [v for v in votes if v.vote_significance == "Important"]

        # Calculate effectiveness based on key vote success
        effectiveness_score = 0.0
        if key_votes:
            successful_key_votes = len([v for v in key_votes if v.vote_position in ["Yes", "Aye"]])
            effectiveness_score = successful_key_votes / len(key_votes)

        # Count bills passed (simplified - would need more data)
        bills_passed = len([v for v in votes if v.vote_type == "Final Passage" and v.vote_position in ["Yes", "Aye"]])

        # Identify controversial votes (party line votes where official voted against party)
        controversial_votes = []
        for vote in votes:
            if vote.party_line_vote and vote.vote_position in ["No", "Nay"]:
                controversial_votes.append(vote)

        return {
            "effectiveness_score": effectiveness_score,
            "total_votes": total_votes,
            "key_votes": len(key_votes),
            "important_votes": len(important_votes),
            "bills_passed": bills_passed,
            "controversial_votes": controversial_votes
        }

    def _calculate_constituency_metrics(self, statements: List[Statement]) -> Dict:
        """Calculate constituency engagement metrics."""
        if not statements:
            return {"engagement_score": 0}

        local_statements = [s for s in statements if s.geographic_context in ["local", "district", "state"]]
        press_releases = [s for s in statements if s.statement_type.value == "press_release"]
        town_halls = [s for s in statements if "town hall" in s.venue.lower() if s.venue]

        engagement_score = 0.0
        if statements:
            local_ratio = len(local_statements) / len(statements)
            press_ratio = len(press_releases) / len(statements)
            engagement_score = (local_ratio * 0.6) + (press_ratio * 0.4)

        return {
            "engagement_score": min(engagement_score, 1.0),
            "total_statements": len(statements),
            "local_statements": len(local_statements),
            "press_releases": len(press_releases),
            "town_halls": len(town_halls)
        }

    def _calculate_media_metrics(self, statements: List[Statement]) -> Dict:
        """Calculate media effectiveness metrics."""
        if not statements:
            return {"effectiveness_score": 0, "coverage_volume": 0, "avg_sentiment": 0}

        media_statements = [s for s in statements if s.statement_type.value in ["press_release", "interview"]]

        # Calculate average sentiment
        sentiments = [s.sentiment_score for s in statements if s.sentiment_score is not None]
        avg_sentiment = np.mean(sentiments) if sentiments else 0

        # Media effectiveness based on volume and sentiment
        coverage_volume = len(media_statements)
        effectiveness_score = min((coverage_volume / 50) * (1 + avg_sentiment), 1.0)

        return {
            "effectiveness_score": max(effectiveness_score, 0),
            "coverage_volume": coverage_volume,
            "avg_sentiment": avg_sentiment,
            "total_media_statements": len(media_statements)
        }

    def _calculate_party_metrics(self, votes: List[Vote], party: str) -> Dict:
        """Calculate party alignment metrics."""
        if not votes:
            return {"alignment_score": 0.5}

        party_line_votes = [v for v in votes if v.party_line_vote]
        if not party_line_votes:
            return {"alignment_score": 0.5}

        # Count votes aligned with party
        aligned_votes = 0
        for vote in party_line_votes:
            # This is simplified - would need actual party position data
            if vote.vote_position in ["Yes", "Aye"]:
                aligned_votes += 1

        alignment_score = aligned_votes / len(party_line_votes)

        return {
            "alignment_score": alignment_score,
            "total_party_line_votes": len(party_line_votes),
            "aligned_votes": aligned_votes
        }

    def _calculate_coalition_building_score(self, votes: List[Vote]) -> float:
        """Calculate how well the official builds bipartisan coalitions."""
        if not votes:
            return 0.0

        # Look for votes where official was in minority of their party
        # but part of successful bipartisan coalition
        bipartisan_votes = [v for v in votes if not v.party_line_vote]

        if not bipartisan_votes:
            return 0.0

        # Simplified calculation - in reality would need more detailed data
        return min(len(bipartisan_votes) / len(votes), 1.0)

    def _assess_financial_strength(self, financial_data: List[FinancialDisclosure]) -> float:
        """Assess financial/fundraising strength."""
        if not financial_data:
            return 0.0

        latest_disclosure = financial_data[0]

        # Extract relevant financial metrics
        campaign_total = 0
        if latest_disclosure.campaign_contributions:
            campaign_total = sum(contrib.get("amount", 0)
                               for contrib in latest_disclosure.campaign_contributions.get("contributions", []))

        # Simplified scoring based on campaign finances
        # In reality, this would compare to district/state averages
        if campaign_total > 1000000:
            return 0.9
        elif campaign_total > 500000:
            return 0.7
        elif campaign_total > 100000:
            return 0.5
        elif campaign_total > 50000:
            return 0.3
        else:
            return 0.1

    def _calculate_years_in_office(self, positions: List[Position]) -> int:
        """Calculate total years in elected office."""
        total_years = 0
        for position in positions:
            start_date = position.start_date
            end_date = position.end_date or datetime.now()
            years = (end_date - start_date).days / 365.25
            total_years += years

        return int(total_years)

    def _determine_analysis_context(self, official: Official) -> str:
        """Determine the current political context for analysis."""
        current_year = datetime.now().year

        # Determine election cycle
        if official.positions and official.positions[0].position_type.value in ["senator"]:
            # Senate 6-year cycles
            senate_cycle_year = 2024  # Would calculate based on when seat is up
            years_until_election = (senate_cycle_year - current_year) % 6
        else:
            # House 2-year cycles
            years_until_election = (2024 - current_year) % 2

        if years_until_election == 0:
            return f"Election year {current_year}"
        elif years_until_election == 1:
            return f"Pre-election year, {current_year + 1} election cycle"
        else:
            return f"Mid-cycle, {years_until_election} years until next election"

    def _identify_trending_issues(self, statements: List[Statement]) -> List[str]:
        """Identify trending policy issues from recent statements."""
        if not statements:
            return []

        # Count issue mentions in recent statements
        issue_counts = Counter()

        for statement in statements[-20:]:  # Last 20 statements
            if statement.key_phrases:
                for phrase in statement.key_phrases:
                    if isinstance(phrase, dict) and "phrase" in phrase:
                        issue_counts[phrase["phrase"]] += 1

        # Return top trending issues
        return [issue for issue, count in issue_counts.most_common(5)]

    def _assess_primary_challenge_risk(self, official: Official, data: Dict) -> float:
        """Assess risk of primary challenge."""
        risk_score = 0.0

        # Party alignment factor
        party_alignment = data["party_metrics"].get("alignment_score", 0.5)
        if party_alignment < 0.5:
            risk_score += 0.3  # Too moderate for party base
        elif party_alignment > 0.9:
            risk_score += 0.2  # May face moderate challenger

        # Controversial votes
        controversial_count = len(data["legislative_metrics"].get("controversial_votes", []))
        risk_score += min(controversial_count * 0.1, 0.3)

        # Low fundraising
        financial_strength = self._assess_financial_strength(data["financial_data"])
        if financial_strength < 0.4:
            risk_score += 0.2

        return min(risk_score, 1.0)

    def _assess_general_election_risk(self, official: Official, data: Dict) -> float:
        """Assess general election vulnerability."""
        # This would incorporate district competitiveness, approval ratings, etc.
        # Simplified calculation for now
        risk_score = 0.3  # Base risk

        # Poor legislative effectiveness increases risk
        legislative_score = data["legislative_metrics"].get("effectiveness_score", 0)
        if legislative_score < 0.3:
            risk_score += 0.2

        # Low constituency engagement
        engagement_score = data["constituency_metrics"].get("engagement_score", 0)
        if engagement_score < 0.4:
            risk_score += 0.2

        return min(risk_score, 1.0)

    def _assess_scandal_risk(self, data: Dict) -> float:
        """Assess potential for scandal exposure."""
        risk_score = 0.1  # Base risk

        # High-value financial disclosures might indicate conflicts
        financial_data = data["financial_data"]
        if financial_data:
            latest = financial_data[0]
            if latest.potential_conflicts:
                risk_score += len(latest.potential_conflicts) * 0.1

        return min(risk_score, 1.0)

    def _analyze_district_demographics(self, official: Official) -> List[Dict]:
        """Analyze demographic opportunities in the district."""
        # This would require demographic data integration
        # Placeholder implementation
        opportunities = []

        if official.district and official.state:
            opportunities.append({
                "category": "Demographic Engagement",
                "description": "Expand outreach to growing demographic groups",
                "details": f"District {official.district} demographic shifts create opportunities",
                "potential": "Medium",
                "timeframe": "1-2 years"
            })

        return opportunities

    def _analyze_electoral_timing(self, official: Official) -> List[Dict]:
        """Analyze electoral cycle opportunities."""
        opportunities = []

        current_year = datetime.now().year
        is_election_year = (current_year % 2) == 0

        if not is_election_year:
            opportunities.append({
                "category": "Off-Year Positioning",
                "description": "Use off-election year to build policy credentials",
                "details": "Reduced campaign pressure allows focus on governance",
                "potential": "Medium",
                "timeframe": "Immediate"
            })

        return opportunities

    def _analyze_demographic_shifts(self, official: Official) -> List[Dict]:
        """Analyze demographic threat patterns."""
        # Placeholder - would need actual demographic data
        return []

    def _analyze_national_environment(self, official: Official) -> List[Dict]:
        """Analyze national political environment threats."""
        threats = []

        # Would analyze presidential approval, national trends, etc.
        # Simplified placeholder
        if official.party:
            threats.append({
                "category": "National Environment",
                "description": f"National trends may impact {official.party} candidates",
                "likelihood": "Medium",
                "impact": "Medium",
                "timeframe": "Next election cycle",
                "risk_score": 0.4
            })

        return threats

    def _calculate_overall_assessment(self, swot_analysis: Dict) -> Dict:
        """Calculate overall assessment from SWOT components."""
        strengths = swot_analysis["strengths"]
        weaknesses = swot_analysis["weaknesses"]
        opportunities = swot_analysis["opportunities"]
        threats = swot_analysis["threats"]

        # Calculate weighted scores
        strength_score = sum(s.get("quantification", 0) for s in strengths) / max(len(strengths), 1)
        weakness_score = sum(w.get("quantification", 0) for w in weaknesses) / max(len(weaknesses), 1)
        opportunity_score = len(opportunities) / 10.0  # Normalize to 0-1
        threat_score = sum(t.get("risk_score", 0) for t in threats) / max(len(threats), 1)

        # Overall competitiveness
        competitiveness = (strength_score + opportunity_score) - (weakness_score + threat_score)

        if competitiveness > 0.5:
            rating = "Strong"
        elif competitiveness > 0:
            rating = "Moderate"
        elif competitiveness > -0.5:
            rating = "Vulnerable"
        else:
            rating = "High Risk"

        return {
            "overall_score": competitiveness,
            "competitiveness_rating": rating,
            "strength_score": strength_score,
            "weakness_score": weakness_score,
            "opportunity_score": opportunity_score,
            "threat_score": threat_score
        }

    def _calculate_detailed_metrics(self, data: Dict) -> Dict:
        """Calculate detailed performance metrics."""
        return {
            "legislative_metrics": data["legislative_metrics"],
            "constituency_metrics": data["constituency_metrics"],
            "media_metrics": data["media_metrics"],
            "party_metrics": data["party_metrics"],
            "analysis_date": datetime.now().isoformat()
        }

    def _generate_strategic_recommendations(self, swot_analysis: Dict) -> List[Dict]:
        """Generate strategic recommendations based on SWOT analysis."""
        recommendations = []

        overall_rating = swot_analysis["overall_assessment"]["competitiveness_rating"]

        if overall_rating == "Strong":
            recommendations.extend([
                {
                    "priority": "High",
                    "category": "Maintain Advantage",
                    "recommendation": "Focus on signature legislative initiatives",
                    "timeframe": "Immediate"
                },
                {
                    "priority": "Medium",
                    "category": "Build Legacy",
                    "recommendation": "Develop long-term policy leadership position",
                    "timeframe": "6-12 months"
                }
            ])
        elif overall_rating in ["Moderate", "Vulnerable"]:
            recommendations.extend([
                {
                    "priority": "High",
                    "category": "Address Weaknesses",
                    "recommendation": "Improve constituency engagement and fundraising",
                    "timeframe": "Immediate"
                },
                {
                    "priority": "High",
                    "category": "Leverage Opportunities",
                    "recommendation": "Build coalitions on trending issues",
                    "timeframe": "3-6 months"
                }
            ])
        else:  # High Risk
            recommendations.extend([
                {
                    "priority": "Critical",
                    "category": "Crisis Management",
                    "recommendation": "Address major weaknesses and threats immediately",
                    "timeframe": "Immediate"
                },
                {
                    "priority": "High",
                    "category": "Reputation Recovery",
                    "recommendation": "Focus on signature accomplishments and base building",
                    "timeframe": "1-3 months"
                }
            ])

        return recommendations