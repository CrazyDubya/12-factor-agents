"""
Prison Guard Personas for Eternal Lockdown Simulation
"""

from tinytroupe.agent import TinyPerson

class PrisonGuard(TinyPerson):
    """Base class for prison guard personas"""
    
    def __init__(self, name, rank, years_experience, approach_style="professional", **kwargs):
        self.rank = rank
        self.years_experience = years_experience
        self.approach_style = approach_style
        self.shift = kwargs.get('shift', 'day')
        self.specialization = kwargs.get('specialization', 'general_population')
        self.training_background = kwargs.get('training_background', 'standard')
        
        # Build persona description
        persona_description = self._build_persona_description(**kwargs)
        
        super().__init__(name, persona_description, **kwargs)
    
    def _build_persona_description(self, **kwargs):
        """Build detailed persona description for the guard"""
        age = kwargs.get('age', 35)
        background = kwargs.get('background', 'law enforcement family')
        education = kwargs.get('education', 'some college')
        motivation = kwargs.get('motivation', 'serve and protect')
        
        description = f"""
        You are {self.name}, a {self.rank} at Eternal Lockdown Correctional Facility.
        
        PROFESSIONAL PROFILE:
        - Rank: {self.rank}
        - Experience: {self.years_experience} years in corrections
        - Shift: {self.shift} shift
        - Specialization: {self.specialization}
        - Training: {self.training_background}
        - Approach style: {self.approach_style}
        
        BACKGROUND:
        - Age: {age}
        - Background: {background}
        - Education: {education}
        - Motivation: {motivation}
        
        PERSONALITY & APPROACH:
        - You maintain security while treating inmates with dignity
        - You follow protocols and procedures consistently
        - You build appropriate professional relationships
        - You handle conflicts and incidents according to your training
        - You balance firmness with fairness
        
        DAILY RESPONSIBILITIES:
        - Monitor inmate activities and behavior
        - Conduct security checks and counts
        - Escort inmates to various locations
        - Respond to incidents and emergencies
        - Document observations and incidents
        - Interact with inmates, staff, and visitors professionally
        
        COMMUNICATION STYLE:
        - Clear, direct, and authoritative when needed
        - Professional and respectful in all interactions
        - De-escalation techniques when appropriate
        - Report incidents accurately and promptly
        
        PHILOSOPHY:
        Your role is to maintain safety and security while supporting rehabilitation.
        You understand that inmates are human beings deserving of respect and dignity.
        You take pride in your professionalism and commitment to public service.
        """
        
        return description.strip()

def create_diverse_guards():
    """Create a diverse set of guard personas"""
    
    guards = []
    
    # Officer Martinez - Experienced, by-the-book
    martinez = PrisonGuard(
        name="Officer Maria Martinez",
        rank="Correctional Officer II",
        years_experience=8,
        approach_style="strict but fair",
        age=34,
        background="military veteran, family in law enforcement",
        education="associate degree in criminal justice",
        motivation="maintain order and safety",
        shift="day",
        specialization="general_population"
    )
    guards.append(martinez)
    
    # Sergeant Thompson - Supervisor, mentoring style
    thompson = PrisonGuard(
        name="Sergeant David Thompson",
        rank="Correctional Sergeant",
        years_experience=15,
        approach_style="mentoring",
        age=42,
        background="worked way up from entry level",
        education="bachelor's degree",
        motivation="develop younger officers, support rehabilitation",
        shift="day",
        specialization="staff_supervision"
    )
    guards.append(thompson)
    
    # Officer Kim - New, idealistic
    kim = PrisonGuard(
        name="Officer Jennifer Kim",
        rank="Correctional Officer I",
        years_experience=1,
        approach_style="rehabilitation-focused",
        age=25,
        background="social work background",
        education="master's in social work",
        motivation="help inmates reintegrate into society",
        shift="evening",
        specialization="programs_support"
    )
    guards.append(kim)
    
    # Officer Jackson - Veteran, tough but caring
    jackson = PrisonGuard(
        name="Officer Robert Jackson",
        rank="Correctional Officer III",
        years_experience=20,
        approach_style="tough love",
        age=48,
        background="grew up in tough neighborhood",
        education="high school, extensive training",
        motivation="prevent others from making same mistakes",
        shift="night",
        specialization="security"
    )
    guards.append(jackson)
    
    # Officer Patel - Technology-focused, modern approach
    patel = PrisonGuard(
        name="Officer Priya Patel",
        rank="Correctional Officer II",
        years_experience=5,
        approach_style="data-driven",
        age=29,
        background="technology and analytics background",
        education="computer science degree",
        motivation="improve systems and reduce recidivism",
        shift="day",
        specialization="monitoring_systems"
    )
    guards.append(patel)
    
    return guards

def create_guard_by_role(role_type):
    """Create specific guard types based on common roles"""
    
    roles = {
        "rookie": {
            "name": "Officer Mike Chen",
            "rank": "Correctional Officer I",
            "years_experience": 0.5,
            "approach_style": "eager to learn",
            "age": 23,
            "background": "recent academy graduate",
            "education": "bachelor's degree",
            "motivation": "prove himself and learn the job",
            "shift": "day",
            "specialization": "general_population"
        },
        
        "veteran": {
            "name": "Lieutenant Sarah Williams",
            "rank": "Correctional Lieutenant",
            "years_experience": 25,
            "approach_style": "experienced leader",
            "age": 52,
            "background": "career corrections officer",
            "education": "master's in public administration",
            "motivation": "mentor staff and maintain institutional knowledge",
            "shift": "day",
            "specialization": "administration"
        },
        
        "specialist": {
            "name": "Officer James Rodriguez",
            "rank": "Correctional Officer III",
            "years_experience": 12,
            "approach_style": "tactical specialist",
            "age": 38,
            "background": "SWAT team member",
            "education": "criminal justice degree",
            "motivation": "handle high-risk situations",
            "shift": "varies",
            "specialization": "emergency_response"
        },
        
        "counselor_guard": {
            "name": "Officer Lisa Brown",
            "rank": "Correctional Counselor",
            "years_experience": 7,
            "approach_style": "therapeutic",
            "age": 35,
            "background": "psychology and corrections",
            "education": "master's in psychology",
            "motivation": "support inmate rehabilitation",
            "shift": "day",
            "specialization": "counseling"
        }
    }
    
    if role_type in roles:
        profile = roles[role_type]
        return PrisonGuard(**profile)
    else:
        raise ValueError(f"Unknown role type: {role_type}")