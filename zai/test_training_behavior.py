#!/usr/bin/env python3
"""
Test script to reproduce the exact training script behavior and identify where it goes wrong
"""

import sys
import json
import torch
from torch.utils.data import Dataset, DataLoader

# Copy the exact classes from train_simple_large.py
class PointerDataset(Dataset):
    def __init__(self, examples):
        self.examples = examples

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        return self.examples[idx]

def test_training_script_behavior(data_path):
    """Reproduce exact training script behavior"""

    print("="*80)
    print(f"🧪 TESTING TRAINING SCRIPT BEHAVIOR")
    print(f"Data: {data_path}")
    print("="*80)

    # Exact copy from train_simple_large.py
    print(f"\n📂 Loading training data from {data_path}...")
    with open(data_path, 'r') as f:
        data = json.load(f)

    # Handle both wrapped and unwrapped formats
    if isinstance(data, dict) and 'examples' in data:
        examples = data['examples']
    else:
        examples = data

    print(f"   Loaded {len(examples)} examples")

    # Create dataset
    dataset = PointerDataset(examples)

    # Split data
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])

    print(f"   Train: {len(train_dataset)}, Val: {len(val_dataset)}")

    # Test accessing items from the split datasets
    print(f"\n🔍 Testing dataset access...")

    # Test train dataset access
    try:
        for i in range(min(3, len(train_dataset))):
            item = train_dataset[i]
            print(f"   ✅ train_dataset[{i}]: {type(item)}")
            if isinstance(item, dict):
                print(f"      Keys: {list(item.keys())}")
    except Exception as e:
        print(f"   ❌ Error accessing train_dataset[{i}]: {e}")
        import traceback
        traceback.print_exc()

    # Test val dataset access
    try:
        for i in range(min(3, len(val_dataset))):
            item = val_dataset[i]
            print(f"   ✅ val_dataset[{i}]: {type(item)}")
    except Exception as e:
        print(f"   ❌ Error accessing val_dataset[{i}]: {e}")
        import traceback
        traceback.print_exc()

    # Test collate function
    print(f"\n🔍 Testing collate function...")

    def collate_fn(batch):
        """Custom collate function from training script"""
        max_len = max(len(ex['segment_embeddings'][0]) for ex in batch)

        batch_embeddings = []
        batch_pointer_indices = []
        batch_labels = []

        for ex in batch:
            # Pad embeddings to max_len
            embeddings = torch.tensor(ex['segment_embeddings'], dtype=torch.float32)
            if embeddings.shape[1] < max_len:
                padding = torch.zeros(embeddings.shape[0], max_len - embeddings.shape[1])
                embeddings = torch.cat([embeddings, padding], dim=1)

            batch_embeddings.append(embeddings)

            # Convert pointer indices to tensor
            pointer_indices = torch.tensor(ex['gold_pointers'][:10], dtype=torch.long)
            if len(pointer_indices) < 10:
                padding = torch.full((10 - len(pointer_indices),), -1, dtype=torch.long)
                pointer_indices = torch.cat([pointer_indices, padding])

            batch_pointer_indices.append(pointer_indices)

            # Simple label: 1 if contains gold pointers, 0 otherwise
            label = torch.tensor(1.0, dtype=torch.float32)
            batch_labels.append(label)

        # Pad all embeddings to same size
        max_segments = max(emb.shape[0] for emb in batch_embeddings)
        max_len = max(emb.shape[1] for emb in batch_embeddings)

        padded_embeddings = []
        for emb in batch_embeddings:
            if emb.shape[0] < max_segments:
                seg_padding = torch.zeros(max_segments - emb.shape[0], emb.shape[1])
                emb = torch.cat([emb, seg_padding], dim=0)
            if emb.shape[1] < max_len:
                len_padding = torch.zeros(emb.shape[0], max_len - emb.shape[1])
                emb = torch.cat([emb, len_padding], dim=1)
            padded_embeddings.append(emb)

        return {
            'embeddings': torch.stack(padded_embeddings),
            'pointer_indices': torch.stack(batch_pointer_indices),
            'labels': torch.stack(batch_labels)
        }

    # Test DataLoader with small batch
    try:
        small_train_dataset, _ = torch.utils.data.random_split(dataset, [min(10, len(dataset)), max(0, len(dataset)-10)])

        train_loader = DataLoader(
            small_train_dataset,
            batch_size=2,
            shuffle=True,
            collate_fn=collate_fn,
            num_workers=0
        )

        print(f"   ✅ DataLoader created")

        for batch in train_loader:
            print(f"   ✅ Batch loaded successfully!")
            print(f"      embeddings shape: {batch['embeddings'].shape}")
            print(f"      pointer_indices shape: {batch['pointer_indices'].shape}")
            print(f"      labels shape: {batch['labels'].shape}")
            break

    except Exception as e:
        print(f"   ❌ DataLoader error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 test_training_behavior.py <dataset_file>")
        sys.exit(1)

    data_path = sys.argv[1]
    test_training_script_behavior(data_path)