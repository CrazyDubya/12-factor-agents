# Lambda.ai Cloud Training Deployment Guide

## Quick Comparison: A10 vs A100

| Feature | A10 (24GB) | A100 (90GB) |
|---------|------------|-------------|
| **Cost** | $0.75/hr | $1.49/hr |
| **Training Time** | 4-6 hours | 2-3 hours |
| **Total Cost** | $3-4.50 | $3-4.50 |
| **Batch Size** | 2 (limited by VRAM) | 4 (more efficient) |
| **LoRA Rank** | 8 (memory-constrained) | 16 (higher quality) |
| **Quantization** | Required (4-bit) | Recommended (4-bit) |
| **Precision** | FP16 | BFloat16 (better) |
| **Recommendation** | **BEST VALUE** - Same cost, just slower | Faster if you need results sooner |

**Bottom Line:** A10 is the better choice unless you need results in 2 hours instead of 5 hours. Both cost approximately the same (~$3-4.50).

---

## Step-by-Step Deployment

### 1. Create Lambda.ai Account & Launch Instance

1. Go to https://lambda.ai/service/gpu-cloud
2. Create account and add payment method
3. Launch new instance:
   - **For A10**: Select "1x A10 (24GB)" - $0.75/hr
   - **For A100**: Select "1x A100 (90GB SXM)" - $1.49/hr
4. Choose Ubuntu 20.04/22.04 with PyTorch pre-installed
5. Launch and wait for instance to start (~2 minutes)

### 2. Upload Training Files to Lambda Instance

From your Mac terminal:

```bash
# Package the corpus and training code
cd /Users/pup/finetune
tar -czf lambda_training_package.tar.gz \
    experiments/ultra_corpus_1759240479/ \
    finetune/ \
    lambda_a10_training.py \
    lambda_cloud_training.py

# Upload to Lambda (replace <LAMBDA_IP> with your instance IP)
scp lambda_training_package.tar.gz ubuntu@<LAMBDA_IP>:~/
```

**Lambda will provide the IP address** in the instance dashboard.

### 3. SSH into Lambda Instance

```bash
# SSH into your Lambda instance
ssh ubuntu@<LAMBDA_IP>

# Extract the package
tar -xzf lambda_training_package.tar.gz
cd ~
```

### 4. Install Dependencies

```bash
# Install required packages (Lambda has PyTorch pre-installed)
pip install transformers==4.36.0
pip install peft==0.7.1
pip install datasets==2.16.1
pip install accelerate==0.25.0
pip install bitsandbytes==0.41.3
pip install sentencepiece==0.1.99
pip install protobuf==4.25.1
pip install rich==13.7.0
pip install flash-attn==2.5.0 --no-build-isolation

# Verify GPU
nvidia-smi
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### 5. Start Training

**For A10 (Recommended - $0.75/hr):**
```bash
# Start training in tmux (so it continues if you disconnect)
tmux new -s training
python3 lambda_a10_training.py 2>&1 | tee a10_training.log

# Detach from tmux: Ctrl+B, then D
# Reattach later: tmux attach -t training
```

**For A100 ($1.49/hr):**
```bash
tmux new -s training
python3 lambda_cloud_training.py 2>&1 | tee a100_training.log
```

### 6. Monitor Training Progress

```bash
# If you detached from tmux, reattach:
tmux attach -t training

# Or monitor the log file:
tail -f a10_training.log  # or a100_training.log

# Check GPU usage:
watch -n 1 nvidia-smi
```

**Expected Timeline (A10):**
- Model loading: ~2-5 minutes
- Training start: ~1 minute
- First checkpoint (1250 steps): ~60-90 minutes
- Total training: ~4-6 hours

**Expected Timeline (A100):**
- Model loading: ~2-5 minutes
- Training start: ~1 minute
- First checkpoint (1250 steps): ~30-45 minutes
- Total training: ~2-3 hours

### 7. Download Trained Model

After training completes:

```bash
# On Lambda instance, compress the trained model
cd ~
tar -czf trained_model.tar.gz models/ultra_narrative_a10/  # or ultra_narrative_cloud

# From your Mac, download the model
scp ubuntu@<LAMBDA_IP>:~/trained_model.tar.gz ~/finetune/
cd ~/finetune
tar -xzf trained_model.tar.gz
```

### 8. Terminate Lambda Instance

**IMPORTANT:** Terminate the instance when done to stop billing!

1. Go to Lambda.ai dashboard
2. Find your running instance
3. Click "Terminate"
4. Confirm termination

---

## Cost Breakdown

### A10 Training ($0.75/hr):
```
Model loading & setup:  5 min = $0.06
Training (5 epochs):    5 hr  = $3.75
Evaluation & samples:   15 min = $0.19
Total:                  ~5.25hr = $3.94
```

### A100 Training ($1.49/hr):
```
Model loading & setup:  5 min = $0.12
Training (5 epochs):    2.5 hr = $3.73
Evaluation & samples:   10 min = $0.25
Total:                  ~2.75hr = $4.10
```

**Recommendation:** Use A10 unless you need results urgently. Cost is nearly identical.

---

## Troubleshooting

### Out of Memory Error
```bash
# If A10 runs out of memory, reduce batch size:
# Edit lambda_a10_training.py, change:
"per_device_train_batch_size": 1,  # from 2
"gradient_accumulation_steps": 16,  # from 8
```

### Connection Lost
```bash
# Training continues in tmux! Just reconnect:
ssh ubuntu@<LAMBDA_IP>
tmux attach -t training
```

### Training Crashed
```bash
# Check the log:
tail -100 a10_training.log

# Resume from last checkpoint:
python3 lambda_a10_training.py --resume models/ultra_narrative_a10/checkpoints/checkpoint-1250
```

---

## Files Included

1. **lambda_a10_training.py** - A10-optimized training script ($0.75/hr)
2. **lambda_cloud_training.py** - A100-optimized training script ($1.49/hr)
3. **experiments/ultra_corpus_1759240479/** - 10K document training corpus
4. **finetune/** - Complete training framework

---

## Expected Results

Based on Option A configuration (10K docs, 5 epochs):

- **Training Loss:** Expected final loss ~0.5-0.8 (down from initial ~3.8)
- **Improvement:** Target +15-25% over baseline (vs previous +2.7%)
- **Quality:** Higher coherence, better world consistency, richer narratives

---

## Next Steps After Training

1. **Test the model:**
   ```bash
   cd ~/finetune
   python3 -c "
   from transformers import AutoTokenizer, AutoModelForCausalLM
   from peft import PeftModel

   model = AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-1.5B')
   model = PeftModel.from_pretrained(model, 'models/ultra_narrative_a10')
   tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen2.5-1.5B')

   prompt = '<|chronicle|>\nTitle: The Discovery\nDate: Year 1250\n\n'
   inputs = tokenizer(prompt, return_tensors='pt')
   outputs = model.generate(**inputs, max_new_tokens=200)
   print(tokenizer.decode(outputs[0]))
   "
   ```

2. **Compare vs baseline:** Run evaluation script comparing base model vs fine-tuned

3. **Deploy:** Merge LoRA adapters for production use

---

## Support

- Lambda.ai Docs: https://docs.lambda.ai/
- Lambda Support: support@lambda.ai
- Instance Issues: Check Lambda dashboard for status
