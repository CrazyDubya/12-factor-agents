"""
New York State Legislature API client for state-level data collection.
"""
import httpx
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
from config.settings import settings
import structlog

logger = structlog.get_logger()


class NYStateAPI:
    """Client for New York State Legislature data."""

    SENATE_BASE_URL = "https://www.nysenate.gov"
    ASSEMBLY_BASE_URL = "https://nyassembly.gov"
    OPEN_LEGISLATION_API = "https://legislation.nysenate.gov/api/3"

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=settings.REQUEST_TIMEOUT,
            headers={
                "User-Agent": "Official Profiler Research Tool - Academic Use Only"
            }
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def _make_request(self, url: str, params: Dict[str, Any] = None) -> Dict:
        """Make authenticated request to NY State APIs."""
        # Add API key to params for Open Legislation API
        if not params:
            params = {}

        if self.OPEN_LEGISLATION_API in url:
            params["key"] = settings.NYS_OPEN_LEG_API_KEY

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json() if 'json' in response.headers.get('content-type', '') else {"html": response.text}
        except httpx.HTTPStatusError as e:
            logger.error("NY State API error", status_code=e.response.status_code, url=url)
            raise
        except Exception as e:
            logger.error("Request failed", error=str(e), url=url)
            raise

    async def get_senate_members(self, session_year: int = 2023) -> List[Dict]:
        """Get all NY State Senate members for a session."""
        url = f"{self.OPEN_LEGISLATION_API}/members/{session_year}"

        try:
            data = await self._make_request(url)
            members = data.get("result", {}).get("items", [])

            senate_members = []
            for member in members:
                if member.get("chamber") == "SENATE":
                    senate_members.append({
                        "member_id": member.get("memberId"),
                        "session_member_id": member.get("sessionMemberId"),
                        "full_name": member.get("fullName"),
                        "first_name": member.get("firstName"),
                        "last_name": member.get("lastName"),
                        "district_code": member.get("districtCode"),
                        "chamber": member.get("chamber"),
                        "incumbent": member.get("incumbent", True),
                        "session_year": session_year
                    })

            return senate_members
        except Exception as e:
            logger.error("Failed to get Senate members", error=str(e))
            return []

    async def get_assembly_members(self, session_year: int = 2023) -> List[Dict]:
        """Get all NY State Assembly members for a session."""
        url = f"{self.OPEN_LEGISLATION_API}/members/{session_year}"

        try:
            data = await self._make_request(url)
            members = data.get("result", {}).get("items", [])

            assembly_members = []
            for member in members:
                if member.get("chamber") == "ASSEMBLY":
                    assembly_members.append({
                        "member_id": member.get("memberId"),
                        "session_member_id": member.get("sessionMemberId"),
                        "full_name": member.get("fullName"),
                        "first_name": member.get("firstName"),
                        "last_name": member.get("lastName"),
                        "district_code": member.get("districtCode"),
                        "chamber": member.get("chamber"),
                        "incumbent": member.get("incumbent", True),
                        "session_year": session_year
                    })

            return assembly_members
        except Exception as e:
            logger.error("Failed to get Assembly members", error=str(e))
            return []

    async def get_member_details(self, member_id: str, session_year: int = 2023) -> Dict:
        """Get detailed information about a specific member."""
        url = f"{self.OPEN_LEGISLATION_API}/members/{session_year}/{member_id}"

        try:
            data = await self._make_request(url)
            member_data = data.get("result", {})

            return {
                "member_id": member_data.get("memberId"),
                "full_name": member_data.get("fullName"),
                "first_name": member_data.get("firstName"),
                "last_name": member_data.get("lastName"),
                "district_code": member_data.get("districtCode"),
                "chamber": member_data.get("chamber"),
                "incumbent": member_data.get("incumbent"),
                "email": member_data.get("email"),
                "website": member_data.get("website"),
                "image_name": member_data.get("imgName"),
                "session_year": session_year
            }
        except Exception as e:
            logger.error("Failed to get member details", member_id=member_id, error=str(e))
            return {}

    async def get_member_votes(self, member_id: str, session_year: int = 2023,
                             limit: int = 100) -> List[Dict]:
        """Get voting record for a NY State legislator."""
        url = f"{self.OPEN_LEGISLATION_API}/members/{session_year}/{member_id}/votes"
        params = {"limit": limit}

        try:
            data = await self._make_request(url, params)
            votes = data.get("result", {}).get("items", [])

            processed_votes = []
            for vote in votes:
                vote_info = vote.get("vote", {})
                bill_info = vote_info.get("bill", {})

                processed_votes.append({
                    "vote_id": vote_info.get("voteId"),
                    "vote_date": vote_info.get("voteDate"),
                    "vote_type": vote_info.get("voteType"),
                    "member_vote": vote_info.get("memberVotes", {}).get(member_id, {}).get("voteCode"),
                    "bill_id": bill_info.get("basePrintNo"),
                    "bill_session": bill_info.get("session"),
                    "bill_title": bill_info.get("title"),
                    "bill_summary": bill_info.get("summary"),
                    "committee": vote_info.get("committee"),
                    "session_year": session_year
                })

            return processed_votes
        except Exception as e:
            logger.error("Failed to get member votes", member_id=member_id, error=str(e))
            return []

    async def get_bill_details(self, bill_id: str, session_year: int = 2023) -> Dict:
        """Get detailed information about a NY State bill."""
        url = f"{self.OPEN_LEGISLATION_API}/bills/{session_year}/{bill_id}"

        try:
            data = await self._make_request(url)
            bill_data = data.get("result", {})

            return {
                "bill_id": bill_data.get("basePrintNo"),
                "session": bill_data.get("session"),
                "bill_type": bill_data.get("billType"),
                "title": bill_data.get("title"),
                "summary": bill_data.get("summary"),
                "law_section": bill_data.get("lawSection"),
                "law_code": bill_data.get("lawCode"),
                "sponsor": bill_data.get("sponsor", {}).get("member", {}).get("fullName"),
                "sponsor_district": bill_data.get("sponsor", {}).get("member", {}).get("districtCode"),
                "status": bill_data.get("status", {}).get("statusDesc"),
                "introduced_date": bill_data.get("introducedDate"),
                "actions": bill_data.get("actions", {}).get("items", []),
                "votes": bill_data.get("votes", {}).get("items", [])
            }
        except Exception as e:
            logger.error("Failed to get bill details", bill_id=bill_id, error=str(e))
            return {}

    async def get_member_sponsored_bills(self, member_id: str, session_year: int = 2023,
                                       limit: int = 100) -> List[Dict]:
        """Get bills sponsored by a NY State legislator."""
        url = f"{self.OPEN_LEGISLATION_API}/bills/{session_year}/search"
        params = {
            "term": f"sponsor.member.memberId:{member_id}",
            "sort": "introduced_date:desc",
            "limit": limit
        }

        try:
            data = await self._make_request(url, params)
            bills = data.get("result", {}).get("items", [])

            sponsored_bills = []
            for bill in bills:
                bill_data = bill.get("result", {})
                sponsored_bills.append({
                    "bill_id": bill_data.get("basePrintNo"),
                    "session": bill_data.get("session"),
                    "title": bill_data.get("title"),
                    "summary": bill_data.get("summary"),
                    "introduced_date": bill_data.get("introducedDate"),
                    "status": bill_data.get("status", {}).get("statusDesc"),
                    "law_section": bill_data.get("lawSection"),
                    "co_sponsors": [
                        cosponsor.get("member", {}).get("fullName")
                        for cosponsor in bill_data.get("coSponsors", {}).get("items", [])
                    ]
                })

            return sponsored_bills
        except Exception as e:
            logger.error("Failed to get sponsored bills", member_id=member_id, error=str(e))
            return []

    async def get_committee_assignments(self, session_year: int = 2023) -> List[Dict]:
        """Get committee assignments for NY State Legislature."""
        url = f"{self.OPEN_LEGISLATION_API}/committees/{session_year}"

        try:
            data = await self._make_request(url)
            committees = data.get("result", {}).get("items", [])

            committee_assignments = []
            for committee in committees:
                committee_data = committee.get("committee", {})
                committee_assignments.append({
                    "committee_name": committee_data.get("name"),
                    "chamber": committee_data.get("chamber"),
                    "chair": committee_data.get("chair", {}).get("fullName"),
                    "chair_district": committee_data.get("chair", {}).get("districtCode"),
                    "members": [
                        {
                            "name": member.get("fullName"),
                            "district": member.get("districtCode"),
                            "title": member.get("title", "Member")
                        }
                        for member in committee_data.get("members", {}).get("items", [])
                    ],
                    "session_year": session_year
                })

            return committee_assignments
        except Exception as e:
            logger.error("Failed to get committee assignments", error=str(e))
            return []

    async def search_legislation(self, query: str, session_year: int = 2023,
                               chamber: str = None, limit: int = 50) -> List[Dict]:
        """Search NY State legislation."""
        url = f"{self.OPEN_LEGISLATION_API}/bills/{session_year}/search"
        params = {
            "term": query,
            "sort": "introduced_date:desc",
            "limit": limit
        }

        if chamber:
            params["term"] += f" AND chamber:{chamber}"

        try:
            data = await self._make_request(url, params)
            bills = data.get("result", {}).get("items", [])

            search_results = []
            for bill in bills:
                bill_data = bill.get("result", {})
                search_results.append({
                    "bill_id": bill_data.get("basePrintNo"),
                    "session": bill_data.get("session"),
                    "title": bill_data.get("title"),
                    "summary": bill_data.get("summary")[:200] + "..." if bill_data.get("summary") else "",
                    "sponsor": bill_data.get("sponsor", {}).get("member", {}).get("fullName"),
                    "introduced_date": bill_data.get("introducedDate"),
                    "status": bill_data.get("status", {}).get("statusDesc")
                })

            return search_results
        except Exception as e:
            logger.error("Failed to search legislation", query=query, error=str(e))
            return []

    async def get_richmond_county_legislators(self, session_year: int = 2023) -> List[Dict]:
        """Get legislators specifically representing Richmond County (Staten Island)."""
        # Richmond County Senate District is 24 (wholly contained), Assembly districts are 61, 62, 63, 64
        richmond_legislators = []

        # Get Senate members
        senate_members = await self.get_senate_members(session_year)
        for member in senate_members:
            if member.get("district_code") == "24":  # Senate District 24 (wholly contained)
                member_details = await self.get_member_details(member["member_id"], session_year)
                member_details["jurisdiction"] = "state_senate"
                member_details["represents_richmond"] = True
                member_details["wholly_contained"] = True
                richmond_legislators.append(member_details)

        # Get Assembly members
        assembly_members = await self.get_assembly_members(session_year)
        richmond_assembly_districts = ["61", "62", "63", "64"]
        for member in assembly_members:
            if member.get("district_code") in richmond_assembly_districts:
                member_details = await self.get_member_details(member["member_id"], session_year)
                member_details["jurisdiction"] = "state_assembly"
                member_details["represents_richmond"] = True
                richmond_legislators.append(member_details)

        return richmond_legislators

    async def get_member_press_releases(self, member_id: str, chamber: str) -> List[Dict]:
        """Scrape press releases from member's official page."""
        press_releases = []

        try:
            if chamber.upper() == "SENATE":
                # Senate press releases are typically on nysenate.gov
                base_url = f"{self.SENATE_BASE_URL}/newsroom/press-releases"
                # This would need specific scraping logic for Senate press releases
            elif chamber.upper() == "ASSEMBLY":
                # Assembly press releases are on nyassembly.gov
                base_url = f"{self.ASSEMBLY_BASE_URL}/press-releases"
                # This would need specific scraping logic for Assembly press releases

            # Placeholder for actual scraping implementation
            # Would need to parse HTML pages for press releases

        except Exception as e:
            logger.error("Failed to get press releases", member_id=member_id, error=str(e))

        return press_releases


class NYCDataCollector:
    """Collector for NYC municipal data (Mayor, City Council, Borough Presidents)."""

    NYC_COUNCIL_API = "https://council.nyc.gov"
    NYC_GOV_API = "https://www1.nyc.gov"

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=settings.REQUEST_TIMEOUT,
            headers={
                "User-Agent": "Official Profiler Research Tool - Academic Use Only"
            }
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def get_council_members(self) -> List[Dict]:
        """Get NYC Council members."""
        # NYC Council has 51 districts
        # Staten Island has districts 49, 50, 51
        council_members = []

        # This would implement actual NYC Council API calls
        # For now, focusing on Staten Island districts
        staten_island_districts = ["49", "50", "51"]

        for district in staten_island_districts:
            member_data = {
                "district": district,
                "borough": "Staten Island",
                "jurisdiction": "municipal",
                "position_type": "city_council"
            }
            council_members.append(member_data)

        return council_members

    async def get_borough_president(self) -> Dict:
        """Get Staten Island Borough President information."""
        return {
            "borough": "Staten Island",
            "position_type": "borough_president",
            "jurisdiction": "municipal"
        }

    async def get_mayor_info(self) -> Dict:
        """Get NYC Mayor information."""
        return {
            "city": "New York City",
            "position_type": "mayor",
            "jurisdiction": "municipal"
        }