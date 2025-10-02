"""
DataAugmentor - Techniques for expanding and diversifying synthetic datasets.

This module provides sophisticated data augmentation techniques specifically
designed for narrative content, including paraphrasing, style transfer,
perspective shifts, and content expansion.
"""

import logging
import random
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import json

import numpy as np

logger = logging.getLogger(__name__)

class AugmentationType(Enum):
    """Types of data augmentation techniques."""
    PARAPHRASING = "paraphrasing"
    STYLE_TRANSFER = "style_transfer"
    PERSPECTIVE_SHIFT = "perspective_shift"
    CONTENT_EXPANSION = "content_expansion"
    TEMPORAL_SHIFT = "temporal_shift"
    GENRE_ADAPTATION = "genre_adaptation"
    CHARACTER_FOCUS = "character_focus"
    EMOTIONAL_TONE = "emotional_tone"

@dataclass
class AugmentationConfig:
    """Configuration for data augmentation."""
    techniques: List[AugmentationType]
    augmentation_ratio: float = 0.3  # Ratio of original data to augment
    preserve_entities: bool = True
    preserve_plot_points: bool = True
    max_length_change: float = 0.5  # Maximum change in document length
    quality_threshold: float = 0.7

class DataAugmentor:
    """
    Sophisticated data augmentation for narrative content.

    This class provides various techniques to expand and diversify training
    datasets while maintaining narrative coherence and world consistency.
    """

    def __init__(self, llm=None):
        """
        Initialize the data augmentor.

        Args:
            llm: Language model for generating augmented content
        """
        self.llm = llm
        self.logger = logging.getLogger(__name__)

        # Style transfer mappings
        self.style_mappings = {
            'formal_to_casual': {
                'patterns': [
                    (r'\bshall\b', 'will'),
                    (r'\bmust\b', 'have to'),
                    (r'\bwherein\b', 'where'),
                    (r'\btherefore\b', 'so'),
                    (r'\bhowever\b', 'but'),
                    (r'\bnevertheless\b', 'still'),
                ]
            },
            'casual_to_formal': {
                'patterns': [
                    (r'\bwill\b', 'shall'),
                    (r'\bhave to\b', 'must'),
                    (r'\bso\b', 'therefore'),
                    (r'\bbut\b', 'however'),
                    (r'\bstill\b', 'nevertheless'),
                ]
            },
            'archaic_to_modern': {
                'patterns': [
                    (r'\bthou\b', 'you'),
                    (r'\bthee\b', 'you'),
                    (r'\bthy\b', 'your'),
                    (r'\bthine\b', 'yours'),
                    (r'\bhath\b', 'has'),
                    (r'\bdoth\b', 'does'),
                ]
            }
        }

        # Emotional tone modifiers
        self.emotional_modifiers = {
            'neutral_to_dramatic': [
                ('said', 'declared'),
                ('went', 'rushed'),
                ('looked', 'gazed intensely'),
                ('spoke', 'proclaimed'),
            ],
            'dramatic_to_subtle': [
                ('declared', 'mentioned'),
                ('rushed', 'moved'),
                ('gazed intensely', 'looked'),
                ('proclaimed', 'said'),
            ],
            'positive_emphasis': [
                ('good', 'excellent'),
                ('nice', 'wonderful'),
                ('happy', 'overjoyed'),
                ('glad', 'delighted'),
            ],
            'negative_emphasis': [
                ('bad', 'terrible'),
                ('sad', 'devastated'),
                ('angry', 'furious'),
                ('worried', 'terrified'),
            ]
        }

    def augment_dataset(self, documents: List[Dict[str, Any]],
                       config: AugmentationConfig) -> List[Dict[str, Any]]:
        """
        Augment a dataset using specified techniques.

        Args:
            documents: Original documents to augment
            config: Augmentation configuration

        Returns:
            Combined original and augmented documents
        """
        augmented_documents = []
        total_to_augment = int(len(documents) * config.augmentation_ratio)

        self.logger.info(f"Augmenting {total_to_augment} documents using {len(config.techniques)} techniques")

        # Select documents for augmentation
        docs_to_augment = random.sample(documents, min(total_to_augment, len(documents)))

        for doc in docs_to_augment:
            for technique in config.techniques:
                try:
                    augmented_doc = self._apply_augmentation_technique(doc, technique, config)

                    if augmented_doc:
                        # Add augmentation metadata
                        if 'metadata' not in augmented_doc:
                            augmented_doc['metadata'] = {}

                        augmented_doc['metadata']['augmentation'] = {
                            'technique': technique.value,
                            'source_document': doc['id'],
                            'augmented_id': f"{doc['id']}_aug_{technique.value}"
                        }

                        # Update document ID
                        augmented_doc['id'] = augmented_doc['metadata']['augmentation']['augmented_id']

                        augmented_documents.append(augmented_doc)

                except Exception as e:
                    self.logger.error(f"Error augmenting document {doc.get('id', 'unknown')} with {technique.value}: {str(e)}")

        self.logger.info(f"Generated {len(augmented_documents)} augmented documents")

        return documents + augmented_documents

    def _apply_augmentation_technique(self, document: Dict[str, Any],
                                    technique: AugmentationType,
                                    config: AugmentationConfig) -> Optional[Dict[str, Any]]:
        """Apply a specific augmentation technique to a document."""

        if technique == AugmentationType.PARAPHRASING:
            return self._paraphrase_document(document, config)
        elif technique == AugmentationType.STYLE_TRANSFER:
            return self._transfer_style(document, config)
        elif technique == AugmentationType.PERSPECTIVE_SHIFT:
            return self._shift_perspective(document, config)
        elif technique == AugmentationType.CONTENT_EXPANSION:
            return self._expand_content(document, config)
        elif technique == AugmentationType.TEMPORAL_SHIFT:
            return self._shift_temporal_perspective(document, config)
        elif technique == AugmentationType.GENRE_ADAPTATION:
            return self._adapt_genre(document, config)
        elif technique == AugmentationType.CHARACTER_FOCUS:
            return self._shift_character_focus(document, config)
        elif technique == AugmentationType.EMOTIONAL_TONE:
            return self._modify_emotional_tone(document, config)
        else:
            self.logger.warning(f"Unknown augmentation technique: {technique}")
            return None

    def _paraphrase_document(self, document: Dict[str, Any],
                           config: AugmentationConfig) -> Optional[Dict[str, Any]]:
        """Paraphrase document content while preserving meaning."""

        if not self.llm:
            return self._rule_based_paraphrasing(document, config)

        try:
            paraphrase_prompt = f"""Please paraphrase the following {document['type']} while maintaining its core meaning, narrative purpose, and factual content.

Original Title: {document.get('title', 'Untitled')}
Original Content: {document['content']}

Requirements:
1. Preserve all character names, locations, and key plot points
2. Maintain the document's original tone and style
3. Keep the same document type and structure
4. Ensure all facts and events remain consistent
5. Vary sentence structure and word choice without changing meaning

Provide the paraphrased version:"""

            # This would use the LLM to generate paraphrased content
            # For now, return rule-based paraphrasing
            return self._rule_based_paraphrasing(document, config)

        except Exception as e:
            self.logger.error(f"Error in LLM paraphrasing: {str(e)}")
            return self._rule_based_paraphrasing(document, config)

    def _rule_based_paraphrasing(self, document: Dict[str, Any],
                                config: AugmentationConfig) -> Dict[str, Any]:
        """Rule-based paraphrasing using synonym substitution and sentence restructuring."""

        content = document['content']

        # Extract entities to preserve
        entities = self._extract_entities(content) if config.preserve_entities else set()

        # Apply synonym substitutions
        paraphrased_content = self._apply_synonym_substitutions(content, entities)

        # Apply sentence restructuring
        paraphrased_content = self._restructure_sentences(paraphrased_content)

        # Create augmented document
        augmented_doc = document.copy()
        augmented_doc['content'] = paraphrased_content
        augmented_doc['title'] = f"{document.get('title', 'Untitled')} (Paraphrased)"

        return augmented_doc

    def _transfer_style(self, document: Dict[str, Any],
                       config: AugmentationConfig) -> Dict[str, Any]:
        """Transfer the document's style while preserving content."""

        content = document['content']
        doc_type = document['type']

        # Determine appropriate style transfer based on document type
        if doc_type in ['law', 'treaty']:
            # Formal to casual or vice versa
            transfer_type = random.choice(['formal_to_casual', 'casual_to_formal'])
        elif doc_type in ['diary', 'letter']:
            # Emotional tone modifications
            transfer_type = random.choice(['neutral_to_dramatic', 'dramatic_to_subtle'])
        else:
            # General style modifications
            transfer_type = random.choice(list(self.style_mappings.keys()))

        # Apply style transfer
        if transfer_type in self.style_mappings:
            patterns = self.style_mappings[transfer_type]['patterns']
            styled_content = content

            for old_pattern, new_pattern in patterns:
                styled_content = re.sub(old_pattern, new_pattern, styled_content, flags=re.IGNORECASE)

        else:
            styled_content = content

        # Create augmented document
        augmented_doc = document.copy()
        augmented_doc['content'] = styled_content
        augmented_doc['title'] = f"{document.get('title', 'Untitled')} ({transfer_type.replace('_', ' ').title()})"

        return augmented_doc

    def _shift_perspective(self, document: Dict[str, Any],
                          config: AugmentationConfig) -> Dict[str, Any]:
        """Shift the narrative perspective of the document."""

        content = document['content']
        doc_type = document['type']

        # Only apply perspective shift to appropriate document types
        if doc_type not in ['diary', 'letter', 'chronicle', 'report']:
            return document

        # Detect current perspective
        current_perspective = self._detect_perspective(content)

        # Apply perspective shift
        if current_perspective == 'first_person':
            shifted_content = self._convert_first_to_third_person(content)
            shift_description = "Third Person"
        elif current_perspective == 'third_person':
            shifted_content = self._convert_third_to_first_person(content)
            shift_description = "First Person"
        else:
            # For mixed or unclear perspectives, make minimal changes
            shifted_content = content
            shift_description = "Perspective Adjusted"

        # Create augmented document
        augmented_doc = document.copy()
        augmented_doc['content'] = shifted_content
        augmented_doc['title'] = f"{document.get('title', 'Untitled')} ({shift_description})"

        return augmented_doc

    def _expand_content(self, document: Dict[str, Any],
                       config: AugmentationConfig) -> Dict[str, Any]:
        """Expand document content with additional detail."""

        content = document['content']
        expansion_types = ['descriptive_detail', 'background_context', 'character_detail', 'sensory_detail']
        expansion_type = random.choice(expansion_types)

        # Apply expansion based on type
        if expansion_type == 'descriptive_detail':
            expanded_content = self._add_descriptive_detail(content)
        elif expansion_type == 'background_context':
            expanded_content = self._add_background_context(content)
        elif expansion_type == 'character_detail':
            expanded_content = self._add_character_detail(content)
        else:  # sensory_detail
            expanded_content = self._add_sensory_detail(content)

        # Ensure expansion doesn't exceed length limits
        original_length = len(content.split())
        expanded_length = len(expanded_content.split())
        length_ratio = expanded_length / original_length

        if length_ratio > (1 + config.max_length_change):
            # Truncate if expansion is too long
            target_length = int(original_length * (1 + config.max_length_change))
            words = expanded_content.split()
            expanded_content = ' '.join(words[:target_length])

        # Create augmented document
        augmented_doc = document.copy()
        augmented_doc['content'] = expanded_content
        augmented_doc['title'] = f"{document.get('title', 'Untitled')} (Expanded)"

        return augmented_doc

    def _shift_temporal_perspective(self, document: Dict[str, Any],
                                  config: AugmentationConfig) -> Dict[str, Any]:
        """Shift the temporal perspective of events in the document."""

        content = document['content']

        # Convert present tense to past tense or vice versa
        if self._is_primarily_present_tense(content):
            shifted_content = self._convert_present_to_past(content)
            shift_description = "Past Tense"
        else:
            shifted_content = self._convert_past_to_present(content)
            shift_description = "Present Tense"

        # Create augmented document
        augmented_doc = document.copy()
        augmented_doc['content'] = shifted_content
        augmented_doc['title'] = f"{document.get('title', 'Untitled')} ({shift_description})"

        return augmented_doc

    def _adapt_genre(self, document: Dict[str, Any],
                    config: AugmentationConfig) -> Dict[str, Any]:
        """Adapt document to a different genre style."""

        content = document['content']

        # Define genre adaptations
        genre_adaptations = {
            'fantasy_to_scifi': [
                ('magic', 'technology'),
                ('spell', 'program'),
                ('wizard', 'scientist'),
                ('kingdom', 'colony'),
                ('castle', 'station'),
            ],
            'medieval_to_modern': [
                ('horse', 'car'),
                ('sword', 'weapon'),
                ('messenger', 'phone'),
                ('scroll', 'document'),
                ('tavern', 'bar'),
            ],
            'formal_to_steampunk': [
                ('machine', 'contraption'),
                ('device', 'apparatus'),
                ('power', 'steam'),
                ('building', 'manufactory'),
            ]
        }

        # Select a genre adaptation
        adaptation_type = random.choice(list(genre_adaptations.keys()))
        adaptations = genre_adaptations[adaptation_type]

        adapted_content = content
        for old_term, new_term in adaptations:
            adapted_content = re.sub(r'\b' + re.escape(old_term) + r'\b', new_term,
                                   adapted_content, flags=re.IGNORECASE)

        # Create augmented document
        augmented_doc = document.copy()
        augmented_doc['content'] = adapted_content
        augmented_doc['title'] = f"{document.get('title', 'Untitled')} ({adaptation_type.replace('_', ' ').title()})"

        return augmented_doc

    def _shift_character_focus(self, document: Dict[str, Any],
                              config: AugmentationConfig) -> Dict[str, Any]:
        """Shift the focus to different characters in the narrative."""

        content = document['content']

        # Extract character names
        characters = self._extract_character_names(content)

        if len(characters) < 2:
            return document  # Need at least 2 characters to shift focus

        # Find primary character (most mentioned)
        char_counts = {}
        for char in characters:
            char_counts[char] = content.lower().count(char.lower())

        primary_char = max(char_counts, key=char_counts.get)
        other_chars = [c for c in characters if c != primary_char]
        new_focus_char = random.choice(other_chars)

        # Shift focus by emphasizing the new character
        focused_content = self._emphasize_character(content, new_focus_char, primary_char)

        # Create augmented document
        augmented_doc = document.copy()
        augmented_doc['content'] = focused_content
        augmented_doc['title'] = f"{document.get('title', 'Untitled')} (Focus: {new_focus_char})"

        return augmented_doc

    def _modify_emotional_tone(self, document: Dict[str, Any],
                              config: AugmentationConfig) -> Dict[str, Any]:
        """Modify the emotional tone of the document."""

        content = document['content']
        doc_type = document['type']

        # Select appropriate emotional modification based on document type
        if doc_type in ['diary', 'letter']:
            tone_modifications = ['positive_emphasis', 'negative_emphasis', 'neutral_to_dramatic', 'dramatic_to_subtle']
        else:
            tone_modifications = ['neutral_to_dramatic', 'dramatic_to_subtle']

        tone_modification = random.choice(tone_modifications)

        # Apply emotional tone modification
        if tone_modification in self.emotional_modifiers:
            modified_content = content
            for old_word, new_word in self.emotional_modifiers[tone_modification]:
                modified_content = re.sub(r'\b' + re.escape(old_word) + r'\b', new_word,
                                        modified_content, flags=re.IGNORECASE)
        else:
            modified_content = content

        # Create augmented document
        augmented_doc = document.copy()
        augmented_doc['content'] = modified_content
        augmented_doc['title'] = f"{document.get('title', 'Untitled')} ({tone_modification.replace('_', ' ').title()})"

        return augmented_doc

    # Helper methods for content analysis and transformation

    def _extract_entities(self, content: str) -> Set[str]:
        """Extract entity names to preserve during augmentation."""
        # Simple entity extraction - capitalized words
        entities = set(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content))
        return entities

    def _apply_synonym_substitutions(self, content: str, preserve_entities: Set[str]) -> str:
        """Apply synonym substitutions while preserving entities."""

        # Basic synonym dictionary
        synonyms = {
            'said': ['stated', 'mentioned', 'declared', 'remarked'],
            'went': ['traveled', 'moved', 'proceeded', 'journeyed'],
            'looked': ['gazed', 'glanced', 'observed', 'peered'],
            'big': ['large', 'huge', 'enormous', 'massive'],
            'small': ['tiny', 'little', 'minute', 'compact'],
            'good': ['excellent', 'fine', 'great', 'wonderful'],
            'bad': ['poor', 'terrible', 'awful', 'dreadful'],
        }

        words = content.split()
        result_words = []

        for word in words:
            # Clean word for lookup
            clean_word = re.sub(r'[^\w]', '', word.lower())

            # Don't substitute if it's a preserved entity
            if any(entity.lower() in word.lower() for entity in preserve_entities):
                result_words.append(word)
            elif clean_word in synonyms and random.random() < 0.3:  # 30% chance of substitution
                synonym = random.choice(synonyms[clean_word])
                # Preserve original capitalization and punctuation
                if word[0].isupper():
                    synonym = synonym.capitalize()
                # Add back punctuation
                punctuation = re.findall(r'[^\w]', word)
                if punctuation:
                    synonym += ''.join(punctuation)
                result_words.append(synonym)
            else:
                result_words.append(word)

        return ' '.join(result_words)

    def _restructure_sentences(self, content: str) -> str:
        """Restructure sentences to vary syntax."""

        sentences = re.split(r'[.!?]+', content)
        restructured_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Simple restructuring: move prepositional phrases
            if random.random() < 0.2:  # 20% chance of restructuring
                restructured = self._move_prepositional_phrase(sentence)
                restructured_sentences.append(restructured)
            else:
                restructured_sentences.append(sentence)

        return '. '.join(restructured_sentences) + '.'

    def _move_prepositional_phrase(self, sentence: str) -> str:
        """Move prepositional phrases to create sentence variety."""

        # Look for prepositional phrases at the beginning or end
        prep_pattern = r'\b(in|on|at|by|for|with|from|to|of|about|under|over|through)\s+[^,.]+'

        prep_matches = list(re.finditer(prep_pattern, sentence, re.IGNORECASE))

        if prep_matches and random.random() < 0.5:
            match = random.choice(prep_matches)
            prep_phrase = match.group()

            # Remove the phrase and add it at a different position
            sentence_without_prep = sentence[:match.start()] + sentence[match.end():]

            # Add at beginning or end
            if match.start() == 0:  # Was at beginning, move to end
                return sentence_without_prep.strip() + ', ' + prep_phrase.lower()
            else:  # Move to beginning
                return prep_phrase.capitalize() + ', ' + sentence_without_prep.strip().lower()

        return sentence

    def _detect_perspective(self, content: str) -> str:
        """Detect the narrative perspective of the content."""

        first_person_indicators = len(re.findall(r'\b(I|me|my|mine|myself)\b', content, re.IGNORECASE))
        third_person_indicators = len(re.findall(r'\b(he|she|him|her|his|hers|they|them|their)\b', content, re.IGNORECASE))

        if first_person_indicators > third_person_indicators * 1.5:
            return 'first_person'
        elif third_person_indicators > first_person_indicators * 1.5:
            return 'third_person'
        else:
            return 'mixed'

    def _convert_first_to_third_person(self, content: str) -> str:
        """Convert first person narrative to third person."""

        # Simple pronoun substitutions
        conversions = [
            (r'\bI\b', 'they'),
            (r'\bme\b', 'them'),
            (r'\bmy\b', 'their'),
            (r'\bmine\b', 'theirs'),
            (r'\bmyself\b', 'themselves'),
        ]

        result = content
        for old_pattern, new_pattern in conversions:
            result = re.sub(old_pattern, new_pattern, result)

        return result

    def _convert_third_to_first_person(self, content: str) -> str:
        """Convert third person narrative to first person."""

        # This is more complex as we need to identify the main character
        # Simple implementation
        conversions = [
            (r'\bthey\b', 'I'),
            (r'\bthem\b', 'me'),
            (r'\btheir\b', 'my'),
            (r'\btheirs\b', 'mine'),
            (r'\bthemselves\b', 'myself'),
        ]

        result = content
        for old_pattern, new_pattern in conversions:
            result = re.sub(old_pattern, new_pattern, result)

        return result

    def _add_descriptive_detail(self, content: str) -> str:
        """Add descriptive detail to the content."""

        # Simple descriptive additions
        descriptive_additions = [
            ('walked', 'walked slowly through the shadows'),
            ('room', 'dimly lit room'),
            ('door', 'heavy wooden door'),
            ('voice', 'trembling voice'),
            ('eyes', 'piercing blue eyes'),
        ]

        result = content
        for simple_word, detailed_phrase in descriptive_additions:
            if simple_word in result and random.random() < 0.3:
                result = result.replace(simple_word, detailed_phrase, 1)

        return result

    def _add_background_context(self, content: str) -> str:
        """Add background context to the content."""

        sentences = content.split('. ')

        # Add context to some sentences
        enhanced_sentences = []
        for sentence in sentences:
            enhanced_sentences.append(sentence)

            # Occasionally add background context
            if random.random() < 0.2:
                context_additions = [
                    "This had been a long-standing tradition in the region.",
                    "The implications of this event would be felt for years to come.",
                    "Such occurrences were not uncommon in those days.",
                    "The local population had grown accustomed to such events.",
                ]
                enhanced_sentences.append(random.choice(context_additions))

        return '. '.join(enhanced_sentences)

    def _add_character_detail(self, content: str) -> str:
        """Add character detail to the content."""

        characters = self._extract_character_names(content)

        if not characters:
            return content

        result = content

        # Add character details
        for char in characters:
            if random.random() < 0.3:
                detail_templates = [
                    f"{char}, known for their unwavering determination,",
                    f"{char}, whose reputation preceded them,",
                    f"{char}, despite their youth,",
                    f"{char}, with years of experience,",
                ]

                # Replace first mention with detailed version
                char_pattern = r'\b' + re.escape(char) + r'\b'
                match = re.search(char_pattern, result)
                if match:
                    detail = random.choice(detail_templates)
                    result = result[:match.start()] + detail + result[match.start() + len(char):]
                    break  # Only modify first occurrence

        return result

    def _add_sensory_detail(self, content: str) -> str:
        """Add sensory detail to the content."""

        sensory_enhancements = {
            'sound': ['The sound echoed through the halls.', 'A distant murmur could be heard.'],
            'sight': ['The scene was illuminated by flickering torchlight.', 'Shadows danced on the walls.'],
            'smell': ['The air was thick with the scent of aged parchment.', 'A musty odor filled the space.'],
            'touch': ['The surface felt rough beneath their fingertips.', 'A chill ran through the air.'],
        }

        sentences = content.split('. ')
        enhanced_sentences = []

        for sentence in sentences:
            enhanced_sentences.append(sentence)

            # Occasionally add sensory detail
            if random.random() < 0.15:
                sense_type = random.choice(list(sensory_enhancements.keys()))
                sensory_detail = random.choice(sensory_enhancements[sense_type])
                enhanced_sentences.append(sensory_detail)

        return '. '.join(enhanced_sentences)

    def _extract_character_names(self, content: str) -> List[str]:
        """Extract character names from content."""

        # Find capitalized words that could be names
        potential_names = re.findall(r'\b[A-Z][a-z]+\b', content)

        # Filter out common words that aren't names
        common_words = {'The', 'This', 'That', 'When', 'Where', 'What', 'Who', 'How', 'And', 'But', 'Or'}
        names = [name for name in potential_names if name not in common_words]

        # Return unique names, sorted by frequency
        name_counts = {}
        for name in names:
            name_counts[name] = name_counts.get(name, 0) + 1

        return sorted(name_counts.keys(), key=lambda x: name_counts[x], reverse=True)

    def _emphasize_character(self, content: str, focus_char: str, original_focus: str) -> str:
        """Emphasize a specific character in the narrative."""

        # Add more mentions of the focus character
        sentences = content.split('. ')
        enhanced_sentences = []

        for sentence in sentences:
            enhanced_sentences.append(sentence)

            # If sentence mentions the focus character, occasionally add more detail
            if focus_char in sentence and random.random() < 0.3:
                emphasis_additions = [
                    f"{focus_char} paused, considering the implications.",
                    f"The decision weighed heavily on {focus_char}.",
                    f"{focus_char} had always been central to these events.",
                ]
                enhanced_sentences.append(random.choice(emphasis_additions))

        return '. '.join(enhanced_sentences)

    def _is_primarily_present_tense(self, content: str) -> bool:
        """Determine if content is primarily in present tense."""

        present_indicators = len(re.findall(r'\b(is|are|am|has|have|does|do)\b', content, re.IGNORECASE))
        past_indicators = len(re.findall(r'\b(was|were|had|did|went|came|said)\b', content, re.IGNORECASE))

        return present_indicators > past_indicators

    def _convert_present_to_past(self, content: str) -> str:
        """Convert present tense to past tense."""

        conversions = [
            (r'\bis\b', 'was'),
            (r'\bare\b', 'were'),
            (r'\bam\b', 'was'),
            (r'\bhas\b', 'had'),
            (r'\bhave\b', 'had'),
            (r'\bdoes\b', 'did'),
            (r'\bdo\b', 'did'),
        ]

        result = content
        for old_pattern, new_pattern in conversions:
            result = re.sub(old_pattern, new_pattern, result, flags=re.IGNORECASE)

        return result

    def _convert_past_to_present(self, content: str) -> str:
        """Convert past tense to present tense."""

        conversions = [
            (r'\bwas\b', 'is'),
            (r'\bwere\b', 'are'),
            (r'\bhad\b', 'has'),
            (r'\bdid\b', 'does'),
            (r'\bwent\b', 'goes'),
            (r'\bcame\b', 'comes'),
            (r'\bsaid\b', 'says'),
        ]

        result = content
        for old_pattern, new_pattern in conversions:
            result = re.sub(old_pattern, new_pattern, result, flags=re.IGNORECASE)

        return result

    def get_augmentation_stats(self, original_docs: List[Dict[str, Any]],
                             augmented_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about the augmentation process."""

        augmented_only = [doc for doc in augmented_docs if 'augmentation' in doc.get('metadata', {})]

        technique_counts = {}
        for doc in augmented_only:
            technique = doc['metadata']['augmentation']['technique']
            technique_counts[technique] = technique_counts.get(technique, 0) + 1

        return {
            'original_documents': len(original_docs),
            'augmented_documents': len(augmented_only),
            'total_documents': len(augmented_docs),
            'augmentation_ratio': len(augmented_only) / len(original_docs) if original_docs else 0,
            'techniques_used': technique_counts,
            'average_length_change': self._calculate_average_length_change(original_docs, augmented_only)
        }

    def _calculate_average_length_change(self, original_docs: List[Dict[str, Any]],
                                       augmented_docs: List[Dict[str, Any]]) -> float:
        """Calculate average length change from augmentation."""

        length_changes = []

        for aug_doc in augmented_docs:
            if 'augmentation' in aug_doc.get('metadata', {}):
                source_id = aug_doc['metadata']['augmentation']['source_document']

                # Find original document
                original_doc = next((doc for doc in original_docs if doc['id'] == source_id), None)

                if original_doc:
                    orig_length = len(original_doc['content'].split())
                    aug_length = len(aug_doc['content'].split())

                    if orig_length > 0:
                        length_change = (aug_length - orig_length) / orig_length
                        length_changes.append(length_change)

        return sum(length_changes) / len(length_changes) if length_changes else 0.0