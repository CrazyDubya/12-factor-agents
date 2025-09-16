"""
Congress.gov API client for collecting legislative data.
"""
import httpx
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from config.settings import settings
import structlog

logger = structlog.get_logger()


class CongressAPI:
    """Client for Congress.gov API."""

    BASE_URL = "https://api.congress.gov/v3"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.CONGRESS_API_KEY
        self.client = httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _build_headers(self) -> Dict[str, str]:
        """Build request headers with API key."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict:
        """Make authenticated request to Congress API."""
        url = f"{self.BASE_URL}/{endpoint}"
        headers = self._build_headers()

        try:
            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error("Congress API error", status_code=e.response.status_code, endpoint=endpoint)
            raise
        except Exception as e:
            logger.error("Request failed", error=str(e), endpoint=endpoint)
            raise

    async def get_members(self, congress: int = 118, chamber: str = "all") -> List[Dict]:
        """Get list of congress members."""
        endpoint = f"member/{congress}/{chamber}"
        params = {"format": "json", "limit": 250}

        data = await self._make_request(endpoint, params)
        return data.get("members", [])

    async def get_member_details(self, bioguide_id: str) -> Dict:
        """Get detailed information about a specific member."""
        endpoint = f"member/{bioguide_id}"
        params = {"format": "json"}

        data = await self._make_request(endpoint, params)
        return data.get("member", {})

    async def get_member_votes(self, bioguide_id: str, congress: int = 118,
                             limit: int = 250) -> List[Dict]:
        """Get voting record for a member."""
        endpoint = f"member/{bioguide_id}/votes"
        params = {
            "format": "json",
            "limit": limit,
            "fromDateTime": (datetime.now() - timedelta(days=365)).isoformat()
        }

        data = await self._make_request(endpoint, params)
        return data.get("votes", [])

    async def get_member_sponsored_legislation(self, bioguide_id: str,
                                             congress: int = 118) -> List[Dict]:
        """Get bills sponsored by a member."""
        endpoint = f"member/{bioguide_id}/sponsored-legislation"
        params = {"format": "json", "limit": 250}

        data = await self._make_request(endpoint, params)
        return data.get("sponsoredLegislation", [])

    async def get_bill_details(self, congress: int, bill_type: str, bill_number: int) -> Dict:
        """Get detailed information about a bill."""
        endpoint = f"bill/{congress}/{bill_type}/{bill_number}"
        params = {"format": "json"}

        data = await self._make_request(endpoint, params)
        return data.get("bill", {})

    async def get_recent_bills(self, congress: int = 118, limit: int = 250) -> List[Dict]:
        """Get recently introduced bills."""
        endpoint = f"bill/{congress}"
        params = {
            "format": "json",
            "limit": limit,
            "sort": "updateDate+desc"
        }

        data = await self._make_request(endpoint, params)
        return data.get("bills", [])

    async def get_committee_assignments(self, congress: int = 118,
                                      chamber: str = "house") -> List[Dict]:
        """Get committee assignments for a congress."""
        endpoint = f"committee/{congress}/{chamber}"
        params = {"format": "json", "limit": 250}

        data = await self._make_request(endpoint, params)
        return data.get("committees", [])

    async def search_congress_data(self, query: str,
                                 content_type: str = "bill") -> List[Dict]:
        """Search Congress.gov data."""
        endpoint = "search"
        params = {
            "format": "json",
            "query": query,
            "contentType": content_type,
            "limit": 100
        }

        data = await self._make_request(endpoint, params)
        return data.get("results", [])