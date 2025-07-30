"""
CrewAI Integration for Eternal Lockdown Prison Simulation
Implements task-oriented workflows for prison operations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from crewai import Agent, Task, Crew, Process
    from crewai.tools import BaseTool
    CREWAI_AVAILABLE = True
except ImportError:
    print("CrewAI not installed. Install with: pip install crewai")
    CREWAI_AVAILABLE = False

from ollama_utils import OllamaClient
import json
from typing import List, Dict, Any

class OllamaLLM:
    """Ollama LLM wrapper for CrewAI compatibility"""
    
    def __init__(self, model="llama2:latest"):
        self.client = OllamaClient()
        self.model = model
    
    def __call__(self, prompt: str) -> str:
        """Make the LLM callable for CrewAI"""
        try:
            response = self.client.send_message([{"role": "user", "content": prompt}], model=self.model)
            return response.get("content", "")
        except Exception as e:
            return f"Error: {str(e)}"

class PrisonPatrolTool(BaseTool):
    """Tool for conducting prison patrols"""
    name: str = "prison_patrol"
    description: str = "Conduct a patrol of prison areas and report findings"
    
    def _run(self, area: str) -> str:
        """Execute patrol of specified area"""
        findings = [
            f"Patrolled {area}",
            f"All inmates accounted for in {area}",
            f"No security issues detected in {area}",
            f"Area {area} secure"
        ]
        return "; ".join(findings)

class IncidentResponseTool(BaseTool):
    """Tool for responding to prison incidents"""
    name: str = "incident_response"
    description: str = "Respond to and manage prison incidents"
    
    def _run(self, incident_type: str, location: str) -> str:
        """Execute incident response protocol"""
        response = f"Responding to {incident_type} at {location}. "
        response += f"Security team dispatched. Area secured. Incident logged."
        return response

class PrisonCrewAI:
    """CrewAI integration for prison task management"""
    
    def __init__(self):
        if not CREWAI_AVAILABLE:
            raise ImportError("CrewAI is required but not installed")
        
        self.ollama_llm = OllamaLLM("llama2:latest")
        self.patrol_tool = PrisonPatrolTool()
        self.incident_tool = IncidentResponseTool()
        
        # Create specialized agents
        self.security_chief = self._create_security_chief()
        self.patrol_officer = self._create_patrol_officer()
        self.incident_responder = self._create_incident_responder()
        self.maintenance_crew = self._create_maintenance_crew()
    
    def _create_security_chief(self) -> Agent:
        """Create security chief agent"""
        return Agent(
            role="Security Chief",
            goal="Oversee all security operations and coordinate response teams",
            backstory="""You are the head of security at Eternal Lockdown Correctional Facility. 
            You have 15 years of experience in prison security and are responsible for maintaining 
            order, coordinating patrols, and managing incident responses.""",
            verbose=True,
            allow_delegation=True,
            llm=self.ollama_llm,
            tools=[self.patrol_tool, self.incident_tool]
        )
    
    def _create_patrol_officer(self) -> Agent:
        """Create patrol officer agent"""
        return Agent(
            role="Patrol Officer",
            goal="Conduct regular patrols and maintain security in assigned areas",
            backstory="""You are an experienced correctional officer responsible for patrolling 
            the prison facility. You check on inmates, monitor for contraband, and ensure 
            all security protocols are followed.""",
            verbose=True,
            allow_delegation=False,
            llm=self.ollama_llm,
            tools=[self.patrol_tool]
        )
    
    def _create_incident_responder(self) -> Agent:
        """Create incident response agent"""
        return Agent(
            role="Incident Response Officer",
            goal="Quickly respond to and resolve security incidents",
            backstory="""You are a specialized officer trained in crisis management and 
            incident response. You handle fights, medical emergencies, and security breaches 
            with quick thinking and decisive action.""",
            verbose=True,
            allow_delegation=False,
            llm=self.ollama_llm,
            tools=[self.incident_tool, self.patrol_tool]
        )
    
    def _create_maintenance_crew(self) -> Agent:
        """Create maintenance crew leader agent"""
        return Agent(
            role="Maintenance Crew Leader",
            goal="Coordinate facility maintenance and manage inmate work details",
            backstory="""You oversee the maintenance operations and coordinate inmate work crews. 
            You ensure the facility is properly maintained while providing inmates with 
            productive work opportunities.""",
            verbose=True,
            allow_delegation=True,
            llm=self.ollama_llm
        )
    
    def create_patrol_crew(self, areas: List[str]) -> Crew:
        """Create a patrol crew for specified areas"""
        tasks = []
        
        # Create patrol tasks for each area
        for area in areas:
            task = Task(
                description=f"Conduct thorough patrol of {area}. Check for security issues, contraband, and inmate compliance.",
                expected_output=f"Detailed patrol report for {area} including any findings or concerns",
                agent=self.patrol_officer
            )
            tasks.append(task)
        
        # Create coordination task for security chief
        coordination_task = Task(
            description="Review all patrol reports and coordinate any necessary follow-up actions",
            expected_output="Summary of patrol findings and any required security actions",
            agent=self.security_chief
        )
        tasks.append(coordination_task)
        
        return Crew(
            agents=[self.security_chief, self.patrol_officer],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
    
    def create_incident_response_crew(self, incident_type: str, location: str) -> Crew:
        """Create incident response crew"""
        
        # Primary response task
        response_task = Task(
            description=f"Respond immediately to {incident_type} at {location}. Secure the area and manage the situation.",
            expected_output=f"Incident response report for {incident_type} at {location}",
            agent=self.incident_responder
        )
        
        # Security coordination task
        coordination_task = Task(
            description="Coordinate overall security response and ensure facility-wide security is maintained",
            expected_output="Security coordination report and status update",
            agent=self.security_chief
        )
        
        return Crew(
            agents=[self.security_chief, self.incident_responder],
            tasks=[response_task, coordination_task],
            process=Process.sequential,
            verbose=True
        )
    
    def create_work_detail_crew(self, work_type: str, inmates: List[str]) -> Crew:
        """Create work detail crew for inmate tasks"""
        
        work_task = Task(
            description=f"Organize and supervise {work_type} work detail with inmates: {', '.join(inmates)}",
            expected_output=f"Work detail completion report for {work_type}",
            agent=self.maintenance_crew
        )
        
        return Crew(
            agents=[self.maintenance_crew],
            tasks=[work_task],
            process=Process.sequential,
            verbose=True
        )

def demo_crewai_integration():
    """Demonstrate CrewAI integration with prison workflows"""
    if not CREWAI_AVAILABLE:
        print("❌ CrewAI not available. Install with: pip install crewai")
        return
    
    print("🚀 CrewAI Prison Integration Demo")
    print("=" * 50)
    
    try:
        # Initialize CrewAI system
        prison_crew = PrisonCrewAI()
        print("✅ CrewAI system initialized")
        
        # Demo 1: Patrol Crew
        print("\n🔍 Demo 1: Patrol Operations")
        patrol_areas = ["Cell Block A", "Common Area", "Kitchen", "Yard"]
        patrol_crew = prison_crew.create_patrol_crew(patrol_areas)
        
        print(f"Created patrol crew for areas: {', '.join(patrol_areas)}")
        patrol_result = patrol_crew.kickoff()
        print("Patrol crew results:", patrol_result)
        
        # Demo 2: Incident Response
        print("\n🚨 Demo 2: Incident Response")
        incident_crew = prison_crew.create_incident_response_crew("Fight", "Cell Block B")
        
        print("Created incident response crew for fight in Cell Block B")
        incident_result = incident_crew.kickoff()
        print("Incident response results:", incident_result)
        
        # Demo 3: Work Detail
        print("\n🔧 Demo 3: Work Detail Management")
        work_crew = prison_crew.create_work_detail_crew("Kitchen Cleaning", ["Carlos", "Diego", "Tommy"])
        
        print("Created work detail crew for kitchen cleaning")
        work_result = work_crew.kickoff()
        print("Work detail results:", work_result)
        
        print("\n✅ CrewAI integration demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in CrewAI demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_crewai_integration()