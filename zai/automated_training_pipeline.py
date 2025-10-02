"""
Automated Training Pipeline for Large Models
Continues training with different configurations when previous models finish
"""

import os
import time
import subprocess
import json
from datetime import datetime

def monitor_and_retrain():
    """Monitor running processes and start new training when they complete."""

    print("="*80)
    print("🚀 AUTOMATED TRAINING PIPELINE")
    print("Monitoring progress and launching new training jobs")
    print("="*80)

    # Configurations to train
    configs = [
        {"size": "200M", "data": "pointer_training_data_semantic_5000.json", "batch": 6},
        {"size": "200M", "data": "pointer_training_data_semantic_10000.json", "batch": 4},
        {"size": "300M", "data": "pointer_training_data_semantic_10000.json", "batch": 3},
        {"size": "300M", "data": "pointer_training_data_semantic_20000.json", "batch": 2},
    ]

    completed_training = set()

    while True:
        print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Checking training status...")

        # Check current processes
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        running_training = []

        for line in result.stdout.split('\n'):
            if 'train_simple_large.py' in line and 'grep' not in line:
                # Extract model size from command line
                if '--size 200M' in line:
                    running_training.append('200M')
                elif '--size 300M' in line:
                    running_training.append('300M')

        print(f"   Currently training: {running_training}")

        # Check for new completed models
        for size in ['200M', '300M']:
            if size not in running_training and size not in completed_training:
                print(f"   ✅ {size} model training completed!")
                completed_training.add(size)

                # Start next configuration for this size if available
                remaining_configs = [c for c in configs if c["size"] == size]
                for config in remaining_configs:
                    print(f"   🚀 Starting additional {size} training with {config['data']}")

                    cmd = [
                        'python3', 'train_simple_large.py',
                        '--size', config['size'],
                        '--epochs', '15',
                        '--batch-size', str(config['batch']),
                        '--data-path', config['data']
                    ]

                    subprocess.Popen(cmd,
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)

                    time.sleep(30)  # Wait between starts

        # Check for checkpoint directories
        checkpoint_dirs = []
        for item in os.listdir('.'):
            if item.startswith('checkpoints_') and os.path.isdir(item):
                checkpoint_dirs.append(item)

        if checkpoint_dirs:
            print(f"   📁 Checkpoint directories: {len(checkpoint_dirs)}")

            # Report latest checkpoints
            latest_checkpoints = {}
            for cp_dir in checkpoint_dirs:
                if os.path.exists(cp_dir):
                    files = [f for f in os.listdir(cp_dir) if f.endswith('.pt')]
                    if files:
                        latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(cp_dir, x)))
                        latest_checkpoints[cp_dir] = latest_file

            for cp_dir, latest_file in latest_checkpoints.items():
                print(f"      {cp_dir}: {latest_file}")

        # Report memory usage
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            python_processes = [line for line in result.stdout.split('\n')
                              if 'python3' in line and 'grep' not in line]

            total_memory = 0
            for proc in python_processes:
                parts = proc.split()
                if len(parts) > 5:
                    try:
                        memory_mb = float(parts[5]) / 1024
                        total_memory += memory_mb
                    except:
                        pass

            print(f"   💾 Total Python memory usage: {total_memory:.1f} GB")

        except Exception as e:
            print(f"   ⚠️  Memory check failed: {e}")

        # Check if all training is complete
        if len(completed_training) >= 2 and len(running_training) == 0:
            print("\n🎉 ALL TRAINING COMPLETE!")
            print(f"   Completed models: {list(completed_training)}")

            # Create final summary
            summary = {
                "completion_time": datetime.now().isoformat(),
                "completed_models": list(completed_training),
                "checkpoint_directories": checkpoint_dirs,
                "total_configs_planned": len(configs)
            }

            with open(f'training_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
                json.dump(summary, f, indent=2)

            print("   📊 Training summary saved!")
            break

        # Wait before next check
        print("   ⏳ Waiting 60 seconds...")
        time.sleep(60)

if __name__ == "__main__":
    monitor_and_retrain()