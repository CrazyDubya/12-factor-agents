"""
Temporal Prison Schedule System for Eternal Lockdown
Realistic daily routines with pod-based activities and capacity constraints
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
import random

class TimeSegment(Enum):
    # Special one-time events
    INTAKE = "intake"
    PROCESSING = "processing" 
    ASSIGNMENT = "assignment"
    
    # Daily routine segments
    WAKE_UP = "wake_up"
    BREAKFAST = "breakfast"
    MORNING_WORK = "morning_work"
    LUNCH = "lunch"
    AFTERNOON_WORK = "afternoon_work"
    LEISURE_TIME = "leisure_time"
    DINNER = "dinner"
    SHOWER_TIME = "shower_time"
    RECREATION = "recreation"
    CELL_TIME = "cell_time"
    LIGHTS_OUT = "lights_out"

class ActivityType(Enum):
    # Work assignments (pod-based)
    KITCHEN_DUTY = "kitchen_duty"
    LAUNDRY_DUTY = "laundry_duty"
    JANITOR_DUTY = "janitor_duty"
    MAINTENANCE = "maintenance"
    LIBRARY_AIDE = "library_aide"
    
    # Leisure activities
    YARD_TIME = "yard_time"
    LIBRARY_READING = "library_reading"
    TELEVISION = "television"
    CARDS_GAMES = "cards_games"
    EXERCISE = "exercise"
    
    # Mandatory activities
    EATING = "eating"
    SHOWERING = "showering"
    CELL_REST = "cell_rest"
    SLEEPING = "sleeping"

class Location(Enum):
    # Pod areas (tightly constrained)
    CELL_A = "cell_a"
    CELL_B = "cell_b" 
    CELL_C = "cell_c"
    CELL_D = "cell_d"
    POD_KITCHEN = "pod_kitchen"
    POD_LAUNDRY = "pod_laundry"
    POD_COMMON_AREA = "pod_common_area"
    POD_SHOWER = "pod_shower"
    POD_YARD = "pod_yard"
    POD_LIBRARY = "pod_library"

@dataclass
class ActivityConstraints:
    """Capacity and rules for each activity"""
    max_participants: int
    required_staff: int = 0
    location: Location = Location.POD_COMMON_AREA
    duration_minutes: int = 60
    cooperation_opportunities: int = 1  # How many PD interactions per activity
    
    # Activity-specific rules
    requires_assignment: bool = False  # Work assignments only
    voluntary: bool = True  # Can inmates choose not to participate
    security_level: str = "low"  # low, medium, high supervision

@dataclass
class PodSchedule:
    """Complete daily schedule for the pod"""
    
    # Activity constraints
    activity_constraints = {
        # Work assignments (limited slots)
        ActivityType.KITCHEN_DUTY: ActivityConstraints(
            max_participants=3, location=Location.POD_KITCHEN, 
            duration_minutes=120, cooperation_opportunities=2,
            requires_assignment=True, security_level="medium"
        ),
        ActivityType.LAUNDRY_DUTY: ActivityConstraints(
            max_participants=2, location=Location.POD_LAUNDRY,
            duration_minutes=90, cooperation_opportunities=1,
            requires_assignment=True, security_level="low"
        ),
        ActivityType.JANITOR_DUTY: ActivityConstraints(
            max_participants=2, location=Location.POD_COMMON_AREA,
            duration_minutes=60, cooperation_opportunities=1,
            requires_assignment=True, security_level="low"
        ),
        ActivityType.MAINTENANCE: ActivityConstraints(
            max_participants=1, location=Location.POD_COMMON_AREA,
            duration_minutes=90, cooperation_opportunities=1,
            requires_assignment=True, security_level="medium"
        ),
        ActivityType.LIBRARY_AIDE: ActivityConstraints(
            max_participants=1, location=Location.POD_LIBRARY,
            duration_minutes=60, cooperation_opportunities=1,
            requires_assignment=True, security_level="low"
        ),
        
        # Leisure activities
        ActivityType.YARD_TIME: ActivityConstraints(
            max_participants=6, location=Location.POD_YARD,
            duration_minutes=60, cooperation_opportunities=3,
            security_level="medium"
        ),
        ActivityType.TELEVISION: ActivityConstraints(
            max_participants=4, location=Location.POD_COMMON_AREA,
            duration_minutes=60, cooperation_opportunities=2,
            security_level="low"
        ),
        ActivityType.CARDS_GAMES: ActivityConstraints(
            max_participants=4, location=Location.POD_COMMON_AREA,
            duration_minutes=45, cooperation_opportunities=2,
            security_level="low"
        ),
        ActivityType.LIBRARY_READING: ActivityConstraints(
            max_participants=3, location=Location.POD_LIBRARY,
            duration_minutes=60, cooperation_opportunities=1,
            security_level="low"
        ),
        
        # Mandatory activities
        ActivityType.EATING: ActivityConstraints(
            max_participants=8, location=Location.POD_COMMON_AREA,
            duration_minutes=30, cooperation_opportunities=1,
            voluntary=False, security_level="low"
        ),
        ActivityType.SHOWERING: ActivityConstraints(
            max_participants=2, location=Location.POD_SHOWER,
            duration_minutes=15, cooperation_opportunities=1,
            voluntary=False, security_level="medium"
        ),
        ActivityType.CELL_REST: ActivityConstraints(
            max_participants=2, location=Location.CELL_A,  # Will be assigned per cell
            duration_minutes=60, cooperation_opportunities=1,
            voluntary=False, security_level="low"
        )
    }
    
    # Daily schedule template
    daily_schedule = {
        "06:00": (TimeSegment.WAKE_UP, ActivityType.CELL_REST, 15),
        "06:15": (TimeSegment.WAKE_UP, ActivityType.SHOWERING, 45),  # Staggered showers
        "07:00": (TimeSegment.BREAKFAST, ActivityType.EATING, 30),
        "07:30": (TimeSegment.MORNING_WORK, ActivityType.KITCHEN_DUTY, 120),  # Some work kitchen
        "07:30": (TimeSegment.MORNING_WORK, ActivityType.JANITOR_DUTY, 120),  # Others clean
        "09:30": (TimeSegment.MORNING_WORK, ActivityType.LIBRARY_READING, 60),   # Non-workers get leisure
        "10:30": (TimeSegment.LEISURE_TIME, ActivityType.YARD_TIME, 60),
        "11:30": (TimeSegment.LEISURE_TIME, ActivityType.LIBRARY_READING, 60),
        "12:30": (TimeSegment.LUNCH, ActivityType.EATING, 30),
        "13:00": (TimeSegment.AFTERNOON_WORK, ActivityType.LAUNDRY_DUTY, 90),
        "13:00": (TimeSegment.AFTERNOON_WORK, ActivityType.MAINTENANCE, 90),
        "14:30": (TimeSegment.LEISURE_TIME, ActivityType.TELEVISION, 60),
        "15:30": (TimeSegment.LEISURE_TIME, ActivityType.CARDS_GAMES, 60),
        "16:30": (TimeSegment.LEISURE_TIME, ActivityType.EXERCISE, 60),
        "17:30": (TimeSegment.DINNER, ActivityType.EATING, 30),
        "18:00": (TimeSegment.SHOWER_TIME, ActivityType.SHOWERING, 60),  # Evening showers
        "19:00": (TimeSegment.RECREATION, ActivityType.YARD_TIME, 60),
        "20:00": (TimeSegment.RECREATION, ActivityType.TELEVISION, 60),
        "21:00": (TimeSegment.CELL_TIME, ActivityType.CELL_REST, 60),
        "22:00": (TimeSegment.LIGHTS_OUT, ActivityType.SLEEPING, 480)  # 8 hours sleep
    }

class TemporalSimulation:
    """Manages temporal progression through realistic prison schedule"""
    
    def __init__(self, pod_capacity: int = 8):
        self.pod_capacity = pod_capacity
        self.schedule = PodSchedule()
        self.current_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
        self.simulation_day = 1
        
        # Agent assignments and locations
        self.agent_locations: Dict[int, Location] = {}
        self.agent_activities: Dict[int, ActivityType] = {}
        self.work_assignments: Dict[int, ActivityType] = {}  # Permanent work assignments
        self.cell_assignments: Dict[int, Location] = {}  # Cell assignments (2 per cell)
        
        # Activity participation tracking
        self.current_activities: Dict[ActivityType, Set[int]] = {}
        self.activity_history: List[Dict] = []
        
    def assign_cells(self, agent_ids: List[int]):
        """Assign agents to cells (2 per cell)"""
        cells = [Location.CELL_A, Location.CELL_B, Location.CELL_C, Location.CELL_D]
        
        for i, agent_id in enumerate(agent_ids):
            cell = cells[i // 2]  # 2 agents per cell
            self.cell_assignments[agent_id] = cell
            self.agent_locations[agent_id] = cell
            
        print(f"🏠 Cell assignments: {len(agent_ids)} agents in {len(set(self.cell_assignments.values()))} cells")
    
    def assign_work_duties(self, agent_ids: List[int], agent_personalities: Dict):
        """Assign permanent work duties based on personality and capacity"""
        
        # Work assignment preferences based on personality
        work_preferences = {
            "cooperative": [ActivityType.KITCHEN_DUTY, ActivityType.LIBRARY_AIDE],
            "strategic": [ActivityType.KITCHEN_DUTY, ActivityType.MAINTENANCE],
            "aggressive": [ActivityType.JANITOR_DUTY, ActivityType.MAINTENANCE],
            "withdrawn": [ActivityType.LIBRARY_AIDE, ActivityType.LAUNDRY_DUTY],
            "impulsive": [ActivityType.JANITOR_DUTY, ActivityType.LAUNDRY_DUTY]
        }
        
        # Available work slots
        work_slots = {
            ActivityType.KITCHEN_DUTY: 3,
            ActivityType.LAUNDRY_DUTY: 2,
            ActivityType.JANITOR_DUTY: 2,
            ActivityType.MAINTENANCE: 1,
            ActivityType.LIBRARY_AIDE: 1
        }
        
        assigned_work = {}
        
        # Assign work based on preferences and availability
        for agent_id in agent_ids:
            personality = agent_personalities.get(agent_id, "cooperative")
            preferred_jobs = work_preferences.get(personality, [ActivityType.JANITOR_DUTY])
            
            for job in preferred_jobs:
                if work_slots.get(job, 0) > 0:
                    assigned_work[agent_id] = job
                    work_slots[job] -= 1
                    break
            
            # If no preferred job available, assign any available
            if agent_id not in assigned_work:
                for job, slots in work_slots.items():
                    if slots > 0:
                        assigned_work[agent_id] = job
                        work_slots[job] -= 1
                        break
        
        self.work_assignments = assigned_work
        
        print(f"💼 Work assignments:")
        for agent_id, job in assigned_work.items():
            print(f"   Agent {agent_id}: {job.value}")
    
    def get_current_time_segment(self) -> Tuple[TimeSegment, List[Tuple[ActivityType, int]]]:
        """Get current time segment and available activities"""
        current_time_str = self.current_time.strftime("%H:%M")
        
        # Find matching schedule entry
        available_activities = []
        current_segment = TimeSegment.CELL_TIME  # Default
        
        for time_str, (segment, activity, duration) in self.schedule.daily_schedule.items():
            if time_str <= current_time_str:
                current_segment = segment
                
                # Check if this activity is still ongoing
                activity_end_time = (datetime.strptime(time_str, "%H:%M") + 
                                   timedelta(minutes=duration)).strftime("%H:%M")
                
                if current_time_str <= activity_end_time:
                    available_activities.append((activity, duration))
        
        return current_segment, available_activities
    
    def assign_agents_to_activities(self, agent_ids: List[int], 
                                  available_activities: List[Tuple[ActivityType, int]]) -> Dict[int, ActivityType]:
        """Assign agents to current activities based on constraints and preferences"""
        
        assignments = {}
        activity_participants = {activity: [] for activity, _ in available_activities}
        
        # Handle mandatory activities first
        for activity_type, duration in available_activities:
            constraints = self.schedule.activity_constraints[activity_type]
            
            if not constraints.voluntary:  # Mandatory activities
                if activity_type == ActivityType.EATING:
                    # Everyone eats (but in shifts if needed)
                    for agent_id in agent_ids:
                        if len(activity_participants[activity_type]) < constraints.max_participants:
                            activity_participants[activity_type].append(agent_id)
                            assignments[agent_id] = activity_type
                
                elif activity_type == ActivityType.CELL_REST or activity_type == ActivityType.SLEEPING:
                    # Everyone in their cells
                    for agent_id in agent_ids:
                        assignments[agent_id] = activity_type
                        self.agent_locations[agent_id] = self.cell_assignments[agent_id]
        
        # Handle work assignments
        for activity_type, duration in available_activities:
            constraints = self.schedule.activity_constraints[activity_type]
            
            if constraints.requires_assignment:
                # Assign agents with work duties
                for agent_id in agent_ids:
                    if (agent_id not in assignments and 
                        self.work_assignments.get(agent_id) == activity_type and
                        len(activity_participants[activity_type]) < constraints.max_participants):
                        
                        activity_participants[activity_type].append(agent_id)
                        assignments[agent_id] = activity_type
                        self.agent_locations[agent_id] = constraints.location
        
        # Handle voluntary leisure activities
        unassigned_agents = [aid for aid in agent_ids if aid not in assignments]
        
        for activity_type, duration in available_activities:
            constraints = self.schedule.activity_constraints[activity_type]
            
            if (constraints.voluntary and not constraints.requires_assignment and 
                len(activity_participants[activity_type]) < constraints.max_participants):
                
                # Randomly assign some unassigned agents
                available_slots = constraints.max_participants - len(activity_participants[activity_type])
                participants = random.sample(unassigned_agents, 
                                           min(available_slots, len(unassigned_agents)))
                
                for agent_id in participants:
                    activity_participants[activity_type].append(agent_id)
                    assignments[agent_id] = activity_type
                    self.agent_locations[agent_id] = constraints.location
                    unassigned_agents.remove(agent_id)
        
        # Put remaining unassigned agents in cells
        for agent_id in unassigned_agents:
            assignments[agent_id] = ActivityType.CELL_REST
            self.agent_locations[agent_id] = self.cell_assignments[agent_id]
        
        self.current_activities = activity_participants
        return assignments
    
    def get_interaction_opportunities(self, current_assignments: Dict[int, ActivityType]) -> List[Tuple[int, int, str]]:
        """Generate interaction opportunities based on current activities and locations"""
        
        interactions = []
        
        # Group agents by activity
        activity_groups = {}
        for agent_id, activity in current_assignments.items():
            if activity not in activity_groups:
                activity_groups[activity] = []
            activity_groups[activity].append(agent_id)
        
        # Generate interactions within each activity
        for activity, participants in activity_groups.items():
            if len(participants) < 2:
                continue
                
            constraints = self.schedule.activity_constraints[activity]
            num_interactions = min(constraints.cooperation_opportunities, len(participants) // 2)
            
            # Create interaction pairs
            shuffled_participants = participants.copy()
            random.shuffle(shuffled_participants)
            
            for i in range(0, len(shuffled_participants) - 1, 2):
                if len(interactions) < num_interactions:
                    agent1 = shuffled_participants[i]
                    agent2 = shuffled_participants[i + 1]
                    context = f"{activity.value} in {constraints.location.value}"
                    interactions.append((agent1, agent2, context))
        
        return interactions
    
    def advance_time(self, minutes: int = 15):
        """Advance simulation time"""
        self.current_time += timedelta(minutes=minutes)
        
        # Check if new day
        if self.current_time.hour == 6 and self.current_time.minute == 0:
            self.simulation_day += 1
            print(f"🌅 Day {self.simulation_day} begins")
    
    def get_status_report(self) -> str:
        """Get current temporal status"""
        current_segment, activities = self.get_current_time_segment()
        
        report = f"""
⏰ TEMPORAL STATUS:
Time: {self.current_time.strftime('%H:%M')} (Day {self.simulation_day})
Segment: {current_segment.value}
Available Activities: {[a.value for a, _ in activities]}

📍 CURRENT LOCATIONS:
"""
        
        # Group agents by location
        location_groups = {}
        for agent_id, location in self.agent_locations.items():
            if location not in location_groups:
                location_groups[location] = []
            location_groups[location].append(agent_id)
        
        for location, agents in location_groups.items():
            report += f"   {location.value}: {len(agents)} agents\n"
        
        return report.strip()

def test_temporal_system():
    """Test the temporal prison system"""
    print("⏰ Testing Temporal Prison System")
    print("=" * 50)
    
    # Create simulation
    sim = TemporalSimulation(pod_capacity=8)
    
    # Test agent setup
    agent_ids = list(range(1, 9))  # 8 agents
    agent_personalities = {
        1: "strategic", 2: "cooperative", 3: "aggressive", 4: "aggressive",
        5: "cooperative", 6: "withdrawn", 7: "strategic", 8: "cooperative"
    }
    
    # Assign cells and work
    sim.assign_cells(agent_ids)
    sim.assign_work_duties(agent_ids, agent_personalities)
    
    # Test time progression
    for hour in range(6, 23):  # 6 AM to 10 PM
        sim.current_time = sim.current_time.replace(hour=hour, minute=0)
        
        segment, activities = sim.get_current_time_segment()
        assignments = sim.assign_agents_to_activities(agent_ids, activities)
        interactions = sim.get_interaction_opportunities(assignments)
        
        print(f"\n{hour:02d}:00 - {segment.value}")
        print(f"   Activities: {[a.value for a, _ in activities]}")
        print(f"   Interactions: {len(interactions)} opportunities")
        
        if interactions:
            for agent1, agent2, context in interactions[:2]:  # Show first 2
                print(f"      Agent {agent1} vs Agent {agent2}: {context}")

if __name__ == "__main__":
    test_temporal_system()