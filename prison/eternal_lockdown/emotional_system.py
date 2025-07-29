"""
Emotional System with Game Theory Integration
Emotions, needs, and privileges in tight lockdown environment
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import random

class EmotionalState(Enum):
    ANGRY = "angry"
    SAD = "sad" 
    HOPEFUL = "hopeful"
    FRUSTRATED = "frustrated"
    RESIGNED = "resigned"
    ANXIOUS = "anxious"
    CONTENT = "content"

class BasicNeed(Enum):
    FOOD = "food"
    SAFETY = "safety"
    RESPECT = "respect"
    FREEDOM = "freedom"
    SOCIAL_CONNECTION = "social_connection"
    PURPOSE = "purpose"

class PrivilegeType(Enum):
    EXTRA_FOOD = "extra_food"
    RECREATION_TIME = "recreation_time"
    PHONE_CALL = "phone_call"
    VISITOR_RIGHTS = "visitor_rights"
    WORK_ASSIGNMENT = "work_assignment"
    LIBRARY_ACCESS = "library_access"
    COMMISSARY = "commissary"

@dataclass
class EmotionalProfile:
    """Agent's emotional state and needs"""
    current_emotion: EmotionalState = EmotionalState.RESIGNED
    emotion_intensity: float = 0.5  # 0.0-1.0
    
    # Need satisfaction levels (0.0-1.0)
    needs: Dict[BasicNeed, float] = field(default_factory=lambda: {
        BasicNeed.FOOD: 0.6,
        BasicNeed.SAFETY: 0.4,
        BasicNeed.RESPECT: 0.3,
        BasicNeed.FREEDOM: 0.1,  # Always low in prison
        BasicNeed.SOCIAL_CONNECTION: 0.5,
        BasicNeed.PURPOSE: 0.3
    })
    
    # Privileges earned/lost
    privileges: Dict[PrivilegeType, bool] = field(default_factory=lambda: {
        PrivilegeType.EXTRA_FOOD: False,
        PrivilegeType.RECREATION_TIME: True,  # Basic right
        PrivilegeType.PHONE_CALL: False,
        PrivilegeType.VISITOR_RIGHTS: True,   # Basic right
        PrivilegeType.WORK_ASSIGNMENT: False,
        PrivilegeType.LIBRARY_ACCESS: True,   # Basic right
        PrivilegeType.COMMISSARY: False
    })
    
    def get_overall_wellbeing(self) -> float:
        """Calculate overall emotional wellbeing (0.0-1.0)"""
        need_satisfaction = sum(self.needs.values()) / len(self.needs)
        privilege_bonus = sum(self.privileges.values()) / len(self.privileges) * 0.2
        emotion_factor = 0.7 if self.current_emotion in [EmotionalState.HOPEFUL, EmotionalState.CONTENT] else 0.3
        
        return min(1.0, (need_satisfaction * 0.6) + privilege_bonus + (emotion_factor * 0.2))
    
    def get_emotional_decision_context(self, sentence_days_remaining: int) -> str:
        """Get emotional context for Ollama decision making"""
        
        wellbeing = self.get_overall_wellbeing()
        
        # Identify critical needs
        critical_needs = [need.value for need, level in self.needs.items() if level < 0.3]
        
        # Count privileges
        privilege_count = sum(self.privileges.values())
        
        context = f"""
EMOTIONAL STATE: {self.current_emotion.value} (intensity: {self.emotion_intensity:.1f})
WELLBEING: {wellbeing:.1f}/1.0 ({'struggling' if wellbeing < 0.4 else 'managing' if wellbeing < 0.7 else 'doing well'})
DAYS REMAINING: {sentence_days_remaining} days
PRIVILEGES: {privilege_count}/7 earned
CRITICAL NEEDS: {', '.join(critical_needs) if critical_needs else 'none'}

Your emotional state affects your decisions. You are {self.current_emotion.value} and {'desperate' if wellbeing < 0.3 else 'struggling' if wellbeing < 0.6 else 'stable'}.
"""
        
        return context.strip()

class EmotionalDecisionEngine:
    """Integrates emotions with game theory decisions"""
    
    def __init__(self):
        # Emotional impact on cooperation tendency
        self.emotion_cooperation_modifiers = {
            EmotionalState.ANGRY: -0.3,
            EmotionalState.FRUSTRATED: -0.2,
            EmotionalState.SAD: -0.1,
            EmotionalState.ANXIOUS: -0.1,
            EmotionalState.RESIGNED: 0.0,
            EmotionalState.HOPEFUL: 0.2,
            EmotionalState.CONTENT: 0.1
        }
        
        # Need deficits impact on cooperation
        self.need_cooperation_impact = {
            BasicNeed.FOOD: -0.4,      # Hungry people less cooperative
            BasicNeed.SAFETY: -0.3,    # Unsafe people defensive
            BasicNeed.RESPECT: -0.2,   # Disrespected people defiant
            BasicNeed.FREEDOM: -0.1,   # Always low, minimal impact
            BasicNeed.SOCIAL_CONNECTION: 0.1,  # Social needs encourage cooperation
            BasicNeed.PURPOSE: 0.1     # Purpose encourages cooperation
        }
    
    def calculate_emotional_cooperation_modifier(self, emotional_profile: EmotionalProfile, 
                                               sentence_days_remaining: int) -> float:
        """Calculate how emotions affect cooperation tendency"""
        
        # Base emotional modifier
        emotion_mod = self.emotion_cooperation_modifiers.get(emotional_profile.current_emotion, 0.0)
        emotion_mod *= emotional_profile.emotion_intensity
        
        # Need satisfaction impact
        need_mod = 0.0
        for need, satisfaction in emotional_profile.needs.items():
            if satisfaction < 0.5:  # Unmet need
                deficit = 0.5 - satisfaction
                need_mod += self.need_cooperation_impact[need] * deficit
        
        # Sentence time remaining impact (desperation vs hope)
        if sentence_days_remaining <= 3:
            time_mod = 0.2  # Almost free, more cooperative
        elif sentence_days_remaining <= 7:
            time_mod = 0.1  # Light at end of tunnel
        elif sentence_days_remaining >= 25:
            time_mod = -0.1  # Long time left, more desperate
        else:
            time_mod = 0.0
        
        # Privilege impact
        privilege_count = sum(emotional_profile.privileges.values())
        privilege_mod = (privilege_count - 3) * 0.05  # 3 is baseline (basic rights)
        
        total_modifier = emotion_mod + need_mod + time_mod + privilege_mod
        return max(-0.5, min(0.5, total_modifier))  # Cap at ±0.5
    
    def update_emotions_from_interaction(self, emotional_profile: EmotionalProfile,
                                       my_choice: str, opponent_choice: str, 
                                       my_payoff: float, relationship: str) -> EmotionalProfile:
        """Update emotions based on interaction outcome"""
        
        # Determine emotional response to interaction
        if my_choice == "cooperate" and opponent_choice == "cooperate":
            # Mutual cooperation - positive emotions
            if relationship == "gang member" or relationship == "ally":
                new_emotion = EmotionalState.CONTENT
                emotional_profile.needs[BasicNeed.SOCIAL_CONNECTION] = min(1.0, 
                    emotional_profile.needs[BasicNeed.SOCIAL_CONNECTION] + 0.1)
            else:
                new_emotion = EmotionalState.HOPEFUL
            
            emotional_profile.needs[BasicNeed.RESPECT] = min(1.0,
                emotional_profile.needs[BasicNeed.RESPECT] + 0.05)
                
        elif my_choice == "cooperate" and opponent_choice == "defect":
            # Exploited - negative emotions
            new_emotion = EmotionalState.FRUSTRATED if emotional_profile.current_emotion != EmotionalState.ANGRY else EmotionalState.ANGRY
            emotional_profile.needs[BasicNeed.RESPECT] = max(0.0,
                emotional_profile.needs[BasicNeed.RESPECT] - 0.15)
            emotional_profile.needs[BasicNeed.SAFETY] = max(0.0,
                emotional_profile.needs[BasicNeed.SAFETY] - 0.1)
                
        elif my_choice == "defect" and opponent_choice == "cooperate":
            # Exploited someone - mixed emotions
            if relationship == "enemy":
                new_emotion = EmotionalState.CONTENT  # Satisfied revenge
            else:
                new_emotion = EmotionalState.RESIGNED  # Guilty but necessary
                
        else:  # mutual defection
            # Both defected - resigned/frustrated
            new_emotion = EmotionalState.FRUSTRATED
            emotional_profile.needs[BasicNeed.SOCIAL_CONNECTION] = max(0.0,
                emotional_profile.needs[BasicNeed.SOCIAL_CONNECTION] - 0.05)
        
        # Update emotion with some persistence (don't change too quickly)
        if random.random() < 0.7:  # 70% chance to change emotion
            emotional_profile.current_emotion = new_emotion
            emotional_profile.emotion_intensity = min(1.0, emotional_profile.emotion_intensity + 0.1)
        
        return emotional_profile
    
    def daily_need_decay(self, emotional_profile: EmotionalProfile) -> EmotionalProfile:
        """Daily decay of needs in prison environment"""
        
        # Basic prison conditions cause need decay
        decay_rates = {
            BasicNeed.FOOD: -0.02,  # Institutional food
            BasicNeed.SAFETY: -0.03,  # Always some danger
            BasicNeed.RESPECT: -0.02,  # Institutional dehumanization
            BasicNeed.FREEDOM: -0.01,  # Already minimal
            BasicNeed.SOCIAL_CONNECTION: -0.02,  # Isolation
            BasicNeed.PURPOSE: -0.02   # Lack of meaningful activity
        }
        
        for need, decay in decay_rates.items():
            emotional_profile.needs[need] = max(0.0, 
                emotional_profile.needs[need] + decay + random.uniform(-0.01, 0.01))
        
        # Privilege benefits
        if emotional_profile.privileges[PrivilegeType.EXTRA_FOOD]:
            emotional_profile.needs[BasicNeed.FOOD] = min(1.0, 
                emotional_profile.needs[BasicNeed.FOOD] + 0.05)
        
        if emotional_profile.privileges[PrivilegeType.WORK_ASSIGNMENT]:
            emotional_profile.needs[BasicNeed.PURPOSE] = min(1.0,
                emotional_profile.needs[BasicNeed.PURPOSE] + 0.03)
        
        if emotional_profile.privileges[PrivilegeType.COMMISSARY]:
            emotional_profile.needs[BasicNeed.RESPECT] = min(1.0,
                emotional_profile.needs[BasicNeed.RESPECT] + 0.02)
        
        return emotional_profile
    
    def award_privilege(self, emotional_profile: EmotionalProfile, 
                       privilege: PrivilegeType, reason: str) -> EmotionalProfile:
        """Award a privilege for good behavior"""
        emotional_profile.privileges[privilege] = True
        
        # Positive emotional response
        if emotional_profile.current_emotion in [EmotionalState.ANGRY, EmotionalState.FRUSTRATED]:
            emotional_profile.current_emotion = EmotionalState.RESIGNED
        elif emotional_profile.current_emotion == EmotionalState.RESIGNED:
            emotional_profile.current_emotion = EmotionalState.HOPEFUL
        
        # Boost relevant needs
        emotional_profile.needs[BasicNeed.RESPECT] = min(1.0,
            emotional_profile.needs[BasicNeed.RESPECT] + 0.1)
        
        return emotional_profile
    
    def revoke_privilege(self, emotional_profile: EmotionalProfile,
                        privilege: PrivilegeType, reason: str) -> EmotionalProfile:
        """Revoke a privilege for bad behavior"""
        if privilege in [PrivilegeType.RECREATION_TIME, PrivilegeType.VISITOR_RIGHTS, PrivilegeType.LIBRARY_ACCESS]:
            # Can't revoke basic rights completely, just reduce
            pass
        else:
            emotional_profile.privileges[privilege] = False
        
        # Negative emotional response
        if emotional_profile.current_emotion == EmotionalState.CONTENT:
            emotional_profile.current_emotion = EmotionalState.FRUSTRATED
        elif emotional_profile.current_emotion in [EmotionalState.HOPEFUL, EmotionalState.RESIGNED]:
            emotional_profile.current_emotion = EmotionalState.ANGRY
        
        # Reduce needs
        emotional_profile.needs[BasicNeed.RESPECT] = max(0.0,
            emotional_profile.needs[BasicNeed.RESPECT] - 0.15)
        
        return emotional_profile

def test_emotional_system():
    """Test the emotional decision system"""
    print("🧠 Testing Emotional System")
    print("=" * 40)
    
    engine = EmotionalDecisionEngine()
    profile = EmotionalProfile()
    
    print(f"Initial emotion: {profile.current_emotion.value}")
    print(f"Initial wellbeing: {profile.get_overall_wellbeing():.2f}")
    
    # Test interaction impact
    profile = engine.update_emotions_from_interaction(
        profile, "cooperate", "defect", 0.0, "neutral"
    )
    print(f"After being exploited: {profile.current_emotion.value}")
    
    # Test cooperation modifier
    modifier = engine.calculate_emotional_cooperation_modifier(profile, 15)
    print(f"Cooperation modifier: {modifier:.2f}")
    
    # Test privilege award
    profile = engine.award_privilege(profile, PrivilegeType.EXTRA_FOOD, "good behavior")
    print(f"After earning privilege: {profile.current_emotion.value}")
    
    print(f"Final wellbeing: {profile.get_overall_wellbeing():.2f}")

if __name__ == "__main__":
    test_emotional_system()