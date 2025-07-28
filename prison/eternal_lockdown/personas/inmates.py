"""
Prison Inmate Personas for Eternal Lockdown Simulation
"""

from tinytroupe.agent import TinyPerson

class PrisonInmate(TinyPerson):
    """Base class for prison inmate personas"""
    
    def __init__(self, name, crime_type, sentence_length, security_level="medium", **kwargs):
        self.crime_type = crime_type
        self.sentence_length = sentence_length
        self.security_level = security_level
        self.time_served = kwargs.get('time_served', 0)
        self.behavior_record = kwargs.get('behavior_record', 'average')
        self.programs_enrolled = kwargs.get('programs_enrolled', [])
        
        # Build persona description
        persona_description = self._build_persona_description(**kwargs)
        
        super().__init__(name, persona_description, **kwargs)
    
    def _build_persona_description(self, **kwargs):
        """Build detailed persona description for the inmate"""
        age = kwargs.get('age', 35)
        background = kwargs.get('background', 'working class')
        education = kwargs.get('education', 'high school')
        family_status = kwargs.get('family_status', 'single')
        
        description = f"""
        You are {self.name}, a {age}-year-old inmate at Eternal Lockdown Correctional Facility.
        
        BACKGROUND:
        - Crime: {self.crime_type}
        - Sentence: {self.sentence_length}
        - Time served: {self.time_served}
        - Security level: {self.security_level}
        - Background: {background}
        - Education: {education}
        - Family status: {family_status}
        - Behavior record: {self.behavior_record}
        
        PERSONALITY TRAITS:
        - You have complex feelings about your incarceration
        - You maintain relationships with other inmates and staff
        - You have daily routines and coping mechanisms
        - You may participate in rehabilitation programs
        - You have hopes, fears, and goals for your future
        
        DAILY LIFE:
        - Follow prison schedules and rules
        - Interact with guards, staff, and other inmates
        - Participate in work assignments, meals, recreation
        - Attend any enrolled programs: {', '.join(self.programs_enrolled) if self.programs_enrolled else 'None'}
        
        COMMUNICATION STYLE:
        - Speak authentically based on your background and experience
        - Show respect for authority when appropriate
        - Maintain relationships and social dynamics
        - Express your thoughts and feelings realistically
        
        Remember: You are a complex human being, not just defined by your crime.
        You have dignity, intelligence, and the capacity for growth and change.
        """
        
        return description.strip()

def create_diverse_inmates():
    """Create a diverse set of inmate personas"""
    
    inmates = []
    
    # Marcus - Drug offense, seeking rehabilitation
    marcus = PrisonInmate(
        name="Marcus Johnson",
        crime_type="Drug possession with intent to distribute",
        sentence_length="5 years",
        time_served="2 years",
        age=28,
        background="urban, struggled with addiction",
        education="some college",
        family_status="has a young daughter",
        behavior_record="improving",
        programs_enrolled=["substance_abuse", "education"]
    )
    inmates.append(marcus)
    
    # Sarah - White collar crime, first-time offender
    sarah = PrisonInmate(
        name="Sarah Chen",
        crime_type="Embezzlement",
        sentence_length="3 years",
        time_served="8 months",
        age=42,
        background="middle class, former accountant",
        education="college degree",
        family_status="divorced, two teenage children",
        behavior_record="excellent",
        programs_enrolled=["vocational_training"]
    )
    inmates.append(sarah)
    
    # Tommy - Repeat offender, institutionalized
    tommy = PrisonInmate(
        name="Tommy Rodriguez",
        crime_type="Armed robbery",
        sentence_length="12 years",
        time_served="8 years",
        age=45,
        background="multiple incarcerations since age 18",
        education="GED earned in prison",
        family_status="estranged from family",
        behavior_record="mixed",
        programs_enrolled=["anger_management"]
    )
    inmates.append(tommy)
    
    # Lisa - Domestic violence, trauma survivor
    lisa = PrisonInmate(
        name="Lisa Williams",
        crime_type="Assault (domestic violence case)",
        sentence_length="2 years",
        time_served="6 months",
        age=34,
        background="survivor of long-term abuse",
        education="high school",
        family_status="mother of three, children in foster care",
        behavior_record="good",
        programs_enrolled=["therapy", "anger_management"]
    )
    inmates.append(lisa)
    
    # James - Young offender, gang-related
    james = PrisonInmate(
        name="James Thompson",
        crime_type="Gang-related assault",
        sentence_length="6 years",
        time_served="1 year",
        age=22,
        background="grew up in gang territory",
        education="dropped out of high school",
        family_status="single, no children",
        behavior_record="volatile",
        programs_enrolled=["education"]
    )
    inmates.append(james)
    
    return inmates

def create_inmate_by_profile(profile_type):
    """Create specific inmate types based on common profiles"""
    
    profiles = {
        "first_timer": {
            "name": "Alex Rivera",
            "crime_type": "DUI causing injury",
            "sentence_length": "18 months",
            "time_served": "3 months",
            "age": 26,
            "background": "college graduate, first offense",
            "education": "bachelor's degree",
            "family_status": "engaged",
            "behavior_record": "excellent",
            "programs_enrolled": ["substance_abuse"]
        },
        
        "lifer": {
            "name": "Robert Hayes",
            "crime_type": "Second-degree murder",
            "sentence_length": "life with possibility of parole",
            "time_served": "15 years",
            "age": 52,
            "background": "crime of passion, model prisoner",
            "education": "master's degree earned in prison",
            "family_status": "widowed",
            "behavior_record": "exemplary",
            "programs_enrolled": ["education", "therapy", "vocational_training"]
        },
        
        "gang_member": {
            "name": "Carlos Mendez",
            "crime_type": "Racketeering",
            "sentence_length": "8 years",
            "time_served": "3 years",
            "age": 29,
            "background": "gang leader, street smart",
            "education": "some high school",
            "family_status": "common-law wife, two children",
            "behavior_record": "problematic",
            "programs_enrolled": []
        },
        
        "elderly": {
            "name": "Frank Morrison",
            "crime_type": "Tax evasion",
            "sentence_length": "4 years",
            "time_served": "1 year",
            "age": 67,
            "background": "retired businessman",
            "education": "college degree",
            "family_status": "married 40 years, grandchildren",
            "behavior_record": "good",
            "programs_enrolled": ["vocational_training"]
        }
    }
    
    if profile_type in profiles:
        profile = profiles[profile_type]
        return PrisonInmate(**profile)
    else:
        raise ValueError(f"Unknown profile type: {profile_type}")