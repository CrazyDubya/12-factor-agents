"""
Version 2.0 Modern Threat Integration Modules
Emergency Preparedness System Enhancement

These modules address critical gaps identified in stress testing:
- Cyber Attack Response (38.6% → 70% target)
- EMP/Solar Flare Hardening (41.0% → 60% target)  
- Nuclear/Radiation Safety (40.7% → 65% target)
"""

from .cyber_attack_response import CyberAttackResponseModule
from .emp_hardening_module import EMPHardeningModule
from .nuclear_safety_module import NuclearSafetyModule

__all__ = [
    'CyberAttackResponseModule',
    'EMPHardeningModule', 
    'NuclearSafetyModule'
]

__version__ = '2.0.0'