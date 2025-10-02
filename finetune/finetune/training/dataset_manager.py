"""
Dataset Manager for Narrative Training Data

Handles preprocessing, formatting, and management of training datasets
optimized for narrative generation and multi-document coherence.
"""

import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import torch
from datasets import Dataset
from transformers import AutoTokenizer

from ..config import TrainingConfig


class DatasetManager:
    """
    Advanced dataset management for narrative training.

    Features:
    - Multi-document narrative preprocessing
    - Context-aware tokenization
    - Cross-document coherence preparation
    - Efficient data loading and caching
    """

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./dataset_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def create_datasets(
        self,
        train_data: List[Dict],
        eval_data: Optional[List[Dict]] = None,
        test_data: Optional[List[Dict]] = None,
        tokenizer: AutoTokenizer = None,
        max_length: int = 2048,
        document_context_length: int = 1024,
        include_cross_document_context: bool = True,
    ) -> Dict[str, Dataset]:
        """
        Create HuggingFace datasets from raw narrative data.

        Args:
            train_data: Training examples
            eval_data: Evaluation examples
            test_data: Test examples
            tokenizer: Tokenizer for preprocessing
            max_length: Maximum sequence length
            document_context_length: Context length for cross-document coherence
            include_cross_document_context: Whether to include cross-document examples

        Returns:
            Dictionary containing datasets
        """

        logging.info(f"Creating datasets: {len(train_data)} train samples")

        datasets = {}

        # Process training data
        processed_train = self._process_narrative_data(
            train_data,
            tokenizer,
            max_length,
            document_context_length,
            include_cross_document_context,
            split="train",
        )
        datasets["train"] = Dataset.from_list(processed_train)

        # Process evaluation data
        if eval_data:
            processed_eval = self._process_narrative_data(
                eval_data,
                tokenizer,
                max_length,
                document_context_length,
                include_cross_document_context,
                split="eval",
            )
            datasets["eval"] = Dataset.from_list(processed_eval)

        # Process test data
        if test_data:
            processed_test = self._process_narrative_data(
                test_data,
                tokenizer,
                max_length,
                document_context_length,
                include_cross_document_context,
                split="test",
            )
            datasets["test"] = Dataset.from_list(processed_test)

        logging.info(f"Datasets created successfully: {list(datasets.keys())}")
        return datasets

    def _process_narrative_data(
        self,
        data: List[Dict],
        tokenizer: AutoTokenizer,
        max_length: int,
        document_context_length: int,
        include_cross_document_context: bool,
        split: str = "train",
    ) -> List[Dict]:
        """Process narrative data with document-aware formatting."""

        processed_samples = []
        document_groups = self._group_by_world(data)

        logging.info(f"Processing {len(data)} {split} samples across {len(document_groups)} worlds")

        for world_id, world_documents in document_groups.items():
            # Process individual documents
            for doc in world_documents:
                sample = self._create_training_sample(
                    doc, tokenizer, max_length, document_type="individual"
                )
                if sample:
                    processed_samples.append(sample)

            # Create cross-document coherence samples
            if include_cross_document_context and len(world_documents) > 1:
                cross_doc_samples = self._create_cross_document_samples(
                    world_documents,
                    tokenizer,
                    max_length,
                    document_context_length,
                )
                processed_samples.extend(cross_doc_samples)

        logging.info(f"Generated {len(processed_samples)} processed samples for {split}")
        return processed_samples

    def _group_by_world(self, data: List[Dict]) -> Dict[str, List[Dict]]:
        """Group documents by world_id for cross-document training."""
        world_groups = {}

        for doc in data:
            world_id = doc.get("world_id", "default_world")
            if world_id not in world_groups:
                world_groups[world_id] = []
            world_groups[world_id].append(doc)

        return world_groups

    def _create_training_sample(
        self,
        document: Dict,
        tokenizer: AutoTokenizer,
        max_length: int,
        document_type: str = "individual",
    ) -> Optional[Dict]:
        """Create a single training sample from a document."""

        # Extract content
        content = document.get("content", document.get("text", ""))
        if not content.strip():
            return None

        # Create formatted text based on document type
        formatted_text = self._format_document_for_training(document)

        # Tokenize
        if tokenizer:
            encoding = tokenizer(
                formatted_text,
                truncation=True,
                max_length=max_length,
                padding=False,
                return_tensors=None,
            )

            return {
                "input_ids": encoding["input_ids"],
                "attention_mask": encoding["attention_mask"],
                "text": formatted_text,
                "document_type": document.get("document_type", "unknown"),
                "world_id": document.get("world_id", "default"),
                "training_type": document_type,
                "metadata": {
                    "original_length": len(content),
                    "tokenized_length": len(encoding["input_ids"]),
                    "timestamp": document.get("timestamp"),
                    "character_names": document.get("character_names", []),
                    "locations": document.get("locations", []),
                    "events": document.get("events", []),
                }
            }
        else:
            return {
                "text": formatted_text,
                "document_type": document.get("document_type", "unknown"),
                "world_id": document.get("world_id", "default"),
                "training_type": document_type,
            }

    def _format_document_for_training(self, document: Dict) -> str:
        """Format document with appropriate structure for training."""

        doc_type = document.get("document_type", "unknown")
        content = document.get("content", document.get("text", ""))

        # Extract metadata
        metadata = document.get("metadata", {})
        title = document.get("title", metadata.get("title", ""))
        author = document.get("author", metadata.get("author", ""))
        date = document.get("timestamp", metadata.get("date", ""))

        # Create structured format based on document type
        if doc_type == "chronicle":
            formatted = f"<|chronicle|>\n"
            if title:
                formatted += f"Title: {title}\n"
            if date:
                formatted += f"Date: {date}\n"
            formatted += f"\n{content}\n<|end_chronicle|>"

        elif doc_type == "diary":
            formatted = f"<|diary_entry|>\n"
            if author:
                formatted += f"Author: {author}\n"
            if date:
                formatted += f"Date: {date}\n"
            formatted += f"\n{content}\n<|end_diary|>"

        elif doc_type == "letter":
            recipient = metadata.get("recipient", "")
            sender = metadata.get("sender", author)

            formatted = f"<|letter|>\n"
            if sender:
                formatted += f"From: {sender}\n"
            if recipient:
                formatted += f"To: {recipient}\n"
            if date:
                formatted += f"Date: {date}\n"
            formatted += f"\n{content}\n<|end_letter|>"

        elif doc_type == "legal_document":
            formatted = f"<|legal_document|>\n"
            if title:
                formatted += f"Document: {title}\n"
            if date:
                formatted += f"Date: {date}\n"
            formatted += f"\n{content}\n<|end_legal|>"

        elif doc_type == "news_article":
            headline = metadata.get("headline", title)

            formatted = f"<|news_article|>\n"
            if headline:
                formatted += f"Headline: {headline}\n"
            if author:
                formatted += f"Reporter: {author}\n"
            if date:
                formatted += f"Date: {date}\n"
            formatted += f"\n{content}\n<|end_news|>"

        elif doc_type == "song":
            artist = metadata.get("artist", author)

            formatted = f"<|song|>\n"
            if title:
                formatted += f"Title: {title}\n"
            if artist:
                formatted += f"Artist: {artist}\n"
            formatted += f"\n{content}\n<|end_song|>"

        elif doc_type == "map":
            formatted = f"<|map|>\n"
            if title:
                formatted += f"Map: {title}\n"
            formatted += f"\n{content}\n<|end_map|>"

        elif doc_type == "inventory":
            location = metadata.get("location", "")

            formatted = f"<|inventory|>\n"
            if location:
                formatted += f"Location: {location}\n"
            if date:
                formatted += f"Date: {date}\n"
            formatted += f"\n{content}\n<|end_inventory|>"

        elif doc_type == "treaty":
            parties = metadata.get("parties", [])

            formatted = f"<|treaty|>\n"
            if title:
                formatted += f"Treaty: {title}\n"
            if parties:
                formatted += f"Parties: {', '.join(parties)}\n"
            if date:
                formatted += f"Date: {date}\n"
            formatted += f"\n{content}\n<|end_treaty|>"

        elif doc_type == "speech":
            speaker = metadata.get("speaker", author)
            occasion = metadata.get("occasion", "")

            formatted = f"<|speech|>\n"
            if speaker:
                formatted += f"Speaker: {speaker}\n"
            if occasion:
                formatted += f"Occasion: {occasion}\n"
            if date:
                formatted += f"Date: {date}\n"
            formatted += f"\n{content}\n<|end_speech|>"

        else:
            # Generic document format
            formatted = f"<|document|>\n"
            if doc_type != "unknown":
                formatted += f"Type: {doc_type}\n"
            if title:
                formatted += f"Title: {title}\n"
            formatted += f"\n{content}\n<|end_document|>"

        return formatted

    def _create_cross_document_samples(
        self,
        documents: List[Dict],
        tokenizer: AutoTokenizer,
        max_length: int,
        context_length: int,
    ) -> List[Dict]:
        """Create training samples that span multiple documents for coherence."""

        cross_doc_samples = []

        # Sort documents by timestamp if available
        sorted_docs = sorted(
            documents,
            key=lambda x: x.get("timestamp", x.get("metadata", {}).get("date", "9999"))
        )

        # Create context-response pairs
        for i in range(1, len(sorted_docs)):
            context_docs = sorted_docs[:i]
            target_doc = sorted_docs[i]

            # Create context from previous documents
            context_text = self._create_document_context(
                context_docs, context_length, tokenizer
            )

            # Format target document
            target_text = self._format_document_for_training(target_doc)

            # Combine context and target
            full_text = f"<|context|>\n{context_text}\n<|end_context|>\n\n{target_text}"

            # Create training sample
            if tokenizer:
                encoding = tokenizer(
                    full_text,
                    truncation=True,
                    max_length=max_length,
                    padding=False,
                    return_tensors=None,
                )

                sample = {
                    "input_ids": encoding["input_ids"],
                    "attention_mask": encoding["attention_mask"],
                    "text": full_text,
                    "document_type": target_doc.get("document_type", "unknown"),
                    "world_id": target_doc.get("world_id", "default"),
                    "training_type": "cross_document",
                    "context_documents": len(context_docs),
                    "metadata": {
                        "target_doc_type": target_doc.get("document_type"),
                        "context_doc_types": [d.get("document_type") for d in context_docs],
                        "tokenized_length": len(encoding["input_ids"]),
                    }
                }
            else:
                sample = {
                    "text": full_text,
                    "document_type": target_doc.get("document_type", "unknown"),
                    "world_id": target_doc.get("world_id", "default"),
                    "training_type": "cross_document",
                    "context_documents": len(context_docs),
                }

            cross_doc_samples.append(sample)

        return cross_doc_samples

    def _create_document_context(
        self,
        documents: List[Dict],
        max_context_length: int,
        tokenizer: Optional[AutoTokenizer] = None,
    ) -> str:
        """Create context string from multiple documents."""

        context_parts = []
        current_length = 0

        # Start with most recent documents
        for doc in reversed(documents):
            doc_summary = self._create_document_summary(doc)

            # Estimate length (rough approximation if no tokenizer)
            if tokenizer:
                doc_tokens = len(tokenizer.encode(doc_summary))
            else:
                doc_tokens = len(doc_summary.split()) * 1.3  # Rough estimate

            if current_length + doc_tokens > max_context_length:
                break

            context_parts.insert(0, doc_summary)  # Insert at beginning
            current_length += doc_tokens

        return "\n---\n".join(context_parts)

    def _create_document_summary(self, document: Dict) -> str:
        """Create a concise summary of a document for context."""

        doc_type = document.get("document_type", "document")
        content = document.get("content", document.get("text", ""))
        metadata = document.get("metadata", {})

        # Create brief summary
        title = document.get("title", metadata.get("title", ""))
        date = document.get("timestamp", metadata.get("date", ""))
        author = document.get("author", metadata.get("author", ""))

        # Truncate content for summary
        content_summary = content[:200] + "..." if len(content) > 200 else content

        summary_parts = [f"[{doc_type.upper()}]"]

        if title:
            summary_parts.append(f"Title: {title}")
        if author:
            summary_parts.append(f"Author: {author}")
        if date:
            summary_parts.append(f"Date: {date}")

        summary_parts.append(f"Content: {content_summary}")

        return " | ".join(summary_parts)

    def load_dataset_from_file(
        self,
        file_path: Union[str, Path],
        tokenizer: Optional[AutoTokenizer] = None,
        max_length: int = 2048,
    ) -> Dataset:
        """Load and process dataset from file."""

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {file_path}")

        # Load data based on file extension
        if file_path.suffix == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        elif file_path.suffix == ".jsonl":
            data = []
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    data.append(json.loads(line.strip()))
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        # Process data
        processed_data = self._process_narrative_data(
            data, tokenizer, max_length, 1024, True, "loaded"
        )

        return Dataset.from_list(processed_data)

    def save_dataset(self, dataset: Dataset, output_path: Union[str, Path]):
        """Save processed dataset to file."""

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to list and save as JSON
        data_list = [item for item in dataset]

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data_list, f, indent=2, ensure_ascii=False)

        logging.info(f"Dataset saved to: {output_path}")

    def get_dataset_statistics(self, dataset: Dataset) -> Dict:
        """Get comprehensive statistics about the dataset."""

        if len(dataset) == 0:
            return {"error": "Empty dataset"}

        stats = {
            "total_samples": len(dataset),
            "document_types": {},
            "training_types": {},
            "world_ids": set(),
            "avg_sequence_length": 0,
            "min_sequence_length": float('inf'),
            "max_sequence_length": 0,
        }

        sequence_lengths = []

        for sample in dataset:
            # Document type distribution
            doc_type = sample.get("document_type", "unknown")
            stats["document_types"][doc_type] = stats["document_types"].get(doc_type, 0) + 1

            # Training type distribution
            training_type = sample.get("training_type", "individual")
            stats["training_types"][training_type] = stats["training_types"].get(training_type, 0) + 1

            # World IDs
            world_id = sample.get("world_id", "default")
            stats["world_ids"].add(world_id)

            # Sequence lengths
            if "input_ids" in sample:
                seq_len = len(sample["input_ids"])
                sequence_lengths.append(seq_len)
                stats["min_sequence_length"] = min(stats["min_sequence_length"], seq_len)
                stats["max_sequence_length"] = max(stats["max_sequence_length"], seq_len)

        if sequence_lengths:
            stats["avg_sequence_length"] = sum(sequence_lengths) / len(sequence_lengths)
            stats["median_sequence_length"] = sorted(sequence_lengths)[len(sequence_lengths) // 2]

        stats["unique_worlds"] = len(stats["world_ids"])
        stats["world_ids"] = list(stats["world_ids"])  # Convert set to list for JSON serialization

        return stats