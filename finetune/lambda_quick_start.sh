#!/bin/bash
# Lambda.ai Quick Start - Copy/paste commands after SSH

set -e

echo "===================================================="
echo "Lambda.ai Training Setup"
echo "===================================================="

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -q transformers==4.36.0 peft==0.7.1 datasets==2.16.1 \
    accelerate==0.25.0 bitsandbytes==0.41.3 sentencepiece==0.1.99 \
    protobuf==4.25.1 rich==13.7.0

# Install flash-attention (can take 5-10 minutes)
echo ""
echo "⚡ Installing flash-attention (this takes 5-10 minutes)..."
pip install -q flash-attn==2.5.0 --no-build-isolation

# Verify GPU
echo ""
echo "🎮 Checking GPU..."
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

echo ""
python3 -c "import torch; print(f'✅ CUDA available: {torch.cuda.is_available()}')"
python3 -c "import torch; print(f'✅ GPU count: {torch.cuda.device_count()}')"
python3 -c "import torch; print(f'✅ GPU name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

echo ""
echo "===================================================="
echo "✅ Setup complete!"
echo "===================================================="
echo ""
echo "Next steps:"
echo "1. Start training with:"
echo "   tmux new -s training"
echo "   python3 lambda_a10_training.py 2>&1 | tee training.log"
echo ""
echo "2. Detach from tmux: Ctrl+B, then D"
echo "3. Reattach later: tmux attach -t training"
echo "4. Monitor progress: tail -f training.log"
echo ""
echo "Estimated time: 4-6 hours on A10, 2-3 hours on A100"
echo "===================================================="
