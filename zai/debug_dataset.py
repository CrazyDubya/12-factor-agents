#!/usr/bin/env python3
"""
Debug script to identify the exact dataset loading issue
"""

import json
import sys
import os

def debug_dataset_loading(file_path):
    """Debug exactly what happens during dataset loading"""

    print(f"🔍 DEBUG: Analyzing dataset file: {file_path}")
    print(f"🔍 DEBUG: File exists: {os.path.exists(file_path)}")

    if not os.path.exists(file_path):
        print(f"❌ File does not exist!")
        return

    # Check file size
    file_size = os.path.getsize(file_path)
    print(f"🔍 DEBUG: File size: {file_size:,} bytes ({file_size/1024/1024/1024:.2f} GB)")

    # Try to load the JSON
    print(f"🔍 DEBUG: Loading JSON...")
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        print(f"✅ JSON loaded successfully")
    except Exception as e:
        print(f"❌ JSON loading failed: {e}")
        return

    print(f"🔍 DEBUG: Data type: {type(data)}")

    # Check structure
    if isinstance(data, dict):
        print(f"🔍 DEBUG: Data keys: {list(data.keys())}")
        if 'examples' in data:
            examples = data['examples']
            print(f"🔍 DEBUG: Examples from 'examples' key: {len(examples)}")
        else:
            print(f"❌ No 'examples' key found!")
            return
    elif isinstance(data, list):
        examples = data
        print(f"🔍 DEBUG: Examples as list: {len(examples)}")
    else:
        print(f"❌ Unexpected data type!")
        return

    # Check first few examples
    if examples:
        print(f"🔍 DEBUG: First example type: {type(examples[0])}")
        if isinstance(examples[0], dict):
            print(f"🔍 DEBUG: First example keys: {list(examples[0].keys())}")

            # Check segment_embeddings structure
            if 'segment_embeddings' in examples[0]:
                seg_emb = examples[0]['segment_embeddings']
                print(f"🔍 DEBUG: segment_embeddings type: {type(seg_emb)}")
                if isinstance(seg_emb, list):
                    print(f"🔍 DEBUG: segment_embeddings length: {len(seg_emb)}")
                    if seg_emb:
                        print(f"🔍 DEBUG: First segment embedding length: {len(seg_emb[0])}")

            # Check gold_pointers
            if 'gold_pointers' in examples[0]:
                pointers = examples[0]['gold_pointers']
                print(f"🔍 DEBUG: gold_pointers: {pointers}")

    # Simulate the train/val split
    print(f"\n🔍 DEBUG: Simulating train/val split...")
    train_size = int(0.8 * len(examples))
    val_size = len(examples) - train_size
    print(f"🔍 DEBUG: Train size: {train_size}, Val size: {val_size}")

    # This should match the training script output
    print(f"\n📊 SUMMARY:")
    print(f"   File: {file_path}")
    print(f"   Total examples: {len(examples)}")
    print(f"   Expected train: {train_size}")
    print(f"   Expected val: {val_size}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 debug_dataset.py <dataset_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    debug_dataset_loading(file_path)