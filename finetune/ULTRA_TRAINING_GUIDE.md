# Ultra Training Guide - Option A Implementation

**Status**: ✅ Ready to Execute
**Target**: 10,000 documents, 5 epochs with early stopping
**Estimated Time**: 30 hours on Mac M2
**Expected Improvement**: +15-25% quality

---

## Quick Start

```bash
# Step 1: Generate ultra-enhanced corpus (2-3 hours)
python3 ultra_enhanced_corpus_generator.py

# Step 2: Run training (30 hours)
python3 ultra_production_training_mac.py > ultra_training_output.log 2>&1 &

# Step 3: Monitor progress
tail -f ultra_training_output.log

# Step 4: Check completion
cat models/ultra_narrative_mac/training_results.json
```

---

## Phase 1: Corpus Generation (2-3 hours)

### What It Does
Generates 20,000 candidate documents and filters to top 10,000 based on quality.

### Command
```bash
python3 ultra_enhanced_corpus_generator.py
```

### Output
- `experiments/ultra_corpus_TIMESTAMP/training_data.json` (10,000 documents)
- `experiments/ultra_corpus_TIMESTAMP/metadata.json` (statistics)

### Expected Statistics
```
Documents Generated: 20,000
Documents Kept: 10,000
Average Quality: 0.90-0.95
Average Length: 350-450 words
Total Cross-References: 50,000-80,000
Refs per Document: 5-8
```

### What's Enhanced vs Previous Corpus

| Aspect | Previous (2K) | Ultra (10K) | Improvement |
|--------|---------------|-------------|-------------|
| **Documents** | 2,000 | 10,000 | 5x |
| **Quality Filter** | None | Top 50% from 20K | Much higher |
| **Avg Length** | 233 words | 350-450 words | 1.7x longer |
| **Characters** | 10 | 20 | 2x |
| **Factions** | 4 | 8 | 2x |
| **Locations** | 8 | 50 | 6x |
| **Document Types** | 7 | 10 | Added 3 new |
| **Writing Styles** | 1 | 5 per type | Massive diversity |
| **Conflicts** | 5 | 15 | 3x |
| **Cross-refs/doc** | 3.0 | 5-8 | 2x denser |

---

## Phase 2: Production Training (30 hours)

### What It Does
Trains Qwen-1.5B on 10,000 documents for up to 5 epochs with automatic early stopping.

### Command
```bash
# Run in background
python3 ultra_production_training_mac.py > ultra_training_output.log 2>&1 &

# Get process ID for monitoring
echo $!
```

### Monitoring Commands
```bash
# View live progress
tail -f ultra_training_output.log

# Check if still running
ps aux | grep ultra_production_training_mac

# Monitor GPU usage
sudo powermetrics --samplers gpu_power -i1000

# Check disk space (models can be large)
df -h .
```

### Training Configuration
```
Model: Qwen-1.5B (1.545B parameters)
Training Documents: 9,500 (500 for eval)
Epochs: Up to 5 (stops early if overfitting)
Batch Size: 1 (effective 8 with gradient accumulation)
Learning Rate: 2e-4
LoRA Rank: 8, Alpha: 16
Steps per Epoch: ~1,188
Total Possible Steps: 5,940 (if all 5 epochs)
Checkpoint Frequency: Every epoch

Early Stopping:
- Patience: 2 epochs
- Metric: Evaluation loss
- Action: Stop if eval loss increases for 2 consecutive epochs
- Saves: Best model automatically
```

### Expected Timeline
```
Epoch 1: ~6 hours
Epoch 2: ~6 hours
Epoch 3: ~6 hours
Epoch 4: ~6 hours (may stop here)
Epoch 5: ~6 hours (if still improving)

Total: 18-30 hours depending on early stopping
```

### Checkpoints Created
```
models/ultra_narrative_mac/checkpoints/
├── checkpoint-1188/  (after epoch 1)
├── checkpoint-2376/  (after epoch 2)
├── checkpoint-3564/  (after epoch 3)
├── checkpoint-4752/  (after epoch 4)
└── checkpoint-5940/  (after epoch 5 - if reached)

Plus final model in main directory
```

### What to Expect

**Epoch 1**:
- Training loss: Should decrease from ~30 to ~15
- Eval loss: Should decrease from ~30 to ~15
- Model learning basic patterns

**Epoch 2**:
- Training loss: ~15 to ~8
- Eval loss: ~15 to ~8
- Model learning narrative structure

**Epoch 3**:
- Training loss: ~8 to ~5
- Eval loss: ~8 to ~5
- Model learning cross-document coherence

**Epoch 4**:
- Training loss: ~5 to ~3
- Eval loss: May start plateauing or increasing
- **Early stopping may trigger here**

**Epoch 5**:
- Only reached if eval loss still improving
- Training loss: ~3 to ~2
- Eval loss: Should be lowest point

### Early Stopping Detection
```
✅ New best eval loss: 5.234 (epoch 3)
⚠️ No improvement for 1 epoch(s)
⚠️ No improvement for 2 epoch(s)
🛑 Early stopping triggered after 5 epochs
   Best eval loss: 5.234 (epoch 3)
```

If this happens, the system automatically:
1. Stops training
2. Uses the best checkpoint (epoch 3 in this example)
3. Saves final model
4. Generates evaluation report

---

## Phase 3: Evaluation & Comparison

### Automatic Outputs
After training completes, you'll have:

```
models/ultra_narrative_mac/
├── checkpoints/           (all epoch checkpoints)
├── best_models/           (best model by metric)
├── evaluation_results/    (eval scores)
├── training_logs/         (tensorboard logs)
├── training_results.json  (final metrics)
└── sample_outputs.json    (generated examples)
```

### Manual Comparison (Recommended)
Run comprehensive comparison against previous models:

```bash
# Compare ultra model vs base
python3 compare_base_vs_ultra.py

# This will generate:
# - ultra_comparison_results.json
# - ULTRA_COMPARISON_REPORT.md
```

### Expected Results (Based on Research)

| Configuration | Documents | Epochs | Time | Expected Improvement |
|--------------|-----------|--------|------|---------------------|
| Previous | 2,000 | 3 | 6h | +2.7% (actual) |
| **Ultra (Option A)** | **10,000** | **3-5** | **30h** | **+15-25%** ⭐ |

**Why this improvement**:
1. **5x more documents** → Better generalization
2. **2x longer documents** → Deeper narrative learning
3. **Quality filtering** → Higher baseline (>0.90 vs 0.876)
4. **5 writing styles** → Better style adaptation
5. **More complex world** → Richer relationships
6. **Optimal epochs** → Sweet spot before overfitting

---

## Troubleshooting

### Issue: "No corpus found"
**Solution**: Run corpus generator first
```bash
python3 ultra_enhanced_corpus_generator.py
```

### Issue: Training stops unexpectedly
**Check**:
```bash
# View error
tail -100 ultra_training_output.log

# Check disk space
df -h .

# Check memory
top -l 1 | grep PhysMem
```

### Issue: Out of memory
**Solution**: System is already optimized for Mac M2. If still failing:
1. Reduce `max_sequence_length` from 1024 to 512
2. Ensure no other heavy processes running
3. Restart Mac to clear memory

### Issue: Training very slow
**Expected**: ~15 seconds per step
**If slower**:
1. Check if other apps using GPU
2. Verify MPS is being used (should show in logs)
3. Consider overnight training

### Issue: Eval loss increasing early
**This is normal!** Early stopping will handle it.
- Epoch 1-2: Should decrease
- Epoch 3: May plateau
- Epoch 4-5: May increase → triggers early stop

---

## After Training: Next Steps

### 1. Verify Training Success
```bash
# Check if model files exist
ls -lh models/ultra_narrative_mac/checkpoints/

# View training results
cat models/ultra_narrative_mac/training_results.json

# Check sample outputs
cat models/ultra_narrative_mac/sample_outputs.json
```

### 2. Compare with Previous Model
```python
from compare_base_vs_finetuned import ModelComparison

# Compare ultra vs previous fine-tuned
comparator = ModelComparison(
    base_model_path="./models/production_narrative_mac/checkpoints",
    finetuned_model_path="./models/ultra_narrative_mac/checkpoints"
)

results = comparator.run_comparison()
```

### 3. Test Interactive Generation
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Load model
base_model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-1.5B",
    trust_remote_code=True,
    torch_dtype=torch.float16
)

model = PeftModel.from_pretrained(
    base_model,
    "./models/ultra_narrative_mac/checkpoints"
)

tokenizer = AutoTokenizer.from_pretrained(
    "./models/ultra_narrative_mac/checkpoints"
)

# Generate
prompt = "<|prophecy|>\\nSpoken by: Prophet Iris\\nDate: Year 1254\\n\\n"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=300)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### 4. Deploy to Production
If results are good, merge LoRA adapters:
```python
# Merge for faster inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("./models/ultra_narrative_merged")
tokenizer.save_pretrained("./models/ultra_narrative_merged")
```

---

## Success Criteria

✅ **Training Complete When**:
- All epochs finished OR early stopping triggered
- `training_results.json` exists
- Sample outputs generated successfully
- No errors in log file

✅ **Good Results When**:
- Training loss < 5.0
- Eval loss < 6.0
- Sample outputs are coherent and on-topic
- Quality improvement > +10% vs previous model

✅ **Ready for Next Iteration When**:
- Achieved +15-25% improvement
- Want to try Option B (20K documents)
- Want to experiment with different hyperparameters

---

## Comparison: Previous vs Ultra

### Quantitative Expectations

| Metric | Previous (2K docs, 3 epochs) | Ultra (10K docs, 5 epochs) |
|--------|------------------------------|---------------------------|
| Training Loss | 27.38 | 2-5 (estimate) |
| Eval Loss | ~28 | 3-6 (estimate) |
| Quality Improvement | +2.7% | +15-25% (target) |
| Training Time | 6 hours | 30 hours |
| Coherence Score | 0.904 | 0.95-1.00 (target) |

### Qualitative Expectations

**Previous Model**:
- Good at formal documents (letters +21%)
- Struggles with some types (diary -5%)
- Limited narrative depth
- Some repetition

**Ultra Model (Expected)**:
- Excellent across all document types
- Rich, varied narratives
- Strong cross-document coherence
- Minimal repetition
- Better style adaptation

---

## Files Created

### Implementation Files
- `ultra_enhanced_corpus_generator.py` (corpus generation)
- `ultra_production_training_mac.py` (training script)
- `ULTRA_TRAINING_GUIDE.md` (this guide)

### Output Files (After Execution)
- `experiments/ultra_corpus_*/training_data.json` (10K documents)
- `models/ultra_narrative_mac/` (trained model + checkpoints)
- `ultra_training_output.log` (complete training log)

---

## Ready to Start?

```bash
# Full pipeline (can run in background):
# 1. Generate corpus
python3 ultra_enhanced_corpus_generator.py

# 2. Start training (30 hours)
python3 ultra_production_training_mac.py > ultra_training_output.log 2>&1 &

# 3. Monitor
tail -f ultra_training_output.log

# 4. Wait for completion
# Check back in ~30 hours or when you see "ULTRA TRAINING COMPLETE!"
```

---

**Last Updated**: September 30, 2025
**Status**: ✅ Implementation Complete, Ready for Execution