"""
CharacterDesigner Agent - Develops personas with consistent traits.

This agent creates detailed character profiles with personality traits,
backgrounds, motivations, and relationships that remain consistent across
all generated documents.
"""

import json
import random
from typing import Dict, List, Any, Optional
import dspy
from .base_agent import BaseAgent, AgentRole, AgentResponse, NarrativeContext

class CharacterDesignSignature(dspy.Signature):
    """Generate a detailed character for a fictional narrative."""

    world_context: str = dspy.InputField(desc="World rules, culture, and setting information")
    character_role: str = dspy.InputField(desc="Character's role in the narrative (e.g., 'protagonist', 'antagonist', 'supporting')")
    character_type: str = dspy.InputField(desc="Type of character (e.g., 'noble', 'merchant', 'scholar', 'warrior')")

    name: str = dspy.OutputField(desc="Character's full name appropriate to the world")
    age: str = dspy.OutputField(desc="Character's age and life stage")
    appearance: str = dspy.OutputField(desc="Physical description and notable features")
    personality: str = dspy.OutputField(desc="Core personality traits and temperament")
    background: str = dspy.OutputField(desc="Personal history and formative experiences")
    motivations: str = dspy.OutputField(desc="What drives this character and their goals")
    skills: str = dspy.OutputField(desc="Notable abilities, talents, and expertise")
    flaws: str = dspy.OutputField(desc="Character weaknesses and negative traits")

class RelationshipDesignSignature(dspy.Signature):
    """Design relationships between characters."""

    character1: str = dspy.InputField(desc="First character's name and key traits")
    character2: str = dspy.InputField(desc="Second character's name and key traits")
    world_context: str = dspy.InputField(desc="World setting and cultural context")

    relationship_type: str = dspy.OutputField(desc="Type of relationship (ally, enemy, family, etc.)")
    relationship_history: str = dspy.OutputField(desc="How they met and relationship development")
    current_dynamic: str = dspy.OutputField(desc="Current state of their relationship")
    potential_conflicts: str = dspy.OutputField(desc="Possible sources of tension or conflict")

class CharacterDesignerAgent(BaseAgent):
    """
    Agent responsible for creating consistent character profiles.

    This agent develops detailed characters with personalities, backgrounds,
    and relationships that maintain consistency across all narrative documents.
    """

    def __init__(self, llm: Optional[dspy.LM] = None, **kwargs):
        super().__init__(role=AgentRole.CHARACTER_DESIGNER, llm=llm, **kwargs)

        # Initialize DSPy modules
        with dspy.context(lm=self.llm):
            self.character_generator = dspy.ChainOfThought(CharacterDesignSignature)
            self.relationship_generator = dspy.ChainOfThought(RelationshipDesignSignature)

        # Character archetypes for different world types
        self.character_archetypes = {
            'fantasy': ['warrior', 'mage', 'rogue', 'noble', 'merchant', 'scholar', 'priest', 'peasant'],
            'sci-fi': ['captain', 'engineer', 'scientist', 'pilot', 'diplomat', 'trader', 'soldier', 'colonist'],
            'modern': ['detective', 'journalist', 'teacher', 'doctor', 'artist', 'politician', 'criminal', 'citizen'],
            'historical': ['knight', 'merchant', 'cleric', 'craftsman', 'noble', 'peasant', 'soldier', 'scholar'],
            'default': ['leader', 'expert', 'rebel', 'keeper', 'seeker', 'guardian', 'trickster', 'innocent']
        }

    def execute(self, context: NarrativeContext, **kwargs) -> AgentResponse:
        """
        Generate characters for the given narrative context.

        Args:
            context: Narrative context with world information
            **kwargs: Additional parameters:
                - num_characters: Number of characters to generate
                - character_roles: Specific roles needed
                - generate_relationships: Whether to create relationships

        Returns:
            AgentResponse containing the generated characters
        """
        try:
            # Extract parameters
            num_characters = kwargs.get('num_characters', 5)
            character_roles = kwargs.get('character_roles', ['protagonist', 'antagonist', 'supporting', 'supporting', 'minor'])
            generate_relationships = kwargs.get('generate_relationships', True)

            # Generate characters
            characters = self._generate_characters(context, num_characters, character_roles)

            # Generate relationships if requested
            relationships = []
            if generate_relationships and len(characters) > 1:
                relationships = self._generate_relationships(context, characters)

            # Update context
            self.update_context(context, {'characters': characters})

            return AgentResponse(
                success=True,
                content={
                    'characters': characters,
                    'relationships': relationships,
                    'character_summary': self._create_character_summary(characters, relationships)
                },
                metadata={
                    'characters_created': len(characters),
                    'relationships_created': len(relationships),
                    'character_diversity': self._assess_character_diversity(characters)
                }
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                content=None,
                error_message=f"Character generation failed: {str(e)}"
            )

    def validate_input(self, context: NarrativeContext, **kwargs) -> bool:
        """Validate input for character generation."""
        if not context.theme:
            self.logger.error("World theme is required for character generation")
            return False

        num_characters = kwargs.get('num_characters', 5)
        if num_characters < 1 or num_characters > 20:
            self.logger.error("Number of characters must be between 1 and 20")
            return False

        return True

    def _generate_characters(self, context: NarrativeContext, num_characters: int, roles: List[str]) -> List[Dict[str, Any]]:
        """Generate individual characters."""

        characters = []
        world_context_str = self._format_world_context(context)

        # Determine character types based on world theme
        theme_lower = context.theme.lower()
        if 'fantasy' in theme_lower or 'medieval' in theme_lower:
            archetypes = self.character_archetypes['fantasy']
        elif 'sci' in theme_lower or 'space' in theme_lower or 'future' in theme_lower:
            archetypes = self.character_archetypes['sci-fi']
        elif 'modern' in theme_lower or 'contemporary' in theme_lower:
            archetypes = self.character_archetypes['modern']
        elif 'historical' in theme_lower:
            archetypes = self.character_archetypes['historical']
        else:
            archetypes = self.character_archetypes['default']

        for i in range(num_characters):
            # Select role and archetype
            role = roles[i] if i < len(roles) else 'supporting'
            character_type = random.choice(archetypes)

            with dspy.context(lm=self.llm):
                result = self.character_generator(
                    world_context=world_context_str,
                    character_role=role,
                    character_type=character_type
                )

            character = {
                'id': f"char_{context.world_id}_{i+1}",
                'name': result.name,
                'role': role,
                'type': character_type,
                'age': result.age,
                'appearance': result.appearance,
                'personality': result.personality,
                'background': result.background,
                'motivations': result.motivations,
                'skills': result.skills,
                'flaws': result.flaws,
                'metadata': {
                    'creation_order': i + 1,
                    'archetype': character_type,
                    'narrative_importance': self._assess_narrative_importance(role)
                }
            }

            characters.append(character)
            self.log_operation(f"Generated character", {'name': character['name'], 'role': role, 'type': character_type})

        return characters

    def _generate_relationships(self, context: NarrativeContext, characters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate relationships between characters."""

        relationships = []
        world_context_str = self._format_world_context(context)

        # Generate relationships for main characters with others
        main_characters = [char for char in characters if char['metadata']['narrative_importance'] >= 7]

        for i, char1 in enumerate(main_characters):
            for j, char2 in enumerate(characters[i+1:], i+1):
                # Skip if both are minor characters
                if (char1['metadata']['narrative_importance'] < 5 and
                    char2['metadata']['narrative_importance'] < 5):
                    continue

                char1_summary = f"{char1['name']} - {char1['personality'][:100]}"
                char2_summary = f"{char2['name']} - {char2['personality'][:100]}"

                with dspy.context(lm=self.llm):
                    result = self.relationship_generator(
                        character1=char1_summary,
                        character2=char2_summary,
                        world_context=world_context_str
                    )

                relationship = {
                    'id': f"rel_{char1['id']}_{char2['id']}",
                    'character1_id': char1['id'],
                    'character2_id': char2['id'],
                    'type': result.relationship_type,
                    'history': result.relationship_history,
                    'current_dynamic': result.current_dynamic,
                    'potential_conflicts': result.potential_conflicts,
                    'metadata': {
                        'strength': self._assess_relationship_strength(result.relationship_type),
                        'conflict_potential': 'conflict' in result.potential_conflicts.lower()
                    }
                }

                relationships.append(relationship)

        return relationships

    def _format_world_context(self, context: NarrativeContext) -> str:
        """Format world context for character generation."""

        context_parts = [f"Theme: {context.theme}"]

        if context.world_rules:
            if isinstance(context.world_rules, dict):
                rules_text = '; '.join([f"{k}: {v}" for k, v in context.world_rules.items() if v])
            else:
                rules_text = str(context.world_rules)
            context_parts.append(f"World Rules: {rules_text}")

        if context.locations:
            location_names = [loc['name'] for loc in context.locations[:3]]
            context_parts.append(f"Key Locations: {', '.join(location_names)}")

        return '; '.join(context_parts)

    def _assess_narrative_importance(self, role: str) -> int:
        """Assess the narrative importance of a character role (1-10 scale)."""
        importance_map = {
            'protagonist': 10,
            'antagonist': 9,
            'deuteragonist': 8,
            'major supporting': 7,
            'supporting': 5,
            'minor': 3,
            'background': 1
        }

        return importance_map.get(role, 5)

    def _assess_relationship_strength(self, relationship_type: str) -> str:
        """Assess the strength of a relationship."""
        strong_types = ['family', 'spouse', 'best friend', 'mentor', 'nemesis']
        medium_types = ['friend', 'ally', 'rival', 'colleague']

        relationship_lower = relationship_type.lower()

        if any(strong_type in relationship_lower for strong_type in strong_types):
            return 'Strong'
        elif any(medium_type in relationship_lower for medium_type in medium_types):
            return 'Medium'
        else:
            return 'Weak'

    def _create_character_summary(self, characters: List[Dict[str, Any]], relationships: List[Dict[str, Any]]) -> str:
        """Create a summary of generated characters and relationships."""

        character_roles = {}
        for char in characters:
            role = char['role']
            character_roles[role] = character_roles.get(role, 0) + 1

        relationship_types = {}
        for rel in relationships:
            rel_type = rel['type']
            relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1

        role_summary = ', '.join([f"{count} {role}" for role, count in character_roles.items()])
        rel_summary = ', '.join([f"{count} {rel_type}" for rel_type, count in relationship_types.items()])

        return f"""
Character Summary:
- Cast: {role_summary}
- Relationships: {rel_summary}
- Total Characters: {len(characters)}
- Total Relationships: {len(relationships)}
"""

    def _assess_character_diversity(self, characters: List[Dict[str, Any]]) -> str:
        """Assess diversity of the character cast."""

        # Check diversity of character types
        types = set(char['type'] for char in characters)
        roles = set(char['role'] for char in characters)

        diversity_score = 0
        if len(types) >= len(characters) * 0.8:  # 80% unique types
            diversity_score += 2
        elif len(types) >= len(characters) * 0.6:  # 60% unique types
            diversity_score += 1

        if len(roles) >= 3:  # At least 3 different narrative roles
            diversity_score += 1

        if diversity_score >= 3:
            return "High"
        elif diversity_score >= 2:
            return "Medium"
        else:
            return "Low"

    def get_character_by_name(self, context: NarrativeContext, name: str) -> Optional[Dict[str, Any]]:
        """Get a character by name from the context."""
        for character in context.characters:
            if character['name'].lower() == name.lower():
                return character
        return None

    def update_character_motivation(self, context: NarrativeContext, character_id: str, new_motivation: str) -> bool:
        """Update a character's motivation based on story events."""
        for character in context.characters:
            if character['id'] == character_id:
                character['motivations'] = new_motivation
                return True
        return False