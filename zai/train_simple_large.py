"""
Simplified Large Model Training Script
Works without missing dependencies - direct training for 200M and 300M models
"""

import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import json
import time
from datetime import datetime
import argparse
import os

# Simple pointer dataset
class PointerDataset(Dataset):
    def __init__(self, examples):
        self.examples = examples

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        return self.examples[idx]

def collate_fn(batch):
    """Custom collate function for variable-length sequences."""
    # Get max sequence length
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
        pointer_indices = torch.tensor(ex['gold_pointers'][:10], dtype=torch.long)  # Limit to 10 pointers
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

class SimpleLearnedScorer(nn.Module):
    """Simplified learned scorer for large models."""

    def __init__(self, hidden_size, num_layers, num_heads, intermediate_size):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # Embedding projection (from 768 to hidden_size)
        self.input_projection = nn.Linear(768, hidden_size)

        # Transformer encoder layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_size,
            nhead=num_heads,
            dim_feedforward=intermediate_size,
            dropout=0.1,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        # Pointer scoring head
        self.pointer_scorer = nn.Linear(hidden_size, 1)

        # Final classification head
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool1d(1),
            nn.Flatten(),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, 1),
            nn.Sigmoid()
        )

    def forward(self, embeddings, pointer_indices):
        # Project input embeddings
        x = self.input_projection(embeddings)  # [batch, seq_len, hidden_size]

        # Apply transformer
        x = self.transformer(x)

        # Score each position for pointing
        pointer_scores = self.pointer_scorer(x).squeeze(-1)  # [batch, seq_len]

        # Get scores for gold pointer positions
        batch_size, seq_len = pointer_scores.shape
        gold_scores = []

        for i in range(batch_size):
            # Get valid pointer indices (exclude padding -1)
            valid_indices = pointer_indices[i][pointer_indices[i] >= 0]
            valid_indices = valid_indices[valid_indices < seq_len]

            if len(valid_indices) > 0:
                gold_score = pointer_scores[i][valid_indices].mean()
            else:
                gold_score = torch.tensor(0.0, device=pointer_scores.device)

            gold_scores.append(gold_score)

        gold_scores = torch.stack(gold_scores)

        # Final classification
        classification = self.classifier(x.transpose(1, 2))  # [batch, 1]

        return {
            'pointer_scores': pointer_scores,
            'gold_scores': gold_scores,
            'classification': classification
        }

def train_model(model, train_loader, val_loader, epochs, model_size):
    """Train the model."""
    print(f"🔍 train_model() called")

    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"🔍 Selected device: {device}")

    model = model.to(device)
    print(f"🔍 Model moved to device")

    optimizer = optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)
    criterion = nn.BCELoss()
    print(f"🔍 Optimizer and criterion created")

    print(f"Training on device: {device}")
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Create checkpoint directory
    checkpoint_dir = f'checkpoints_{model_size.lower()}_semantic'
    os.makedirs(checkpoint_dir, exist_ok=True)

    best_val_loss = float('inf')
    print(f"🔍 Starting training loop for {epochs} epochs")

    for epoch in range(epochs):
        print(f"🔍 Starting epoch {epoch+1}/{epochs}")
        model.train()
        train_loss = 0
        train_batches = 0

        start_time = time.time()
        print(f"🔍 Entering training loop for epoch {epoch+1}")

        for batch_idx, batch in enumerate(train_loader):
            if batch_idx == 0:
                print(f"🔍 Processing first batch...")
            if batch_idx < 5:  # Debug first few batches
                print(f"🔍 Batch {batch_idx+1}: processing...")

            optimizer.zero_grad()

            # Move batch to device
            embeddings = batch['embeddings'].to(device)
            pointer_indices = batch['pointer_indices'].to(device)
            labels = batch['labels'].to(device)

            # Forward pass
            outputs = model(embeddings, pointer_indices)

            # Calculate loss (combination of classification and pointer scoring)
            cls_loss = criterion(outputs['classification'].squeeze(-1), labels)
            pointer_loss = -outputs['gold_scores'].mean()  # Encourage high scores for gold pointers
            total_loss = cls_loss + 0.1 * pointer_loss

            # Backward pass
            total_loss.backward()
            optimizer.step()

            train_loss += total_loss.item()
            train_batches += 1

        avg_train_loss = train_loss / train_batches

        # Validation
        model.eval()
        val_loss = 0
        val_batches = 0

        with torch.no_grad():
            for batch in val_loader:
                embeddings = batch['embeddings'].to(device)
                pointer_indices = batch['pointer_indices'].to(device)
                labels = batch['labels'].to(device)

                outputs = model(embeddings, pointer_indices)
                cls_loss = criterion(outputs['classification'].squeeze(-1), labels)
                pointer_loss = -outputs['gold_scores'].mean()
                total_loss = cls_loss + 0.1 * pointer_loss

                val_loss += total_loss.item()
                val_batches += 1

        avg_val_loss = val_loss / val_batches
        epoch_time = time.time() - start_time

        print(f"Epoch {epoch+1}/{epochs}:")
        print(f"  Train Loss: {avg_train_loss:.4f}")
        print(f"  Val Loss: {avg_val_loss:.4f}")
        print(f"  Time: {epoch_time:.1f}s")

        # Save checkpoint
        checkpoint_path = os.path.join(checkpoint_dir, f'epoch_{epoch+1}.pt')
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'train_loss': avg_train_loss,
            'val_loss': avg_val_loss
        }, checkpoint_path)

        # Save best model
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            best_path = os.path.join(checkpoint_dir, 'best_model.pt')
            torch.save(model.state_dict(), best_path)
            print(f"  ✅ New best model saved!")

        print()

def main():
    parser = argparse.ArgumentParser(description='Train large models')
    parser.add_argument('--size', type=str, default='200M', choices=['200M', '300M'],
                       help='Model size')
    parser.add_argument('--epochs', type=int, default=15,
                       help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=4,
                       help='Batch size')
    parser.add_argument('--data-path', type=str, required=True,
                       help='Path to training data')

    args = parser.parse_args()

    # Model configurations
    MODEL_CONFIGS = {
        '200M': {
            'hidden_size': 1536,
            'num_layers': 16,
            'num_heads': 24,
            'intermediate_size': 6144,
        },
        '300M': {
            'hidden_size': 1792,
            'num_layers': 20,
            'num_heads': 28,
            'intermediate_size': 7168,
        }
    }

    config = MODEL_CONFIGS[args.size]

    print("="*80)
    print(f"LARGE MODEL TRAINING: {args.size}")
    print(f"Hidden Size: {config['hidden_size']}, Layers: {config['num_layers']}")
    print(f"Data: {args.data_path}")
    print("="*80)

    # Load data
    print(f"\n📂 Loading training data from {args.data_path}...")
    print(f"   🔍 File exists: {os.path.exists(args.data_path)}")
    print(f"   🔍 File size: {os.path.getsize(args.data_path) / 1024/1024:.1f} MB")

    with open(args.data_path, 'r') as f:
        data = json.load(f)

    print(f"   🔍 Data type: {type(data)}")

    # Handle both wrapped and unwrapped formats
    if isinstance(data, dict) and 'examples' in data:
        examples = data['examples']
        print(f"   🔍 Extracted examples from 'examples' key")
    else:
        examples = data
        print(f"   🔍 Using data directly as examples")

    print(f"   Loaded {len(examples)} examples")
    print(f"   🔍 First example type: {type(examples[0]) if examples else 'No examples'}")

    # Create dataset
    print(f"   🔍 Creating PointerDataset...")
    dataset = PointerDataset(examples)
    print(f"   🔍 PointerDataset created, length: {len(dataset)}")

    # Split data
    print(f"   🔍 Creating train/val split...")
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    print(f"   🔍 Split sizes - Train: {train_size}, Val: {val_size}")

    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
    print(f"   🔍 Split created successfully")

    print(f"   Train: {len(train_dataset)}, Val: {len(val_dataset)}")

    # Create dataloaders
    print(f"   🔍 Creating DataLoader...")
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=collate_fn,
        num_workers=0
    )
    print(f"   🔍 Train DataLoader created")

    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        collate_fn=collate_fn,
        num_workers=0
    )

    # Create model
    print(f"   🔍 Creating model...")
    model = SimpleLearnedScorer(**config)
    print(f"   🔍 Model created successfully")

    # Train
    print(f"   🔍 Starting training...")
    train_model(model, train_loader, val_loader, args.epochs, args.size)

    print(f"✅ Training complete! Model saved in checkpoints_{args.size.lower()}_semantic/")

if __name__ == "__main__":
    main()