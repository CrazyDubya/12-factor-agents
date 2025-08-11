#!/usr/bin/env python3
"""
Improved data models with validation and type safety
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Any
from enum import Enum
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class DurationType(Enum):
    """Duration categories for disaster events"""
    SUDDEN = "sudden"      # <1 hour
    SHORT = "short"        # 1-24 hours  
    MEDIUM = "medium"      # 1-30 days
    LONG = "long"          # >30 days

class FinancialImpact(Enum):
    """Financial impact levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CATASTROPHIC = "catastrophic"

class InsuranceCoverage(Enum):
    """Insurance coverage levels"""
    NONE = "none"
    PARTIAL = "partial"
    FULL = "full"

class LocationType(Enum):
    """Location type categories"""
    URBAN = "urban"
    SUBURBAN = "suburban"
    RURAL = "rural"

@dataclass
class DisasterEvent:
    """Improved disaster event with comprehensive validation"""
    name: str
    category: str
    duration_type: DurationType
    probability_annual: float
    impact_severity: int
    financial_impact: FinancialImpact
    family_disruption: int
    preparation_possible: bool
    insurance_coverage: InsuranceCoverage
    urban_factor: float
    description: Optional[str] = None
    preparation_strategies: List[str] = field(default_factory=list)
    cost_estimate_low: Optional[float] = None
    cost_estimate_high: Optional[float] = None
    
    def __post_init__(self):
        """Validate data after initialization"""
        self._validate_probability()
        self._validate_severity_scores()
        self._validate_urban_factor()
        self._validate_strings()
    
    def _validate_probability(self):
        """Validate probability is between 0 and 1"""
        if not 0 <= self.probability_annual <= 1:
            raise ValueError(
                f"Probability must be between 0 and 1, got {self.probability_annual} for {self.name}"
            )
    
    def _validate_severity_scores(self):
        """Validate severity scores are in valid range"""
        if not 1 <= self.impact_severity <= 10:
            raise ValueError(
                f"Impact severity must be between 1 and 10, got {self.impact_severity} for {self.name}"
            )
        if not 1 <= self.family_disruption <= 10:
            raise ValueError(
                f"Family disruption must be between 1 and 10, got {self.family_disruption} for {self.name}"
            )
    
    def _validate_urban_factor(self):
        """Validate urban factor is positive"""
        if self.urban_factor <= 0:
            raise ValueError(
                f"Urban factor must be positive, got {self.urban_factor} for {self.name}"
            )
    
    def _validate_strings(self):
        """Validate string fields are not empty"""
        if not self.name or not self.name.strip():
            raise ValueError("Event name cannot be empty")
        if not self.category or not self.category.strip():
            raise ValueError("Event category cannot be empty")
    
    @property
    def risk_score(self) -> float:
        """Calculate basic risk score"""
        return self.probability_annual * self.impact_severity
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'category': self.category,
            'duration_type': self.duration_type.value,
            'probability_annual': self.probability_annual,
            'impact_severity': self.impact_severity,
            'financial_impact': self.financial_impact.value,
            'family_disruption': self.family_disruption,
            'preparation_possible': self.preparation_possible,
            'insurance_coverage': self.insurance_coverage.value,
            'urban_factor': self.urban_factor,
            'description': self.description,
            'preparation_strategies': self.preparation_strategies,
            'cost_estimate_low': self.cost_estimate_low,
            'cost_estimate_high': self.cost_estimate_high
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DisasterEvent':
        """Create from dictionary"""
        return cls(
            name=data['name'],
            category=data['category'],
            duration_type=DurationType(data['duration_type']),
            probability_annual=float(data['probability_annual']),
            impact_severity=int(data['impact_severity']),
            financial_impact=FinancialImpact(data['financial_impact']),
            family_disruption=int(data['family_disruption']),
            preparation_possible=bool(data['preparation_possible']),
            insurance_coverage=InsuranceCoverage(data['insurance_coverage']),
            urban_factor=float(data['urban_factor']),
            description=data.get('description'),
            preparation_strategies=data.get('preparation_strategies', []),
            cost_estimate_low=data.get('cost_estimate_low'),
            cost_estimate_high=data.get('cost_estimate_high')
        )

@dataclass
class FamilyProfile:
    """Comprehensive family demographic profile"""
    adults: int
    children: int
    adult_ages: List[int]
    child_ages: List[int]
    location_type: LocationType
    income_range: str
    emergency_fund_months: float
    housing_type: str = "house"
    own_home: bool = True
    chronic_conditions: bool = False
    mobility_issues: bool = False
    medication_dependent: bool = False
    pets: bool = False
    elderly_care: bool = False
    home_business: bool = False
    dual_income: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate family profile data"""
        self._validate_counts()
        self._validate_ages()
        self._validate_emergency_fund()
    
    def _validate_counts(self):
        """Validate family member counts"""
        if self.adults < 1:
            raise ValueError("Must have at least one adult")
        if self.children < 0:
            raise ValueError("Number of children cannot be negative")
        if len(self.adult_ages) != self.adults:
            raise ValueError(f"Number of adult ages ({len(self.adult_ages)}) must match number of adults ({self.adults})")
        if len(self.child_ages) != self.children:
            raise ValueError(f"Number of child ages ({len(self.child_ages)}) must match number of children ({self.children})")
    
    def _validate_ages(self):
        """Validate age ranges"""
        for age in self.adult_ages:
            if not 18 <= age <= 120:
                raise ValueError(f"Adult age must be between 18 and 120, got {age}")
        for age in self.child_ages:
            if not 0 <= age <= 17:
                raise ValueError(f"Child age must be between 0 and 17, got {age}")
    
    def _validate_emergency_fund(self):
        """Validate emergency fund amount"""
        if self.emergency_fund_months < 0:
            raise ValueError("Emergency fund months cannot be negative")
    
    @property
    def total_family_size(self) -> int:
        """Total family size"""
        return self.adults + self.children
    
    @property
    def average_adult_age(self) -> float:
        """Average age of adults"""
        return sum(self.adult_ages) / len(self.adult_ages) if self.adult_ages else 0
    
    @property
    def has_young_children(self) -> bool:
        """Check if family has children under 5"""
        return any(age < 5 for age in self.child_ages)
    
    @property
    def has_school_children(self) -> bool:
        """Check if family has school-age children"""
        return any(5 <= age <= 17 for age in self.child_ages)
    
    @property
    def has_older_adults(self) -> bool:
        """Check if family has adults over 50"""
        return any(age > 50 for age in self.adult_ages)
    
    def get_cache_key(self) -> str:
        """Generate cache key for this profile"""
        key_data = (
            self.adults, self.children, 
            tuple(self.adult_ages), tuple(self.child_ages),
            self.location_type.value, self.income_range,
            self.emergency_fund_months, self.housing_type,
            self.own_home, self.chronic_conditions,
            self.mobility_issues, self.medication_dependent,
            self.pets, self.elderly_care, self.home_business,
            self.dual_income
        )
        return str(hash(key_data))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'adults': self.adults,
            'children': self.children,
            'adult_ages': self.adult_ages,
            'child_ages': self.child_ages,
            'location_type': self.location_type.value,
            'income_range': self.income_range,
            'emergency_fund_months': self.emergency_fund_months,
            'housing_type': self.housing_type,
            'own_home': self.own_home,
            'chronic_conditions': self.chronic_conditions,
            'mobility_issues': self.mobility_issues,
            'medication_dependent': self.medication_dependent,
            'pets': self.pets,
            'elderly_care': self.elderly_care,
            'home_business': self.home_business,
            'dual_income': self.dual_income,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FamilyProfile':
        """Create from dictionary"""
        created_at = datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now()
        return cls(
            adults=int(data['adults']),
            children=int(data['children']),
            adult_ages=data['adult_ages'],
            child_ages=data['child_ages'],
            location_type=LocationType(data['location_type']),
            income_range=data['income_range'],
            emergency_fund_months=float(data['emergency_fund_months']),
            housing_type=data.get('housing_type', 'house'),
            own_home=bool(data.get('own_home', True)),
            chronic_conditions=bool(data.get('chronic_conditions', False)),
            mobility_issues=bool(data.get('mobility_issues', False)),
            medication_dependent=bool(data.get('medication_dependent', False)),
            pets=bool(data.get('pets', False)),
            elderly_care=bool(data.get('elderly_care', False)),
            home_business=bool(data.get('home_business', False)),
            dual_income=bool(data.get('dual_income', True)),
            created_at=created_at
        )

@dataclass
class RiskAssessmentResult:
    """Results of a risk assessment"""
    profile: FamilyProfile
    events: List[DisasterEvent]
    adjusted_probabilities: Dict[str, float]
    risk_scores: Dict[str, float]
    top_risks: List[str]
    recommendations: Dict[str, List[str]]
    assessment_date: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'profile': self.profile.to_dict(),
            'events': [event.to_dict() for event in self.events],
            'adjusted_probabilities': self.adjusted_probabilities,
            'risk_scores': self.risk_scores,
            'top_risks': self.top_risks,
            'recommendations': self.recommendations,
            'assessment_date': self.assessment_date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RiskAssessmentResult':
        """Create from dictionary"""
        return cls(
            profile=FamilyProfile.from_dict(data['profile']),
            events=[DisasterEvent.from_dict(event_data) for event_data in data['events']],
            adjusted_probabilities=data['adjusted_probabilities'],
            risk_scores=data['risk_scores'],
            top_risks=data['top_risks'],
            recommendations=data['recommendations'],
            assessment_date=datetime.fromisoformat(data['assessment_date'])
        )