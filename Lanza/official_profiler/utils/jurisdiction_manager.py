"""
Multi-level jurisdiction management system for flexible geographic configuration.
"""
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import structlog
from config.settings import settings

logger = structlog.get_logger()


class JurisdictionLevel(Enum):
    FEDERAL = "federal"
    STATE = "state"
    COUNTY = "county"
    MUNICIPAL = "municipal"
    BOROUGH = "borough"  # For NYC-style boroughs
    DISTRICT = "district"  # For special districts


@dataclass
class JurisdictionConfig:
    """Configuration for a specific jurisdiction."""
    name: str
    level: JurisdictionLevel
    parent_jurisdiction: Optional[str] = None
    geographic_bounds: Dict[str, float] = None
    districts: List[str] = None
    position_types: List[str] = None
    data_sources: List[str] = None
    api_endpoints: Dict[str, str] = None


class JurisdictionManager:
    """Manages multiple jurisdiction levels and their configurations."""

    def __init__(self):
        self.jurisdictions: Dict[str, JurisdictionConfig] = {}
        self._initialize_default_configs()

    def _initialize_default_configs(self):
        """Initialize default jurisdiction configurations."""
        # Federal level
        self.add_jurisdiction(JurisdictionConfig(
            name="United States",
            level=JurisdictionLevel.FEDERAL,
            position_types=["senator", "representative"],
            data_sources=["congress_api", "fec_api"],
            api_endpoints={
                "congress": "https://api.congress.gov/v3",
                "fec": "https://api.open.fec.gov/v1"
            }
        ))

        # New York State level
        self.add_jurisdiction(JurisdictionConfig(
            name="New York State",
            level=JurisdictionLevel.STATE,
            parent_jurisdiction="United States",
            position_types=["governor", "lieutenant_governor", "state_senator", "state_assembly"],
            data_sources=["ny_state_api"],
            api_endpoints={
                "legislature": "https://legislation.nysenate.gov/api/3",
                "senate": "https://www.nysenate.gov",
                "assembly": "https://nyassembly.gov"
            }
        ))

        # Richmond County (Staten Island) level
        self.add_jurisdiction(JurisdictionConfig(
            name="Richmond County",
            level=JurisdictionLevel.COUNTY,
            parent_jurisdiction="New York State",
            geographic_bounds={
                "lat": 40.5795,
                "lon": -74.1502,
                "radius": 15  # miles
            },
            districts=["24"],  # State Senate District
            position_types=["district_attorney", "surrogate", "county_clerk", "sheriff"],
            data_sources=["richmond_county_api", "ny_state_api"]
        ))

        # Staten Island Borough level
        self.add_jurisdiction(JurisdictionConfig(
            name="Staten Island",
            level=JurisdictionLevel.BOROUGH,
            parent_jurisdiction="New York City",
            geographic_bounds={
                "lat": 40.5795,
                "lon": -74.1502,
                "radius": 15
            },
            districts=["49", "50", "51"],  # City Council Districts
            position_types=["borough_president"],
            data_sources=["nyc_api"]
        ))

        # NYC Municipal level
        self.add_jurisdiction(JurisdictionConfig(
            name="New York City",
            level=JurisdictionLevel.MUNICIPAL,
            parent_jurisdiction="New York State",
            position_types=["mayor", "city_council", "comptroller", "public_advocate"],
            data_sources=["nyc_api"],
            api_endpoints={
                "council": "https://council.nyc.gov",
                "mayor": "https://www1.nyc.gov"
            }
        ))

        # Richmond State Senate District (wholly contained)
        self.add_jurisdiction(JurisdictionConfig(
            name="NY Senate District 24",
            level=JurisdictionLevel.DISTRICT,
            parent_jurisdiction="Richmond County",
            districts=["24"],
            position_types=["state_senator"],
            data_sources=["ny_state_api"],
            geographic_bounds={
                "lat": 40.5795,
                "lon": -74.1502,
                "radius": 15  # Wholly contained in Staten Island
            }
        ))

        # Richmond Assembly Districts
        for district in ["61", "62", "63", "64"]:
            self.add_jurisdiction(JurisdictionConfig(
                name=f"NY Assembly District {district}",
                level=JurisdictionLevel.DISTRICT,
                parent_jurisdiction="Richmond County",
                districts=[district],
                position_types=["state_assembly"],
                data_sources=["ny_state_api"]
            ))

        # Richmond Congressional District
        self.add_jurisdiction(JurisdictionConfig(
            name="NY Congressional District 11",
            level=JurisdictionLevel.DISTRICT,
            parent_jurisdiction="Richmond County",
            districts=["11"],
            position_types=["representative"],
            data_sources=["congress_api"]
        ))

    def add_jurisdiction(self, config: JurisdictionConfig):
        """Add a jurisdiction configuration."""
        self.jurisdictions[config.name] = config

    def get_jurisdiction(self, name: str) -> Optional[JurisdictionConfig]:
        """Get jurisdiction configuration by name."""
        return self.jurisdictions.get(name)

    def get_jurisdictions_by_level(self, level: JurisdictionLevel) -> List[JurisdictionConfig]:
        """Get all jurisdictions at a specific level."""
        return [config for config in self.jurisdictions.values() if config.level == level]

    def get_jurisdictions_for_location(self, lat: float, lon: float) -> List[JurisdictionConfig]:
        """Get all jurisdictions that cover a specific location."""
        covering_jurisdictions = []

        for config in self.jurisdictions.values():
            if config.geographic_bounds:
                bounds_lat = config.geographic_bounds.get("lat")
                bounds_lon = config.geographic_bounds.get("lon")
                radius = config.geographic_bounds.get("radius", 10)  # Default 10 mile radius

                if bounds_lat and bounds_lon:
                    # Simple distance calculation (for more accuracy, use haversine)
                    distance = ((lat - bounds_lat) ** 2 + (lon - bounds_lon) ** 2) ** 0.5
                    # Convert to approximate miles (rough calculation)
                    distance_miles = distance * 69  # Approximate miles per degree

                    if distance_miles <= radius:
                        covering_jurisdictions.append(config)

        return covering_jurisdictions

    def get_richmond_staten_island_jurisdictions(self) -> List[JurisdictionConfig]:
        """Get all jurisdictions relevant to Richmond, Staten Island."""
        richmond_lat = settings.RICHMOND_COORDINATES["lat"]
        richmond_lon = settings.RICHMOND_COORDINATES["lon"]

        return self.get_jurisdictions_for_location(richmond_lat, richmond_lon)

    def get_hierarchy_for_jurisdiction(self, jurisdiction_name: str) -> List[JurisdictionConfig]:
        """Get the complete hierarchy for a jurisdiction (from federal down)."""
        hierarchy = []
        current = self.get_jurisdiction(jurisdiction_name)

        # Build hierarchy bottom-up
        while current:
            hierarchy.insert(0, current)  # Insert at beginning
            if current.parent_jurisdiction:
                current = self.get_jurisdiction(current.parent_jurisdiction)
            else:
                break

        return hierarchy

    def get_officials_by_jurisdiction(self, jurisdiction_name: str,
                                    position_types: List[str] = None) -> Dict:
        """Get configuration for finding officials by jurisdiction."""
        config = self.get_jurisdiction(jurisdiction_name)
        if not config:
            return {}

        search_config = {
            "jurisdiction_name": jurisdiction_name,
            "level": config.level.value,
            "data_sources": config.data_sources or [],
            "api_endpoints": config.api_endpoints or {},
            "position_types": position_types or config.position_types or [],
            "districts": config.districts or [],
            "geographic_bounds": config.geographic_bounds
        }

        return search_config

    def get_data_collection_strategy(self, jurisdiction_name: str) -> Dict:
        """Get data collection strategy for a jurisdiction."""
        config = self.get_jurisdiction(jurisdiction_name)
        if not config:
            return {}

        strategy = {
            "jurisdiction": jurisdiction_name,
            "level": config.level.value,
            "data_sources": [],
            "collection_methods": [],
            "api_clients": [],
            "scraping_targets": []
        }

        # Determine collection methods based on level and data sources
        for source in (config.data_sources or []):
            if source == "congress_api":
                strategy["api_clients"].append("CongressAPI")
                strategy["collection_methods"].append("api_polling")

            elif source == "ny_state_api":
                strategy["api_clients"].append("NYStateAPI")
                strategy["collection_methods"].append("api_polling")

            elif source == "nyc_api":
                strategy["api_clients"].append("NYCDataCollector")
                strategy["collection_methods"].append("api_polling")

            elif source in ["richmond_county_api", "county_scraping"]:
                strategy["scraping_targets"].extend([
                    "https://www.richmondcountyny.gov/",
                    "https://www.statenislandda.org/",
                    "https://www.richmondcountynysurogates.com/"
                ])
                strategy["collection_methods"].append("web_scraping")

        return strategy

    def create_jurisdiction_profile_template(self, jurisdiction_name: str) -> Dict:
        """Create a profile template for a specific jurisdiction."""
        config = self.get_jurisdiction(jurisdiction_name)
        hierarchy = self.get_hierarchy_for_jurisdiction(jurisdiction_name)

        template = {
            "jurisdiction_info": {
                "name": jurisdiction_name,
                "level": config.level.value,
                "parent_jurisdictions": [j.name for j in hierarchy[:-1]],
                "position_types": config.position_types,
                "districts": config.districts
            },
            "data_collection": self.get_data_collection_strategy(jurisdiction_name),
            "analysis_focus": self._get_analysis_focus_by_level(config.level),
            "reporting_sections": self._get_reporting_sections_by_level(config.level)
        }

        return template

    def _get_analysis_focus_by_level(self, level: JurisdictionLevel) -> List[str]:
        """Get analysis focus areas by jurisdiction level."""
        focus_areas = {
            JurisdictionLevel.FEDERAL: [
                "legislative_effectiveness",
                "national_coalition_building",
                "party_leadership",
                "committee_influence",
                "national_media_presence"
            ],
            JurisdictionLevel.STATE: [
                "state_legislative_effectiveness",
                "statewide_coalition_building",
                "governor_relationship",
                "state_party_influence",
                "regional_media_presence",
                "constituent_services"
            ],
            JurisdictionLevel.COUNTY: [
                "county_administration",
                "local_coalition_building",
                "municipal_relationships",
                "local_media_presence",
                "constituent_services",
                "local_issue_expertise"
            ],
            JurisdictionLevel.MUNICIPAL: [
                "municipal_effectiveness",
                "neighborhood_engagement",
                "city_council_relationships",
                "local_media_presence",
                "constituent_services",
                "community_organizing"
            ],
            JurisdictionLevel.BOROUGH: [
                "borough_advocacy",
                "interborough_relationships",
                "mayoral_relationship",
                "borough_media_presence",
                "community_services"
            ]
        }

        return focus_areas.get(level, ["general_effectiveness", "constituent_services"])

    def _get_reporting_sections_by_level(self, level: JurisdictionLevel) -> List[str]:
        """Get reporting sections by jurisdiction level."""
        sections = {
            JurisdictionLevel.FEDERAL: [
                "congressional_record",
                "committee_assignments",
                "bill_sponsorship",
                "voting_record",
                "campaign_finance",
                "national_media_coverage"
            ],
            JurisdictionLevel.STATE: [
                "state_legislative_record",
                "committee_participation",
                "bill_sponsorship",
                "voting_record",
                "state_budget_involvement",
                "regional_media_coverage"
            ],
            JurisdictionLevel.COUNTY: [
                "county_initiatives",
                "budget_oversight",
                "inter_municipal_cooperation",
                "local_appointments",
                "local_media_coverage"
            ],
            JurisdictionLevel.MUNICIPAL: [
                "municipal_initiatives",
                "city_council_record",
                "budget_votes",
                "neighborhood_projects",
                "local_media_coverage"
            ],
            JurisdictionLevel.BOROUGH: [
                "borough_initiatives",
                "advocacy_record",
                "community_projects",
                "interborough_cooperation"
            ]
        }

        return sections.get(level, ["general_record", "local_initiatives"])

    def get_cross_jurisdiction_analysis_config(self) -> Dict:
        """Get configuration for cross-jurisdiction analysis."""
        return {
            "comparison_metrics": [
                "effectiveness_scores",
                "constituent_engagement",
                "media_presence",
                "coalition_building",
                "fundraising_ability"
            ],
            "interaction_patterns": [
                "federal_state_alignment",
                "state_county_cooperation",
                "municipal_county_coordination",
                "cross_party_collaboration"
            ],
            "issue_coordination": [
                "infrastructure_projects",
                "economic_development",
                "public_safety",
                "environmental_issues",
                "social_services"
            ],
            "influence_networks": [
                "endorsement_patterns",
                "campaign_cooperation",
                "joint_initiatives",
                "shared_constituencies"
            ]
        }

    def validate_jurisdiction_config(self, config: JurisdictionConfig) -> List[str]:
        """Validate a jurisdiction configuration and return any issues."""
        issues = []

        if not config.name:
            issues.append("Jurisdiction name is required")

        if not config.level:
            issues.append("Jurisdiction level is required")

        if config.parent_jurisdiction and config.parent_jurisdiction not in self.jurisdictions:
            issues.append(f"Parent jurisdiction '{config.parent_jurisdiction}' not found")

        if config.level == JurisdictionLevel.FEDERAL and config.parent_jurisdiction:
            issues.append("Federal level should not have a parent jurisdiction")

        if not config.position_types:
            issues.append("At least one position type should be specified")

        return issues