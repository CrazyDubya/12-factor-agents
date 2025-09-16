"""
Federal Election Commission (FEC) API client for campaign finance data.
"""
import httpx
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from config.settings import settings
import structlog

logger = structlog.get_logger()


class FECAPI:
    """Client for FEC API (OpenFEC)."""

    BASE_URL = "https://api.open.fec.gov/v1"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict:
        """Make request to FEC API."""
        url = f"{self.BASE_URL}/{endpoint}"
        default_params = {"format": "json", "per_page": 100}
        if params:
            default_params.update(params)

        try:
            response = await self.client.get(url, params=default_params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error("FEC API error", status_code=e.response.status_code, endpoint=endpoint)
            raise
        except Exception as e:
            logger.error("Request failed", error=str(e), endpoint=endpoint)
            raise

    async def get_candidate_info(self, candidate_id: str) -> Dict:
        """Get candidate information by FEC ID."""
        endpoint = f"candidates/{candidate_id}"
        data = await self._make_request(endpoint)
        results = data.get("results", [])
        return results[0] if results else {}

    async def search_candidates(self, name: str, office: str = None,
                              state: str = None, district: str = None) -> List[Dict]:
        """Search for candidates by name."""
        params = {"name": name}
        if office:
            params["office"] = office.upper()
        if state:
            params["state"] = state.upper()
        if district:
            params["district"] = district

        endpoint = "candidates/search"
        data = await self._make_request(endpoint, params)
        return data.get("results", [])

    async def get_candidate_committees(self, candidate_id: str) -> List[Dict]:
        """Get committees associated with a candidate."""
        endpoint = f"candidate/{candidate_id}/committees"
        data = await self._make_request(endpoint)
        return data.get("results", [])

    async def get_candidate_totals(self, candidate_id: str, cycle: int = 2024) -> Dict:
        """Get financial totals for a candidate."""
        endpoint = f"candidate/{candidate_id}/totals"
        params = {"cycle": cycle}
        data = await self._make_request(endpoint, params)
        results = data.get("results", [])
        return results[0] if results else {}

    async def get_committee_info(self, committee_id: str) -> Dict:
        """Get committee information."""
        endpoint = f"committees/{committee_id}"
        data = await self._make_request(endpoint)
        results = data.get("results", [])
        return results[0] if results else {}

    async def get_committee_filings(self, committee_id: str,
                                  form_type: str = None) -> List[Dict]:
        """Get filings for a committee."""
        params = {"committee_id": committee_id}
        if form_type:
            params["form_type"] = form_type

        endpoint = "filings"
        data = await self._make_request(endpoint, params)
        return data.get("results", [])

    async def get_individual_contributions(self, committee_id: str,
                                         min_amount: float = None,
                                         contributor_name: str = None) -> List[Dict]:
        """Get individual contributions to a committee."""
        params = {"committee_id": committee_id}
        if min_amount:
            params["min_amount"] = min_amount
        if contributor_name:
            params["contributor_name"] = contributor_name

        endpoint = "schedules/schedule_a"
        data = await self._make_request(endpoint, params)
        return data.get("results", [])

    async def get_disbursements(self, committee_id: str,
                              recipient_name: str = None) -> List[Dict]:
        """Get disbursements from a committee."""
        params = {"committee_id": committee_id}
        if recipient_name:
            params["recipient_name"] = recipient_name

        endpoint = "schedules/schedule_b"
        data = await self._make_request(endpoint, params)
        return data.get("results", [])

    async def get_election_results(self, office: str, state: str = None,
                                 district: str = None, cycle: int = 2022) -> List[Dict]:
        """Get election results."""
        params = {
            "office": office.upper(),
            "cycle": cycle
        }
        if state:
            params["state"] = state.upper()
        if district:
            params["district"] = district

        endpoint = "elections"
        data = await self._make_request(endpoint, params)
        return data.get("results", [])

    async def get_financial_summary(self, candidate_id: str,
                                  cycle: int = 2024) -> Dict:
        """Get comprehensive financial summary for a candidate."""
        summary = {}

        # Get candidate totals
        summary["totals"] = await self.get_candidate_totals(candidate_id, cycle)

        # Get associated committees
        committees = await self.get_candidate_committees(candidate_id)
        summary["committees"] = committees

        # Get major contributions for primary committee
        if committees:
            primary_committee = committees[0]["committee_id"]
            contributions = await self.get_individual_contributions(
                primary_committee, min_amount=1000
            )
            summary["major_contributions"] = contributions[:50]  # Top 50

            disbursements = await self.get_disbursements(primary_committee)
            summary["disbursements"] = disbursements[:50]  # Top 50

        return summary