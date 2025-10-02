# Local Inference Testing Guide

## Overview
Test your A10 fine-tuned narrative model locally on Apple Silicon (MPS) or CPU.

**Model**: Qwen-1.5B + LoRA adapters
**Training**: 10,000 documents, 5 epochs, 8.84 hours on A10
**Final Loss**: 0.2524 (training), 0.1613 (eval)
**Location**: `models/ultra_narrative_a10/`

---

## 📋 Available Test Scripts

### 1. **test_local_inference.py** - Quick Test (Recommended First)
**Purpose**: Fast sanity check with 3 narrative types

**Usage**:
```bash
python test_local_inference.py
```

**What it does**:
- Tests 3 document types (chronicle, prophecy, treaty)
- Generates 300 tokens per sample
- Shows generation speed and quality
- Saves results to `test_outputs/inference_test_*.json`

**Time**: ~2-5 minutes (depends on device)

---

### 2. **test_all_checkpoints.py** - Training Progression
**Purpose**: Compare all 5 checkpoints to see learning progression

**Usage**:
```bash
python test_all_checkpoints.py
```

**What it does**:
- Tests same prompt across all 5 checkpoints
- Shows how model improved during training
- Checkpoint-1250 (early) vs checkpoint-5940 (final)
- Generates comparison report (JSON + TXT)

**Time**: ~10-15 minutes (loads 5 models sequentially)

**Output**:
- `test_outputs/checkpoint_comparison/checkpoint_comparison_*.json`
- `test_outputs/checkpoint_comparison/checkpoint_comparison_*.txt`

---

### 3. **batch_test_narratives.py** - Comprehensive Evaluation
**Purpose**: Test all 10 document types with multiple samples each

**Usage**:
```bash
python batch_test_narratives.py
```

**What it does**:
- Tests all 10 narrative types from training corpus
- 3 samples per type = 30 total generations
- Creates beautiful HTML report
- Full JSON data for analysis

**Time**: ~15-20 minutes

**Output**:
- `test_outputs/batch_narratives/batch_narratives_*.json`
- `test_outputs/batch_narratives/batch_narratives_*.html` ← **Open this in browser!**

**Document Types Tested**:
1. Chronicle (historical records)
2. Prophecy (future predictions)
3. Treaty (formal agreements)
4. Letter (correspondence)
5. Journal (personal entries)
6. Report (official reports)
7. Decree (official proclamations)
8. Speech (public addresses)
9. Legend (ancient stories)
10. Ritual (ceremonial procedures)

---

## 🚀 Quick Start

**First-time setup** (if needed):
```bash
# Install requirements (if not already installed)
pip install torch transformers peft rich

# Verify model files are present
ls -lh models/ultra_narrative_a10/checkpoints/checkpoint-5940/
```

**Run your first test**:
```bash
# Quick test (3 samples, ~3 minutes)
python test_local_inference.py
```

---

## 📊 Understanding Results

### Generation Quality Indicators
- **Coherence**: Does the text follow narrative structure?
- **Format Compliance**: Does it use proper tags (`<|chronicle|>`, etc.)?
- **Consistency**: Are names, places, dates consistent?
- **Creativity**: Does it generate unique, interesting content?

### Performance Metrics
- **Tokens/Second**:
  - CPU: 2-5 tokens/sec (slow but works)
  - MPS (Apple Silicon): 10-20 tokens/sec (good)
  - CUDA (NVIDIA): 30-50 tokens/sec (fast)

### Example Good Output
```
<|chronicle|>
Title: The Battle of Shadow's Edge
Date: Year 1262
Location: Shadow's Edge Canyon

The armies clashed at dawn, as the ancient prophecy had foretold.
General Marcus led the Crystal Spire forces through the narrow pass,
while Commander Thane positioned archers on the canyon walls...

[Coherent narrative continues with consistent characters, dates, places]

<|end_chronicle|>
```

---

## 🔧 Customization

### Adjust Generation Parameters

Edit the `generate_text()` function in any script:

```python
outputs = model.generate(
    **inputs,
    max_new_tokens=300,      # Increase for longer text
    temperature=0.8,         # 0.7-0.9 for creativity
    top_p=0.9,               # Nucleus sampling
    do_sample=True,          # Enable sampling
)
```

**Temperature Guide**:
- `0.7`: More focused, consistent
- `0.8`: Balanced (default)
- `0.9`: More creative, varied
- `1.0`: Very creative (may lose coherence)

### Test Your Own Prompts

Add custom prompts to any script:

```python
custom_prompt = """<|chronicle|>
Title: Your Custom Title
Date: Year 1275
Location: Your Location

Your starting text here..."""

result = generate_text(model, tokenizer, custom_prompt, device)
```

---

## 📈 What to Look For

### Early Checkpoints (1250-2500)
- Basic structure learning
- Some format compliance
- May have inconsistencies
- Shorter, simpler narratives

### Middle Checkpoints (3750-5000)
- Improved coherence
- Better format compliance
- Consistent character/place names
- Longer, more detailed text

### Final Checkpoint (5940)
- Best coherence and consistency
- Strong format compliance
- Complex, engaging narratives
- Proper use of narrative tags

---

## 🐛 Troubleshooting

### "Out of Memory" Error
```bash
# Reduce batch size or max tokens
max_new_tokens=150  # Instead of 300
```

### "Model files not found"
```bash
# Verify download
ls -lh models/ultra_narrative_a10/checkpoints/checkpoint-5940/
# Should see adapter_model.safetensors (~8.3 MB)
```

### "Slow generation on CPU"
- Expected behavior (2-5 tokens/sec)
- Consider using smaller `max_new_tokens` for faster testing
- MPS (Apple Silicon) is 5-10x faster if available

### "Import errors"
```bash
pip install torch transformers peft rich
```

---

## 📁 Output Files

All test results are saved to organized directories:

```
test_outputs/
├── inference_test_checkpoint-5940_*.json    # Quick test results
├── checkpoint_comparison/
│   ├── checkpoint_comparison_*.json         # All checkpoints data
│   └── checkpoint_comparison_*.txt          # Readable text report
└── batch_narratives/
    ├── batch_narratives_*.json              # Full batch data
    └── batch_narratives_*.html              # Beautiful HTML report ⭐
```

---

## 🎯 Recommended Testing Workflow

1. **Quick validation** (3 minutes):
   ```bash
   python test_local_inference.py
   ```

2. **Review training progression** (15 minutes):
   ```bash
   python test_all_checkpoints.py
   ```

3. **Comprehensive evaluation** (20 minutes):
   ```bash
   python batch_test_narratives.py
   # Open the HTML file in your browser!
   ```

4. **Custom testing**:
   - Modify prompts in any script
   - Add your own narrative types
   - Experiment with generation parameters

---

## 💡 Tips for Best Results

1. **First run downloads base model** (~3GB Qwen-1.5B)
   - Subsequent runs are much faster
   - Model cached in `~/.cache/huggingface/`

2. **Use HTML reports** for easy review
   - `batch_narratives_*.html` is nicely formatted
   - Open in any browser

3. **Compare checkpoints** to see learning
   - Early vs final shows dramatic improvement
   - Useful for understanding training dynamics

4. **Save interesting outputs**
   - Results auto-saved with timestamps
   - JSON files for programmatic analysis

---

## 🎉 You're Ready!

Your model is trained and ready for local testing. Start with the quick test, then explore the other scripts to evaluate your fine-tuned narrative generator!

**Questions?** Review the code comments in each script for detailed explanations.
