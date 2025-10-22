#!/bin/bash

# Test 3 different Ollama models and compare them

echo "============================================"
echo "Multi-Model Comparison Test"
echo "============================================"
echo ""

models=("qwen2.5:0.5b" "qwen2.5:3b" "llama3.2:latest")

for model in "${models[@]}"; do
    echo "Testing: $model"
    python3 comprehensive_auto_test.py "$model"
    echo ""
done

echo "Generating comparison report..."
python3 compare_agents.py test_results/test_results_*.json

echo ""
echo "Open comparison:"
echo "  open test_results/comparison_report_*.html"
