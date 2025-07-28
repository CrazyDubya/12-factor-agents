# Eternal Lockdown - Prison Simulation System (PSS)

A sophisticated prison simulation system built on Microsoft's TinyTroupe framework, modified to work with Ollama's local LLM API.

## Overview

Eternal Lockdown simulates a prison environment with various personas including:
- **Inmates** with different backgrounds, crimes, and personalities
- **Guards** with varying approaches to authority and rule enforcement
- **Staff** including wardens, counselors, medical personnel
- **Visitors** family members, lawyers, social workers

## Features

- **Realistic Interactions**: AI-powered conversations between all personas
- **Dynamic Events**: Incidents, conflicts, rehabilitation programs
- **Behavioral Analysis**: Track personality changes and social dynamics
- **Scenario Testing**: Test different policies and interventions
- **Data Generation**: Create realistic training data for correctional research

## Technical Stack

- **Base Framework**: Modified Microsoft TinyTroupe
- **LLM Backend**: Ollama (localhost:11434)
- **Models**: Compatible with any Ollama-supported model
- **Language**: Python 3.10+

## Installation

1. Ensure Ollama is running with models available
2. Install dependencies: `pip install -r requirements.txt`
3. Configure settings in `config.ini`
4. Run examples in the `scenarios/` directory

## Prison Simulation Scenarios

- **Daily Routine**: Normal prison operations and interactions
- **Incident Response**: How different personas react to conflicts
- **Rehabilitation Programs**: Educational and therapeutic interventions
- **Visitor Days**: Family interactions and their impact
- **Policy Changes**: Testing new rules and procedures
- **Crisis Management**: Lockdowns, medical emergencies, etc.

## Ethical Considerations

This simulation is designed for:
- Research and policy development
- Training correctional staff
- Understanding social dynamics in confined environments
- Developing better rehabilitation programs

**NOT** for:
- Entertainment or trivializing incarceration
- Reinforcing harmful stereotypes
- Real-world decision making without human oversight