"""
WorldBuilder Agent - Creates consistent world rules and settings.

This agent is responsible for establishing the fundamental rules, physics,
cultures, and background information for a fictional world.
"""

import json
import random
from typing import Dict, List, Any, Optional
import dspy
from .base_agent import BaseAgent, AgentRole, AgentResponse, NarrativeContext

class WorldBuilderSignature(dspy.Signature):
    """Generate world building elements for a fictional narrative."""

    theme: str = dspy.InputField(desc="Theme or genre for the world (e.g., 'medieval fantasy', 'space opera')")
    world_aspects: str = dspy.InputField(desc="Specific aspects to develop (e.g., 'geography,politics,magic')")
    existing_context: str = dspy.InputField(desc="Any existing world information to build upon")

    world_rules: str = dspy.OutputField(desc="Physical and magical laws that govern this world")
    geography: str = dspy.OutputField(desc="Major geographical features and locations")
    cultures: str = dspy.OutputField(desc="Societies, peoples, and their customs")
    history: str = dspy.OutputField(desc="Major historical events and timeline")
    politics: str = dspy.OutputField(desc="Political systems and power structures")

class LocationGeneratorSignature(dspy.Signature):
    """Generate specific locations within the world."""

    world_context: str = dspy.InputField(desc="World rules and background information")
    location_type: str = dspy.InputField(desc="Type of location (e.g., 'city', 'dungeon', 'wilderness')")
    purpose: str = dspy.InputField(desc="Narrative purpose of this location")

    name: str = dspy.OutputField(desc="Name of the location")
    description: str = dspy.OutputField(desc="Detailed description of the location")
    inhabitants: str = dspy.OutputField(desc="Who or what lives or frequents this location")
    significance: str = dspy.OutputField(desc="Why this location matters to the world or story")
    connections: str = dspy.OutputField(desc="How this location connects to other parts of the world")

class WorldBuilderAgent(BaseAgent):
    """
    Agent responsible for creating consistent world rules and settings.

    This agent establishes the foundational elements of a fictional world,
    including physical laws, geography, cultures, history, and politics.
    """

    def __init__(self, llm: Optional[dspy.LM] = None, **kwargs):
        super().__init__(role=AgentRole.WORLD_BUILDER, llm=llm, **kwargs)

        # Initialize DSPy modules
        with dspy.context(lm=self.llm):
            self.world_generator = dspy.ChainOfThought(WorldBuilderSignature)
            self.location_generator = dspy.ChainOfThought(LocationGeneratorSignature)

    def execute(self, context: NarrativeContext, **kwargs) -> AgentResponse:
        """
        Generate world building elements for the given context.

        Args:
            context: Narrative context containing theme and existing world info
            **kwargs: Additional parameters:
                - aspects: List of specific aspects to focus on
                - num_locations: Number of locations to generate
                - location_types: Types of locations to create

        Returns:
            AgentResponse containing the generated world elements
        """
        try:
            # Extract parameters
            aspects = kwargs.get('aspects', ['geography', 'politics', 'cultures', 'history'])
            num_locations = kwargs.get('num_locations', 5)
            location_types = kwargs.get('location_types', ['city', 'wilderness', 'structure', 'landmark'])

            # Generate world foundation
            world_result = self._generate_world_foundation(context, aspects)

            # Generate specific locations
            locations = self._generate_locations(context, num_locations, location_types)

            # Update context with generated elements
            updates = {
                'world_rules': world_result['world_rules'],
                'locations': locations
            }

            # Add additional world elements to context metadata
            context.world_rules.update({
                'geography': world_result.get('geography', ''),
                'cultures': world_result.get('cultures', ''),
                'history': world_result.get('history', ''),
                'politics': world_result.get('politics', '')
            })

            return AgentResponse(
                success=True,
                content={
                    'world_foundation': world_result,
                    'locations': locations,
                    'summary': self._create_world_summary(world_result, locations)
                },
                metadata={
                    'aspects_generated': aspects,
                    'locations_created': len(locations),
                    'world_complexity': self._assess_complexity(world_result, locations)
                }
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                content=None,
                error_message=f"World building failed: {str(e)}"
            )

    def validate_input(self, context: NarrativeContext, **kwargs) -> bool:
        """Validate input for world building."""
        if not context.theme or not context.theme.strip():
            self.logger.error("Theme is required for world building")
            return False

        if len(context.theme) > 500:
            self.logger.error("Theme description too long")
            return False

        return True

    def _generate_world_foundation(self, context: NarrativeContext, aspects: List[str]) -> Dict[str, str]:
        """Generate the foundational elements of the world."""

        # Prepare existing context summary
        existing_context = ""
        if context.world_rules:
            existing_context = f"Existing world rules: {context.world_rules}"
        if context.generated_documents:
            existing_context += f"\nPrevious documents hint at: {len(context.generated_documents)} established elements"

        # Generate world foundation using DSPy
        with dspy.context(lm=self.llm):
            result = self.world_generator(
                theme=context.theme,
                world_aspects=",".join(aspects),
                existing_context=existing_context
            )

        return {
            'world_rules': result.world_rules,
            'geography': result.geography,
            'cultures': result.cultures,
            'history': result.history,
            'politics': result.politics
        }

    def _generate_locations(self, context: NarrativeContext, num_locations: int, location_types: List[str]) -> List[Dict[str, Any]]:
        """Generate specific locations for the world."""

        locations = []
        world_context_str = f"Theme: {context.theme}\nWorld Rules: {context.world_rules}"

        for i in range(num_locations):
            location_type = random.choice(location_types)

            # Define purpose based on location type and world needs
            purposes = {
                'city': 'Major population center and trade hub',
                'wilderness': 'Natural area with unique features or dangers',
                'structure': 'Important building or constructed site',
                'landmark': 'Significant geographical or cultural landmark'
            }

            purpose = purposes.get(location_type, 'Important location for the narrative')

            with dspy.context(lm=self.llm):
                result = self.location_generator(
                    world_context=world_context_str,
                    location_type=location_type,
                    purpose=purpose
                )

            location = {
                'id': f"loc_{context.world_id}_{i+1}",
                'name': result.name,
                'type': location_type,
                'description': result.description,
                'inhabitants': result.inhabitants,
                'significance': result.significance,
                'connections': result.connections,
                'metadata': {
                    'creation_order': i + 1,
                    'narrative_purpose': purpose
                }
            }

            locations.append(location)

        return locations

    def _create_world_summary(self, world_foundation: Dict[str, str], locations: List[Dict[str, Any]]) -> str:
        """Create a summary of the generated world."""

        location_names = [loc['name'] for loc in locations]

        return f"""
World Summary:
- Theme: Rich {world_foundation.get('cultures', 'cultural')} world with {world_foundation.get('politics', 'complex political')} elements
- Geography: {len([loc for loc in locations if loc['type'] in ['wilderness', 'landmark']])} natural features
- Settlements: {len([loc for loc in locations if loc['type'] == 'city'])} major population centers
- Key Locations: {', '.join(location_names[:3])}{"..." if len(location_names) > 3 else ""}
- Historical Depth: Established timeline and cultural background
"""

    def _assess_complexity(self, world_foundation: Dict[str, str], locations: List[Dict[str, Any]]) -> str:
        """Assess the complexity of the generated world."""

        complexity_factors = 0

        # Check for detailed world rules
        if len(world_foundation.get('world_rules', '')) > 200:
            complexity_factors += 1

        # Check for multiple cultures mentioned
        if 'culture' in world_foundation.get('cultures', '').lower():
            complexity_factors += 1

        # Check for political complexity
        if any(term in world_foundation.get('politics', '').lower()
               for term in ['kingdom', 'empire', 'faction', 'guild', 'council']):
            complexity_factors += 1

        # Check location diversity
        location_types = set(loc['type'] for loc in locations)
        if len(location_types) > 2:
            complexity_factors += 1

        if complexity_factors >= 3:
            return "High"
        elif complexity_factors >= 2:
            return "Medium"
        else:
            return "Low"

    def expand_world_element(self, context: NarrativeContext, element_type: str, element_name: str) -> AgentResponse:
        """
        Expand on a specific world element in more detail.

        Args:
            context: Current narrative context
            element_type: Type of element ('location', 'culture', 'history', etc.)
            element_name: Specific element to expand

        Returns:
            AgentResponse with expanded details
        """
        try:
            if element_type == 'location':
                # Find the location in context
                target_location = None
                for loc in context.locations:
                    if loc['name'].lower() == element_name.lower():
                        target_location = loc
                        break

                if not target_location:
                    return AgentResponse(
                        success=False,
                        content=None,
                        error_message=f"Location '{element_name}' not found in world context"
                    )

                # Generate expanded location details
                expanded_details = self._expand_location_details(context, target_location)

                return AgentResponse(
                    success=True,
                    content=expanded_details,
                    metadata={'element_type': element_type, 'element_name': element_name}
                )

            else:
                return AgentResponse(
                    success=False,
                    content=None,
                    error_message=f"Expansion of element type '{element_type}' not yet implemented"
                )

        except Exception as e:
            return AgentResponse(
                success=False,
                content=None,
                error_message=f"Failed to expand world element: {str(e)}"
            )

    def _expand_location_details(self, context: NarrativeContext, location: Dict[str, Any]) -> Dict[str, Any]:
        """Generate expanded details for a specific location."""

        # This would use additional DSPy signatures for detailed expansion
        # For now, return enhanced version of existing location
        expanded = location.copy()
        expanded['expanded_description'] = f"Detailed view: {location['description']}"
        expanded['notable_features'] = [
            "Feature 1 based on location type",
            "Feature 2 based on world rules",
            "Feature 3 based on cultural context"
        ]

        return expanded