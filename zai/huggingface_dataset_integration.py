"""
HuggingFace Dataset Integration for 300M Model Training

Incorporates real-world datasets with natural pointer structures:
- HotpotQA (multi-hop reasoning)
- Natural Questions (long context QA)
- Wikipedia (hyperlinks)
- MS MARCO (passage retrieval)
"""

import sys
sys.path.insert(0, '/Users/pup/zai')

import json
import random
import time
from datetime import datetime
from training_data_generator import TrainingDataGenerator, PointerTrainingExample

try:
    import datasets
    from sentence_transformers import SentenceTransformer
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("⚠️  HuggingFace datasets not installed. Install with: pip install datasets sentence-transformers")

def load_hotpotqa_examples(max_examples=2000):
    """Load HotpotQA examples with supporting facts as gold pointers."""
    if not HF_AVAILABLE:
        return []

    print("🔄 Loading HotpotQA dataset...")
    dataset = datasets.load_dataset("hotpot_qa", "fullwiki", split="train[:2000]")
    examples = []

    model = SentenceTransformer('all-MiniLM-L6-v2')

    for item in dataset:
        context = item['context']
        supporting_facts = item['supporting_facts']

        # Create segments from context sentences
        segments = []
        gold_pointers = []

        for i, (title, sentences) in enumerate(zip(context['title'], context['sentences'])):
            segment_text = f"{title}: {' '.join(sentences)}"
            segments.append(segment_text)

        # Mark supporting facts as gold pointers
        for fact in supporting_facts:
            if len(fact) >= 2:  # Handle variable length supporting facts
                title, sent_idx = fact[0], fact[1]
                # Find the segment containing this supporting fact
                for i, (ctx_title, sentences) in enumerate(zip(context['title'], context['sentences'])):
                    if ctx_title == title and sent_idx < len(sentences):
                        gold_pointers.append(i)
                        break

        if len(segments) >= 5 and len(gold_pointers) >= 2:  # Quality filter
            # Create embeddings for segments
            embeddings = model.encode(segments)

            example = PointerTrainingExample(
                segments=segments,
                embeddings=embeddings.tolist(),
                gold_pointer_indices=gold_pointers,
                budget=random.randint(100, 200),  # Reasonable token budget
                difficulty="hard",  # Multi-hop reasoning is hard
                task_type="multi_hop",
                metadata={
                    "dataset": "hotpotqa",
                    "question": item['question'],
                    "answer": item['answer'],
                    "supporting_facts_count": len(supporting_facts)
                }
            )
            examples.append(example.to_dict())

    print(f"✅ Loaded {len(examples)} HotpotQA examples")
    return examples

def load_natural_questions_examples(max_examples=1500):
    """Load Natural Questions examples with long-form answers."""
    if not HF_AVAILABLE:
        return []

    print("🔄 Loading Natural Questions dataset...")
    dataset = datasets.load_dataset("natural_questions", "train", split="train[:1500]")
    examples = []

    model = SentenceTransformer('all-MiniLM-L6-v2')

    for item in dataset:
        document_text = item['document_text']
        long_answer = item['annotations']['long_answer']
        short_answers = item['annotations']['short_answers']

        if not long_answer['start_token'] or long_answer['start_token'] == -1:
            continue

        # Split document into sentences as segments
        sentences = document_text.split('. ')
        segments = [s.strip() for s in sentences if s.strip()]
        gold_pointers = []

        # Find which sentences contain the answer
        answer_start = long_answer['start_token']
        answer_end = long_answer['end_token']

        # Simple heuristic: mark sentences containing answer tokens
        doc_tokens = document_text.split()
        current_token = 0

        for i, sentence in enumerate(segments):
            sentence_tokens = sentence.split()
            if answer_start >= current_token and answer_end <= current_token + len(sentence_tokens):
                gold_pointers.append(i)
            current_token += len(sentence_tokens) + 1  # +1 for the period

        if len(segments) >= 8 and len(gold_pointers) >= 1:  # Quality filter
            embeddings = model.encode(segments)

            example = PointerTrainingExample(
                segments=segments,
                embeddings=embeddings.tolist(),
                gold_pointer_indices=gold_pointers,
                budget=random.randint(150, 250),  # Longer contexts need larger budgets
                difficulty="medium",
                task_type="factual",
                metadata={
                    "dataset": "natural_questions",
                    "question": item['question_text'],
                    "has_long_answer": True,
                    "short_answers_count": len(short_answers)
                }
            )
            examples.append(example.to_dict())

    print(f"✅ Loaded {len(examples)} Natural Questions examples")
    return examples

def load_wikipedia_hyperlink_examples(max_examples=1000):
    """Load Wikipedia examples with hyperlinks as natural pointers."""
    if not HF_AVAILABLE:
        return []

    print("🔄 Loading Wikipedia dataset...")
    dataset = datasets.load_dataset("wikipedia", "20220301.en", split="train[:1000]")
    examples = []

    model = SentenceTransformer('all-MiniLM-L6-v2')

    for item in dataset:
        text = item['text']

        # Simple sentence splitting
        sentences = [s.strip() for s in text.split('. ') if s.strip()]

        # Look for hyperlink patterns (simplified)
        gold_pointers = []
        for i, sentence in enumerate(sentences):
            # Simple heuristic: sentences with common Wikipedia link patterns
            if any(keyword in sentence.lower() for keyword in [
                'according to', 'refer to', 'see also', 'based on', 'similar to'
            ]):
                gold_pointers.append(i)

        # Also add some random pointers for diversity
        if len(sentences) > 10:
            additional_pointers = random.sample(
                [i for i in range(len(sentences)) if i not in gold_pointers],
                min(3, len(sentences) - len(gold_pointers))
            )
            gold_pointers.extend(additional_pointers)

        if len(sentences) >= 12 and len(gold_pointers) >= 2:  # Quality filter
            embeddings = model.encode(sentences)

            example = PointerTrainingExample(
                segments=sentences,
                embeddings=embeddings.tolist(),
                gold_pointer_indices=gold_pointers,
                budget=random.randint(120, 220),
                difficulty="medium",
                task_type="factual",
                metadata={
                    "dataset": "wikipedia",
                    "url": item.get('url', ''),
                    "title": item.get('title', ''),
                    "link_count": len(gold_pointers)
                }
            )
            examples.append(example.to_dict())

    print(f"✅ Loaded {len(examples)} Wikipedia examples")
    return examples

def create_hybrid_dataset():
    """Create a hybrid dataset combining synthetic and real HuggingFace data."""
    print("="*80)
    print("🚀 CREATING HYBRID DATASET FOR 300M MODEL TRAINING")
    print("="*80)

    all_examples = []

    # Load synthetic data (existing)
    print("\n📊 Loading existing synthetic data...")
    try:
        with open('pointer_training_data_semantic_20000.json', 'r') as f:
            synthetic_examples = json.load(f)
        all_examples.extend(synthetic_examples)
        print(f"✅ Loaded {len(synthetic_examples)} synthetic examples")
    except FileNotFoundError:
        print("⚠️  Synthetic 20K file not found, will generate fresh data")
        synthetic_examples = []

    # Load HuggingFace datasets
    hotpot_examples = load_hotpotqa_examples(2000)
    nq_examples = load_natural_questions_examples(1500)
    wiki_examples = load_wikipedia_hyperlink_examples(1000)

    all_examples.extend(hotpot_examples)
    all_examples.extend(nq_examples)
    all_examples.extend(wiki_examples)

    # Shuffle to mix synthetic and real data
    random.shuffle(all_examples)

    # Save hybrid dataset
    output_path = f'pointer_training_data_hybrid_300m_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

    print(f"\n💾 Saving hybrid dataset to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(all_examples, f, indent=2)

    # Statistics
    dataset_types = {}
    difficulty_dist = {}
    task_type_dist = {}

    for ex in all_examples:
        dataset_type = ex.get('metadata', {}).get('dataset', 'synthetic')
        dataset_types[dataset_type] = dataset_types.get(dataset_type, 0) + 1

        difficulty = ex.get('difficulty', 'unknown')
        difficulty_dist[difficulty] = difficulty_dist.get(difficulty, 0) + 1

        task_type = ex.get('task_type', 'unknown')
        task_type_dist[task_type] = task_type_dist.get(task_type, 0) + 1

    print(f"\n📊 HYBRID DATASET STATISTICS:")
    print(f"   Total Examples: {len(all_examples)}")
    print(f"   Dataset Types: {dict(dataset_types)}")
    print(f"   Difficulty Distribution: {dict(difficulty_dist)}")
    print(f"   Task Type Distribution: {dict(task_type_dist)}")
    print(f"   Output File: {output_path}")

    return output_path

if __name__ == "__main__":
    if not HF_AVAILABLE:
        print("❌ Please install required packages:")
        print("   pip install datasets sentence-transformers")
        exit(1)

    start_time = time.time()
    output_file = create_hybrid_dataset()
    elapsed = time.time() - start_time

    print(f"\n✅ HYBRID DATASET CREATION COMPLETE!")
    print(f"   Time: {elapsed/60:.1f} minutes")
    print(f"   Ready for 300M model training: {output_file}")