"""
Training Data Generator for Learned Scorer.
Generates synthetic pointer-selection tasks using existing NPTS system.
"""

import numpy as np
import json
import random
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib

from context_graph import ContextGraph, TextSegment

# Real semantic embeddings
from sentence_transformers import SentenceTransformer

@dataclass
class PointerTrainingExample:
    """Single training example for pointer selection."""
    query: str
    query_embedding: List[float]
    segments: List[Dict[str, Any]]  # Segment metadata
    segment_embeddings: List[List[float]]
    gold_pointers: List[int]  # Indices of important segments
    gold_budget: int  # Optimal budget for this query
    temporal_chain: Optional[List[int]] = None  # Temporal ordering if applicable
    difficulty: str = "medium"  # easy, medium, hard
    task_type: str = "factual"  # factual, temporal, multi_hop, etc.

class TrainingDataGenerator:
    """Generates training data for learned scorer from synthetic tasks."""

    def __init__(self, embedding_dim: int = 768, use_real_embeddings: bool = True):
        """
        Initialize generator with option for real semantic embeddings.

        Args:
            embedding_dim: Dimension of embeddings (768 for all-mpnet-base-v2)
            use_real_embeddings: If True, use SentenceTransformer. If False, use synthetic hash embeddings.
        """
        self.embedding_dim = embedding_dim
        self.use_real_embeddings = use_real_embeddings
        self.task_types = ['factual', 'temporal', 'multi_hop', 'numerical', 'comparison']
        self.difficulty_levels = ['easy', 'medium', 'hard']

        # Load real embedding model if requested
        if self.use_real_embeddings:
            print("🔄 Loading SentenceTransformer model (all-mpnet-base-v2)...")
            self.embedder = SentenceTransformer('all-mpnet-base-v2')
            self.embedding_dim = 768  # all-mpnet-base-v2 produces 768-dim embeddings
            print(f"✅ Real semantic embeddings loaded (dim={self.embedding_dim})")
        else:
            self.embedder = None
            print(f"⚠️  Using synthetic hash-based embeddings (dim={self.embedding_dim})")

    def generate_embedding(self, text: str, seed: Optional[int] = None) -> np.ndarray:
        """
        Generate embedding from text using real SentenceTransformer or synthetic hash.

        Args:
            text: Text to embed
            seed: Random seed (only used for synthetic embeddings)

        Returns:
            Embedding vector as numpy array
        """
        if self.use_real_embeddings:
            # Use real semantic embeddings from SentenceTransformer
            embedding = self.embedder.encode(text, convert_to_numpy=True)
            return embedding
        else:
            # Fall back to synthetic hash-based embeddings
            if seed is None:
                seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)

            np.random.seed(seed)
            # Generate embedding with some structure based on text length and content
            base_embedding = np.random.randn(self.embedding_dim)

            # Add some deterministic components based on text
            words = text.lower().split()
            if words:
                # Simple heuristic: longer texts and certain keywords affect embedding
                length_factor = min(len(words) / 100, 1.0)
                keyword_factor = sum(1 for w in words if w in ['quantum', 'climate', 'renewable', 'research'])

                base_embedding[0] = length_factor
                base_embedding[1] = keyword_factor / 10

            # Normalize
            norm = np.linalg.norm(base_embedding)
            if norm > 0:
                base_embedding = base_embedding / norm

            return base_embedding

    def generate_synthetic_corpus(self, num_documents: int = 100) -> List[Dict[str, Any]]:
        """Generate synthetic documents with planted needles."""
        topics = [
            ("quantum computing", ["qubit", "superposition", "entanglement", "quantum algorithm"]),
            ("climate change", ["carbon emissions", "global warming", "renewable energy", "climate policy"]),
            ("biotechnology", ["genetic engineering", "CRISPR", "gene therapy", "biotech research"]),
            ("space exploration", ["satellite", "mars mission", "space station", "rocket technology"]),
            ("artificial intelligence", ["machine learning", "neural network", "deep learning", "AI research"]),
            ("renewable energy", ["solar power", "wind energy", "battery technology", "clean energy"]),
            ("ocean conservation", ["marine biodiversity", "coral reef", "ocean acidification", "marine protection"]),
            ("public health", ["vaccination", "disease prevention", "healthcare policy", "medical research"])
        ]

        documents = []

        for doc_id in range(num_documents):
            topic, keywords = random.choice(topics)

            # Generate document with 5-15 segments
            num_segments = random.randint(5, 15)
            doc_segments = []

            # Plant 2-4 "needle" segments with important information
            needle_positions = random.sample(range(num_segments), min(random.randint(2, 4), num_segments))

            for seg_idx in range(num_segments):
                is_needle = seg_idx in needle_positions

                if is_needle:
                    # Generate needle segment with keywords
                    num_keywords = random.randint(2, 3)
                    selected_keywords = random.sample(keywords, num_keywords)

                    text = f"Research on {topic} shows that {' and '.join(selected_keywords)} are critical. "
                    text += f"Studies indicate {random.choice(keywords)} has significant impact. "
                    text += f"Recent advances in {topic} demonstrate {random.choice(keywords)} capabilities. "
                    text += f"The {random.choice(keywords)} research yielded important results. "
                else:
                    # Generate distractor segment
                    distractor_topics = [t for t, _ in topics if t != topic]
                    distractor_topic = random.choice(distractor_topics)

                    text = f"General information about {distractor_topic}. "
                    text += "This is background content with less relevance. "
                    text += "Additional contextual information provided here. "
                    text += "Standard reference material for this topic. "

                # Add timestamp
                timestamp = datetime(2020, 1, 1) + timedelta(days=doc_id * 7 + seg_idx)

                segment = {
                    'id': f"doc{doc_id}_seg{seg_idx}",
                    'text': text,
                    'document_id': f"doc{doc_id}",
                    'position': seg_idx,
                    'timestamp': timestamp.isoformat(),
                    'is_needle': is_needle,
                    'topic': topic
                }

                doc_segments.append(segment)

            documents.append({
                'doc_id': f"doc{doc_id}",
                'topic': topic,
                'segments': doc_segments,
                'needle_positions': needle_positions
            })

        return documents

    def generate_training_examples(self,
                                   corpus: List[Dict[str, Any]],
                                   num_examples: int = 1000) -> List[PointerTrainingExample]:
        """Generate training examples from corpus."""
        examples = []

        for _ in range(num_examples):
            # Select random document
            doc = random.choice(corpus)
            topic = doc['topic']
            segments = doc['segments']
            needle_positions = doc['needle_positions']

            # Generate query
            task_type = random.choice(self.task_types)
            difficulty = random.choice(self.difficulty_levels)

            query = self._generate_query(topic, task_type, difficulty)
            query_embedding = self.generate_embedding(query)

            # Prepare segment data
            segment_data = []
            segment_embeddings = []

            for seg in segments:
                segment_data.append({
                    'id': seg['id'],
                    'text': seg['text'],
                    'position': seg['position'],
                    'timestamp': seg['timestamp'],
                    'is_needle': seg['is_needle']
                })
                segment_embeddings.append(self.generate_embedding(seg['text']).tolist())

            # Gold pointers are the needle segments
            gold_pointers = needle_positions

            # Add some noise based on difficulty
            if difficulty == 'easy':
                # Easy: all needles clearly marked
                pass
            elif difficulty == 'medium':
                # Medium: might miss one needle or include one distractor
                if random.random() < 0.3 and len(gold_pointers) > 1:
                    gold_pointers = random.sample(gold_pointers, len(gold_pointers) - 1)
            else:  # hard
                # Hard: might miss needles or include distractors
                if random.random() < 0.5:
                    # Add distractor
                    non_needles = [i for i in range(len(segments)) if i not in gold_pointers]
                    if non_needles:
                        gold_pointers = gold_pointers + [random.choice(non_needles)]

            # Compute optimal budget (tokens needed)
            gold_budget = sum(len(segments[i]['text'].split()) for i in gold_pointers)
            gold_budget = int(gold_budget * 1.2)  # Add 20% buffer

            # Generate temporal chain for temporal tasks
            temporal_chain = None
            if task_type == 'temporal':
                # Sort needles by timestamp
                temporal_chain = sorted(gold_pointers, key=lambda i: segments[i]['timestamp'])

            example = PointerTrainingExample(
                query=query,
                query_embedding=query_embedding.tolist(),
                segments=segment_data,
                segment_embeddings=segment_embeddings,
                gold_pointers=gold_pointers,
                gold_budget=gold_budget,
                temporal_chain=temporal_chain,
                difficulty=difficulty,
                task_type=task_type
            )

            examples.append(example)

        return examples

    def _generate_query(self, topic: str, task_type: str, difficulty: str) -> str:
        """Generate query based on topic and task type."""
        query_templates = {
            'factual': [
                f"What are the key aspects of {topic}?",
                f"Explain the main concepts in {topic}.",
                f"What is important to know about {topic}?",
                f"Describe the fundamentals of {topic}."
            ],
            'temporal': [
                f"How has {topic} evolved over time?",
                f"What are the historical developments in {topic}?",
                f"Trace the timeline of {topic} research.",
                f"When did major advances in {topic} occur?"
            ],
            'multi_hop': [
                f"What is the relationship between different aspects of {topic}?",
                f"How do various {topic} components interact?",
                f"Connect the key concepts in {topic}.",
                f"What are the dependencies in {topic} research?"
            ],
            'numerical': [
                f"What are the quantitative measures in {topic}?",
                f"What numerical data supports {topic} research?",
                f"What are the statistics for {topic}?",
                f"Quantify the impact of {topic}."
            ],
            'comparison': [
                f"Compare different approaches to {topic}.",
                f"What are the advantages and disadvantages of {topic}?",
                f"How does {topic} compare to alternatives?",
                f"Contrast different {topic} methodologies."
            ]
        }

        templates = query_templates.get(task_type, query_templates['factual'])
        query = random.choice(templates)

        # Add difficulty modifiers
        if difficulty == 'hard':
            query += " Provide comprehensive analysis with supporting evidence."

        return query

    def save_training_data(self, examples: List[PointerTrainingExample], filepath: str):
        """Save training examples to JSON file."""
        data = {
            'examples': [asdict(ex) for ex in examples],
            'metadata': {
                'num_examples': len(examples),
                'embedding_dim': self.embedding_dim,
                'use_real_embeddings': self.use_real_embeddings,
                'embedding_model': 'all-MiniLM-L6-v2' if self.use_real_embeddings else 'synthetic_hash',
                'generated_at': datetime.now().isoformat()
            }
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        embedding_type = "real semantic" if self.use_real_embeddings else "synthetic hash"
        print(f"✅ Saved {len(examples)} training examples ({embedding_type} embeddings) to {filepath}")

    def load_training_data(self, filepath: str) -> List[PointerTrainingExample]:
        """Load training examples from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        examples = [PointerTrainingExample(**ex) for ex in data['examples']]

        print(f"✅ Loaded {len(examples)} training examples from {filepath}")
        return examples

    def generate_and_save_dataset(self,
                                 num_documents: int = 100,
                                 num_examples: int = 1000,
                                 output_path: str = 'pointer_training_data.json'):
        """Complete pipeline: generate corpus, create examples, and save."""
        print(f"🔄 Generating synthetic corpus ({num_documents} documents)...")
        corpus = self.generate_synthetic_corpus(num_documents)

        print(f"🔄 Generating training examples ({num_examples} examples)...")
        examples = self.generate_training_examples(corpus, num_examples)

        # Statistics
        difficulty_counts = {d: sum(1 for ex in examples if ex.difficulty == d) for d in self.difficulty_levels}
        task_counts = {t: sum(1 for ex in examples if ex.task_type == t) for t in self.task_types}

        print(f"\n📊 Dataset Statistics:")
        print(f"   Total Examples: {len(examples)}")
        print(f"   Difficulty Distribution:")
        for diff, count in difficulty_counts.items():
            print(f"      {diff}: {count} ({count/len(examples)*100:.1f}%)")
        print(f"   Task Type Distribution:")
        for task, count in task_counts.items():
            print(f"      {task}: {count} ({count/len(examples)*100:.1f}%)")

        avg_segments = np.mean([len(ex.segments) for ex in examples])
        avg_needles = np.mean([len(ex.gold_pointers) for ex in examples])
        avg_budget = np.mean([ex.gold_budget for ex in examples])

        print(f"   Average Segments per Example: {avg_segments:.1f}")
        print(f"   Average Gold Pointers: {avg_needles:.1f}")
        print(f"   Average Budget: {avg_budget:.1f} tokens")

        print(f"\n💾 Saving to {output_path}...")
        self.save_training_data(examples, output_path)

        return examples

if __name__ == "__main__":
    import sys

    # Check for command line args
    use_real = '--synthetic' not in sys.argv
    num_examples = 2000

    if '--test' in sys.argv:
        num_examples = 500

    # Generate training dataset with real or synthetic embeddings
    generator = TrainingDataGenerator(embedding_dim=384, use_real_embeddings=use_real)

    # Quick test
    print("🧪 Testing training data generator...")

    # Generate dataset
    output_path = 'pointer_training_data_semantic.json' if use_real else 'pointer_training_data_synthetic.json'
    examples = generator.generate_and_save_dataset(
        num_documents=100,
        num_examples=num_examples,
        output_path=output_path
    )

    # Show sample example
    print(f"\n📝 Sample Training Example:")
    sample = examples[0]
    print(f"   Query: {sample.query}")
    print(f"   Task Type: {sample.task_type}")
    print(f"   Difficulty: {sample.difficulty}")
    print(f"   Num Segments: {len(sample.segments)}")
    print(f"   Gold Pointers: {sample.gold_pointers}")
    print(f"   Gold Budget: {sample.gold_budget} tokens")
    print(f"   Embedding Dim: {len(sample.query_embedding)}")
    if sample.temporal_chain:
        print(f"   Temporal Chain: {sample.temporal_chain}")

    print(f"\n✅ Training data generator ready!")
    print(f"   Embeddings: {'Real Semantic' if use_real else 'Synthetic Hash'}")
    print(f"   Output: {output_path}")
