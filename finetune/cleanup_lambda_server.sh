#!/bin/bash
# Lambda Server Cleanup Script
# Removes unnecessary files, keeps only final model weights

SERVER="ubuntu@YOUR_SERVER_IP"
KEY="~/.ssh/id_rsa_lambda"

echo "🧹 Cleaning up Lambda server..."
echo "Keeping: Final model weights only"
echo "Removing: Old checkpoints, training cache, logs"
echo

# Connect and cleanup
ssh -i $KEY $SERVER << 'REMOTE_EOF'

cd ~/finetune_project/models/ultra_narrative_a10

echo "📊 Current disk usage:"
du -sh .
echo

# Keep only the final checkpoint and best model
echo "🗑️  Removing intermediate checkpoints..."

# Remove old checkpoints (keep only checkpoint-5940 - the final one)
rm -rf checkpoints/checkpoint-1250
rm -rf checkpoints/checkpoint-2500  
rm -rf checkpoints/checkpoint-3750
rm -rf checkpoints/checkpoint-5000

# Remove optimizer states and training artifacts from final checkpoint
cd checkpoints/checkpoint-5940
rm -f optimizer.pt scheduler.pt rng_state.pth trainer_state.json training_args.bin

cd ../..

# Remove training logs (already downloaded locally)
rm -rf training_logs/*

# Remove evaluation temp files
rm -rf evaluation_results/*.tmp

echo
echo "✅ Cleanup complete!"
echo
echo "📊 New disk usage:"
du -sh .
echo

echo "📁 Remaining files:"
find . -type f -name "*.safetensors" -o -name "*.json" -o -name "*.txt" | head -20

REMOTE_EOF

echo
echo "🎉 Server cleaned! Only final model weights remain."
