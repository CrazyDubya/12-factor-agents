"""
Core data models for elected officials and their profiles.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from .database import Base


class GeographicLevel(PyEnum):
    NATIONAL = "national"
    REGIONAL = "regional"
    STATE = "state"
    COUNTY = "county"
    CITY = "city"
    DISTRICT = "district"


class PositionType(PyEnum):
    # Federal positions
    SENATOR = "senator"
    REPRESENTATIVE = "representative"

    # State positions
    GOVERNOR = "governor"
    LIEUTENANT_GOVERNOR = "lieutenant_governor"
    STATE_SENATOR = "state_senator"
    STATE_ASSEMBLY = "state_assembly"
    STATE_REPRESENTATIVE = "state_representative"

    # Municipal positions
    MAYOR = "mayor"
    CITY_COUNCIL = "city_council"
    COUNCIL_MEMBER = "council_member"
    BOROUGH_PRESIDENT = "borough_president"

    # County positions
    COUNTY_EXECUTIVE = "county_executive"
    DISTRICT_ATTORNEY = "district_attorney"
    SURROGATE = "surrogate"
    COUNTY_CLERK = "county_clerk"
    SHERIFF = "sheriff"

    # Other positions
    COMMISSIONER = "commissioner"
    JUDGE = "judge"


class StatementType(PyEnum):
    VOTE = "vote"
    SPEECH = "speech"
    PRESS_RELEASE = "press_release"
    INTERVIEW = "interview"
    SOCIAL_MEDIA = "social_media"
    WRITTEN_STATEMENT = "written_statement"


class Official(Base):
    __tablename__ = "officials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bioguide_id = Column(String(7), unique=True, nullable=True)  # Congress.gov ID
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    nickname = Column(String(100), nullable=True)
    full_name = Column(String(200), nullable=False)

    # Basic Demographics
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String(20), nullable=True)
    party = Column(String(50), nullable=False)

    # Contact & Social
    email = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(500), nullable=True)
    twitter_handle = Column(String(100), nullable=True)
    facebook_url = Column(String(500), nullable=True)
    instagram_handle = Column(String(100), nullable=True)

    # Geographic Information
    state = Column(String(50), nullable=True)
    county = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    borough = Column(String(100), nullable=True)  # For NYC boroughs

    # District Information
    congressional_district = Column(String(10), nullable=True)  # e.g., "11" for NY-11
    state_senate_district = Column(String(10), nullable=True)  # e.g., "23" for NY-23
    state_assembly_district = Column(String(10), nullable=True)  # e.g., "61" for NY Assembly 61
    council_district = Column(String(10), nullable=True)  # Municipal council districts

    # Jurisdiction Level
    jurisdiction_level = Column(String(20), nullable=True)  # federal, state, municipal, county

    # Status
    currently_serving = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Profile metadata
    profile_completeness = Column(Float, default=0.0)  # 0-1 score
    last_profile_update = Column(DateTime, default=datetime.utcnow)

    # Relationships
    positions = relationship("Position", back_populates="official", cascade="all, delete-orphan")
    statements = relationship("Statement", back_populates="official", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="official", cascade="all, delete-orphan")
    financial_disclosures = relationship("FinancialDisclosure", back_populates="official", cascade="all, delete-orphan")
    swot_analyses = relationship("SwotAnalysis", back_populates="official", cascade="all, delete-orphan")


class Position(Base):
    __tablename__ = "positions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    official_id = Column(UUID(as_uuid=True), ForeignKey("officials.id"), nullable=False)

    position_type = Column(Enum(PositionType), nullable=False)
    title = Column(String(200), nullable=False)
    chamber = Column(String(50), nullable=True)  # House, Senate, etc.

    # Geographic scope
    state = Column(String(50), nullable=True)
    district = Column(String(10), nullable=True)
    county = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)

    # Tenure
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    is_current = Column(Boolean, default=True)

    # Committee assignments
    committees = Column(JSON, nullable=True)  # List of committee names
    leadership_roles = Column(JSON, nullable=True)  # Chair, Ranking Member, etc.

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    official = relationship("Official", back_populates="positions")


class Issue(Base):
    __tablename__ = "issues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)  # Healthcare, Economy, etc.
    subcategory = Column(String(100), nullable=True)

    # Geographic relevance
    geographic_level = Column(Enum(GeographicLevel), nullable=False)
    relevant_states = Column(JSON, nullable=True)  # For regional issues
    relevant_districts = Column(JSON, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    statements = relationship("Statement", back_populates="issue")
    position_evolutions = relationship("PositionEvolution", back_populates="issue")


class Statement(Base):
    __tablename__ = "statements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    official_id = Column(UUID(as_uuid=True), ForeignKey("officials.id"), nullable=False)
    issue_id = Column(UUID(as_uuid=True), ForeignKey("issues.id"), nullable=True)

    # Content
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)  # AI-generated summary

    # Classification
    statement_type = Column(Enum(StatementType), nullable=False)
    position_stance = Column(String(20), nullable=True)  # Support, Oppose, Neutral
    confidence_score = Column(Float, nullable=True)  # AI confidence in classification

    # Source information
    source_url = Column(String(1000), nullable=True)
    source_type = Column(String(100), nullable=True)  # Congress.gov, Twitter, etc.
    date_made = Column(DateTime, nullable=False)
    date_collected = Column(DateTime, default=datetime.utcnow)

    # Context
    venue = Column(String(200), nullable=True)  # Senate Floor, Committee Hearing, etc.
    audience = Column(String(200), nullable=True)
    geographic_context = Column(String(100), nullable=True)

    # Analysis
    sentiment_score = Column(Float, nullable=True)  # -1 to 1
    key_phrases = Column(JSON, nullable=True)
    entities_mentioned = Column(JSON, nullable=True)

    # Relationships
    official = relationship("Official", back_populates="statements")
    issue = relationship("Issue", back_populates="statements")


class Vote(Base):
    __tablename__ = "votes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    official_id = Column(UUID(as_uuid=True), ForeignKey("officials.id"), nullable=False)

    # Bill Information
    bill_id = Column(String(50), nullable=False)  # e.g., "hr1234-117"
    bill_title = Column(String(500), nullable=False)
    bill_summary = Column(Text, nullable=True)

    # Vote Details
    vote_position = Column(String(20), nullable=False)  # Yes, No, Present, Not Voting
    vote_date = Column(DateTime, nullable=False)
    chamber = Column(String(20), nullable=False)  # House, Senate
    vote_type = Column(String(50), nullable=False)  # Final Passage, Amendment, etc.

    # Context
    issue_categories = Column(JSON, nullable=True)  # Multiple issue tags
    geographic_impact = Column(Enum(GeographicLevel), nullable=True)

    # Analysis
    party_line_vote = Column(Boolean, nullable=True)
    vote_significance = Column(String(20), nullable=True)  # Key, Important, Routine

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    official = relationship("Official", back_populates="votes")


class PositionEvolution(Base):
    __tablename__ = "position_evolutions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    official_id = Column(UUID(as_uuid=True), ForeignKey("officials.id"), nullable=False)
    issue_id = Column(UUID(as_uuid=True), ForeignKey("issues.id"), nullable=False)

    # Position tracking
    position_date = Column(DateTime, nullable=False)
    stance = Column(String(20), nullable=False)  # Support, Oppose, Neutral, Mixed
    strength = Column(String(20), nullable=True)  # Strong, Moderate, Weak

    # Change detection
    previous_stance = Column(String(20), nullable=True)
    is_change = Column(Boolean, default=False)
    change_significance = Column(String(20), nullable=True)  # Major, Minor, Nuanced

    # Evidence
    supporting_statement_ids = Column(JSON, nullable=True)  # List of statement IDs
    supporting_vote_ids = Column(JSON, nullable=True)  # List of vote IDs
    confidence_score = Column(Float, nullable=True)

    # Context
    context_notes = Column(Text, nullable=True)
    political_context = Column(String(200), nullable=True)  # Election year, etc.

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    issue = relationship("Issue", back_populates="position_evolutions")


class FinancialDisclosure(Base):
    __tablename__ = "financial_disclosures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    official_id = Column(UUID(as_uuid=True), ForeignKey("officials.id"), nullable=False)

    # Report Details
    report_year = Column(Integer, nullable=False)
    report_type = Column(String(50), nullable=False)  # Annual, Candidate, etc.
    filing_date = Column(DateTime, nullable=True)

    # Financial Data
    assets = Column(JSON, nullable=True)  # Asset listings
    income_sources = Column(JSON, nullable=True)
    positions_held = Column(JSON, nullable=True)  # Outside positions

    # Campaign Finance
    campaign_contributions = Column(JSON, nullable=True)
    expenditures = Column(JSON, nullable=True)

    # Analysis
    wealth_estimate_min = Column(Float, nullable=True)
    wealth_estimate_max = Column(Float, nullable=True)
    potential_conflicts = Column(JSON, nullable=True)

    source_url = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    official = relationship("Official", back_populates="financial_disclosures")


class SwotAnalysis(Base):
    __tablename__ = "swot_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    official_id = Column(UUID(as_uuid=True), ForeignKey("officials.id"), nullable=False)

    # Analysis Date and Context
    analysis_date = Column(DateTime, default=datetime.utcnow)
    analysis_context = Column(String(200), nullable=True)  # Election cycle, etc.

    # SWOT Components
    strengths = Column(JSON, nullable=False)
    weaknesses = Column(JSON, nullable=False)
    opportunities = Column(JSON, nullable=False)
    threats = Column(JSON, nullable=False)

    # Overall Assessment
    overall_score = Column(Float, nullable=True)  # Composite score
    competitiveness_rating = Column(String(20), nullable=True)  # Strong, Moderate, Vulnerable

    # Context factors
    electoral_cycle = Column(String(10), nullable=True)  # 2024, 2026, etc.
    district_competitiveness = Column(String(20), nullable=True)  # Safe, Lean, Toss-up

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    official = relationship("Official", back_populates="swot_analyses")