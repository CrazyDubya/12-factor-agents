"""
AgentCoordinator - Orchestrates the multi-agent narrative system.

This coordinator manages the interaction between all agents, ensuring they
work together effectively to create coherent fictional worlds and documents.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import time

from .base_agent import BaseAgent, AgentResponse, NarrativeContext, AgentRole
from .world_builder import WorldBuilderAgent
from .character_designer import CharacterDesignerAgent
from .plot_weaver import PlotWeaverAgent
from .document_writer import DocumentWriterAgent
from .consistency_checker import ConsistencyCheckerAgent

logger = logging.getLogger(__name__)

@dataclass
class GenerationConfig:
    """Configuration for world generation pipeline."""

    # World building
    num_locations: int = 5
    world_aspects: List[str] = None

    # Character design
    num_characters: int = 5
    character_roles: List[str] = None
    generate_relationships: bool = True

    # Plot development
    num_plot_threads: int = 3
    plot_complexity: str = 'medium'
    event_density: str = 'medium'

    # Document generation
    num_documents: int = 10
    document_types: List[str] = None

    # Quality control
    consistency_checks: bool = True
    auto_resolve_issues: bool = True
    max_iterations: int = 3

    def __post_init__(self):
        if self.world_aspects is None:
            self.world_aspects = ['geography', 'politics', 'cultures', 'history']
        if self.character_roles is None:
            self.character_roles = ['protagonist', 'antagonist', 'supporting', 'supporting', 'minor']
        if self.document_types is None:
            self.document_types = ['chronicle', 'letter', 'diary', 'law', 'report']

class AgentCoordinator:
    """
    Coordinates the multi-agent narrative generation system.

    This class orchestrates the workflow between different agents to create
    coherent fictional worlds with interconnected documents.
    """

    def __init__(self, llm=None, max_workers: int = 4):
        """
        Initialize the agent coordinator.

        Args:
            llm: Language model to use for all agents
            max_workers: Maximum number of concurrent agent operations
        """
        self.llm = llm
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)

        # Initialize agents
        self.agents = {
            AgentRole.WORLD_BUILDER: WorldBuilderAgent(llm=llm),
            AgentRole.CHARACTER_DESIGNER: CharacterDesignerAgent(llm=llm),
            AgentRole.PLOT_WEAVER: PlotWeaverAgent(llm=llm),
            AgentRole.DOCUMENT_WRITER: DocumentWriterAgent(llm=llm),
            AgentRole.CONSISTENCY_CHECKER: ConsistencyCheckerAgent(llm=llm)
        }

        # Generation pipeline stages
        self.pipeline_stages = [
            'world_building',
            'character_design',
            'plot_development',
            'document_generation',
            'consistency_check'
        ]

    async def generate_world(self, theme: str, world_id: str = None,
                           config: GenerationConfig = None) -> Dict[str, Any]:
        """
        Generate a complete fictional world with documents.

        Args:
            theme: Theme or genre for the world
            world_id: Unique identifier for the world
            config: Generation configuration

        Returns:
            Complete world data with all generated elements
        """
        if world_id is None:
            world_id = f"world_{int(time.time())}"

        if config is None:
            config = GenerationConfig()

        # Initialize context
        context = NarrativeContext(world_id=world_id, theme=theme)

        # Track generation process
        generation_log = {
            'start_time': time.time(),
            'stages': {},
            'iterations': [],
            'final_stats': {}
        }

        try:
            self.logger.info(f"Starting world generation: {world_id} ({theme})")

            # Execute generation pipeline
            for iteration in range(config.max_iterations):
                self.logger.info(f"Generation iteration {iteration + 1}/{config.max_iterations}")

                iteration_log = await self._execute_generation_pipeline(context, config)
                generation_log['iterations'].append(iteration_log)

                # Check if we need another iteration
                if not await self._needs_iteration(context, iteration_log, config):
                    break

            # Final statistics and summary
            generation_log['final_stats'] = self._compile_final_stats(context)
            generation_log['end_time'] = time.time()
            generation_log['total_time'] = generation_log['end_time'] - generation_log['start_time']

            self.logger.info(f"Completed world generation in {generation_log['total_time']:.2f} seconds")

            return {
                'world_id': world_id,
                'context': context,
                'generation_log': generation_log,
                'success': True
            }

        except Exception as e:
            self.logger.error(f"World generation failed: {str(e)}")
            generation_log['error'] = str(e)
            generation_log['end_time'] = time.time()

            return {
                'world_id': world_id,
                'context': context,
                'generation_log': generation_log,
                'success': False,
                'error': str(e)
            }

    async def _execute_generation_pipeline(self, context: NarrativeContext,
                                         config: GenerationConfig) -> Dict[str, Any]:
        """Execute a single iteration of the generation pipeline."""

        iteration_log = {
            'stages': {},
            'start_time': time.time()
        }

        # Stage 1: World Building (if not already complete)
        if not context.locations or len(context.locations) < config.num_locations:
            iteration_log['stages']['world_building'] = await self._execute_world_building(context, config)

        # Stage 2: Character Design (if not already complete)
        if not context.characters or len(context.characters) < config.num_characters:
            iteration_log['stages']['character_design'] = await self._execute_character_design(context, config)

        # Stage 3: Plot Development
        iteration_log['stages']['plot_development'] = await self._execute_plot_development(context, config)

        # Stage 4: Document Generation
        iteration_log['stages']['document_generation'] = await self._execute_document_generation(context, config)

        # Stage 5: Consistency Check (if enabled)
        if config.consistency_checks:
            iteration_log['stages']['consistency_check'] = await self._execute_consistency_check(context, config)

        iteration_log['end_time'] = time.time()
        iteration_log['duration'] = iteration_log['end_time'] - iteration_log['start_time']

        return iteration_log

    async def _execute_world_building(self, context: NarrativeContext,
                                    config: GenerationConfig) -> Dict[str, Any]:
        """Execute world building stage."""

        self.logger.info("Executing world building stage")

        agent = self.agents[AgentRole.WORLD_BUILDER]
        response = agent.execute_with_retry(
            context,
            num_locations=config.num_locations,
            aspects=config.world_aspects
        )

        if response.success:
            self.logger.info(f"World building completed: {response.metadata}")
        else:
            self.logger.error(f"World building failed: {response.error_message}")

        return {
            'success': response.success,
            'metadata': response.metadata,
            'error': response.error_message,
            'execution_time': response.execution_time
        }

    async def _execute_character_design(self, context: NarrativeContext,
                                      config: GenerationConfig) -> Dict[str, Any]:
        """Execute character design stage."""

        self.logger.info("Executing character design stage")

        agent = self.agents[AgentRole.CHARACTER_DESIGNER]
        response = agent.execute_with_retry(
            context,
            num_characters=config.num_characters,
            character_roles=config.character_roles,
            generate_relationships=config.generate_relationships
        )

        if response.success:
            self.logger.info(f"Character design completed: {response.metadata}")
        else:
            self.logger.error(f"Character design failed: {response.error_message}")

        return {
            'success': response.success,
            'metadata': response.metadata,
            'error': response.error_message,
            'execution_time': response.execution_time
        }

    async def _execute_plot_development(self, context: NarrativeContext,
                                      config: GenerationConfig) -> Dict[str, Any]:
        """Execute plot development stage."""

        self.logger.info("Executing plot development stage")

        agent = self.agents[AgentRole.PLOT_WEAVER]
        response = agent.execute_with_retry(
            context,
            narrative_goals='create engaging interconnected stories',
            plot_complexity=config.plot_complexity,
            event_density=config.event_density
        )

        if response.success:
            self.logger.info(f"Plot development completed: {response.metadata}")
        else:
            self.logger.error(f"Plot development failed: {response.error_message}")

        return {
            'success': response.success,
            'metadata': response.metadata,
            'error': response.error_message,
            'execution_time': response.execution_time
        }

    async def _execute_document_generation(self, context: NarrativeContext,
                                         config: GenerationConfig) -> Dict[str, Any]:
        """Execute document generation stage."""

        self.logger.info("Executing document generation stage")

        agent = self.agents[AgentRole.DOCUMENT_WRITER]

        # Calculate documents needed for this iteration
        current_docs = len(context.generated_documents)
        docs_needed = max(0, config.num_documents - current_docs)

        if docs_needed == 0:
            return {
                'success': True,
                'metadata': {'message': 'Sufficient documents already generated'},
                'error': None,
                'execution_time': 0
            }

        response = agent.execute_with_retry(
            context,
            document_types=config.document_types,
            num_documents=min(docs_needed, 5),  # Limit per iteration
            specific_purpose='advance the narrative and world development'
        )

        if response.success:
            self.logger.info(f"Document generation completed: {response.metadata}")
        else:
            self.logger.error(f"Document generation failed: {response.error_message}")

        return {
            'success': response.success,
            'metadata': response.metadata,
            'error': response.error_message,
            'execution_time': response.execution_time
        }

    async def _execute_consistency_check(self, context: NarrativeContext,
                                       config: GenerationConfig) -> Dict[str, Any]:
        """Execute consistency check stage."""

        self.logger.info("Executing consistency check stage")

        agent = self.agents[AgentRole.CONSISTENCY_CHECKER]
        response = agent.execute_with_retry(
            context,
            severity_threshold='minor',
            auto_resolve=config.auto_resolve_issues
        )

        if response.success:
            consistency_score = response.content.get('consistency_score', 0)
            issues_count = response.metadata.get('total_issues', 0)
            self.logger.info(f"Consistency check completed: score={consistency_score}, issues={issues_count}")
        else:
            self.logger.error(f"Consistency check failed: {response.error_message}")

        return {
            'success': response.success,
            'metadata': response.metadata,
            'error': response.error_message,
            'execution_time': response.execution_time,
            'consistency_score': response.content.get('consistency_score', 0) if response.success else 0
        }

    async def _needs_iteration(self, context: NarrativeContext, iteration_log: Dict[str, Any],
                             config: GenerationConfig) -> bool:
        """Determine if another iteration is needed."""

        # Check if we've reached target counts
        docs_needed = config.num_documents - len(context.generated_documents)
        if docs_needed > 0:
            return True

        # Check consistency score if available
        consistency_stage = iteration_log['stages'].get('consistency_check')
        if consistency_stage and consistency_stage['success']:
            consistency_score = consistency_stage.get('consistency_score', 1.0)
            if consistency_score < 0.8:  # Below acceptable threshold
                return True

        # Check for failed stages
        failed_stages = [stage for stage, result in iteration_log['stages'].items()
                        if not result['success']]
        if failed_stages:
            self.logger.warning(f"Failed stages detected: {failed_stages}")
            return True

        return False

    def _compile_final_stats(self, context: NarrativeContext) -> Dict[str, Any]:
        """Compile final statistics for the generated world."""

        return {
            'world_elements': {
                'locations': len(context.locations),
                'characters': len(context.characters),
                'plot_threads': len(context.active_plots),
                'documents': len(context.generated_documents)
            },
            'document_breakdown': self._analyze_document_types(context),
            'character_involvement': self._analyze_character_involvement(context),
            'plot_coverage': self._analyze_plot_coverage(context)
        }

    def _analyze_document_types(self, context: NarrativeContext) -> Dict[str, int]:
        """Analyze the distribution of document types."""
        type_counts = {}
        for doc in context.generated_documents:
            doc_type = doc['type']
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        return type_counts

    def _analyze_character_involvement(self, context: NarrativeContext) -> Dict[str, int]:
        """Analyze character involvement across documents."""
        involvement = {}

        for char in context.characters:
            char_name = char['name']
            mentions = 0

            for doc in context.generated_documents:
                if char_name.lower() in doc['content'].lower():
                    mentions += 1

            involvement[char_name] = mentions

        return involvement

    def _analyze_plot_coverage(self, context: NarrativeContext) -> Dict[str, Any]:
        """Analyze plot thread coverage in documents."""
        total_plots = len(context.active_plots)
        active_plots = len([p for p in context.active_plots if p.get('status') == 'active'])

        return {
            'total_plot_threads': total_plots,
            'active_plot_threads': active_plots,
            'plot_coverage_ratio': active_plots / max(total_plots, 1)
        }

    async def generate_additional_documents(self, context: NarrativeContext,
                                          document_types: List[str],
                                          count: int = 5) -> AgentResponse:
        """Generate additional documents for an existing world."""

        agent = self.agents[AgentRole.DOCUMENT_WRITER]
        return agent.execute_with_retry(
            context,
            document_types=document_types,
            num_documents=count,
            specific_purpose='expand the existing world and narrative'
        )

    async def check_world_consistency(self, context: NarrativeContext) -> AgentResponse:
        """Run consistency checks on an existing world."""

        agent = self.agents[AgentRole.CONSISTENCY_CHECKER]
        return agent.execute_with_retry(
            context,
            severity_threshold='minor',
            auto_resolve=False
        )

    def get_world_summary(self, context: NarrativeContext) -> str:
        """Get a comprehensive summary of a generated world."""

        return f"""
World Summary: {context.world_id}
Theme: {context.theme}

World Elements:
- Locations: {len(context.locations)}
- Characters: {len(context.characters)}
- Active Plots: {len([p for p in context.active_plots if p.get('status') == 'active'])}
- Generated Documents: {len(context.generated_documents)}

Document Types: {', '.join(set(doc['type'] for doc in context.generated_documents))}

Key Characters: {', '.join([char['name'] for char in context.characters[:5]])}

Key Locations: {', '.join([loc['name'] for loc in context.locations[:5]])}
"""

    def export_world_data(self, context: NarrativeContext) -> Dict[str, Any]:
        """Export complete world data for external use."""

        return {
            'world_id': context.world_id,
            'theme': context.theme,
            'world_rules': context.world_rules,
            'characters': context.characters,
            'locations': context.locations,
            'active_plots': context.active_plots,
            'generated_documents': context.generated_documents,
            'consistency_rules': context.consistency_rules,
            'export_timestamp': time.time()
        }