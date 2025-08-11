#!/usr/bin/env python3
"""
Improved risk calculation engine with strategy pattern and caching
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
import pandas as pd
from datetime import datetime, timedelta
import logging
import hashlib
import pickle
from pathlib import Path

from models import DisasterEvent, FamilyProfile, RiskAssessmentResult, LocationType
from config import app_config

logger = logging.getLogger(__name__)

class RiskCalculationStrategy(ABC):
    """Abstract base class for risk calculation strategies"""
    
    @abstractmethod
    def calculate_adjusted_probability(self, event: DisasterEvent, profile: FamilyProfile) -> float:
        """Calculate adjusted probability for given event and family profile"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get name of this strategy"""
        pass

class UrbanFamilyStrategy(RiskCalculationStrategy):
    """Risk calculation strategy optimized for urban families"""
    
    def calculate_adjusted_probability(self, event: DisasterEvent, profile: FamilyProfile) -> float:
        """Calculate probability adjusted for urban setting and family profile"""
        try:
            base_prob = event.probability_annual
            urban_adjusted = base_prob * event.urban_factor
            
            # Apply location-specific adjustments
            location_factor = self._get_location_factor(event, profile.location_type)
            
            # Apply family-specific adjustments
            family_factor = self._get_family_factor(event, profile)
            
            # Apply demographic adjustments
            demo_factor = self._get_demographic_factor(event, profile)
            
            # Combine all factors
            final_probability = min(urban_adjusted * location_factor * family_factor * demo_factor, 1.0)
            
            logger.debug(f"Probability calculation for {event.name}: "
                        f"base={base_prob:.3f}, urban={urban_adjusted:.3f}, "
                        f"final={final_probability:.3f}")
            
            return final_probability
            
        except Exception as e:
            logger.error(f"Error calculating probability for {event.name}: {e}")
            return event.probability_annual  # Fallback to base probability
    
    def _get_location_factor(self, event: DisasterEvent, location: LocationType) -> float:
        """Calculate location-specific adjustment factor"""
        location_adjustments = {
            LocationType.URBAN: {
                'Security': 1.2,
                'Infrastructure': 1.1,
                'Health': 0.9,  # Better healthcare access
                'Transportation': 1.3,
                'Environmental': 1.2
            },
            LocationType.SUBURBAN: {
                'Security': 1.0,
                'Infrastructure': 1.0,
                'Health': 1.0,
                'Transportation': 1.0,
                'Environmental': 1.0
            },
            LocationType.RURAL: {
                'Security': 0.7,
                'Infrastructure': 1.4,  # More vulnerable to outages
                'Health': 1.3,  # Limited healthcare access
                'Transportation': 0.8,
                'Environmental': 0.9
            }
        }
        
        return location_adjustments.get(location, {}).get(event.category, 1.0)
    
    def _get_family_factor(self, event: DisasterEvent, profile: FamilyProfile) -> float:
        """Calculate family composition adjustment factor"""
        factor = 1.0
        
        # Adjust for children
        if "child" in event.name.lower() or event.category in ["Health", "Education"]:
            if profile.has_young_children:
                factor *= 1.3
            elif profile.has_school_children:
                factor *= 1.2
        
        # Adjust for childcare and education disruptions
        if event.category in ["Education"] and profile.children > 0:
            factor *= 1.0 + (profile.children * 0.1)
        
        # Adjust for dual income dependency
        if event.category == "Economic" and not profile.dual_income:
            factor *= 1.4
        
        # Adjust for home business
        if profile.home_business and event.category in ["Infrastructure", "Economic"]:
            factor *= 1.2
        
        return factor
    
    def _get_demographic_factor(self, event: DisasterEvent, profile: FamilyProfile) -> float:
        """Calculate demographic-specific adjustment factor"""
        factor = 1.0
        
        # Age-related health adjustments
        if "parent" in event.name.lower() and event.category == "Health":
            if profile.has_older_adults:
                factor *= 1.3
            elif profile.average_adult_age > 40:
                factor *= 1.1
        
        # Chronic conditions adjustment
        if profile.chronic_conditions and event.category == "Health":
            factor *= 1.2
        
        # Mobility issues adjustment
        if profile.mobility_issues and event.category in ["Health", "Emergency"]:
            factor *= 1.3
        
        # Medication dependency
        if profile.medication_dependent and "supply" in event.name.lower():
            factor *= 1.5
        
        # Pet ownership adjustments
        if profile.pets and "evacuation" in event.name.lower():
            factor *= 1.2
        
        # Elderly care responsibilities
        if profile.elderly_care and event.category in ["Health", "Social"]:
            factor *= 1.2
        
        return factor
    
    def get_strategy_name(self) -> str:
        return "Urban Family Strategy v2.0"

class CacheManager:
    """Manages caching of risk calculations for performance"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = Path(cache_dir or app_config.cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "risk_calculations.cache"
        self._memory_cache: Dict[str, Tuple[float, datetime]] = {}
        self.cache_timeout = timedelta(hours=24)
    
    def get_cache_key(self, event: DisasterEvent, profile: FamilyProfile, strategy_name: str) -> str:
        """Generate cache key for calculation"""
        key_data = f"{event.name}|{profile.get_cache_key()}|{strategy_name}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_cached_probability(self, cache_key: str) -> Optional[float]:
        """Get cached probability if available and not expired"""
        if not app_config.cache_enabled:
            return None
        
        # Check memory cache first
        if cache_key in self._memory_cache:
            probability, timestamp = self._memory_cache[cache_key]
            if datetime.now() - timestamp < self.cache_timeout:
                logger.debug(f"Cache hit (memory): {cache_key}")
                return probability
            else:
                # Remove expired entry
                del self._memory_cache[cache_key]
        
        # Check disk cache
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'rb') as f:
                    disk_cache = pickle.load(f)
                
                if cache_key in disk_cache:
                    probability, timestamp = disk_cache[cache_key]
                    if datetime.now() - timestamp < self.cache_timeout:
                        # Add to memory cache
                        self._memory_cache[cache_key] = (probability, timestamp)
                        logger.debug(f"Cache hit (disk): {cache_key}")
                        return probability
        except Exception as e:
            logger.warning(f"Error reading cache: {e}")
        
        return None
    
    def cache_probability(self, cache_key: str, probability: float):
        """Cache calculated probability"""
        if not app_config.cache_enabled:
            return
        
        timestamp = datetime.now()
        
        # Add to memory cache
        self._memory_cache[cache_key] = (probability, timestamp)
        
        # Limit memory cache size
        if len(self._memory_cache) > app_config.max_cache_size:
            # Remove oldest entries
            sorted_items = sorted(self._memory_cache.items(), key=lambda x: x[1][1])
            for key, _ in sorted_items[:len(self._memory_cache) // 4]:
                del self._memory_cache[key]
        
        # Update disk cache periodically
        try:
            disk_cache = {}
            if self.cache_file.exists():
                with open(self.cache_file, 'rb') as f:
                    disk_cache = pickle.load(f)
            
            disk_cache[cache_key] = (probability, timestamp)
            
            # Clean expired entries
            current_time = datetime.now()
            disk_cache = {k: v for k, v in disk_cache.items() 
                         if current_time - v[1] < self.cache_timeout}
            
            with open(self.cache_file, 'wb') as f:
                pickle.dump(disk_cache, f)
                
        except Exception as e:
            logger.warning(f"Error writing cache: {e}")
    
    def clear_cache(self):
        """Clear all cached data"""
        self._memory_cache.clear()
        if self.cache_file.exists():
            self.cache_file.unlink()
        logger.info("Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        disk_entries = 0
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'rb') as f:
                    disk_cache = pickle.load(f)
                disk_entries = len(disk_cache)
        except Exception:
            pass
        
        return {
            'memory_entries': len(self._memory_cache),
            'disk_entries': disk_entries,
            'cache_enabled': app_config.cache_enabled
        }

class RiskCalculator:
    """Main risk calculator with improved architecture"""
    
    def __init__(self, strategy: RiskCalculationStrategy):
        self.strategy = strategy
        self.cache_manager = CacheManager()
        self._calculation_cache: Dict[str, pd.DataFrame] = {}
    
    def calculate_single_risk(self, event: DisasterEvent, profile: FamilyProfile) -> float:
        """Calculate adjusted probability for a single event"""
        cache_key = self.cache_manager.get_cache_key(event, profile, self.strategy.get_strategy_name())
        
        # Try to get from cache
        cached_prob = self.cache_manager.get_cached_probability(cache_key)
        if cached_prob is not None:
            return cached_prob
        
        # Calculate new probability
        probability = self.strategy.calculate_adjusted_probability(event, profile)
        
        # Cache the result
        self.cache_manager.cache_probability(cache_key, probability)
        
        return probability
    
    def generate_risk_matrix(self, events: List[DisasterEvent], profile: FamilyProfile) -> pd.DataFrame:
        """Generate comprehensive risk matrix"""
        matrix_cache_key = f"{profile.get_cache_key()}_{len(events)}_{self.strategy.get_strategy_name()}"
        
        # Check matrix cache
        if matrix_cache_key in self._calculation_cache:
            logger.debug("Using cached risk matrix")
            return self._calculation_cache[matrix_cache_key].copy()
        
        logger.info(f"Generating risk matrix for {len(events)} events")
        
        data = []
        for event in events:
            try:
                adjusted_prob = self.calculate_single_risk(event, profile)
                risk_score = adjusted_prob * event.impact_severity
                
                data.append({
                    'Event': event.name,
                    'Category': event.category,
                    'Duration': event.duration_type.value,
                    'Base_Probability': event.probability_annual,
                    'Adjusted_Probability': adjusted_prob,
                    'Probability_Percent': f"{adjusted_prob * 100:.2f}%",
                    'Impact_Severity': event.impact_severity,
                    'Financial_Impact': event.financial_impact.value,
                    'Family_Disruption': event.family_disruption,
                    'Preparable': event.preparation_possible,
                    'Insurance': event.insurance_coverage.value,
                    'Urban_Factor': event.urban_factor,
                    'Risk_Score': risk_score,
                    'Description': event.description or ""
                })
                
            except Exception as e:
                logger.error(f"Error processing event {event.name}: {e}")
                continue
        
        df = pd.DataFrame(data)
        
        # Cache the matrix
        self._calculation_cache[matrix_cache_key] = df.copy()
        
        logger.info(f"Generated risk matrix with {len(df)} events")
        return df
    
    def get_top_risks(self, events: List[DisasterEvent], profile: FamilyProfile, n: int = 10) -> pd.DataFrame:
        """Get top N risks by risk score"""
        df = self.generate_risk_matrix(events, profile)
        return df.nlargest(n, 'Risk_Score')
    
    def get_risks_by_category(self, events: List[DisasterEvent], profile: FamilyProfile) -> Dict[str, pd.DataFrame]:
        """Get risks grouped by category"""
        df = self.generate_risk_matrix(events, profile)
        return {category: group.sort_values('Risk_Score', ascending=False) 
                for category, group in df.groupby('Category')}
    
    def get_risks_by_duration(self, events: List[DisasterEvent], profile: FamilyProfile) -> Dict[str, pd.DataFrame]:
        """Get risks grouped by duration"""
        df = self.generate_risk_matrix(events, profile)
        return {duration: group.sort_values('Risk_Score', ascending=False) 
                for duration, group in df.groupby('Duration')}
    
    def calculate_annual_risk_budget(self, events: List[DisasterEvent], profile: FamilyProfile) -> Dict[str, float]:
        """Calculate expected annual financial impact"""
        df = self.generate_risk_matrix(events, profile)
        
        # Cost estimates by financial impact level
        cost_estimates = {
            'low': 500,
            'medium': 2500,
            'high': 15000,
            'catastrophic': 100000
        }
        
        df['Expected_Cost'] = df.apply(
            lambda row: row['Adjusted_Probability'] * cost_estimates.get(row['Financial_Impact'], 1000),
            axis=1
        )
        
        total_expected_cost = df['Expected_Cost'].sum()
        cost_by_category = df.groupby('Category')['Expected_Cost'].sum().to_dict()
        
        return {
            'total_annual_expected_cost': total_expected_cost,
            'cost_by_category': cost_by_category,
            'top_cost_drivers': df.nlargest(5, 'Expected_Cost')[['Event', 'Expected_Cost']].to_dict('records')
        }
    
    def clear_cache(self):
        """Clear all caches"""
        self.cache_manager.clear_cache()
        self._calculation_cache.clear()
        logger.info("All caches cleared")
    
    def get_performance_stats(self) -> Dict[str, any]:
        """Get performance and cache statistics"""
        return {
            'strategy': self.strategy.get_strategy_name(),
            'cache_stats': self.cache_manager.get_cache_stats(),
            'matrix_cache_entries': len(self._calculation_cache)
        }