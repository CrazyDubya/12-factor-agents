"""
Web scrapers for collecting data from government and official websites.
"""
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import httpx
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from config.settings import settings
import structlog

logger = structlog.get_logger()


class GovernmentScraper:
    """Base class for scraping government websites."""

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=settings.REQUEST_TIMEOUT,
            headers={
                "User-Agent": "Official Profiler Research Tool - Academic Use Only"
            }
        )
        self.delay = settings.SCRAPE_DELAY

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch a web page with error handling."""
        try:
            await asyncio.sleep(self.delay)  # Rate limiting
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error("Failed to fetch page", url=url, error=str(e))
            return None

    def _parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content with BeautifulSoup."""
        return BeautifulSoup(html, 'lxml')


class CongressWebScraper(GovernmentScraper):
    """Scraper for additional congressional data not available via API."""

    HOUSE_BASE_URL = "https://www.house.gov"
    SENATE_BASE_URL = "https://www.senate.gov"

    async def scrape_member_bio_page(self, bioguide_id: str, chamber: str) -> Dict:
        """Scrape detailed biography from member's official page."""
        bio_data = {
            "bioguide_id": bioguide_id,
            "chamber": chamber,
            "scraped_at": datetime.now().isoformat(),
            "education": [],
            "career_history": [],
            "family_info": {},
            "awards": [],
            "additional_info": {}
        }

        # Construct member page URL based on chamber
        if chamber.lower() == "house":
            # House members have varied URL patterns, would need member directory lookup
            member_url = await self._find_house_member_url(bioguide_id)
        else:  # Senate
            member_url = await self._find_senate_member_url(bioguide_id)

        if not member_url:
            return bio_data

        html = await self._fetch_page(member_url)
        if not html:
            return bio_data

        soup = self._parse_html(html)

        # Extract education information
        education_section = soup.find(text=re.compile(r"Education", re.I))
        if education_section:
            education_parent = education_section.find_parent()
            if education_parent:
                bio_data["education"] = self._extract_education(education_parent)

        # Extract career history
        career_keywords = ["Career", "Professional Experience", "Work Experience"]
        for keyword in career_keywords:
            career_section = soup.find(text=re.compile(keyword, re.I))
            if career_section:
                career_parent = career_section.find_parent()
                if career_parent:
                    bio_data["career_history"] = self._extract_career_history(career_parent)
                    break

        # Extract committee assignments (current)
        committee_section = soup.find(text=re.compile(r"Committee", re.I))
        if committee_section:
            committees = self._extract_committees(soup)
            bio_data["additional_info"]["current_committees"] = committees

        return bio_data

    async def _find_house_member_url(self, bioguide_id: str) -> Optional[str]:
        """Find House member's official page URL."""
        # House directory search - would need to implement member lookup
        directory_url = f"{self.HOUSE_BASE_URL}/representatives/find-your-representative"
        # This is a placeholder - actual implementation would search the directory
        return None

    async def _find_senate_member_url(self, bioguide_id: str) -> Optional[str]:
        """Find Senate member's official page URL."""
        # Senate directory search
        directory_url = f"{self.SENATE_BASE_URL}/senators"
        # This is a placeholder - actual implementation would search the directory
        return None

    def _extract_education(self, section) -> List[Dict]:
        """Extract education information from HTML section."""
        education = []
        # Look for degree patterns
        text = section.get_text()
        degree_patterns = [
            r"(B\.?A\.?|Bachelor of Arts|Bachelor's)",
            r"(B\.?S\.?|Bachelor of Science)",
            r"(M\.?A\.?|Master of Arts|Master's)",
            r"(M\.?S\.?|Master of Science)",
            r"(Ph\.?D\.?|Doctor of Philosophy|Doctorate)",
            r"(J\.?D\.?|Juris Doctor|Law Degree)"
        ]

        for pattern in degree_patterns:
            matches = re.finditer(pattern, text, re.I)
            for match in matches:
                # Try to extract surrounding context for school name
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].strip()
                education.append({
                    "degree_type": match.group(1),
                    "context": context,
                    "raw_match": match.group(0)
                })

        return education

    def _extract_career_history(self, section) -> List[Dict]:
        """Extract career history from HTML section."""
        career = []
        text = section.get_text()

        # Look for job title patterns
        job_patterns = [
            r"(CEO|President|Vice President|Director|Manager|Attorney|Lawyer|Professor|Teacher)",
            r"(Senator|Representative|Governor|Mayor|Judge|Prosecutor)",
            r"(Owner|Founder|Partner|Executive|Administrator)"
        ]

        for pattern in job_patterns:
            matches = re.finditer(pattern, text, re.I)
            for match in matches:
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end].strip()
                career.append({
                    "position_type": match.group(1),
                    "context": context,
                    "raw_match": match.group(0)
                })

        return career

    def _extract_committees(self, soup: BeautifulSoup) -> List[str]:
        """Extract committee assignments from page."""
        committees = []
        committee_links = soup.find_all("a", href=re.compile(r"committee", re.I))

        for link in committee_links:
            committee_name = link.get_text().strip()
            if len(committee_name) > 10 and "committee" in committee_name.lower():
                committees.append(committee_name)

        return list(set(committees))  # Remove duplicates


class PressReleaseScraper(GovernmentScraper):
    """Scraper for press releases and official statements."""

    async def scrape_senate_press_releases(self, senator_name: str,
                                         limit: int = 50) -> List[Dict]:
        """Scrape press releases from Senate.gov."""
        press_releases = []
        search_url = f"{CongressWebScraper.SENATE_BASE_URL}/search"

        # This would need to implement the actual search mechanism
        # Senate.gov has a search interface that could be automated

        return press_releases

    async def scrape_house_press_releases(self, representative_name: str,
                                        limit: int = 50) -> List[Dict]:
        """Scrape press releases from House.gov."""
        press_releases = []
        # Similar implementation for House press releases
        return press_releases


class CSpanScraper(GovernmentScraper):
    """Scraper for C-SPAN video archives and transcripts."""

    CSPAN_BASE_URL = "https://www.c-span.org"

    async def search_cspan_appearances(self, official_name: str,
                                     days_back: int = 90) -> List[Dict]:
        """Search for C-SPAN appearances by an official."""
        appearances = []

        search_url = f"{self.CSPAN_BASE_URL}/search/"
        params = {
            "searchtype": "Videos",
            "query": official_name,
            "sort": "Most+Recent"
        }

        # This would implement the actual C-SPAN search
        # C-SPAN has a search API that could be used

        return appearances

    async def get_video_transcript(self, video_id: str) -> Optional[Dict]:
        """Get transcript for a specific C-SPAN video."""
        transcript_url = f"{self.CSPAN_BASE_URL}/video/{video_id}/transcript"

        html = await self._fetch_page(transcript_url)
        if not html:
            return None

        soup = self._parse_html(html)

        transcript_data = {
            "video_id": video_id,
            "scraped_at": datetime.now().isoformat(),
            "speakers": [],
            "full_text": "",
            "timestamps": []
        }

        # Extract transcript content
        transcript_container = soup.find("div", class_="transcript-container")
        if transcript_container:
            # Parse speakers and timestamps
            speaker_segments = transcript_container.find_all("div", class_="speaker-segment")

            for segment in speaker_segments:
                timestamp = segment.find("span", class_="timestamp")
                speaker = segment.find("span", class_="speaker")
                text = segment.find("div", class_="text")

                if all([timestamp, speaker, text]):
                    segment_data = {
                        "timestamp": timestamp.get_text().strip(),
                        "speaker": speaker.get_text().strip(),
                        "text": text.get_text().strip()
                    }
                    transcript_data["timestamps"].append(segment_data)

            # Combine all text
            transcript_data["full_text"] = " ".join([
                seg["text"] for seg in transcript_data["timestamps"]
            ])

            # Extract unique speakers
            transcript_data["speakers"] = list(set([
                seg["speaker"] for seg in transcript_data["timestamps"]
            ]))

        return transcript_data


class PlaywrightScraper:
    """Advanced scraper using Playwright for dynamic content."""

    async def scrape_with_playwright(self, url: str, wait_selector: str = None) -> Dict:
        """Scrape dynamic content using Playwright."""
        result = {
            "url": url,
            "scraped_at": datetime.now().isoformat(),
            "content": "",
            "links": [],
            "images": []
        }

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(url, wait_until="networkidle")

                # Wait for specific element if provided
                if wait_selector:
                    await page.wait_for_selector(wait_selector, timeout=10000)

                # Extract content
                result["content"] = await page.content()

                # Extract links
                links = await page.query_selector_all("a")
                result["links"] = [
                    {
                        "text": await link.text_content(),
                        "href": await link.get_attribute("href")
                    }
                    for link in links if await link.get_attribute("href")
                ]

                # Extract images
                images = await page.query_selector_all("img")
                result["images"] = [
                    {
                        "alt": await img.get_attribute("alt"),
                        "src": await img.get_attribute("src")
                    }
                    for img in images if await img.get_attribute("src")
                ]

            except Exception as e:
                logger.error("Playwright scraping failed", url=url, error=str(e))
            finally:
                await browser.close()

        return result