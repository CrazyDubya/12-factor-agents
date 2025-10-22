#!/bin/bash

echo "=========================================="
echo "TESTING ALL OLLAMA MODELS"
echo "=========================================="
echo ""

# All text generation models (excluding embedding and vision models)
models=(
    # Large models (4-5GB)
    "gemma2:9b"
    "gemma2-32k:latest"
    "llama3-32k:latest"
    "mistral-32k:latest"
    "mistral:7b"
    "llama3:8b"

    # Medium models (2GB)
    "llama32-long:latest"
    "qwen-128k:latest"
    "qwen2.5:3b"
    "llama3.2:latest"
    "llama3.2:3b"
    "theater-long-context:latest"

    # Small models (1-2GB)
    "gemma2:2b"
    "smollm2:1.7b"
    "llama3.2:1b"
    "qwen2.5:1.5b"
    "toastie-qwen:latest"

    # Tiny models (<1GB)
    "gemma3:1b"
    "qwen2.5:0.5b"
    "smollm2:360m"
    "smollm2:135m"
)

echo "Will test ${#models[@]} models"
echo ""

# Test each model
for model in "${models[@]}"; do
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Testing: $model"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Check if results already exist
    safe_name=$(echo "$model" | sed 's/:/_/g' | sed 's/\//_/g')
    existing=$(ls test_results/test_results_${safe_name}_*.json 2>/dev/null | tail -1)

    if [ -n "$existing" ]; then
        echo "✓ Already tested (results exist: $existing)"
        echo "  Skipping..."
    else
        python3 test_single_model.py "$model"
    fi
done

echo ""
echo "=========================================="
echo "ALL MODELS TESTED"
echo "=========================================="
echo ""

# Count results
total_results=$(ls test_results/test_results_*.json 2>/dev/null | wc -l)
echo "Total test results: $total_results"
echo ""
echo "Generating comprehensive comparison..."
python3 compare_agents.py test_results/test_results_*.json

echo ""
echo "✓ Complete! View: open test_results/comparison_report_*.html"
