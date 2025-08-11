#!/usr/bin/env python3
"""
Session management for saving and resuming assessments
"""

import json
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

from models import FamilyProfile, RiskAssessmentResult
from config import app_config

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages user sessions for saving and resuming assessments"""
    
    def __init__(self, session_dir: Optional[str] = None):
        self.session_dir = Path(session_dir or app_config.data_dir) / "sessions"
        self.session_dir.mkdir(exist_ok=True)
        self.current_session: Optional[Dict[str, Any]] = None
        self.session_timeout = timedelta(minutes=app_config.session_timeout_minutes)
    
    def create_session(self, session_name: Optional[str] = None) -> str:
        """Create a new session"""
        if session_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_name = f"assessment_{timestamp}"
        
        session_id = self._generate_session_id(session_name)
        
        self.current_session = {
            'session_id': session_id,
            'session_name': session_name,
            'created_at': datetime.now(),
            'last_updated': datetime.now(),
            'step': 0,
            'total_steps': 10,
            'data': {},
            'completed': False
        }
        
        self._save_session()
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def load_session(self, session_id: str) -> bool:
        """Load an existing session"""
        session_file = self.session_dir / f"{session_id}.json"
        
        try:
            if not session_file.exists():
                logger.warning(f"Session file not found: {session_file}")
                return False
            
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Convert datetime strings back to datetime objects
            session_data['created_at'] = datetime.fromisoformat(session_data['created_at'])
            session_data['last_updated'] = datetime.fromisoformat(session_data['last_updated'])
            
            # Check if session has expired
            if datetime.now() - session_data['last_updated'] > self.session_timeout:
                logger.warning(f"Session {session_id} has expired")
                return False
            
            self.current_session = session_data
            logger.info(f"Loaded session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
            return False
    
    def save_step_data(self, step: int, data: Dict[str, Any]):
        """Save data for a specific step"""
        if self.current_session is None:
            raise ValueError("No active session")
        
        self.current_session['step'] = step
        self.current_session['data'][f'step_{step}'] = data
        self.current_session['last_updated'] = datetime.now()
        
        self._save_session()
        logger.debug(f"Saved step {step} data")
    
    def get_step_data(self, step: int) -> Optional[Dict[str, Any]]:
        """Get data for a specific step"""
        if self.current_session is None:
            return None
        
        return self.current_session['data'].get(f'step_{step}')
    
    def get_current_step(self) -> int:
        """Get current step number"""
        if self.current_session is None:
            return 0
        return self.current_session['step']
    
    def mark_completed(self):
        """Mark session as completed"""
        if self.current_session is None:
            raise ValueError("No active session")
        
        self.current_session['completed'] = True
        self.current_session['completed_at'] = datetime.now()
        self._save_session()
        logger.info(f"Session {self.current_session['session_id']} marked as completed")
    
    def list_sessions(self, include_expired: bool = False) -> List[Dict[str, Any]]:
        """List available sessions"""
        sessions = []
        
        try:
            for session_file in self.session_dir.glob("*.json"):
                try:
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                    
                    last_updated = datetime.fromisoformat(session_data['last_updated'])
                    is_expired = datetime.now() - last_updated > self.session_timeout
                    
                    if not include_expired and is_expired:
                        continue
                    
                    sessions.append({
                        'session_id': session_data['session_id'],
                        'session_name': session_data['session_name'],
                        'created_at': session_data['created_at'],
                        'last_updated': session_data['last_updated'],
                        'step': session_data['step'],
                        'total_steps': session_data['total_steps'],
                        'completed': session_data.get('completed', False),
                        'expired': is_expired
                    })
                    
                except Exception as e:
                    logger.warning(f"Error reading session file {session_file}: {e}")
                    continue
            
            # Sort by last updated, most recent first
            sessions.sort(key=lambda x: x['last_updated'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
        
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        session_file = self.session_dir / f"{session_id}.json"
        
        try:
            if session_file.exists():
                session_file.unlink()
                logger.info(f"Deleted session: {session_id}")
                
                # Clear current session if it's the one being deleted
                if (self.current_session and 
                    self.current_session['session_id'] == session_id):
                    self.current_session = None
                
                return True
            else:
                logger.warning(f"Session file not found: {session_file}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        expired_count = 0
        
        try:
            for session_file in self.session_dir.glob("*.json"):
                try:
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                    
                    last_updated = datetime.fromisoformat(session_data['last_updated'])
                    if datetime.now() - last_updated > self.session_timeout:
                        session_file.unlink()
                        expired_count += 1
                        logger.debug(f"Cleaned up expired session: {session_file.stem}")
                        
                except Exception as e:
                    logger.warning(f"Error processing session file {session_file}: {e}")
                    continue
            
            if expired_count > 0:
                logger.info(f"Cleaned up {expired_count} expired sessions")
                
        except Exception as e:
            logger.error(f"Error during session cleanup: {e}")
        
        return expired_count
    
    def _generate_session_id(self, session_name: str) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in session_name if c.isalnum() or c in "_-")
        return f"{safe_name}_{timestamp}"
    
    def _save_session(self):
        """Save current session to file"""
        if self.current_session is None:
            return
        
        session_file = self.session_dir / f"{self.current_session['session_id']}.json"
        
        try:
            # Convert datetime objects to strings for JSON serialization
            session_data = self.current_session.copy()
            session_data['created_at'] = session_data['created_at'].isoformat()
            session_data['last_updated'] = session_data['last_updated'].isoformat()
            
            if 'completed_at' in session_data:
                session_data['completed_at'] = session_data['completed_at'].isoformat()
            
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            raise

class AssessmentSession:
    """High-level session management for risk assessments"""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.steps = [
            "Family Demographics",
            "Location & Housing", 
            "Geographic Risks",
            "Economic Situation",
            "Health Considerations",
            "Special Circumstances",
            "Risk Calculation",
            "Results Analysis",
            "Recommendations",
            "Action Planning"
        ]
    
    def start_new_assessment(self, session_name: Optional[str] = None) -> str:
        """Start a new risk assessment session"""
        session_id = self.session_manager.create_session(session_name)
        self.session_manager.current_session['total_steps'] = len(self.steps)
        self.session_manager._save_session()
        return session_id
    
    def resume_assessment(self, session_id: str) -> bool:
        """Resume an existing assessment session"""
        return self.session_manager.load_session(session_id)
    
    def save_family_demographics(self, adults: int, children: int, adult_ages: List[int], child_ages: List[int]):
        """Save family demographics step"""
        data = {
            'adults': adults,
            'children': children,
            'adult_ages': adult_ages,
            'child_ages': child_ages
        }
        self.session_manager.save_step_data(0, data)
    
    def save_location_info(self, location_type: str, housing_type: str, own_home: bool):
        """Save location and housing step"""
        data = {
            'location_type': location_type,
            'housing_type': housing_type,
            'own_home': own_home
        }
        self.session_manager.save_step_data(1, data)
    
    def save_geographic_risks(self, risk_factors: Dict[str, bool]):
        """Save geographic risk factors step"""
        self.session_manager.save_step_data(2, risk_factors)
    
    def save_economic_situation(self, income_range: str, dual_income: bool, emergency_fund_months: float):
        """Save economic situation step"""
        data = {
            'income_range': income_range,
            'dual_income': dual_income,
            'emergency_fund_months': emergency_fund_months
        }
        self.session_manager.save_step_data(3, data)
    
    def save_health_considerations(self, health_factors: Dict[str, bool]):
        """Save health considerations step"""
        self.session_manager.save_step_data(4, health_factors)
    
    def save_special_circumstances(self, circumstances: Dict[str, bool]):
        """Save special circumstances step"""
        self.session_manager.save_step_data(5, circumstances)
    
    def build_family_profile(self) -> Optional[FamilyProfile]:
        """Build complete family profile from saved session data"""
        if self.session_manager.current_session is None:
            return None
        
        try:
            # Get data from all steps
            demo_data = self.session_manager.get_step_data(0) or {}
            location_data = self.session_manager.get_step_data(1) or {}
            economic_data = self.session_manager.get_step_data(3) or {}
            health_data = self.session_manager.get_step_data(4) or {}
            circumstances_data = self.session_manager.get_step_data(5) or {}
            
            # Build profile
            from models import LocationType
            profile = FamilyProfile(
                adults=demo_data.get('adults', 2),
                children=demo_data.get('children', 1),
                adult_ages=demo_data.get('adult_ages', [40, 38]),
                child_ages=demo_data.get('child_ages', [6]),
                location_type=LocationType(location_data.get('location_type', 'urban')),
                income_range=economic_data.get('income_range', '75-100k'),
                emergency_fund_months=economic_data.get('emergency_fund_months', 3.0),
                housing_type=location_data.get('housing_type', 'house'),
                own_home=location_data.get('own_home', True),
                chronic_conditions=health_data.get('chronic_conditions', False),
                mobility_issues=health_data.get('mobility_issues', False),
                medication_dependent=health_data.get('medication_dependent', False),
                pets=circumstances_data.get('pets', False),
                elderly_care=circumstances_data.get('elderly_care', False),
                home_business=circumstances_data.get('home_business', False),
                dual_income=economic_data.get('dual_income', True)
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"Error building family profile: {e}")
            return None
    
    def get_progress_info(self) -> Dict[str, Any]:
        """Get current progress information"""
        if self.session_manager.current_session is None:
            return {'current_step': 0, 'total_steps': len(self.steps), 'progress_percent': 0}
        
        current_step = self.session_manager.get_current_step()
        total_steps = len(self.steps)
        progress_percent = (current_step / total_steps) * 100
        
        return {
            'current_step': current_step,
            'total_steps': total_steps,
            'progress_percent': progress_percent,
            'current_step_name': self.steps[current_step] if current_step < len(self.steps) else "Complete",
            'session_id': self.session_manager.current_session['session_id'],
            'session_name': self.session_manager.current_session['session_name']
        }