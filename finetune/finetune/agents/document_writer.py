"""
DocumentWriter Agent - Generates specific document types.

This agent specializes in creating various types of fictional documents
while maintaining consistency with the established world and characters.
"""

import json
import random
from typing import Dict, List, Any, Optional
import dspy
from datetime import datetime
from .base_agent import BaseAgent, AgentRole, AgentResponse, NarrativeContext

class DocumentGenerationSignature(dspy.Signature):
    """Generate a specific type of document within a fictional world."""

    document_type: str = dspy.InputField(desc="Type of document to generate (e.g., 'letter', 'chronicle', 'law')")
    world_context: str = dspy.InputField(desc="World setting, rules, and background information")
    character_context: str = dspy.InputField(desc="Relevant characters and their relationships")
    narrative_purpose: str = dspy.InputField(desc="What this document should accomplish in the narrative")
    existing_documents: str = dspy.InputField(desc="Summary of previously generated documents for consistency")

    title: str = dspy.OutputField(desc="Title or header for the document")
    author: str = dspy.OutputField(desc="Who created this document (character name or organization)")
    content: str = dspy.OutputField(desc="Main content of the document, appropriate to its type")
    context_notes: str = dspy.OutputField(desc="When, where, and why this document was created")
    references: str = dspy.OutputField(desc="References to characters, locations, or events mentioned")

class DocumentRefinementSignature(dspy.Signature):
    """Refine a document for consistency and quality."""

    original_document: str = dspy.InputField(desc="The original document content")
    world_rules: str = dspy.InputField(desc="World consistency rules to follow")
    consistency_issues: str = dspy.InputField(desc="Any identified consistency problems")

    refined_content: str = dspy.OutputField(desc="Improved version of the document")
    consistency_notes: str = dspy.OutputField(desc="How consistency issues were addressed")

class DocumentWriterAgent(BaseAgent):
    """
    Agent responsible for generating various types of fictional documents.

    This agent creates documents that serve specific narrative purposes while
    maintaining consistency with the established world, characters, and timeline.
    """

    def __init__(self, llm: Optional[dspy.LM] = None, **kwargs):
        super().__init__(role=AgentRole.DOCUMENT_WRITER, llm=llm, **kwargs)

        # Initialize DSPy modules
        with dspy.context(lm=self.llm):
            self.document_generator = dspy.ChainOfThought(DocumentGenerationSignature)
            self.document_refiner = dspy.ChainOfThought(DocumentRefinementSignature)

        # Document type templates and characteristics
        self.document_templates = {
            'chronicle': {
                'description': 'Historical record documenting events over time',
                'typical_length': (1000, 3000),
                'style': 'formal, historical',
                'author_types': ['historian', 'scribe', 'witness'],
                'content_focus': 'events, dates, consequences'
            },
            'letter': {
                'description': 'Personal correspondence between characters',
                'typical_length': (300, 1200),
                'style': 'personal, intimate',
                'author_types': ['any character'],
                'content_focus': 'emotions, requests, news'
            },
            'diary': {
                'description': 'Personal journal entries',
                'typical_length': (400, 1500),
                'style': 'introspective, personal',
                'author_types': ['any character'],
                'content_focus': 'thoughts, feelings, daily events'
            },
            'law': {
                'description': 'Legal document or decree',
                'typical_length': (500, 2000),
                'style': 'formal, authoritative',
                'author_types': ['ruler', 'council', 'judge'],
                'content_focus': 'rules, consequences, procedures'
            },
            'treaty': {
                'description': 'Agreement between factions or nations',
                'typical_length': (800, 2500),
                'style': 'formal, diplomatic',
                'author_types': ['diplomat', 'ruler', 'representative'],
                'content_focus': 'terms, obligations, signatures'
            },
            'report': {
                'description': 'Official account of events or investigations',
                'typical_length': (600, 2000),
                'style': 'factual, professional',
                'author_types': ['investigator', 'scout', 'official'],
                'content_focus': 'findings, evidence, recommendations'
            },
            'map': {
                'description': 'Geographical description with locations and features',
                'typical_length': (400, 1200),
                'style': 'descriptive, technical',
                'author_types': ['cartographer', 'explorer', 'scholar'],
                'content_focus': 'locations, distances, landmarks'
            },
            'inventory': {
                'description': 'List of items, resources, or people',
                'typical_length': (300, 1500),
                'style': 'systematic, detailed',
                'author_types': ['clerk', 'steward', 'merchant'],
                'content_focus': 'quantities, descriptions, values'
            },
            'song': {
                'description': 'Cultural artifact with lyrics or poetry',
                'typical_length': (200, 800),
                'style': 'artistic, rhythmic',
                'author_types': ['bard', 'poet', 'minstrel'],
                'content_focus': 'story, emotion, cultural values'
            },
            'newspaper': {
                'description': 'News article or public announcement',
                'typical_length': (400, 1500),
                'style': 'informative, engaging',
                'author_types': ['journalist', 'herald', 'editor'],
                'content_focus': 'current events, public interest'
            }
        }

    def execute(self, context: NarrativeContext, **kwargs) -> AgentResponse:
        """
        Generate documents for the given narrative context.

        Args:
            context: Narrative context with world and character information
            **kwargs: Additional parameters:
                - document_types: List of document types to generate
                - num_documents: Number of documents to generate
                - specific_purpose: Specific narrative purpose for documents
                - author_preferences: Preferred authors for documents

        Returns:
            AgentResponse containing the generated documents
        """
        try:
            # Extract parameters
            document_types = kwargs.get('document_types', ['chronicle', 'letter', 'diary'])
            num_documents = kwargs.get('num_documents', 3)
            specific_purpose = kwargs.get('specific_purpose', 'advance the narrative')
            author_preferences = kwargs.get('author_preferences', {})

            # Generate documents
            documents = self._generate_documents(
                context, document_types, num_documents, specific_purpose, author_preferences
            )

            # Refine documents for consistency
            refined_documents = self._refine_documents(context, documents)

            # Update context
            self.update_context(context, {'generated_documents': refined_documents})

            return AgentResponse(
                success=True,
                content={
                    'documents': refined_documents,
                    'document_summary': self._create_document_summary(refined_documents),
                    'cross_references': self._extract_cross_references(refined_documents)
                },
                metadata={
                    'documents_generated': len(refined_documents),
                    'document_types': list(set(doc['type'] for doc in refined_documents)),
                    'average_length': sum(len(doc['content']) for doc in refined_documents) / len(refined_documents),
                    'consistency_score': self._assess_consistency(refined_documents, context)
                }
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                content=None,
                error_message=f"Document generation failed: {str(e)}"
            )

    def validate_input(self, context: NarrativeContext, **kwargs) -> bool:
        """Validate input for document generation."""
        if not context.world_rules and not context.theme:
            self.logger.error("World context is required for document generation")
            return False

        document_types = kwargs.get('document_types', [])
        if document_types:
            unsupported_types = [dt for dt in document_types if dt not in self.document_templates]
            if unsupported_types:
                self.logger.error(f"Unsupported document types: {unsupported_types}")
                return False

        num_documents = kwargs.get('num_documents', 3)
        if num_documents < 1 or num_documents > 50:
            self.logger.error("Number of documents must be between 1 and 50")
            return False

        return True

    def _generate_documents(self, context: NarrativeContext, document_types: List[str],
                           num_documents: int, narrative_purpose: str,
                           author_preferences: Dict[str, str]) -> List[Dict[str, Any]]:
        """Generate the requested documents."""

        documents = []
        world_context_str = self._format_world_context(context)
        character_context_str = self._format_character_context(context)
        existing_docs_str = self._format_existing_documents(context)

        for i in range(num_documents):
            # Select document type
            doc_type = document_types[i % len(document_types)]

            # Determine author
            author = self._select_document_author(context, doc_type, author_preferences)

            # Customize narrative purpose for this document
            specific_purpose = self._customize_narrative_purpose(
                doc_type, narrative_purpose, i, num_documents
            )

            with dspy.context(lm=self.llm):
                result = self.document_generator(
                    document_type=doc_type,
                    world_context=world_context_str,
                    character_context=character_context_str,
                    narrative_purpose=specific_purpose,
                    existing_documents=existing_docs_str
                )

            document = {
                'id': f"doc_{context.world_id}_{i+1}",
                'type': doc_type,
                'title': result.title,
                'author': author or result.author,
                'content': result.content,
                'context_notes': result.context_notes,
                'references': result.references,
                'metadata': {
                    'creation_order': i + 1,
                    'narrative_purpose': specific_purpose,
                    'template_info': self.document_templates[doc_type],
                    'word_count': len(result.content.split()),
                    'generated_at': datetime.now().isoformat()
                }
            }

            documents.append(document)
            self.log_operation(f"Generated {doc_type} document", {
                'title': document['title'][:50] + '...',
                'author': document['author'],
                'word_count': document['metadata']['word_count']
            })

        return documents

    def _refine_documents(self, context: NarrativeContext, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Refine documents for consistency and quality."""

        refined_documents = []
        world_rules_str = self._format_world_rules(context)

        for doc in documents:
            # Check for consistency issues
            consistency_issues = self._identify_consistency_issues(doc, context, documents)

            if consistency_issues:
                self.log_operation(f"Refining document {doc['title']}", {
                    'issues_found': len(consistency_issues)
                })

                with dspy.context(lm=self.llm):
                    refinement_result = self.document_refiner(
                        original_document=doc['content'],
                        world_rules=world_rules_str,
                        consistency_issues='; '.join(consistency_issues)
                    )

                # Update document with refined content
                doc['content'] = refinement_result.refined_content
                doc['metadata']['refined'] = True
                doc['metadata']['consistency_notes'] = refinement_result.consistency_notes
            else:
                doc['metadata']['refined'] = False

            refined_documents.append(doc)

        return refined_documents

    def _format_world_context(self, context: NarrativeContext) -> str:
        """Format world context for document generation."""
        context_parts = [f"Theme: {context.theme}"]

        if context.world_rules:
            if isinstance(context.world_rules, dict):
                rules_text = '; '.join([f"{k}: {v}" for k, v in context.world_rules.items() if v])
            else:
                rules_text = str(context.world_rules)
            context_parts.append(f"World Rules: {rules_text}")

        if context.locations:
            locations_text = '; '.join([f"{loc['name']}: {loc['description'][:100]}" for loc in context.locations[:5]])
            context_parts.append(f"Key Locations: {locations_text}")

        return ' | '.join(context_parts)

    def _format_character_context(self, context: NarrativeContext) -> str:
        """Format character context for document generation."""
        if not context.characters:
            return "No established characters yet"

        character_summaries = []
        for char in context.characters[:10]:  # Limit to top 10 characters
            summary = f"{char['name']} ({char['role']}): {char['personality'][:100]}"
            character_summaries.append(summary)

        return ' | '.join(character_summaries)

    def _format_existing_documents(self, context: NarrativeContext) -> str:
        """Format existing documents for consistency reference."""
        if not context.generated_documents:
            return "No previous documents"

        doc_summaries = []
        for doc in context.generated_documents[-5:]:  # Last 5 documents
            summary = f"{doc['type']}: {doc['title']} by {doc['author']}"
            doc_summaries.append(summary)

        return ' | '.join(doc_summaries)

    def _format_world_rules(self, context: NarrativeContext) -> str:
        """Format world rules for consistency checking."""
        if isinstance(context.world_rules, dict):
            return '; '.join([f"{k}: {v}" for k, v in context.world_rules.items() if v])
        else:
            return str(context.world_rules) if context.world_rules else "No specific world rules established"

    def _select_document_author(self, context: NarrativeContext, doc_type: str,
                               author_preferences: Dict[str, str]) -> Optional[str]:
        """Select an appropriate author for the document."""

        # Check for explicit preference
        if doc_type in author_preferences:
            return author_preferences[doc_type]

        # Select based on document type and available characters
        template = self.document_templates[doc_type]
        suitable_authors = []

        for character in context.characters:
            char_type = character.get('type', '').lower()
            char_role = character.get('role', '').lower()

            # Check if character fits document author types
            for author_type in template['author_types']:
                if author_type == 'any character' or author_type in char_type or author_type in char_role:
                    suitable_authors.append(character['name'])
                    break

        return random.choice(suitable_authors) if suitable_authors else None

    def _customize_narrative_purpose(self, doc_type: str, base_purpose: str,
                                   doc_index: int, total_docs: int) -> str:
        """Customize the narrative purpose for a specific document."""

        template = self.document_templates[doc_type]
        specific_purposes = {
            'chronicle': f"Document historical events to establish timeline and world history",
            'letter': f"Reveal character relationships and personal motivations through correspondence",
            'diary': f"Provide intimate character perspective and internal monologue",
            'law': f"Establish world rules and social structures through legal framework",
            'treaty': f"Show political relationships and conflicts between factions",
            'report': f"Present factual information about events or investigations",
            'map': f"Describe geographical features and spatial relationships in the world",
            'inventory': f"Detail resources, items, or organizational structure",
            'song': f"Express cultural values and historical memory through artistic form",
            'newspaper': f"Communicate current events and public sentiment"
        }

        return specific_purposes.get(doc_type, base_purpose)

    def _identify_consistency_issues(self, document: Dict[str, Any], context: NarrativeContext,
                                   all_documents: List[Dict[str, Any]]) -> List[str]:
        """Identify potential consistency issues in a document."""

        issues = []

        # Check for character name consistency
        mentioned_characters = self._extract_character_mentions(document['content'])
        for char_name in mentioned_characters:
            if not self._find_character_by_name(context, char_name):
                issues.append(f"Character '{char_name}' mentioned but not established in world")

        # Check for location consistency
        mentioned_locations = self._extract_location_mentions(document['content'])
        for loc_name in mentioned_locations:
            if not self._find_location_by_name(context, loc_name):
                issues.append(f"Location '{loc_name}' mentioned but not established in world")

        # Check for contradictions with previous documents
        contradictions = self._check_document_contradictions(document, context.generated_documents)
        issues.extend(contradictions)

        return issues

    def _extract_character_mentions(self, content: str) -> List[str]:
        """Extract character names mentioned in document content."""
        # This is a simplified implementation
        # In practice, you'd use more sophisticated NLP techniques
        import re

        # Look for capitalized words that might be names
        potential_names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)

        # Filter out common words that aren't names
        common_words = {'The', 'This', 'That', 'These', 'Those', 'When', 'Where', 'What', 'Why', 'How', 'And', 'But', 'Or'}
        names = [name for name in potential_names if name not in common_words]

        return list(set(names))  # Remove duplicates

    def _extract_location_mentions(self, content: str) -> List[str]:
        """Extract location names mentioned in document content."""
        # Similar to character extraction but looking for location patterns
        import re

        # Look for phrases like "in [Place]", "at [Place]", "from [Place]"
        location_patterns = [
            r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\bat\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\bfrom\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\bto\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]

        locations = []
        for pattern in location_patterns:
            matches = re.findall(pattern, content)
            locations.extend(matches)

        return list(set(locations))

    def _find_character_by_name(self, context: NarrativeContext, name: str) -> Optional[Dict[str, Any]]:
        """Find a character by name in the context."""
        for character in context.characters:
            if character['name'].lower() == name.lower():
                return character
        return None

    def _find_location_by_name(self, context: NarrativeContext, name: str) -> Optional[Dict[str, Any]]:
        """Find a location by name in the context."""
        for location in context.locations:
            if location['name'].lower() == name.lower():
                return location
        return None

    def _check_document_contradictions(self, document: Dict[str, Any],
                                     existing_documents: List[Dict[str, Any]]) -> List[str]:
        """Check for contradictions with existing documents."""

        contradictions = []

        # This is a simplified check - in practice you'd use more sophisticated methods
        # For now, we'll just flag if the same event is described differently

        # Check for timeline contradictions by looking for date references
        import re

        date_patterns = re.findall(r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:day|month|year)', document['content'].lower())

        if date_patterns:
            # Check if these dates contradict any dates in existing documents
            for existing_doc in existing_documents:
                existing_dates = re.findall(r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:day|month|year)', existing_doc['content'].lower())

                # Simple check for conflicting date references
                # This could be much more sophisticated
                if date_patterns and existing_dates:
                    # If both documents mention dates, flag for manual review
                    contradictions.append(f"Potential timeline conflict with document '{existing_doc['title']}'")

        return contradictions

    def _create_document_summary(self, documents: List[Dict[str, Any]]) -> str:
        """Create a summary of generated documents."""

        doc_types = {}
        total_words = 0
        authors = set()

        for doc in documents:
            doc_type = doc['type']
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            total_words += doc['metadata']['word_count']
            authors.add(doc['author'])

        type_summary = ', '.join([f"{count} {doc_type}" for doc_type, count in doc_types.items()])
        avg_words = total_words // len(documents) if documents else 0

        return f"""
Document Summary:
- Types Generated: {type_summary}
- Total Documents: {len(documents)}
- Total Words: {total_words:,}
- Average Length: {avg_words:,} words
- Unique Authors: {len(authors)}
- Authors: {', '.join(sorted(list(authors))[:5])}{"..." if len(authors) > 5 else ""}
"""

    def _extract_cross_references(self, documents: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Extract cross-references between documents."""

        cross_references = {}

        for doc in documents:
            doc_id = doc['id']
            references = []

            # Extract references from the 'references' field
            if doc['references']:
                ref_parts = doc['references'].split(';')
                references.extend([ref.strip() for ref in ref_parts if ref.strip()])

            # Extract character and location mentions
            characters = self._extract_character_mentions(doc['content'])
            locations = self._extract_location_mentions(doc['content'])

            references.extend([f"Character: {char}" for char in characters])
            references.extend([f"Location: {loc}" for loc in locations])

            cross_references[doc_id] = references

        return cross_references

    def _assess_consistency(self, documents: List[Dict[str, Any]], context: NarrativeContext) -> float:
        """Assess the consistency score of generated documents."""

        total_issues = 0
        total_checks = 0

        for doc in documents:
            issues = self._identify_consistency_issues(doc, context, documents)
            total_issues += len(issues)
            total_checks += 10  # Assume 10 consistency checks per document

        consistency_score = max(0.0, 1.0 - (total_issues / max(total_checks, 1)))
        return round(consistency_score, 2)