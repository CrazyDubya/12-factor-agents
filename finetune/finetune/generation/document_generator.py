"""
Document Generator with Narrative Coherence

High-level document generation system that produces coherent narratives
using trained models with real-time coherence validation.
"""

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import torch
from peft import PeftModel
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    GenerationConfig as HFGenerationConfig,
    TextIteratorStreamer,
)
from threading import Thread

from ..config import SUPPORTED_MODELS
from ..knowledge_graph import KnowledgeGraphManager, EntityTracker, ConsistencyValidator
from .coherence_validator import CoherenceValidator
from .output_formatter import OutputFormatter, DocumentFormat


@dataclass
class GenerationConfig:
    """Configuration for document generation."""

    # Generation parameters
    max_new_tokens: int = 512
    temperature: float = 0.8
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.1
    do_sample: bool = True
    num_return_sequences: int = 1

    # Narrative coherence parameters
    coherence_threshold: float = 0.6
    validate_coherence: bool = True
    use_knowledge_graph: bool = True
    max_context_length: int = 1024

    # Cross-document consistency
    maintain_character_consistency: bool = True
    maintain_timeline_consistency: bool = True
    maintain_world_consistency: bool = True

    # Output formatting
    output_format: DocumentFormat = DocumentFormat.STRUCTURED
    include_metadata: bool = True
    validate_output: bool = True

    # Advanced options
    use_streaming: bool = False
    batch_generation: bool = False
    seed: Optional[int] = None


class DocumentGenerator:
    """
    Advanced document generator with narrative coherence validation.

    Features:
    - Multi-document narrative consistency
    - Real-time coherence validation
    - Knowledge graph integration
    - Streaming generation support
    - Batch generation capabilities
    """

    def __init__(
        self,
        model_path: Union[str, Path],
        config: GenerationConfig = None,
        device: str = "auto",
        load_in_4bit: bool = False,
    ):
        self.model_path = Path(model_path)
        self.config = config or GenerationConfig()
        self.device = device
        self.load_in_4bit = load_in_4bit

        # Components
        self.model = None
        self.tokenizer = None
        self.coherence_validator = None
        self.output_formatter = None
        self.knowledge_graph = None

        # Generation state
        self.generation_history = []
        self.current_world_context = {}

        self._load_model_and_components()

    def _load_model_and_components(self):
        """Load model, tokenizer, and supporting components."""
        logging.info(f"Loading model from: {self.model_path}")

        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                str(self.model_path),
                trust_remote_code=True,
                padding_side="left",  # For batch generation
            )

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Load model
            model_kwargs = {
                "trust_remote_code": True,
                "torch_dtype": torch.bfloat16,
                "device_map": "auto" if self.device == "auto" else None,
            }

            if self.load_in_4bit:
                from transformers import BitsAndBytesConfig
                model_kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.bfloat16,
                    bnb_4bit_use_double_quant=True,
                )

            # Try to load as PEFT model first
            try:
                base_model = AutoModelForCausalLM.from_pretrained(
                    str(self.model_path),
                    **model_kwargs
                )
                # Check if this is a PEFT checkpoint
                if (self.model_path / "adapter_config.json").exists():
                    self.model = PeftModel.from_pretrained(base_model, str(self.model_path))
                else:
                    self.model = base_model
            except Exception as e:
                logging.warning(f"Failed to load as PEFT model, loading as base model: {e}")
                self.model = AutoModelForCausalLM.from_pretrained(
                    str(self.model_path),
                    **model_kwargs
                )

            self.model.eval()

            # Initialize supporting components
            if self.config.validate_coherence:
                self.coherence_validator = CoherenceValidator()

            self.output_formatter = OutputFormatter()

            if self.config.use_knowledge_graph:
                self.knowledge_graph = KnowledgeGraphManager()

            logging.info("Model and components loaded successfully")

        except Exception as e:
            logging.error(f"Failed to load model: {e}")
            raise

    def generate_document(
        self,
        prompt: str,
        document_type: str = "chronicle",
        world_context: Optional[Dict] = None,
        **generation_kwargs
    ) -> Dict[str, Any]:
        """
        Generate a single document with coherence validation.

        Args:
            prompt: Initial prompt for generation
            document_type: Type of document to generate
            world_context: Optional world context for consistency
            **generation_kwargs: Override generation parameters

        Returns:
            Generated document with metadata
        """

        logging.info(f"Generating {document_type} document")

        # Merge generation config
        gen_config = self._create_generation_config(**generation_kwargs)

        # Update world context
        if world_context:
            self.current_world_context.update(world_context)

        # Format prompt for document type
        formatted_prompt = self._format_prompt(prompt, document_type)

        # Generate text
        if self.config.use_streaming:
            generated_text = self._generate_streaming(formatted_prompt, gen_config)
        else:
            generated_text = self._generate_standard(formatted_prompt, gen_config)

        # Validate coherence
        coherence_score = 1.0
        if self.config.validate_coherence and self.coherence_validator:
            coherence_score = self.coherence_validator.validate_text(
                generated_text, self.current_world_context
            )

            # Regenerate if below threshold
            if coherence_score < self.config.coherence_threshold:
                logging.warning(f"Low coherence score ({coherence_score:.3f}), regenerating...")
                generated_text = self._regenerate_with_guidance(formatted_prompt, gen_config)
                coherence_score = self.coherence_validator.validate_text(
                    generated_text, self.current_world_context
                )

        # Format output
        document = self._format_document_output(
            generated_text,
            document_type,
            prompt,
            coherence_score,
        )

        # Update knowledge graph
        if self.config.use_knowledge_graph and self.knowledge_graph:
            self._update_knowledge_graph(document)

        # Track generation
        self.generation_history.append({
            "timestamp": time.time(),
            "document_type": document_type,
            "coherence_score": coherence_score,
            "prompt_length": len(prompt),
            "output_length": len(generated_text),
        })

        return document

    def generate_document_sequence(
        self,
        initial_prompt: str,
        document_types: List[str],
        world_context: Optional[Dict] = None,
        maintain_narrative: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Generate a sequence of related documents maintaining narrative coherence.

        Args:
            initial_prompt: Starting prompt for the sequence
            document_types: List of document types to generate
            world_context: World context for consistency
            maintain_narrative: Whether to maintain narrative coherence across documents

        Returns:
            List of generated documents
        """

        logging.info(f"Generating document sequence: {document_types}")

        documents = []
        current_context = world_context or {}

        for i, doc_type in enumerate(document_types):
            # Create context-aware prompt
            if i == 0:
                prompt = initial_prompt
            else:
                prompt = self._create_continuation_prompt(documents, doc_type, current_context)

            # Generate document
            document = self.generate_document(
                prompt=prompt,
                document_type=doc_type,
                world_context=current_context,
            )

            documents.append(document)

            # Update context for next document
            if maintain_narrative:
                current_context = self._extract_narrative_context(documents)

        # Validate sequence coherence
        if self.config.validate_coherence:
            sequence_coherence = self._validate_sequence_coherence(documents)
            logging.info(f"Sequence coherence score: {sequence_coherence:.3f}")

        return documents

    def generate_batch(
        self,
        prompts: List[str],
        document_types: Optional[List[str]] = None,
        **generation_kwargs
    ) -> List[Dict[str, Any]]:
        """Generate multiple documents in batch for efficiency."""

        if not self.config.batch_generation:
            # Fall back to individual generation
            results = []
            for i, prompt in enumerate(prompts):
                doc_type = document_types[i] if document_types else "chronicle"
                result = self.generate_document(prompt, doc_type, **generation_kwargs)
                results.append(result)
            return results

        logging.info(f"Batch generating {len(prompts)} documents")

        # Format all prompts
        formatted_prompts = []
        for i, prompt in enumerate(prompts):
            doc_type = document_types[i] if document_types else "chronicle"
            formatted_prompts.append(self._format_prompt(prompt, doc_type))

        # Batch tokenization
        gen_config = self._create_generation_config(**generation_kwargs)

        inputs = self.tokenizer(
            formatted_prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=self.config.max_context_length,
        ).to(self.model.device)

        # Batch generation
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                **gen_config,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        # Decode results
        results = []
        for i, output in enumerate(outputs):
            # Extract only new tokens
            generated_tokens = output[inputs["input_ids"].shape[1]:]
            generated_text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)

            doc_type = document_types[i] if document_types else "chronicle"
            document = self._format_document_output(
                generated_text,
                doc_type,
                prompts[i],
                coherence_score=0.8,  # Placeholder for batch
            )

            results.append(document)

        return results

    def _create_generation_config(self, **kwargs) -> Dict:
        """Create HuggingFace generation config from our config."""
        gen_params = {
            "max_new_tokens": kwargs.get("max_new_tokens", self.config.max_new_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "top_p": kwargs.get("top_p", self.config.top_p),
            "top_k": kwargs.get("top_k", self.config.top_k),
            "repetition_penalty": kwargs.get("repetition_penalty", self.config.repetition_penalty),
            "do_sample": kwargs.get("do_sample", self.config.do_sample),
            "num_return_sequences": kwargs.get("num_return_sequences", self.config.num_return_sequences),
        }

        if self.config.seed is not None:
            torch.manual_seed(self.config.seed)

        return gen_params

    def _format_prompt(self, prompt: str, document_type: str) -> str:
        """Format prompt with document type structure."""

        # Document type templates
        templates = {
            "chronicle": "<|chronicle|>\nTitle: {title}\nDate: {date}\n\n{content}",
            "diary": "<|diary_entry|>\nAuthor: {author}\nDate: {date}\n\n{content}",
            "letter": "<|letter|>\nFrom: {sender}\nTo: {recipient}\nDate: {date}\n\n{content}",
            "news_article": "<|news_article|>\nHeadline: {headline}\nReporter: {reporter}\nDate: {date}\n\n{content}",
            "song": "<|song|>\nTitle: {title}\nArtist: {artist}\n\n{content}",
            "legal_document": "<|legal_document|>\nDocument: {title}\nDate: {date}\n\n{content}",
            "map": "<|map|>\nMap: {title}\n\n{content}",
            "inventory": "<|inventory|>\nLocation: {location}\nDate: {date}\n\n{content}",
            "treaty": "<|treaty|>\nTreaty: {title}\nParties: {parties}\nDate: {date}\n\n{content}",
            "speech": "<|speech|>\nSpeaker: {speaker}\nOccasion: {occasion}\nDate: {date}\n\n{content}",
        }

        template = templates.get(document_type, "<|document|>\nType: {document_type}\n\n{content}")

        # If prompt already contains template structure, return as-is
        if any(marker in prompt for marker in ["<|", "|>", "Title:", "Author:", "From:"]):
            return prompt

        # Otherwise, wrap in appropriate template
        if document_type in templates:
            # Extract any existing metadata from prompt
            if "Title:" in prompt or "Date:" in prompt:
                return prompt  # Already formatted
            else:
                # Simple wrapper - let the model fill in details
                return f"{template.split('{content}')[0]}{prompt}"

        return prompt

    def _generate_standard(self, prompt: str, gen_config: Dict) -> str:
        """Standard generation without streaming."""

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.config.max_context_length,
        ).to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                **gen_config,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        # Extract only new tokens
        generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]
        generated_text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)

        return generated_text.strip()

    def _generate_streaming(self, prompt: str, gen_config: Dict) -> str:
        """Generate text with streaming (for real-time display)."""

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.config.max_context_length,
        ).to(self.model.device)

        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
        )

        generation_kwargs = {**gen_config, "streamer": streamer}

        # Start generation in separate thread
        thread = Thread(
            target=self.model.generate,
            kwargs={**inputs, **generation_kwargs, "pad_token_id": self.tokenizer.eos_token_id}
        )
        thread.start()

        # Collect streamed text
        generated_text = ""
        for token in streamer:
            generated_text += token

        thread.join()
        return generated_text.strip()

    def _regenerate_with_guidance(self, prompt: str, gen_config: Dict) -> str:
        """Regenerate with additional guidance for coherence."""

        # Add coherence guidance to prompt
        guidance = "\n[Generate coherent, well-structured content that maintains consistency with established narrative elements.]"
        guided_prompt = prompt + guidance

        # Slightly adjust generation parameters for more coherent output
        adjusted_config = gen_config.copy()
        adjusted_config["temperature"] = max(0.5, adjusted_config["temperature"] - 0.2)
        adjusted_config["repetition_penalty"] = min(1.3, adjusted_config["repetition_penalty"] + 0.1)

        return self._generate_standard(guided_prompt, adjusted_config)

    def _format_document_output(
        self,
        generated_text: str,
        document_type: str,
        original_prompt: str,
        coherence_score: float,
    ) -> Dict[str, Any]:
        """Format the generated text into a structured document."""

        # Use output formatter
        formatted_doc = self.output_formatter.format_document(
            generated_text,
            document_type,
            self.config.output_format,
        )

        # Add metadata
        if self.config.include_metadata:
            formatted_doc["metadata"] = {
                "generation_timestamp": time.time(),
                "document_type": document_type,
                "coherence_score": coherence_score,
                "generation_config": {
                    "temperature": self.config.temperature,
                    "top_p": self.config.top_p,
                    "max_new_tokens": self.config.max_new_tokens,
                },
                "original_prompt": original_prompt,
                "generated_length": len(generated_text),
                "model_path": str(self.model_path),
            }

        return formatted_doc

    def _create_continuation_prompt(
        self,
        previous_documents: List[Dict],
        next_doc_type: str,
        context: Dict,
    ) -> str:
        """Create a prompt for continuing the narrative."""

        # Extract key narrative elements from previous documents
        characters = set()
        locations = set()
        events = []

        for doc in previous_documents[-2:]:  # Use last 2 documents
            content = doc.get("content", "")
            # Simple extraction (could be enhanced with NER)
            if "characters" in doc.get("metadata", {}):
                characters.update(doc["metadata"]["characters"])
            if "locations" in doc.get("metadata", {}):
                locations.update(doc["metadata"]["locations"])

        # Create continuation prompt
        continuation_elements = []

        if characters:
            continuation_elements.append(f"Characters: {', '.join(list(characters)[:3])}")
        if locations:
            continuation_elements.append(f"Setting: {list(locations)[0] if locations else 'Unknown'}")

        context_str = " | ".join(continuation_elements) if continuation_elements else "Continuing the narrative"

        # Format for next document type
        type_prompts = {
            "chronicle": f"Chronicle Entry - {context_str}\n\nRecording the events that followed",
            "diary": f"Personal Diary - {context_str}\n\nToday I must record what transpired",
            "letter": f"Correspondence - {context_str}\n\nI write to inform you of recent developments",
            "news_article": f"News Report - {context_str}\n\nBreaking: Recent events have unfolded",
        }

        return type_prompts.get(next_doc_type, f"{next_doc_type.title()} - {context_str}\n\n")

    def _extract_narrative_context(self, documents: List[Dict]) -> Dict:
        """Extract narrative context from generated documents."""

        context = {
            "characters": set(),
            "locations": set(),
            "events": [],
            "timeline": [],
            "themes": [],
        }

        for doc in documents:
            # Extract from metadata if available
            if "metadata" in doc:
                meta = doc["metadata"]
                if "characters" in meta:
                    context["characters"].update(meta["characters"])
                if "locations" in meta:
                    context["locations"].update(meta["locations"])
                if "events" in meta:
                    context["events"].extend(meta["events"])

            # Simple text analysis
            content = doc.get("content", "")
            # This could be enhanced with proper NER and event extraction

        # Convert sets to lists for JSON serialization
        context["characters"] = list(context["characters"])
        context["locations"] = list(context["locations"])

        return context

    def _validate_sequence_coherence(self, documents: List[Dict]) -> float:
        """Validate coherence across a sequence of documents."""

        if not self.coherence_validator:
            return 0.8  # Default score

        # Extract text from all documents
        texts = [doc.get("content", "") for doc in documents]

        # Calculate average pairwise coherence
        scores = []
        for i in range(len(texts) - 1):
            score = self.coherence_validator.validate_coherence_between_texts(
                texts[i], texts[i + 1]
            )
            scores.append(score)

        return sum(scores) / len(scores) if scores else 0.8

    def _update_knowledge_graph(self, document: Dict):
        """Update knowledge graph with information from generated document."""

        if not self.knowledge_graph:
            return

        # Extract entities and relationships
        content = document.get("content", "")
        doc_type = document.get("document_type", "unknown")

        # This would integrate with the knowledge graph system
        # to track characters, locations, events, and relationships
        try:
            # Simple entity extraction (could be enhanced)
            entities = self._extract_simple_entities(content)

            for entity in entities:
                self.knowledge_graph.add_entity(
                    entity_type="character",  # Could be more sophisticated
                    name=entity,
                    properties={"mentioned_in": doc_type}
                )
        except Exception as e:
            logging.warning(f"Failed to update knowledge graph: {e}")

    def _extract_simple_entities(self, text: str) -> List[str]:
        """Simple entity extraction (placeholder for more sophisticated NER)."""
        import re

        # Look for capitalized words that might be names
        potential_entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)

        # Filter out common words
        common_words = {"The", "This", "That", "And", "But", "When", "Where", "Who", "What", "How"}
        entities = [entity for entity in potential_entities if entity not in common_words]

        return entities[:10]  # Limit to prevent noise

    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive generation statistics."""

        if not self.generation_history:
            return {"error": "No generation history available"}

        stats = {
            "total_generations": len(self.generation_history),
            "average_coherence_score": sum(g["coherence_score"] for g in self.generation_history) / len(self.generation_history),
            "document_type_distribution": {},
            "average_output_length": sum(g["output_length"] for g in self.generation_history) / len(self.generation_history),
            "generation_times": [],
        }

        # Document type distribution
        for gen in self.generation_history:
            doc_type = gen["document_type"]
            stats["document_type_distribution"][doc_type] = stats["document_type_distribution"].get(doc_type, 0) + 1

        # Recent performance
        if len(self.generation_history) >= 2:
            recent_generations = self.generation_history[-10:]  # Last 10
            stats["recent_average_coherence"] = sum(g["coherence_score"] for g in recent_generations) / len(recent_generations)

        return stats

    def save_generation_log(self, output_path: Union[str, Path]):
        """Save generation history to file."""

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        log_data = {
            "config": self.config.__dict__,
            "model_path": str(self.model_path),
            "generation_history": self.generation_history,
            "statistics": self.get_generation_statistics(),
        }

        with open(output_path, "w") as f:
            json.dump(log_data, f, indent=2)

        logging.info(f"Generation log saved to: {output_path}")

    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'model') and self.model:
            del self.model

        if hasattr(self, 'tokenizer') and self.tokenizer:
            del self.tokenizer

        torch.cuda.empty_cache()
        logging.info("Document generator resources cleaned up")