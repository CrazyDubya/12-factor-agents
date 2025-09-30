"""
Create a simple million-token dataset with proper JSON serialization.
"""

import json
import random
import numpy as np
from datetime import datetime

def create_simple_million_token_dataset():
    """Create a simple dataset with 1 million tokens."""
    print("Creating simple million-token dataset...")

    # Generate a mix of content
    topics = [
        "Artificial intelligence and machine learning are transforming industries worldwide.",
        "Climate change represents one of the most pressing challenges of our time.",
        "Renewable energy sources include solar, wind, hydro, and geothermal power.",
        "Quantum computing promises revolutionary advances in computational capability.",
        "Biotechnology enables new medical treatments and genetic engineering applications.",
        "Space exploration continues to push the boundaries of human knowledge.",
        "Environmental protection requires international cooperation and sustainable practices.",
        "Ocean acidification threatens marine ecosystems worldwide.",
        "Biodiversity loss accelerates due to habitat destruction and climate change.",
        "Sustainable development must balance economic growth with environmental protection."
    ]

    documents = []
    target_tokens = 1_000_000
    current_tokens = 0

    doc_id = 0
    while current_tokens < target_tokens:
        # Create document of varying size
        doc_size = random.choice([10000, 25000, 50000, 100000])
        if current_tokens + doc_size > target_tokens:
            doc_size = target_tokens - current_tokens

        # Generate content
        content_parts = []
        tokens_in_doc = 0

        # Add header
        header = f"# Document {doc_id:04d}\n\n"
        content_parts.append(header)
        tokens_in_doc += len(header.split())

        # Add paragraphs
        while tokens_in_doc < doc_size:
            # Choose topic
            topic = random.choice(topics)

            # Generate paragraph by repeating and varying the topic
            paragraph_words = []
            for i in range(random.randint(50, 200)):
                if i % 10 == 0:
                    paragraph_words.extend(topic.split())
                else:
                    # Add related words
                    related = random.choice([
                        "research", "development", "analysis", "study", "investigation",
                        "implementation", "application", "methodology", "framework",
                        "strategy", "approach", "technique", "process", "system"
                    ])
                    paragraph_words.append(related)

            paragraph = " ".join(paragraph_words) + ". "
            content_parts.append(paragraph)
            tokens_in_doc += len(paragraph.split())

        # Create document
        document = {
            "id": f"doc_{doc_id:04d}",
            "title": f"Document {doc_id:04d} - Mixed Content",
            "text": "".join(content_parts),
            "timestamp": datetime(2024, 1 + (doc_id % 12), 1 + (doc_id % 28)).isoformat(),
            "metadata": {
                "tokens_estimated": tokens_in_doc,
                "type": "mixed_content",
                "complexity": random.choice(["low", "medium", "high"])
            }
        }

        documents.append(document)
        current_tokens += tokens_in_doc
        doc_id += 1

        if doc_id % 100 == 0:
            print(f"  Created {doc_id} documents, {current_tokens:,} tokens...")

    # Create dataset
    dataset = {
        "metadata": {
            "created_at": datetime.now().isoformat(),
            "total_documents": len(documents),
            "total_tokens": current_tokens,
            "dataset_type": "simple_mixed",
            "description": "Simple mixed content dataset for testing"
        },
        "documents": documents
    }

    # Save dataset
    with open('simple_million_token_dataset.json', 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2)

    print(f"\nDataset created successfully:")
    print(f"- Documents: {len(documents)}")
    print(f"- Total tokens: {current_tokens:,}")
    print(f"- Saved to: simple_million_token_dataset.json")

    # Show sample
    sample = documents[0]
    print(f"\nSample document:")
    print(f"- ID: {sample['id']}")
    print(f"- Tokens: {sample['metadata']['tokens_estimated']:,}")
    print(f"- Preview: {sample['text'][:200]}...")

    return dataset

if __name__ == "__main__":
    # Set seeds for reproducibility
    random.seed(42)
    np.random.seed(42)

    dataset = create_simple_million_token_dataset()