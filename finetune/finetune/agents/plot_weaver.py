"""
PlotWeaver Agent - Manages narrative threads and causality.

This agent coordinates plot development across documents, ensuring that
narrative threads develop logically and events have appropriate consequences.
"""

import json
import random
from typing import Dict, List, Any, Optional
import dspy
from dataclasses import dataclass
from .base_agent import BaseAgent, AgentRole, AgentResponse, NarrativeContext

@dataclass
class PlotThread:
    """Represents a narrative thread in the story."""
    thread_id: str
    title: str
    description: str
    status: str  # 'active', 'resolved', 'suspended'
    priority: str  # 'primary', 'secondary', 'background'
    involved_characters: List[str]
    related_locations: List[str]
    events: List[Dict[str, Any]]
    created_in_document: str
    last_mentioned: str

class PlotDesignSignature(dspy.Signature):
    """Design plot threads for narrative development."""

    world_context: str = dspy.InputField(desc="World setting and established elements")
    character_context: str = dspy.InputField(desc="Available characters and their motivations")
    existing_plots: str = dspy.InputField(desc="Currently active or established plot threads")
    narrative_goals: str = dspy.InputField(desc="What the overall narrative should achieve")

    plot_threads: str = dspy.OutputField(desc="New plot threads to introduce or develop")
    plot_connections: str = dspy.OutputField(desc="How plots connect and influence each other")
    character_arcs: str = dspy.OutputField(desc="Character development opportunities")
    conflict_opportunities: str = dspy.OutputField(desc="Potential sources of dramatic tension")

class EventPlanningSignature(dspy.Signature):
    """Plan specific events to advance plot threads."""

    active_plots: str = dspy.InputField(desc="Current active plot threads and their status")
    world_constraints: str = dspy.InputField(desc="World rules and logical constraints")
    character_motivations: str = dspy.InputField(desc="What characters want and why")
    document_type: str = dspy.InputField(desc="Type of document that will contain this event")

    planned_events: str = dspy.OutputField(desc="Specific events that should occur")
    causal_relationships: str = dspy.OutputField(desc="How events cause and affect each other")
    character_reactions: str = dspy.OutputField(desc="How characters respond to events")
    plot_advancement: str = dspy.OutputField(desc="How events advance the plot threads")

class PlotWeaverAgent(BaseAgent):
    """
    Agent responsible for managing narrative threads and causality.

    This agent ensures that plot development is coherent, characters act
    according to their motivations, and events have logical consequences.
    """

    def __init__(self, llm: Optional[dspy.LM] = None, **kwargs):
        super().__init__(role=AgentRole.PLOT_WEAVER, llm=llm, **kwargs)

        # Initialize DSPy modules
        with dspy.context(lm=self.llm):
            self.plot_designer = dspy.ChainOfThought(PlotDesignSignature)
            self.event_planner = dspy.ChainOfThought(EventPlanningSignature)

        # Plot structure templates
        self.plot_archetypes = {
            'hero_journey': {
                'stages': ['call_to_adventure', 'refusal', 'mentor', 'crossing_threshold', 'tests', 'ordeal', 'reward', 'return'],
                'typical_length': 'long',
                'character_focus': 'protagonist'
            },
            'mystery': {
                'stages': ['crime', 'investigation', 'clues', 'red_herrings', 'revelation', 'resolution'],
                'typical_length': 'medium',
                'character_focus': 'investigator'
            },
            'romance': {
                'stages': ['meeting', 'attraction', 'obstacles', 'separation', 'reunion', 'commitment'],
                'typical_length': 'medium',
                'character_focus': 'romantic_pair'
            },
            'conflict': {
                'stages': ['tension', 'escalation', 'confrontation', 'climax', 'resolution'],
                'typical_length': 'variable',
                'character_focus': 'opposing_parties'
            },
            'coming_of_age': {
                'stages': ['innocence', 'challenge', 'struggle', 'growth', 'maturity'],
                'typical_length': 'long',
                'character_focus': 'young_protagonist'
            }
        }

    def execute(self, context: NarrativeContext, **kwargs) -> AgentResponse:
        """
        Develop and manage plot threads for the narrative.

        Args:
            context: Narrative context with world and character information
            **kwargs: Additional parameters:
                - focus_plots: Specific plots to focus on
                - narrative_goals: Overall narrative objectives
                - event_density: How many events to plan
                - plot_complexity: Desired complexity level

        Returns:
            AgentResponse containing plot development and event planning
        """
        try:
            # Extract parameters
            focus_plots = kwargs.get('focus_plots', [])
            narrative_goals = kwargs.get('narrative_goals', 'create engaging character-driven stories')
            event_density = kwargs.get('event_density', 'medium')
            plot_complexity = kwargs.get('plot_complexity', 'medium')

            # Analyze existing plot state
            current_plots = self._analyze_current_plots(context)

            # Design new plot threads if needed
            new_plots = self._design_plot_threads(context, current_plots, narrative_goals, plot_complexity)

            # Plan specific events
            planned_events = self._plan_events(context, current_plots + new_plots, event_density)

            # Update plot tracking
            updated_plots = self._update_plot_tracking(context, current_plots, new_plots, planned_events)

            # Update context
            context.active_plots = updated_plots

            return AgentResponse(
                success=True,
                content={
                    'current_plots': current_plots,
                    'new_plots': new_plots,
                    'planned_events': planned_events,
                    'plot_summary': self._create_plot_summary(updated_plots),
                    'narrative_opportunities': self._identify_narrative_opportunities(updated_plots)
                },
                metadata={
                    'active_plots': len([p for p in updated_plots if p['status'] == 'active']),
                    'total_plots': len(updated_plots),
                    'planned_events': len(planned_events),
                    'plot_complexity_score': self._assess_plot_complexity(updated_plots)
                }
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                content=None,
                error_message=f"Plot weaving failed: {str(e)}"
            )

    def validate_input(self, context: NarrativeContext, **kwargs) -> bool:
        """Validate input for plot weaving."""
        if not context.characters:
            self.logger.error("Characters are required for plot development")
            return False

        if not context.world_rules and not context.theme:
            self.logger.error("World context is required for plot development")
            return False

        return True

    def _analyze_current_plots(self, context: NarrativeContext) -> List[Dict[str, Any]]:
        """Analyze existing plot threads from context and documents."""

        current_plots = []

        # Convert existing active_plots to proper format
        for plot_data in context.active_plots:
            if isinstance(plot_data, dict):
                current_plots.append(plot_data)

        # Extract implicit plots from generated documents
        implicit_plots = self._extract_implicit_plots(context)
        current_plots.extend(implicit_plots)

        # Update plot status based on recent mentions
        for plot in current_plots:
            plot['last_activity'] = self._find_last_plot_mention(plot, context)
            plot['status'] = self._determine_plot_status(plot, context)

        return current_plots

    def _extract_implicit_plots(self, context: NarrativeContext) -> List[Dict[str, Any]]:
        """Extract implicit plot threads from generated documents."""

        implicit_plots = []

        # Look for recurring themes, conflicts, or character arcs in documents
        character_arcs = self._identify_character_arcs(context)
        for arc in character_arcs:
            plot = {
                'thread_id': f"arc_{arc['character_id']}",
                'title': f"{arc['character_name']} Character Arc",
                'description': arc['development'],
                'status': 'active',
                'priority': 'secondary',
                'involved_characters': [arc['character_id']],
                'related_locations': [],
                'events': arc['events'],
                'created_in_document': arc['first_document'],
                'last_mentioned': arc['last_document']
            }
            implicit_plots.append(plot)

        # Look for conflicts between characters or factions
        conflicts = self._identify_conflicts(context)
        for conflict in conflicts:
            plot = {
                'thread_id': f"conflict_{conflict['id']}",
                'title': conflict['title'],
                'description': conflict['description'],
                'status': 'active',
                'priority': 'primary' if conflict['intensity'] == 'high' else 'secondary',
                'involved_characters': conflict['involved_characters'],
                'related_locations': conflict['locations'],
                'events': conflict['events'],
                'created_in_document': conflict['first_mention'],
                'last_mentioned': conflict['last_mention']
            }
            implicit_plots.append(plot)

        return implicit_plots

    def _design_plot_threads(self, context: NarrativeContext, current_plots: List[Dict[str, Any]],
                           narrative_goals: str, complexity: str) -> List[Dict[str, Any]]:
        """Design new plot threads to develop the narrative."""

        # Prepare context strings
        world_context_str = self._format_world_context(context)
        character_context_str = self._format_character_context(context)
        existing_plots_str = self._format_existing_plots(current_plots)

        with dspy.context(lm=self.llm):
            design_result = self.plot_designer(
                world_context=world_context_str,
                character_context=character_context_str,
                existing_plots=existing_plots_str,
                narrative_goals=narrative_goals
            )

        # Parse the designed plots
        new_plots = self._parse_plot_design(design_result, context)

        # Assign plot archetypes
        for plot in new_plots:
            archetype = self._assign_plot_archetype(plot, context)
            plot['archetype'] = archetype
            plot['expected_stages'] = self.plot_archetypes[archetype]['stages']

        return new_plots

    def _plan_events(self, context: NarrativeContext, all_plots: List[Dict[str, Any]],
                    event_density: str) -> List[Dict[str, Any]]:
        """Plan specific events to advance plot threads."""

        # Determine number of events based on density
        density_multipliers = {'low': 0.5, 'medium': 1.0, 'high': 1.5}
        base_events = len(all_plots) * 2  # 2 events per active plot
        num_events = int(base_events * density_multipliers.get(event_density, 1.0))

        # Select active plots for event planning
        active_plots = [p for p in all_plots if p['status'] == 'active']

        if not active_plots:
            return []

        # Prepare context strings
        active_plots_str = self._format_active_plots(active_plots)
        world_constraints_str = self._format_world_constraints(context)
        character_motivations_str = self._format_character_motivations(context)

        planned_events = []

        # Plan events for different document types
        document_types = ['chronicle', 'letter', 'diary', 'report']

        for i in range(min(num_events, len(document_types) * 3)):
            doc_type = document_types[i % len(document_types)]

            with dspy.context(lm=self.llm):
                event_result = self.event_planner(
                    active_plots=active_plots_str,
                    world_constraints=world_constraints_str,
                    character_motivations=character_motivations_str,
                    document_type=doc_type
                )

            events = self._parse_event_planning(event_result, active_plots, doc_type, i)
            planned_events.extend(events)

        return planned_events

    def _parse_plot_design(self, design_result, context: NarrativeContext) -> List[Dict[str, Any]]:
        """Parse plot design results into structured format."""

        new_plots = []

        if design_result.plot_threads:
            # Split plot threads by some delimiter (assuming semicolon separation)
            thread_descriptions = design_result.plot_threads.split(';')

            for i, thread_desc in enumerate(thread_descriptions):
                thread_desc = thread_desc.strip()
                if not thread_desc:
                    continue

                # Extract title and description
                if ':' in thread_desc:
                    title, description = thread_desc.split(':', 1)
                else:
                    title = f"Plot Thread {i+1}"
                    description = thread_desc

                plot = {
                    'thread_id': f"plot_{context.world_id}_{len(context.active_plots) + i + 1}",
                    'title': title.strip(),
                    'description': description.strip(),
                    'status': 'active',
                    'priority': 'secondary',
                    'involved_characters': self._extract_character_names(description, context),
                    'related_locations': self._extract_location_names(description, context),
                    'events': [],
                    'created_in_document': 'plot_design',
                    'last_mentioned': 'plot_design'
                }

                new_plots.append(plot)

        return new_plots

    def _parse_event_planning(self, event_result, active_plots: List[Dict[str, Any]],
                            doc_type: str, event_index: int) -> List[Dict[str, Any]]:
        """Parse event planning results into structured format."""

        events = []

        if event_result.planned_events:
            event_descriptions = event_result.planned_events.split(';')

            for i, event_desc in enumerate(event_descriptions):
                event_desc = event_desc.strip()
                if not event_desc:
                    continue

                # Assign to a random active plot
                target_plot = random.choice(active_plots) if active_plots else None

                event = {
                    'event_id': f"event_{event_index}_{i}",
                    'description': event_desc,
                    'plot_thread_id': target_plot['thread_id'] if target_plot else None,
                    'document_type': doc_type,
                    'involved_characters': target_plot['involved_characters'][:2] if target_plot else [],
                    'location': random.choice(target_plot['related_locations']) if target_plot and target_plot['related_locations'] else None,
                    'consequences': self._predict_event_consequences(event_desc),
                    'narrative_function': self._determine_narrative_function(event_desc, doc_type)
                }

                events.append(event)

        return events

    def _update_plot_tracking(self, context: NarrativeContext, current_plots: List[Dict[str, Any]],
                            new_plots: List[Dict[str, Any]], planned_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update plot tracking with new information."""

        all_plots = current_plots + new_plots

        # Add planned events to relevant plots
        for event in planned_events:
            plot_id = event.get('plot_thread_id')
            if plot_id:
                for plot in all_plots:
                    if plot['thread_id'] == plot_id:
                        plot['events'].append(event)
                        break

        return all_plots

    def _format_world_context(self, context: NarrativeContext) -> str:
        """Format world context for plot design."""
        parts = [f"Theme: {context.theme}"]

        if context.world_rules:
            if isinstance(context.world_rules, dict):
                rules = '; '.join([f"{k}: {v}" for k, v in context.world_rules.items() if v])
            else:
                rules = str(context.world_rules)
            parts.append(f"Rules: {rules}")

        if context.locations:
            locations = ', '.join([loc['name'] for loc in context.locations[:5]])
            parts.append(f"Locations: {locations}")

        return ' | '.join(parts)

    def _format_character_context(self, context: NarrativeContext) -> str:
        """Format character context for plot design."""
        if not context.characters:
            return "No established characters"

        char_summaries = []
        for char in context.characters[:10]:
            summary = f"{char['name']} ({char['role']}): {char['motivations']}"
            char_summaries.append(summary)

        return ' | '.join(char_summaries)

    def _format_existing_plots(self, plots: List[Dict[str, Any]]) -> str:
        """Format existing plots for reference."""
        if not plots:
            return "No existing plot threads"

        plot_summaries = []
        for plot in plots:
            summary = f"{plot['title']}: {plot['description']} (Status: {plot['status']})"
            plot_summaries.append(summary)

        return ' | '.join(plot_summaries)

    def _format_active_plots(self, active_plots: List[Dict[str, Any]]) -> str:
        """Format active plots for event planning."""
        if not active_plots:
            return "No active plot threads"

        summaries = []
        for plot in active_plots:
            characters = ', '.join(plot['involved_characters'][:3])
            summary = f"{plot['title']}: {plot['description']} | Characters: {characters}"
            summaries.append(summary)

        return ' | '.join(summaries)

    def _format_world_constraints(self, context: NarrativeContext) -> str:
        """Format world constraints for event planning."""
        constraints = []

        if context.world_rules:
            if isinstance(context.world_rules, dict):
                for rule_type, rule_desc in context.world_rules.items():
                    if rule_desc:
                        constraints.append(f"{rule_type}: {rule_desc}")
            else:
                constraints.append(str(context.world_rules))

        return ' | '.join(constraints) if constraints else "No specific world constraints"

    def _format_character_motivations(self, context: NarrativeContext) -> str:
        """Format character motivations for event planning."""
        if not context.characters:
            return "No character motivations established"

        motivations = []
        for char in context.characters:
            motivation = f"{char['name']}: {char['motivations']}"
            motivations.append(motivation)

        return ' | '.join(motivations)

    def _assign_plot_archetype(self, plot: Dict[str, Any], context: NarrativeContext) -> str:
        """Assign an appropriate archetype to a plot based on its characteristics."""

        description_lower = plot['description'].lower()

        # Simple keyword matching for archetype assignment
        if any(keyword in description_lower for keyword in ['journey', 'quest', 'adventure', 'hero']):
            return 'hero_journey'
        elif any(keyword in description_lower for keyword in ['mystery', 'investigate', 'crime', 'solve']):
            return 'mystery'
        elif any(keyword in description_lower for keyword in ['love', 'romance', 'relationship', 'marriage']):
            return 'romance'
        elif any(keyword in description_lower for keyword in ['conflict', 'war', 'fight', 'battle', 'enemy']):
            return 'conflict'
        elif any(keyword in description_lower for keyword in ['grow', 'learn', 'young', 'mature', 'childhood']):
            return 'coming_of_age'
        else:
            return 'conflict'  # Default archetype

    def _identify_character_arcs(self, context: NarrativeContext) -> List[Dict[str, Any]]:
        """Identify character development arcs from documents."""
        # Simplified implementation
        arcs = []

        for char in context.characters[:3]:  # Focus on main characters
            arc = {
                'character_id': char['id'],
                'character_name': char['name'],
                'development': f"Personal growth and development of {char['name']}",
                'events': [],
                'first_document': context.generated_documents[0]['id'] if context.generated_documents else 'none',
                'last_document': context.generated_documents[-1]['id'] if context.generated_documents else 'none'
            }
            arcs.append(arc)

        return arcs

    def _identify_conflicts(self, context: NarrativeContext) -> List[Dict[str, Any]]:
        """Identify conflicts from character relationships and world state."""
        conflicts = []

        # Look for characters with opposing motivations
        for i, char1 in enumerate(context.characters):
            for char2 in context.characters[i+1:]:
                # Simplified conflict detection
                if ('power' in char1['motivations'].lower() and
                    'power' in char2['motivations'].lower()):

                    conflict = {
                        'id': f"{char1['id']}_{char2['id']}",
                        'title': f"Power Struggle between {char1['name']} and {char2['name']}",
                        'description': f"Conflict over power and influence between {char1['name']} and {char2['name']}",
                        'intensity': 'medium',
                        'involved_characters': [char1['id'], char2['id']],
                        'locations': [],
                        'events': [],
                        'first_mention': context.generated_documents[0]['id'] if context.generated_documents else 'none',
                        'last_mention': context.generated_documents[-1]['id'] if context.generated_documents else 'none'
                    }
                    conflicts.append(conflict)

        return conflicts

    def _extract_character_names(self, text: str, context: NarrativeContext) -> List[str]:
        """Extract character names mentioned in text."""
        mentioned_chars = []

        for char in context.characters:
            if char['name'].lower() in text.lower():
                mentioned_chars.append(char['id'])

        return mentioned_chars

    def _extract_location_names(self, text: str, context: NarrativeContext) -> List[str]:
        """Extract location names mentioned in text."""
        mentioned_locs = []

        for loc in context.locations:
            if loc['name'].lower() in text.lower():
                mentioned_locs.append(loc['id'])

        return mentioned_locs

    def _find_last_plot_mention(self, plot: Dict[str, Any], context: NarrativeContext) -> str:
        """Find the last document that mentioned this plot."""
        # Simplified - would search through documents for plot references
        if context.generated_documents:
            return context.generated_documents[-1]['id']
        return 'none'

    def _determine_plot_status(self, plot: Dict[str, Any], context: NarrativeContext) -> str:
        """Determine current status of a plot thread."""
        # Simplified logic
        if plot.get('last_activity') and plot['last_activity'] != 'none':
            return 'active'
        return 'suspended'

    def _predict_event_consequences(self, event_description: str) -> List[str]:
        """Predict potential consequences of an event."""
        # Simplified consequence prediction
        consequences = []

        if 'conflict' in event_description.lower():
            consequences.extend(['escalation', 'retaliation', 'alliance_shifts'])
        if 'discovery' in event_description.lower():
            consequences.extend(['revelation', 'changed_relationships', 'new_opportunities'])
        if 'death' in event_description.lower():
            consequences.extend(['grief', 'power_vacuum', 'revenge_plots'])

        return consequences[:3]  # Limit to 3 consequences

    def _determine_narrative_function(self, event_description: str, doc_type: str) -> str:
        """Determine the narrative function of an event."""
        functions = {
            'chronicle': 'historical_record',
            'letter': 'character_development',
            'diary': 'introspection',
            'report': 'information_revelation'
        }

        return functions.get(doc_type, 'plot_advancement')

    def _create_plot_summary(self, plots: List[Dict[str, Any]]) -> str:
        """Create a summary of current plot state."""
        active_plots = [p for p in plots if p['status'] == 'active']
        primary_plots = [p for p in plots if p.get('priority') == 'primary']

        return f"""
Plot Summary:
- Active Plot Threads: {len(active_plots)}
- Primary Plots: {len(primary_plots)}
- Total Events Planned: {sum(len(p.get('events', [])) for p in plots)}
- Plot Archetypes: {', '.join(set(p.get('archetype', 'unknown') for p in plots))}
"""

    def _identify_narrative_opportunities(self, plots: List[Dict[str, Any]]) -> List[str]:
        """Identify opportunities for narrative development."""
        opportunities = []

        # Check for plot convergence opportunities
        char_involvement = {}
        for plot in plots:
            for char_id in plot['involved_characters']:
                char_involvement[char_id] = char_involvement.get(char_id, 0) + 1

        multi_plot_chars = [char_id for char_id, count in char_involvement.items() if count > 1]
        if multi_plot_chars:
            opportunities.append(f"Plot convergence through characters: {', '.join(multi_plot_chars[:3])}")

        # Check for conflict escalation opportunities
        conflict_plots = [p for p in plots if p.get('archetype') == 'conflict' and p['status'] == 'active']
        if conflict_plots:
            opportunities.append(f"Conflict escalation opportunities in {len(conflict_plots)} active conflicts")

        # Check for resolution opportunities
        long_running_plots = [p for p in plots if len(p.get('events', [])) > 3]
        if long_running_plots:
            opportunities.append(f"Resolution opportunities for {len(long_running_plots)} developed plots")

        return opportunities

    def _assess_plot_complexity(self, plots: List[Dict[str, Any]]) -> float:
        """Assess overall plot complexity score."""
        if not plots:
            return 0.0

        complexity_factors = 0
        total_plots = len(plots)

        # Factor 1: Number of active plots
        active_plots = len([p for p in plots if p['status'] == 'active'])
        complexity_factors += min(active_plots / 5, 1.0)  # Normalize to max of 1

        # Factor 2: Character involvement spread
        all_chars = set()
        for plot in plots:
            all_chars.update(plot['involved_characters'])
        complexity_factors += min(len(all_chars) / 10, 1.0)  # Normalize to max of 1

        # Factor 3: Event density
        total_events = sum(len(p.get('events', [])) for p in plots)
        complexity_factors += min(total_events / (total_plots * 5), 1.0)  # Normalize to max of 1

        return round(complexity_factors / 3, 2)  # Average of factors