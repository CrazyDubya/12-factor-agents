"""
PromptTemplateManager - Structured prompts for different document types.

This module manages sophisticated prompt templates that ensure consistent,
high-quality generation across different document types and narrative contexts.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import random

logger = logging.getLogger(__name__)

@dataclass
class PromptTemplate:
    """A structured prompt template for document generation."""
    template_id: str
    document_type: str
    template_text: str
    required_variables: List[str]
    optional_variables: List[str]
    style_instructions: str
    quality_criteria: str
    examples: List[str]
    metadata: Dict[str, Any]

class PromptTemplateManager:
    """
    Manages structured prompt templates for narrative document generation.

    This class provides sophisticated prompting strategies that incorporate
    world context, character information, and document-specific requirements.
    """

    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize the prompt template manager.

        Args:
            template_dir: Directory containing custom template files
        """
        self.template_dir = template_dir
        self.templates: Dict[str, PromptTemplate] = {}
        self.logger = logging.getLogger(__name__)

        # Initialize built-in templates
        self._load_builtin_templates()

        # Load custom templates if directory provided
        if template_dir and template_dir.exists():
            self._load_custom_templates(template_dir)

    def get_template(self, document_type: str, theme: Optional[str] = None) -> Optional[PromptTemplate]:
        """
        Get a template for a specific document type and theme.

        Args:
            document_type: Type of document to generate
            theme: Optional theme to customize the template

        Returns:
            PromptTemplate object or None if not found
        """
        # Try theme-specific template first
        if theme:
            theme_key = f"{document_type}_{theme.lower().replace(' ', '_')}"
            if theme_key in self.templates:
                return self.templates[theme_key]

        # Fall back to generic template
        return self.templates.get(document_type)

    def format_prompt(self, template: PromptTemplate, **kwargs) -> str:
        """
        Format a template with provided variables.

        Args:
            template: Template to format
            **kwargs: Variables to substitute in template

        Returns:
            Formatted prompt string
        """
        try:
            # Check required variables
            missing_vars = [var for var in template.required_variables if var not in kwargs]
            if missing_vars:
                self.logger.warning(f"Missing required variables for template {template.template_id}: {missing_vars}")

            # Format the template
            formatted_prompt = template.template_text.format(**kwargs)

            return formatted_prompt

        except Exception as e:
            self.logger.error(f"Error formatting template {template.template_id}: {str(e)}")
            return template.template_text  # Return unformatted template as fallback

    def create_world_context_prompt(self, world_context: Dict[str, Any],
                                  document_type: str, specific_requirements: str = "") -> str:
        """
        Create a comprehensive prompt incorporating world context.

        Args:
            world_context: World information and constraints
            document_type: Type of document to generate
            specific_requirements: Additional specific requirements

        Returns:
            Formatted prompt with world context
        """
        template = self.get_template(document_type, world_context.get('theme'))

        if not template:
            return self._create_fallback_prompt(document_type, world_context, specific_requirements)

        # Extract world context information
        world_info = self._format_world_context(world_context)
        character_info = self._format_character_context(world_context.get('characters', []))
        location_info = self._format_location_context(world_context.get('locations', []))

        # Format template with world context
        formatted_prompt = self.format_prompt(
            template,
            world_context=world_info,
            character_context=character_info,
            location_context=location_info,
            theme=world_context.get('theme', 'fantasy'),
            document_type=document_type,
            specific_requirements=specific_requirements,
            style_guidance=template.style_instructions,
            quality_expectations=template.quality_criteria
        )

        return formatted_prompt

    def _load_builtin_templates(self):
        """Load built-in prompt templates."""

        # Chronicle template
        self.templates['chronicle'] = PromptTemplate(
            template_id='chronicle_default',
            document_type='chronicle',
            template_text=self._get_chronicle_template(),
            required_variables=['world_context', 'theme'],
            optional_variables=['character_context', 'location_context', 'specific_requirements'],
            style_instructions="Write in a formal, historical tone as if recording events for posterity.",
            quality_criteria="Must maintain chronological consistency and factual coherence.",
            examples=[],
            metadata={'complexity': 'medium', 'typical_length': '1000-3000 words'}
        )

        # Diary template
        self.templates['diary'] = PromptTemplate(
            template_id='diary_default',
            document_type='diary',
            template_text=self._get_diary_template(),
            required_variables=['world_context', 'character_context'],
            optional_variables=['theme', 'location_context', 'specific_requirements'],
            style_instructions="Write in first person with personal, intimate tone reflecting the character's personality.",
            quality_criteria="Must maintain character voice consistency and emotional authenticity.",
            examples=[],
            metadata={'complexity': 'low', 'typical_length': '400-1500 words'}
        )

        # Letter template
        self.templates['letter'] = PromptTemplate(
            template_id='letter_default',
            document_type='letter',
            template_text=self._get_letter_template(),
            required_variables=['world_context', 'character_context'],
            optional_variables=['theme', 'recipient_info', 'specific_requirements'],
            style_instructions="Write as personal correspondence with appropriate greeting and closing.",
            quality_criteria="Must reflect sender's relationship with recipient and current world events.",
            examples=[],
            metadata={'complexity': 'low', 'typical_length': '300-1200 words'}
        )

        # Law template
        self.templates['law'] = PromptTemplate(
            template_id='law_default',
            document_type='law',
            template_text=self._get_law_template(),
            required_variables=['world_context', 'theme'],
            optional_variables=['authority_info', 'specific_requirements'],
            style_instructions="Write in formal, authoritative legal language with clear structure.",
            quality_criteria="Must be internally consistent and reflect world's political structure.",
            examples=[],
            metadata={'complexity': 'high', 'typical_length': '500-2000 words'}
        )

        # Report template
        self.templates['report'] = PromptTemplate(
            template_id='report_default',
            document_type='report',
            template_text=self._get_report_template(),
            required_variables=['world_context', 'subject_matter'],
            optional_variables=['author_info', 'specific_requirements'],
            style_instructions="Write in objective, factual tone with clear organization and evidence.",
            quality_criteria="Must present information logically and maintain factual consistency.",
            examples=[],
            metadata={'complexity': 'medium', 'typical_length': '600-2000 words'}
        )

        # Add more templates
        for doc_type in ['treaty', 'map', 'inventory', 'song', 'newspaper']:
            self._add_generic_template(doc_type)

    def _get_chronicle_template(self) -> str:
        """Get the chronicle document template."""
        return """You are writing a historical chronicle for the world of {theme}. This chronicle should document significant events, providing context and consequences that shape the world's history.

WORLD CONTEXT:
{world_context}

CHARACTERS INVOLVED:
{character_context}

LOCATIONS:
{location_context}

WRITING GUIDELINES:
{style_guidance}

QUALITY REQUIREMENTS:
{quality_expectations}

SPECIFIC REQUIREMENTS:
{specific_requirements}

Write a chronicle entry that:
1. Documents a significant historical event or period
2. Provides context about causes and consequences
3. Mentions relevant characters and locations from the world
4. Maintains consistency with established world rules
5. Uses formal, historical language appropriate for official records

The chronicle should be between 1000-3000 words and feel authentic to the {theme} setting.

Begin your chronicle:"""

    def _get_diary_template(self) -> str:
        """Get the diary document template."""
        return """You are writing a personal diary entry from the perspective of a character in the world of {theme}. This should be intimate and personal, revealing the character's thoughts, feelings, and experiences.

WORLD CONTEXT:
{world_context}

YOUR CHARACTER:
{character_context}

CURRENT LOCATION:
{location_context}

WRITING GUIDELINES:
{style_guidance}

QUALITY REQUIREMENTS:
{quality_expectations}

SPECIFIC REQUIREMENTS:
{specific_requirements}

Write a diary entry that:
1. Reflects the character's personality and speaking voice
2. Describes recent events from their personal perspective
3. Shows emotional responses and internal thoughts
4. References other characters and locations naturally
5. Maintains consistency with the character's established traits

The diary entry should be between 400-1500 words and feel authentic to both the character and the {theme} setting.

Dear Diary,"""

    def _get_letter_template(self) -> str:
        """Get the letter document template."""
        return """You are writing a letter from one character to another in the world of {theme}. This should feel like authentic correspondence, reflecting the relationship between sender and recipient.

WORLD CONTEXT:
{world_context}

LETTER WRITER:
{character_context}

RECIPIENT INFORMATION:
{recipient_info}

CURRENT SITUATION:
{location_context}

WRITING GUIDELINES:
{style_guidance}

QUALITY REQUIREMENTS:
{quality_expectations}

SPECIFIC REQUIREMENTS:
{specific_requirements}

Write a letter that:
1. Uses appropriate greeting and closing for the relationship
2. Shares news, requests, or personal thoughts
3. Reflects the sender's voice and relationship with recipient
4. References current events in the world naturally
5. Maintains consistency with established character relationships

The letter should be between 300-1200 words and feel authentic to the {theme} setting.

Begin your letter:"""

    def _get_law_template(self) -> str:
        """Get the law/decree document template."""
        return """You are writing an official law, decree, or legal document for the world of {theme}. This should reflect the political structure and legal system of the world.

WORLD CONTEXT:
{world_context}

POLITICAL STRUCTURE:
{authority_info}

LEGAL FRAMEWORK:
{location_context}

WRITING GUIDELINES:
{style_guidance}

QUALITY REQUIREMENTS:
{quality_expectations}

SPECIFIC REQUIREMENTS:
{specific_requirements}

Write a legal document that:
1. Uses formal, authoritative language appropriate to the world
2. Establishes clear rules, punishments, or procedures
3. Reflects the world's political and social structure
4. Maintains consistency with established world rules
5. Includes proper legal formatting (articles, sections, etc.)

The document should be between 500-2000 words and feel authentic to the {theme} setting's legal system.

By decree of [Authority]:"""

    def _get_report_template(self) -> str:
        """Get the report document template."""
        return """You are writing an official report about {subject_matter} in the world of {theme}. This should be objective, factual, and well-organized.

WORLD CONTEXT:
{world_context}

REPORT AUTHOR:
{author_info}

SUBJECT MATTER:
{subject_matter}

WRITING GUIDELINES:
{style_guidance}

QUALITY REQUIREMENTS:
{quality_expectations}

SPECIFIC REQUIREMENTS:
{specific_requirements}

Write a report that:
1. Presents information objectively and systematically
2. Includes relevant evidence and observations
3. Maintains factual consistency with the world
4. Uses appropriate formal structure (introduction, findings, conclusion)
5. Reflects the author's expertise and perspective

The report should be between 600-2000 words and feel authentic to the {theme} setting.

OFFICIAL REPORT:"""

    def _add_generic_template(self, doc_type: str):
        """Add a generic template for a document type."""

        style_instructions = {
            'treaty': "Write as formal diplomatic agreement with clear terms and conditions.",
            'map': "Write as detailed geographical description with landmarks and distances.",
            'inventory': "Write as systematic catalog with detailed descriptions and quantities.",
            'song': "Write as artistic expression with rhythm, emotion, and cultural significance.",
            'newspaper': "Write as informative news article with engaging headlines and current events."
        }

        quality_criteria = {
            'treaty': "Must include specific terms, obligations, and consequences for all parties.",
            'map': "Must provide clear spatial relationships and consistent geographical details.",
            'inventory': "Must be systematic, accurate, and reflect the world's available resources.",
            'song': "Must reflect cultural values and artistic traditions of the world.",
            'newspaper': "Must report current events that advance the narrative and world development."
        }

        template_text = f"""You are writing a {doc_type} for the world of {{theme}}.

WORLD CONTEXT:
{{world_context}}

CHARACTER CONTEXT:
{{character_context}}

LOCATION CONTEXT:
{{location_context}}

WRITING GUIDELINES:
{{style_guidance}}

QUALITY REQUIREMENTS:
{{quality_expectations}}

SPECIFIC REQUIREMENTS:
{{specific_requirements}}

Create a {doc_type} that maintains consistency with the established world while serving its specific narrative purpose.

Begin your {doc_type}:"""

        self.templates[doc_type] = PromptTemplate(
            template_id=f'{doc_type}_default',
            document_type=doc_type,
            template_text=template_text,
            required_variables=['world_context', 'theme'],
            optional_variables=['character_context', 'location_context', 'specific_requirements'],
            style_instructions=style_instructions.get(doc_type, f"Write appropriate to {doc_type} format and purpose."),
            quality_criteria=quality_criteria.get(doc_type, f"Must serve the narrative purpose of a {doc_type}."),
            examples=[],
            metadata={'complexity': 'medium', 'typical_length': '500-1500 words'}
        )

    def _load_custom_templates(self, template_dir: Path):
        """Load custom templates from directory."""
        try:
            for template_file in template_dir.glob('*.json'):
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)

                template = PromptTemplate(**template_data)
                self.templates[template.template_id] = template

                self.logger.info(f"Loaded custom template: {template.template_id}")

        except Exception as e:
            self.logger.error(f"Error loading custom templates: {str(e)}")

    def _format_world_context(self, world_context: Dict[str, Any]) -> str:
        """Format world context information for prompts."""
        context_parts = []

        theme = world_context.get('theme', 'Unknown')
        context_parts.append(f"World Theme: {theme}")

        world_rules = world_context.get('world_rules', {})
        if world_rules:
            if isinstance(world_rules, dict):
                rules_text = []
                for rule_type, rule_desc in world_rules.items():
                    if rule_desc:
                        rules_text.append(f"- {rule_type.title()}: {rule_desc}")
                if rules_text:
                    context_parts.append("World Rules:\n" + "\n".join(rules_text))
            else:
                context_parts.append(f"World Rules: {world_rules}")

        # Add any additional world context
        for key, value in world_context.items():
            if key not in ['theme', 'world_rules', 'characters', 'locations'] and value:
                context_parts.append(f"{key.replace('_', ' ').title()}: {value}")

        return "\n\n".join(context_parts) if context_parts else "No specific world context provided."

    def _format_character_context(self, characters: List[Dict[str, Any]]) -> str:
        """Format character information for prompts."""
        if not characters:
            return "No established characters."

        character_descriptions = []
        for char in characters[:5]:  # Limit to top 5 characters
            desc_parts = [f"• {char.get('name', 'Unnamed')} ({char.get('role', 'unknown role')})"]

            if char.get('personality'):
                desc_parts.append(f"  Personality: {char['personality'][:100]}...")

            if char.get('motivations'):
                desc_parts.append(f"  Motivations: {char['motivations'][:100]}...")

            character_descriptions.append("\n".join(desc_parts))

        return "\n\n".join(character_descriptions)

    def _format_location_context(self, locations: List[Dict[str, Any]]) -> str:
        """Format location information for prompts."""
        if not locations:
            return "No established locations."

        location_descriptions = []
        for loc in locations[:5]:  # Limit to top 5 locations
            desc_parts = [f"• {loc.get('name', 'Unnamed')} ({loc.get('type', 'unknown type')})"]

            if loc.get('description'):
                desc_parts.append(f"  Description: {loc['description'][:150]}...")

            if loc.get('significance'):
                desc_parts.append(f"  Significance: {loc['significance'][:100]}...")

            location_descriptions.append("\n".join(desc_parts))

        return "\n\n".join(location_descriptions)

    def _create_fallback_prompt(self, document_type: str, world_context: Dict[str, Any],
                              specific_requirements: str) -> str:
        """Create a fallback prompt when no template is available."""

        world_info = self._format_world_context(world_context)
        theme = world_context.get('theme', 'fantasy')

        fallback_prompt = f"""You are writing a {document_type} document for the world of {theme}.

WORLD CONTEXT:
{world_info}

REQUIREMENTS:
{specific_requirements}

Create a {document_type} that:
1. Maintains consistency with the established world
2. Serves its intended narrative purpose
3. Uses appropriate style and tone for the document type
4. Includes relevant details about characters and locations

Write the {document_type}:"""

        return fallback_prompt

    def create_consistency_prompt(self, document: Dict[str, Any],
                                world_context: Dict[str, Any],
                                consistency_issues: List[str]) -> str:
        """Create a prompt for fixing consistency issues in a document."""

        issue_descriptions = "\n".join([f"- {issue}" for issue in consistency_issues])
        world_info = self._format_world_context(world_context)

        consistency_prompt = f"""Please revise the following {document['type']} document to fix consistency issues while maintaining its core content and narrative purpose.

ORIGINAL DOCUMENT:
Title: {document.get('title', 'Untitled')}
Content: {document['content']}

WORLD CONTEXT FOR REFERENCE:
{world_info}

CONSISTENCY ISSUES TO FIX:
{issue_descriptions}

REVISION REQUIREMENTS:
1. Fix all identified consistency issues
2. Maintain the document's original purpose and tone
3. Ensure consistency with established world rules
4. Keep character names and traits consistent
5. Preserve important plot and world-building elements

Please provide the revised document that addresses these consistency issues while maintaining narrative quality."""

        return consistency_prompt

    def create_expansion_prompt(self, document: Dict[str, Any],
                              expansion_type: str = "detail") -> str:
        """Create a prompt for expanding a document with additional detail."""

        expansion_prompts = {
            "detail": "Add more descriptive detail and sensory information",
            "dialogue": "Include more character dialogue and interaction",
            "backstory": "Expand with relevant backstory and historical context",
            "consequences": "Explore the consequences and implications of events",
            "emotion": "Deepen the emotional content and character development"
        }

        expansion_instruction = expansion_prompts.get(expansion_type, "Add more depth and detail")

        expansion_prompt = f"""Please expand the following {document['type']} document by adding {expansion_instruction}.

ORIGINAL DOCUMENT:
Title: {document.get('title', 'Untitled')}
Content: {document['content']}

EXPANSION REQUIREMENTS:
1. {expansion_instruction.capitalize()}
2. Maintain consistency with the original content
3. Preserve the document's tone and style
4. Ensure all additions feel natural and necessary
5. Keep the expanded content within reasonable length

Please provide the expanded version of the document:"""

        return expansion_prompt

    def get_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available templates."""

        template_info = {}

        for template_id, template in self.templates.items():
            template_info[template_id] = {
                'document_type': template.document_type,
                'required_variables': template.required_variables,
                'optional_variables': template.optional_variables,
                'complexity': template.metadata.get('complexity', 'medium'),
                'typical_length': template.metadata.get('typical_length', 'varies')
            }

        return template_info

    def validate_template_variables(self, template: PromptTemplate,
                                  provided_variables: Dict[str, Any]) -> List[str]:
        """Validate that all required template variables are provided."""

        missing_variables = []

        for required_var in template.required_variables:
            if required_var not in provided_variables:
                missing_variables.append(required_var)

        return missing_variables

    def create_multi_document_prompt(self, document_types: List[str],
                                   world_context: Dict[str, Any],
                                   narrative_connection: str) -> str:
        """Create a prompt for generating multiple related documents."""

        world_info = self._format_world_context(world_context)
        doc_list = ", ".join(document_types)

        multi_doc_prompt = f"""You are creating a series of related documents for the world of {world_context.get('theme', 'fantasy')}. These documents should tell a connected story and maintain consistency across all pieces.

WORLD CONTEXT:
{world_info}

DOCUMENTS TO CREATE:
{doc_list}

NARRATIVE CONNECTION:
{narrative_connection}

REQUIREMENTS FOR THE DOCUMENT SERIES:
1. All documents must be consistent with each other
2. Characters and events should connect across documents
3. Each document should serve its specific purpose while advancing the overall narrative
4. Maintain appropriate tone and style for each document type
5. Ensure timeline and factual consistency across all pieces

Please create each document in sequence, ensuring they work together as a cohesive narrative collection."""

        return multi_doc_prompt