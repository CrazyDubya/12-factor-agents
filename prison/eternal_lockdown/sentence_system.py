"""
Deterministic Sentence System for Eternal Lockdown
Short sentences (3-30 days) based on crime severity
"""

import random
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Tuple

class CrimeSeverity(Enum):
    MINOR = "minor"
    MODERATE = "moderate" 
    SERIOUS = "serious"
    SEVERE = "severe"

@dataclass
class SentenceInfo:
    """Complete sentence information"""
    crime: str
    severity: CrimeSeverity
    base_days: int
    actual_days: int
    time_served: int
    days_remaining: int
    good_behavior_eligible: bool = True
    
    @property
    def completion_percentage(self) -> float:
        """Percentage of sentence completed"""
        return (self.time_served / max(self.actual_days, 1)) * 100
    
    @property
    def is_completed(self) -> bool:
        """Check if sentence is complete"""
        return self.time_served >= self.actual_days

class SentenceCalculator:
    """Calculate deterministic sentences based on crime type"""
    
    def __init__(self):
        # Crime categories with base sentence ranges (days)
        self.crime_categories = {
            # Minor crimes (3-7 days)
            "disorderly conduct": (CrimeSeverity.MINOR, 3, 7),
            "public intoxication": (CrimeSeverity.MINOR, 3, 5),
            "petty theft": (CrimeSeverity.MINOR, 5, 7),
            "trespassing": (CrimeSeverity.MINOR, 3, 6),
            
            # Moderate crimes (8-15 days)
            "drug possession": (CrimeSeverity.MODERATE, 8, 15),
            "shoplifting": (CrimeSeverity.MODERATE, 8, 12),
            "vandalism": (CrimeSeverity.MODERATE, 10, 15),
            "driving under influence": (CrimeSeverity.MODERATE, 10, 14),
            
            # Serious crimes (16-25 days)
            "assault": (CrimeSeverity.SERIOUS, 16, 25),
            "burglary": (CrimeSeverity.SERIOUS, 18, 25),
            "drug dealing": (CrimeSeverity.SERIOUS, 20, 25),
            "fraud": (CrimeSeverity.SERIOUS, 16, 22),
            
            # Severe crimes (26-30 days)
            "armed robbery": (CrimeSeverity.SEVERE, 26, 30),
            "aggravated assault": (CrimeSeverity.SEVERE, 28, 30),
            "major fraud": (CrimeSeverity.SEVERE, 26, 30),
            "weapons charges": (CrimeSeverity.SEVERE, 27, 30)
        }
    
    def calculate_sentence(self, crime: str, prior_offenses: int = 0) -> SentenceInfo:
        """Calculate deterministic sentence for a crime"""
        
        # Normalize crime name
        crime_lower = crime.lower()
        
        # Find matching crime category
        severity, min_days, max_days = self._get_crime_info(crime_lower)
        
        # Calculate base sentence (deterministic based on crime hash)
        crime_hash = hash(crime_lower) % 1000
        sentence_range = max_days - min_days
        base_days = min_days + (crime_hash % (sentence_range + 1))
        
        # Apply prior offense multiplier
        multiplier = 1.0 + (prior_offenses * 0.2)  # 20% increase per prior offense
        actual_days = min(30, int(base_days * multiplier))  # Cap at 30 days
        
        return SentenceInfo(
            crime=crime,
            severity=severity,
            base_days=base_days,
            actual_days=actual_days,
            time_served=0,
            days_remaining=actual_days,
            good_behavior_eligible=actual_days >= 7  # Only for week+ sentences
        )
    
    def _get_crime_info(self, crime: str) -> Tuple[CrimeSeverity, int, int]:
        """Get crime severity and sentence range"""
        
        # Direct match
        if crime in self.crime_categories:
            return self.crime_categories[crime]
        
        # Partial match for similar crimes
        for crime_key, (severity, min_days, max_days) in self.crime_categories.items():
            if any(word in crime for word in crime_key.split()):
                return severity, min_days, max_days
        
        # Default for unknown crimes
        return CrimeSeverity.MODERATE, 10, 15
    
    def advance_time(self, sentence_info: SentenceInfo, days: int = 1) -> SentenceInfo:
        """Advance time served and update sentence status"""
        sentence_info.time_served = min(
            sentence_info.actual_days, 
            sentence_info.time_served + days
        )
        sentence_info.days_remaining = max(
            0, 
            sentence_info.actual_days - sentence_info.time_served
        )
        return sentence_info
    
    def apply_good_behavior(self, sentence_info: SentenceInfo, reduction_days: int = 1) -> SentenceInfo:
        """Apply good behavior time reduction"""
        if sentence_info.good_behavior_eligible and sentence_info.days_remaining > 0:
            sentence_info.actual_days = max(
                sentence_info.time_served,  # Can't reduce below time already served
                sentence_info.actual_days - reduction_days
            )
            sentence_info.days_remaining = sentence_info.actual_days - sentence_info.time_served
        return sentence_info
    
    def get_sentence_status(self, sentence_info: SentenceInfo) -> str:
        """Get human-readable sentence status"""
        if sentence_info.is_completed:
            return "COMPLETED"
        elif sentence_info.completion_percentage >= 75:
            return "NEAR_COMPLETION"
        elif sentence_info.completion_percentage >= 50:
            return "HALFWAY"
        elif sentence_info.completion_percentage >= 25:
            return "EARLY_STAGE"
        else:
            return "JUST_STARTED"

def test_sentence_system():
    """Test the sentence calculation system"""
    calculator = SentenceCalculator()
    
    print("🏛️ Testing Sentence System")
    print("=" * 40)
    
    test_crimes = [
        "drug possession",
        "armed robbery", 
        "assault",
        "petty theft",
        "fraud"
    ]
    
    for crime in test_crimes:
        # Test with no priors
        sentence = calculator.calculate_sentence(crime, prior_offenses=0)
        print(f"\n📋 {crime.title()}:")
        print(f"   Severity: {sentence.severity.value}")
        print(f"   Sentence: {sentence.actual_days} days")
        print(f"   Status: {calculator.get_sentence_status(sentence)}")
        
        # Test with priors
        sentence_repeat = calculator.calculate_sentence(crime, prior_offenses=2)
        print(f"   With 2 priors: {sentence_repeat.actual_days} days")
        
        # Test time advancement
        calculator.advance_time(sentence, 5)
        print(f"   After 5 days: {sentence.days_remaining} days remaining ({sentence.completion_percentage:.1f}% complete)")

if __name__ == "__main__":
    test_sentence_system()