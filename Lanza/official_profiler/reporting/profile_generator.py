"""
Comprehensive profile report generation system.
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import structlog
from sqlalchemy.orm import Session
from models.official import Official
from analyzers.swot_analyzer import SWOTAnalyzer
from analyzers.issue_tracker import IssueTracker

logger = structlog.get_logger()


class ProfileGenerator:
    """Generate comprehensive official profiles and reports."""

    def __init__(self):
        self.swot_analyzer = SWOTAnalyzer()
        self.issue_tracker = IssueTracker()

        # Setup Jinja2 templates
        template_dir = Path(__file__).parent / "templates"
        template_dir.mkdir(exist_ok=True)
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

        # Create default templates if they don't exist
        self._create_default_templates()

    async def generate_comprehensive_profile(self, official_id: str,
                                           db_session: Session,
                                           output_format: str = "html") -> Dict:
        """Generate a complete official profile."""
        official = db_session.query(Official).filter_by(id=official_id).first()
        if not official:
            return {"error": "Official not found"}

        profile_data = {
            "generation_info": {
                "official_id": official_id,
                "generated_at": datetime.now().isoformat(),
                "format": output_format
            },
            "basic_info": {},
            "career_summary": {},
            "legislative_record": {},
            "position_analysis": {},
            "swot_analysis": {},
            "issue_tracking": {},
            "financial_overview": {},
            "media_presence": {},
            "visualizations": {}
        }

        # Basic Information
        profile_data["basic_info"] = self._extract_basic_info(official)

        # Career Summary
        profile_data["career_summary"] = self._generate_career_summary(official, db_session)

        # Legislative Record
        profile_data["legislative_record"] = await self._analyze_legislative_record(
            official, db_session
        )

        # Position Analysis
        profile_data["position_analysis"] = await self._analyze_position_evolution(
            official, db_session
        )

        # SWOT Analysis
        profile_data["swot_analysis"] = await self.swot_analyzer.generate_comprehensive_swot(
            official_id, db_session
        )

        # Issue Tracking
        profile_data["issue_tracking"] = await self._comprehensive_issue_analysis(
            official, db_session
        )

        # Financial Overview
        profile_data["financial_overview"] = self._analyze_financial_data(official, db_session)

        # Media Presence
        profile_data["media_presence"] = self._analyze_media_presence(official, db_session)

        # Generate Visualizations
        profile_data["visualizations"] = await self._generate_visualizations(
            profile_data, official
        )

        # Generate final report
        if output_format.lower() == "html":
            report_content = self._generate_html_report(profile_data)
            profile_data["report_content"] = report_content
        elif output_format.lower() == "json":
            profile_data["report_content"] = json.dumps(profile_data, indent=2, default=str)
        elif output_format.lower() == "pdf":
            # Generate HTML first, then convert to PDF
            html_content = self._generate_html_report(profile_data)
            profile_data["report_content"] = self._convert_to_pdf(html_content)

        return profile_data

    def _extract_basic_info(self, official: Official) -> Dict:
        """Extract basic information about the official."""
        current_position = next(
            (p for p in official.positions if p.is_current), None
        )

        return {
            "full_name": official.full_name,
            "party": official.party,
            "position": {
                "title": current_position.title if current_position else "Unknown",
                "chamber": current_position.chamber if current_position else None,
                "state": official.state,
                "district": official.district
            },
            "contact_info": {
                "email": official.email,
                "phone": official.phone,
                "website": official.website
            },
            "social_media": {
                "twitter": official.twitter_handle,
                "facebook": official.facebook_url,
                "instagram": official.instagram_handle
            },
            "demographics": {
                "date_of_birth": official.date_of_birth,
                "gender": official.gender
            },
            "service_info": {
                "currently_serving": official.currently_serving,
                "profile_completeness": official.profile_completeness,
                "last_updated": official.last_updated
            }
        }

    def _generate_career_summary(self, official: Official,
                                db_session: Session) -> Dict:
        """Generate career timeline and summary."""
        positions = sorted(official.positions, key=lambda x: x.start_date)

        career_timeline = []
        total_years = 0

        for position in positions:
            end_date = position.end_date or datetime.now()
            duration_years = (end_date - position.start_date).days / 365.25

            career_timeline.append({
                "position": position.title,
                "start_date": position.start_date,
                "end_date": position.end_date,
                "duration_years": round(duration_years, 1),
                "is_current": position.is_current,
                "committees": position.committees or [],
                "leadership_roles": position.leadership_roles or []
            })

            total_years += duration_years

        # Career highlights
        highlights = {
            "total_years_service": round(total_years, 1),
            "positions_held": len(positions),
            "current_committees": [],
            "leadership_experience": []
        }

        current_position = next((p for p in positions if p.is_current), None)
        if current_position:
            highlights["current_committees"] = current_position.committees or []
            highlights["leadership_experience"] = current_position.leadership_roles or []

        return {
            "timeline": career_timeline,
            "highlights": highlights,
            "career_progression": self._analyze_career_progression(positions)
        }

    async def _analyze_legislative_record(self, official: Official,
                                        db_session: Session) -> Dict:
        """Analyze legislative effectiveness and record."""
        cutoff_date = datetime.now() - timedelta(days=730)  # 2 years

        votes = [v for v in official.votes if v.vote_date >= cutoff_date]
        statements = [s for s in official.statements if s.date_made >= cutoff_date]

        # Vote analysis
        vote_breakdown = {
            "total_votes": len(votes),
            "yes_votes": len([v for v in votes if v.vote_position in ["Yes", "Aye"]]),
            "no_votes": len([v for v in votes if v.vote_position in ["No", "Nay"]]),
            "key_votes": len([v for v in votes if v.vote_significance == "Key"]),
            "party_line_votes": len([v for v in votes if v.party_line_vote])
        }

        if vote_breakdown["total_votes"] > 0:
            vote_breakdown["yes_percentage"] = (
                vote_breakdown["yes_votes"] / vote_breakdown["total_votes"] * 100
            )
            vote_breakdown["party_loyalty"] = (
                vote_breakdown["party_line_votes"] / vote_breakdown["total_votes"] * 100
            )

        # Bill sponsorship (simplified)
        sponsored_bills = len([v for v in votes if v.vote_type == "Final Passage"
                              and v.vote_position in ["Yes", "Aye"]])

        # Statement analysis
        statement_breakdown = {
            "total_statements": len(statements),
            "press_releases": len([s for s in statements
                                 if s.statement_type.value == "press_release"]),
            "floor_speeches": len([s for s in statements
                                 if s.statement_type.value == "speech"]),
            "interviews": len([s for s in statements
                             if s.statement_type.value == "interview"])
        }

        return {
            "vote_analysis": vote_breakdown,
            "legislation": {
                "bills_sponsored": sponsored_bills,
                "bills_supported": vote_breakdown["yes_votes"]
            },
            "communication": statement_breakdown,
            "effectiveness_metrics": self._calculate_effectiveness_metrics(votes, statements)
        }

    async def _analyze_position_evolution(self, official: Official,
                                        db_session: Session) -> Dict:
        """Analyze evolution of positions on key issues."""
        position_analysis = {
            "consistency_overview": {},
            "major_issues": {},
            "recent_changes": [],
            "trend_analysis": {}
        }

        # Get consistency analysis
        consistency = await self.issue_tracker.analyze_issue_consistency(
            str(official.id), db_session
        )
        position_analysis["consistency_overview"] = {
            "overall_score": consistency.get("overall_consistency_score", 0),
            "stable_positions": len(consistency.get("stable_positions", [])),
            "inconsistent_areas": len(consistency.get("inconsistent_areas", [])),
            "flip_flops": len(consistency.get("flip_flops", []))
        }

        # Analyze major issues
        major_issues = ["Healthcare", "Economy", "Education", "Environment"]
        for issue_category in major_issues:
            # Find issues in this category
            category_issues = db_session.query(Issue).filter(
                Issue.category == issue_category,
                Issue.is_active == True
            ).all()

            if category_issues:
                issue = category_issues[0]  # Take first issue as example
                evolution = await self.issue_tracker.track_position_evolution(
                    str(official.id), str(issue.id), db_session
                )

                position_analysis["major_issues"][issue_category] = {
                    "current_position": self._determine_current_position(evolution),
                    "consistency_score": evolution.get("consistency_score", 0),
                    "position_changes": len(evolution.get("position_changes", [])),
                    "last_statement_date": self._get_last_statement_date(evolution)
                }

        return position_analysis

    async def _comprehensive_issue_analysis(self, official: Official,
                                          db_session: Session) -> Dict:
        """Comprehensive analysis of issue engagement."""
        issue_analysis = {}

        # Geographic relevance analysis
        geographic_analysis = await self.issue_tracker.analyze_geographic_issue_relevance(
            official, db_session
        )
        issue_analysis["geographic_breakdown"] = geographic_analysis

        # Emerging issues
        emerging_issues = await self.issue_tracker.identify_emerging_issues(
            str(official.id), db_session
        )
        issue_analysis["emerging_issues"] = emerging_issues[:5]  # Top 5

        # Issue category engagement
        statements_by_category = {}
        for statement in official.statements[-100:]:  # Last 100 statements
            if statement.issue and statement.issue.category:
                category = statement.issue.category
                if category not in statements_by_category:
                    statements_by_category[category] = 0
                statements_by_category[category] += 1

        issue_analysis["category_engagement"] = statements_by_category

        return issue_analysis

    def _analyze_financial_data(self, official: Official,
                              db_session: Session) -> Dict:
        """Analyze financial disclosures and campaign data."""
        financial_disclosures = sorted(
            official.financial_disclosures,
            key=lambda x: x.report_year,
            reverse=True
        )

        if not financial_disclosures:
            return {"status": "no_data"}

        latest_disclosure = financial_disclosures[0]

        financial_overview = {
            "latest_report_year": latest_disclosure.report_year,
            "filing_date": latest_disclosure.filing_date,
            "wealth_estimate": {
                "min": latest_disclosure.wealth_estimate_min,
                "max": latest_disclosure.wealth_estimate_max
            },
            "potential_conflicts": latest_disclosure.potential_conflicts or [],
            "disclosure_history": len(financial_disclosures)
        }

        # Campaign finance summary
        if latest_disclosure.campaign_contributions:
            contributions = latest_disclosure.campaign_contributions
            financial_overview["campaign_finance"] = {
                "total_contributions": len(contributions.get("contributions", [])),
                "total_amount": sum(c.get("amount", 0)
                                  for c in contributions.get("contributions", [])),
                "top_contributors": contributions.get("top_contributors", [])[:5]
            }

        return financial_overview

    def _analyze_media_presence(self, official: Official,
                              db_session: Session) -> Dict:
        """Analyze media presence and communication patterns."""
        cutoff_date = datetime.now() - timedelta(days=365)
        recent_statements = [s for s in official.statements if s.date_made >= cutoff_date]

        media_analysis = {
            "total_statements": len(recent_statements),
            "by_type": {},
            "sentiment_analysis": {},
            "reach_analysis": {},
            "trending_topics": []
        }

        # Breakdown by statement type
        for statement in recent_statements:
            stmt_type = statement.statement_type.value
            if stmt_type not in media_analysis["by_type"]:
                media_analysis["by_type"][stmt_type] = 0
            media_analysis["by_type"][stmt_type] += 1

        # Sentiment analysis
        sentiments = [s.sentiment_score for s in recent_statements
                     if s.sentiment_score is not None]
        if sentiments:
            media_analysis["sentiment_analysis"] = {
                "average_sentiment": sum(sentiments) / len(sentiments),
                "positive_statements": len([s for s in sentiments if s > 0.1]),
                "negative_statements": len([s for s in sentiments if s < -0.1]),
                "neutral_statements": len([s for s in sentiments if -0.1 <= s <= 0.1])
            }

        return media_analysis

    async def _generate_visualizations(self, profile_data: Dict,
                                     official: Official) -> Dict:
        """Generate visualization data for the profile."""
        visualizations = {}

        # SWOT Analysis Radar Chart
        swot_data = profile_data.get("swot_analysis", {})
        if "overall_assessment" in swot_data:
            assessment = swot_data["overall_assessment"]
            visualizations["swot_radar"] = self._create_swot_radar_chart(assessment)

        # Legislative Activity Timeline
        legislative_data = profile_data.get("legislative_record", {})
        visualizations["legislative_timeline"] = self._create_legislative_timeline(
            legislative_data, official
        )

        # Issue Engagement Pie Chart
        issue_data = profile_data.get("issue_tracking", {})
        if "category_engagement" in issue_data:
            visualizations["issue_pie"] = self._create_issue_engagement_pie(
                issue_data["category_engagement"]
            )

        # Position Consistency Bar Chart
        position_data = profile_data.get("position_analysis", {})
        if "consistency_overview" in position_data:
            visualizations["consistency_bar"] = self._create_consistency_bar_chart(
                position_data["consistency_overview"]
            )

        # Geographic Focus Map
        geographic_data = issue_data.get("geographic_breakdown", {})
        if "geographic_focus" in geographic_data:
            visualizations["geographic_map"] = self._create_geographic_focus_chart(
                geographic_data["geographic_focus"]
            )

        return visualizations

    def _create_swot_radar_chart(self, assessment: Dict) -> Dict:
        """Create SWOT radar chart visualization."""
        categories = ['Strengths', 'Opportunities', 'Threats (Inverted)', 'Weaknesses (Inverted)']
        values = [
            assessment.get("strength_score", 0),
            assessment.get("opportunity_score", 0),
            1 - assessment.get("threat_score", 0),  # Invert threats
            1 - assessment.get("weakness_score", 0)  # Invert weaknesses
        ]

        fig = go.Figure(data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Assessment'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=False,
            title="SWOT Analysis Overview"
        )

        return {
            "type": "radar",
            "data": fig.to_dict(),
            "html": fig.to_html(include_plotlyjs=False)
        }

    def _create_legislative_timeline(self, legislative_data: Dict,
                                   official: Official) -> Dict:
        """Create legislative activity timeline."""
        # Get recent votes for timeline
        recent_votes = [v for v in official.votes[-50:]]  # Last 50 votes
        dates = [v.vote_date for v in recent_votes]
        positions = [1 if v.vote_position in ["Yes", "Aye"] else -1 for v in recent_votes]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=positions,
            mode='markers+lines',
            name='Vote Position',
            marker=dict(size=8),
            hovertemplate='<b>%{text}</b><br>Date: %{x}<br>Position: %{customdata}',
            text=[v.bill_title[:50] + "..." if len(v.bill_title) > 50
                  else v.bill_title for v in recent_votes],
            customdata=[v.vote_position for v in recent_votes]
        ))

        fig.update_layout(
            title="Recent Legislative Activity",
            xaxis_title="Date",
            yaxis_title="Position (1=Yes, -1=No)",
            hovermode='closest'
        )

        return {
            "type": "timeline",
            "data": fig.to_dict(),
            "html": fig.to_html(include_plotlyjs=False)
        }

    def _create_issue_engagement_pie(self, category_engagement: Dict) -> Dict:
        """Create issue engagement pie chart."""
        if not category_engagement:
            return {"type": "pie", "data": None, "html": "No data available"}

        labels = list(category_engagement.keys())
        values = list(category_engagement.values())

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3
        )])

        fig.update_layout(
            title="Issue Category Engagement",
            annotations=[dict(text='Issues', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )

        return {
            "type": "pie",
            "data": fig.to_dict(),
            "html": fig.to_html(include_plotlyjs=False)
        }

    def _create_consistency_bar_chart(self, consistency_data: Dict) -> Dict:
        """Create position consistency bar chart."""
        categories = ['Overall Score', 'Stable Positions', 'Inconsistent Areas', 'Flip-Flops']
        values = [
            consistency_data.get("overall_score", 0),
            consistency_data.get("stable_positions", 0) / 10,  # Normalize
            consistency_data.get("inconsistent_areas", 0) / 10,  # Normalize
            consistency_data.get("flip_flops", 0) / 5  # Normalize
        ]

        colors = ['green', 'blue', 'orange', 'red']

        fig = go.Figure(data=[
            go.Bar(x=categories, y=values, marker_color=colors)
        ])

        fig.update_layout(
            title="Position Consistency Analysis",
            yaxis_title="Score/Count (normalized)",
            xaxis_title="Category"
        )

        return {
            "type": "bar",
            "data": fig.to_dict(),
            "html": fig.to_html(include_plotlyjs=False)
        }

    def _create_geographic_focus_chart(self, geographic_focus: Dict) -> Dict:
        """Create geographic focus bar chart."""
        if not geographic_focus:
            return {"type": "bar", "data": None, "html": "No data available"}

        levels = list(geographic_focus.keys())
        percentages = [geographic_focus[level]["percentage"] for level in levels]

        fig = go.Figure(data=[
            go.Bar(x=levels, y=percentages, marker_color='lightblue')
        ])

        fig.update_layout(
            title="Geographic Focus Distribution",
            xaxis_title="Geographic Level",
            yaxis_title="Percentage of Statements"
        )

        return {
            "type": "bar",
            "data": fig.to_dict(),
            "html": fig.to_html(include_plotlyjs=False)
        }

    def _generate_html_report(self, profile_data: Dict) -> str:
        """Generate HTML report from profile data."""
        template = self.jinja_env.get_template("profile_template.html")
        return template.render(**profile_data)

    def _convert_to_pdf(self, html_content: str) -> bytes:
        """Convert HTML content to PDF."""
        try:
            import weasyprint
            pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
            return pdf_bytes
        except ImportError:
            logger.warning("WeasyPrint not available, cannot generate PDF")
            return html_content.encode('utf-8')

    def _create_default_templates(self):
        """Create default Jinja2 templates."""
        template_dir = Path(__file__).parent / "templates"
        profile_template_path = template_dir / "profile_template.html"

        if not profile_template_path.exists():
            template_content = self._get_default_html_template()
            profile_template_path.write_text(template_content)

    def _get_default_html_template(self) -> str:
        """Get default HTML template content."""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Official Profile: {{ basic_info.full_name }}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .header { background-color: #f4f4f4; padding: 20px; border-radius: 5px; }
        .section { margin: 30px 0; }
        .subsection { margin: 20px 0; }
        .metric { display: inline-block; margin: 10px; padding: 10px; background-color: #e9e9e9; border-radius: 5px; }
        .swot-item { margin: 10px 0; padding: 10px; border-left: 4px solid #007bff; background-color: #f8f9fa; }
        .strength { border-left-color: #28a745; }
        .weakness { border-left-color: #dc3545; }
        .opportunity { border-left-color: #ffc107; }
        .threat { border-left-color: #fd7e14; }
        .chart-container { margin: 20px 0; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f2f2f2; }
        .timeline-item { margin: 10px 0; padding: 10px; border-left: 3px solid #007bff; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ basic_info.full_name }}</h1>
        <h2>{{ basic_info.position.title }} ({{ basic_info.party }})</h2>
        <p><strong>State:</strong> {{ basic_info.position.state }}
        {% if basic_info.position.district %} | <strong>District:</strong> {{ basic_info.position.district }}{% endif %}</p>
        <p><strong>Generated:</strong> {{ generation_info.generated_at }}</p>
    </div>

    <div class="section">
        <h2>Executive Summary</h2>
        {% if swot_analysis.overall_assessment %}
        <p><strong>Overall Rating:</strong> {{ swot_analysis.overall_assessment.competitiveness_rating }}</p>
        <p><strong>Profile Completeness:</strong> {{ "%.1f"|format(basic_info.service_info.profile_completeness * 100) }}%</p>
        {% endif %}
    </div>

    <div class="section">
        <h2>Career Summary</h2>
        {% if career_summary.highlights %}
        <div class="metric">Total Years in Office: {{ career_summary.highlights.total_years_service }}</div>
        <div class="metric">Positions Held: {{ career_summary.highlights.positions_held }}</div>
        {% endif %}

        <h3>Career Timeline</h3>
        {% for position in career_summary.timeline %}
        <div class="timeline-item">
            <strong>{{ position.position }}</strong> ({{ position.duration_years }} years)
            <br>{{ position.start_date.strftime("%Y") }} - {{ position.end_date.strftime("%Y") if position.end_date else "Present" }}
            {% if position.committees %}
            <br><em>Committees:</em> {{ position.committees|join(", ") }}
            {% endif %}
        </div>
        {% endfor %}
    </div>

    <div class="section">
        <h2>Legislative Record</h2>
        {% if legislative_record.vote_analysis %}
        <div class="metric">Total Votes: {{ legislative_record.vote_analysis.total_votes }}</div>
        <div class="metric">Yes Votes: {{ "%.1f"|format(legislative_record.vote_analysis.yes_percentage) }}%</div>
        <div class="metric">Party Loyalty: {{ "%.1f"|format(legislative_record.vote_analysis.party_loyalty) }}%</div>
        {% endif %}
    </div>

    <div class="section">
        <h2>SWOT Analysis</h2>

        <div class="subsection">
            <h3>Strengths</h3>
            {% for strength in swot_analysis.strengths %}
            <div class="swot-item strength">
                <strong>{{ strength.category }}:</strong> {{ strength.description }}
                <br><em>Evidence:</em> {{ strength.evidence }}
            </div>
            {% endfor %}
        </div>

        <div class="subsection">
            <h3>Weaknesses</h3>
            {% for weakness in swot_analysis.weaknesses %}
            <div class="swot-item weakness">
                <strong>{{ weakness.category }}:</strong> {{ weakness.description }}
                <br><em>Evidence:</em> {{ weakness.evidence }}
            </div>
            {% endfor %}
        </div>

        <div class="subsection">
            <h3>Opportunities</h3>
            {% for opportunity in swot_analysis.opportunities %}
            <div class="swot-item opportunity">
                <strong>{{ opportunity.category }}:</strong> {{ opportunity.description }}
                <br><em>Details:</em> {{ opportunity.details }}
            </div>
            {% endfor %}
        </div>

        <div class="subsection">
            <h3>Threats</h3>
            {% for threat in swot_analysis.threats %}
            <div class="swot-item threat">
                <strong>{{ threat.category }}:</strong> {{ threat.description }}
                <br><em>Likelihood:</em> {{ threat.likelihood }} | <em>Impact:</em> {{ threat.impact }}
            </div>
            {% endfor %}
        </div>
    </div>

    <div class="section">
        <h2>Position Analysis</h2>
        {% if position_analysis.consistency_overview %}
        <p><strong>Overall Consistency Score:</strong> {{ "%.2f"|format(position_analysis.consistency_overview.overall_score) }}</p>
        <div class="metric">Stable Positions: {{ position_analysis.consistency_overview.stable_positions }}</div>
        <div class="metric">Inconsistent Areas: {{ position_analysis.consistency_overview.inconsistent_areas }}</div>
        <div class="metric">Position Changes: {{ position_analysis.consistency_overview.flip_flops }}</div>
        {% endif %}
    </div>

    <div class="section">
        <h2>Issue Engagement</h2>
        {% if issue_tracking.emerging_issues %}
        <h3>Emerging Issues</h3>
        <table>
            <tr><th>Issue</th><th>Recent Mentions</th><th>Growth Rate</th><th>Type</th></tr>
            {% for issue in issue_tracking.emerging_issues %}
            <tr>
                <td>{{ issue.topic }}</td>
                <td>{{ issue.recent_mentions }}</td>
                <td>{{ "%.1f"|format(issue.growth_rate * 100) }}%</td>
                <td>{{ issue.change_type }}</td>
            </tr>
            {% endfor %}
        </table>
        {% endif %}
    </div>

    <div class="section">
        <h2>Visualizations</h2>
        {% for viz_name, viz_data in visualizations.items() %}
        {% if viz_data.html %}
        <div class="chart-container">
            <h3>{{ viz_name.replace('_', ' ').title() }}</h3>
            {{ viz_data.html|safe }}
        </div>
        {% endif %}
        {% endfor %}
    </div>

    {% if swot_analysis.strategic_recommendations %}
    <div class="section">
        <h2>Strategic Recommendations</h2>
        {% for rec in swot_analysis.strategic_recommendations %}
        <div class="swot-item">
            <strong>{{ rec.category }} ({{ rec.priority }} Priority):</strong> {{ rec.recommendation }}
            <br><em>Timeframe:</em> {{ rec.timeframe }}
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <div class="section">
        <h2>Data Sources & Methodology</h2>
        <p>This profile was generated using data from:</p>
        <ul>
            <li>Congress.gov API for legislative records</li>
            <li>Federal Election Commission data for financial information</li>
            <li>Official government websites and press releases</li>
            <li>Social media platforms for public statements</li>
            <li>C-SPAN archives for speeches and appearances</li>
        </ul>
        <p><em>Analysis conducted using natural language processing, statistical analysis, and political science frameworks.</em></p>
    </div>
</body>
</html>
        '''

    # Helper methods
    def _analyze_career_progression(self, positions: List) -> Dict:
        """Analyze career progression patterns."""
        if len(positions) < 2:
            return {"trend": "insufficient_data"}

        # Simplified analysis
        progression_score = len(positions) * 0.2  # Basic scoring
        return {
            "trend": "ascending" if progression_score > 0.5 else "stable",
            "progression_score": min(progression_score, 1.0),
            "advancement_pattern": "linear"  # Simplified
        }

    def _calculate_effectiveness_metrics(self, votes: List, statements: List) -> Dict:
        """Calculate legislative effectiveness metrics."""
        if not votes:
            return {"effectiveness_score": 0}

        key_votes = [v for v in votes if v.vote_significance == "Key"]
        successful_votes = len([v for v in key_votes if v.vote_position in ["Yes", "Aye"]])

        effectiveness_score = successful_votes / max(len(key_votes), 1)

        return {
            "effectiveness_score": effectiveness_score,
            "key_vote_success_rate": effectiveness_score,
            "communication_activity": len(statements),
            "overall_activity_score": min((len(votes) + len(statements)) / 100, 1.0)
        }

    def _determine_current_position(self, evolution: Dict) -> str:
        """Determine current position from evolution data."""
        timeline = evolution.get("timeline", [])
        if timeline:
            return timeline[-1].get("stance", "Unknown")
        return "Unknown"

    def _get_last_statement_date(self, evolution: Dict) -> Optional[datetime]:
        """Get date of last statement from evolution data."""
        timeline = evolution.get("timeline", [])
        if timeline:
            return timeline[-1].get("date")
        return None