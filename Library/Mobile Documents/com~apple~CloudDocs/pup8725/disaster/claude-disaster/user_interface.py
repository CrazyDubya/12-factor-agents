#!/usr/bin/env python3
"""
Improved user interface with better UX and session management
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from models import FamilyProfile, LocationType
from validation import (
    InputValidator, safe_input, confirm_action, ProgressIndicator
)
from config import app_config

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages user sessions with save/resume capability"""
    
    def __init__(self, session_dir: Optional[str] = None):
        self.session_dir = Path(session_dir or app_config.output_dir) / "sessions"
        self.session_dir.mkdir(exist_ok=True)
        self.current_session: Optional[Dict[str, Any]] = None
        self.session_file: Optional[Path] = None
    
    def create_new_session(self) -> str:
        """Create a new session"""
        session_id = datetime.now().strftime("session_%Y%m%d_%H%M%S")
        self.session_file = self.session_dir / f"{session_id}.json"
        
        self.current_session = {
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'step': 0,
            'total_steps': 8,
            'data': {},
            'completed_steps': []
        }
        
        self.save_session()
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def save_session(self):
        """Save current session to file"""
        if self.current_session and self.session_file:
            try:
                self.current_session['last_updated'] = datetime.now().isoformat()
                with open(self.session_file, 'w') as f:
                    json.dump(self.current_session, f, indent=2)
                logger.debug(f"Session saved: {self.session_file}")
            except Exception as e:
                logger.error(f"Error saving session: {e}")
    
    def load_session(self, session_id: str) -> bool:
        """Load existing session"""
        session_file = self.session_dir / f"{session_id}.json"
        
        try:
            if session_file.exists():
                with open(session_file, 'r') as f:
                    self.current_session = json.load(f)
                self.session_file = session_file
                logger.info(f"Loaded session: {session_id}")
                return True
            else:
                logger.warning(f"Session file not found: {session_file}")
                return False
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            return False
    
    def list_sessions(self) -> List[Dict[str, str]]:
        """List available sessions"""
        sessions = []
        try:
            for session_file in self.session_dir.glob("session_*.json"):
                try:
                    with open(session_file, 'r') as f:
                        data = json.load(f)
                    
                    sessions.append({
                        'session_id': data['session_id'],
                        'created_at': data['created_at'],
                        'last_updated': data['last_updated'],
                        'progress': f"{len(data.get('completed_steps', []))}/{data.get('total_steps', 8)}"
                    })
                except Exception as e:
                    logger.warning(f"Error reading session file {session_file}: {e}")
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
        
        return sorted(sessions, key=lambda x: x['last_updated'], reverse=True)
    
    def update_step(self, step: int, step_name: str, data: Dict[str, Any]):
        """Update current step and save data"""
        if self.current_session:
            self.current_session['step'] = step
            self.current_session['data'].update(data)
            if step_name not in self.current_session['completed_steps']:
                self.current_session['completed_steps'].append(step_name)
            self.save_session()
    
    def get_session_data(self, key: str, default: Any = None) -> Any:
        """Get data from current session"""
        if self.current_session:
            return self.current_session['data'].get(key, default)
        return default
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        session_file = self.session_dir / f"{session_id}.json"
        try:
            if session_file.exists():
                session_file.unlink()
                logger.info(f"Deleted session: {session_id}")
                return True
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
        return False

class ImprovedUserInterface:
    """Enhanced user interface with better UX"""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.validator = InputValidator()
    
    def show_welcome(self):
        """Display welcome message and options"""
        print("\n" + "="*70)
        print("🏠 FAMILY DISASTER PREPAREDNESS ASSESSMENT")
        print("="*70)
        print("Welcome! This tool will help you assess your family's disaster risks")
        print("and create a personalized preparedness plan.")
        print("\nFeatures:")
        print("  ✅ Personalized risk assessment")
        print("  ✅ Save and resume sessions")
        print("  ✅ Comprehensive recommendations")
        print("  ✅ Export results and action plans")
        print("\n" + "="*70)
    
    def show_session_menu(self) -> str:
        """Show session management menu"""
        print("\n📋 SESSION MANAGEMENT")
        print("-" * 30)
        print("1. Start new assessment")
        print("2. Resume previous session")
        print("3. View session history")
        print("4. Delete old sessions")
        print("5. Exit")
        
        choice = safe_input(
            "\nSelect option (1-5): ",
            lambda x: self.validator.validate_choice(x, ['1', '2', '3', '4', '5'], "Choice"),
            help_text="Enter a number from 1 to 5"
        )
        
        return choice or "5"
    
    def handle_resume_session(self) -> Optional[str]:
        """Handle resuming a previous session"""
        sessions = self.session_manager.list_sessions()
        
        if not sessions:
            print("\n❌ No previous sessions found.")
            return None
        
        print("\n📁 AVAILABLE SESSIONS")
        print("-" * 50)
        print(f"{'#':<3} {'Session ID':<20} {'Progress':<10} {'Last Updated'}")
        print("-" * 50)
        
        for i, session in enumerate(sessions[:10], 1):  # Show max 10 sessions
            last_updated = datetime.fromisoformat(session['last_updated']).strftime("%m/%d %H:%M")
            print(f"{i:<3} {session['session_id']:<20} {session['progress']:<10} {last_updated}")
        
        if len(sessions) > 10:
            print(f"... and {len(sessions) - 10} more sessions")
        
        choice = safe_input(
            f"\nSelect session (1-{min(len(sessions), 10)}) or 0 to cancel: ",
            lambda x: self.validator.validate_choice(
                x, [str(i) for i in range(len(sessions) + 1)], "Session choice"
            ),
            help_text="Enter the session number or 0 to go back"
        )
        
        if choice and choice != "0":
            session_index = int(choice) - 1
            session_id = sessions[session_index]['session_id']
            
            if self.session_manager.load_session(session_id):
                print(f"✅ Loaded session: {session_id}")
                return session_id
            else:
                print(f"❌ Failed to load session: {session_id}")
        
        return None
    
    def collect_family_demographics(self) -> Optional[Dict[str, Any]]:
        """Collect family demographic information with improved UX"""
        print("\n👨‍👩‍👧‍👦 FAMILY DEMOGRAPHICS")
        print("-" * 30)
        print("Let's start by learning about your family composition.")
        
        progress = ProgressIndicator(6, "Collecting demographics")
        
        # Number of adults
        progress.update(1, "Adults in household")
        adults = safe_input(
            "\nHow many adults (18+) live in your household? ",
            lambda x: self.validator.validate_positive_int(x, "Number of adults"),
            help_text="Include all adults who live in your home full-time"
        )
        
        if adults is None:
            return None
        
        # Adult ages
        progress.update(2, "Adult ages")
        adult_ages = []
        for i in range(adults):
            age = safe_input(
                f"Age of adult #{i+1}: ",
                self.validator.validate_adult_age,
                help_text="Age must be 18 or older"
            )
            if age is None:
                return None
            adult_ages.append(age)
        
        # Number of children
        progress.update(3, "Children in household")
        children = safe_input(
            "\nHow many children (under 18) live in your household? ",
            lambda x: self.validator.validate_positive_int(x, "Number of children"),
            help_text="Include all children who live in your home full-time"
        )
        
        if children is None:
            return None
        
        # Child ages
        progress.update(4, "Child ages")
        child_ages = []
        for i in range(children):
            age = safe_input(
                f"Age of child #{i+1}: ",
                self.validator.validate_child_age,
                help_text="Age must be under 18"
            )
            if age is None:
                return None
            child_ages.append(age)
        
        # Location type
        progress.update(5, "Location type")
        location_choices = [loc.value for loc in LocationType]
        location_str = safe_input(
            f"\nWhat type of area do you live in? ({'/'.join(location_choices)}): ",
            lambda x: self.validator.validate_choice(x, location_choices, "Location type"),
            help_text="Urban = city center, Suburban = residential area, Rural = countryside"
        )
        
        if location_str is None:
            return None
        
        location_type = LocationType(location_str)
        
        # Income range
        progress.update(6, "Income information")
        income_ranges = ["<30k", "30-50k", "50-75k", "75-100k", "100-150k", ">150k"]
        income_range = safe_input(
            f"\nHousehold income range? ({'/'.join(income_ranges)}): ",
            lambda x: self.validator.validate_choice(x, income_ranges, "Income range"),
            help_text="This helps assess financial resilience and insurance needs"
        )
        
        if income_range is None:
            return None
        
        progress.finish("Demographics complete")
        
        return {
            'adults': adults,
            'children': children,
            'adult_ages': adult_ages,
            'child_ages': child_ages,
            'location_type': location_type,
            'income_range': income_range
        }
    
    def collect_housing_information(self) -> Optional[Dict[str, Any]]:
        """Collect housing and living situation information"""
        print("\n🏠 HOUSING INFORMATION")
        print("-" * 30)
        
        progress = ProgressIndicator(4, "Housing details")
        
        # Housing type
        progress.update(1, "Housing type")
        housing_types = ["house", "apartment", "condo", "mobile_home", "other"]
        housing_type = safe_input(
            f"What type of housing do you live in? ({'/'.join(housing_types)}): ",
            lambda x: self.validator.validate_choice(x, housing_types, "Housing type"),
            help_text="This affects evacuation planning and emergency preparations"
        )
        
        if housing_type is None:
            return None
        
        # Home ownership
        progress.update(2, "Ownership status")
        own_home = safe_input(
            "Do you own your home? (y/n): ",
            lambda x: self.validator.validate_yes_no(x, "Home ownership"),
            help_text="Affects insurance needs and modification options"
        )
        
        if own_home is None:
            return None
        
        # Emergency fund
        progress.update(3, "Emergency fund")
        emergency_fund = safe_input(
            "How many months of expenses do you have in emergency savings? ",
            lambda x: self.validator.validate_positive_float(x, "Emergency fund months"),
            help_text="Include easily accessible savings, not retirement accounts"
        )
        
        if emergency_fund is None:
            return None
        
        # Dual income
        progress.update(4, "Income sources")
        dual_income = safe_input(
            "Is this a dual-income household? (y/n): ",
            lambda x: self.validator.validate_yes_no(x, "Dual income"),
            help_text="Affects financial vulnerability to job loss"
        )
        
        if dual_income is None:
            return None
        
        progress.finish("Housing information complete")
        
        return {
            'housing_type': housing_type,
            'own_home': own_home,
            'emergency_fund_months': emergency_fund,
            'dual_income': dual_income
        }
    
    def collect_health_information(self) -> Optional[Dict[str, Any]]:
        """Collect health-related information"""
        print("\n🏥 HEALTH INFORMATION")
        print("-" * 30)
        print("This information helps assess health-related risks and needs.")
        
        progress = ProgressIndicator(4, "Health assessment")
        
        # Chronic conditions
        progress.update(1, "Chronic conditions")
        chronic_conditions = safe_input(
            "Does anyone in your family have chronic health conditions? (y/n): ",
            lambda x: self.validator.validate_yes_no(x, "Chronic conditions"),
            help_text="Diabetes, heart disease, asthma, etc."
        )
        
        if chronic_conditions is None:
            return None
        
        # Mobility issues
        progress.update(2, "Mobility assessment")
        mobility_issues = safe_input(
            "Does anyone have mobility limitations? (y/n): ",
            lambda x: self.validator.validate_yes_no(x, "Mobility issues"),
            help_text="Wheelchair use, walking difficulties, etc."
        )
        
        if mobility_issues is None:
            return None
        
        # Medication dependency
        progress.update(3, "Medication needs")
        medication_dependent = safe_input(
            "Is anyone dependent on daily medications? (y/n): ",
            lambda x: self.validator.validate_yes_no(x, "Medication dependency"),
            help_text="Prescription medications needed daily"
        )
        
        if medication_dependent is None:
            return None
        
        progress.finish("Health information complete")
        
        return {
            'chronic_conditions': chronic_conditions,
            'mobility_issues': mobility_issues,
            'medication_dependent': medication_dependent
        }
    
    def collect_special_circumstances(self) -> Optional[Dict[str, Any]]:
        """Collect information about special circumstances"""
        print("\n🔍 SPECIAL CIRCUMSTANCES")
        print("-" * 30)
        print("These factors can affect your emergency planning needs.")
        
        progress = ProgressIndicator(3, "Special circumstances")
        
        # Pets
        progress.update(1, "Pet ownership")
        pets = safe_input(
            "Do you have pets? (y/n): ",
            lambda x: self.validator.validate_yes_no(x, "Pet ownership"),
            help_text="Affects evacuation planning and emergency supplies"
        )
        
        if pets is None:
            return None
        
        # Elderly care
        progress.update(2, "Caregiving responsibilities")
        elderly_care = safe_input(
            "Are you responsible for elderly relatives? (y/n): ",
            lambda x: self.validator.validate_yes_no(x, "Elderly care"),
            help_text="Either living with you or nearby dependents"
        )
        
        if elderly_care is None:
            return None
        
        # Home business
        progress.update(3, "Home business")
        home_business = safe_input(
            "Do you run a business from home? (y/n): ",
            lambda x: self.validator.validate_yes_no(x, "Home business"),
            help_text="Affects infrastructure dependency and income vulnerability"
        )
        
        if home_business is None:
            return None
        
        progress.finish("Special circumstances complete")
        
        return {
            'pets': pets,
            'elderly_care': elderly_care,
            'home_business': home_business
        }
    
    def create_family_profile(self) -> Optional[FamilyProfile]:
        """Create complete family profile through guided collection"""
        print("\n🎯 CREATING YOUR FAMILY PROFILE")
        print("=" * 50)
        print("We'll collect information in several steps. You can save and resume anytime.")
        
        # Check if resuming session
        session_data = self.session_manager.get_session_data('profile_data', {})
        
        # Collect demographics
        if 'demographics' not in session_data:
            demographics = self.collect_family_demographics()
            if demographics is None:
                return None
            session_data['demographics'] = demographics
            self.session_manager.update_step(1, 'demographics', {'profile_data': session_data})
        
        # Collect housing information
        if 'housing' not in session_data:
            housing = self.collect_housing_information()
            if housing is None:
                return None
            session_data['housing'] = housing
            self.session_manager.update_step(2, 'housing', {'profile_data': session_data})
        
        # Collect health information
        if 'health' not in session_data:
            health = self.collect_health_information()
            if health is None:
                return None
            session_data['health'] = health
            self.session_manager.update_step(3, 'health', {'profile_data': session_data})
        
        # Collect special circumstances
        if 'special' not in session_data:
            special = self.collect_special_circumstances()
            if special is None:
                return None
            session_data['special'] = special
            self.session_manager.update_step(4, 'special', {'profile_data': session_data})
        
        # Create profile
        try:
            profile = FamilyProfile(
                adults=session_data['demographics']['adults'],
                children=session_data['demographics']['children'],
                adult_ages=session_data['demographics']['adult_ages'],
                child_ages=session_data['demographics']['child_ages'],
                location_type=session_data['demographics']['location_type'],
                income_range=session_data['demographics']['income_range'],
                emergency_fund_months=session_data['housing']['emergency_fund_months'],
                housing_type=session_data['housing']['housing_type'],
                own_home=session_data['housing']['own_home'],
                dual_income=session_data['housing']['dual_income'],
                chronic_conditions=session_data['health']['chronic_conditions'],
                mobility_issues=session_data['health']['mobility_issues'],
                medication_dependent=session_data['health']['medication_dependent'],
                pets=session_data['special']['pets'],
                elderly_care=session_data['special']['elderly_care'],
                home_business=session_data['special']['home_business']
            )
            
            print("\n✅ Family profile created successfully!")
            return profile
            
        except Exception as e:
            logger.error(f"Error creating family profile: {e}")
            print(f"\n❌ Error creating profile: {e}")
            return None
    
    def display_profile_summary(self, profile: FamilyProfile):
        """Display a summary of the family profile"""
        print("\n📊 FAMILY PROFILE SUMMARY")
        print("=" * 40)
        print(f"Family Size: {profile.total_family_size} members")
        print(f"  Adults: {profile.adults} (avg age: {profile.average_adult_age:.0f})")
        print(f"  Children: {profile.children}")
        
        if profile.child_ages:
            print(f"  Child ages: {', '.join(map(str, profile.child_ages))}")
        
        print(f"Location: {profile.location_type.value.title()}")
        print(f"Income Range: {profile.income_range}")
        print(f"Emergency Fund: {profile.emergency_fund_months:.1f} months")
        print(f"Housing: {profile.housing_type.title()} ({'Owned' if profile.own_home else 'Rented'})")
        
        special_factors = []
        if profile.chronic_conditions:
            special_factors.append("Chronic conditions")
        if profile.mobility_issues:
            special_factors.append("Mobility issues")
        if profile.medication_dependent:
            special_factors.append("Medication dependent")
        if profile.pets:
            special_factors.append("Pets")
        if profile.elderly_care:
            special_factors.append("Elderly care")
        if profile.home_business:
            special_factors.append("Home business")
        
        if special_factors:
            print(f"Special Factors: {', '.join(special_factors)}")
        
        print("=" * 40)
    
    def confirm_profile(self, profile: FamilyProfile) -> bool:
        """Confirm profile information with user"""
        self.display_profile_summary(profile)
        return confirm_action("\nIs this information correct?", default=True)