"""
Main application entry point for the Official Profiler system.
"""
import asyncio
import sys
import argparse
from pathlib import Path
from datetime import datetime
import structlog
from sqlalchemy.orm import Session

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from models.database import get_db, engine, Base
from models.official import Official, Issue
from apis.congress_api import CongressAPI
from apis.ny_state_api import NYStateAPI, NYCDataCollector
from collectors.municipal_collector import MunicipalDataCollector
from analyzers.swot_analyzer import SWOTAnalyzer
from analyzers.issue_tracker import IssueTracker
from analyzers.state_issue_tracker import StateIssueTracker
from reporting.profile_generator import ProfileGenerator
from utils.async_tasks import AsyncDataCollector, TaskMonitor
from utils.jurisdiction_manager import JurisdictionManager, JurisdictionLevel

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class OfficialProfiler:
    """Main application class for the Official Profiler system."""

    def __init__(self):
        self.db_session = None
        self.congress_api = None
        self.ny_state_api = None
        self.municipal_collector = None
        self.swot_analyzer = SWOTAnalyzer()
        self.issue_tracker = IssueTracker()
        self.state_issue_tracker = StateIssueTracker()
        self.profile_generator = ProfileGenerator()
        self.async_collector = AsyncDataCollector()
        self.jurisdiction_manager = JurisdictionManager()

    async def initialize(self):
        """Initialize the application."""
        logger.info("Initializing Official Profiler system")

        # Initialize database
        self.db_session = next(get_db())

        # Initialize APIs
        self.congress_api = CongressAPI()
        self.ny_state_api = NYStateAPI()
        self.municipal_collector = MunicipalDataCollector()
        await self.async_collector.initialize()

        logger.info("System initialization complete")

    async def cleanup(self):
        """Cleanup resources."""
        if self.db_session:
            self.db_session.close()
        if self.congress_api:
            await self.congress_api.__aexit__(None, None, None)
        await self.async_collector.cleanup()

        logger.info("System cleanup complete")

    async def create_database_tables(self):
        """Create all database tables."""
        logger.info("Creating database tables")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

    async def import_congressional_members(self, congress: int = 118):
        """Import all current congressional members."""
        logger.info("Importing congressional members", congress=congress)

        async with self.congress_api as api:
            # Get House members
            house_members = await api.get_members(congress, "house")
            logger.info("Retrieved House members", count=len(house_members))

            # Get Senate members
            senate_members = await api.get_members(congress, "senate")
            logger.info("Retrieved Senate members", count=len(senate_members))

            all_members = house_members + senate_members

            # Import to database
            imported_count = 0
            for member_data in all_members:
                try:
                    # Check if member already exists
                    bioguide_id = member_data.get("bioguideId")
                    if not bioguide_id:
                        continue

                    existing_member = self.db_session.query(Official).filter_by(
                        bioguide_id=bioguide_id
                    ).first()

                    if existing_member:
                        continue  # Skip if already exists

                    # Create new official record
                    official = Official(
                        bioguide_id=bioguide_id,
                        first_name=member_data.get("firstName", ""),
                        last_name=member_data.get("lastName", ""),
                        full_name=f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}".strip(),
                        party=member_data.get("partyName", ""),
                        state=member_data.get("state", ""),
                        district=member_data.get("district"),
                        currently_serving=True
                    )

                    # Add contact information if available
                    if "url" in member_data:
                        official.website = member_data["url"]

                    self.db_session.add(official)
                    imported_count += 1

                except Exception as e:
                    logger.error("Error importing member",
                               member=member_data.get("bioguideId"),
                               error=str(e))
                    continue

            self.db_session.commit()
            logger.info("Congressional members imported successfully",
                       total=len(all_members), imported=imported_count)

    async def import_ny_state_members(self, session_year: int = 2023):
        """Import NY State Legislature members."""
        logger.info("Importing NY State legislators", session_year=session_year)

        async with self.ny_state_api as api:
            # Get Senate members
            senate_members = await api.get_senate_members(session_year)
            logger.info("Retrieved NY Senate members", count=len(senate_members))

            # Get Assembly members
            assembly_members = await api.get_assembly_members(session_year)
            logger.info("Retrieved NY Assembly members", count=len(assembly_members))

            all_members = senate_members + assembly_members

            # Import to database
            imported_count = 0
            for member_data in all_members:
                try:
                    # Check if member already exists
                    member_id = member_data.get("member_id")
                    if not member_id:
                        continue

                    existing_member = self.db_session.query(Official).filter_by(
                        bioguide_id=member_id  # Using member_id as unique identifier
                    ).first()

                    if existing_member:
                        continue  # Skip if already exists

                    # Determine position type and jurisdiction
                    chamber = member_data.get("chamber", "").lower()
                    if chamber == "senate":
                        position_type = "state_senator"
                        jurisdiction = "state"
                    elif chamber == "assembly":
                        position_type = "state_assembly"
                        jurisdiction = "state"
                    else:
                        continue

                    # Create new official record
                    official = Official(
                        bioguide_id=member_id,
                        first_name=member_data.get("first_name", ""),
                        last_name=member_data.get("last_name", ""),
                        full_name=member_data.get("full_name", ""),
                        party="Unknown",  # Would need additional lookup
                        state="New York",
                        state_senate_district=member_data.get("district_code") if chamber == "senate" else None,
                        state_assembly_district=member_data.get("district_code") if chamber == "assembly" else None,
                        jurisdiction_level=jurisdiction,
                        currently_serving=member_data.get("incumbent", True)
                    )

                    # Add Richmond County focus for specific districts
                    if chamber == "senate" and member_data.get("district_code") == "24":
                        official.county = "Richmond County"
                        official.borough = "Staten Island"
                    elif chamber == "assembly" and member_data.get("district_code") in ["61", "62", "63", "64"]:
                        official.county = "Richmond County"
                        official.borough = "Staten Island"

                    self.db_session.add(official)
                    imported_count += 1

                except Exception as e:
                    logger.error("Error importing NY State member",
                               member=member_data.get("member_id"),
                               error=str(e))
                    continue

            self.db_session.commit()
            logger.info("NY State legislators imported successfully",
                       total=len(all_members), imported=imported_count)

    async def import_richmond_municipal_officials(self):
        """Import Richmond County/Staten Island municipal officials."""
        logger.info("Importing Richmond County/Staten Island municipal officials")

        async with self.municipal_collector as collector:
            municipal_data = await collector.collect_richmond_county_officials()

            imported_count = 0
            for official_data in municipal_data:
                try:
                    # Check for existing official
                    full_name = official_data.get("full_name")
                    position_type = official_data.get("position_type")

                    if not full_name or not position_type:
                        continue

                    existing_official = self.db_session.query(Official).filter_by(
                        full_name=full_name
                    ).first()

                    if existing_official:
                        continue  # Skip if already exists

                    # Create new official record
                    official = Official(
                        full_name=full_name,
                        first_name=full_name.split()[0] if full_name else "",
                        last_name=" ".join(full_name.split()[1:]) if full_name else "",
                        party="Unknown",  # Would need additional lookup
                        state="New York",
                        county="Richmond County",
                        city="New York City",
                        borough="Staten Island",
                        jurisdiction_level=official_data.get("jurisdiction_level", "municipal"),
                        website=official_data.get("website"),
                        currently_serving=True
                    )

                    # Set district information based on position
                    if position_type == "city_council":
                        official.council_district = official_data.get("district")
                    elif position_type == "representative" and official_data.get("district"):
                        official.congressional_district = official_data.get("district")

                    self.db_session.add(official)
                    imported_count += 1

                except Exception as e:
                    logger.error("Error importing municipal official",
                               official=official_data.get("full_name"),
                               error=str(e))
                    continue

            self.db_session.commit()
            logger.info("Richmond municipal officials imported successfully",
                       total=len(municipal_data), imported=imported_count)

    async def generate_profile(self, official_id: str = None,
                             bioguide_id: str = None,
                             name: str = None,
                             output_format: str = "html") -> str:
        """Generate a comprehensive profile for an official."""
        # Find the official
        official = None
        if official_id:
            official = self.db_session.query(Official).filter_by(id=official_id).first()
        elif bioguide_id:
            official = self.db_session.query(Official).filter_by(bioguide_id=bioguide_id).first()
        elif name:
            official = self.db_session.query(Official).filter(
                Official.full_name.ilike(f"%{name}%")
            ).first()

        if not official:
            logger.error("Official not found",
                        official_id=official_id,
                        bioguide_id=bioguide_id,
                        name=name)
            return None

        logger.info("Generating profile", official=official.full_name)

        # Generate comprehensive profile
        profile = await self.profile_generator.generate_comprehensive_profile(
            str(official.id), self.db_session, output_format
        )

        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = official.full_name.replace(" ", "_").replace(",", "")

        if output_format.lower() == "html":
            filename = f"profile_{safe_name}_{timestamp}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(profile["report_content"])
        elif output_format.lower() == "json":
            filename = f"profile_{safe_name}_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(profile["report_content"])
        elif output_format.lower() == "pdf":
            filename = f"profile_{safe_name}_{timestamp}.pdf"
            with open(filename, 'wb') as f:
                f.write(profile["report_content"])

        logger.info("Profile generated successfully", filename=filename)
        return filename

    async def run_swot_analysis(self, official_id: str = None,
                              bioguide_id: str = None) -> Dict:
        """Run SWOT analysis for an official."""
        # Find the official
        official = None
        if official_id:
            official = self.db_session.query(Official).filter_by(id=official_id).first()
        elif bioguide_id:
            official = self.db_session.query(Official).filter_by(bioguide_id=bioguide_id).first()

        if not official:
            logger.error("Official not found for SWOT analysis")
            return {}

        logger.info("Running SWOT analysis", official=official.full_name)

        swot_analysis = await self.swot_analyzer.generate_comprehensive_swot(
            str(official.id), self.db_session
        )

        return swot_analysis

    async def track_position_evolution(self, official_id: str,
                                     issue_name: str) -> Dict:
        """Track position evolution on a specific issue."""
        # Find the issue
        issue = self.db_session.query(Issue).filter_by(name=issue_name).first()
        if not issue:
            logger.error("Issue not found", issue=issue_name)
            return {}

        logger.info("Tracking position evolution",
                   official_id=official_id, issue=issue_name)

        evolution = await self.issue_tracker.track_position_evolution(
            official_id, str(issue.id), self.db_session
        )

        return evolution

    async def run_state_analysis(self, official_id: str) -> Dict:
        """Run state legislative analysis for an official."""
        logger.info("Running state analysis", official_id=official_id)

        analysis = await self.state_issue_tracker.generate_state_legislative_report(
            official_id, self.db_session
        )

        return analysis

    async def list_officials(self, limit: int = 20, state: str = None,
                           jurisdiction: str = None, richmond_focus: bool = False) -> List[Dict]:
        """List officials in the database with filtering options."""
        query = self.db_session.query(Official).filter(
            Official.currently_serving == True
        )

        if state:
            query = query.filter(Official.state == state)

        if jurisdiction:
            query = query.filter(Official.jurisdiction_level == jurisdiction)

        if richmond_focus:
            query = query.filter(
                (Official.county == "Richmond County") |
                (Official.borough == "Staten Island")
            )

        officials = query.limit(limit).all()

        return [
            {
                "id": str(official.id),
                "bioguide_id": official.bioguide_id,
                "name": official.full_name,
                "party": official.party,
                "state": official.state,
                "jurisdiction": official.jurisdiction_level,
                "county": official.county,
                "borough": official.borough,
                "congressional_district": official.congressional_district,
                "state_senate_district": official.state_senate_district,
                "state_assembly_district": official.state_assembly_district,
                "council_district": official.council_district,
                "profile_completeness": official.profile_completeness
            }
            for official in officials
        ]


async def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="Official Profiler - Comprehensive Political Analysis")

    parser.add_argument("--init-db", action="store_true",
                       help="Initialize database tables")
    parser.add_argument("--import-congress", type=int, default=118,
                       help="Import congressional members (default: 118th Congress)")
    parser.add_argument("--import-ny-state", type=int, default=2023,
                       help="Import NY State legislators (default: 2023 session)")
    parser.add_argument("--import-richmond-municipal", action="store_true",
                       help="Import Richmond County/Staten Island municipal officials")
    parser.add_argument("--profile", type=str,
                       help="Generate profile by bioguide ID or name")
    parser.add_argument("--format", choices=["html", "json", "pdf"], default="html",
                       help="Output format for profiles")
    parser.add_argument("--swot", type=str,
                       help="Run SWOT analysis by bioguide ID")
    parser.add_argument("--state-analysis", type=str,
                       help="Run state legislative analysis by official ID")
    parser.add_argument("--list-officials", action="store_true",
                       help="List current officials")
    parser.add_argument("--jurisdiction", choices=["federal", "state", "municipal", "county"],
                       help="Filter by jurisdiction level")
    parser.add_argument("--state", type=str,
                       help="Filter by state")
    parser.add_argument("--limit", type=int, default=20,
                       help="Limit number of results")
    parser.add_argument("--richmond-focus", action="store_true",
                       help="Focus on Richmond County/Staten Island officials")

    args = parser.parse_args()

    profiler = OfficialProfiler()

    try:
        await profiler.initialize()

        if args.init_db:
            await profiler.create_database_tables()
            print("Database tables created successfully")

        if args.import_congress:
            await profiler.import_congressional_members(args.import_congress)
            print(f"Congressional members imported for {args.import_congress}th Congress")

        if args.import_ny_state:
            await profiler.import_ny_state_members(args.import_ny_state)
            print(f"NY State legislators imported for {args.import_ny_state} session")

        if args.import_richmond_municipal:
            await profiler.import_richmond_municipal_officials()
            print("Richmond County/Staten Island municipal officials imported")

        if args.profile:
            # Determine if it's a bioguide ID or name
            if len(args.profile) == 7 and args.profile.isalpha():
                # Likely a bioguide ID
                filename = await profiler.generate_profile(
                    bioguide_id=args.profile,
                    output_format=args.format
                )
            else:
                # Likely a name
                filename = await profiler.generate_profile(
                    name=args.profile,
                    output_format=args.format
                )

            if filename:
                print(f"Profile generated: {filename}")
            else:
                print("Official not found")

        if args.swot:
            swot_result = await profiler.run_swot_analysis(bioguide_id=args.swot)
            if swot_result:
                print("\nSWOT Analysis Results:")
                print(f"Overall Rating: {swot_result.get('overall_assessment', {}).get('competitiveness_rating', 'Unknown')}")
                print(f"Strengths: {len(swot_result.get('strengths', []))}")
                print(f"Weaknesses: {len(swot_result.get('weaknesses', []))}")
                print(f"Opportunities: {len(swot_result.get('opportunities', []))}")
                print(f"Threats: {len(swot_result.get('threats', []))}")
            else:
                print("Official not found for SWOT analysis")

        if args.state_analysis:
            state_result = await profiler.run_state_analysis(args.state_analysis)
            if state_result:
                exec_summary = state_result.get("executive_summary", {})
                print("\nState Legislative Analysis Results:")
                print(f"Overall Assessment: {exec_summary.get('overall_assessment', 'Unknown')}")
                print(f"Priority Focus: {exec_summary.get('priority_focus', 'Unknown')}")
                print(f"Key Strengths: {', '.join(exec_summary.get('key_strengths', []))}")

                recommendations = state_result.get("recommendations", [])
                if recommendations:
                    print(f"\nTop Recommendations:")
                    for rec in recommendations[:3]:
                        print(f"- {rec.get('category')}: {rec.get('recommendation')}")
            else:
                print("Official not found for state analysis")

        if args.list_officials:
            officials = await profiler.list_officials(
                args.limit, args.state, args.jurisdiction, args.richmond_focus
            )
            print(f"\nCurrent Officials ({len(officials)} results):")
            print("-" * 100)
            for official in officials:
                # Build district info
                district_parts = []
                if official['congressional_district']:
                    district_parts.append(f"CD-{official['congressional_district']}")
                if official['state_senate_district']:
                    district_parts.append(f"SD-{official['state_senate_district']}")
                if official['state_assembly_district']:
                    district_parts.append(f"AD-{official['state_assembly_district']}")
                if official['council_district']:
                    district_parts.append(f"Council-{official['council_district']}")

                district_info = f" ({', '.join(district_parts)})" if district_parts else ""
                completeness = f"{official['profile_completeness']*100:.1f}%" if official['profile_completeness'] else "0.0%"

                jurisdiction_info = f"[{official['jurisdiction']}]" if official['jurisdiction'] else ""
                location_parts = []
                if official['borough']:
                    location_parts.append(official['borough'])
                if official['county']:
                    location_parts.append(official['county'])
                if official['state']:
                    location_parts.append(official['state'])
                location_info = ", ".join(location_parts)

                print(f"{official['name']} ({official['party']}) {jurisdiction_info}")
                print(f"  Location: {location_info}{district_info}")
                print(f"  ID: {official.get('bioguide_id', official['id'])} | Profile: {completeness} complete")
                print()

    except Exception as e:
        logger.error("Application error", error=str(e))
        print(f"Error: {str(e)}")
        return 1

    finally:
        await profiler.cleanup()

    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error("Fatal error", error=str(e))
        sys.exit(1)