#!/usr/bin/env python3
"""
Data management and configuration loading
"""

import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from models import DisasterEvent, DurationType, FinancialImpact, InsuranceCoverage
from config import AppConfig

logger = logging.getLogger(__name__)

class DataManager:
    """Manages loading and saving of risk data and configurations"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.data_dir = Path(config.data_dir)
        self.cache_dir = Path(config.cache_dir)
        self._events_cache: Optional[List[DisasterEvent]] = None
        
    def load_risk_events(self, force_reload: bool = False) -> List[DisasterEvent]:
        """Load risk events from configuration file or use defaults"""
        if not force_reload and self._events_cache is not None:
            return self._events_cache
        
        events_file = self.data_dir / "risk_events.json"
        
        try:
            if events_file.exists():
                events = self._load_events_from_file(events_file)
                logger.info(f"Loaded {len(events)} events from {events_file}")
            else:
                events = self._get_default_events()
                logger.info(f"Using default events ({len(events)} events)")
                # Save defaults for future editing
                self.save_risk_events(events)
            
            self._events_cache = events
            return events
            
        except Exception as e:
            logger.error(f"Error loading risk events: {e}")
            logger.info("Falling back to default events")
            return self._get_default_events()
    
    def _load_events_from_file(self, file_path: Path) -> List[DisasterEvent]:
        """Load events from JSON or YAML file"""
        with open(file_path, 'r') as f:
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        
        events = []
        for event_data in data.get('events', []):
            try:
                event = DisasterEvent.from_dict(event_data)
                events.append(event)
            except Exception as e:
                logger.warning(f"Skipping invalid event {event_data.get('name', 'unknown')}: {e}")
        
        return events
    
    def save_risk_events(self, events: List[DisasterEvent], backup: bool = True):
        """Save risk events to configuration file"""
        events_file = self.data_dir / "risk_events.json"
        
        try:
            # Create backup if requested
            if backup and events_file.exists():
                backup_file = self.data_dir / f"risk_events_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                events_file.rename(backup_file)
                logger.info(f"Created backup: {backup_file}")
            
            # Save events
            data = {
                'events': [event.to_dict() for event in events],
                'metadata': {
                    'last_updated': datetime.now().isoformat(),
                    'version': '2.0',
                    'total_events': len(events)
                }
            }
            
            with open(events_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {len(events)} events to {events_file}")
            self._events_cache = events  # Update cache
            
        except Exception as e:
            logger.error(f"Error saving risk events: {e}")
            raise
    
    def _get_default_events(self) -> List[DisasterEvent]:
        """Return comprehensive default set of risk events"""
        return [
            # SUDDEN DURATION (<1 hour) - Infrastructure
            DisasterEvent(
                name="Power outage (local)",
                category="Infrastructure",
                duration_type=DurationType.SUDDEN,
                probability_annual=0.8,
                impact_severity=2,
                financial_impact=FinancialImpact.LOW,
                family_disruption=3,
                preparation_possible=True,
                insurance_coverage=InsuranceCoverage.NONE,
                urban_factor=1.2,
                description="Local power grid failure affecting neighborhood",
                preparation_strategies=["Battery backup", "Flashlights", "Non-perishable food"],
                cost_estimate_low=50,
                cost_estimate_high=500
            ),
            DisasterEvent(
                name="Water main break",
                category="Infrastructure",
                duration_type=DurationType.SUDDEN,
                probability_annual=0.3,
                impact_severity=3,
                financial_impact=FinancialImpact.LOW,
                family_disruption=4,
                preparation_possible=False,
                insurance_coverage=InsuranceCoverage.NONE,
                urban_factor=1.5,
                description="Municipal water system failure",
                preparation_strategies=["Water storage", "Water purification tablets"],
                cost_estimate_low=0,
                cost_estimate_high=200
            ),
            DisasterEvent(
                name="Internet/cable outage",
                category="Infrastructure",
                duration_type=DurationType.SUDDEN,
                probability_annual=0.6,
                impact_severity=1,
                financial_impact=FinancialImpact.LOW,
                family_disruption=2,
                preparation_possible=False,
                insurance_coverage=InsuranceCoverage.PARTIAL,
                urban_factor=1.1,
                description="Internet service provider outage",
                preparation_strategies=["Mobile hotspot", "Offline entertainment"],
                cost_estimate_low=0,
                cost_estimate_high=100
            ),
            
            # SUDDEN DURATION - Health
            DisasterEvent(
                name="Child injury (minor)",
                category="Health",
                duration_type=DurationType.SUDDEN,
                probability_annual=0.4,
                impact_severity=4,
                financial_impact=FinancialImpact.MEDIUM,
                family_disruption=6,
                preparation_possible=True,
                insurance_coverage=InsuranceCoverage.FULL,
                urban_factor=1.0,
                description="Minor injuries requiring medical attention",
                preparation_strategies=["First aid training", "Emergency contacts", "Pediatric first aid kit"],
                cost_estimate_low=100,
                cost_estimate_high=2000
            ),
            DisasterEvent(
                name="Food poisoning",
                category="Health",
                duration_type=DurationType.SUDDEN,
                probability_annual=0.25,
                impact_severity=3,
                financial_impact=FinancialImpact.LOW,
                family_disruption=5,
                preparation_possible=True,
                insurance_coverage=InsuranceCoverage.PARTIAL,
                urban_factor=1.0,
                description="Foodborne illness affecting family members",
                preparation_strategies=["Food safety protocols", "Hydration supplies"],
                cost_estimate_low=50,
                cost_estimate_high=500
            ),
            DisasterEvent(
                name="Heart attack (parent)",
                category="Health",
                duration_type=DurationType.SUDDEN,
                probability_annual=0.008,
                impact_severity=8,
                financial_impact=FinancialImpact.HIGH,
                family_disruption=9,
                preparation_possible=True,
                insurance_coverage=InsuranceCoverage.FULL,
                urban_factor=1.0,
                description="Cardiac emergency requiring immediate medical intervention",
                preparation_strategies=["CPR training", "Emergency action plan", "Medical alert system"],
                cost_estimate_low=5000,
                cost_estimate_high=50000
            ),
            
            # SUDDEN DURATION - Weather
            DisasterEvent(
                name="Severe thunderstorm",
                category="Weather",
                duration_type=DurationType.SUDDEN,
                probability_annual=0.5,
                impact_severity=4,
                financial_impact=FinancialImpact.MEDIUM,
                family_disruption=5,
                preparation_possible=True,
                insurance_coverage=InsuranceCoverage.PARTIAL,
                urban_factor=0.9,
                description="Severe weather with high winds and potential damage",
                preparation_strategies=["Weather radio", "Safe room identification", "Emergency supplies"],
                cost_estimate_low=100,
                cost_estimate_high=5000
            ),
            DisasterEvent(
                name="Flash flood",
                category="Weather",
                duration_type=DurationType.SUDDEN,
                probability_annual=0.1,
                impact_severity=6,
                financial_impact=FinancialImpact.HIGH,
                family_disruption=7,
                preparation_possible=True,
                insurance_coverage=InsuranceCoverage.PARTIAL,
                urban_factor=1.4,
                description="Rapid flooding from heavy rainfall",
                preparation_strategies=["Evacuation plan", "Flood insurance", "Emergency kit"],
                cost_estimate_low=1000,
                cost_estimate_high=25000
            ),
            
            # SUDDEN DURATION - Security
            DisasterEvent(
                name="Burglary attempt",
                category="Security",
                duration_type=DurationType.SUDDEN,
                probability_annual=0.08,
                impact_severity=5,
                financial_impact=FinancialImpact.MEDIUM,
                family_disruption=7,
                preparation_possible=True,
                insurance_coverage=InsuranceCoverage.PARTIAL,
                urban_factor=1.8,
                description="Attempted break-in or theft",
                preparation_strategies=["Security system", "Neighborhood watch", "Emergency contacts"],
                cost_estimate_low=0,
                cost_estimate_high=5000
            ),
            
            # SHORT DURATION (1-24 hours)
            DisasterEvent(
                name="Extended power outage",
                category="Infrastructure",
                duration_type=DurationType.SHORT,
                probability_annual=0.4,
                impact_severity=3,
                financial_impact=FinancialImpact.MEDIUM,
                family_disruption=5,
                preparation_possible=True,
                insurance_coverage=InsuranceCoverage.NONE,
                urban_factor=1.2,
                description="Power outage lasting 6-24 hours",
                preparation_strategies=["Generator", "Battery bank", "Non-perishable food"],
                cost_estimate_low=200,
                cost_estimate_high=2000
            ),
            DisasterEvent(
                name="School closure (weather)",
                category="Education",
                duration_type=DurationType.SHORT,
                probability_annual=0.8,
                impact_severity=2,
                financial_impact=FinancialImpact.LOW,
                family_disruption=4,
                preparation_possible=False,
                insurance_coverage=InsuranceCoverage.NONE,
                urban_factor=1.0,
                description="School closure due to weather conditions",
                preparation_strategies=["Childcare backup plan", "Work from home arrangements"],
                cost_estimate_low=0,
                cost_estimate_high=300
            ),
            DisasterEvent(
                name="Stomach flu (family)",
                category="Health",
                duration_type=DurationType.SHORT,
                probability_annual=0.6,
                impact_severity=3,
                financial_impact=FinancialImpact.LOW,
                family_disruption=6,
                preparation_possible=True,
                insurance_coverage=InsuranceCoverage.PARTIAL,
                urban_factor=1.0,
                description="Viral gastroenteritis affecting multiple family members",
                preparation_strategies=["Hydration supplies", "Isolation protocols", "Medical supplies"],
                cost_estimate_low=100,
                cost_estimate_high=1000
            ),
            DisasterEvent(
                name="Hospital emergency",
                category="Health",
                duration_type=DurationType.SHORT,
                probability_annual=0.2,
                impact_severity=6,
                financial_impact=FinancialImpact.HIGH,
                family_disruption=8,
                preparation_possible=True,
                insurance_coverage=InsuranceCoverage.FULL,
                urban_factor=1.0,
                description="Emergency requiring hospital admission",
                preparation_strategies=["Insurance verification", "Emergency contacts", "Childcare plan"],
                cost_estimate_low=1000,
                cost_estimate_high=15000
            ),
            
            # MEDIUM DURATION (1-30 days)
            DisasterEvent(
                name="Extended illness (parent)",
                category="Health",
                duration_type=DurationType.MEDIUM,
                probability_annual=0.3,
                impact_severity=4,
                financial_impact=FinancialImpact.MEDIUM,
                family_disruption=6,
                preparation_possible=True,
                insurance_coverage=InsuranceCoverage.PARTIAL,
                urban_factor=1.0,
                description="Prolonged illness affecting work and family responsibilities",
                preparation_strategies=["Sick leave planning", "Family support network", "Household management"],
                cost_estimate_low=500,
                cost_estimate_high=5000
            ),
            DisasterEvent(
                name="Temporary job loss",
                category="Economic",
                duration_type=DurationType.MEDIUM,
                probability_annual=0.15,
                impact_severity=5,
                financial_impact=FinancialImpact.HIGH,
                family_disruption=7,
                preparation_possible=True,
                insurance_coverage=InsuranceCoverage.PARTIAL,
                urban_factor=1.0,
                description="Short-term unemployment or job elimination",
                preparation_strategies=["Emergency fund", "Unemployment insurance", "Job search preparation"],
                cost_estimate_low=2000,
                cost_estimate_high=20000
            ),
            DisasterEvent(
                name="Car breakdown/repair",
                category="Transportation",
                duration_type=DurationType.MEDIUM,
                probability_annual=0.25,
                impact_severity=3,
                financial_impact=FinancialImpact.MEDIUM,
                family_disruption=4,
                preparation_possible=True,
                insurance_coverage=InsuranceCoverage.PARTIAL,
                urban_factor=1.0,
                description="Major vehicle repair or replacement needed",
                preparation_strategies=["Emergency transportation plan", "Repair fund", "Maintenance schedule"],
                cost_estimate_low=500,
                cost_estimate_high=8000
            ),
            DisasterEvent(
                name="Home repairs needed",
                category="Infrastructure",
                duration_type=DurationType.MEDIUM,
                probability_annual=0.2,
                impact_severity=4,
                financial_impact=FinancialImpact.MEDIUM,
                family_disruption=5,
                preparation_possible=True,
                insurance_coverage=InsuranceCoverage.PARTIAL,
                urban_factor=1.0,
                description="Significant home maintenance or repair requirements",
                preparation_strategies=["Home maintenance fund", "Contractor relationships", "Temporary housing plan"],
                cost_estimate_low=1000,
                cost_estimate_high=15000
            ),
            
            # LONG DURATION (>30 days)
            DisasterEvent(
                name="Financial strain",
                category="Economic",
                duration_type=DurationType.LONG,
                probability_annual=0.25,
                impact_severity=5,
                financial_impact=FinancialImpact.MEDIUM,
                family_disruption=6,
                preparation_possible=True,
                insurance_coverage=InsuranceCoverage.NONE,
                urban_factor=1.0,
                description="Extended period of financial difficulty",
                preparation_strategies=["Budget optimization", "Debt management", "Additional income sources"],
                cost_estimate_low=1000,
                cost_estimate_high=10000
            ),
            DisasterEvent(
                name="Extended unemployment",
                category="Economic",
                duration_type=DurationType.LONG,
                probability_annual=0.08,
                impact_severity=6,
                financial_impact=FinancialImpact.HIGH,
                family_disruption=7,
                preparation_possible=True,
                insurance_coverage=InsuranceCoverage.PARTIAL,
                urban_factor=1.0,
                description="Long-term job loss requiring career transition",
                preparation_strategies=["Extended emergency fund", "Skill development", "Career counseling"],
                cost_estimate_low=5000,
                cost_estimate_high=50000
            ),
            DisasterEvent(
                name="Chronic illness (mild)",
                category="Health",
                duration_type=DurationType.LONG,
                probability_annual=0.1,
                impact_severity=4,
                financial_impact=FinancialImpact.MEDIUM,
                family_disruption=5,
                preparation_possible=True,
                insurance_coverage=InsuranceCoverage.PARTIAL,
                urban_factor=1.0,
                description="Ongoing health condition requiring management",
                preparation_strategies=["Health insurance optimization", "Lifestyle modifications", "Support groups"],
                cost_estimate_low=2000,
                cost_estimate_high=20000
            ),
            DisasterEvent(
                name="Aging parent care",
                category="Social",
                duration_type=DurationType.LONG,
                probability_annual=0.15,
                impact_severity=5,
                financial_impact=FinancialImpact.MEDIUM,
                family_disruption=6,
                preparation_possible=True,
                insurance_coverage=InsuranceCoverage.NONE,
                urban_factor=1.0,
                description="Increased caregiving responsibilities for aging parents",
                preparation_strategies=["Care planning", "Financial planning", "Support services"],
                cost_estimate_low=1000,
                cost_estimate_high=30000
            )
        ]
    
    def get_events_by_category(self, category: str) -> List[DisasterEvent]:
        """Get all events in a specific category"""
        events = self.load_risk_events()
        return [event for event in events if event.category.lower() == category.lower()]
    
    def get_events_by_duration(self, duration: DurationType) -> List[DisasterEvent]:
        """Get all events of a specific duration type"""
        events = self.load_risk_events()
        return [event for event in events if event.duration_type == duration]
    
    def search_events(self, query: str) -> List[DisasterEvent]:
        """Search events by name or description"""
        events = self.load_risk_events()
        query_lower = query.lower()
        return [
            event for event in events 
            if query_lower in event.name.lower() or 
               (event.description and query_lower in event.description.lower())
        ]
    
    def validate_events(self) -> Dict[str, List[str]]:
        """Validate all events and return any issues found"""
        events = self.load_risk_events()
        issues = {
            'errors': [],
            'warnings': []
        }
        
        for event in events:
            try:
                # Validation is done in __post_init__, so just creating the object validates it
                pass
            except Exception as e:
                issues['errors'].append(f"{event.name}: {str(e)}")
        
        # Check for duplicate names
        names = [event.name for event in events]
        duplicates = [name for name in set(names) if names.count(name) > 1]
        for duplicate in duplicates:
            issues['warnings'].append(f"Duplicate event name: {duplicate}")
        
        return issues