"""
SyntheticDataGenerator - Main pipeline for generating coherent training datasets.

This class orchestrates the entire synthetic data generation process, combining
multi-agent narrative generation with quality control and consistency validation.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import random

from ..agents import AgentCoordinator
from ..agents.base_agent import NarrativeContext
from ..knowledge_graph import KnowledgeGraphManager, EntityTracker, ConsistencyValidator
from .quality_control import QualityController, QualityMetrics
from .prompt_templates import PromptTemplateManager

logger = logging.getLogger(__name__)

@dataclass
class DatasetConfig:
    """Configuration for synthetic dataset generation."""

    # Dataset parameters
    num_worlds: int = 10
    documents_per_world: int = 50
    min_document_length: int = 500
    max_document_length: int = 5000

    # Content diversity
    themes: List[str] = None
    document_types: List[str] = None
    complexity_levels: List[str] = None

    # Quality thresholds
    min_consistency_score: float = 0.8
    min_coherence_score: float = 0.75
    max_contradiction_rate: float = 0.1

    # Training format
    output_format: str = 'jsonl'  # 'jsonl', 'json', 'txt'
    include_metadata: bool = True
    include_world_context: bool = True

    # Performance settings
    batch_size: int = 5
    max_retries: int = 3
    quality_checks_enabled: bool = True

    def __post_init__(self):
        if self.themes is None:
            self.themes = [
                'medieval fantasy kingdom',
                'space exploration colony',
                'steampunk industrial revolution',
                'post-apocalyptic survival',
                'magical school academy',
                'pirate adventure',
                'cyberpunk dystopia',
                'ancient civilization',
                'wild west frontier',
                'underwater civilization'
            ]

        if self.document_types is None:
            self.document_types = [
                'chronicle', 'diary', 'letter', 'law', 'treaty',
                'report', 'map', 'inventory', 'song', 'newspaper'
            ]

        if self.complexity_levels is None:
            self.complexity_levels = ['low', 'medium', 'high']

@dataclass
class GenerationStats:
    """Statistics for a data generation run."""
    start_time: float
    end_time: float
    worlds_generated: int
    documents_generated: int
    quality_filtered: int
    consistency_issues: int
    average_document_length: float
    generation_rate: float  # documents per second

class SyntheticDataGenerator:
    """
    Main synthetic data generation pipeline.

    This class coordinates multi-agent generation, quality control, and
    consistency validation to produce high-quality training datasets.
    """

    def __init__(self, llm=None, neo4j_config: Dict[str, str] = None):
        """
        Initialize the synthetic data generator.

        Args:
            llm: Language model for generation
            neo4j_config: Neo4j connection configuration
        """
        self.llm = llm
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.agent_coordinator = AgentCoordinator(llm=llm)
        self.quality_controller = QualityController()
        self.prompt_template_manager = PromptTemplateManager()

        # Knowledge graph components (optional)
        self.knowledge_graph = None
        self.entity_tracker = EntityTracker()
        self.consistency_validator = ConsistencyValidator(self.entity_tracker)

        if neo4j_config:
            try:
                self.knowledge_graph = KnowledgeGraphManager(**neo4j_config)
                if self.knowledge_graph.connect():
                    self.logger.info("Connected to Neo4j knowledge graph")
                else:
                    self.logger.warning("Failed to connect to Neo4j, running without knowledge graph")
                    self.knowledge_graph = None
            except Exception as e:
                self.logger.warning(f"Knowledge graph initialization failed: {str(e)}")
                self.knowledge_graph = None

    async def generate_dataset(self, config: DatasetConfig,
                             output_path: Path) -> GenerationStats:
        """
        Generate a complete synthetic dataset.

        Args:
            config: Configuration for dataset generation
            output_path: Path to save the generated dataset

        Returns:
            Statistics about the generation process
        """
        start_time = time.time()

        self.logger.info(f"Starting dataset generation with {config.num_worlds} worlds")
        self.logger.info(f"Target: {config.documents_per_world} documents per world")

        # Initialize generation statistics
        stats = GenerationStats(
            start_time=start_time,
            end_time=0,
            worlds_generated=0,
            documents_generated=0,
            quality_filtered=0,
            consistency_issues=0,
            average_document_length=0,
            generation_rate=0
        )

        generated_data = []

        try:
            # Generate worlds in batches
            for batch_start in range(0, config.num_worlds, config.batch_size):
                batch_end = min(batch_start + config.batch_size, config.num_worlds)
                batch_size = batch_end - batch_start

                self.logger.info(f"Generating batch {batch_start//config.batch_size + 1}: worlds {batch_start+1}-{batch_end}")

                # Generate worlds concurrently within batch
                batch_tasks = []
                for world_idx in range(batch_start, batch_end):
                    theme = random.choice(config.themes)
                    complexity = random.choice(config.complexity_levels)

                    task = self._generate_world_data(
                        world_id=f"world_{world_idx:04d}",
                        theme=theme,
                        config=config,
                        complexity=complexity
                    )
                    batch_tasks.append(task)

                # Wait for batch completion
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

                # Process batch results
                for result in batch_results:
                    if isinstance(result, Exception):
                        self.logger.error(f"World generation failed: {str(result)}")
                        continue

                    if result and result['success']:
                        world_data = result['data']

                        # Apply quality control
                        filtered_data = await self._apply_quality_control(world_data, config)

                        if filtered_data:
                            generated_data.extend(filtered_data)
                            stats.worlds_generated += 1
                            stats.documents_generated += len(filtered_data)

                        # Update quality stats
                        stats.quality_filtered += len(world_data) - len(filtered_data) if filtered_data else len(world_data)

                # Progress update
                self.logger.info(f"Batch complete: {stats.worlds_generated}/{config.num_worlds} worlds, {stats.documents_generated} documents")

        except Exception as e:
            self.logger.error(f"Dataset generation failed: {str(e)}")
            raise

        # Save dataset
        await self._save_dataset(generated_data, output_path, config)

        # Calculate final statistics
        end_time = time.time()
        stats.end_time = end_time

        if stats.documents_generated > 0:
            total_length = sum(len(doc['content']) for doc in generated_data)
            stats.average_document_length = total_length / stats.documents_generated

        generation_time = end_time - start_time
        stats.generation_rate = stats.documents_generated / generation_time if generation_time > 0 else 0

        self.logger.info(f"Dataset generation complete!")
        self.logger.info(f"Generated {stats.documents_generated} documents in {generation_time:.2f} seconds")
        self.logger.info(f"Generation rate: {stats.generation_rate:.2f} documents/second")

        return stats

    async def _generate_world_data(self, world_id: str, theme: str,
                                 config: DatasetConfig, complexity: str) -> Dict[str, Any]:
        """Generate all data for a single world."""

        try:
            self.logger.info(f"Generating world: {world_id} ({theme})")

            # Set up generation configuration
            gen_config = GenerationConfig(
                num_locations=self._get_location_count(complexity),
                num_characters=self._get_character_count(complexity),
                num_documents=config.documents_per_world,
                document_types=config.document_types,
                plot_complexity=complexity,
                consistency_checks=config.quality_checks_enabled
            )

            # Generate world using agent coordinator
            world_result = await self.agent_coordinator.generate_world(
                theme=theme,
                world_id=world_id,
                config=gen_config
            )

            if not world_result['success']:
                self.logger.error(f"Failed to generate world {world_id}: {world_result.get('error', 'unknown error')}")
                return {'success': False, 'error': world_result.get('error')}

            # Extract generated documents
            context = world_result['context']
            documents = []

            for doc in context.generated_documents:
                # Format document for training
                training_doc = self._format_document_for_training(doc, context, config)
                if training_doc:
                    documents.append(training_doc)

            # Store in knowledge graph if available
            if self.knowledge_graph:
                await self._store_world_in_kg(world_id, context)

            return {
                'success': True,
                'data': documents,
                'world_context': context,
                'generation_log': world_result['generation_log']
            }

        except Exception as e:
            self.logger.error(f"Error generating world {world_id}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _format_document_for_training(self, document: Dict[str, Any],
                                    context: NarrativeContext,
                                    config: DatasetConfig) -> Optional[Dict[str, Any]]:
        """Format a document for training data."""

        try:
            # Basic document data
            training_doc = {
                'id': document['id'],
                'type': document['type'],
                'title': document['title'],
                'content': document['content'],
                'author': document.get('author', ''),
                'word_count': len(document['content'].split())
            }

            # Add world context if requested
            if config.include_world_context:
                training_doc['world_context'] = {
                    'world_id': context.world_id,
                    'theme': context.theme,
                    'characters': [{'name': c['name'], 'role': c['role']} for c in context.characters[:10]],
                    'locations': [{'name': l['name'], 'type': l['type']} for l in context.locations[:10]]
                }

            # Add metadata if requested
            if config.include_metadata:
                training_doc['metadata'] = {
                    'generation_time': document.get('metadata', {}).get('generated_at'),
                    'consistency_score': getattr(document, 'consistency_score', 1.0),
                    'document_order': document.get('metadata', {}).get('creation_order', 0)
                }

            # Validate document length
            word_count = training_doc['word_count']
            if word_count < config.min_document_length or word_count > config.max_document_length:
                self.logger.debug(f"Document {document['id']} filtered by length: {word_count} words")
                return None

            return training_doc

        except Exception as e:
            self.logger.error(f"Error formatting document {document.get('id', 'unknown')}: {str(e)}")
            return None

    async def _apply_quality_control(self, documents: List[Dict[str, Any]],
                                   config: DatasetConfig) -> List[Dict[str, Any]]:
        """Apply quality control filters to generated documents."""

        if not config.quality_checks_enabled:
            return documents

        filtered_documents = []

        for doc in documents:
            try:
                # Calculate quality metrics
                metrics = self.quality_controller.evaluate_document(doc)

                # Apply quality thresholds
                if (metrics.coherence_score >= config.min_coherence_score and
                    metrics.consistency_score >= config.min_consistency_score and
                    metrics.contradiction_rate <= config.max_contradiction_rate):

                    # Add quality scores to document
                    if config.include_metadata:
                        doc['metadata']['quality_scores'] = asdict(metrics)

                    filtered_documents.append(doc)
                else:
                    self.logger.debug(f"Document {doc['id']} filtered by quality: "
                                    f"coherence={metrics.coherence_score:.2f}, "
                                    f"consistency={metrics.consistency_score:.2f}")

            except Exception as e:
                self.logger.error(f"Error in quality control for document {doc.get('id', 'unknown')}: {str(e)}")
                # Include document without quality scores if evaluation fails
                filtered_documents.append(doc)

        return filtered_documents

    async def _store_world_in_kg(self, world_id: str, context: NarrativeContext):
        """Store world data in the knowledge graph."""

        if not self.knowledge_graph:
            return

        try:
            # Create world node
            self.knowledge_graph.create_world(
                world_id=world_id,
                theme=context.theme,
                properties={'total_documents': len(context.generated_documents)}
            )

            # Add characters
            for character in context.characters:
                self.knowledge_graph.create_character(world_id, character)

            # Add locations
            for location in context.locations:
                self.knowledge_graph.create_location(world_id, location)

            # Add documents
            for document in context.generated_documents:
                self.knowledge_graph.create_document(world_id, document)

            self.logger.debug(f"Stored world {world_id} in knowledge graph")

        except Exception as e:
            self.logger.error(f"Error storing world {world_id} in knowledge graph: {str(e)}")

    async def _save_dataset(self, data: List[Dict[str, Any]],
                          output_path: Path, config: DatasetConfig):
        """Save the generated dataset to disk."""

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if config.output_format == 'jsonl':
                # JSONL format - one JSON object per line
                with open(output_path, 'w', encoding='utf-8') as f:
                    for doc in data:
                        f.write(json.dumps(doc, ensure_ascii=False) + '\n')

            elif config.output_format == 'json':
                # JSON format - single JSON array
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

            elif config.output_format == 'txt':
                # Plain text format - just document content
                with open(output_path, 'w', encoding='utf-8') as f:
                    for doc in data:
                        f.write(f"=== {doc['title']} ===\n")
                        f.write(f"Type: {doc['type']}\n")
                        f.write(f"Author: {doc['author']}\n\n")
                        f.write(doc['content'])
                        f.write('\n\n' + '='*50 + '\n\n')

            self.logger.info(f"Saved {len(data)} documents to {output_path}")

        except Exception as e:
            self.logger.error(f"Error saving dataset to {output_path}: {str(e)}")
            raise

    def _get_location_count(self, complexity: str) -> int:
        """Get number of locations based on complexity level."""
        complexity_map = {'low': 3, 'medium': 5, 'high': 8}
        return complexity_map.get(complexity, 5)

    def _get_character_count(self, complexity: str) -> int:
        """Get number of characters based on complexity level."""
        complexity_map = {'low': 3, 'medium': 5, 'high': 8}
        return complexity_map.get(complexity, 5)

    async def generate_world_samples(self, themes: List[str],
                                   output_dir: Path,
                                   samples_per_theme: int = 3) -> Dict[str, Any]:
        """
        Generate sample worlds for each theme for evaluation purposes.

        Args:
            themes: List of themes to generate samples for
            output_dir: Directory to save samples
            samples_per_theme: Number of sample worlds per theme

        Returns:
            Dictionary with generation results and statistics
        """

        self.logger.info(f"Generating samples: {len(themes)} themes, {samples_per_theme} samples each")

        output_dir.mkdir(parents=True, exist_ok=True)
        results = {'themes': {}, 'total_samples': 0, 'successful_samples': 0}

        for theme in themes:
            theme_results = []
            theme_dir = output_dir / theme.replace(' ', '_')
            theme_dir.mkdir(exist_ok=True)

            for sample_idx in range(samples_per_theme):
                world_id = f"sample_{theme.replace(' ', '_')}_{sample_idx}"

                try:
                    # Generate small sample world
                    config = GenerationConfig(
                        num_locations=3,
                        num_characters=3,
                        num_documents=5,
                        document_types=['chronicle', 'diary', 'letter']
                    )

                    world_result = await self.agent_coordinator.generate_world(
                        theme=theme,
                        world_id=world_id,
                        config=config
                    )

                    if world_result['success']:
                        # Save sample
                        sample_path = theme_dir / f"sample_{sample_idx}.json"
                        with open(sample_path, 'w', encoding='utf-8') as f:
                            json.dump({
                                'world_id': world_id,
                                'theme': theme,
                                'context': world_result['context'].__dict__,
                                'generation_log': world_result['generation_log']
                            }, f, ensure_ascii=False, indent=2, default=str)

                        theme_results.append({'success': True, 'path': str(sample_path)})
                        results['successful_samples'] += 1
                    else:
                        theme_results.append({'success': False, 'error': world_result.get('error')})

                except Exception as e:
                    theme_results.append({'success': False, 'error': str(e)})

                results['total_samples'] += 1

            results['themes'][theme] = {
                'samples': theme_results,
                'success_rate': sum(1 for r in theme_results if r['success']) / len(theme_results)
            }

            self.logger.info(f"Theme '{theme}' complete: {len([r for r in theme_results if r['success']])}/{samples_per_theme} successful")

        # Save summary
        summary_path = output_dir / 'generation_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        self.logger.info(f"Sample generation complete: {results['successful_samples']}/{results['total_samples']} successful")

        return results

    def get_generation_statistics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get detailed statistics about generated data."""

        if not data:
            return {'error': 'No data provided'}

        # Basic statistics
        total_docs = len(data)
        total_words = sum(doc['word_count'] for doc in data)
        avg_length = total_words / total_docs

        # Document type distribution
        doc_types = {}
        for doc in data:
            doc_type = doc['type']
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1

        # World distribution
        worlds = set()
        for doc in data:
            if 'world_context' in doc:
                worlds.add(doc['world_context']['world_id'])

        # Theme distribution
        themes = {}
        for doc in data:
            if 'world_context' in doc:
                theme = doc['world_context']['theme']
                themes[theme] = themes.get(theme, 0) + 1

        return {
            'dataset_overview': {
                'total_documents': total_docs,
                'total_words': total_words,
                'average_document_length': round(avg_length, 2),
                'unique_worlds': len(worlds)
            },
            'content_distribution': {
                'document_types': doc_types,
                'themes': themes
            },
            'quality_metrics': self._calculate_dataset_quality_metrics(data)
        }

    def _calculate_dataset_quality_metrics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate quality metrics for the entire dataset."""

        quality_docs = [doc for doc in data if 'metadata' in doc and 'quality_scores' in doc['metadata']]

        if not quality_docs:
            return {'error': 'No quality scores available'}

        total_docs = len(quality_docs)

        # Average quality scores
        avg_coherence = sum(doc['metadata']['quality_scores']['coherence_score'] for doc in quality_docs) / total_docs
        avg_consistency = sum(doc['metadata']['quality_scores']['consistency_score'] for doc in quality_docs) / total_docs
        avg_contradiction_rate = sum(doc['metadata']['quality_scores']['contradiction_rate'] for doc in quality_docs) / total_docs

        return {
            'documents_with_scores': total_docs,
            'average_coherence_score': round(avg_coherence, 3),
            'average_consistency_score': round(avg_consistency, 3),
            'average_contradiction_rate': round(avg_contradiction_rate, 3)
        }