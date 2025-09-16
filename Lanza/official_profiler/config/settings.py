"""
Configuration settings for the Official Profiler system.
"""
from decouple import config
from typing import Optional


class Settings:
    # Database Configuration
    DATABASE_URL: str = config(
        "DATABASE_URL",
        default="postgresql://user:password@localhost:5432/official_profiler"
    )

    # Redis Configuration (for Celery)
    REDIS_URL: str = config("REDIS_URL", default="redis://localhost:6379/0")

    # API Keys
    CONGRESS_API_KEY: Optional[str] = config("CONGRESS_API_KEY", default=None)
    NYS_OPEN_LEG_API_KEY: str = config("NYS_OPEN_LEG_API_KEY", default="gNyGkkPgvKrEKXaq7OehFL5D65t4S7yM")
    TWITTER_API_KEY: Optional[str] = config("TWITTER_API_KEY", default=None)
    TWITTER_API_SECRET: Optional[str] = config("TWITTER_API_SECRET", default=None)
    TWITTER_ACCESS_TOKEN: Optional[str] = config("TWITTER_ACCESS_TOKEN", default=None)
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = config("TWITTER_ACCESS_TOKEN_SECRET", default=None)
    OPENAI_API_KEY: Optional[str] = config("OPENAI_API_KEY", default=None)

    # Data Collection Settings
    SCRAPE_DELAY: float = config("SCRAPE_DELAY", default=1.0, cast=float)
    MAX_CONCURRENT_REQUESTS: int = config("MAX_CONCURRENT_REQUESTS", default=10, cast=int)
    REQUEST_TIMEOUT: int = config("REQUEST_TIMEOUT", default=30, cast=int)

    # NLP Settings
    SPACY_MODEL: str = config("SPACY_MODEL", default="en_core_web_sm")

    # File Storage
    DATA_DIRECTORY: str = config("DATA_DIRECTORY", default="./data")
    REPORTS_DIRECTORY: str = config("REPORTS_DIRECTORY", default="./reports")

    # Processing Settings
    BATCH_SIZE: int = config("BATCH_SIZE", default=100, cast=int)
    UPDATE_FREQUENCY_HOURS: int = config("UPDATE_FREQUENCY_HOURS", default=24, cast=int)

    # Geographic Hierarchy for Richmond, Staten Island
    RICHMOND_COORDINATES = {"lat": 40.5795, "lon": -74.1502}
    RICHMOND_COUNTY = "Richmond County"  # Staten Island
    RICHMOND_STATE = "New York"
    RICHMOND_CONGRESSIONAL_DISTRICT = 11  # NY-11 Congressional District
    RICHMOND_STATE_SENATE_DISTRICT = 24  # NY Senate District 24 (wholly contained)
    RICHMOND_ASSEMBLY_DISTRICT = 61  # NY Assembly District 61-64 area
    RICHMOND_BOROUGH = "Staten Island"

    # Multi-jurisdiction configuration
    JURISDICTION_LEVELS = {
        "federal": ["house", "senate"],
        "state": ["state_senate", "state_assembly"],
        "municipal": ["mayor", "city_council", "borough_president"],
        "county": ["district_attorney", "surrogate", "county_clerk"]
    }

    class Config:
        case_sensitive = True


settings = Settings()