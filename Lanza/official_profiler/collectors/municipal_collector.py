"""
Municipal government data collector for NYC and Richmond County officials.
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from bs4 import BeautifulSoup
import re
import json
from config.settings import settings
import structlog

logger = structlog.get_logger()


class MunicipalDataCollector:
    """Collector for municipal government data across NYC and Richmond County."""

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

    async def collect_richmond_county_officials(self) -> List[Dict]:
        """Collect Richmond County (Staten Island) municipal officials."""
        officials = []

        # NYC Mayor (serves Staten Island)
        mayor_data = await self.get_nyc_mayor_info()
        if mayor_data:
            officials.append(mayor_data)

        # Staten Island Borough President
        borough_president = await self.get_borough_president_info()
        if borough_president:
            officials.append(borough_president)

        # Staten Island City Council Members (Districts 49, 50, 51)
        council_members = await self.get_staten_island_council_members()
        officials.extend(council_members)

        # Richmond County DA
        da_info = await self.get_richmond_county_da()
        if da_info:
            officials.append(da_info)

        # Other county officials
        county_officials = await self.get_other_county_officials()
        officials.extend(county_officials)

        return officials

    async def get_nyc_mayor_info(self) -> Optional[Dict]:
        """Get NYC Mayor information."""
        try:
            url = "https://www1.nyc.gov/office-of-the-mayor/index.page"
            response = await self.client.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            mayor_info = {
                "position_type": "mayor",
                "jurisdiction_level": "municipal",
                "city": "New York City",
                "borough": "Citywide",
                "serves_richmond": True,
                "website": url,
                "data_source": "nyc_gov",
                "collected_at": datetime.now().isoformat()
            }

            # Try to extract mayor name
            title_element = soup.find("title")
            if title_element and "mayor" in title_element.text.lower():
                mayor_info["extracted_info"] = title_element.text

            # Look for mayor's name in page content
            name_patterns = [
                r"Mayor\s+([A-Z][a-z]+\s+[A-Z][a-z]+)",
                r"Mayor\s+([A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+)"
            ]

            for pattern in name_patterns:
                match = re.search(pattern, response.text)
                if match:
                    mayor_info["full_name"] = match.group(1)
                    break

            return mayor_info

        except Exception as e:
            logger.error("Failed to get NYC Mayor info", error=str(e))
            return None

    async def get_borough_president_info(self) -> Optional[Dict]:
        """Get Staten Island Borough President information."""
        try:
            url = "https://www.statenislandbp.org/"
            response = await self.client.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            bp_info = {
                "position_type": "borough_president",
                "jurisdiction_level": "borough",
                "borough": "Staten Island",
                "county": "Richmond County",
                "website": url,
                "data_source": "statenislandbp_org",
                "collected_at": datetime.now().isoformat()
            }

            # Try to extract borough president name from page
            # Look for common patterns
            name_selectors = [
                "h1", "h2", ".president-name", ".bp-name",
                "[class*='president']", "[class*='borough']"
            ]

            for selector in name_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if any(word in text.lower() for word in ['president', 'borough']):
                        bp_info["extracted_text"] = text
                        # Try to extract name
                        name_match = re.search(r'([A-Z][a-z]+\s+[A-Z][a-z]+)', text)
                        if name_match:
                            bp_info["full_name"] = name_match.group(1)
                        break

            return bp_info

        except Exception as e:
            logger.error("Failed to get Borough President info", error=str(e))
            return None

    async def get_staten_island_council_members(self) -> List[Dict]:
        """Get Staten Island City Council Members (Districts 49, 50, 51)."""
        council_members = []
        si_districts = ["49", "50", "51"]

        for district in si_districts:
            try:
                member_info = await self.get_council_member_by_district(district)
                if member_info:
                    council_members.append(member_info)
            except Exception as e:
                logger.error("Failed to get council member", district=district, error=str(e))

        return council_members

    async def get_council_member_by_district(self, district: str) -> Optional[Dict]:
        """Get NYC Council Member information by district."""
        try:
            # NYC Council website pattern
            url = f"https://council.nyc.gov/district-{district}/"
            response = await self.client.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            member_info = {
                "position_type": "city_council",
                "jurisdiction_level": "municipal",
                "district": district,
                "borough": "Staten Island",
                "county": "Richmond County",
                "website": url,
                "data_source": "nyc_council",
                "collected_at": datetime.now().isoformat()
            }

            # Try to extract council member name
            name_selectors = [
                ".council-member-name", ".member-name", "h1", "h2",
                "[class*='council']", "[class*='member']"
            ]

            for selector in name_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    # Look for names (avoid generic text)
                    if len(text) > 5 and len(text) < 50:
                        name_match = re.search(r'([A-Z][a-z]+\s+[A-Z][a-z]+)', text)
                        if name_match:
                            member_info["full_name"] = name_match.group(1)
                            break

            # Try to find contact information
            contact_elements = soup.find_all(text=re.compile(r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})|([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'))
            if contact_elements:
                member_info["contact_info"] = [elem.strip() for elem in contact_elements[:2]]

            return member_info

        except Exception as e:
            logger.error("Failed to get council member by district", district=district, error=str(e))
            return None

    async def get_richmond_county_da(self) -> Optional[Dict]:
        """Get Richmond County District Attorney information."""
        try:
            url = "https://www.statenislandda.org/"
            response = await self.client.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            da_info = {
                "position_type": "district_attorney",
                "jurisdiction_level": "county",
                "county": "Richmond County",
                "borough": "Staten Island",
                "website": url,
                "data_source": "statenislandda_org",
                "collected_at": datetime.now().isoformat()
            }

            # Try to extract DA name
            name_selectors = [
                ".da-name", ".district-attorney", "h1", "h2",
                "[class*='attorney']", "[class*='district']"
            ]

            for selector in name_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if 'district attorney' in text.lower() or 'da' in text.lower():
                        da_info["extracted_text"] = text
                        # Extract name
                        name_match = re.search(r'([A-Z][a-z]+\s+[A-Z][a-z]+)', text)
                        if name_match:
                            da_info["full_name"] = name_match.group(1)
                        break

            return da_info

        except Exception as e:
            logger.error("Failed to get Richmond County DA info", error=str(e))
            return None

    async def get_other_county_officials(self) -> List[Dict]:
        """Get other Richmond County officials."""
        officials = []

        # County Clerk
        clerk_info = await self.get_county_clerk_info()
        if clerk_info:
            officials.append(clerk_info)

        # Sheriff
        sheriff_info = await self.get_sheriff_info()
        if sheriff_info:
            officials.append(sheriff_info)

        # Surrogate Judge
        surrogate_info = await self.get_surrogate_info()
        if surrogate_info:
            officials.append(surrogate_info)

        return officials

    async def get_county_clerk_info(self) -> Optional[Dict]:
        """Get Richmond County Clerk information."""
        try:
            # Richmond County Clerk website
            url = "https://www.richmondcountyclerk.org/"
            response = await self.client.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            clerk_info = {
                "position_type": "county_clerk",
                "jurisdiction_level": "county",
                "county": "Richmond County",
                "borough": "Staten Island",
                "website": url,
                "data_source": "richmondcountyclerk_org",
                "collected_at": datetime.now().isoformat()
            }

            # Extract clerk name
            title_text = soup.find("title")
            if title_text:
                clerk_info["page_title"] = title_text.get_text()

            # Look for clerk name in content
            text_content = soup.get_text()
            clerk_patterns = [
                r'County Clerk\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
                r'Clerk\s+([A-Z][a-z]+\s+[A-Z][a-z]+)'
            ]

            for pattern in clerk_patterns:
                match = re.search(pattern, text_content)
                if match:
                    clerk_info["full_name"] = match.group(1)
                    break

            return clerk_info

        except Exception as e:
            logger.error("Failed to get County Clerk info", error=str(e))
            return None

    async def get_sheriff_info(self) -> Optional[Dict]:
        """Get Richmond County Sheriff information."""
        try:
            # Sheriff's office is typically part of NYPD in NYC
            # But Richmond County may have specific arrangements
            sheriff_info = {
                "position_type": "sheriff",
                "jurisdiction_level": "county",
                "county": "Richmond County",
                "borough": "Staten Island",
                "data_source": "manual_research_needed",
                "collected_at": datetime.now().isoformat(),
                "notes": "Richmond County Sheriff role may be integrated with NYPD"
            }

            return sheriff_info

        except Exception as e:
            logger.error("Failed to get Sheriff info", error=str(e))
            return None

    async def get_surrogate_info(self) -> Optional[Dict]:
        """Get Richmond County Surrogate information."""
        try:
            url = "https://www.nycourts.gov/courts/2jd/richmond/surrogate/"
            response = await self.client.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            surrogate_info = {
                "position_type": "surrogate",
                "jurisdiction_level": "county",
                "county": "Richmond County",
                "borough": "Staten Island",
                "website": url,
                "data_source": "nycourts_gov",
                "collected_at": datetime.now().isoformat()
            }

            # Extract surrogate name from page
            text_content = soup.get_text()
            surrogate_patterns = [
                r'Surrogate\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
                r'Judge\s+([A-Z][a-z]+\s+[A-Z][a-z]+)'
            ]

            for pattern in surrogate_patterns:
                match = re.search(pattern, text_content)
                if match:
                    surrogate_info["full_name"] = match.group(1)
                    break

            return surrogate_info

        except Exception as e:
            logger.error("Failed to get Surrogate info", error=str(e))
            return None

    async def collect_municipal_press_releases(self, official_data: Dict) -> List[Dict]:
        """Collect press releases from municipal websites."""
        press_releases = []

        try:
            position_type = official_data.get("position_type")
            website = official_data.get("website")

            if not website:
                return press_releases

            # Navigate to press/news section
            press_urls = await self._find_press_release_urls(website)

            for press_url in press_urls[:10]:  # Limit to 10 most recent
                release_data = await self._scrape_press_release(press_url)
                if release_data:
                    release_data["official_data"] = official_data
                    press_releases.append(release_data)

        except Exception as e:
            logger.error("Failed to collect municipal press releases",
                        official=official_data.get("full_name"), error=str(e))

        return press_releases

    async def _find_press_release_urls(self, base_url: str) -> List[str]:
        """Find press release URLs from a municipal website."""
        press_urls = []

        try:
            response = await self.client.get(base_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for press/news links
            press_keywords = [
                'press', 'news', 'releases', 'announcements',
                'statements', 'media', 'updates'
            ]

            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                text = link.get_text().lower()

                if any(keyword in text or keyword in href.lower() for keyword in press_keywords):
                    if href.startswith('/'):
                        full_url = base_url.rstrip('/') + href
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        continue

                    press_urls.append(full_url)

        except Exception as e:
            logger.error("Failed to find press release URLs", base_url=base_url, error=str(e))

        return press_urls[:5]  # Return up to 5 URLs

    async def _scrape_press_release(self, url: str) -> Optional[Dict]:
        """Scrape individual press release."""
        try:
            response = await self.client.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract press release data
            release_data = {
                "url": url,
                "scraped_at": datetime.now().isoformat(),
                "title": "",
                "date": None,
                "content": "",
                "summary": ""
            }

            # Extract title
            title_selectors = ["h1", "h2", ".title", ".headline", "[class*='title']"]
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    release_data["title"] = title_element.get_text(strip=True)
                    break

            # Extract date
            date_patterns = [
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{1,2}-\d{1,2}-\d{4})',
                r'([A-Z][a-z]{2,8}\s+\d{1,2},?\s+\d{4})'
            ]

            page_text = soup.get_text()
            for pattern in date_patterns:
                date_match = re.search(pattern, page_text)
                if date_match:
                    release_data["date"] = date_match.group(1)
                    break

            # Extract content
            content_selectors = [
                ".content", ".body", ".article-body", "main",
                "[class*='content']", "[class*='body']"
            ]

            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    release_data["content"] = content_element.get_text(strip=True)
                    break

            if not release_data["content"]:
                # Fallback to all text
                release_data["content"] = soup.get_text()

            # Create summary (first 200 characters)
            if release_data["content"]:
                release_data["summary"] = release_data["content"][:200] + "..."

            return release_data

        except Exception as e:
            logger.error("Failed to scrape press release", url=url, error=str(e))
            return None

    async def get_municipal_voting_records(self, official_data: Dict) -> List[Dict]:
        """Get municipal voting records where available."""
        voting_records = []

        position_type = official_data.get("position_type")

        if position_type == "city_council":
            # NYC Council voting records
            district = official_data.get("district")
            if district:
                council_votes = await self._get_nyc_council_votes(district)
                voting_records.extend(council_votes)

        return voting_records

    async def _get_nyc_council_votes(self, district: str) -> List[Dict]:
        """Get NYC Council voting records for a district."""
        try:
            # NYC Council has an API for legislation/votes
            # This is a simplified implementation
            url = f"https://webapi.legistar.com/v1/nyc/matters"
            params = {"$filter": f"MatterBodyName eq 'City Council'"}

            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return data[:20]  # Return first 20 matters
            else:
                return []

        except Exception as e:
            logger.error("Failed to get NYC Council votes", district=district, error=str(e))
            return []

    async def collect_comprehensive_municipal_data(self, jurisdiction_config: Dict) -> Dict:
        """Collect comprehensive municipal data for a jurisdiction."""
        municipal_data = {
            "jurisdiction": jurisdiction_config.get("name"),
            "collection_date": datetime.now().isoformat(),
            "officials": [],
            "press_releases": [],
            "voting_records": [],
            "municipal_issues": {},
            "data_sources": []
        }

        try:
            # Collect officials
            if jurisdiction_config.get("name") == "Richmond County":
                officials = await self.collect_richmond_county_officials()
                municipal_data["officials"] = officials

                # Collect additional data for each official
                for official in officials:
                    # Press releases
                    press_releases = await self.collect_municipal_press_releases(official)
                    municipal_data["press_releases"].extend(press_releases)

                    # Voting records
                    voting_records = await self.get_municipal_voting_records(official)
                    municipal_data["voting_records"].extend(voting_records)

            # Track data sources used
            municipal_data["data_sources"] = [
                "nyc_gov", "statenislandbp_org", "nyc_council",
                "statenislandda_org", "richmondcountyclerk_org",
                "nycourts_gov"
            ]

        except Exception as e:
            logger.error("Failed to collect comprehensive municipal data", error=str(e))
            municipal_data["error"] = str(e)

        return municipal_data