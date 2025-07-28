"""
Eternal Lockdown Core Module
Game theory-driven prison simulation engine
"""

from .game_theory import GameTheoryEngine, Strategy, PrisonersDilemma, ReplicatorDynamics
from .agents import Agent, Prisoner, Guard, Warden, create_sample_agents
from .simulation import PrisonSimulation, run_demo_simulation

__all__ = [
    'GameTheoryEngine', 'Strategy', 'PrisonersDilemma', 'ReplicatorDynamics',
    'Agent', 'Prisoner', 'Guard', 'Warden', 'create_sample_agents',
    'PrisonSimulation', 'run_demo_simulation'
]