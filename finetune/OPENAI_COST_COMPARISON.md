# OpenAI API Cost Comparison vs Fine-Tuned Model (2025)

## Current OpenAI API Pricing (2025)

### GPT-4o (Most Powerful)
- **Input**: $2.50 per 1M tokens
- **Output**: $10.00 per 1M tokens
- **8K generation**: $0.02 input + $0.08 output = **$0.10 per story**

### GPT-4o-mini (Budget Option)
- **Input**: $0.15 per 1M tokens  
- **Output**: $0.60 per 1M tokens
- **8K generation**: $0.0012 input + $0.0048 output = **$0.006 per story**

### GPT-5 (Latest, Most Capable)
- **Input**: $1.25 per 1M tokens
- **Output**: $10.00 per 1M tokens
- **8K generation**: $0.01 input + $0.08 output = **$0.09 per story**
- **With caching**: ~$0.08 per story (cached inputs)

### GPT-5 Mini
- **Input**: $0.25 per 1M tokens
- **Output**: $2.00 per 1M tokens
- **8K generation**: $0.002 input + $0.016 output = **$0.018 per story**

---

## Your Fine-Tuned Model Costs

### One-Time Training Cost
- **A100 40GB**: ~$34 (26 hours @ $1.29/hr)
- **Result**: Unlimited 8K token generations

### Per-Generation Cost (Local Inference)
- **Electricity**: ~$0.0001 per generation (negligible)
- **Amortized**: $0 after break-even point

---

## Break-Even Analysis

### vs GPT-4o ($0.10 per 8K story)
- **Break-even**: 340 stories
- **After 340 stories**: You're saving money
- **After 1,000 stories**: Saved $66 ($100 - $34)
- **After 10,000 stories**: Saved $966 ($1,000 - $34)

### vs GPT-4o-mini ($0.006 per 8K story)
- **Break-even**: 5,667 stories
- **After 10,000 stories**: Saved $26 ($60 - $34)
- **After 100,000 stories**: Saved $566 ($600 - $34)

### vs GPT-5 ($0.09 per 8K story)
- **Break-even**: 378 stories
- **After 1,000 stories**: Saved $56 ($90 - $34)
- **After 10,000 stories**: Saved $866 ($900 - $34)

### vs GPT-5 Mini ($0.018 per 8K story)
- **Break-even**: 1,889 stories
- **After 10,000 stories**: Saved $146 ($180 - $34)
- **After 100,000 stories**: Saved $1,766 ($1,800 - $34)

---

## Use Case Analysis

### Scenario 1: Casual Use (100 stories/year)
**Winner**: GPT-4o-mini API
- Your cost: $34 + electricity
- GPT-4o-mini: $0.60/year
- **Verdict**: Not worth training for casual use

### Scenario 2: Regular Use (1,000 stories/year)
**Winner**: Your Fine-Tuned Model ✅
- Your cost: $34 one-time
- GPT-4o: $100/year
- GPT-5: $90/year
- GPT-5 Mini: $18/year
- **Savings**: $56-66/year vs premium models
- **Break-even**: 4-5 months vs GPT-4o/GPT-5

### Scenario 3: Heavy Use (10,000 stories/year)
**Winner**: Your Fine-Tuned Model ✅✅
- Your cost: $34 one-time
- GPT-4o: $1,000/year
- GPT-5: $900/year
- GPT-5 Mini: $180/year
- GPT-4o-mini: $60/year
- **Savings**: $146-966/year
- **ROI**: 2850% on GPT-4o, 429% on GPT-5 Mini

### Scenario 4: Commercial Use (100,000 stories/year)
**Winner**: Your Fine-Tuned Model ✅✅✅
- Your cost: $34 one-time
- GPT-4o: $10,000/year
- GPT-5: $9,000/year
- GPT-5 Mini: $1,800/year
- GPT-4o-mini: $600/year
- **Savings**: $566-9,966/year
- **ROI**: 29,300% on GPT-4o, 1,664% on GPT-4o-mini

---

## Quality Comparison

### Your Fine-Tuned 8K Model
- ✅ **Specialized**: Trained on your exact narrative style
- ✅ **Consistent**: Uses your world-building entities
- ✅ **Format**: 100% compliance with your document types
- ✅ **Privacy**: Runs locally, data never leaves your machine
- ⚠️ **General Knowledge**: Limited to training domain
- ⚠️ **Flexibility**: Can't switch topics easily

### GPT-4o
- ✅ **General Knowledge**: Knows everything
- ✅ **Flexibility**: Any topic, any style
- ✅ **Reasoning**: Complex logic and analysis
- ⚠️ **Consistency**: May vary between generations
- ⚠️ **Privacy**: Data sent to OpenAI
- ⚠️ **Cost**: Adds up quickly

### GPT-5 / GPT-5 Mini
- ✅ **Latest**: Most capable model
- ✅ **Caching**: 90% discount on cached inputs
- ✅ **Quality**: Better than GPT-4o
- ⚠️ **Cost**: Still expensive at scale
- ⚠️ **Privacy**: Data sent to OpenAI

### GPT-4o-mini
- ✅ **Cheapest**: $0.006 per 8K story
- ✅ **Fast**: Quick responses
- ✅ **General**: Handles any topic
- ⚠️ **Quality**: Lower than full GPT-4o
- ⚠️ **Reasoning**: Simpler than premium models

---

## Real-World Cost Comparison Table

| Stories | Fine-Tuned | GPT-4o-mini | GPT-5 Mini | GPT-5 | GPT-4o | Best Choice |
|---------|------------|-------------|------------|-------|--------|-------------|
| 100 | $34 | $0.60 | $1.80 | $9 | $10 | **GPT-4o-mini** |
| 500 | $34 | $3 | $9 | $45 | $50 | **Fine-Tuned** ✅ |
| 1,000 | $34 | $6 | $18 | $90 | $100 | **Fine-Tuned** ✅ |
| 5,000 | $34 | $30 | $90 | $450 | $500 | **Fine-Tuned** ✅ |
| 10,000 | $34 | $60 | $180 | $900 | $1,000 | **Fine-Tuned** ✅ |
| 50,000 | $34 | $300 | $900 | $4,500 | $5,000 | **Fine-Tuned** ✅ |
| 100,000 | $34 | $600 | $1,800 | $9,000 | $10,000 | **Fine-Tuned** ✅ |

---

## When to Use Which Model

### Use Your Fine-Tuned Model When:
- ✅ Generating 500+ stories (breaks even quickly)
- ✅ Need consistent world-building/characters
- ✅ Want specific narrative format compliance
- ✅ Privacy is important (local inference)
- ✅ Building a product/service (predictable costs)

### Use GPT-4o-mini When:
- ✅ Generating < 500 stories
- ✅ Need general knowledge/reasoning
- ✅ Want to switch topics frequently
- ✅ Don't want to manage infrastructure
- ✅ Occasional use only

### Use GPT-5/GPT-5 Mini When:
- ✅ Need absolute best quality
- ✅ Complex reasoning required
- ✅ Can leverage prompt caching (90% off)
- ✅ Moderate usage (1K-10K stories)
- ✅ Willing to pay for convenience

### Use GPT-4o When:
- ✅ Need multimodal (vision, audio)
- ✅ Maximum capability required
- ✅ Small volume (< 1,000 stories)
- ✅ Business critical quality

---

## Hybrid Strategy (Recommended)

### Best Approach: Use Both!

**For Narrative Generation** (your specialty):
- Use fine-tuned model
- Cost: $0/generation after training
- Quality: Specialized, consistent

**For General Tasks** (research, analysis, variation):
- Use GPT-4o-mini API
- Cost: Very cheap ($0.006 per 8K)
- Quality: Good enough for general use

**For Critical/Creative Tasks**:
- Use GPT-5 with caching
- Cost: Moderate with cache
- Quality: Best available

### Example Monthly Budget
```
Fine-Tuned Model:
- Training: $34 one-time
- 10,000 narratives/month: $0

GPT-4o-mini for variety:
- 1,000 variations/month: $6

GPT-5 for special cases:
- 100 premium generations: $9

Total: $34 one-time + $15/month
vs GPT-4o only: $1,100/month (73x more expensive)
```

---

## Bottom Line

### For Your Use Case (8K Token Narrative Generation):

**If generating < 500 stories**:
- Use **GPT-4o-mini** API ($3 total)
- Don't bother training

**If generating 500-5,000 stories**:
- Train your model ($34 once)
- **Saves $10-456** depending on volume
- **ROI**: 30-1,400%

**If generating 10,000+ stories**:
- Train your model ($34 once)
- **Saves $146-966** per 10K stories
- **ROI**: 429-2,850%
- **No-brainer decision** ✅

### Your Actual Situation
You've already proven:
- ✅ Model works (100% format compliance)
- ✅ Quality is good (42% longer, stays in character)
- ✅ Local inference works (10 tok/s on MPS)

**Recommendation**: 
1. ✅ Train 8K model on A100 ($34)
2. ✅ Use it for all narrative generation
3. ✅ Keep GPT-4o-mini API for quick variations/experiments
4. ✅ Save hundreds to thousands of dollars

**Your $34 investment breaks even after just 378 GPT-5 calls or 5,667 GPT-4o-mini calls.**

That's probably **1-2 months** of moderate use. After that, pure profit! 🚀
